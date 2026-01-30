from fastapi import APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from collections import defaultdict

from functools import lru_cache
from app.services.pose_runtime import PoseRuntime
from app.services.pose_logic import RepDetector, RepConfig

router = APIRouter()

@lru_cache(maxsize=1)
def get_runtime() -> PoseRuntime:
    # cria 1 vez e reaproveita
    return PoseRuntime()

# ======== MODELOS ========

class KeypointsIn(BaseModel):
    # Sequência de frames; cada frame é uma lista de keypoints [x,y,conf]
    keypoints: list[list[list[float]]]
    fps: Optional[float] = None
    normalization: Optional[Literal["pixel", "normalized"]] = "pixel"
    exercise_id: Optional[str] = None
    session_id: Optional[str] = None

class InferOut(BaseModel):
    reps: int
    rom: float
    cadence: float | None = None
    alerts: list[str] = []

# ======== ENDPOINTS REST ========

@router.post("/frame", response_model=InferOut)
async def infer_frame(
    file: UploadFile = File(...),
    exercise_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    # TODO: processar imagem com OpenCV/Modelo
    return InferOut(reps=3, rom=52.0, cadence=2.1, alerts=["Ótimo alcance!"])

@router.post("/keypoints", response_model=InferOut)
async def infer_keypoints(payload: KeypointsIn):
    # TODO: analisar sequência payload.keypoints
    return InferOut(reps=4, rom=48.5, cadence=2.3, alerts=["Tente estender um pouco mais"])

# ======== WEBSOCKET (se já estiver usando) ========
try:
    _runtime = PoseRuntime()
except Exception as e:
    # 503: serviço indisponível (dependência opcional/erro de runtime)
    raise HTTPException(status_code=503, detail=str(e))

_detectors: dict[str, RepDetector] = defaultdict(lambda: RepDetector(RepConfig()))

@router.websocket("/ws/session/{session_id}")
async def ws_infer(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    print(f"WS: session {session_id} conectado")

    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"WS: recebeu frame de {len(data)} bytes")

            # TODO: aqui você reaproveita sua lógica de inferência
            # Ex.: keypoints = runtime.detect_pose(data)
            #      reps, rom, cadence, alerts = lógica_de_reps(keypoints)
            metrics = {
                "reps": 0,
                "rom": 40.3,
                "cadence": None,
                "alerts": ["Exemplo de alerta"],
            }

            await websocket.send_json(metrics)
            print(f"WS: enviou métricas: {metrics}")

    except WebSocketDisconnect:
        print(f"WS: session {session_id} desconectado")
    except Exception as e:
        print(f"WS: erro na sessão {session_id}: {e}")
        await websocket.close()