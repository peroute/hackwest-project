#!/bin/bash

echo "Starting Texas Tech University AI Assistant..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup_team.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ".env file not found. Please create it with your MongoDB credentials."
    echo "See TEAM_SETUP_GUIDE.md for instructions."
    exit 1
fi

# Start the server
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
