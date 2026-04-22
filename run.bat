@echo off
echo ============================================
echo   ShoesHub E-Commerce (Automation Testing)
echo ============================================

cd /d "%~dp0backend"

echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo [2/3] Seeding database...
python seed.py

echo [3/3] Starting server at http://localhost:8000
echo.
echo  Frontend : http://localhost:8000/
echo  API Docs : http://localhost:8000/docs
echo  Admin    : http://localhost:8000/admin/index.html
echo.
echo  Test accounts:
echo    Admin  : admin / admin1234
echo    User   : testuser / test1234
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
