"""Tests de logger."""

from pathlib import Path

from acodo_utils.logger import get_logger


def test_get_logger_initial_and_repeated(tmp_path: Path) -> None:
    logger = get_logger(app_name="testapp", file=tmp_path / "a.log")
    assert logger is not None
    again = get_logger()
    assert again is not None


def test_get_logger_invalid() -> None:
    assert get_logger(app_name="bad/name") is None
    assert get_logger(file=Path("x").with_name("bad?.log")) is None


def test_get_logger_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "out.log"
    logger = get_logger(file=path)
    assert logger is not None
    assert path.parent.exists()
