import pytest

SHIPPING = {
    "shipping_name":    "Test User",
    "shipping_address": "123 Test Rd",
    "shipping_city":    "Bangkok",
    "shipping_postal":  "10100",
    "shipping_phone":   "080-000-0000",
    "payment_method":   "credit_card",
}


@pytest.fixture(scope="module")
def product(client):
    items = client.get("/api/products").json()["items"]
    return next(p for p in items if p["stock"] > 0)


@pytest.fixture(autouse=True)
def filled_cart(client, user_headers, product):
    """Each test starts with 1 item in cart; cart is cleared after."""
    client.delete("/api/cart/clear", headers=user_headers)
    size = product["sizes"][0] if product.get("sizes") else ""
    client.post("/api/cart", headers=user_headers, json={
        "product_id": product["id"], "quantity": 1, "size": size,
    })
    yield
    client.delete("/api/cart/clear", headers=user_headers)


# ── basic order flow ──────────────────────────────────────────────────────────

class TestPlaceOrder:
    def test_requires_auth(self, client):
        r = client.post("/api/orders", json=SHIPPING)
        assert r.status_code == 401

    def test_place_order_success(self, client, user_headers):
        r = client.post("/api/orders", headers=user_headers, json=SHIPPING)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "pending"
        assert data["total_amount"] > 0

    def test_order_appears_in_history(self, client, user_headers):
        client.post("/api/orders", headers=user_headers, json=SHIPPING)
        r = client.get("/api/orders", headers=user_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_empty_cart_returns_400(self, client, user_headers):
        client.delete("/api/cart/clear", headers=user_headers)
        r = client.post("/api/orders", headers=user_headers, json=SHIPPING)
        assert r.status_code == 400

    def test_cart_cleared_after_order(self, client, user_headers):
        client.post("/api/orders", headers=user_headers, json=SHIPPING)
        cart = client.get("/api/cart", headers=user_headers).json()
        assert cart["items"] == []


# ── discount applied on order ─────────────────────────────────────────────────

class TestOrderWithDiscount:
    def test_no_discount_code(self, client, user_headers, product):
        cart = client.get("/api/cart", headers=user_headers).json()
        r = client.post("/api/orders", headers=user_headers, json=SHIPPING)
        data = r.json()
        assert data["discount_code"] is None
        assert data["discount_amount"] == 0
        assert data["total_amount"] == pytest.approx(cart["total"], abs=0.01)

    def test_percentage_discount_spike10(self, client, user_headers):
        cart = client.get("/api/cart", headers=user_headers).json()
        subtotal = cart["total"]

        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "SPIKE10"})
        assert r.status_code == 200
        data = r.json()
        expected_discount = round(subtotal * 0.10, 2)
        assert data["discount_code"] == "SPIKE10"
        assert data["discount_amount"] == pytest.approx(expected_discount, abs=0.01)
        assert data["total_amount"] == pytest.approx(subtotal - expected_discount, abs=0.01)

    def test_percentage_discount_spike20(self, client, user_headers):
        cart = client.get("/api/cart", headers=user_headers).json()
        subtotal = cart["total"]

        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "SPIKE20"})
        assert r.status_code == 200
        data = r.json()
        assert data["discount_amount"] == pytest.approx(subtotal * 0.20, abs=0.01)

    def test_fixed_discount_flat100(self, client, user_headers):
        cart = client.get("/api/cart", headers=user_headers).json()
        subtotal = cart["total"]

        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "FLAT100"})
        assert r.status_code == 200
        data = r.json()
        assert data["discount_code"] == "FLAT100"
        assert data["discount_amount"] == 100.0
        assert data["total_amount"] == pytest.approx(subtotal - 100.0, abs=0.01)

    def test_fixed_discount_flat500(self, client, user_headers):
        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "FLAT500"})
        assert r.status_code == 200
        assert r.json()["discount_amount"] == 500.0

    def test_invalid_code_returns_404(self, client, user_headers):
        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "FAKEXXXX"})
        assert r.status_code == 404

    def test_case_insensitive_code(self, client, user_headers):
        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "flat100"})
        assert r.status_code == 200
        assert r.json()["discount_code"] == "FLAT100"

    def test_total_never_goes_negative(self, client, user_headers, admin_headers):
        # Create a fixed code larger than any product price
        client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "BIGDISCOUNT",
            "discount_type": "fixed",
            "discount_value": 999999.0,
        })
        r = client.post("/api/orders", headers=user_headers,
                        json={**SHIPPING, "discount_code": "BIGDISCOUNT"})
        assert r.status_code == 200
        assert r.json()["total_amount"] >= 0
        # cleanup
        codes = client.get("/api/admin/discount-codes", headers=admin_headers).json()
        code_id = next(c["id"] for c in codes if c["code"] == "BIGDISCOUNT")
        client.delete(f"/api/admin/discount-codes/{code_id}", headers=admin_headers)


# ── uses counter ──────────────────────────────────────────────────────────────

class TestDiscountUsesCounter:
    def test_current_uses_incremented(self, client, user_headers, admin_headers):
        codes = client.get("/api/admin/discount-codes", headers=admin_headers).json()
        before = next(c["current_uses"] for c in codes if c["code"] == "SPIKE10")

        client.post("/api/orders", headers=user_headers,
                    json={**SHIPPING, "discount_code": "SPIKE10"})

        codes_after = client.get("/api/admin/discount-codes", headers=admin_headers).json()
        after = next(c["current_uses"] for c in codes_after if c["code"] == "SPIKE10")
        assert after == before + 1

    def test_max_uses_enforced(self, client, user_headers, admin_headers):
        # Create a code with max_uses=1
        client.post("/api/admin/discount-codes", headers=admin_headers, json={
            "code": "ONETIME",
            "discount_type": "percentage",
            "discount_value": 5.0,
            "max_uses": 1,
        })
        # First use — should succeed
        r1 = client.post("/api/orders", headers=user_headers,
                         json={**SHIPPING, "discount_code": "ONETIME"})
        assert r1.status_code == 200

        # Need a fresh cart for second use
        size = client.get("/api/products").json()["items"][0]
        client.post("/api/cart", headers=user_headers, json={
            "product_id": size["id"], "quantity": 1, "size": "",
        })
        r2 = client.post("/api/orders", headers=user_headers,
                         json={**SHIPPING, "discount_code": "ONETIME"})
        assert r2.status_code == 400

        codes = client.get("/api/admin/discount-codes", headers=admin_headers).json()
        code_id = next(c["id"] for c in codes if c["code"] == "ONETIME")
        client.delete(f"/api/admin/discount-codes/{code_id}", headers=admin_headers)


# ── order detail ──────────────────────────────────────────────────────────────

class TestOrderDetail:
    def test_get_order_detail(self, client, user_headers):
        order = client.post("/api/orders", headers=user_headers, json=SHIPPING).json()
        r = client.get(f"/api/orders/{order['id']}", headers=user_headers)
        assert r.status_code == 200
        assert r.json()["id"] == order["id"]

    def test_cannot_view_other_user_order(self, client, user_headers, admin_headers):
        order = client.post("/api/orders", headers=user_headers, json=SHIPPING).json()
        # john_doe tries to view testuser's order
        r2 = client.post("/api/auth/login", json={"username": "john_doe", "password": "john1234"})
        john_headers = {"Authorization": f"Bearer {r2.json()['access_token']}"}
        r = client.get(f"/api/orders/{order['id']}", headers=john_headers)
        assert r.status_code == 404

    def test_order_not_found_returns_404(self, client, user_headers):
        r = client.get("/api/orders/99999", headers=user_headers)
        assert r.status_code == 404
