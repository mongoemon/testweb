from datetime import datetime, timezone

from fastapi import HTTPException


def check_code_valid(db, code: str) -> dict:
    """Return the discount_code row or raise 400/404."""
    row = db.execute(
        "SELECT * FROM discount_codes WHERE code=? COLLATE NOCASE", (code,)
    ).fetchone()
    if not row:
        raise HTTPException(404, f"Discount code '{code}' not found")
    dc = dict(row)
    if not dc["is_active"]:
        raise HTTPException(400, "Discount code is inactive")
    if dc["expires_at"]:
        try:
            exp = datetime.fromisoformat(dc["expires_at"])
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > exp:
                raise HTTPException(400, "Discount code has expired")
        except ValueError:
            pass
    if dc["max_uses"] is not None and dc["current_uses"] >= dc["max_uses"]:
        raise HTTPException(400, "Discount code has reached its usage limit")
    return dc


def apply_discount(subtotal: float, dc: dict) -> float:
    """Return discount amount (always >= 0, never exceeds subtotal)."""
    if dc["discount_type"] == "percentage":
        amount = round(subtotal * dc["discount_value"] / 100, 2)
    else:
        amount = dc["discount_value"]
    return min(amount, subtotal)
