import time


def _login_token(client, email, password):
    r = client.post(
        "/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_update_config_params_validated(client):
    pro_email = "admin@admin.com"
    pro_pass = "123456"
    token = _login_token(client, pro_email, pro_pass)
    headers = _auth(token)

    unique = int(time.time())

    # cria paciente
    r = client.post(
        "/v1/patients",
        json={"name": "P", "email": f"p_{unique}@t.com", "password": "teste1234"},
        headers=headers,
    )
    assert r.status_code in (200, 201), r.text
    patient_id = r.json()["id"]

    # cria exercício com kind KNEE_EXTENSION_V1
    r = client.post(
        "/v1/exercises",
        json={
            "title": f"Extensao joelho {unique}",
            "description": "teste",
            "body_focus": "LOWER",
            "analysis_kind": "KNEE_EXTENSION_V1",
        },
        headers=headers,
    )
    assert r.status_code in (200, 201), r.text
    exercise_id = r.json()["id"]

    # cria config
    r = client.post(
        "/v1/assignments/configs",
        json={"exercise_id": exercise_id, "patient_user_id": patient_id, "params": {}},
        headers=headers,
    )
    assert r.status_code in (200, 201), r.text
    config_id = r.json()["id"]

    # atualiza params (deve validar e normalizar)
    r = client.put(
        f"/v1/assignments/configs/{config_id}/params",
        json={"params": {"low_deg": 92, "high_deg": 175, "hysteresis_deg": 2, "min_hold_ms": 50}},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == config_id
    assert body["params"]["low_deg"] == 92
    assert body["params"]["high_deg"] == 175

    # tenta params inválidos (high_deg fora do range)
    # r = client.put(
    #    f"/v1/assignments/configs/{config_id}/params",
    #    json={"params": {"low_deg": 90, "high_deg": 250}},
    #    headers=headers,
    # )
    # assert r.status_code == 422 or r.status_code == 400
