import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name     TEXT,
            is_admin      INTEGER DEFAULT 0,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT,
            price       REAL NOT NULL,
            stock       INTEGER DEFAULT 0,
            category_id INTEGER REFERENCES categories(id),
            image_url   TEXT,
            brand       TEXT,
            sizes       TEXT DEFAULT '[]',
            is_active   INTEGER DEFAULT 1,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            quantity   INTEGER NOT NULL DEFAULT 1,
            size       TEXT NOT NULL DEFAULT '',
            UNIQUE(user_id, product_id, size)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id),
            total_amount     REAL NOT NULL,
            status           TEXT DEFAULT 'pending',
            shipping_name    TEXT,
            shipping_address TEXT,
            shipping_city    TEXT,
            shipping_postal  TEXT,
            shipping_phone   TEXT,
            payment_method   TEXT DEFAULT 'credit_card',
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id   INTEGER REFERENCES products(id),
            product_name TEXT NOT NULL,
            quantity     INTEGER NOT NULL,
            price        REAL NOT NULL,
            size         TEXT
        );
    """)
    conn.commit()
    conn.close()


def migrate_db():
    conn = get_db()
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    new_cols = [
        ("default_shipping_name",    "TEXT"),
        ("default_shipping_address", "TEXT"),
        ("default_shipping_city",    "TEXT"),
        ("default_shipping_postal",  "TEXT"),
        ("default_shipping_phone",   "TEXT"),
        ("default_payment_method",   "TEXT DEFAULT 'credit_card'"),
    ]
    for col, typedef in new_cols:
        if col not in cols:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} {typedef}")
    conn.commit()
    conn.close()
