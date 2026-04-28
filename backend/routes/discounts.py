from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_admin_user, get_current_user
from database import get_db
from discount_utils import apply_discount, check_code_valid
from models import DiscountCodeCreate, DiscountCodeUpdate, DiscountValidateRequest

# Two routers to mirror the existing pattern (prefix per resource group)
discount_router = APIRouter(prefix="/api/discount-codes", tags=["discounts"])
admin_router    = APIRouter(prefix="/api/admin/discount-codes", tags=["discounts"])

# Expose a single `router` tuple so main.py can include both cleanly
router = (discount_router, admin_router)


def _row_to_dict(row) -> dict:
    return dict(row)


# ── user endpoint — validate ──────────────────────────────────────────────────

@discount_router.post(
    "/validate",
    summary="Validate discount code",
    description="ตรวจสอบว่า discount code ใช้ได้หรือไม่ และคืนข้อมูลส่วนลด",
)
def validate_discount(body: DiscountValidateRequest, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        dc = check_code_valid(db, body.code)
    finally:
        db.close()
    return {
        "code":           dc["code"],
        "description":    dc["description"],
        "discount_type":  dc["discount_type"],
        "discount_value": dc["discount_value"],
        "expires_at":     dc["expires_at"],
        "max_uses":       dc["max_uses"],
        "current_uses":   dc["current_uses"],
    }


# ── admin endpoints ───────────────────────────────────────────────────────────

@admin_router.get("", summary="List all discount codes [Admin]")
def list_discount_codes(admin: dict = Depends(get_admin_user)):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM discount_codes ORDER BY created_at DESC"
    ).fetchall()
    db.close()
    return [_row_to_dict(r) for r in rows]


@admin_router.post("", summary="Create discount code [Admin]", status_code=201)
def create_discount_code(data: DiscountCodeCreate, admin: dict = Depends(get_admin_user)):
    db = get_db()
    existing = db.execute(
        "SELECT id FROM discount_codes WHERE code=? COLLATE NOCASE", (data.code,)
    ).fetchone()
    if existing:
        db.close()
        raise HTTPException(400, f"Code '{data.code}' already exists")
    cur = db.execute(
        """INSERT INTO discount_codes
           (code, description, discount_type, discount_value, expires_at, max_uses, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data.code.upper(),
            data.description,
            data.discount_type,
            data.discount_value,
            data.expires_at,
            data.max_uses,
            1 if data.is_active else 0,
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM discount_codes WHERE id=?", (cur.lastrowid,)).fetchone()
    db.close()
    return _row_to_dict(row)


@admin_router.put("/{code_id}", summary="Update discount code [Admin]")
def update_discount_code(code_id: int, data: DiscountCodeUpdate, admin: dict = Depends(get_admin_user)):
    db = get_db()
    row = db.execute("SELECT * FROM discount_codes WHERE id=?", (code_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Discount code not found")
    current = _row_to_dict(row)
    fields = {
        "description":    data.description    if data.description    is not None else current["description"],
        "discount_type":  data.discount_type  if data.discount_type  is not None else current["discount_type"],
        "discount_value": data.discount_value if data.discount_value is not None else current["discount_value"],
        "expires_at":     data.expires_at     if data.expires_at     is not None else current["expires_at"],
        "max_uses":       data.max_uses       if data.max_uses       is not None else current["max_uses"],
        "is_active":      (1 if data.is_active else 0) if data.is_active is not None else current["is_active"],
    }
    db.execute(
        """UPDATE discount_codes SET description=?, discount_type=?, discount_value=?,
           expires_at=?, max_uses=?, is_active=? WHERE id=?""",
        (fields["description"], fields["discount_type"], fields["discount_value"],
         fields["expires_at"], fields["max_uses"], fields["is_active"], code_id),
    )
    db.commit()
    updated = db.execute("SELECT * FROM discount_codes WHERE id=?", (code_id,)).fetchone()
    db.close()
    return _row_to_dict(updated)


@admin_router.delete("/{code_id}", summary="Delete discount code [Admin]")
def delete_discount_code(code_id: int, admin: dict = Depends(get_admin_user)):
    db = get_db()
    row = db.execute("SELECT id FROM discount_codes WHERE id=?", (code_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Discount code not found")
    db.execute("DELETE FROM discount_codes WHERE id=?", (code_id,))
    db.commit()
    db.close()
    return {"message": "Discount code deleted"}
