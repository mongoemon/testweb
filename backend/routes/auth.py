import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from auth_utils import create_token, get_current_user, hash_password, user_to_dict, verify_password
from database import get_db
from models import AddressUpdate, PasswordUpdate, ProfileUpdate, UserLogin, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])

_TOKEN_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 2,
        "username": "testuser",
        "email": "test@shoeshub.com",
        "full_name": "Test User",
        "is_admin": False,
        "created_at": "2024-01-01 00:00:00",
    },
}

_RESPONSES_401 = {401: {"description": "Invalid credentials or token expired"}}
_RESPONSES_400 = {400: {"description": "Validation error (duplicate username/email, weak password)"}}


def _build_response(user: dict) -> dict:
    return {
        "access_token": create_token(user["id"]),
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


@router.post(
    "/register",
    summary="Register a new user",
    description=(
        "Create a new user account and receive a JWT token immediately.\n\n"
        "**Constraints:**\n"
        "- `username` ต้องมีอย่างน้อย 3 ตัวอักษร และไม่ซ้ำกัน\n"
        "- `email` ต้องไม่ซ้ำกัน\n"
        "- `password` ต้องมีอย่างน้อย 6 ตัวอักษร"
    ),
    response_description="JWT access token + user profile",
    responses={
        200: {"content": {"application/json": {"example": _TOKEN_EXAMPLE}}},
        **_RESPONSES_400,
    },
)
def register(data: UserRegister):
    if len(data.username) < 3:
        raise HTTPException(400, "Username must be at least 3 characters")
    if len(data.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (data.username.strip(), data.email.strip(), hash_password(data.password), data.full_name),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE username = ?", (data.username.strip(),)).fetchone()
        return _build_response(dict(user))
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise HTTPException(400, "Username already taken")
        if "email" in msg:
            raise HTTPException(400, "Email already registered")
        raise HTTPException(400, "Registration failed")
    finally:
        db.close()


@router.post(
    "/login",
    summary="Login and get JWT token",
    description=(
        "ยืนยันตัวตนด้วย username/password และรับ JWT token สำหรับใช้ใน header:\n\n"
        "```\nAuthorization: Bearer <access_token>\n```\n\n"
        "**Test accounts:**\n"
        "- User: `testuser` / `test1234`\n"
        "- Admin: `admin` / `admin1234`"
    ),
    response_description="JWT access token + user profile",
    responses={
        200: {"content": {"application/json": {"example": _TOKEN_EXAMPLE}}},
        **_RESPONSES_401,
    },
)
def login(data: UserLogin):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (data.username.strip(),)).fetchone()
    db.close()
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid username or password")
    return _build_response(dict(user))


@router.get(
    "/me",
    summary="Get current user profile",
    description="คืนข้อมูล user ที่ login อยู่ ต้องแนบ Bearer token ใน Authorization header",
    response_description="User profile object",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "username": "testuser",
                        "email": "test@shoeshub.com",
                        "full_name": "Test User",
                        "is_admin": False,
                        "created_at": "2024-01-01 00:00:00",
                    }
                }
            }
        },
        **_RESPONSES_401,
    },
)
def get_me(user: dict = Depends(get_current_user)):
    return user_to_dict(user)


@router.put("/profile", summary="Update name and email")
def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        db.execute(
            "UPDATE users SET full_name = ?, email = ? WHERE id = ?",
            (data.full_name, data.email.strip(), user["id"]),
        )
        db.commit()
        updated = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
        return user_to_dict(dict(updated))
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Email already in use")
    finally:
        db.close()


@router.put("/password", summary="Change password")
def update_password(data: PasswordUpdate, user: dict = Depends(get_current_user)):
    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(400, "Current password is incorrect")
    db = get_db()
    try:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(data.new_password), user["id"]),
        )
        db.commit()
        return {"message": "Password updated"}
    finally:
        db.close()


@router.put("/address", summary="Save default shipping address and payment method")
def update_address(data: AddressUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        db.execute(
            """UPDATE users SET
               default_shipping_name    = ?,
               default_shipping_address = ?,
               default_shipping_city    = ?,
               default_shipping_postal  = ?,
               default_shipping_phone   = ?,
               default_payment_method   = ?
             WHERE id = ?""",
            (
                data.default_shipping_name,
                data.default_shipping_address,
                data.default_shipping_city,
                data.default_shipping_postal,
                data.default_shipping_phone,
                data.default_payment_method or "credit_card",
                user["id"],
            ),
        )
        db.commit()
        updated = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
        return user_to_dict(dict(updated))
    finally:
        db.close()
