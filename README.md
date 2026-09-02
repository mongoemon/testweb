# ShoesHub — E-Commerce Automation Testing Demo

เว็บไซต์ e-commerce ซื้อขายรองเท้าแบบเต็มรูปแบบ สร้างขึ้นเพื่อใช้เป็น target สำหรับ Playwright automation testing

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | HTML5 + Vanilla JS + Tailwind CSS (CDN) |
| Backend  | Python + FastAPI                    |
| Database | SQLite                              |
| Auth     | JWT (Bearer token) + bcrypt         |

---

## Prerequisites

- Python 3.10+
- pip

ตรวจสอบ version:

```bash
python --version
pip --version
```

---

## Setup & Run

### 1. Clone / เตรียม project

```bash
cd testweb
```

### 2. ติดตั้ง dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Seed ข้อมูลตัวอย่าง

```bash
python seed.py
```

สร้าง `shop.db` พร้อมข้อมูล:
- 4 หมวดหมู่ (Running, Casual, Basketball, Lifestyle)
- 12 สินค้า
- 3 user accounts
- 4 discount codes (ไม่มีกำหนดเวลา ใช้ได้ไม่จำกัด — สำหรับ spike/performance test)

### 4. Start server

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

หรือใช้ script ที่เตรียมไว้ (รัน step 2-4 อัตโนมัติ):

```bash
# Windows
run.bat

# Linux / macOS
chmod +x run.sh && ./run.sh
```

### 5. เปิด browser

| URL | คำอธิบาย |
|-----|----------|
| `http://localhost:8000/` | หน้าแรก |
| `http://localhost:8000/docs` | FastAPI Swagger UI (API docs) |
| `http://localhost:8000/admin/index.html` | Admin panel |

---

## Test Accounts

| Role  | Username   | Password    |
|-------|------------|-------------|
| Admin | `admin`    | `admin1234` |
| User  | `testuser` | `test1234`  |
| User  | `john_doe` | `john1234`  |

---

## หน้าของ Frontend

| URL | หน้า |
|-----|------|
| `/` | หน้าแรก – hero + featured products + categories |
| `/products.html` | รายการสินค้า – search, filter, sort, paginate |
| `/product.html?id={id}` | รายละเอียดสินค้า – size selector, add to cart |
| `/cart.html` | ตะกร้าสินค้า – update qty, remove, clear |
| `/checkout.html` | ชำระเงิน – shipping form, payment method |
| `/login.html` | เข้าสู่ระบบ |
| `/register.html` | สมัครสมาชิก |
| `/orders.html` | ประวัติคำสั่งซื้อ |
| `/order-detail.html?id={id}` | รายละเอียดคำสั่งซื้อ |
| `/admin/index.html` | Admin – dashboard stats |
| `/admin/products.html` | Admin – จัดการสินค้า (CRUD) |
| `/admin/orders.html` | Admin – จัดการออเดอร์ (update status) |
| `/admin/discounts.html` | Admin – จัดการ discount codes (CRUD) |

---

## API Endpoints

Base URL: `http://localhost:8000/api`

### Auth
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| POST | `/auth/register` | - | สมัครสมาชิก |
| POST | `/auth/login` | - | เข้าสู่ระบบ → คืน JWT token |
| GET | `/auth/me` | User | ดูข้อมูล user ปัจจุบัน |

### Products
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/products` | - | รายการสินค้า (filter/sort/paginate) |
| GET | `/products/{id}` | - | รายละเอียดสินค้า |
| POST | `/products` | Admin | สร้างสินค้า |
| PUT | `/products/{id}` | Admin | แก้ไขสินค้า |
| DELETE | `/products/{id}` | Admin | ลบสินค้า (soft delete) |
| GET | `/categories` | - | รายการหมวดหมู่ |

Query params สำหรับ `GET /products`:

| Param | Type | คำอธิบาย |
|-------|------|----------|
| `search` | string | ค้นหาชื่อ/แบรนด์/คำอธิบาย |
| `category` | int | filter ตาม category ID |
| `brand` | string | filter ตามแบรนด์ |
| `min_price` | float | ราคาขั้นต่ำ |
| `max_price` | float | ราคาสูงสุด |
| `size` | string | filter ตามไซส์ |
| `sort` | string | `newest`, `price_asc`, `price_desc`, `name_asc` |
| `page` | int | หน้าที่ (default: 1) |
| `limit` | int | จำนวนต่อหน้า (default: 12, max: 100) |

### Cart
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/cart` | User | ดูตะกร้า |
| POST | `/cart` | User | เพิ่มสินค้าลงตะกร้า |
| PUT | `/cart/{item_id}` | User | แก้ไขจำนวน |
| DELETE | `/cart/{item_id}` | User | ลบรายการ |
| DELETE | `/cart/clear` | User | ล้างตะกร้าทั้งหมด |

### Orders
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/orders` | User | ประวัติคำสั่งซื้อของตนเอง |
| POST | `/orders` | User | สั่งซื้อ (จากตะกร้า) รับ `discount_code` แบบ optional |
| GET | `/orders/{id}` | User | รายละเอียดคำสั่งซื้อ |

### Discount Codes
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| POST | `/discount-codes/validate` | User | ตรวจสอบ discount code ก่อน checkout |
| GET | `/admin/discount-codes` | Admin | รายการ discount codes ทั้งหมด |
| POST | `/admin/discount-codes` | Admin | สร้าง discount code ใหม่ |
| PUT | `/admin/discount-codes/{id}` | Admin | แก้ไข discount code |
| DELETE | `/admin/discount-codes/{id}` | Admin | ลบ discount code |

**Discount Code Types:**
- `percentage` — ส่วนลดเป็น % ของยอดรวม (เช่น 10 = 10%)
- `fixed` — ส่วนลดเป็นจำนวนเงินคงที่ (เช่น 100 = ลด ฿100)

**Seeded codes สำหรับ Spike/Performance Test** (ไม่มีกำหนดอายุ ใช้ได้ไม่จำกัด):

| Code | ประเภท | ส่วนลด |
|------|--------|--------|
| `SPIKE10` | percentage | 10% |
| `SPIKE20` | percentage | 20% |
| `FLAT100` | fixed | ฿100 |
| `FLAT500` | fixed | ฿500 |

### Admin
| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/admin/stats` | Admin | สถิติ dashboard |
| GET | `/admin/orders` | Admin | ออเดอร์ทั้งหมด (filter by status) |
| PUT | `/admin/orders/{id}/status` | Admin | อัปเดตสถานะออเดอร์ |
| GET | `/admin/users` | Admin | รายชื่อ users ทั้งหมด |

Order statuses: `pending` → `confirmed` → `processing` → `shipped` → `delivered` / `cancelled`

---

## data-testid Reference (สำหรับ Playwright)

### Navigation
```
[data-testid="navbar"]
[data-testid="nav-logo"]
[data-testid="nav-home"]
[data-testid="nav-products"]
[data-testid="nav-cart"]
[data-testid="nav-orders"]
[data-testid="nav-login"]
[data-testid="nav-register"]
[data-testid="nav-admin"]
[data-testid="nav-user-menu"]
[data-testid="nav-logout"]
[data-testid="cart-count"]
```

### Product Listing
```
[data-testid="search-input"]
[data-testid="search-btn"]
[data-testid="filter-category"]
[data-testid="filter-brand"]
[data-testid="filter-size"]
[data-testid="filter-sort"]
[data-testid="clear-filters-btn"]
[data-testid="product-grid"]
[data-testid="product-count"]
[data-testid="product-card"]          data-product-id="{id}"
[data-testid="product-name"]
[data-testid="product-brand"]
[data-testid="product-price"]
[data-testid="pagination"]
[data-testid="page-btn"]              data-page="{n}"
[data-testid="category-card"]         data-category-slug="{slug}"
[data-testid="empty-state"]
```

### Product Detail
```
[data-testid="product-detail"]
[data-testid="product-image"]
[data-testid="product-name"]
[data-testid="product-brand"]
[data-testid="product-price"]
[data-testid="product-stock"]
[data-testid="product-description"]
[data-testid="product-category"]
[data-testid="size-selector"]
[data-testid="size-option"]           data-size="{size}"
[data-testid="size-error"]
[data-testid="qty-input"]
[data-testid="qty-increase"]
[data-testid="qty-decrease"]
[data-testid="add-to-cart-btn"]
[data-testid="product-not-found"]
```

### Cart
```
[data-testid="cart-container"]
[data-testid="cart-items"]
[data-testid="cart-item"]             data-item-id="{id}"
[data-testid="cart-item-name"]
[data-testid="cart-item-price"]
[data-testid="cart-item-qty"]
[data-testid="cart-item-size"]
[data-testid="cart-item-subtotal"]
[data-testid="qty-increase-{id}"]
[data-testid="qty-decrease-{id}"]
[data-testid="remove-item-{id}"]
[data-testid="cart-total"]
[data-testid="clear-cart-btn"]
[data-testid="checkout-btn"]
[data-testid="continue-shopping-link"]
[data-testid="empty-cart"]
```

### Checkout
```
[data-testid="checkout-form"]
[data-testid="shipping-name"]
[data-testid="shipping-address"]
[data-testid="shipping-city"]
[data-testid="shipping-postal"]
[data-testid="shipping-phone"]
[data-testid="payment-methods"]
[data-testid="payment-credit-card"]
[data-testid="payment-bank-transfer"]
[data-testid="payment-cod"]
[data-testid="discount-code-input"]
[data-testid="apply-discount-btn"]
[data-testid="discount-message"]
[data-testid="discount-line"]
[data-testid="order-summary"]
[data-testid="checkout-total"]
[data-testid="place-order-btn"]
[data-testid="form-error"]
```

### Auth
```
[data-testid="login-form"]
[data-testid="username-input"]
[data-testid="password-input"]
[data-testid="toggle-password"]
[data-testid="login-btn"]
[data-testid="login-error"]
[data-testid="register-link"]

[data-testid="register-form"]
[data-testid="full-name-input"]
[data-testid="email-input"]
[data-testid="confirm-password-input"]
[data-testid="register-btn"]
[data-testid="register-error"]
[data-testid="register-success"]
[data-testid="login-link"]
```

### Orders
```
[data-testid="orders-container"]
[data-testid="order-card"]            data-order-id="{id}"
[data-testid="order-id"]
[data-testid="order-date"]
[data-testid="order-total"]
[data-testid="order-status"]
[data-testid="view-order-{id}"]
[data-testid="empty-orders"]

[data-testid="order-detail"]
[data-testid="order-success-banner"]
[data-testid="order-items"]
[data-testid="order-item"]
[data-testid="shipping-info"]
[data-testid="shipping-name"]
[data-testid="shipping-address"]
[data-testid="shipping-phone"]
[data-testid="payment-method"]
```

### Admin
```
[data-testid="admin-nav-dashboard"]
[data-testid="admin-nav-products"]
[data-testid="admin-nav-orders"]
[data-testid="admin-nav-discounts"]

[data-testid="stats-grid"]
[data-testid="stat-total-orders"]
[data-testid="stat-pending-orders"]
[data-testid="stat-revenue"]
[data-testid="stat-products"]
[data-testid="stat-users"]
[data-testid="recent-orders"]

[data-testid="add-product-btn"]
[data-testid="product-table"]
[data-testid="product-row"]           data-product-id="{id}"
[data-testid="edit-product-{id}"]
[data-testid="delete-product-{id}"]

[data-testid="product-modal"]
[data-testid="modal-close-btn"]
[data-testid="product-form"]
[data-testid="product-form-name"]
[data-testid="product-form-brand"]
[data-testid="product-form-category"]
[data-testid="product-form-price"]
[data-testid="product-form-stock"]
[data-testid="product-form-image"]
[data-testid="product-form-sizes"]
[data-testid="product-form-description"]
[data-testid="product-form-active"]
[data-testid="product-save-btn"]
[data-testid="product-cancel-btn"]
[data-testid="product-form-error"]

[data-testid="orders-table"]
[data-testid="order-row"]             data-order-id="{id}"
[data-testid="status-filter-select"]
[data-testid="status-select-{id}"]
[data-testid="order-status-{id}"]

[data-testid="add-discount-btn"]
[data-testid="discount-table"]
[data-testid="discount-row"]
[data-testid="edit-discount-btn"]
[data-testid="delete-discount-btn"]
[data-testid="discount-modal"]
[data-testid="discount-code-field"]
[data-testid="discount-desc-field"]
[data-testid="discount-type-field"]
[data-testid="discount-value-field"]
[data-testid="discount-expires-field"]
[data-testid="discount-maxuses-field"]
[data-testid="discount-active-field"]
[data-testid="save-discount-btn"]
```

### Global
```
[data-testid="toast"]                 data-type="success|error|info|warning"
```

---

## Project Structure

```
testweb/
├── backend/
│   ├── main.py           # FastAPI app entry point + static file mount
│   ├── observability.py  # JSON logging + request-id middleware (CloudWatch-ready)
│   ├── database.py       # SQLite init + connection helper
│   ├── models.py         # Pydantic request/response models
│   ├── auth_utils.py     # JWT creation/decode, password hash, Depends helpers
│   ├── seed.py           # One-time data seeding script
│   ├── requirements.txt
│   ├── shop.db           # SQLite database (generated on first run)
│   └── routes/
│       ├── auth.py       # /api/auth/*
│       ├── products.py   # /api/products/*, /api/categories
│       ├── cart.py       # /api/cart/*
│       ├── orders.py     # /api/orders/*
│       ├── admin.py      # /api/admin/*
│       └── discounts.py  # /api/discount-codes/*, /api/admin/discount-codes/*
├── docs/
│   └── QA_AWS_RUNBOOK.md  # QA guide: CloudWatch/SQS/SNS/S3/load-test/DR + IAM policy
├── .mcp.json.example     # AWS MCP servers config (cp → .mcp.json to activate)
└── frontend/
    ├── js/
    │   ├── api.js        # Fetch wrapper + all API calls
    │   ├── auth.js       # Auth state helpers (localStorage)
    │   └── nav.js        # Navbar injection, toast, formatters
    ├── index.html
    ├── products.html
    ├── product.html
    ├── cart.html
    ├── checkout.html     # มี discount code input
    ├── login.html
    ├── register.html
    ├── orders.html
    ├── order-detail.html
    └── admin/
        ├── index.html
        ├── products.html
        ├── orders.html
        └── discounts.html  # จัดการ discount codes
```

---

## Reset Database

ลบ DB เดิมแล้ว seed ใหม่:

```bash
cd backend
rm shop.db       # Windows: del shop.db
python seed.py
```

---

## Observability & AWS (สำหรับ QA)

### Structured logging (built-in, ไม่มี dependency เพิ่ม)

ทุก request ถูก log เป็น JSON บรรทัดเดียวออก stdout โดย `backend/observability.py`:

```json
{"ts":"2026-09-02T14:03:11.482000+00:00","level":"INFO","logger":"shoeshub",
 "message":"request","request_id":"7f3c...","method":"POST","path":"/api/orders",
 "status":201,"latency_ms":42.8}
```

- ทุก response มี header `x-request-id` (ส่ง header นี้เข้ามาเองได้เพื่อ trace ข้าม service)
- request ที่ช้า ≥ 1000ms ถูกยก level เป็น `WARNING`
- บน ECS / App Runner / Lambda: stdout เข้า CloudWatch Logs อัตโนมัติ แล้ว query ด้วย Logs Insights ได้ทันที (ตัวอย่าง query ใน [docs/QA_AWS_RUNBOOK.md](docs/QA_AWS_RUNBOOK.md) §3)
- เพิ่ม field เองในโค้ดได้ด้วย `log_event("order_placed", request_id=..., amount=...)`

### AWS Agent Toolkit + MCP (ตั้งค่าครั้งเดียวต่อเครื่อง)

ให้ Claude Code เข้าถึง AWS (CloudWatch / SQS / SNS / S3 / Backup) ผ่าน MCP:

```powershell
# 1. ติดตั้ง AWS CLI v2 (build ที่มี agent-toolkit)
irm 'https://awscli.amazonaws.com/v2/install.ps1' | iex

# 2. login ผ่านเบราว์เซอร์ (credentials อายุ 12 ชม. ต่อได้ 90 วัน)
aws configure set region ap-southeast-1 --profile shoeshub-qa
aws login --region ap-southeast-1 --profile shoeshub-qa
aws sts get-caller-identity --profile shoeshub-qa      # ต้องได้ Account/Arn

# 3. ติดตั้ง toolkit + AWS skills (23 ตัว → ~/.claude/skills/)
aws configure agent-toolkit --yes --region us-east-1 --profile shoeshub-qa
```

จากนั้นเพิ่ม MCP server ใน `~/.claude.json` (ขั้นนี้ auto-write มัก crash บน Windows Thai codepage — เติมมือ):

```json
"aws-mcp": {
  "command": "uvx",
  "args": ["mcp-proxy-for-aws@latest", "https://aws-mcp.us-east-1.api.aws/mcp",
           "--metadata", "INSTALL_SOURCE=aws-cli"],
  "env": { "AWS_MCP_PROXY_PROFILES": "shoeshub-qa" },
  "timeout": 100000,
  "transport": "stdio"
}
```

ปิด-เปิด Claude Code ใหม่ → `/mcp` ต้องเห็น `aws-mcp` connected

- **เรียกผ่าน MCP ห้ามใส่ `--profile`** — proxy กำหนดจาก env `AWS_MCP_PROXY_PROFILES` ให้แล้ว (ใส่ `--region` ได้)
- **ถ้าเจอ error `'charmap' codec`** ตอนรัน `aws` ให้ `chcp 65001` ก่อน หรือ set user env var `PYTHONUTF8=1`
- ทางเลือก: `.mcp.json.example` (project scope) รวม awslabs MCP servers รายตัว — `cp` เป็น `.mcp.json` ถ้าอยากใช้แทน `aws-mcp`

### เอกสารเต็ม

[docs/QA_AWS_RUNBOOK.md](docs/QA_AWS_RUNBOOK.md) — วิธีตรวจ CloudWatch / SQS-SNS / S3 / load-test bottleneck / DR drill แบบ QA + IAM policy read-only

---

## Deploy to Render.com (QA Environment)

> Free tier รองรับ **1 web service** ฟรี — ใช้ branch `qa` สำหรับ environment นี้

### ขั้นตอน

**1. ให้สิทธิ์ Render เข้าถึง repo**

Render ใช้ GitHub App ในการดึง repo list หากหา `testweb` ไม่เจอในหน้า New Web Service:

1. คลิก **Credentials → Manage** (มุมขวาของช่องค้นหา repo)
2. หน้า GitHub จะเปิด → ไปที่ **Repository access**
3. เลือก **Only select repositories** → เพิ่ม `mongoemon/testweb`
4. กด **Save** แล้วกลับมาที่ Render ค้นใหม่

**2. สร้าง Web Service**

- Render dashboard → **New → Web Service**
- เลือก repo `mongoemon/testweb`
- ตั้งค่าดังนี้:

| Field | Value |
|-------|-------|
| Name | `shoeshub-qa` |
| Branch | `qa` |
| Build Command | `cd backend && pip install -r requirements.txt` |
| Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |

**3. เพิ่ม Environment Variables**

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `qa` |
| `AUTO_SEED` | `true` |
| `SECRET_KEY` | *(กด Generate ให้ Render สร้างให้)* |

**4. Deploy**

กด **Create Web Service** — Render จะ build และ deploy อัตโนมัติ  
URL จะอยู่ในรูป `https://shoeshub-qa.onrender.com`

### หมายเหตุ

- **Free tier จะ sleep** หลังไม่มี traffic 15 นาที — request แรกหลัง sleep จะช้า ~30 วินาที
- **Database เป็น ephemeral** — ข้อมูลจะหายทุกครั้งที่ redeploy (จึงตั้ง `AUTO_SEED=true` ให้ seed ใหม่อัตโนมัติ)
- **Blueprint** (`render.yaml`) ใช้สร้างหลาย service พร้อมกันได้ แต่ต้องใช้ plan แบบเสียเงิน

### Environments

| Environment | Branch | วัตถุประสงค์ |
|-------------|--------|-------------|
| DEV | local | นักพัฒนาทดสอบ local |
| QA | `qa` | QA team ทดสอบหลัง dev เสร็จ |
| STAGING | `staging` | ทดสอบ pre-production |
| PROD | `main` | Production จริง |
