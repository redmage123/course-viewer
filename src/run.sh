#!/bin/bash
# Course Material Viewer - Startup Script

cd "$(dirname "$0")"

echo "=============================================="
echo "  Mastering LLMs - Course Material Viewer"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the app
echo ""
echo "Starting server on http://localhost:4050"
echo "Press Ctrl+C to stop"
echo ""
python app.py
