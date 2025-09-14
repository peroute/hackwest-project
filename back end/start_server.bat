@echo off
echo Starting Texas Tech University AI Assistant...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup_team.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found. Please create it with your MongoDB credentials.
    echo See TEAM_SETUP_GUIDE.md for instructions.
    pause
    exit /b 1
)

REM Start the server
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
