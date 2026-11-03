#!/usr/bin/env bash
# Renew the certificate when it has less than 30 days left, then restart the dashboard.
# Runs as root from cert-renew.service (step 12).
cd "$(dirname "$0")/.."
if ! .venv/bin/python -m lab.cert_check --min-days 30; then
  bash certs/make_cert.sh
  chown "$(stat -c %U:%G .)" certs/lab.key certs/lab.crt   # dashboard user must read the key
  systemctl restart lab-dashboard
  echo "$(date -Is) certificate renewed" >> certs/renew.log
fi