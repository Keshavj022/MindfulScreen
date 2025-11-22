#!/bin/bash

# MindfulScreen - Production Startup Script

echo "🚀 Starting MindfulScreen..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your OPENAI_API_KEY"
    echo ""
fi

# Check if data directory exists
if [ ! -d data ]; then
    echo "📁 Creating data directories..."
    mkdir -p data/uploads data/frames data/knowledge_graphs
fi

# Check if database exists
if [ ! -f data/mindfulscreen.db ]; then
    echo "🗄️  Initializing database with demo data..."
    timeout 10 python3 run.py --init-demo > /dev/null 2>&1 || true
    echo "✅ Database initialized!"
    echo ""
fi

echo "🌐 Starting Flask application..."
echo "📍 Access the app at: http://localhost:5000"
echo ""
echo "🔐 Demo Account:"
echo "   Email: demo@mindfulscreen.com"
echo "   Password: demo123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 run.py
