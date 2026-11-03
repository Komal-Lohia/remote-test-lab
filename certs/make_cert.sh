#!/usr/bin/env bash
# Create a self-signed certificate for the lab dashboard.
set -e
cd "$(dirname "$0")"
IP=$(hostname -I | awk '{print $1}')
DAYS=${DAYS:-90}
openssl req -x509 -newkey rsa:2048 -nodes -days "$DAYS" \
  -keyout lab.key -out lab.crt -subj "/CN=testlab.local" \
  -addext "subjectAltName=DNS:testlab.local,DNS:localhost,IP:${IP:-127.0.0.1}"
chmod 600 lab.key
echo "new certificate valid for $DAYS days"