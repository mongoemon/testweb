import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db, migrate_db
from routes import admin, auth, cart, orders, products
from seed import seed

TAGS_METADATA = [
    {
        "name": "auth",
        "description": (
            "Authentication endpoints. Use **login** to get a JWT token, then click "
            "**Authorize** (🔒) at the top of this page and paste the token to test "
            "protected endpoints."
        ),
    },
    {
        "name": "products",
        "description": (
            "Public product catalog and admin CRUD. "
            "GET endpoints require no authentication. POST/PUT/DELETE require **Admin** token."
        ),
    },
    {
        "name": "cart",
        "description": "Shopping cart management. All endpoints require a **User** token.",
    },
    {
        "name": "orders",
        "description": "Order placement and history. All endpoints require a **User** token.",
    },
    {
        "name": "admin",
        "description": (
            "Admin-only endpoints: dashboard stats, all orders, user list. "
            "Require an **Admin** token (username: `admin`, password: `admin1234`)."
        ),
    },
]

DESCRIPTION = """
## ShoesHub API

E-Commerce REST API สำหรับระบบซื้อขายรองเท้า ออกแบบมาเพื่อใช้เป็น target สำหรับ **Playwright automation testing**

---

### Quick Start

1. เรียก **POST /api/auth/login** ด้วย `{"username": "testuser", "password": "test1234"}`
2. คัดลอก `access_token` จาก response
3. กดปุ่ม **Authorize 🔒** มุมบนขวา แล้วใส่ token ในช่อง `HTTPBearer`
4. ทดสอบ endpoint ที่ต้องการได้เลย

---

### Test Accounts

| Role  | Username   | Password    |
|-------|------------|-------------|
| Admin | `admin`    | `admin1234` |
| User  | `testuser` | `test1234`  |
| User  | `john_doe` | `john1234`  |

---

### Order Status Flow

`pending` → `confirmed` → `processing` → `shipped` → `delivered`
(หรือ `cancelled` ได้จากทุก status)
"""

app = FastAPI(
    title="ShoesHub API",
    version="1.0.0",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "ShoesHub Dev",
        "email": "dev@shoeshub.example.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")


@app.on_event("startup")
def startup():
    init_db()
    migrate_db()
    seed()
    print("[OK] Database initialized")
    print(f"[OK] Frontend : http://localhost:8000/")
    print(f"[OK] Swagger  : http://localhost:8000/docs")
    print(f"[OK] ReDoc    : http://localhost:8000/redoc")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
