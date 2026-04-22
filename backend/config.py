import os
from pathlib import Path

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    str(Path(__file__).parent / "shop.db"),
)

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "shoeshub-dev-secret-key-NOT-for-production",
)

DEBUG = os.environ.get(
    "DEBUG",
    "true" if ENVIRONMENT == "dev" else "false",
).lower() == "true"

AUTO_SEED = os.environ.get(
    "AUTO_SEED",
    "true" if ENVIRONMENT in ("dev", "qa") else "false",
).lower() == "true"

_cors_raw = os.environ.get("CORS_ORIGINS", "*")
CORS_ORIGINS = (
    ["*"] if _cors_raw.strip() == "*"
    else [o.strip() for o in _cors_raw.split(",")]
)
