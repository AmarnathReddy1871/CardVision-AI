#!/bin/bash

# 🚀 Card Digitization System - Quick Start Script

set -e

echo "================================"
echo "📇 Card Digitization Setup"
echo "================================"
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.11+"
    exit 1
fi

# Check Node
echo "✓ Checking Node..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node 18+"
    exit 1
fi

# Check Git
echo "✓ Checking Git..."
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install Git"
    exit 1
fi

echo ""
echo "✅ All prerequisites installed"
echo ""

# Setup Python venv
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate
pip install -q -r requirements.txt
echo "✓ Python packages installed"

# Setup .env
echo ""
echo "🔐 Setting up .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠️  IMPORTANT: Edit .env with your credentials:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - GOOGLE_SHEETS_ID"
    echo "   - GOOGLE_CREDENTIALS_JSON"
    echo "   - MONGODB_URI"
else
    echo "✓ .env file already exists"
fi

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd frontend 2>/dev/null || {
    echo "Creating frontend directory..."
    mkdir -p frontend/src/components frontend/public
    cd frontend
}

if [ ! -f "package.json" ]; then
    echo "Creating package.json..."
    cp ../frontend_package.json package.json 2>/dev/null || npm init -y
fi

if [ ! -d "node_modules" ]; then
    npm install -q
fi

echo "✓ Frontend packages installed"

cd ..

# Create .env for frontend
if [ ! -f "frontend/.env" ]; then
    echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Run: python main.py      (Backend)"
echo "3. Run: cd frontend && npm start  (Frontend)"
echo "4. Open: http://localhost:3000"
echo ""
echo "For more info, see EXECUTION_GUIDE.md"
