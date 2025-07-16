#!/bin/bash

# Mimir API Environment Setup Script
# This script helps initialize the environment configuration

set -e

echo "🚀 Mimir API Environment Setup"
echo "================================"

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p /home/user/data/{chromadb,uploads,tmp,logs}

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your actual configuration."
else
    echo "⚠️  .env file already exists. Skipping template copy."
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your Azure OpenAI credentials"
echo "2. Generate a hashed admin password:"
echo "   python -c \"import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())\""
echo "3. Activate the virtual environment: source venv/bin/activate"
echo "4. Run the application: uvicorn app.dependencies:app --host 0.0.0.0 --port 8000"
echo ""
echo "For more information, see the README.md file."
