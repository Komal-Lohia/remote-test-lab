"""Tests without hardware: fake the board and check the recovery logic."""
from lab import monitor


def test_board_up(monkeypatch):
    monkeypatch.setattr(monitor, "find_port", lambda p: "/dev/fake")
    monkeypatch.setattr(monitor, "board_ping", lambda port: (True, 3.0, "PONG"))
    assert monitor.check_board({"port": "auto"})[0] == "UP"


def test_board_missing(monkeypatch):
    monkeypatch.setattr(monitor, "find_port", lambda p: None)
    assert monitor.check_board({"port": "auto"})[0] == "DOWN"


def test_board_recovers_after_reset(monkeypatch):
    replies = iter([TimeoutError("no reply"), (True, 4.0, "PONG")])

    def fake_ping(port):
        r = next(replies)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(monitor, "find_port", lambda p: "/dev/fake")
    monkeypatch.setattr(monitor, "board_ping", fake_ping)
    monkeypatch.setattr(monitor.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(monitor.time, "sleep", lambda s: None)
    status, _, detail = monitor.check_board({"port": "auto", "reset_cmd": "true"})
    assert status == "RECOVERED" and "no reply" in detail