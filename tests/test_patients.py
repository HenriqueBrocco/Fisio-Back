import os
import time
import pytest

def _login_and_get_token(client) -> str:
    """
    Faz login via OAuth2PasswordRequestForm:
    - Swagger envia 'username' e 'password'
    - No seu backend, 'username' = email
    """
    email = os.getenv("TEST_PRO_EMAIL", "admin@admin.com")
    password = os.getenv("TEST_PRO_PASSWORD", "123456")

    # Se você preferir obrigar env vars:
    # if not os.getenv("TEST_PRO_EMAIL") or not os.getenv("TEST_PRO_PASSWORD"):
    #     pytest.skip("Defina TEST_PRO_EMAIL e TEST_PRO_PASSWORD para rodar este teste.")

    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},  # <-- FORM, não JSON
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token
    return token


def test_create_and_list_patient_authenticated(client):
    token = _login_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    unique = int(time.time())
    payload = {
        "name": "Paciente Teste",
        "email": f"paciente{unique}@teste.com",
        "password": "teste1234",
    }

    r = client.post("/patients", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["role"] == "PATIENT"
    assert created["email"] == payload["email"]

    r = client.get("/patients", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)
    assert any(p["id"] == created["id"] for p in data)
