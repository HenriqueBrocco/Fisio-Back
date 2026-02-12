from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.db.session import SessionLocal  # usa o mesmo SessionLocal do seu db/session.py
from app.models.session import Session as SessionModel, SessionSummary as SessionSummaryModel
from app.models.user import User
from app.services.pose_runtime import PoseRuntime
from app.services.pose_logic import rom_from_keypoints, RepDetector

router = APIRouter(prefix="/infer", tags=["infer"])


def _get_token_from_ws(websocket: WebSocket) -> str | None:
    """
    Aceita token via:
      - Header: Authorization: Bearer <token>
      - Query: ?token=<token>
    """
    auth = websocket.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return websocket.query_params.get("token")


def _ensure_session_access(user: User, sess: SessionModel) -> None:
    if user.role == "PATIENT" and sess.patient_user_id != user.id:
        raise PermissionError("Sem permissão para esta sessão.")


@router.websocket("/ws/session/{session_id}")
async def ws_infer_session(websocket: WebSocket, session_id: str):
    """
    Cliente envia: bytes JPEG (binary)
    Servidor responde: JSON metrics (sem persistir por frame)

    Persistência:
      - on_connect: valida sessão e marca RUNNING (start automático)
      - on_disconnect: grava SessionSummary final e marca FINISHED
    """
    await websocket.accept()

    # 1) runtime vision opcional
    try:
        runtime = PoseRuntime()
    except Exception as e:
        await websocket.send_json({"type": "error", "detail": f"Vision indisponível: {e}"})
        await websocket.close(code=1011)
        return

    # 2) abre sessão DB (sync) e valida sessão + permissão
    db: DBSession = SessionLocal()
    user: User | None = None
    sess: SessionModel | None = None

    try:
        # ---- autenticação (recomendado) ----
        # Se você ainda não quiser auth no WS, pode comentar este bloco.
        token = _get_token_from_ws(websocket)
        if not token:
            await websocket.send_json({"type": "error", "detail": "Token ausente (Authorization Bearer ou ?token=...)"})
            await websocket.close(code=1008)
            return

        # Reusa sua função de validação de token / current user
        # Ajuste o import conforme seu projeto:
        from app.api.deps import get_current_user_from_token  # crie essa função se não existir

        user = get_current_user_from_token(db, token)

        # ---- valida sessão existe ----
        sess = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
        if not sess:
            await websocket.send_json({"type": "error", "detail": "Sessão não encontrada."})
            await websocket.close(code=1008)
            return

        # ---- permissão ----
        try:
            _ensure_session_access(user, sess)
        except PermissionError as e:
            await websocket.send_json({"type": "error", "detail": str(e)})
            await websocket.close(code=1008)
            return

        # 3) start automático
        if sess.status == "CREATED":
            sess.status = "RUNNING"
            sess.started_at = datetime.utcnow()
            db.add(sess)
            db.commit()
            db.refresh(sess)

        detector = RepDetector()
        last_metrics = {"reps": 0, "rom": 0.0, "cadence": None, "alerts": []}
        had_valid_metrics = False

        await websocket.send_json({"type": "ready", "session_id": session_id, "status": sess.status})

        # 4) loop de frames
        while True:
            msg = await websocket.receive()
            frame: bytes | None = msg.get("bytes")

            if frame is None:
                await websocket.send_json({"type": "error", "detail": "Envie frames como binário (JPEG bytes)."})
                continue

            bgr = runtime.decode_jpeg(frame)
            if bgr is None:
                await websocket.send_json({"type": "metrics", "session_id": session_id, "ok": False, "reason": "decode_failed"})
                continue

            keypoints = runtime.infer_keypoints(bgr)
            if not keypoints:
                await websocket.send_json({"type": "metrics", "session_id": session_id, "ok": False, "reason": "no_pose"})
                continue

            rom = rom_from_keypoints(keypoints)
            if rom is None:
                await websocket.send_json({"type": "metrics", "session_id": session_id, "ok": False, "reason": "low_visibility"})
                continue

            metrics = detector.update(rom)
            last_metrics = metrics
            had_valid_metrics = True

            await websocket.send_json(
                {
                    "type": "metrics",
                    "session_id": session_id,
                    "ok": True,
                    "reps": metrics["reps"],
                    "rom": float(metrics["rom"]),
                    "cadence": metrics["cadence"],
                    "alerts": metrics["alerts"],
                }
            )

    except WebSocketDisconnect:
        # normal: cliente fechou
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "detail": str(e)})
        except Exception:
            pass
    finally:
        # 5) persistir summary final + finalizar sessão
        try:
            if had_valid_metrics:
                if db and sess:
                    # grava/atualiza summary final (apenas no final)
                    summary = db.execute(
                        select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
                    ).scalar_one_or_none()

                    if summary:
                        summary.reps = int(last_metrics.get("reps", 0))
                        summary.rom = float(last_metrics.get("rom", 0.0))
                        summary.cadence = last_metrics.get("cadence")
                        summary.alerts = last_metrics.get("alerts", [])
                    else:
                        summary = SessionSummaryModel(
                            session_id=session_id,
                            reps=int(last_metrics.get("reps", 0)),
                            rom=float(last_metrics.get("rom", 0.0)),
                            cadence=last_metrics.get("cadence"),
                            alerts=last_metrics.get("alerts", []),
                        )
                        db.add(summary)

                    # finaliza sessão
                    if sess.status != "FINISHED":
                        sess.status = "FINISHED"
                        sess.finished_at = datetime.utcnow()
                        db.add(sess)

                    db.commit()
        finally:
            if db:
                db.close()
            try:
                await websocket.close()
            except Exception:
                pass

@router.get("/ws/ping")
def ws_ping():
    return {"ok": True}