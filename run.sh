#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  ShoesHub — DEV"
echo "============================================"

# Load dev environment variables
if [ -f "$ROOT_DIR/.env.dev" ]; then
    set -a
    source "$ROOT_DIR/.env.dev"
    set +a
    echo "[ENV] Loaded .env.dev"
fi

cd "$ROOT_DIR/backend"

echo "[1/2] Installing dependencies..."
pip install -r requirements.txt --quiet

echo "[2/2] Starting server at http://localhost:8000"
echo ""
echo "  Frontend : http://localhost:8000/"
echo "  API Docs : http://localhost:8000/docs"
echo "  Admin    : http://localhost:8000/admin/index.html"
echo ""
echo "  Test accounts:"
echo "    Admin  : admin / admin1234"
echo "    User   : testuser / test1234"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
