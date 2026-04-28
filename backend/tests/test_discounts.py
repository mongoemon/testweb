import pytest


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def temp_code(client, admin_headers):
    """Create a throwaway code for update/delete tests."""
    r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
        "code": "TMPTEST01",
        "description": "Temp code for testing",
        "discount_type": "percentage",
        "discount_value": 5.0,
        "is_active": True,
    })
    assert r.status_code == 201
    dc = r.json()
    yield dc
    client.delete(f"/api/admin/discount-codes/{dc['id']}", headers=admin_headers)


# ── validate endpoint ─────────────────────────────────────────────────────────

class TestValidateDiscount:
    def test_requires_auth(self, client):
        r = client.post("/api/discount-codes/validate", json={"code": "SPIKE10"})
        assert r.status_code == 401

    def test_valid_percentage_code(self, client, user_headers):
        r = client.post("/api/discount-codes/validate", headers=user_headers,
                        json={"code": "SPIKE10"})
        assert r.status_code == 200
        data = r.json()
        assert data["code"] == "SPIKE10"
        assert data["discount_type"] == "percentage"
        assert data["discount_value"] == 10.0
        assert data["expires_at"] is None

    def test_valid_fixed_code(self, client, user_headers):
        r = client.post("/api/discount-codes/validate", headers=user_headers,
                        json={"code": "FLAT100"})
        assert r.status_code == 200
        data = r.json()
        assert data["discount_type"] == "fixed"
        assert data["discount_value"] == 100.0

    def test_case_insensitive(self, client, user_headers):
        r = client.post("/api/discount-codes/validate", headers=user_headers,
                        json={"code": "spike10"})
        assert r.status_code == 200
        assert r.json()["code"] == "SPIKE10"

    def test_nonexistent_returns_404(self, client, user_headers):
        r = client.post("/api/discount-codes/validate", headers=user_headers,
                        json={"code": "DOESNOTEXIST"})
        assert r.status_code == 404

    def test_all_spike_codes_valid(self, client, user_headers):
        for code in ("SPIKE10", "SPIKE20", "FLAT100", "FLAT500"):
            r = client.post("/api/discount-codes/validate", headers=user_headers,
                            json={"code": code})
            assert r.status_code == 200, f"{code} should be valid"


# ── admin list ────────────────────────────────────────────────────────────────

class TestAdminList:
    def test_user_cannot_list(self, client, user_headers):
        r = client.get("/api/admin/discount-codes", headers=user_headers)
        assert r.status_code == 403

    def test_no_auth_cannot_list(self, client):
        r = client.get("/api/admin/discount-codes")
        assert r.status_code in (401, 403)

    def test_admin_gets_list(self, client, admin_headers):
        r = client.get("/api/admin/discount-codes", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_spike_codes_present(self, client, admin_headers):
        codes = {dc["code"] for dc in client.get(
            "/api/admin/discount-codes", headers=admin_headers).json()}
        assert {"SPIKE10", "SPIKE20", "FLAT100", "FLAT500"}.issubset(codes)


# ── admin create ──────────────────────────────────────────────────────────────

class TestAdminCreate:
    def test_create_percentage_code(self, client, admin_headers):
        r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "NEWPCT15",
            "discount_type": "percentage",
            "discount_value": 15.0,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["code"] == "NEWPCT15"
        assert data["current_uses"] == 0
        # cleanup
        client.delete(f"/api/admin/discount-codes/{data['id']}", headers=admin_headers)

    def test_create_fixed_code_with_expiry(self, client, admin_headers):
        r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "FIXEDEXP",
            "discount_type": "fixed",
            "discount_value": 200.0,
            "expires_at": "2099-12-31T23:59:59",
            "max_uses": 50,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["max_uses"] == 50
        assert data["expires_at"] is not None
        client.delete(f"/api/admin/discount-codes/{data['id']}", headers=admin_headers)

    def test_duplicate_code_returns_400(self, client, admin_headers):
        r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "SPIKE10",
            "discount_type": "percentage",
            "discount_value": 5.0,
        })
        assert r.status_code == 400

    def test_user_cannot_create(self, client, user_headers):
        r = client.post("/api/admin/discount-codes", headers=user_headers, json={
            "code": "USERHACK",
            "discount_type": "percentage",
            "discount_value": 99.0,
        })
        assert r.status_code == 403


# ── admin update ──────────────────────────────────────────────────────────────

class TestAdminUpdate:
    def test_update_value(self, client, admin_headers, temp_code):
        r = client.put(f"/api/admin/discount-codes/{temp_code['id']}",
                       headers=admin_headers, json={"discount_value": 25.0})
        assert r.status_code == 200
        assert r.json()["discount_value"] == 25.0

    def test_deactivate_code(self, client, admin_headers, temp_code):
        r = client.put(f"/api/admin/discount-codes/{temp_code['id']}",
                       headers=admin_headers, json={"is_active": False})
        assert r.status_code == 200
        # Reactivate for other tests
        client.put(f"/api/admin/discount-codes/{temp_code['id']}",
                   headers=admin_headers, json={"is_active": True})

    def test_deactivated_code_fails_validation(self, client, admin_headers, user_headers):
        r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "DEACTEST",
            "discount_type": "percentage",
            "discount_value": 5.0,
            "is_active": False,
        })
        code_id = r.json()["id"]
        val = client.post("/api/discount-codes/validate", headers=user_headers,
                          json={"code": "DEACTEST"})
        assert val.status_code == 400
        client.delete(f"/api/admin/discount-codes/{code_id}", headers=admin_headers)

    def test_update_nonexistent_returns_404(self, client, admin_headers):
        r = client.put("/api/admin/discount-codes/99999",
                       headers=admin_headers, json={"discount_value": 5.0})
        assert r.status_code == 404


# ── admin delete ──────────────────────────────────────────────────────────────

class TestAdminDelete:
    def test_delete_code(self, client, admin_headers):
        r = client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "TOBEDELETED",
            "discount_type": "fixed",
            "discount_value": 50.0,
        })
        code_id = r.json()["id"]
        del_r = client.delete(f"/api/admin/discount-codes/{code_id}", headers=admin_headers)
        assert del_r.status_code == 200
        # Confirm gone from list
        codes = {dc["code"] for dc in client.get(
            "/api/admin/discount-codes", headers=admin_headers).json()}
        assert "TOBEDELETED" not in codes

    def test_delete_nonexistent_returns_404(self, client, admin_headers):
        r = client.delete("/api/admin/discount-codes/99999", headers=admin_headers)
        assert r.status_code == 404
