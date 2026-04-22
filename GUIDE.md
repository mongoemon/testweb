# ShoesHub — คู่มือการใช้งาน

ระบบ e-commerce สำหรับซื้อขายรองเท้า พัฒนาด้วย FastAPI + SQLite (backend) และ HTML/JS (frontend)

---

## การเริ่มต้นใช้งาน

### รันระบบ

```bash
# Windows
run.bat

# Mac / Linux
./run.sh
```

| URL | คำอธิบาย |
|-----|----------|
| `http://localhost:8000/` | หน้าเว็บหลัก (frontend) |
| `http://localhost:8000/docs` | Swagger UI — ทดสอบ API พร้อม token |
| `http://localhost:8000/redoc` | ReDoc — เอกสาร API แบบอ่าน |

### ดูและแก้ไขข้อมูลใน Database

```bash
cd backend
pip install sqlite-web
sqlite_web shop.db --port 8081
```

เปิดเบราว์เซอร์ `http://localhost:8081` เพื่อดู/แก้ไขข้อมูลในตาราง, รัน SQL query, หรือ export CSV

---

## บัญชีผู้ใช้งาน (Test Accounts)

| Role  | Username   | Password    | Email                  |
|-------|------------|-------------|------------------------|
| Admin | `admin`    | `admin1234` | admin@shoeshub.com     |
| User  | `testuser` | `test1234`  | test@shoeshub.com      |
| User  | `john_doe` | `john1234`  | john@example.com       |

---

## สิทธิ์การใช้งานตาม Role

### Guest (ไม่ได้ล็อกอิน)

สามารถทำได้:

- ดูรายการสินค้าทั้งหมด (`/products.html`)
- ค้นหาสินค้าตามชื่อ แบรนด์ หมวดหมู่ ราคา และไซส์
- ดูรายละเอียดสินค้าแต่ละชิ้น (`/product.html`)
- ดูหมวดหมู่สินค้า (Running, Casual, Basketball, Lifestyle)
- สมัครสมาชิก (`/register.html`)
- ล็อกอิน (`/login.html`)

ไม่สามารถทำได้:

- เพิ่มสินค้าลงตะกร้า
- สั่งซื้อสินค้า
- ดูประวัติคำสั่งซื้อ

---

### User (ล็อกอินแล้ว — role ปกติ)

ทำได้ทุกอย่างของ Guest บวกกับ:

**ตะกร้าสินค้า**
- เพิ่มสินค้าลงตะกร้า (ระบุไซส์และจำนวน)
- แก้ไขจำนวนสินค้าในตะกร้า
- ลบสินค้าออกจากตะกร้า (รายชิ้น หรือล้างทั้งหมด)
- ดูยอดรวมในตะกร้า

**คำสั่งซื้อ**
- สั่งซื้อสินค้าจากตะกร้า (ระบุที่อยู่จัดส่ง + วิธีชำระเงิน)
- ดูประวัติคำสั่งซื้อของตัวเอง (`/orders.html`)
- ดูรายละเอียดคำสั่งซื้อแต่ละรายการ (`/order-detail.html`)

**ข้อมูลส่วนตัว**
- ดูข้อมูลโปรไฟล์ตัวเอง (`GET /api/auth/me`)

ไม่สามารถทำได้:
- ดู order ของ user คนอื่น
- แก้ไขสถานะ order
- เข้าถึงหน้า admin

---

### Admin

ทำได้ทุกอย่างของ User บวกกับ:

**Dashboard** (`/admin/`)
- ดูสถิติภาพรวม: จำนวน order, รายได้รวม, จำนวนสินค้า, จำนวน user
- ดู order 5 รายการล่าสุด

**จัดการ Order** (`/admin/orders.html`)
- ดู order ทั้งหมดของทุก user
- กรอง order ตามสถานะ
- อัปเดตสถานะ order

**จัดการสินค้า** (`/admin/products.html`)
- เพิ่มสินค้าใหม่
- แก้ไขข้อมูลสินค้า (ชื่อ, ราคา, stock, รูป, ไซส์)
- ลบสินค้า (soft-delete — สินค้าหายจาก catalog แต่ยังอยู่ใน DB เพื่อ order history)

**จัดการ User**
- ดูรายชื่อ user ทั้งหมด

---

## วิธีชำระเงิน (Payment Methods)

| ค่า | ความหมาย |
|-----|----------|
| `credit_card` | บัตรเครดิต/เดบิต |
| `bank_transfer` | โอนเงินผ่านธนาคาร |
| `cod` | เก็บเงินปลายทาง |

---

## สถานะคำสั่งซื้อ (Order Status Flow)

```
pending → confirmed → processing → shipped → delivered
```

สามารถเปลี่ยนเป็น `cancelled` ได้จากทุกสถานะ (Admin เท่านั้น)

| Status | ความหมาย |
|--------|----------|
| `pending` | รอการยืนยัน (default เมื่อสั่งซื้อ) |
| `confirmed` | Admin ยืนยันแล้ว |
| `processing` | กำลังจัดเตรียมสินค้า |
| `shipped` | จัดส่งแล้ว |
| `delivered` | ได้รับสินค้าแล้ว |
| `cancelled` | ยกเลิก |

---

## โครงสร้างข้อมูล (Database Tables)

| ตาราง | คำอธิบาย |
|-------|----------|
| `users` | บัญชีผู้ใช้ทั้งหมด (มี `is_admin` flag) |
| `categories` | หมวดหมู่สินค้า: Running, Casual, Basketball, Lifestyle |
| `products` | สินค้าทั้งหมด (มี `is_active` สำหรับ soft-delete) |
| `cart_items` | สินค้าในตะกร้าของแต่ละ user |
| `orders` | คำสั่งซื้อ (มีข้อมูลจัดส่งและวิธีชำระเงิน) |
| `order_items` | รายการสินค้าใน order แต่ละรายการ |

---

## การทดสอบผ่าน Swagger UI

1. เปิด `http://localhost:8000/docs`
2. เรียก `POST /api/auth/login` ด้วย username/password ที่ต้องการ
3. คัดลอก `access_token` จาก response
4. กดปุ่ม **Authorize** (🔒) มุมบนขวา
5. วาง token ในช่อง `HTTPBearer (http, Bearer)`
6. กด **Authorize** แล้วปิด dialog
7. ทดสอบ endpoint ที่ต้องการได้เลย

---

## ข้อมูลสินค้าตัวอย่าง (Seed Data)

12 รายการจาก 4 แบรนด์หลัก:

| แบรนด์ | สินค้า |
|--------|--------|
| Nike | Air Max 90, ZoomX Vaporfly Next%, LeBron 21, Jordan 1 Retro High OG |
| Adidas | Ultraboost 23, Stan Smith |
| New Balance | 990v6, 574 |
| Converse | Chuck Taylor All Star |
| Vans | Old Skool |
| Puma | RS-X |
| Reebok | Classic Leather |

รีเซ็ต seed data:
```bash
cd backend
rm shop.db
python seed.py
```
