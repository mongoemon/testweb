from typing import List, Optional

from pydantic import BaseModel, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username:  str           = Field(..., min_length=3,  example="john_doe")
    email:     str           = Field(...,                example="john@example.com")
    password:  str           = Field(..., min_length=6,  example="secret123")
    full_name: Optional[str] = Field(None,               example="John Doe")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "New user registration",
                    "value": {
                        "username": "john_doe",
                        "email": "john@example.com",
                        "password": "secret123",
                        "full_name": "John Doe",
                    },
                }
            ]
        }
    }


class UserLogin(BaseModel):
    username: str = Field(..., example="testuser")
    password: str = Field(..., example="test1234")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Regular user",
                    "value": {"username": "testuser", "password": "test1234"},
                },
                {
                    "summary": "Admin user",
                    "value": {"username": "admin", "password": "admin1234"},
                },
            ]
        }
    }


# ── Products ──────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name:        str            = Field(...,       example="Nike Air Max 90")
    description: Optional[str] = Field(None,       example="Classic cushioning with timeless design.")
    price:       float          = Field(..., gt=0, example=4990.0)
    stock:       int            = Field(0,   ge=0, example=50)
    category_id: Optional[int] = Field(None,       example=4)
    image_url:   Optional[str] = Field(None,       example="https://picsum.photos/seed/airmax90/600/400")
    brand:       Optional[str] = Field(None,       example="Nike")
    sizes:       Optional[List[str]] = Field([],   example=["38", "39", "40", "41", "42", "43"])
    is_active:   Optional[bool]= Field(True,       example=True)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "New shoe product",
                    "value": {
                        "name": "Nike Air Max 90",
                        "description": "Classic Air Max cushioning with a timeless design.",
                        "price": 4990.0,
                        "stock": 50,
                        "category_id": 4,
                        "image_url": "https://picsum.photos/seed/airmax90/600/400",
                        "brand": "Nike",
                        "sizes": ["38", "39", "40", "41", "42", "43", "44", "45"],
                        "is_active": True,
                    },
                }
            ]
        }
    }


# ── Cart ──────────────────────────────────────────────────────────────────────

class CartItemAdd(BaseModel):
    product_id: int = Field(..., gt=0, example=1)
    quantity:   int = Field(1,   ge=1, example=2)
    size:       str = Field("",        example="42")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Add 2 pairs of Nike Air Max 90 size 42",
                    "value": {"product_id": 1, "quantity": 2, "size": "42"},
                },
                {
                    "summary": "Add 1 item without size",
                    "value": {"product_id": 3, "quantity": 1, "size": ""},
                },
            ]
        }
    }


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, example=3)

    model_config = {
        "json_schema_extra": {
            "examples": [{"summary": "Update to 3 items", "value": {"quantity": 3}}]
        }
    }


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    shipping_name:    str = Field(..., example="John Doe")
    shipping_address: str = Field(..., example="123 Sukhumvit Rd, Khlong Toei")
    shipping_city:    str = Field(..., example="Bangkok")
    shipping_postal:  str = Field(..., example="10110")
    shipping_phone:   str = Field(..., example="081-234-5678")
    payment_method:   str = Field("credit_card", example="credit_card",
                                  description="credit_card | bank_transfer | cod")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Credit card payment",
                    "value": {
                        "shipping_name": "John Doe",
                        "shipping_address": "123 Sukhumvit Rd, Khlong Toei",
                        "shipping_city": "Bangkok",
                        "shipping_postal": "10110",
                        "shipping_phone": "081-234-5678",
                        "payment_method": "credit_card",
                    },
                },
                {
                    "summary": "Cash on delivery",
                    "value": {
                        "shipping_name": "Jane Smith",
                        "shipping_address": "456 Silom Rd",
                        "shipping_city": "Bangkok",
                        "shipping_postal": "10500",
                        "shipping_phone": "089-999-0000",
                        "payment_method": "cod",
                    },
                },
            ]
        }
    }


# ── User Profile ─────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, example="John Doe")
    email:     str           = Field(...,  example="john@example.com")


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=1, example="oldpassword")
    new_password:     str = Field(..., min_length=6, example="newpassword")


class AddressUpdate(BaseModel):
    default_shipping_name:    Optional[str] = Field(None, example="John Doe")
    default_shipping_address: Optional[str] = Field(None, example="123 Sukhumvit Rd")
    default_shipping_city:    Optional[str] = Field(None, example="Bangkok")
    default_shipping_postal:  Optional[str] = Field(None, example="10110")
    default_shipping_phone:   Optional[str] = Field(None, example="081-234-5678")
    default_payment_method:   Optional[str] = Field(None, example="credit_card")


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        example="confirmed",
        description="pending | confirmed | processing | shipped | delivered | cancelled",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"summary": "Confirm order",  "value": {"status": "confirmed"}},
                {"summary": "Mark shipped",   "value": {"status": "shipped"}},
                {"summary": "Mark delivered", "value": {"status": "delivered"}},
                {"summary": "Cancel order",   "value": {"status": "cancelled"}},
            ]
        }
    }
