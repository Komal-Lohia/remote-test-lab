import sqlite3
from datetime import datetime
from lab.config import ROOT

DB_PATH = ROOT / "lab.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
  ts TEXT, device TEXT, type TEXT, status TEXT, latency_ms REAL, detail TEXT);
CREATE TABLE IF NOT EXISTS runs (
  ts TEXT, passed INTEGER, failed INTEGER, duration_s REAL, snapshot TEXT, report TEXT);
CREATE TABLE IF NOT EXISTS alerts (
  ts TEXT, device TEXT, old_status TEXT, new_status TEXT);
"""


def connect(path=None):
    con = sqlite3.connect(path or DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def now():
    return datetime.now().isoformat(timespec="seconds")


def last_status(con, device):
    row = con.execute(
        "SELECT status FROM checks WHERE device=? ORDER BY rowid DESC LIMIT 1", (device,)
    ).fetchone()
    return row["status"] if row else None


def latest_per_device(con):
    return con.execute(
        "SELECT * FROM checks WHERE rowid IN (SELECT MAX(rowid) FROM checks GROUP BY device) "
        "ORDER BY device"
    ).fetchall()