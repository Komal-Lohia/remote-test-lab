# Test firmware for the Raspberry Pi Pico (MicroPython).
# It listens on USB serial and answers simple text commands.
import sys
import time
import machine

VERSION = "1.0.0"
START = time.ticks_ms()

try:
    led = machine.Pin("LED", machine.Pin.OUT)   # Pico W and newer firmware
except (TypeError, ValueError):
    led = machine.Pin(25, machine.Pin.OUT)      # older Pico firmware

sensor = machine.ADC(4)                         # built-in temperature sensor


def read_temp_c():
    volts = sensor.read_u16() * 3.3 / 65535
    return 27 - (volts - 0.706) / 0.001721


def handle(cmd):
    if cmd == "PING":
        return "PONG"
    if cmd == "VERSION":
        return VERSION
    if cmd == "LED ON":
        led.value(1)
        return "OK"
    if cmd == "LED OFF":
        led.value(0)
        return "OK"
    if cmd == "LED?":
        return "ON" if led.value() else "OFF"
    if cmd == "UPTIME":
        return str(time.ticks_diff(time.ticks_ms(), START) // 1000)
    if cmd == "TEMP":
        return "{:.1f}".format(read_temp_c())
    return "ERR unknown command"


while True:
    line = sys.stdin.readline().strip()
    if line:
        print(handle(line))