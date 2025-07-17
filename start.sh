#!/bin/bash

# Universal Video Downloader Startup Script

echo "🚀 Starting Universal Video Downloader..."
echo "======================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if not already installed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads temp static/images

# Set permissions
chmod 755 downloads temp

echo "🌟 Starting the application..."
echo "💡 Access the application at: http://localhost:5000"
echo "💡 Press Ctrl+C to stop the server"
echo "======================================="

# Run the Flask application
python app.py