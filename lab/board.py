"""Talk to the target board over USB serial."""
import time
import serial
from serial.tools import list_ports

PICO_VID = 0x2E8A  # USB vendor id of Raspberry Pi boards


def find_port(preferred="auto"):
    if preferred and preferred != "auto":
        return preferred
    for p in list_ports.comports():
        if p.vid == PICO_VID:
            return p.device
    return None


class Board:
    def __init__(self, port, baud=115200, timeout=2.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(0.2)
        self.ser.reset_input_buffer()

    def send(self, cmd):
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\n").encode())
        deadline = time.monotonic() + self.ser.timeout
        while time.monotonic() < deadline:
            line = self.ser.readline().decode(errors="replace").strip()
            if line and line != cmd:      # skip an echo of our own command
                return line
        raise TimeoutError(f"no reply to {cmd!r}")

    def close(self):
        self.ser.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        