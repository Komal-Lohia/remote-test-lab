"""Save a snapshot from an IP camera as test evidence."""
from datetime import datetime
import requests
from lab.config import ROOT

SNAP_DIR = ROOT / "snapshots"


def snapshot(url, label="snap", timeout=5):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    if not r.headers.get("Content-Type", "").startswith("image"):
        raise ValueError("camera did not return an image")
    SNAP_DIR.mkdir(exist_ok=True)
    name = f"{datetime.now():%Y%m%d_%H%M%S}_{label}.jpg"
    (SNAP_DIR / name).write_bytes(r.content)
    return name