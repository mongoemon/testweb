import pytest


@pytest.fixture(scope="module")
def product(client):
    items = client.get("/api/products").json()["items"]
    return next(p for p in items if p["stock"] > 0)


@pytest.fixture(autouse=True)
def clear_cart(client, user_headers):
    client.delete("/api/cart/clear", headers=user_headers)
    yield
    client.delete("/api/cart/clear", headers=user_headers)


class TestCartAccess:
    def test_get_cart_requires_auth(self, client):
        r = client.get("/api/cart")
        assert r.status_code == 401

    def test_add_requires_auth(self, client, product):
        r = client.post("/api/cart", json={"product_id": product["id"], "quantity": 1, "size": ""})
        assert r.status_code == 401

    def test_empty_cart_on_fresh_user(self, client, user_headers):
        r = client.get("/api/cart", headers=user_headers)
        assert r.status_code == 200
        assert r.json()["items"] == []
        assert r.json()["total"] == 0


class TestAddToCart:
    def test_add_item(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        r = client.post("/api/cart", headers=user_headers, json={
            "product_id": product["id"], "quantity": 2, "size": size,
        })
        assert r.status_code == 200

    def test_cart_has_item_after_add(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        client.post("/api/cart", headers=user_headers, json={
            "product_id": product["id"], "quantity": 1, "size": size,
        })
        cart = client.get("/api/cart", headers=user_headers).json()
        assert len(cart["items"]) == 1
        assert cart["total"] > 0

    def test_add_same_item_merges_quantity(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        payload = {"product_id": product["id"], "quantity": 1, "size": size}
        client.post("/api/cart", headers=user_headers, json=payload)
        client.post("/api/cart", headers=user_headers, json=payload)
        cart = client.get("/api/cart", headers=user_headers).json()
        assert cart["items"][0]["quantity"] == 2

    def test_nonexistent_product_returns_404(self, client, user_headers):
        r = client.post("/api/cart", headers=user_headers, json={
            "product_id": 99999, "quantity": 1, "size": "",
        })
        assert r.status_code == 404


class TestUpdateCart:
    def test_update_quantity(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        client.post("/api/cart", headers=user_headers, json={
            "product_id": product["id"], "quantity": 1, "size": size,
        })
        item_id = client.get("/api/cart", headers=user_headers).json()["items"][0]["id"]
        r = client.put(f"/api/cart/{item_id}", headers=user_headers, json={"quantity": 3})
        assert r.status_code == 200
        cart = client.get("/api/cart", headers=user_headers).json()
        assert cart["items"][0]["quantity"] == 3


class TestRemoveFromCart:
    def test_remove_item(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        client.post("/api/cart", headers=user_headers, json={
            "product_id": product["id"], "quantity": 1, "size": size,
        })
        item_id = client.get("/api/cart", headers=user_headers).json()["items"][0]["id"]
        r = client.delete(f"/api/cart/{item_id}", headers=user_headers)
        assert r.status_code == 200
        cart = client.get("/api/cart", headers=user_headers).json()
        assert cart["items"] == []

    def test_clear_cart(self, client, user_headers, product):
        size = product["sizes"][0] if product.get("sizes") else ""
        client.post("/api/cart", headers=user_headers, json={
            "product_id": product["id"], "quantity": 1, "size": size,
        })
        r = client.delete("/api/cart/clear", headers=user_headers)
        assert r.status_code == 200
        assert client.get("/api/cart", headers=user_headers).json()["items"] == []
