"""Web dashboard for the test lab (HTTPS + password)."""
import os
import subprocess
import sys
from functools import wraps
from flask import Flask, Response, redirect, render_template, request, send_from_directory, url_for

from lab import db
from lab.cert_check import days_left
from lab.config import ROOT, load_inventory
from lab.monitor import run_once

app = Flask(__name__)
PASSWORD = os.environ.get("LAB_PASSWORD", "change-me")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != PASSWORD:
            return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Test Lab"'})
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
@login_required
def index():
    con = db.connect()
    devices = db.latest_per_device(con)
    runs = con.execute("SELECT * FROM runs ORDER BY rowid DESC LIMIT 10").fetchall()
    alerts = con.execute("SELECT * FROM alerts ORDER BY rowid DESC LIMIT 5").fetchall()
    try:
        cert_days = days_left()
    except FileNotFoundError:
        cert_days = None
    return render_template("index.html", lab=load_inventory()["lab_name"], devices=devices,
                           runs=runs, alerts=alerts, cert_days=cert_days)


@app.post("/check")
@login_required
def check_now():
    run_once()
    return redirect(url_for("index"))


@app.post("/run-tests")
@login_required
def run_tests():
    subprocess.Popen([sys.executable, "-m", "lab.run_tests"], cwd=ROOT)
    return redirect(url_for("index"))


@app.route("/snapshots/<path:name>")
@login_required
def snapshot_file(name):
    return send_from_directory(ROOT / "snapshots", name)


if __name__ == "__main__":
    cert, key = ROOT / "certs" / "lab.crt", ROOT / "certs" / "lab.key"
    app.run(host="0.0.0.0", port=8443, ssl_context=(str(cert), str(key)))