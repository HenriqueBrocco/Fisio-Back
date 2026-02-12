import os
import time
import json
import urllib.parse
import requests
from websocket import create_connection

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
WS_BASE = os.getenv("WS_BASE", "ws://127.0.0.1:8000")

PRO_EMAIL = os.getenv("TEST_PRO_EMAIL", "admin@admin.com")
PRO_PASSWORD = os.getenv("TEST_PRO_PASSWORD", "123456")

FRAME_PATH = os.getenv("WS_TEST_FRAME", "tests/assets/frame.jpg")
N_FRAMES = int(os.getenv("WS_TEST_N_FRAMES", "30"))
SLEEP_BETWEEN = float(os.getenv("WS_TEST_SLEEP", "0.05"))  # 50ms

def _assert(ok: bool, msg: str):
    if not ok:
        raise SystemExit(msg)

def login_token() -> str:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": PRO_EMAIL, "password": PRO_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    _assert(r.status_code == 200, f"Login falhou: {r.status_code} {r.text}")
    token = r.json().get("access_token")
    _assert(bool(token), "Token vazio no login.")
    return token

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def create_patient(token: str) -> str:
    unique = int(time.time())
    payload = {
        "name": "Paciente WS",
        "email": f"paciente_ws_{unique}@teste.com",
        "password": "teste1234",
    }
    r = requests.post(f"{BASE_URL}/patients", json=payload, headers=auth_headers(token), timeout=20)
    _assert(r.status_code in (200, 201), f"Create patient falhou: {r.status_code} {r.text}")
    return r.json()["id"]

def create_exercise(token: str) -> int:
    unique = int(time.time())
    payload = {
        "title": f"Exercicio WS {unique}",
        "description": "Criado pelo ws_stream_test",
        "body_focus": "TRUNK",
        "analysis_kind": "V1_LITE_THRESHOLDS",
    }
    r = requests.post(f"{BASE_URL}/exercises", json=payload, headers=auth_headers(token), timeout=20)
    _assert(r.status_code in (200, 201), f"Create exercise falhou: {r.status_code} {r.text}")
    return r.json()["id"]

def create_config(token: str, patient_id: str, exercise_id: int) -> int:
    payload = {
        "exercise_id": exercise_id,
        "patient_user_id": patient_id,
        "params": {"threshold": 0.8, "side": "R"},
    }
    r = requests.post(f"{BASE_URL}/assignments/configs", json=payload, headers=auth_headers(token), timeout=20)
    _assert(r.status_code in (200, 201), f"Create config falhou: {r.status_code} {r.text}")
    return r.json()["id"]

def create_assignment(token: str, patient_id: str, exercise_id: int, config_id: int) -> int:
    payload = {
        "patient_user_id": patient_id,
        "exercise_id": exercise_id,
        "config_id": config_id,
        "schedule": "DAILY",
        "active": True,
    }
    r = requests.post(f"{BASE_URL}/assignments", json=payload, headers=auth_headers(token), timeout=20)
    _assert(r.status_code in (200, 201), f"Create assignment falhou: {r.status_code} {r.text}")
    return r.json()["id"]

def create_session(token: str, patient_id: str, exercise_id: int, assignment_id: int) -> str:
    payload = {
        "exercise_id": exercise_id,
        "assignment_id": assignment_id,
        "config_snapshot": {"threshold": 0.8, "side": "R"},
    }
    r = requests.post(
        f"{BASE_URL}/patients/{patient_id}/sessions",
        json=payload,
        headers=auth_headers(token),
        timeout=20,
    )
    _assert(r.status_code in (200, 201), f"Create session falhou: {r.status_code} {r.text}")
    return r.json()["id"]

def get_session(token: str, session_id: str) -> dict:
    r = requests.get(f"{BASE_URL}/sessions/{session_id}", headers=auth_headers(token), timeout=20)
    _assert(r.status_code == 200, f"GET session falhou: {r.status_code} {r.text}")
    return r.json()

def get_summary(token: str, session_id: str) -> tuple[int, str]:
    r = requests.get(f"{BASE_URL}/sessions/{session_id}/summary", headers=auth_headers(token), timeout=20)
    return r.status_code, r.text

def main():
    _assert(os.path.exists(FRAME_PATH), f"Frame não encontrado: {FRAME_PATH}")
    with open(FRAME_PATH, "rb") as f:
        frame_bytes = f.read()
    _assert(len(frame_bytes) > 10, "Frame parece vazio.")

    print("1) Login...")
    token = login_token()

    print("2) Criando patient/exercise/config/assignment/session...")
    patient_id = create_patient(token)
    exercise_id = create_exercise(token)
    config_id = create_config(token, patient_id, exercise_id)
    assignment_id = create_assignment(token, patient_id, exercise_id, config_id)
    session_id = create_session(token, patient_id, exercise_id, assignment_id)

    token_q = urllib.parse.quote(token, safe="")
    ws_url = f"{WS_BASE}/infer/ws/session/{session_id}?token={token_q}"

    print("3) Conectando no WS...")
    ws = create_connection(ws_url)
    ready = ws.recv()
    print("WS ready:", ready)

    print(f"4) Enviando {N_FRAMES} frames...")
    last_metrics = None
    for i in range(N_FRAMES):
        ws.send_binary(frame_bytes)
        msg = ws.recv()
        last_metrics = msg
        if i < 3 or i == N_FRAMES - 1:
            print("WS msg:", msg)
        time.sleep(SLEEP_BETWEEN)

    print("5) Fechando WS...")
    ws.close()

    # dá um tempinho pro finally do WS commitar
    time.sleep(0.5)

    print("6) Validando sessão...")
    sess = get_session(token, session_id)
    print("Session:", json.dumps({k: sess.get(k) for k in ["id", "status", "started_at", "finished_at"]}, indent=2))
    _assert(sess.get("status") in ("FINISHED", "RUNNING"), "Status inesperado após WS.")  # pode demorar 1s em dev

    print("7) Validando summary (pode ser 404 se não teve métrica válida)...")
    code, text = get_summary(token, session_id)
    print("Summary status:", code)
    print("Summary body:", text[:300] + ("..." if len(text) > 300 else ""))

    print("\n✅ ws_stream_test concluído.")
    print("Obs: se Summary deu 404, é normal quando o frame não contém pose detectável (por causa do ajuste de não salvar vazio).")

if __name__ == "__main__":
    main()
