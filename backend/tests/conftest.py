import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    db_path = str(tmp_path_factory.mktemp("testdb") / "test.db")

    import database
    database.DB_PATH = db_path

    from main import app
    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def user_headers(client):
    r = client.post("/api/auth/login", json={"username": "testuser", "password": "test1234"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin_headers(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
