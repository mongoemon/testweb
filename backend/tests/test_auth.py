class TestLogin:
    def test_success_returns_token(self, client):
        r = client.post("/api/auth/login", json={"username": "testuser", "password": "test1234"})
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_wrong_password_returns_401(self, client):
        r = client.post("/api/auth/login", json={"username": "testuser", "password": "wrong"})
        assert r.status_code == 401

    def test_nonexistent_user_returns_401(self, client):
        r = client.post("/api/auth/login", json={"username": "nobody", "password": "pass"})
        assert r.status_code == 401

    def test_admin_login(self, client):
        r = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
        assert r.status_code == 200
        assert r.json()["user"]["is_admin"] is True


class TestRegister:
    def test_success(self, client):
        r = client.post("/api/auth/register", json={
            "username": "reg_test_user",
            "email": "reg_test@test.com",
            "password": "pass1234",
        })
        assert r.status_code == 200
        assert r.json()["user"]["username"] == "reg_test_user"

    def test_duplicate_username_returns_400(self, client):
        r = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "other@test.com",
            "password": "pass1234",
        })
        assert r.status_code == 400

    def test_duplicate_email_returns_400(self, client):
        r = client.post("/api/auth/register", json={
            "username": "unique_name_xyz",
            "email": "test@shoeshub.com",
            "password": "pass1234",
        })
        assert r.status_code == 400

    def test_short_password_returns_422(self, client):
        r = client.post("/api/auth/register", json={
            "username": "shortpw_user",
            "email": "shortpw@test.com",
            "password": "abc",
        })
        assert r.status_code == 422


class TestMe:
    def test_returns_user_info(self, client, user_headers):
        r = client.get("/api/auth/me", headers=user_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "testuser"
        assert r.json()["is_admin"] is False

    def test_without_token_returns_401(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401
