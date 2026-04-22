@echo off
echo ============================================
echo   ShoesHub -- DEV
echo ============================================

cd /d "%~dp0"

rem Load .env.dev variables
if exist .env.dev (
    for /f "usebackq tokens=1,* delims==" %%a in (".env.dev") do (
        if not "%%a"=="" (
            set "line=%%a"
            if not "!line:~0,1!"=="#" set "%%a=%%b"
        )
    )
    echo [ENV] Loaded .env.dev
)

cd backend

echo [1/2] Installing dependencies...
pip install -r requirements.txt --quiet

echo [2/2] Starting server at http://localhost:8000
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
