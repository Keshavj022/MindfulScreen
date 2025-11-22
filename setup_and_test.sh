#!/bin/bash

echo "=========================================="
echo "MindfulScreen Setup & Test Script"
echo "=========================================="
echo ""

# Stop if any command fails
set -e

echo "Step 1: Cleaning up old data..."
rm -rf data/
rm -f *.db
mkdir -p data/uploads data/frames data/knowledge_graphs

echo "Step 2: Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    exit 1
fi

echo "Step 3: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "Step 4: Activating virtual environment..."
source venv/bin/activate

echo "Step 5: Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Step 6: Checking .env file..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating .env from example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env and add your OpenAI API key!"
    echo "Then run this script again."
    exit 1
fi

echo "Step 7: Initializing database..."
python3 run.py --init-demo &
sleep 5
pkill -f "python3 run.py"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "✅ Database created"
echo "✅ Demo user initialized"
echo ""
echo "Demo Login Credentials:"
echo "  Email: demo@mindfulscreen.com"
echo "  Password: demo123"
echo ""
echo "To start the application:"
echo "  python3 run.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
echo "=========================================="
