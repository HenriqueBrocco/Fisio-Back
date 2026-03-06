from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KneeExtensionParams:
    # thresholds principais (graus)
    low_deg: float = 95.0  # ~90 flexionado, com margem
    high_deg: float = 170.0  # ~180 estendido, com margem

    # histerese (evita “trepidação” em torno do limiar)
    hysteresis_deg: float = 3.0

    # debounce por tempo (ms) para confirmar que cruzou de verdade
    min_hold_ms: int = 80

    # sanity range para alertas (se ângulo muito fora do esperado)
    min_valid_deg: float = 40.0
    max_valid_deg: float = 200.0


@dataclass
class KneeExtensionState:
    # estados:
    # "WAIT_LOW"  -> esperando passar abaixo do limiar inferior (flexão)
    # "WAIT_HIGH" -> depois da flexão, esperando passar acima do superior (extensão)
    phase: str = "WAIT_LOW"

    reps: int = 0
    last_rom: float = 0.0

    # tracking de tempo para cadence
    last_rep_ts: float | None = None
    cadence: float | None = None  # reps por segundo (ou você pode transformar em reps/min no front)

    # debounce
    last_cross_ts_ms: int = 0

    # debug/alerts acumulados do frame atual
    alerts: list[str] = field(default_factory=list)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _load_params(params: dict[str, Any] | None) -> KneeExtensionParams:
    p = KneeExtensionParams()
    if not params:
        return p

    # permite override via ExerciseConfig.params
    p.low_deg = float(params.get("low_deg", p.low_deg))
    p.high_deg = float(params.get("high_deg", p.high_deg))
    p.hysteresis_deg = float(params.get("hysteresis_deg", p.hysteresis_deg))
    p.min_hold_ms = int(params.get("min_hold_ms", p.min_hold_ms))
    p.min_valid_deg = float(params.get("min_valid_deg", p.min_valid_deg))
    p.max_valid_deg = float(params.get("max_valid_deg", p.max_valid_deg))
    return p


def update_knee_extension(
    rom_deg: float,
    state: KneeExtensionState,
    params: dict[str, Any] | None = None,
    *,
    ts_ms: int | None = None,
) -> dict[str, Any]:
    """
    Atualiza o estado do exercício usando apenas o ROM (ângulo do joelho).
    Retorna um pacote de métricas para enviar ao front.
    """
    p = _load_params(params)
    if ts_ms is None:
        ts_ms = _now_ms()

    state.alerts = []
    state.last_rom = float(rom_deg)

    # sanity checks
    if rom_deg < p.min_valid_deg or rom_deg > p.max_valid_deg:
        state.alerts.append("ROM_OUT_OF_RANGE")

    # limiares com histerese
    low_enter = p.low_deg
    low_exit = p.low_deg + p.hysteresis_deg

    high_enter = p.high_deg
    # high_exit = p.high_deg - p.hysteresis_deg

    # debounce helper
    def can_accept_cross() -> bool:
        return (ts_ms - state.last_cross_ts_ms) >= p.min_hold_ms

    # state machine
    if state.phase == "WAIT_LOW":
        # queremos “confirmar flexão”: rom <= low_enter
        if rom_deg <= low_enter and can_accept_cross():
            state.phase = "WAIT_HIGH"
            state.last_cross_ts_ms = ts_ms
            state.alerts.append("LOW_REACHED")  # opcional (debug)
        # dica de feedback
        elif rom_deg > low_exit:
            # ainda não flexionou o suficiente
            pass

    elif state.phase == "WAIT_HIGH":
        # queremos “confirmar extensão”: rom >= high_enter
        if rom_deg >= high_enter and can_accept_cross():
            state.reps += 1
            now_s = ts_ms / 1000.0
            if state.last_rep_ts is not None:
                dt = now_s - state.last_rep_ts
                if dt > 0:
                    state.cadence = 1.0 / dt  # reps/s
            state.last_rep_ts = now_s

            state.phase = "WAIT_LOW"
            state.last_cross_ts_ms = ts_ms
            state.alerts.append("REP_COUNTED")
        # se voltou a flexionar muito cedo, pode avisar (opcional)
        elif rom_deg < low_enter and can_accept_cross():
            state.alerts.append("RETURNED_TO_LOW_BEFORE_HIGH")

    # status de “ok” simples (você pode sofisticar depois)
    ok = "ROM_OUT_OF_RANGE" not in state.alerts

    return {
        "reps": state.reps,
        "rom": state.last_rom,
        "cadence": state.cadence,
        "alerts": state.alerts,
        "phase": state.phase,
        "ok": ok,
    }
