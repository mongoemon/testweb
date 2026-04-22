import json

from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from database import get_db
from models import CartItemAdd, CartItemUpdate

router = APIRouter(prefix="/api/cart", tags=["cart"])

_CART_EXAMPLE = {
    "items": [
        {
            "id": 1,
            "quantity": 2,
            "size": "42",
            "product_id": 1,
            "name": "Nike Air Max 90",
            "price": 4990.0,
            "image_url": "https://picsum.photos/seed/airmax90/600/400",
            "brand": "Nike",
            "stock": 50,
            "subtotal": 9980.0,
        }
    ],
    "total": 9980.0,
    "count": 2,
}

_RESPONSES_401 = {401: {"description": "Not authenticated — Bearer token required"}}
_RESPONSES_404 = {404: {"description": "Cart item not found"}}


def _get_cart_items(db, user_id: int) -> list:
    rows = db.execute(
        """SELECT ci.id, ci.quantity, ci.size,
                  p.id AS product_id, p.name, p.price, p.image_url, p.brand, p.stock
           FROM cart_items ci
           JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id = ?""",
        (user_id,),
    ).fetchall()
    items = []
    for r in rows:
        item = dict(r)
        item["subtotal"] = round(item["price"] * item["quantity"], 2)
        items.append(item)
    return items


@router.get(
    "",
    summary="Get cart",
    description="คืนรายการสินค้าในตะกร้าพร้อมยอดรวม ต้องมี Bearer token",
    response_description="Cart object with items, total, count",
    responses={
        200: {"content": {"application/json": {"example": _CART_EXAMPLE}}},
        **_RESPONSES_401,
    },
)
def get_cart(user: dict = Depends(get_current_user)):
    db = get_db()
    items = _get_cart_items(db, user["id"])
    db.close()
    total = round(sum(i["subtotal"] for i in items), 2)
    return {"items": items, "total": total, "count": sum(i["quantity"] for i in items)}


@router.post(
    "",
    summary="Add item to cart",
    description=(
        "เพิ่มสินค้าลงตะกร้า ถ้าสินค้า+ไซส์เดิมมีอยู่แล้วจะ **เพิ่ม quantity** ให้\n\n"
        "คืน cart ทั้งหมดหลังอัปเดต"
    ),
    response_description="Updated cart object",
    responses={
        200: {"content": {"application/json": {"example": _CART_EXAMPLE}}},
        **_RESPONSES_401,
        400: {"description": "Insufficient stock"},
        404: {"description": "Product not found or inactive"},
    },
)
def add_to_cart(data: CartItemAdd, user: dict = Depends(get_current_user)):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ? AND is_active = 1", (data.product_id,)
    ).fetchone()
    if not product:
        db.close()
        raise HTTPException(404, "Product not found")
    if product["stock"] < data.quantity:
        db.close()
        raise HTTPException(400, f"Only {product['stock']} items in stock")

    existing = db.execute(
        "SELECT id, quantity FROM cart_items WHERE user_id=? AND product_id=? AND size=?",
        (user["id"], data.product_id, data.size),
    ).fetchone()

    if existing:
        new_qty = existing["quantity"] + data.quantity
        if product["stock"] < new_qty:
            db.close()
            raise HTTPException(400, f"Only {product['stock']} items in stock")
        db.execute("UPDATE cart_items SET quantity=? WHERE id=?", (new_qty, existing["id"]))
    else:
        db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity, size) VALUES (?, ?, ?, ?)",
            (user["id"], data.product_id, data.quantity, data.size),
        )
    db.commit()
    items = _get_cart_items(db, user["id"])
    db.close()
    total = round(sum(i["subtotal"] for i in items), 2)
    return {"items": items, "total": total, "count": sum(i["quantity"] for i in items)}


@router.put(
    "/{item_id}",
    summary="Update cart item quantity",
    description="แก้ไขจำนวนสินค้าใน cart ตาม `item_id` (ไม่ใช่ product_id)",
    response_description="Updated cart object",
    responses={
        200: {"content": {"application/json": {"example": _CART_EXAMPLE}}},
        **_RESPONSES_401,
        **_RESPONSES_404,
        400: {"description": "quantity < 1 or exceeds stock"},
    },
)
def update_cart_item(item_id: int, data: CartItemUpdate, user: dict = Depends(get_current_user)):
    if data.quantity < 1:
        raise HTTPException(400, "Quantity must be at least 1")
    db = get_db()
    item = db.execute(
        "SELECT ci.*, p.stock FROM cart_items ci JOIN products p ON p.id = ci.product_id WHERE ci.id=? AND ci.user_id=?",
        (item_id, user["id"]),
    ).fetchone()
    if not item:
        db.close()
        raise HTTPException(404, "Cart item not found")
    if item["stock"] < data.quantity:
        db.close()
        raise HTTPException(400, f"Only {item['stock']} items in stock")
    db.execute("UPDATE cart_items SET quantity=? WHERE id=?", (data.quantity, item_id))
    db.commit()
    items = _get_cart_items(db, user["id"])
    db.close()
    total = round(sum(i["subtotal"] for i in items), 2)
    return {"items": items, "total": total, "count": sum(i["quantity"] for i in items)}


@router.delete(
    "/clear",
    summary="Clear entire cart",
    description="ลบสินค้าทั้งหมดออกจากตะกร้า",
    response_description='{"items": [], "total": 0, "count": 0}',
    responses={**_RESPONSES_401},
)
def clear_cart(user: dict = Depends(get_current_user)):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE user_id=?", (user["id"],))
    db.commit()
    db.close()
    return {"items": [], "total": 0, "count": 0}


@router.delete(
    "/{item_id}",
    summary="Remove cart item",
    description="ลบสินค้ารายการเดียวออกจากตะกร้า คืน cart ที่เหลือหลังลบ",
    response_description="Updated cart object",
    responses={
        200: {"content": {"application/json": {"example": {"items": [], "total": 0, "count": 0}}}},
        **_RESPONSES_401,
        **_RESPONSES_404,
    },
)
def remove_cart_item(item_id: int, user: dict = Depends(get_current_user)):
    db = get_db()
    existing = db.execute(
        "SELECT id FROM cart_items WHERE id=? AND user_id=?", (item_id, user["id"])
    ).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, "Cart item not found")
    db.execute("DELETE FROM cart_items WHERE id=?", (item_id,))
    db.commit()
    items = _get_cart_items(db, user["id"])
    db.close()
    total = round(sum(i["subtotal"] for i in items), 2)
    return {"items": items, "total": total, "count": sum(i["quantity"] for i in items)}
