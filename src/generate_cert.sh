#!/bin/bash
# Generate a self-signed SSL certificate for the course viewer
# Certificate is valid for 365 days with the server IP as SAN

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERT_FILE="$SCRIPT_DIR/cert.pem"
KEY_FILE="$SCRIPT_DIR/key.pem"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "Certificate files already exist:"
    echo "  $CERT_FILE"
    echo "  $KEY_FILE"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "Generating self-signed SSL certificate..."

openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -subj "/CN=176.9.99.103" \
    -addext "subjectAltName=IP:176.9.99.103"

if [ $? -eq 0 ]; then
    echo ""
    echo "Certificate generated successfully:"
    echo "  Certificate: $CERT_FILE"
    echo "  Private key: $KEY_FILE"
    echo ""
    echo "Restart the app to enable HTTPS."
else
    echo "ERROR: Failed to generate certificate."
    exit 1
fi
