import os
import time

from jose import jwt

# ===== helpers =====


def _login_token(client, email: str, password: str) -> str:
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _pro_token(client) -> str:
    return _login_token(
        client,
        os.getenv("TEST_PRO_EMAIL", "admin@admin.com"),
        os.getenv("TEST_PRO_PASSWORD", "123456"),
    )


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_patient(client, pro_token: str, email: str, password: str = "teste1234") -> dict:
    payload = {"name": "Paciente", "email": email, "password": password}
    r = client.post("/patients", json=payload, headers=_auth_headers(pro_token))
    assert r.status_code in (200, 201), r.text
    return r.json()


def _create_exercise(client, pro_token: str) -> int:
    unique = int(time.time())
    payload = {
        "title": f"Exercicio Perm {unique}",
        "description": "perm test",
        "body_focus": "TRUNK",
        "analysis_kind": "V1_LITE_THRESHOLDS",
    }
    r = client.post("/exercises", json=payload, headers=_auth_headers(pro_token))
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _create_config(client, pro_token: str, patient_id: str, exercise_id: int) -> int:
    payload = {
        "exercise_id": exercise_id,
        "patient_user_id": patient_id,
        "params": {"threshold": 0.8},
    }
    r = client.post("/assignments/configs", json=payload, headers=_auth_headers(pro_token))
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _create_assignment(
    client, pro_token: str, patient_id: str, exercise_id: int, config_id: int
) -> int:
    payload = {
        "patient_user_id": patient_id,
        "exercise_id": exercise_id,
        "config_id": config_id,
        "schedule": "DAILY",
        "active": True,
    }
    r = client.post("/assignments", json=payload, headers=_auth_headers(pro_token))
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _create_session(
    client, pro_token: str, patient_id: str, exercise_id: int, assignment_id: int
) -> str:
    payload = {"exercise_id": exercise_id, "assignment_id": assignment_id, "config_snapshot": {}}
    r = client.post(
        f"/patients/{patient_id}/sessions", json=payload, headers=_auth_headers(pro_token)
    )
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _patient_token_via_jwt(patient_id: str) -> str:
    """
    Versão B (robusta): gera token direto.
    Requer SECRET_KEY do .env (mesmo usado pela API).
    """
    secret = os.getenv("SECRET_KEY")
    assert secret, "SECRET_KEY não definido no ambiente de teste"
    payload = {"sub": patient_id, "role": "PATIENT"}
    return jwt.encode(payload, secret, algorithm="HS256")


# ===== tests =====


def test_patient_cannot_access_other_patient_session(client):
    pro = _pro_token(client)

    unique = int(time.time())
    p1 = _create_patient(client, pro, f"p1_{unique}@teste.com")
    p2 = _create_patient(client, pro, f"p2_{unique}@teste.com")

    ex_id = _create_exercise(client, pro)

    cfg1 = _create_config(client, pro, p1["id"], ex_id)
    asg1 = _create_assignment(client, pro, p1["id"], ex_id, cfg1)
    s1 = _create_session(client, pro, p1["id"], ex_id, asg1)

    cfg2 = _create_config(client, pro, p2["id"], ex_id)
    asg2 = _create_assignment(client, pro, p2["id"], ex_id, cfg2)
    s2 = _create_session(client, pro, p2["id"], ex_id, asg2)

    # tenta logar como paciente (Versão A). Se falhar, usa token direto (Versão B).
    try:
        patient1_token = _login_token(client, p1["email"], "teste1234")
    except AssertionError:
        patient1_token = _patient_token_via_jwt(p1["id"])

    # Patient1 pode acessar sua sessão
    r = client.get(f"/sessions/{s1}", headers=_auth_headers(patient1_token))
    assert r.status_code == 200, r.text

    # Patient1 NÃO pode acessar sessão do Patient2
    r = client.get(f"/sessions/{s2}", headers=_auth_headers(patient1_token))
    assert r.status_code == 403, r.text


def test_patient_cannot_access_other_patient_summary(client):
    pro = _pro_token(client)

    unique = int(time.time())
    p1 = _create_patient(client, pro, f"p1s_{unique}@teste.com")
    p2 = _create_patient(client, pro, f"p2s_{unique}@teste.com")

    ex_id = _create_exercise(client, pro)

    cfg2 = _create_config(client, pro, p2["id"], ex_id)
    asg2 = _create_assignment(client, pro, p2["id"], ex_id, cfg2)
    s2 = _create_session(client, pro, p2["id"], ex_id, asg2)

    # cria summary do patient2 com PRO (permitido)
    r = client.post(
        f"/sessions/{s2}/summary",
        json={"reps": 1, "rom": 10.0, "cadence": 1.0, "alerts": []},
        headers=_auth_headers(pro),
    )
    assert r.status_code in (200, 201), r.text

    # token do patient1
    try:
        patient1_token = _login_token(client, p1["email"], "teste1234")
    except AssertionError:
        patient1_token = _patient_token_via_jwt(p1["id"])

    # Patient1 NÃO pode ver summary do Patient2
    r = client.get(f"/sessions/{s2}/summary", headers=_auth_headers(patient1_token))
    assert r.status_code == 403, r.text


def test_pro_can_access_any_session_and_summary(client):
    pro = _pro_token(client)

    unique = int(time.time())
    p = _create_patient(client, pro, f"pp_{unique}@teste.com")

    ex_id = _create_exercise(client, pro)
    cfg = _create_config(client, pro, p["id"], ex_id)
    asg = _create_assignment(client, pro, p["id"], ex_id, cfg)
    s = _create_session(client, pro, p["id"], ex_id, asg)

    # PRO acessa sessão
    r = client.get(f"/sessions/{s}", headers=_auth_headers(pro))
    assert r.status_code == 200, r.text

    # PRO pode criar/ler summary
    r = client.post(
        f"/sessions/{s}/summary",
        json={"reps": 2, "rom": 15.5, "cadence": 1.1, "alerts": ["ok"]},
        headers=_auth_headers(pro),
    )
    assert r.status_code in (200, 201), r.text

    r = client.get(f"/sessions/{s}/summary", headers=_auth_headers(pro))
    assert r.status_code == 200, r.text
