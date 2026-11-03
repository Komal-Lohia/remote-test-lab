import time


def test_ping(board):
    assert board.send("PING") == "PONG"


def test_firmware_version(board, expected_version):
    assert board.send("VERSION") == expected_version


def test_led_on_off(board):
    assert board.send("LED ON") == "OK"
    assert board.send("LED?") == "ON"
    assert board.send("LED OFF") == "OK"
    assert board.send("LED?") == "OFF"


def test_uptime_counts_up(board):
    first = int(board.send("UPTIME"))
    time.sleep(1.2)
    assert int(board.send("UPTIME")) > first


def test_temperature_is_plausible(board):
    assert 5 < float(board.send("TEMP")) < 70


def test_unknown_command(board):
    assert board.send("FOO").startswith("ERR")


def test_reply_is_fast(board):
    t0 = time.monotonic()
    board.send("PING")
    assert time.monotonic() - t0 < 0.2   # 200 ms