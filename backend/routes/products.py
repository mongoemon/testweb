import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth_utils import get_admin_user
from database import get_db
from models import ProductCreate

router = APIRouter(tags=["products"])

_PRODUCT_EXAMPLE = {
    "id": 1,
    "name": "Nike Air Max 90",
    "description": "Classic Air Max cushioning with a timeless design.",
    "price": 4990.0,
    "stock": 50,
    "category_id": 4,
    "image_url": "https://picsum.photos/seed/airmax90/600/400",
    "brand": "Nike",
    "sizes": ["38", "39", "40", "41", "42", "43", "44", "45"],
    "is_active": True,
    "created_at": "2024-01-01 00:00:00",
    "category_name": "Lifestyle",
    "category_slug": "lifestyle",
}

_RESPONSES_404 = {404: {"description": "Product not found"}}
_RESPONSES_403 = {403: {"description": "Admin access required"}}


def row_to_product(row) -> dict:
    p = dict(row)
    try:
        p["sizes"] = json.loads(p.get("sizes") or "[]")
    except Exception:
        p["sizes"] = []
    p["is_active"] = bool(p.get("is_active", 1))
    return p


# ── Categories ────────────────────────────────────────────────────────────────

@router.get(
    "/api/categories",
    summary="List all categories",
    description="คืนหมวดหมู่สินค้าทั้งหมด ไม่ต้อง authentication",
    response_description="Array of category objects",
    tags=["products"],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {"id": 3, "name": "Basketball", "slug": "basketball"},
                        {"id": 2, "name": "Casual",     "slug": "casual"},
                        {"id": 4, "name": "Lifestyle",  "slug": "lifestyle"},
                        {"id": 1, "name": "Running",    "slug": "running"},
                    ]
                }
            }
        }
    },
)
def list_categories():
    db = get_db()
    rows = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    db.close()
    return [dict(r) for r in rows]


# ── Products (public) ─────────────────────────────────────────────────────────

@router.get(
    "/api/products",
    summary="List products",
    description=(
        "คืนรายการสินค้าพร้อม pagination รองรับการ filter และ sort\n\n"
        "**Sort options:** `newest` | `price_asc` | `price_desc` | `name_asc`\n\n"
        "**ตัวอย่าง:**\n"
        "- ค้นหา Nike: `?search=nike`\n"
        "- Running shoes ราคาต่ำกว่า 5000: `?category=1&max_price=5000`\n"
        "- ไซส์ 42 เรียงราคาถูกสุด: `?size=42&sort=price_asc`"
    ),
    response_description="Paginated product list",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "items": [_PRODUCT_EXAMPLE],
                        "total": 12,
                        "page": 1,
                        "limit": 12,
                        "pages": 1,
                    }
                }
            }
        }
    },
)
def list_products(
    search:    Optional[str]   = Query(None,     description="ค้นหาจากชื่อ แบรนด์ หรือคำอธิบาย"),
    category:  Optional[int]   = Query(None,     description="Category ID (ดูได้จาก GET /api/categories)"),
    brand:     Optional[str]   = Query(None,     description="ชื่อแบรนด์ เช่น Nike, Adidas"),
    min_price: Optional[float] = Query(None,     description="ราคาขั้นต่ำ (บาท)"),
    max_price: Optional[float] = Query(None,     description="ราคาสูงสุด (บาท)"),
    size:      Optional[str]   = Query(None,     description="ไซส์รองเท้า เช่น 40, 42"),
    sort:      Optional[str]   = Query("newest", description="newest | price_asc | price_desc | name_asc"),
    page:      int             = Query(1,  ge=1, description="หน้าที่ (เริ่มที่ 1)"),
    limit:     int             = Query(12, ge=1, le=100, description="จำนวนต่อหน้า (สูงสุด 100)"),
):
    db = get_db()
    conditions = ["p.is_active = 1"]
    params: list = []

    if search:
        conditions.append("(p.name LIKE ? OR p.brand LIKE ? OR p.description LIKE ?)")
        term = f"%{search}%"
        params += [term, term, term]
    if category:
        conditions.append("p.category_id = ?")
        params.append(category)
    if brand:
        conditions.append("p.brand = ?")
        params.append(brand)
    if min_price is not None:
        conditions.append("p.price >= ?")
        params.append(min_price)
    if max_price is not None:
        conditions.append("p.price <= ?")
        params.append(max_price)
    if size:
        conditions.append("p.sizes LIKE ?")
        params.append(f'%"{size}"%')

    where = " AND ".join(conditions)
    sort_map = {
        "newest":     "p.created_at DESC",
        "price_asc":  "p.price ASC",
        "price_desc": "p.price DESC",
        "name_asc":   "p.name ASC",
    }
    order = sort_map.get(sort, "p.created_at DESC")

    total = db.execute(f"SELECT COUNT(*) FROM products p WHERE {where}", params).fetchone()[0]
    offset = (page - 1) * limit
    rows = db.execute(
        f"""SELECT p.*, c.name AS category_name, c.slug AS category_slug
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ).fetchall()
    db.close()

    return {
        "items": [row_to_product(r) for r in rows],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get(
    "/api/products/{product_id}",
    summary="Get product by ID",
    description="คืนรายละเอียดสินค้าชิ้นเดียว รวมถึงขนาดที่มี และหมวดหมู่",
    response_description="Product detail object",
    responses={
        200: {"content": {"application/json": {"example": _PRODUCT_EXAMPLE}}},
        **_RESPONSES_404,
    },
)
def get_product(product_id: int):
    db = get_db()
    row = db.execute(
        """SELECT p.*, c.name AS category_name, c.slug AS category_slug
           FROM products p LEFT JOIN categories c ON c.id = p.category_id
           WHERE p.id = ? AND p.is_active = 1""",
        (product_id,),
    ).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, "Product not found")
    return row_to_product(row)


# ── Products (admin CRUD) ─────────────────────────────────────────────────────

@router.post(
    "/api/products",
    summary="Create product [Admin]",
    description="สร้างสินค้าใหม่ ต้องใช้ **Admin token**",
    response_description="Created product object",
    status_code=200,
    responses={
        **_RESPONSES_403,
        401: {"description": "Not authenticated"},
    },
)
def create_product(data: ProductCreate, _=Depends(get_admin_user)):
    db = get_db()
    cur = db.execute(
        """INSERT INTO products (name, description, price, stock, category_id,
           image_url, brand, sizes, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.name, data.description, data.price, data.stock, data.category_id,
            data.image_url, data.brand, json.dumps(data.sizes or []),
            1 if data.is_active else 0,
        ),
    )
    db.commit()
    product_id = cur.lastrowid
    row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    return row_to_product(row)


@router.put(
    "/api/products/{product_id}",
    summary="Update product [Admin]",
    description="อัปเดตข้อมูลสินค้า ต้องใช้ **Admin token**",
    response_description="Updated product object",
    responses={
        **_RESPONSES_404,
        **_RESPONSES_403,
    },
)
def update_product(product_id: int, data: ProductCreate, _=Depends(get_admin_user)):
    db = get_db()
    existing = db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, "Product not found")
    db.execute(
        """UPDATE products SET name=?, description=?, price=?, stock=?, category_id=?,
           image_url=?, brand=?, sizes=?, is_active=? WHERE id=?""",
        (
            data.name, data.description, data.price, data.stock, data.category_id,
            data.image_url, data.brand, json.dumps(data.sizes or []),
            1 if data.is_active else 0, product_id,
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    return row_to_product(row)


@router.delete(
    "/api/products/{product_id}",
    summary="Delete product [Admin]",
    description=(
        "Soft-delete สินค้า (ตั้งค่า `is_active = false`) ต้องใช้ **Admin token**\n\n"
        "สินค้าจะไม่แสดงใน catalog แต่ยังคงอยู่ใน DB เพื่อ order history"
    ),
    response_description='{"message": "Product deleted"}',
    responses={
        **_RESPONSES_404,
        **_RESPONSES_403,
    },
)
def delete_product(product_id: int, _=Depends(get_admin_user)):
    db = get_db()
    existing = db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, "Product not found")
    db.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
    db.commit()
    db.close()
    return {"message": "Product deleted"}
