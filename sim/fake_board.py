"""A fake Pico on a virtual serial port (Linux / WSL / Mac).

Run one per board:
  python sim/fake_board.py --name board-01
  python sim/fake_board.py --name board-02 --version 1.0.0
Make a board hang:   touch sim/HANG-board-01
"Reset" it:          rm sim/HANG-board-01
"""
import argparse
import json
import os
import pty
import time
import tty
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_DIR = HERE / "state"


class FakeBoard:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.led = False
        self.start = time.time()
        self.hang_file = HERE / f"HANG-{name}"
        self.save()

    def save(self):
        STATE_DIR.mkdir(exist_ok=True)
        state = {"name": self.name, "version": self.version, "led": self.led,
                 "hung": self.hang_file.exists(), "updated": time.time()}
        (STATE_DIR / f"{self.name}.json").write_text(json.dumps(state))

    def handle(self, cmd):
        if cmd == "PING":
            return "PONG"
        if cmd == "VERSION":
            return self.version
        if cmd in ("LED ON", "LED OFF"):
            self.led = cmd == "LED ON"
            return "OK"
        if cmd == "LED?":
            return "ON" if self.led else "OFF"
        if cmd == "UPTIME":
            return str(int(time.time() - self.start))
        if cmd == "TEMP":
            return "24.5"
        if cmd.startswith("FLASH "):            # simulated firmware update
            self.version = cmd.split(" ", 1)[1]
            self.led = False
            self.start = time.time()            # a flash reboots the board
            return "OK flashed " + self.version
        return "ERR unknown command"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="board-01")
    ap.add_argument("--version", default="1.0.0")
    args = ap.parse_args()

    board = FakeBoard(args.name, args.version)
    link = f"/tmp/{args.name}"
    master, slave = pty.openpty()
    tty.setraw(slave)                      # no echo, no line editing
    if os.path.lexists(link):
        os.remove(link)
    os.symlink(os.ttyname(slave), link)
    print(f"{args.name} ready on {link}  (Ctrl+C to stop)", flush=True)

    buf = b""
    while True:
        buf += os.read(master, 1024)
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            cmd = line.decode().strip()
            if not cmd or board.hang_file.exists():
                board.save()
                continue
            os.write(master, (board.handle(cmd) + "\r\n").encode())
            board.save()


if __name__ == "__main__":
    main()