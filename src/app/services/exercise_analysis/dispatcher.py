from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.services.exercise_analysis.knee_extension_v1 import (
    KneeExtensionState,
    update_knee_extension,
)

AnalyzeFn = Callable[[float, dict[str, Any] | None, int | None], dict[str, Any]]


def _translate_alerts(alert_codes: list[str]) -> list[str]:
    mapping = {
        "ROM_OUT_OF_RANGE": "Ângulo fora do intervalo esperado.",
        "LOW_REACHED": "Flexão mínima atingida.",
        "REP_COUNTED": "Repetição contabilizada.",
        "RETURNED_TO_LOW_BEFORE_HIGH": "Você voltou antes de estender totalmente a perna.",
    }
    return [mapping.get(code, code) for code in alert_codes]


@dataclass
class Analyzer:
    analysis_kind: str
    run: AnalyzeFn


def create_analyzer(analysis_kind: str) -> Analyzer:
    """
    Retorna um Analyzer com estado interno para o exercício escolhido.
    O retorno do run já vem com alertas em PT-BR.
    """
    if analysis_kind == "KNEE_EXTENSION_V1":
        state = KneeExtensionState()

        def run(
            rom_deg: float, params: dict[str, Any] | None = None, ts_ms: int | None = None
        ) -> dict[str, Any]:
            metrics = update_knee_extension(rom_deg, state, params, ts_ms=ts_ms)
            metrics["alertas"] = _translate_alerts(metrics.get("alerts", []))
            # remove os códigos para não vazar pro paciente
            metrics.pop("alerts", None)
            return metrics

        return Analyzer(analysis_kind=analysis_kind, run=run)

    raise ValueError(f"analysis_kind não suportado: {analysis_kind}")
