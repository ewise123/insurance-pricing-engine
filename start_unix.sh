#!/bin/bash

echo "============================================================"
echo "AI-Augmented Dynamic Pricing Engine"
echo "============================================================"
echo ""

echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.10 or higher"
    exit 1
fi
echo ""

echo "Starting backend server..."
echo ""
echo "Backend will start at http://localhost:8000"
echo ""
echo "To use the system:"
echo "1. Wait for 'Uvicorn running on...' message"
echo "2. Open frontend.html in your web browser"
echo "3. Select a customer and watch it score!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 backend_api.py
