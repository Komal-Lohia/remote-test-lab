import os
import pytest
from lab.board import Board, find_port
from lab.config import devices_of_type, load_inventory

BOARDS = devices_of_type(load_inventory(), "board")


@pytest.fixture(scope="session", params=BOARDS, ids=[b["name"] for b in BOARDS])
def board_dev(request):
    return request.param


@pytest.fixture(scope="session")
def board(board_dev):
    port = os.environ.get("LAB_PORT") or find_port(board_dev.get("port", "auto"))
    if not port:
        pytest.skip(f"{board_dev['name']} not connected")
    try:
        b = Board(port)
    except OSError as e:
        pytest.skip(f"{board_dev['name']} not reachable: {e}")
    yield b
    b.close()


@pytest.fixture
def expected_version(board_dev):
    return board_dev["firmware_version"]