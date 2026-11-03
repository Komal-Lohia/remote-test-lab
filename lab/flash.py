"""Flash firmware to a board: the fake board gets a FLASH command, a real Pico gets mpremote."""
import argparse
import re
import subprocess

from lab.board import Board, find_port
from lab.config import ROOT, load_inventory

FIRMWARE = ROOT / "firmware" / "main.py"


def firmware_version():
    m = re.search(r'VERSION = "([^"]+)"', FIRMWARE.read_text())
    return m.group(1)


def flash(dev, version=None):
    port = find_port(dev.get("port", "auto"))
    version = version or firmware_version()
    if port.startswith("/tmp/"):                      # fake board
        with Board(port) as b:
            return b.send(f"FLASH {version}")
    subprocess.run(["mpremote", "connect", port, "fs", "cp", str(FIRMWARE), ":main.py",
                    "+", "reset"], check=True)
    return f"OK flashed {version}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("board", help="name from inventory.yaml, e.g. board-01")
    ap.add_argument("--version", help="only for fake boards; default = VERSION in firmware/main.py")
    args = ap.parse_args()
    dev = next(d for d in load_inventory()["devices"] if d["name"] == args.board)
    print(flash(dev, args.version))