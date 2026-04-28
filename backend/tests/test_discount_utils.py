"""Pure unit tests for discount_utils — no HTTP, no app, in-memory SQLite."""
import sqlite3
from datetime import datetime, timezone, timedelta

import pytest
from fastapi import HTTPException

from discount_utils import apply_discount, check_code_valid

CREATE_TABLE = """
    CREATE TABLE discount_codes (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        code          TEXT UNIQUE NOT NULL,
        description   TEXT,
        discount_type TEXT NOT NULL DEFAULT 'percentage',
        discount_value REAL NOT NULL,
        expires_at    TIMESTAMP,
        max_uses      INTEGER,
        current_uses  INTEGER NOT NULL DEFAULT 0,
        is_active     INTEGER NOT NULL DEFAULT 1,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(CREATE_TABLE)
    yield conn
    conn.close()


def _insert(db, code, **kw):
    defaults = dict(
        description="test", discount_type="percentage",
        discount_value=10.0, expires_at=None,
        max_uses=None, current_uses=0, is_active=1,
    )
    defaults.update(kw)
    db.execute(
        """INSERT INTO discount_codes
           (code, description, discount_type, discount_value,
            expires_at, max_uses, current_uses, is_active)
           VALUES (?,?,?,?,?,?,?,?)""",
        (code, defaults["description"], defaults["discount_type"],
         defaults["discount_value"], defaults["expires_at"],
         defaults["max_uses"], defaults["current_uses"], defaults["is_active"]),
    )
    db.commit()


# ── apply_discount ────────────────────────────────────────────────────────────

class TestApplyDiscount:
    def test_percentage_basic(self):
        dc = {"discount_type": "percentage", "discount_value": 10.0}
        assert apply_discount(1000.0, dc) == 100.0

    def test_percentage_20(self):
        dc = {"discount_type": "percentage", "discount_value": 20.0}
        assert apply_discount(500.0, dc) == 100.0

    def test_percentage_rounding(self):
        dc = {"discount_type": "percentage", "discount_value": 10.0}
        assert apply_discount(999.0, dc) == pytest.approx(99.9)

    def test_fixed_basic(self):
        dc = {"discount_type": "fixed", "discount_value": 100.0}
        assert apply_discount(1000.0, dc) == 100.0

    def test_fixed_capped_at_subtotal(self):
        dc = {"discount_type": "fixed", "discount_value": 2000.0}
        assert apply_discount(500.0, dc) == 500.0

    def test_percentage_100_capped(self):
        dc = {"discount_type": "percentage", "discount_value": 100.0}
        assert apply_discount(800.0, dc) == 800.0

    def test_percentage_zero_subtotal(self):
        dc = {"discount_type": "percentage", "discount_value": 10.0}
        assert apply_discount(0.0, dc) == 0.0


# ── check_code_valid ──────────────────────────────────────────────────────────

class TestCheckCodeValid:
    def test_valid_code_returned(self, db):
        _insert(db, "OK10")
        result = check_code_valid(db, "OK10")
        assert result["code"] == "OK10"
        assert result["discount_type"] == "percentage"

    def test_case_insensitive_lookup(self, db):
        _insert(db, "UPPER20")
        result = check_code_valid(db, "upper20")
        assert result["code"] == "UPPER20"

    def test_not_found_raises_404(self, db):
        with pytest.raises(HTTPException) as exc:
            check_code_valid(db, "GHOST")
        assert exc.value.status_code == 404

    def test_inactive_raises_400(self, db):
        _insert(db, "PAUSED", is_active=0)
        with pytest.raises(HTTPException) as exc:
            check_code_valid(db, "PAUSED")
        assert exc.value.status_code == 400

    def test_expired_raises_400(self, db):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        _insert(db, "OLD", expires_at=past)
        with pytest.raises(HTTPException) as exc:
            check_code_valid(db, "OLD")
        assert exc.value.status_code == 400

    def test_future_expiry_passes(self, db):
        future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        _insert(db, "SOON", expires_at=future)
        result = check_code_valid(db, "SOON")
        assert result["code"] == "SOON"

    def test_no_expiry_always_passes(self, db):
        _insert(db, "FOREVER", expires_at=None)
        result = check_code_valid(db, "FOREVER")
        assert result["code"] == "FOREVER"

    def test_max_uses_reached_raises_400(self, db):
        _insert(db, "FULL", max_uses=5, current_uses=5)
        with pytest.raises(HTTPException) as exc:
            check_code_valid(db, "FULL")
        assert exc.value.status_code == 400

    def test_max_uses_not_yet_reached(self, db):
        _insert(db, "ALMOST", max_uses=5, current_uses=4)
        result = check_code_valid(db, "ALMOST")
        assert result["code"] == "ALMOST"

    def test_unlimited_uses(self, db):
        _insert(db, "INF", max_uses=None, current_uses=99999)
        result = check_code_valid(db, "INF")
        assert result["code"] == "INF"
