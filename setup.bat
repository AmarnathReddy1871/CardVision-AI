@echo off
REM 🚀 Card Digitization System - Quick Start Script (Windows)

setlocal enabledelayedexpansion

echo ================================
echo 📇 Card Digitization Setup
echo ================================
echo.

REM Check Python
echo ✓ Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.11+
    pause
    exit /b 1
)

REM Check Node
echo ✓ Checking Node...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Install Node 18+
    pause
    exit /b 1
)

REM Check Git
echo ✓ Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not found. Install Git
    pause
    exit /b 1
)

echo.
echo ✅ All prerequisites installed
echo.

REM Setup Python venv
echo 📦 Setting up Python environment...
if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo ✓ Python packages installed

REM Setup .env
echo.
echo 🔐 Setting up .env file...
if not exist ".env" (
    copy .env.example .env
    echo ✓ Created .env file
    echo ⚠️  IMPORTANT: Edit .env with your credentials
) else (
    echo ✓ .env file already exists
)

REM Setup Frontend
echo.
echo 🎨 Setting up Frontend...
if not exist "frontend" mkdir frontend
if not exist "frontend\src" mkdir frontend\src
if not exist "frontend\src\components" mkdir frontend\src\components
if not exist "frontend\public" mkdir frontend\public

cd frontend

if not exist "package.json" (
    echo Creating package.json...
    if exist "..\frontend_package.json" (
        copy ..\frontend_package.json package.json
    ) else (
        call npm init -y
    )
)

if not exist "node_modules" (
    call npm install -q
)

echo ✓ Frontend packages installed

if not exist ".env" (
    echo REACT_APP_API_URL=http://localhost:8000 > .env
)

cd ..

echo.
echo ================================
echo ✅ Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env with your credentials
echo 2. Run: python main.py          (Backend)
echo 3. Run: cd frontend ^&^& npm start (Frontend in new terminal)
echo 4. Open: http://localhost:3000
echo.
echo For more info, see EXECUTION_GUIDE.md
echo.
pause
