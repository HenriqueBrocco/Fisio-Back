from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from pydantic import BaseModel
import json
import asyncio
import random

router = APIRouter()

class KeypointsIn(BaseModel):
    # exemplo simples; ajuste conforme seu pipeline
    keypoints: list[list[float]]  # [[x,y,conf], ...]
    fps: float | None = None

class InferOut(BaseModel):
    reps: int
    rom: float
    cadence: float | None = None
    alerts: list[str] = []

@router.websocket("/ws/session/{session_id}")
async def ws_infer(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive()  # pode ser 'text' ou 'bytes'
            # 1) Se receber texto (JSON de keypoints)
            if "text" in msg and msg["text"] is not None:
                payload = json.loads(msg["text"])
                # TODO: chamar seu serviço de visão com payload
            # 2) Se receber binário (frame JPEG)
            elif "bytes" in msg and msg["bytes"] is not None:
                img_bytes = msg["bytes"]
                # TODO: processar frame com OpenCV/modelo

            # 3) Enviar métricas 'fake' (simulação)
            metrics = {
                "type": "metrics",
                "reps": random.randint(0, 20),
                "rom": round(random.uniform(30, 60), 1),
                "cadence": round(random.uniform(1.8, 2.6), 2),
                "alerts": ["Mantenha a cadência"] if random.random() > 0.5 else [],
            }
            await websocket.send_text(json.dumps(metrics))
            await asyncio.sleep(0.2)  # ~5 Hz

    except WebSocketDisconnect:
        # conexão encerrada pelo cliente
        return

@router.post("/frame", response_model=InferOut)
async def infer_frame(file: UploadFile = File(...)):
    # TODO: processar imagem com OpenCV/Modelo
    # Por agora, devolve mock:
    return InferOut(reps=3, rom=52.0, cadence=2.1, alerts=["Ótimo alcance!"])

@router.post("/keypoints", response_model=InferOut)
async def infer_keypoints(payload: KeypointsIn):
    # TODO: avaliar sequência de keypoints
    return InferOut(reps=4, rom=48.5, cadence=2.3, alerts=["Tente estender um pouco mais"])