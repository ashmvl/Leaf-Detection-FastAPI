#!/bin/bash

# Start script for Plant Disease Detection API

echo "======================================"
echo "Plant Disease Detection API"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    echo "Virtual environment created!"
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Virtual environment activated!"

# Check if requirements are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Dependencies installed!"
fi

# Check if model exists
if [ ! -f "models/best_model.keras" ]; then
    echo "WARNING: Model file not found at models/best_model.keras"
    echo "Please ensure your model file is in the correct location."
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Start the server
echo ""
echo "Starting the API server..."
echo "Web Interface: http://localhost:8080/static/index.html"
echo "API Docs: http://localhost:8080/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
