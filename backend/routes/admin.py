from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_admin_user, user_to_dict
from database import get_db
from models import OrderStatusUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_STATUSES = {"pending", "confirmed", "processing", "shipped", "delivered", "cancelled"}

_RESPONSES_403 = {403: {"description": "Admin access required"}}
_RESPONSES_401 = {401: {"description": "Not authenticated"}}


@router.get(
    "/stats",
    summary="Dashboard statistics [Admin]",
    description=(
        "คืนสถิติภาพรวมของระบบ:\n"
        "- `total_orders` — จำนวน order ทั้งหมด\n"
        "- `pending_orders` — order ที่รอดำเนินการ\n"
        "- `total_revenue` — รายได้รวม (ไม่นับ cancelled)\n"
        "- `total_products` — สินค้าที่ active\n"
        "- `total_users` — จำนวน user (ไม่นับ admin)\n"
        "- `recent_orders` — 5 order ล่าสุด"
    ),
    response_description="Dashboard stats object",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "total_orders": 42,
                        "total_revenue": 189560.0,
                        "total_products": 12,
                        "total_users": 3,
                        "pending_orders": 5,
                        "recent_orders": [
                            {
                                "id": 42,
                                "total_amount": 9980.0,
                                "status": "pending",
                                "created_at": "2024-01-15 10:30:00",
                                "username": "testuser",
                            }
                        ],
                    }
                }
            }
        },
        **_RESPONSES_403,
        **_RESPONSES_401,
    },
)
def get_stats(_=Depends(get_admin_user)):
    db = get_db()
    total_orders   = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue  = db.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status != 'cancelled'").fetchone()[0]
    total_products = db.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0]
    total_users    = db.execute("SELECT COUNT(*) FROM users WHERE is_admin=0").fetchone()[0]
    pending_orders = db.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
    recent_orders  = db.execute(
        """SELECT o.id, o.total_amount, o.status, o.created_at, u.username
           FROM orders o JOIN users u ON u.id = o.user_id
           ORDER BY o.created_at DESC LIMIT 5"""
    ).fetchall()
    db.close()
    return {
        "total_orders":   total_orders,
        "total_revenue":  round(total_revenue, 2),
        "total_products": total_products,
        "total_users":    total_users,
        "pending_orders": pending_orders,
        "recent_orders":  [dict(r) for r in recent_orders],
    }


@router.get(
    "/orders",
    summary="List all orders [Admin]",
    description=(
        "คืน order ทุกรายการของทุก user พร้อม order items\n\n"
        "กรอง status ได้ด้วย query param: `?status=pending`\n\n"
        "**Status ที่ใช้ได้:** `pending` | `confirmed` | `processing` | `shipped` | `delivered` | `cancelled`"
    ),
    response_description="Array of all orders (newest first)",
    responses={
        **_RESPONSES_403,
        **_RESPONSES_401,
    },
)
def list_all_orders(status: str = None, _=Depends(get_admin_user)):
    db = get_db()
    if status:
        rows = db.execute(
            """SELECT o.*, u.username FROM orders o JOIN users u ON u.id=o.user_id
               WHERE o.status=? ORDER BY o.created_at DESC""",
            (status,),
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT o.*, u.username FROM orders o JOIN users u ON u.id=o.user_id
               ORDER BY o.created_at DESC"""
        ).fetchall()
    orders = []
    for row in rows:
        o = dict(row)
        items = db.execute("SELECT * FROM order_items WHERE order_id=?", (o["id"],)).fetchall()
        o["items"] = [dict(i) for i in items]
        orders.append(o)
    db.close()
    return orders


@router.put(
    "/orders/{order_id}/status",
    summary="Update order status [Admin]",
    description=(
        "อัปเดตสถานะ order\n\n"
        "**Flow ปกติ:** `pending` → `confirmed` → `processing` → `shipped` → `delivered`\n\n"
        "**Status ที่ใช้ได้:** `pending` | `confirmed` | `processing` | `shipped` | `delivered` | `cancelled`"
    ),
    response_description="Updated order object",
    responses={
        **_RESPONSES_403,
        **_RESPONSES_401,
        400: {"description": "Invalid status value"},
        404: {"description": "Order not found"},
    },
)
def update_order_status(order_id: int, data: OrderStatusUpdate, _=Depends(get_admin_user)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}")
    db = get_db()
    existing = db.execute("SELECT id FROM orders WHERE id=?", (order_id,)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, "Order not found")
    db.execute(
        "UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (data.status, order_id),
    )
    db.commit()
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    db.close()
    return dict(row)


@router.get(
    "/users",
    summary="List all users [Admin]",
    description="คืนรายชื่อ user ทั้งหมด (รวม admin) ไม่แสดง password hash",
    response_description="Array of user objects",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@shoeshub.com",
                            "full_name": "Admin User",
                            "is_admin": True,
                            "created_at": "2024-01-01 00:00:00",
                        },
                        {
                            "id": 2,
                            "username": "testuser",
                            "email": "test@shoeshub.com",
                            "full_name": "Test User",
                            "is_admin": False,
                            "created_at": "2024-01-01 00:00:00",
                        },
                    ]
                }
            }
        },
        **_RESPONSES_403,
        **_RESPONSES_401,
    },
)
def list_users(_=Depends(get_admin_user)):
    db = get_db()
    rows = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    db.close()
    return [user_to_dict(dict(r)) for r in rows]
