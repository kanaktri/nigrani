def test_register_and_login_roundtrip(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "New Official",
        "email": "newofficial@qa.dosje-nigrani.gov.in",
        "password": "StrongPass123!",
        "role": "official",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "official"
    assert "access_token" in body

    login_resp = client.post("/api/v1/auth/login", json={
        "email": "newofficial@qa.dosje-nigrani.gov.in",
        "password": "StrongPass123!",
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["role"] == "official"


def test_login_wrong_password_rejected(client):
    client.post("/api/v1/auth/register", json={
        "name": "X", "email": "x@qa.dosje-nigrani.gov.in", "password": "CorrectPass123!", "role": "official",
    })
    resp = client.post("/api/v1/auth/login", json={"email": "x@qa.dosje-nigrani.gov.in", "password": "WrongPassword!"})
    assert resp.status_code == 401


def test_duplicate_email_rejected(client):
    payload = {"name": "AB", "email": "dupe@qa.dosje-nigrani.gov.in", "password": "StrongPass123!", "role": "official"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_invalid_role_rejected(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "X", "email": "badrole@qa.dosje-nigrani.gov.in", "password": "StrongPass123!", "role": "superuser",
    })
    assert resp.status_code == 422


def test_unauthenticated_request_rejected(client):
    resp = client.get("/api/v1/institutes")
    assert resp.status_code == 401


def test_rbac_blocks_wrong_role(client, make_user):
    _, staff_headers = make_user(role="institute_staff")
    resp = client.post("/api/v1/assignments/generate", headers=staff_headers)
    assert resp.status_code == 403


def test_rbac_allows_correct_role(client, make_user, make_institute):
    make_institute()
    make_user(role="inspector", email="insp@qa.dosje-nigrani.gov.in")
    _, admin_headers = make_user(role="admin")
    resp = client.post("/api/v1/assignments/generate", headers=admin_headers)
    assert resp.status_code == 201
