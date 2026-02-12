import os
import time


def _login_token(client) -> str:
    email = os.getenv("TEST_PRO_EMAIL", "admin@admin.com")
    password = os.getenv("TEST_PRO_PASSWORD", "123456")

    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},  # OAuth2 form
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token
    return token


def test_full_flow_patient_assignment_session_summary(client):
    token = _login_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    unique = int(time.time())

    # 1) cria paciente
    patient_payload = {
        "name": "Paciente Teste",
        "email": f"paciente{unique}@teste.com",
        "password": "teste1234",
    }
    r = client.post("/patients", json=patient_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    patient = r.json()
    patient_id = patient["id"]

    # 2) cria exercício
    exercise_payload = {
        "title": f"Exercício Teste {unique}",
        "description": "Exercício criado no teste",
        "body_focus": "TRUNK",
        "analysis_kind": "V1_LITE_THRESHOLDS",
    }
    r = client.post("/exercises", json=exercise_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    exercise = r.json()
    exercise_id = exercise["id"]

    # 3) cria config do exercício para o paciente
    config_payload = {
        "exercise_id": exercise_id,
        "patient_user_id": patient_id,
        "params": {"threshold": 0.8, "side": "R"},
    }
    r = client.post("/assignments/configs", json=config_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    cfg = r.json()
    config_id = cfg["id"]

    # 4) cria assignment (prescrição)
    assignment_payload = {
        "patient_user_id": patient_id,
        "exercise_id": exercise_id,
        "config_id": config_id,
        "schedule": "DAILY",
        "active": True,
    }
    r = client.post("/assignments", json=assignment_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    assignment = r.json()
    assignment_id = assignment["id"]

    # 5) cria sessão do paciente
    session_payload = {
        "exercise_id": exercise_id,
        "assignment_id": assignment_id,
        "config_snapshot": {"threshold": 0.8, "side": "R"},
    }
    r = client.post(f"/patients/{patient_id}/sessions", json=session_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    session = r.json()
    session_id = session["id"]

    # 5.1) start session (core endpoint)
    r = client.post(f"/sessions/{session_id}/start", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "RUNNING"
    s_started = r.json()
    assert s_started["status"] == "RUNNING"

    # 6) cria/upsert summary
    summary_payload = {
        "reps": 10,
        "rom": 35.5,
        "cadence": 1.2,
        "alerts": ["ok"],
    }
    r = client.post(f"/sessions/{session_id}/summary", json=summary_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    summary = r.json()
    assert summary["session_id"] == session_id
    assert summary["reps"] == 10

    # 7) lê summary
    r = client.get(f"/sessions/{session_id}/summary", headers=headers)
    assert r.status_code == 200, r.text
    summary2 = r.json()
    assert summary2["session_id"] == session_id
    assert summary2["reps"] == 10

    # 7.1) Finaliza summario
    r = client.post(f"/sessions/{session_id}/finalize", json={"reps": 10, "rom": 35.5}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "FINISHED"
    
    # 8) finish session (core endpoint)
    r = client.post(f"/sessions/{session_id}/finish", headers=headers)
    assert r.status_code == 200, r.text
    s_finished = r.json()
    assert s_finished["status"] == "FINISHED"
    assert s_finished["finished_at"] is not None
