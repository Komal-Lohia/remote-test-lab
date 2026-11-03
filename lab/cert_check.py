"""How many days until the dashboard's SSL certificate expires?"""
import argparse
import sys
from datetime import datetime, timezone
from cryptography import x509
from lab.config import ROOT

CERT = ROOT / "certs" / "lab.crt"


def days_left(path=CERT):
    cert = x509.load_pem_x509_certificate(open(path, "rb").read())
    expires = cert.not_valid_after_utc
    return (expires - datetime.now(timezone.utc)).days


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-days", type=int, default=30)
    args = ap.parse_args()
    d = days_left()
    print(f"certificate expires in {d} days")
    sys.exit(0 if d >= args.min_days else 1)   # exit 1 = renew needed