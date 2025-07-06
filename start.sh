#!/bin/bash

# SmartRecruit Startup Script

echo "🚀 Starting SmartRecruit..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
    echo "   Required: GEMINI_API_KEY, SECRET_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p model/resume/uploads model/resume/parsed data/resumes data/analyses data/metadata

# Start the application
echo "🎯 Starting SmartRecruit API..."
echo "   API: http://localhost:8000"
echo "   Frontend: http://localhost:8000/static/index.html"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 