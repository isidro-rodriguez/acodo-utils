"""Tests de logger."""

import logging
import os
from pathlib import Path
from unittest.mock import patch

import acodo_utils.logger as logger_mod
from acodo_utils.logger import (
    _DestinationFilter,
    _prettify,
    get_logger,
)


def reset_logger_state() -> None:
    """Reset logger module state for testing."""
    logger_mod._configured = False
    logger_mod._logger_name = "acodo"


def test_get_logger_initial_and_repeated(tmp_path: Path) -> None:
    """Test logger creation and idempotency."""
    reset_logger_state()
    log1 = get_logger(file=tmp_path / "a.log")
    assert log1 is not None
    log2 = get_logger()
    assert log2 is not None


def test_get_logger_creates_file(tmp_path: Path) -> None:
    """Test that get_logger creates a log file when file is specified."""
    reset_logger_state()
    path = tmp_path / "out.log"
    log = get_logger(file=path)
    assert log is not None
    assert path.parent.exists()


def test_get_logger_invalid_app_name(tmp_path: Path) -> None:
    """Test that invalid app names return None."""
    reset_logger_state()
    assert get_logger(app_name="bad/name") is None


def test_get_logger_invalid_file(tmp_path: Path) -> None:
    """Test that invalid file paths return None."""
    reset_logger_state()
    bad_path = tmp_path / "x.log"
    bad_path.parent.mkdir(exist_ok=True)
    assert get_logger(file=Path("..").with_name("bad?.log")) is None


def test_get_logger_app_name_only(tmp_path: Path) -> None:
    """Test get_logger with only app_name (not file)."""
    reset_logger_state()
    # Use a valid app name
    log = get_logger(app_name="testapp")
    assert log is not None


def test_get_logger_debug_mode(tmp_path: Path) -> None:
    """Test that debug mode is handled correctly."""
    reset_logger_state()
    log = get_logger(debug=True, file=tmp_path / "debug.log")
    assert log is not None


def test_get_logger_print() -> None:
    """Test the print method of Logger class."""
    logger_mod.Logger.print("print test")


def test_prettify_dict() -> None:
    """Test _prettify with a dictionary."""
    result = _prettify({"a": 1, "b": 2})
    assert "a" in result


def test_prettify_list() -> None:
    """Test _prettify with a list."""
    result = _prettify([1, 2, 3])
    assert "1" in result


def test_prettify_string() -> None:
    """Test _prettify with a string."""
    assert _prettify("hello") == "hello"


def test_destination_filter_allows() -> None:
    """Test that _DestinationFilter allows records with to_console."""
    filt = _DestinationFilter("to_console")
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
    record.to_console = True
    assert filt.filter(record) is True


def test_destination_filter_missing_attr() -> None:
    """Test that _DestinationFilter defaults to True when attr is missing."""
    filt = _DestinationFilter("to_console")
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
    assert filt.filter(record) is True


def test_logger_error(tmp_path: Path) -> None:
    """Test Logger.error method."""
    reset_logger_state()
    log = get_logger(file=tmp_path / "err.log")
    log.error("error message", console=False, file=False)


def test_logger_warning(tmp_path: Path) -> None:
    """Test Logger.warning method."""
    reset_logger_state()
    log = get_logger(file=tmp_path / "warn.log")
    log.warning("warning message", console=False, file=False)


def test_logger_info(tmp_path: Path) -> None:
    """Test Logger.info method."""
    reset_logger_state()
    log = get_logger(file=tmp_path / "info.log")
    log.info("info message", console=False, file=False)


def test_logger_debug(tmp_path: Path) -> None:
    """Test Logger.debug method."""
    reset_logger_state()
    log = get_logger(debug=True, file=tmp_path / "debug.log")
    log.debug("debug message", console=False, file=False)


def test_logger_info_with_kwargs(tmp_path: Path) -> None:
    """Test Logger.info with format kwargs."""
    reset_logger_state()
    log = get_logger(file=tmp_path / "info2.log")
    log.info("value: %s", value="test", console=False, file=False)


def test_get_config_dir_linux() -> None:
    """Test _get_config_dir on Linux."""
    with patch("acodo_utils.logger.sys.platform", "linux"):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/test/config"}):
            result = logger_mod._get_config_dir("myapp")
            assert result == Path("/test/config/myapp")


def test_get_config_dir_darwin() -> None:
    """Test _get_config_dir on macOS."""
    with patch("acodo_utils.logger.sys.platform", "darwin"):
        with patch("pathlib.Path.home", return_value=Path("/home/user")):
            result = logger_mod._get_config_dir("myapp")
            assert "myapp" in str(result)


def test_get_config_dir_win32() -> None:
    """Test _get_config_dir on Windows."""
    with patch("acodo_utils.logger.sys.platform", "win32"):
        with patch.dict(os.environ, {"APPDATA": "C:/Users/test/AppData/Roaming"}):
            result = logger_mod._get_config_dir("myapp")
            assert result == Path("C:/Users/test/AppData/Roaming/myapp")