"""Run once to populate the database with sample data."""
import json
import sys

from auth_utils import hash_password
from database import get_db, init_db

CATEGORIES = [
    ("Running", "running"),
    ("Casual", "casual"),
    ("Basketball", "basketball"),
    ("Lifestyle", "lifestyle"),
]

PRODUCTS = [
    {
        "name": "Nike Air Max 90",
        "brand": "Nike",
        "description": "Classic Air Max cushioning with a timeless design. Perfect for everyday wear and light running.",
        "price": 4990,
        "stock": 1000,
        "category": "lifestyle",
        "image_url": "https://picsum.photos/seed/airmax90/600/400",
        "sizes": ["38", "39", "40", "41", "42", "43", "44", "45"],
    },
    {
        "name": "Adidas Ultraboost 23",
        "brand": "Adidas",
        "description": "Energy-returning Boost midsole for a responsive run. Primeknit upper for a sock-like fit.",
        "price": 5990,
        "stock": 1000,
        "category": "running",
        "image_url": "https://picsum.photos/seed/ultraboost/600/400",
        "sizes": ["38", "39", "40", "41", "42", "43", "44"],
    },
    {
        "name": "New Balance 990v6",
        "brand": "New Balance",
        "description": "Made in USA. Premium ENCAP midsole technology for maximum support and durability.",
        "price": 7490,
        "stock": 1000,
        "category": "running",
        "image_url": "https://picsum.photos/seed/nb990/600/400",
        "sizes": ["39", "40", "41", "42", "43", "44", "45"],
    },
    {
        "name": "Converse Chuck Taylor All Star",
        "brand": "Converse",
        "description": "The iconic sneaker since 1917. Canvas upper with vulcanized rubber sole.",
        "price": 2490,
        "stock": 1000,
        "category": "casual",
        "image_url": "https://picsum.photos/seed/converse/600/400",
        "sizes": ["36", "37", "38", "39", "40", "41", "42", "43", "44"],
    },
    {
        "name": "Vans Old Skool",
        "brand": "Vans",
        "description": "The first shoe to feature the iconic side stripe. Durable suede and canvas upper.",
        "price": 2990,
        "stock": 1000,
        "category": "casual",
        "image_url": "https://picsum.photos/seed/vansoldskool/600/400",
        "sizes": ["37", "38", "39", "40", "41", "42", "43"],
    },
    {
        "name": "Puma RS-X",
        "brand": "Puma",
        "description": "Chunky retro-inspired design with Running System technology.",
        "price": 3590,
        "stock": 1000,
        "category": "lifestyle",
        "image_url": "https://picsum.photos/seed/pumarsx/600/400",
        "sizes": ["39", "40", "41", "42", "43", "44"],
    },
    {
        "name": "Reebok Classic Leather",
        "brand": "Reebok",
        "description": "Clean leather upper with a cushioned midsole for all-day comfort.",
        "price": 3290,
        "stock": 1000,
        "category": "lifestyle",
        "image_url": "https://picsum.photos/seed/reebokclassic/600/400",
        "sizes": ["38", "39", "40", "41", "42", "43", "44", "45"],
    },
    {
        "name": "Jordan 1 Retro High OG",
        "brand": "Nike",
        "description": "The shoe that started it all. High-top silhouette with premium leather upper.",
        "price": 8990,
        "stock": 1000,
        "category": "basketball",
        "image_url": "https://picsum.photos/seed/jordan1/600/400",
        "sizes": ["40", "41", "42", "43", "44", "45"],
    },
    {
        "name": "Nike ZoomX Vaporfly Next%",
        "brand": "Nike",
        "description": "Carbon fiber plate and ZoomX foam for record-breaking speed on race day.",
        "price": 9990,
        "stock": 1000,
        "category": "running",
        "image_url": "https://picsum.photos/seed/vaporfly/600/400",
        "sizes": ["39", "40", "41", "42", "43", "44"],
    },
    {
        "name": "Adidas Stan Smith",
        "brand": "Adidas",
        "description": "Tennis legend, street icon. Clean white leather with perforated 3-Stripes.",
        "price": 2990,
        "stock": 1000,
        "category": "casual",
        "image_url": "https://picsum.photos/seed/stansmith/600/400",
        "sizes": ["37", "38", "39", "40", "41", "42", "43", "44"],
    },
    {
        "name": "Nike LeBron 21",
        "brand": "Nike",
        "description": "Built for domination. Full-length Air Zoom Turbo unit for explosive performance.",
        "price": 7990,
        "stock": 1000,
        "category": "basketball",
        "image_url": "https://picsum.photos/seed/lebron21/600/400",
        "sizes": ["40", "41", "42", "43", "44", "45", "46"],
    },
    {
        "name": "New Balance 574",
        "brand": "New Balance",
        "description": "A versatile classic. ENCAP midsole technology with suede and mesh upper.",
        "price": 3490,
        "stock": 1000,
        "category": "lifestyle",
        "image_url": "https://picsum.photos/seed/nb574/600/400",
        "sizes": ["38", "39", "40", "41", "42", "43", "44"],
    },
]

USERS = [
    {"username": "admin", "email": "admin@shoeshub.com", "password": "admin1234", "full_name": "Admin User", "is_admin": 1},
    {"username": "testuser", "email": "test@shoeshub.com", "password": "test1234", "full_name": "Test User", "is_admin": 0},
    {"username": "john_doe", "email": "john@example.com", "password": "john1234", "full_name": "John Doe", "is_admin": 0},
]


SPIKE_CODES = [
    {
        "code": "SPIKE10",
        "description": "Spike test — 10% off, unlimited, no expiry",
        "discount_type": "percentage",
        "discount_value": 10.0,
    },
    {
        "code": "SPIKE20",
        "description": "Spike test — 20% off, unlimited, no expiry",
        "discount_type": "percentage",
        "discount_value": 20.0,
    },
    {
        "code": "FLAT100",
        "description": "Spike test — 100 baht off, unlimited, no expiry",
        "discount_type": "fixed",
        "discount_value": 100.0,
    },
    {
        "code": "FLAT500",
        "description": "Spike test — 500 baht off, unlimited, no expiry",
        "discount_type": "fixed",
        "discount_value": 500.0,
    },
]


def seed_discount_codes():
    """Always-run: insert spike codes if they don't exist yet."""
    db = get_db()
    for dc in SPIKE_CODES:
        db.execute(
            """INSERT OR IGNORE INTO discount_codes
               (code, description, discount_type, discount_value, expires_at, max_uses, is_active)
               VALUES (?, ?, ?, ?, NULL, NULL, 1)""",
            (dc["code"], dc["description"], dc["discount_type"], dc["discount_value"]),
        )
    db.commit()
    db.close()


def seed():
    init_db()
    db = get_db()

    existing = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if existing > 0:
        print("[SKIP] Database already seeded.")
        db.close()
        seed_discount_codes()
        return

    # Categories
    cat_map = {}
    for name, slug in CATEGORIES:
        cur = db.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug))
        cat_map[slug] = cur.lastrowid

    # Users
    for u in USERS:
        db.execute(
            "INSERT OR IGNORE INTO users (username, email, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?, ?)",
            (u["username"], u["email"], hash_password(u["password"]), u["full_name"], u["is_admin"]),
        )

    # Products
    for p in PRODUCTS:
        db.execute(
            """INSERT INTO products (name, brand, description, price, stock, category_id, image_url, sizes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p["name"], p["brand"], p["description"], p["price"],
                p["stock"], cat_map[p["category"]], p["image_url"],
                json.dumps(p["sizes"]),
            ),
        )

    db.commit()
    db.close()

    seed_discount_codes()

    print("[OK] Seed data inserted successfully!")
    print("\n[TEST ACCOUNTS]")
    for u in USERS:
        role = "Admin" if u["is_admin"] else "User"
        print(f"   [{role}] username: {u['username']}  password: {u['password']}")
    print("\n[DISCOUNT CODES] (no expiry, unlimited uses)")
    print("   SPIKE10  — 10% off")
    print("   SPIKE20  — 20% off")
    print("   FLAT100  — 100 baht off")
    print("   FLAT500  — 500 baht off")


if __name__ == "__main__":
    seed()
