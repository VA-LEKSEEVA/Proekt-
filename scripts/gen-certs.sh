#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="${1:-$(pwd)/certs}"
DAYS="${DAYS:-825}"
SUBJ="/C=RU/ST=Local/L=Local/O=Dev/OU=Dev/CN=localhost"

mkdir -p "$CERT_DIR"

if [[ -f "$CERT_DIR/server.crt" && -f "$CERT_DIR/server.key" && "${FORCE:-0}" != "1" ]]; then
    echo "Сертификаты уже есть в $CERT_DIR (FORCE=1 для перегенерации)"
    exit 0
fi

openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout "$CERT_DIR/server.key" \
    -out    "$CERT_DIR/server.crt" \
    -days   "$DAYS" \
    -subj   "$SUBJ" \
    -addext "subjectAltName=DNS:localhost,DNS:nginx,IP:127.0.0.1"

chmod 600 "$CERT_DIR/server.key"
chmod 644 "$CERT_DIR/server.crt"

echo "OK:"
echo "  $CERT_DIR/server.crt"
echo "  $CERT_DIR/server.key"