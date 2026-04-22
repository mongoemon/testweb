# ShoesHub — Test Plan

ระบบ e-commerce ซื้อขายรองเท้า | FastAPI + SQLite (backend) · Vanilla JS + Tailwind (frontend)

---

## สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [สภาพแวดล้อมการทดสอบ](#2-สภาพแวดล้อมการทดสอบ)
3. [บัญชีทดสอบ](#3-บัญชีทดสอบ)
4. [รายการหน้าเว็บ (Page Inventory)](#4-รายการหน้าเว็บ-page-inventory)
5. [Data-testid Reference](#5-data-testid-reference)
6. [User Journey Scenarios](#6-user-journey-scenarios)
   - [AUTH — Authentication](#auth--authentication)
   - [HOME — Homepage](#home--homepage)
   - [PROD — Product Catalog](#prod--product-catalog)
   - [DETAIL — Product Detail](#detail--product-detail)
   - [CART — Shopping Cart](#cart--shopping-cart)
   - [CHK — Checkout](#chk--checkout)
   - [ORD — Order History & Detail](#ord--order-history--detail)
   - [PROF — User Profile](#prof--user-profile)
   - [DASH — Admin Dashboard](#dash--admin-dashboard)
   - [APROD — Admin Product Management](#aprod--admin-product-management)
   - [AORD — Admin Order Management](#aord--admin-order-management)
   - [I18N — Multi-language](#i18n--multi-language)
   - [NAV — Navigation](#nav--navigation)

---

## 1. ภาพรวมระบบ

### Architecture

```
Browser (Vanilla JS + Tailwind)
    ↕ HTTP/REST (JSON)
FastAPI (Python)
    ↕ SQLite
shop.db
```

### Role & สิทธิ์การใช้งาน

| Role | เงื่อนไข | สิ่งที่ทำได้ |
|------|----------|-------------|
| **Guest** | ไม่ได้ login | ดูสินค้า, ค้นหา, สมัคร/login |
| **User** | Login แล้ว (`is_admin = 0`) | ทุกอย่างของ Guest + ตะกร้า, ออเดอร์, โปรไฟล์ |
| **Admin** | Login แล้ว (`is_admin = 1`) | ทุกอย่างของ User + จัดการสินค้า/ออเดอร์/dashboard |

### Order Status Flow

```
pending → confirmed → processing → shipped → delivered
                                                ↑
                              cancelled ←───────┘ (ได้จากทุก status)
```

---

## 2. สภาพแวดล้อมการทดสอบ

### การรันระบบ

```bash
# Windows
run.bat

# macOS / Linux
./run.sh
```

### URLs

| URL | คำอธิบาย |
|-----|----------|
| `http://localhost:8000/` | Frontend (หน้าหลัก) |
| `http://localhost:8000/docs` | Swagger UI — ทดสอบ API |
| `http://localhost:8000/redoc` | ReDoc — เอกสาร API |

### รีเซ็ต test data

```bash
cd backend
rm shop.db       # หรือ del shop.db บน Windows
python seed.py
```

---

## 3. บัญชีทดสอบ

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin | `admin` | `admin1234` | admin@shoeshub.com |
| User | `testuser` | `test1234` | test@shoeshub.com |
| User | `john_doe` | `john1234` | john@example.com |

---

## 4. รายการหน้าเว็บ (Page Inventory)

| URL | หน้า | สิทธิ์ที่ต้องการ |
|-----|------|-----------------|
| `/` | Home — hero, categories, featured products | Public |
| `/products.html` | Product listing — search, filter, sort | Public |
| `/product.html?id={id}` | Product detail — info, add to cart | Public (ดู) / User (ซื้อ) |
| `/cart.html` | Shopping cart | User |
| `/checkout.html` | Checkout form | User |
| `/orders.html` | Order history list | User |
| `/order-detail.html?id={id}` | Order detail | User (เจ้าของ order เท่านั้น) |
| `/profile.html` | User profile — personal, password, address | User |
| `/login.html` | Login form | Guest (redirect ถ้า login แล้ว) |
| `/register.html` | Register form | Guest (redirect ถ้า login แล้ว) |
| `/admin/index.html` | Admin dashboard | Admin |
| `/admin/products.html` | Admin product management | Admin |
| `/admin/orders.html` | Admin order management | Admin |

---

## 5. Data-testid Reference

### Navbar (`nav.js` — ปรากฏทุกหน้า)

| testid | Element |
|--------|---------|
| `navbar` | `<nav>` element |
| `nav-logo` | ShoesHub logo link |
| `nav-home` | Home link |
| `nav-products` | Products link |
| `nav-cart` | Cart icon link |
| `cart-count` | Cart badge (จำนวนสินค้า) |
| `nav-orders` | Orders link |
| `nav-admin` | Admin link (Admin เท่านั้น) |
| `nav-user-menu` | User dropdown button (ชื่อ user) |
| `nav-profile` | Profile link ใน dropdown |
| `nav-logout` | Logout button ใน dropdown |
| `nav-login` | Login link (Guest เท่านั้น) |
| `nav-register` | Register link (Guest เท่านั้น) |

### Toast

| testid | Element |
|--------|---------|
| `toast` | Toast notification (`data-type="success/error/info/warning"`) |

### Home (`/`)

| testid | Element |
|--------|---------|
| `hero-section` | Hero banner section |
| `hero-shop-btn` | CTA button "เลือกซื้อเลย" |
| `categories-section` | Category cards grid |
| `featured-products` | Featured products grid |
| `view-all-link` | "ดูทั้งหมด" link |

### Products (`/products.html`)

| testid | Element |
|--------|---------|
| `search-input` | Search box |
| `category-select` | Category dropdown |
| `brand-select` | Brand dropdown |
| `size-select` | Size dropdown |
| `sort-select` | Sort dropdown |
| `product-count` | Product count label |
| `products-grid` | Products grid container |
| `product-card` | Individual product card |
| `product-card-name` | Product name in card |
| `product-card-price` | Price in card |
| `product-card-image` | Product image |

### Product Detail (`/product.html`)

| testid | Element |
|--------|---------|
| `product-name` | Product name heading |
| `product-price` | Price display |
| `product-brand` | Brand label |
| `product-description` | Description text |
| `product-stock` | Stock status text |
| `size-buttons` | Container ของ size buttons |
| `size-btn-{size}` | Size button (เช่น `size-btn-42`) |
| `quantity-input` | Quantity input |
| `qty-decrease` | Decrease quantity button |
| `qty-increase` | Increase quantity button |
| `add-to-cart-btn` | Add to Cart button |
| `size-error` | Error message เมื่อไม่เลือก size |
| `back-to-products` | Back link |

### Cart (`/cart.html`)

| testid | Element |
|--------|---------|
| `cart-container` | Main cart container |
| `cart-items` | Cart items list |
| `cart-item` | Individual cart item row |
| `item-name` | Product name in cart |
| `item-size` | Size label |
| `item-quantity` | Quantity input |
| `item-subtotal` | Subtotal per item |
| `remove-item-{id}` | Remove button per item |
| `clear-cart-btn` | Clear cart button |
| `cart-total` | Total price |
| `checkout-btn` | Checkout button |
| `empty-cart` | Empty cart message |

### Checkout (`/checkout.html`)

| testid | Element |
|--------|---------|
| `checkout-form` | Main checkout form |
| `shipping-name` | Name input |
| `shipping-address` | Address input |
| `shipping-city` | City input |
| `shipping-postal` | Postal code input |
| `shipping-phone` | Phone input |
| `payment-methods` | Payment method container |
| `payment-credit-card` | Credit card radio |
| `payment-bank-transfer` | Bank transfer radio |
| `payment-cod` | COD radio |
| `order-summary` | Order summary panel |
| `checkout-total` | Total price in summary |
| `place-order-btn` | Submit button |
| `form-error` | Error message |

### Orders (`/orders.html`)

| testid | Element |
|--------|---------|
| `orders-container` | Main container |
| `order-card` | Individual order card |
| `order-id` | Order ID text |
| `order-date` | Order date |
| `order-total` | Order total |
| `order-status` | Status badge |
| `view-order-{id}` | View detail link per order |
| `empty-orders` | Empty state message |

### Order Detail (`/order-detail.html`)

| testid | Element |
|--------|---------|
| `order-detail-container` | Main container |
| `success-banner` | Success message (เมื่อมาจาก checkout) |
| `order-number` | Order ID |
| `order-status-badge` | Status badge |
| `order-items-list` | Items list |
| `order-grand-total` | Grand total |
| `shipping-info` | Shipping address block |
| `payment-info` | Payment method block |
| `continue-shopping-btn` | Continue shopping link |
| `back-to-orders` | Back to orders link |

### Profile (`/profile.html`)

| testid | Element |
|--------|---------|
| `form-personal` | Personal info form |
| `profile-fullname` | Full name input |
| `profile-email` | Email input |
| `profile-personal-save` | Save personal info button |
| `profile-personal-error` | Error message |
| `form-password` | Change password form |
| `profile-current-password` | Current password input |
| `profile-new-password` | New password input |
| `profile-confirm-password` | Confirm password input |
| `profile-password-save` | Change password button |
| `profile-password-error` | Error message |
| `form-address` | Address form |
| `profile-shipping-name` | Shipping name input |
| `profile-shipping-address` | Shipping address input |
| `profile-shipping-city` | City input |
| `profile-shipping-postal` | Postal code input |
| `profile-shipping-phone` | Phone input |
| `payment-credit-card` | Credit card radio |
| `payment-bank-transfer` | Bank transfer radio |
| `payment-cod` | COD radio |
| `profile-address-save` | Save address button |
| `profile-address-error` | Error message |

### Admin — Dashboard (`/admin/index.html`)

| testid | Element |
|--------|---------|
| `stats-grid` | Stats cards grid |
| `stat-total-orders` | Total orders card |
| `stat-pending-orders` | Pending orders card |
| `stat-revenue` | Revenue card |
| `stat-products` | Active products card |
| `stat-users` | Users count card |
| `recent-orders` | Recent orders table |
| `admin-nav-dashboard` | Dashboard nav link |
| `admin-nav-products` | Products nav link |
| `admin-nav-orders` | Orders nav link |

### Admin — Products (`/admin/products.html`)

| testid | Element |
|--------|---------|
| `product-table` | Products table body |
| `product-row` | Individual row (`data-product-id`) |
| `add-product-btn` | Add product button |
| `product-modal` | Add/Edit modal |
| `modal-close-btn` | Close modal button |
| `product-form` | Product form in modal |
| `product-form-name` | Name input |
| `product-form-brand` | Brand input |
| `product-form-category` | Category select |
| `product-form-price` | Price input |
| `product-form-stock` | Stock input |
| `product-form-image` | Image URL input |
| `product-form-sizes` | Sizes input |
| `product-form-description` | Description textarea |
| `product-form-active` | Active checkbox |
| `product-save-btn` | Save button |
| `product-cancel-btn` | Cancel button |
| `product-form-error` | Error message |
| `edit-product-{id}` | Edit button per row |
| `delete-product-{id}` | Delete button per row |

### Admin — Orders (`/admin/orders.html`)

| testid | Element |
|--------|---------|
| `status-filter-select` | Status filter dropdown |
| `orders-table` | Orders table body |
| `order-row` | Individual row (`data-order-id`) |
| `order-status-{id}` | Current status badge per order |
| `status-select-{id}` | Status change dropdown per order |
| `no-orders` | Empty state message |

---

## 6. User Journey Scenarios

> **อ่านก่อน:** แต่ละ Test Case มีโครงสร้างดังนี้
> - **Role** — สิทธิ์ที่ต้องการ
> - **Precondition** — สภาพก่อนเริ่มทดสอบ
> - **Steps** — ขั้นตอน
> - **Expected** — ผลลัพธ์ที่ต้องการ
> - **testids** — elements ที่ควร assert

---

### AUTH — Authentication

---

#### TC-AUTH-01 · สมัครสมาชิกสำเร็จ

**Role:** Guest  
**Precondition:** ยังไม่มีบัญชีในระบบ

**Steps:**
1. เปิด `/register.html`
2. กรอก Full Name: `"Test New User"`
3. กรอก Username: `"newuser01"`
4. กรอก Email: `"newuser01@test.com"`
5. กรอก Password: `"pass1234"`
6. กรอก Confirm Password: `"pass1234"`
7. กดปุ่ม Submit

**Expected:**
- แสดง toast success
- redirect ไปหน้า `/` (home)
- navbar แสดงชื่อ `"newuser01"` แทนปุ่ม Login/Register

**testids:** `nav-register` → กรอก form → `toast[data-type="success"]` → `nav-user-menu`

---

#### TC-AUTH-02 · สมัครซ้ำ — username ซ้ำ

**Role:** Guest  
**Precondition:** มี `testuser` อยู่ในระบบแล้ว

**Steps:**
1. เปิด `/register.html`
2. กรอก Username: `"testuser"` (ซ้ำ)
3. กรอกข้อมูลอื่นให้ครบ
4. กดปุ่ม Submit

**Expected:**
- ไม่ redirect
- แสดงข้อความ error ใน form ว่า username ถูกใช้แล้ว
- ยังอยู่หน้า register

---

#### TC-AUTH-03 · สมัคร — password สั้นเกินไป (< 6 ตัว)

**Role:** Guest

**Steps:**
1. เปิด `/register.html`
2. กรอก Password: `"abc"` (3 ตัว)
3. กดปุ่ม Submit

**Expected:**
- แสดง error message ก่อน submit (client-side validation) หรือจาก API
- ไม่สร้าง account ใหม่

---

#### TC-AUTH-04 · สมัคร — password ไม่ตรงกัน

**Role:** Guest

**Steps:**
1. เปิด `/register.html`
2. กรอก Password: `"pass1234"` / Confirm: `"pass9999"`
3. กดปุ่ม Submit

**Expected:**
- แสดง error `"รหัสผ่านไม่ตรงกัน"`
- ไม่ส่ง request ไป API

---

#### TC-AUTH-05 · Login สำเร็จ — User

**Role:** Guest  
**Precondition:** มี `testuser / test1234` ในระบบ

**Steps:**
1. เปิด `/login.html`
2. กรอก Username: `"testuser"`, Password: `"test1234"`
3. กดปุ่ม Login

**Expected:**
- redirect ไป `/`
- navbar แสดง `"testuser"` พร้อม cart icon
- ไม่เห็นปุ่ม Login/Register

**testids:** `nav-login` → กรอก → `nav-user-menu` (แสดงชื่อ)

---

#### TC-AUTH-06 · Login สำเร็จ — Admin

**Role:** Guest  
**Precondition:** มี `admin / admin1234` ในระบบ

**Steps:**
1. Login ด้วย `admin / admin1234`

**Expected:**
- redirect ไป `/`
- navbar แสดงทั้ง cart, orders, **และ Admin link**
- `[data-testid="nav-admin"]` ปรากฏ

---

#### TC-AUTH-07 · Login ผิด — wrong password

**Role:** Guest

**Steps:**
1. เปิด `/login.html`
2. กรอก Username: `"testuser"`, Password: `"wrongpass"`
3. กดปุ่ม Login

**Expected:**
- ไม่ redirect
- แสดง error message ใน form
- ยังอยู่หน้า login

---

#### TC-AUTH-08 · Logout

**Role:** User (login แล้ว)

**Steps:**
1. คลิก user menu (ชื่อ user ใน navbar)
2. คลิก "ออกจากระบบ"

**Expected:**
- redirect ไป `/`
- navbar แสดงปุ่ม Login / Register
- ไม่เห็น cart icon, orders link

**testids:** `nav-user-menu` → `nav-logout` → `nav-login` (ปรากฏ)

---

#### TC-AUTH-09 · เข้าหน้า protected page ขณะ logout — redirect to login

**Role:** Guest

**Steps:**
1. เปิด `/cart.html` โดยตรง (ไม่ได้ login)

**Expected:**
- redirect ไป `/login.html?redirect=%2Fcart.html`
- หลัง login สำเร็จ ควร redirect กลับ `/cart.html`

---

#### TC-AUTH-10 · User เข้าหน้า Admin — redirect

**Role:** User (ไม่ใช่ admin)

**Steps:**
1. Login ด้วย `testuser`
2. เปิด `/admin/index.html` โดยตรง

**Expected:**
- redirect ไป `/login.html` หรือแสดง error
- ไม่เห็น dashboard content

---

### HOME — Homepage

---

#### TC-HOME-01 · หน้า Home โหลดสำเร็จ

**Role:** Guest  
**Precondition:** ระบบทำงาน, มี seed data

**Steps:**
1. เปิด `http://localhost:8000/`

**Expected:**
- Hero section แสดง (title, subtitle, CTA button)
- Categories section แสดง cards ≥ 1 ใบ
- Featured products section แสดงสินค้า ≥ 1 รายการ
- ไม่มี error ใน console

**testids:** `hero-section`, `hero-shop-btn`, `categories-section`, `featured-products`

---

#### TC-HOME-02 · กด CTA ไป Products

**Role:** Guest

**Steps:**
1. เปิดหน้า Home
2. คลิกปุ่ม "เลือกซื้อเลย →"

**Expected:**
- navigate ไป `/products.html`
- แสดงรายการสินค้า

**testids:** `hero-shop-btn`

---

#### TC-HOME-03 · คลิก Category card

**Role:** Guest

**Steps:**
1. เปิดหน้า Home
2. คลิก category card ใด category หนึ่ง (เช่น "Running")

**Expected:**
- navigate ไป `/products.html?category={id}`
- products ถูก filter ตาม category นั้น

**testids:** `categories-section` → category link

---

### PROD — Product Catalog

---

#### TC-PROD-01 · แสดงสินค้าทั้งหมด

**Role:** Guest  
**Precondition:** มี seed data 12 รายการ

**Steps:**
1. เปิด `/products.html`

**Expected:**
- แสดง product cards ≥ 12 รายการ
- product count label แสดงตัวเลข
- แต่ละ card มี: ชื่อ, ราคา, รูปภาพ

**testids:** `products-grid`, `product-card`, `product-count`

---

#### TC-PROD-02 · ค้นหาด้วยชื่อสินค้า

**Role:** Guest

**Steps:**
1. เปิด `/products.html`
2. พิมพ์ `"Nike"` ในช่อง search
3. (รอ debounce หรือกด Enter)

**Expected:**
- แสดงเฉพาะสินค้าที่มีคำว่า "Nike" ในชื่อหรือ brand
- count แสดงตัวเลขที่ลดลง

**testids:** `search-input`, `product-card`

---

#### TC-PROD-03 · ค้นหาแล้วไม่พบสินค้า

**Role:** Guest

**Steps:**
1. พิมพ์ `"xxxxnotexist"` ในช่อง search

**Expected:**
- แสดงข้อความ "ไม่พบสินค้า"
- ไม่แสดง product card

**testids:** `search-input`, `products-grid` (ว่าง หรือ empty state)

---

#### TC-PROD-04 · Filter ตาม Category

**Role:** Guest

**Steps:**
1. เลือก category "Running" จาก dropdown

**Expected:**
- แสดงเฉพาะสินค้าหมวด Running
- URL มี `?category={id}` หรือ state อัปเดต

**testids:** `category-select`, `product-card`

---

#### TC-PROD-05 · Filter ตาม Brand

**Role:** Guest

**Steps:**
1. เลือก brand "Nike" จาก dropdown

**Expected:**
- แสดงเฉพาะสินค้าแบรนด์ Nike
- count อัปเดต

**testids:** `brand-select`, `product-count`

---

#### TC-PROD-06 · Sort ราคา ต่ำ→สูง

**Role:** Guest

**Steps:**
1. เลือก sort "ราคา: ต่ำ→สูง"

**Expected:**
- ราคาของ card แรกน้อยกว่าหรือเท่ากับ card ถัดไปทุกใบ

**testids:** `sort-select`, `product-card-price`

---

#### TC-PROD-07 · Sort ราคา สูง→ต่ำ

**Role:** Guest

**Steps:**
1. เลือก sort "ราคา: สูง→ต่ำ"

**Expected:**
- ราคาของ card แรกมากกว่าหรือเท่ากับ card ถัดไปทุกใบ

---

#### TC-PROD-08 · Filter หลายเงื่อนไขพร้อมกัน

**Role:** Guest

**Steps:**
1. เลือก Category: "Casual"
2. เลือก Brand: "Nike"
3. เลือก Size: "42"

**Expected:**
- แสดงเฉพาะสินค้าที่ตรงทุกเงื่อนไข (AND logic)

---

#### TC-PROD-09 · คลิกไป Product Detail

**Role:** Guest

**Steps:**
1. คลิกที่ product card ใดก็ได้

**Expected:**
- navigate ไป `/product.html?id={id}`
- URL มี id ที่ถูกต้อง

**testids:** `product-card`

---

### DETAIL — Product Detail

---

#### TC-DETAIL-01 · แสดงข้อมูลสินค้าครบ

**Role:** Guest

**Steps:**
1. เปิด `/product.html?id=1`

**Expected:**
- แสดงชื่อสินค้า, ราคา, brand, รูปภาพ, คำอธิบาย
- แสดง size buttons (ถ้ามี)
- แสดง stock status

**testids:** `product-name`, `product-price`, `product-brand`, `product-description`, `product-stock`, `size-buttons`

---

#### TC-DETAIL-02 · Guest กด Add to Cart — redirect to login

**Role:** Guest

**Steps:**
1. เปิดหน้า product detail
2. เลือก size
3. คลิก "เพิ่มลงตะกร้า"

**Expected:**
- redirect ไป `/login.html?redirect=/product.html?id=...`
- ไม่เพิ่มสินค้าลงตะกร้า

---

#### TC-DETAIL-03 · User เพิ่มสินค้าโดยไม่เลือก size — error

**Role:** User  
**Precondition:** สินค้ามี size options

**Steps:**
1. Login แล้วเปิดหน้า product detail
2. ไม่เลือก size
3. คลิก "เพิ่มลงตะกร้า"

**Expected:**
- แสดง error message "กรุณาเลือกไซส์"
- ไม่ส่ง request
- cart count ไม่เพิ่ม

**testids:** `size-error`, `add-to-cart-btn`

---

#### TC-DETAIL-04 · User เพิ่มสินค้าลงตะกร้าสำเร็จ

**Role:** User  
**Precondition:** Login แล้ว, สินค้ามี stock

**Steps:**
1. เปิดหน้า product detail
2. เลือก size (เช่น "42")
3. ตั้ง quantity เป็น 2
4. คลิก "เพิ่มลงตะกร้า"

**Expected:**
- แสดง toast `"เพิ่มลงตะกร้าแล้ว!"`
- cart badge ใน navbar อัปเดต (+2 หรือ +1 item)

**testids:** `size-btn-42`, `quantity-input`, `add-to-cart-btn`, `toast[data-type="success"]`, `cart-count`

---

#### TC-DETAIL-05 · สินค้าหมดสต็อก

**Role:** Guest  
**Precondition:** สินค้ามี `stock = 0`

**Steps:**
1. เปิดหน้า product detail ของสินค้าที่ stock = 0

**Expected:**
- แสดงข้อความ "หมดสต็อก"
- ปุ่ม Add to Cart ถูก disable หรือไม่แสดง

**testids:** `product-stock`, `add-to-cart-btn`

---

#### TC-DETAIL-06 · สินค้า stock น้อย (≤ 5)

**Role:** Guest

**Expected:**
- แสดงข้อความ "เหลือ {n} คู่" พร้อม warning styling

**testids:** `product-stock`

---

### CART — Shopping Cart

---

#### TC-CART-01 · ตะกร้าว่าง

**Role:** User  
**Precondition:** Login แล้ว, ไม่มีสินค้าในตะกร้า

**Steps:**
1. เปิด `/cart.html`

**Expected:**
- แสดง empty state message "ตะกร้าของคุณว่างเปล่า"
- มีปุ่ม "เลือกซื้อสินค้า" ลิงก์ไป `/products.html`

**testids:** `empty-cart`

---

#### TC-CART-02 · ตะกร้ามีสินค้า

**Role:** User  
**Precondition:** เพิ่มสินค้า ≥ 1 รายการแล้ว

**Steps:**
1. เปิด `/cart.html`

**Expected:**
- แสดงรายการสินค้าครบ (ชื่อ, size, quantity, subtotal)
- แสดงยอดรวมทั้งหมด
- มีปุ่ม Checkout

**testids:** `cart-items`, `cart-item`, `item-name`, `item-size`, `cart-total`, `checkout-btn`

---

#### TC-CART-03 · แก้ไขจำนวนสินค้าในตะกร้า

**Role:** User  
**Precondition:** มีสินค้าในตะกร้า

**Steps:**
1. เปิด `/cart.html`
2. เปลี่ยน quantity ของ item แรกเป็น 3

**Expected:**
- subtotal ของ item นั้นอัปเดต (price × 3)
- total ด้านล่างอัปเดต

**testids:** `item-quantity`, `item-subtotal`, `cart-total`

---

#### TC-CART-04 · ลบสินค้าออกจากตะกร้า

**Role:** User  
**Precondition:** มีสินค้า ≥ 2 รายการในตะกร้า

**Steps:**
1. เปิด `/cart.html`
2. คลิกปุ่มลบ (×) ของ item แรก

**Expected:**
- item นั้นหายออกจาก list
- total อัปเดต
- แสดง toast "ลบสินค้าแล้ว"

**testids:** `remove-item-{id}`, `cart-items`, `toast`

---

#### TC-CART-05 · ล้างตะกร้าทั้งหมด

**Role:** User  
**Precondition:** มีสินค้าในตะกร้า

**Steps:**
1. คลิกปุ่ม "🗑 ล้างตะกร้า"
2. กด OK ใน confirm dialog

**Expected:**
- cart ว่างเปล่า แสดง empty state
- cart badge ใน navbar เป็น 0 หรือซ่อน

**testids:** `clear-cart-btn`, `empty-cart`, `cart-count`

---

#### TC-CART-06 · Cart badge ใน navbar

**Role:** User  
**Precondition:** Login แล้ว

**Steps:**
1. เพิ่มสินค้า 3 ชิ้น ลงตะกร้า (แยก request)
2. reload หน้าหรือ navigate ไปหน้าอื่น

**Expected:**
- badge แสดงตัวเลขที่ถูกต้อง (ตาม total items หรือ total quantity)

**testids:** `cart-count`

---

### CHK — Checkout

---

#### TC-CHK-01 · แสดงหน้า Checkout พร้อม order summary

**Role:** User  
**Precondition:** มีสินค้าในตะกร้า

**Steps:**
1. เปิด `/checkout.html`

**Expected:**
- แสดง form จัดส่ง (ว่าง)
- แสดง order summary ด้านขวา (รายการสินค้า + total)
- `checkout-total` ตรงกับ total ใน cart

**testids:** `checkout-form`, `order-summary`, `checkout-total`

---

#### TC-CHK-02 · ตะกร้าว่าง redirect ไป cart

**Role:** User  
**Precondition:** ตะกร้าว่าง

**Steps:**
1. เปิด `/checkout.html` โดยตรง

**Expected:**
- redirect ไป `/cart.html` อัตโนมัติ

---

#### TC-CHK-03 · Pre-fill ที่อยู่จาก profile ที่บันทึกไว้

**Role:** User  
**Precondition:** บันทึก default address ใน `/profile.html` แล้ว

**Steps:**
1. Login
2. ไปที่ `/profile.html` → บันทึกที่อยู่และ payment method
3. เพิ่มสินค้าลงตะกร้า
4. ไปที่ `/checkout.html`

**Expected:**
- fields `shipping-name`, `shipping-address`, `shipping-city`, `shipping-postal`, `shipping-phone` ถูก pre-fill
- payment method radio ที่บันทึกไว้ถูก pre-select

**testids:** `shipping-name` (มีค่า), `shipping-address` (มีค่า), `payment-{method}` (checked)

---

#### TC-CHK-04 · สั่งซื้อสำเร็จ

**Role:** User  
**Precondition:** มีสินค้าในตะกร้า

**Steps:**
1. กรอก Shipping Name: `"John Doe"`
2. กรอก Address: `"123 Test Rd"`
3. กรอก City: `"Bangkok"`
4. กรอก Postal: `"10110"`
5. กรอก Phone: `"081-000-0000"`
6. เลือก payment: Credit Card
7. คลิก "ยืนยันคำสั่งซื้อ"

**Expected:**
- redirect ไป `/order-detail.html?id={new_id}&success=1`
- แสดง success banner
- ตะกร้าถูก clear (badge = 0)

**testids:** `place-order-btn`, `success-banner`, `cart-count`

---

#### TC-CHK-05 · Validation — field ว่าง

**Role:** User

**Steps:**
1. ปล่อย "Shipping Name" ว่าง
2. คลิก "ยืนยันคำสั่งซื้อ"

**Expected:**
- แสดง error message "กรุณากรอกข้อมูลให้ครบถ้วน"
- ไม่ส่ง request
- focus ไปที่ field ที่ว่าง

**testids:** `form-error`, `place-order-btn`

---

### ORD — Order History & Detail

---

#### TC-ORD-01 · ไม่มีออเดอร์ — empty state

**Role:** User  
**Precondition:** Account ใหม่ ยังไม่เคยสั่ง

**Steps:**
1. เปิด `/orders.html`

**Expected:**
- แสดง empty state "ยังไม่มีคำสั่งซื้อ"
- มีปุ่ม "เลือกซื้อสินค้า"

**testids:** `empty-orders`

---

#### TC-ORD-02 · แสดงรายการออเดอร์

**Role:** User  
**Precondition:** มีออเดอร์อย่างน้อย 1 รายการ

**Steps:**
1. เปิด `/orders.html`

**Expected:**
- แสดง order card ทุกรายการของ user นี้ (ไม่เห็น order ของ user อื่น)
- แต่ละ card มี: order ID, วันที่, จำนวน items, ยอดรวม, status badge

**testids:** `orders-container`, `order-card`, `order-id`, `order-date`, `order-total`, `order-status`

---

#### TC-ORD-03 · ดูรายละเอียด order

**Role:** User

**Steps:**
1. คลิก "ดูรายละเอียด →" บน order card

**Expected:**
- navigate ไป `/order-detail.html?id={id}`
- แสดง: order number, status, รายการสินค้า, ที่อยู่จัดส่ง, วิธีชำระเงิน, grand total

**testids:** `order-number`, `order-status-badge`, `order-items-list`, `order-grand-total`, `shipping-info`, `payment-info`

---

#### TC-ORD-04 · User เข้าดู order ของคนอื่น — ไม่พบ

**Role:** User

**Steps:**
1. Login ด้วย `testuser`
2. เปิด `/order-detail.html?id=9999` (ID ที่ไม่ใช่ของตัวเอง)

**Expected:**
- แสดงข้อความ "ไม่พบคำสั่งซื้อ" หรือ redirect
- ไม่แสดงข้อมูล order ของคนอื่น

---

### PROF — User Profile

---

#### TC-PROF-01 · โหลดหน้า profile พร้อมข้อมูลปัจจุบัน

**Role:** User  
**Precondition:** Login แล้ว

**Steps:**
1. เปิด `/profile.html`

**Expected:**
- `profile-email` แสดง email ของ user ที่ login
- `profile-fullname` แสดง full name (ถ้ามี)
- form password ว่าง
- form address แสดงค่าที่บันทึกไว้ (ถ้ามี)

**testids:** `profile-email`, `profile-fullname`, `form-personal`, `form-password`, `form-address`

---

#### TC-PROF-02 · แก้ไขชื่อและอีเมลสำเร็จ

**Role:** User

**Steps:**
1. แก้ Full Name เป็น `"Updated Name"`
2. แก้ Email เป็น `"updated@test.com"`
3. คลิก "บันทึกข้อมูล"

**Expected:**
- แสดง toast "บันทึกข้อมูลส่วนตัวแล้ว"
- reload หน้า → `profile-email` แสดง `"updated@test.com"` และ `profile-fullname` แสดง `"Updated Name"`

**testids:** `profile-fullname`, `profile-email`, `profile-personal-save`, `toast[data-type="success"]`

---

#### TC-PROF-03 · เปลี่ยนรหัสผ่านสำเร็จ

**Role:** User  
**Precondition:** Login ด้วย `testuser / test1234`

**Steps:**
1. กรอก Current Password: `"test1234"`
2. กรอก New Password: `"newpass99"`
3. กรอก Confirm: `"newpass99"`
4. คลิก "เปลี่ยนรหัสผ่าน"

**Expected:**
- แสดง toast "เปลี่ยนรหัสผ่านแล้ว"
- form password ถูก reset เป็นว่าง
- Logout แล้ว login ด้วย password ใหม่ สำเร็จ

**testids:** `profile-current-password`, `profile-new-password`, `profile-confirm-password`, `profile-password-save`, `toast`

> ⚠️ **Teardown:** รีเซ็ต password กลับ `test1234` หลัง test นี้

---

#### TC-PROF-04 · เปลี่ยนรหัสผ่าน — current password ผิด

**Role:** User

**Steps:**
1. กรอก Current Password: `"wrongpassword"`
2. กรอก New + Confirm ที่ถูกต้อง
3. Submit

**Expected:**
- แสดง error "Current password is incorrect"
- password ไม่เปลี่ยน

**testids:** `profile-password-error`

---

#### TC-PROF-05 · เปลี่ยนรหัสผ่าน — new password ไม่ตรงกัน

**Role:** User

**Steps:**
1. กรอก Current Password ถูกต้อง
2. New Password: `"pass1111"` / Confirm: `"pass2222"`
3. Submit

**Expected:**
- แสดง error "รหัสผ่านใหม่ไม่ตรงกัน"
- ไม่ส่ง request

**testids:** `profile-password-error`

---

#### TC-PROF-06 · บันทึกที่อยู่จัดส่งเริ่มต้น

**Role:** User

**Steps:**
1. กรอก Shipping Name: `"Test Shipper"`
2. กรอก Address: `"456 Sample St"`
3. กรอก City: `"Chiang Mai"`
4. กรอก Postal: `"50000"`
5. กรอก Phone: `"089-000-0000"`
6. เลือก Payment: Bank Transfer
7. คลิก "บันทึกที่อยู่"

**Expected:**
- แสดง toast "บันทึกที่อยู่แล้ว"
- reload หน้า → fields แสดงค่าที่บันทึก
- radio `bank_transfer` ถูก pre-select

**testids:** `profile-shipping-name`, `profile-address-save`, `toast`, `payment-bank-transfer`

---

#### TC-PROF-07 · ที่อยู่ที่บันทึกไว้ auto-fill ใน Checkout

**Role:** User  
**Precondition:** บันทึก default address ใน profile แล้ว (TC-PROF-06)

**Steps:**
1. เพิ่มสินค้าลงตะกร้า
2. เปิด `/checkout.html`

**Expected:**
- `shipping-name` = `"Test Shipper"`
- `shipping-city` = `"Chiang Mai"`
- `payment-bank-transfer` radio checked

**testids:** `shipping-name`, `shipping-city`, `payment-bank-transfer`

---

### DASH — Admin Dashboard

---

#### TC-DASH-01 · Stats cards โหลดครบ

**Role:** Admin  
**Precondition:** Login ด้วย `admin`

**Steps:**
1. เปิด `/admin/index.html`

**Expected:**
- `stat-total-orders` แสดงตัวเลข (≥ 0)
- `stat-pending-orders` แสดงตัวเลข
- `stat-revenue` แสดงตัวเลข (format ฿)
- `stat-products` แสดงตัวเลข
- `stat-users` แสดงตัวเลข

**testids:** `stats-grid`, `stat-total-orders`, `stat-pending-orders`, `stat-revenue`, `stat-products`, `stat-users`

---

#### TC-DASH-02 · Recent orders table

**Role:** Admin  
**Precondition:** มี order อย่างน้อย 1 รายการ

**Steps:**
1. เปิด `/admin/index.html`

**Expected:**
- `recent-orders` แสดง table พร้อม order rows
- แต่ละ row มี: order link, username, วันที่, total, status badge

**testids:** `recent-orders`

---

#### TC-DASH-03 · Non-admin เข้า dashboard — redirect

**Role:** User (ไม่ใช่ admin)

**Steps:**
1. Login ด้วย `testuser`
2. เปิด `/admin/index.html`

**Expected:**
- redirect ไป `/login.html`

---

### APROD — Admin Product Management

---

#### TC-APROD-01 · รายการสินค้า

**Role:** Admin

**Steps:**
1. เปิด `/admin/products.html`

**Expected:**
- `product-table` แสดง rows ≥ 12 รายการ
- แต่ละ row มี: รูป, ชื่อ, brand, category, ราคา, stock, status, ปุ่ม edit/delete

**testids:** `product-table`, `product-row`

---

#### TC-APROD-02 · เพิ่มสินค้าใหม่สำเร็จ

**Role:** Admin

**Steps:**
1. คลิก "+ เพิ่มสินค้า"
2. กรอก Name: `"Test Shoe X"`
3. กรอก Brand: `"TestBrand"`
4. เลือก Category: `"Running"`
5. กรอก Price: `"1990"`
6. กรอก Stock: `"10"`
7. กรอก Sizes: `"40,41,42"`
8. คลิก "บันทึก"

**Expected:**
- modal ปิด
- แสดง toast "เพิ่มสินค้าแล้ว"
- table แสดงสินค้าใหม่ `"Test Shoe X"` ใน list

**testids:** `add-product-btn`, `product-modal`, `product-form-name`, `product-save-btn`, `toast`, `product-row`

---

#### TC-APROD-03 · เพิ่มสินค้า — ไม่กรอก required field

**Role:** Admin

**Steps:**
1. คลิก "+ เพิ่มสินค้า"
2. ปล่อย Name ว่าง
3. กรอก Price: `"1990"`
4. คลิก "บันทึก"

**Expected:**
- แสดง error ใน modal "กรุณากรอกชื่อสินค้าและราคา"
- modal ไม่ปิด
- ไม่เพิ่มสินค้า

**testids:** `product-form-error`

---

#### TC-APROD-04 · แก้ไขสินค้า

**Role:** Admin  
**Precondition:** มีสินค้าใน list

**Steps:**
1. คลิก "Edit" ของสินค้าแรก
2. แก้ไข Stock เป็น `"99"`
3. คลิก "บันทึก"

**Expected:**
- modal ปิด
- แสดง toast "อัปเดตสินค้าแล้ว"
- row ของสินค้านั้นแสดง stock = 99

**testids:** `edit-product-{id}`, `product-form-stock`, `product-save-btn`, `toast`

---

#### TC-APROD-05 · Modal ปิดได้ด้วยปุ่ม X

**Role:** Admin

**Steps:**
1. คลิก "+ เพิ่มสินค้า" เพื่อเปิด modal
2. คลิกปุ่ม X มุมบนขวา

**Expected:**
- modal ซ่อน
- ไม่มีการบันทึกข้อมูล

**testids:** `product-modal`, `modal-close-btn`

---

#### TC-APROD-06 · Modal ปิดได้ด้วยคลิก backdrop

**Role:** Admin

**Steps:**
1. เปิด modal
2. คลิกนอก modal (บน overlay สีดำ)

**Expected:**
- modal ปิด

---

#### TC-APROD-07 · ลบสินค้า

**Role:** Admin  
**Precondition:** มีสินค้าที่ไม่มีใน active order

**Steps:**
1. คลิก "Delete" ของสินค้า `"Test Shoe X"` (ที่เพิ่งเพิ่ม)
2. กด OK ใน confirm dialog

**Expected:**
- แสดง toast "ลบสินค้าแล้ว"
- สินค้านั้นหายออกจาก list

**testids:** `delete-product-{id}`, `toast`

---

### AORD — Admin Order Management

---

#### TC-AORD-01 · แสดง orders ทั้งหมด

**Role:** Admin  
**Precondition:** มี order อย่างน้อย 1 รายการ

**Steps:**
1. เปิด `/admin/orders.html`

**Expected:**
- `orders-table` แสดง rows ของทุก user
- แต่ละ row มี: order link, username, วันที่, ที่อยู่, total, status badge, status dropdown

**testids:** `orders-table`, `order-row`

---

#### TC-AORD-02 · Filter order ตาม status

**Role:** Admin

**Steps:**
1. เลือก "รอดำเนินการ" จาก `status-filter-select`

**Expected:**
- แสดงเฉพาะ order ที่มี status = `pending`
- ไม่เห็น order สถานะอื่น

**testids:** `status-filter-select`, `order-row`

---

#### TC-AORD-03 · Filter ไม่พบ order ในสถานะนั้น

**Role:** Admin  
**Precondition:** ไม่มี order status = `delivered`

**Steps:**
1. เลือก "ได้รับแล้ว" จาก filter

**Expected:**
- แสดง empty state "ไม่มีออเดอร์"

**testids:** `no-orders`

---

#### TC-AORD-04 · อัปเดตสถานะ order

**Role:** Admin  
**Precondition:** มี order status = `pending`

**Steps:**
1. หา order row ที่ status = `pending`
2. เปลี่ยน status dropdown เป็น `"confirmed"`

**Expected:**
- แสดง toast "อัปเดตสถานะออเดอร์ #{id} แล้ว"
- status badge ของ row นั้นเปลี่ยนเป็น `"ยืนยันแล้ว"`
- table reload

**testids:** `status-select-{id}`, `order-status-{id}`, `toast`

---

#### TC-AORD-05 · อัปเดตสถานะเป็น cancelled

**Role:** Admin

**Steps:**
1. เลือก `"cancelled"` จาก status dropdown ของ order ใดก็ได้

**Expected:**
- status badge เปลี่ยนเป็น `"ยกเลิก"` พร้อม red styling
- order ยังอยู่ใน list (ไม่ลบ)

**testids:** `status-select-{id}`, `order-status-{id}`

---

#### TC-AORD-06 · คลิก order link ไป order detail

**Role:** Admin

**Steps:**
1. คลิก `#123` link ใน order row

**Expected:**
- navigate ไป `/order-detail.html?id=123`
- แสดงรายละเอียด order ครบถ้วน

---

### I18N — Multi-language

---

#### TC-I18N-01 · เปลี่ยนเป็นภาษาอังกฤษ

**Role:** Guest  
**Precondition:** ภาษาปัจจุบันเป็นไทย

**Steps:**
1. คลิกไอคอน 🌐 ใน navbar
2. คลิก "English" จาก dropdown

**Expected:**
- หน้า reload
- navbar links เปลี่ยนเป็น `Home`, `Products`, `Cart`, `Orders`, `Login`, `Register`
- hero text เปลี่ยนเป็น English
- ปุ่ม CTA แสดง "Shop Now →"

---

#### TC-I18N-02 · เปลี่ยนกลับเป็นภาษาไทย

**Role:** Guest

**Steps:**
1. คลิก 🌐 → เลือก "ภาษาไทย"

**Expected:**
- หน้า reload
- ข้อความทั้งหมดกลับเป็นภาษาไทย

---

#### TC-I18N-03 · ภาษาคงอยู่หลัง reload

**Role:** Guest  
**Precondition:** เปลี่ยนเป็น English แล้ว

**Steps:**
1. กด F5 / reload หน้า

**Expected:**
- ยังเป็นภาษา English (ค่าใน localStorage คงอยู่)

---

#### TC-I18N-04 · Dynamic content ใช้ภาษาที่เลือก

**Role:** User  
**Precondition:** ภาษา English

**Steps:**
1. เปิด `/orders.html` ขณะ English
2. ดู status badge ของ order

**Expected:**
- status แสดงเป็น `"Pending"`, `"Confirmed"`, `"Shipped"` (ไม่ใช่ภาษาไทย)

---

#### TC-I18N-05 · Toast messages ใช้ภาษาที่เลือก

**Role:** User  
**Precondition:** ภาษา English

**Steps:**
1. ลบ item ออกจาก cart

**Expected:**
- toast แสดง `"Item removed"` (ไม่ใช่ "ลบสินค้าแล้ว")

---

### NAV — Navigation

---

#### TC-NAV-01 · Navbar ของ Guest

**Role:** Guest

**Expected:**
- แสดง: logo, Home, Products link
- แสดง: Login, Register buttons
- ไม่แสดง: cart icon, orders link, admin link, user menu

**testids:** `nav-logo`, `nav-home`, `nav-products`, `nav-login`, `nav-register`

---

#### TC-NAV-02 · Navbar ของ User

**Role:** User (login แล้ว)

**Expected:**
- แสดง: logo, Home, Products, Cart (+ badge), Orders, user menu (ชื่อ user)
- ไม่แสดง: Login, Register, Admin link
- `nav-user-menu` แสดงชื่อ user

**testids:** `nav-cart`, `cart-count`, `nav-orders`, `nav-user-menu`

---

#### TC-NAV-03 · Navbar ของ Admin

**Role:** Admin

**Expected:**
- แสดงทุกอย่างของ User + `nav-admin` link

**testids:** `nav-admin`

---

#### TC-NAV-04 · User dropdown เปิด/ปิดด้วย click

**Role:** User

**Steps:**
1. คลิก user menu button
2. ตรวจว่า dropdown แสดง
3. คลิก user menu button อีกครั้ง
4. ตรวจว่า dropdown ซ่อน

**Expected:**
- dropdown toggle ด้วย click
- dropdown ปรากฏ: email, Profile link, Logout button

**testids:** `nav-user-menu`, `nav-profile`, `nav-logout`

---

#### TC-NAV-05 · Language dropdown เปิด/ปิดด้วย click

**Role:** Guest

**Steps:**
1. คลิก 🌐 icon
2. ตรวจว่า `lang-menu` แสดง
3. คลิกนอก dropdown
4. ตรวจว่า `lang-menu` ซ่อน

**Expected:**
- dropdown toggle ด้วย click
- คลิก outside ปิด dropdown
- ไม่หาย เมื่อเลื่อน cursor จากปุ่มเข้าไปใน dropdown

---

#### TC-NAV-06 · เปิด menu แรกปิดอีก menu

**Role:** User

**Steps:**
1. เปิด user dropdown
2. คลิก 🌐 เพื่อเปิด language dropdown

**Expected:**
- user dropdown ปิด
- language dropdown เปิด (ไม่เปิดพร้อมกัน)

---

#### TC-NAV-07 · Mobile menu toggle

**Steps:**
1. resize viewport เป็น < 768px
2. คลิก hamburger button

**Expected:**
- mobile menu แสดง
- มี Home, Products links
- คลิกอีกครั้ง → ซ่อน

---

## สรุป Test Coverage Matrix

| Feature Area | Happy Path | Negative / Edge | Total TCs |
|-------------|:----------:|:---------------:|:---------:|
| Authentication | 6 | 4 | 10 |
| Homepage | 3 | 0 | 3 |
| Product Catalog | 7 | 2 | 9 |
| Product Detail | 3 | 3 | 6 |
| Shopping Cart | 5 | 1 | 6 |
| Checkout | 3 | 2 | 5 |
| Orders | 3 | 1 | 4 |
| User Profile | 4 | 3 | 7 |
| Admin Dashboard | 2 | 1 | 3 |
| Admin Products | 4 | 3 | 7 |
| Admin Orders | 4 | 2 | 6 |
| Multi-language | 4 | 1 | 5 |
| Navigation | 6 | 1 | 7 |
| **รวม** | **54** | **24** | **78** |

---

## API Endpoints Reference

| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| POST | `/api/auth/register` | — | สมัครสมาชิก |
| POST | `/api/auth/login` | — | Login รับ JWT |
| GET | `/api/auth/me` | User | ข้อมูล user ปัจจุบัน |
| PUT | `/api/auth/profile` | User | แก้ชื่อ/email |
| PUT | `/api/auth/password` | User | เปลี่ยนรหัสผ่าน |
| PUT | `/api/auth/address` | User | บันทึกที่อยู่/payment เริ่มต้น |
| GET | `/api/products` | — | รายการสินค้า (query: search, category_id, brand, size, sort, limit, offset) |
| GET | `/api/products/{id}` | — | รายละเอียดสินค้า |
| POST | `/api/products` | Admin | เพิ่มสินค้า |
| PUT | `/api/products/{id}` | Admin | แก้ไขสินค้า |
| DELETE | `/api/products/{id}` | Admin | ลบสินค้า |
| GET | `/api/categories` | — | หมวดหมู่สินค้า |
| GET | `/api/cart` | User | ดูตะกร้า |
| POST | `/api/cart` | User | เพิ่มสินค้าลงตะกร้า |
| PUT | `/api/cart/{id}` | User | แก้จำนวนใน cart |
| DELETE | `/api/cart/{id}` | User | ลบ item ออกจาก cart |
| DELETE | `/api/cart/clear` | User | ล้างตะกร้า |
| GET | `/api/orders` | User | ประวัติออเดอร์ของตัวเอง |
| GET | `/api/orders/{id}` | User | รายละเอียด order |
| POST | `/api/orders` | User | สั่งซื้อ |
| GET | `/api/admin/stats` | Admin | สถิติ dashboard |
| GET | `/api/admin/orders` | Admin | orders ทั้งหมด (query: status) |
| PUT | `/api/admin/orders/{id}/status` | Admin | เปลี่ยนสถานะ order |
| GET | `/api/admin/users` | Admin | รายชื่อ user ทั้งหมด |
