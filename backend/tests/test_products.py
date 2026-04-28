import pytest


@pytest.fixture(scope="module")
def first_product(client):
    r = client.get("/api/products")
    assert r.status_code == 200
    return r.json()["items"][0]


class TestListProducts:
    def test_public_access(self, client):
        r = client.get("/api/products")
        assert r.status_code == 200

    def test_returns_items_and_total(self, client):
        data = client.get("/api/products").json()
        assert "items" in data
        assert "total" in data
        assert data["total"] > 0

    def test_search_filter(self, client):
        r = client.get("/api/products?search=Nike")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert "nike" in item["name"].lower() or "nike" in (item.get("brand") or "").lower()

    def test_sort_price_asc(self, client):
        r = client.get("/api/products?sort=price_asc&limit=100")
        items = r.json()["items"]
        prices = [i["price"] for i in items]
        assert prices == sorted(prices)

    def test_sort_price_desc(self, client):
        r = client.get("/api/products?sort=price_desc&limit=100")
        items = r.json()["items"]
        prices = [i["price"] for i in items]
        assert prices == sorted(prices, reverse=True)

    def test_pagination(self, client):
        r1 = client.get("/api/products?page=1&limit=2")
        r2 = client.get("/api/products?page=2&limit=2")
        ids1 = {i["id"] for i in r1.json()["items"]}
        ids2 = {i["id"] for i in r2.json()["items"]}
        assert ids1.isdisjoint(ids2)


class TestGetProduct:
    def test_returns_product(self, client, first_product):
        r = client.get(f"/api/products/{first_product['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == first_product["id"]

    def test_not_found_returns_404(self, client):
        r = client.get("/api/products/99999")
        assert r.status_code == 404

    def test_has_required_fields(self, client, first_product):
        data = client.get(f"/api/products/{first_product['id']}").json()
        for field in ("id", "name", "price", "stock", "sizes"):
            assert field in data


class TestProductAdmin:
    def test_create_requires_admin(self, client, user_headers):
        r = client.post("/api/products", headers=user_headers,
                        json={"name": "Fake Shoe", "price": 999.0})
        assert r.status_code == 403

    def test_create_without_auth_returns_401(self, client):
        r = client.post("/api/products",
                        json={"name": "Fake Shoe", "price": 999.0})
        assert r.status_code in (401, 403)

    def test_create_product_admin(self, client, admin_headers):
        r = client.post("/api/products", headers=admin_headers, json={
            "name": "Test Shoe X",
            "price": 1234.0,
            "stock": 5,
            "brand": "TestBrand",
            "sizes": ["40", "41", "42"],
        })
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Test Shoe X"
        assert data["price"] == 1234.0

    def test_update_product_admin(self, client, admin_headers, first_product):
        r = client.put(f"/api/products/{first_product['id']}", headers=admin_headers,
                       json={"name": first_product["name"], "price": first_product["price"],
                             "stock": first_product["stock"]})
        assert r.status_code == 200


class TestCategories:
    def test_list_categories_public(self, client):
        r = client.get("/api/categories")
        assert r.status_code == 200
        assert len(r.json()) >= 4

    def test_category_has_name_and_slug(self, client):
        cats = client.get("/api/categories").json()
        for cat in cats:
            assert "name" in cat
            assert "slug" in cat
