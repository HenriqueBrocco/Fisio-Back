# src/app/services/pose_logic.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict
import math
import time

# Índices dos pontos do lado DIREITO (MediaPipe BlazePose)
HIP_R = 24
KNEE_R = 26
ANKLE_R = 28

VIS_MIN = 0.5  # visibilidade mínima aceitável


def _angle_between(p1, p2, p3) -> float:
    """
    Ângulo em graus no ponto p2, entre os vetores p1->p2 e p3->p2.
    p1, p2, p3: (x, y)
    """
    ax, ay = p1[0] - p2[0], p1[1] - p2[1]
    bx, by = p3[0] - p2[0], p3[1] - p2[1]

    dot = ax * bx + ay * by
    na = math.hypot(ax, ay)
    nb = math.hypot(bx, by)
    if na == 0 or nb == 0:
        return 0.0
    cosang = max(-1.0, min(1.0, dot / (na * nb)))
    return math.degrees(math.acos(cosang))


def rom_from_keypoints(keypoints: List[List[float]]) -> Optional[float]:
    """
    Calcula o ângulo do joelho (ROM) a partir dos keypoints normalizados BlazePose.

    keypoints[i] = [x, y, visibility]
    Retorna o ângulo em graus ou None se os pontos não forem confiáveis.
    """
    try:
        hip = keypoints[HIP_R]
        knee = keypoints[KNEE_R]
        ankle = keypoints[ANKLE_R]
    except IndexError:
        return None

    if hip[2] < VIS_MIN or knee[2] < VIS_MIN or ankle[2] < VIS_MIN:
        return None

    p1 = (hip[0], hip[1])
    p2 = (knee[0], knee[1])
    p3 = (ankle[0], ankle[1])

    ang = _angle_between(p1, p2, p3)
    return float(ang)


@dataclass
class RepConfig:
    low_deg: float = 30.0        # abaixo disso consideramos "joelho flexionado"
    high_deg: float = 55.0       # acima disso consideramos "joelho estendido"
    rom_target: float = 50.0     # alvo desejado de ROM
    min_cycle_time: float = 0.3  # tempo mínimo (s) para considerar uma repetição
    refractory: float = 0.2      # tempo mínimo entre reps (s)
    ema_alpha: float = 0.2       # fator de suavização da cadência


class RepDetector:
    """
    Máquina de estados simples para contar repetições e calcular cadência.
    Estados: 'idle' -> 'up' -> 'down'
    """

    def __init__(self, cfg: RepConfig | None = None) -> None:
        self.cfg = cfg or RepConfig()
        self.state = "idle"
        self.reps = 0
        self.last_rom: Optional[float] = None
        self.last_peak_time: Optional[float] = None
        self.last_rep_time: Optional[float] = None
        self.ema_cadence: Optional[float] = None  # segundos por repetição

    def update(self, rom: float) -> Dict[str, object]:
        """
        Atualiza o detector com o ROM atual.
        Retorna um dicionário com métricas:
        { "reps": int, "rom": float, "cadence": float|None, "alerts": [str] }
        """
        now = time.time()
        alerts: List[str] = []

        # Guarda ROM atual
        self.last_rom = rom

        # Máquina de estados
        if self.state == "idle":
            if rom > self.cfg.high_deg:
                self.state = "up"
                self.last_peak_time = now

        elif self.state == "up":
            # tracking do pico
            if rom > self.cfg.high_deg:
                self.last_peak_time = now
            # começou a descer
            if rom < self.cfg.low_deg:
                self.state = "down"

        elif self.state == "down":
            # completou o ciclo (voltou a flexionar)
            if rom < self.cfg.low_deg:
                # checa tempos
                if self.last_peak_time is not None:
                    cycle_time = now - self.last_peak_time
                    if cycle_time >= self.cfg.min_cycle_time:
                        if self.last_rep_time is None or (
                            now - self.last_rep_time >= self.cfg.refractory
                        ):
                            self.reps += 1
                            if self.last_rep_time is not None:
                                dt = now - self.last_rep_time
                                # cadência = segundos por rep
                                if dt > 0:
                                    if self.ema_cadence is None:
                                        self.ema_cadence = dt
                                    else:
                                        a = self.cfg.ema_alpha
                                        self.ema_cadence = (
                                            a * dt + (1 - a) * self.ema_cadence
                                        )
                            self.last_rep_time = now
                # volta para idle esperando o próximo ciclo
                self.state = "idle"

        # Regras simples de feedback
        if rom < self.cfg.rom_target * 0.7:
            alerts.append("Tente estender um pouco mais.")
        elif rom > self.cfg.rom_target * 1.1:
            alerts.append("Cuidado com a hiperextensão.")

        return {
            "reps": self.reps,
            "rom": rom,
            "cadence": self.ema_cadence,
            "alerts": alerts,
        }
