"""Run the hardware tests, take camera evidence and save the result."""
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

from lab import db
from lab.camera import snapshot
from lab.config import ROOT, devices_of_type, load_inventory


def summarize(report_path):
    root = ET.parse(report_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.get("tests", 0))
    bad = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    return total - int(suite.get("skipped", 0)) - bad, bad


def main():
    inv = load_inventory()
    (ROOT / "results").mkdir(exist_ok=True)
    report = ROOT / "results" / f"{datetime.now():%Y%m%d_%H%M%S}.xml"
    t0 = time.monotonic()
    subprocess.run([sys.executable, "-m", "pytest", str(ROOT / "tests" / "hardware"),
                    "-q", f"--junitxml={report}"], cwd=ROOT)
    duration = round(time.monotonic() - t0, 1)
    passed, failed = summarize(report)
    snap = None
    cams = devices_of_type(inv, "camera")
    if cams:
        try:
            snap = snapshot(cams[0]["url"], label="after_tests")
        except Exception as e:
            print("camera snapshot failed:", e)
    con = db.connect()
    con.execute("INSERT INTO runs VALUES (?,?,?,?,?,?)",
                (db.now(), passed, failed, duration, snap, report.name))
    con.commit()
    print(f"passed={passed} failed={failed} in {duration}s, snapshot={snap}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())