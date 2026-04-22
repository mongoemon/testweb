from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from database import get_db
from models import OrderCreate

router = APIRouter(prefix="/api/orders", tags=["orders"])

_ORDER_EXAMPLE = {
    "id": 1,
    "user_id": 2,
    "total_amount": 9980.0,
    "status": "pending",
    "shipping_name": "John Doe",
    "shipping_address": "123 Sukhumvit Rd, Khlong Toei",
    "shipping_city": "Bangkok",
    "shipping_postal": "10110",
    "shipping_phone": "081-234-5678",
    "payment_method": "credit_card",
    "created_at": "2024-01-15 10:30:00",
    "updated_at": "2024-01-15 10:30:00",
    "items": [
        {
            "id": 1,
            "order_id": 1,
            "product_id": 1,
            "product_name": "Nike Air Max 90",
            "quantity": 2,
            "price": 4990.0,
            "size": "42",
        }
    ],
}

_RESPONSES_401 = {401: {"description": "Not authenticated — Bearer token required"}}
_RESPONSES_404 = {404: {"description": "Order not found"}}


def _get_order_items(db, order_id: int) -> list:
    rows = db.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()
    return [dict(r) for r in rows]


def _format_order(row, items: list) -> dict:
    o = dict(row)
    o["items"] = items
    return o


@router.get(
    "",
    summary="List my orders",
    description="คืนประวัติคำสั่งซื้อของ user ที่ login อยู่ เรียงจากล่าสุด",
    response_description="Array of order objects (newest first)",
    responses={
        200: {"content": {"application/json": {"example": [_ORDER_EXAMPLE]}}},
        **_RESPONSES_401,
    },
)
def list_orders(user: dict = Depends(get_current_user)):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    orders = []
    for row in rows:
        items = _get_order_items(db, row["id"])
        orders.append(_format_order(row, items))
    db.close()
    return orders


@router.get(
    "/{order_id}",
    summary="Get order detail",
    description="คืนรายละเอียดคำสั่งซื้อ user สามารถดูได้เฉพาะ order ของตนเองเท่านั้น",
    response_description="Order detail with items and shipping info",
    responses={
        200: {"content": {"application/json": {"example": _ORDER_EXAMPLE}}},
        **_RESPONSES_401,
        **_RESPONSES_404,
    },
)
def get_order(order_id: int, user: dict = Depends(get_current_user)):
    db = get_db()
    row = db.execute(
        "SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, user["id"])
    ).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Order not found")
    items = _get_order_items(db, order_id)
    db.close()
    return _format_order(row, items)


@router.post(
    "",
    summary="Place order",
    description=(
        "สั่งซื้อจากสินค้าในตะกร้าทั้งหมด\n\n"
        "**ขั้นตอน:**\n"
        "1. ตรวจสอบว่าตะกร้าไม่ว่าง\n"
        "2. ตรวจสอบ stock ทุกรายการ\n"
        "3. สร้าง order + ลด stock\n"
        "4. ล้างตะกร้า\n\n"
        "**หมายเหตุ:** ต้อง Add สินค้าเข้าตะกร้าก่อนผ่าน `POST /api/cart`"
    ),
    response_description="Created order object with all items",
    responses={
        200: {"content": {"application/json": {"example": _ORDER_EXAMPLE}}},
        **_RESPONSES_401,
        400: {"description": "Cart is empty or insufficient stock"},
    },
)
def place_order(data: OrderCreate, user: dict = Depends(get_current_user)):
    db = get_db()

    cart_items = db.execute(
        """SELECT ci.*, p.price, p.name AS product_name, p.stock
           FROM cart_items ci JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id=?""",
        (user["id"],),
    ).fetchall()

    if not cart_items:
        db.close()
        raise HTTPException(400, "Cart is empty")

    for item in cart_items:
        if item["stock"] < item["quantity"]:
            db.close()
            raise HTTPException(400, f"Not enough stock for {item['product_name']}")

    total = round(sum(item["price"] * item["quantity"] for item in cart_items), 2)

    cur = db.execute(
        """INSERT INTO orders (user_id, total_amount, status, shipping_name,
           shipping_address, shipping_city, shipping_postal, shipping_phone, payment_method)
           VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?)""",
        (
            user["id"], total, data.shipping_name, data.shipping_address,
            data.shipping_city, data.shipping_postal, data.shipping_phone, data.payment_method,
        ),
    )
    order_id = cur.lastrowid

    for item in cart_items:
        db.execute(
            """INSERT INTO order_items (order_id, product_id, product_name, quantity, price, size)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (order_id, item["product_id"], item["product_name"], item["quantity"], item["price"], item["size"]),
        )
        db.execute(
            "UPDATE products SET stock = stock - ? WHERE id=?",
            (item["quantity"], item["product_id"]),
        )

    db.execute("DELETE FROM cart_items WHERE user_id=?", (user["id"],))
    db.commit()

    order_row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    order_items = _get_order_items(db, order_id)
    db.close()
    return _format_order(order_row, order_items)
