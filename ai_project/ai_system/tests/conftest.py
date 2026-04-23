import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai_system.tests.utils import Cassette


def pytest_configure(config) -> None:
    # Ensures the cache directory exists before tests run.
    Cassette()


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--cache-mode",
        action="store",
        default=None,
        help="Set TEST_CACHE_MODE for cassettes: record or replay",
    )


def pytest_sessionstart(session) -> None:
    mode = session.config.getoption("--cache-mode")
    if mode:
        import os

        os.environ["TEST_CACHE_MODE"] = mode


@pytest.fixture()
def cassette() -> Cassette:
    return Cassette()
