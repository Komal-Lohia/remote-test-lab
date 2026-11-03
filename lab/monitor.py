"""Check every device in inventory.yaml, try to recover a stuck board, log everything."""
import platform
import re
import socket
import subprocess
import time
import requests

from lab import db
from lab.board import Board, find_port
from lab.config import load_inventory


def ping(address, timeout=2):
    flag = "-n" if platform.system() == "Windows" else "-c"
    cmd = ["ping", flag, "1", address] + ([] if platform.system() == "Windows" else ["-W", str(timeout)])
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 3)
    m = re.search(r"time[=<]([\d.]+)", out.stdout)
    if out.returncode == 0:
        return "UP", float(m.group(1)) if m else None, ""
    return "DOWN", None, "no ping reply"


def check_host(dev):
    try:
        return ping(dev["address"])
    except subprocess.TimeoutExpired:
        return "DOWN", None, "ping timed out"
    except FileNotFoundError:
        return "DOWN", None, "ping command not installed"


def check_ssh(dev):
    """A test controller is UP when its SSH port answers with an SSH banner."""
    t0 = time.monotonic()
    try:
        with socket.create_connection((dev["address"], dev.get("port", 22)), timeout=3) as s:
            banner = s.recv(64).decode(errors="replace")
        ms = (time.monotonic() - t0) * 1000
        if banner.startswith("SSH-"):
            return "UP", round(ms, 1), ""
        return "DOWN", None, "port open but no SSH banner"
    except OSError as e:
        return "DOWN", None, type(e).__name__


def check_camera(dev):
    t0 = time.monotonic()
    try:
        r = requests.get(dev["url"], timeout=5)
        ms = (time.monotonic() - t0) * 1000
        if r.ok and r.headers.get("Content-Type", "").startswith("image"):
            return "UP", round(ms, 1), ""
        return "DOWN", None, f"HTTP {r.status_code}"
    except requests.RequestException as e:
        return "DOWN", None, type(e).__name__


def board_ping(port):
    with Board(port) as b:
        t0 = time.monotonic()
        reply = b.send("PING")
        ms = (time.monotonic() - t0) * 1000
    return reply == "PONG", round(ms, 1), reply


def check_board(dev, recover=True):
    port = find_port(dev.get("port", "auto"))
    if not port:
        return "DOWN", None, "board not found on USB"
    try:
        ok, ms, reply = board_ping(port)
        if ok:
            return "UP", ms, ""
        detail = f"unexpected reply {reply!r}"
    except (TimeoutError, OSError) as e:
        detail = str(e)
    if not recover or not dev.get("reset_cmd"):
        return "DOWN", None, detail
    # auto-recovery: reset the board once, then check again
    subprocess.run(dev["reset_cmd"].format(port=port), shell=True, capture_output=True, timeout=30)
    time.sleep(4)
    try:
        ok, ms, _ = board_ping(port)
        if ok:
            return "RECOVERED", ms, f"reset after: {detail}"
    except (TimeoutError, OSError):
        pass
    return "DOWN", None, f"still down after reset ({detail})"


CHECKS = {"host": check_host, "ssh": check_ssh, "camera": check_camera, "board": check_board}


def run_once(inventory=None, con=None):
    inventory = inventory or load_inventory()
    con = con or db.connect()
    results = []
    for dev in inventory["devices"]:
        status, ms, detail = CHECKS[dev["type"]](dev)
        old = db.last_status(con, dev["name"])
        if old is not None and old != status:
            con.execute("INSERT INTO alerts VALUES (?,?,?,?)", (db.now(), dev["name"], old, status))
            print(f"ALERT {dev['name']}: {old} -> {status}")
        con.execute("INSERT INTO checks VALUES (?,?,?,?,?,?)",
                    (db.now(), dev["name"], dev["type"], status, ms, detail))
        results.append((dev["name"], status, ms, detail))
    con.commit()
    return results


if __name__ == "__main__":
    for name, status, ms, detail in run_once():
        print(f"{name:15} {status:10} {'' if ms is None else f'{ms} ms':>10}  {detail}")