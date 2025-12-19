@echo off
REM Start script for Plant Disease Detection API (Windows)

echo ======================================
echo Plant Disease Detection API
echo ======================================

REM Check if virtual environment exists
if not exist "venv\" if not exist ".venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created!
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Virtual environment activated!

REM Check if requirements are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed!
)

REM Check if model exists
if not exist "models\best_model.keras" (
    echo WARNING: Model file not found at models\best_model.keras
    echo Please ensure your model file is in the correct location.
    pause
)

REM Start the server
echo.
echo Starting the API server...
echo Web Interface: http://localhost:8080/static/index.html
echo API Docs: http://localhost:8080/docs
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
