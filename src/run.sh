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

# Generate SSL cert if missing
if [ ! -f cert.pem ] || [ ! -f key.pem ]; then
    echo "Generating SSL certificate..."
    bash generate_cert.sh
fi

# Run the app with gunicorn + SSL
echo ""
if [ -f cert.pem ] && [ -f key.pem ]; then
    echo "Starting server on https://0.0.0.0:4050"
    echo "Press Ctrl+C to stop"
    echo ""
    exec gunicorn --bind 0.0.0.0:4050 \
        --workers 4 \
        --threads 2 \
        --certfile cert.pem \
        --keyfile key.pem \
        app:app
else
    echo "WARNING: No SSL certs found. Starting without HTTPS."
    echo "Starting server on http://0.0.0.0:4050"
    echo "Press Ctrl+C to stop"
    echo ""
    exec gunicorn --bind 0.0.0.0:4050 \
        --workers 4 \
        --threads 2 \
        app:app
fi
