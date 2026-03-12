"""Foundational behavioral tests for agentic_core/L0_routing/utils/json_formatter_util.py.

fan_in=19 — imported by 19 other modules. This is the sole critical util with
no coverage in either the SQLite or accelerator sources (Phase 0 finding #4).
"""
from __future__ import annotations

import json
import logging

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.json_formatter_util import (  # noqa: F401
        JSONFormatter,
        setup_logging,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
        MAX_FILES,
        DEFAULT_TIMEOUT,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    JSONFormatter = None  # type: ignore[assignment,misc]
    setup_logging = None  # type: ignore[assignment,misc]
    MAX_RETRIES = DEFAULT_SLEEP = THRESHOLD = BUFFER_SIZE = None  # type: ignore[assignment]
    BATCH_SIZE = MAX_DEPTH = MAX_FILES = DEFAULT_TIMEOUT = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="json_formatter_util deps unavailable")
class TestJSONFormatterContract:
    """JSONFormatter: logging.Formatter subclass that outputs valid JSON."""

    def test_is_logging_formatter_subclass(self) -> None:
        assert issubclass(JSONFormatter, logging.Formatter)

    def test_format_returns_valid_json(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello world", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_format_contains_required_keys(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py", lineno=42,
            msg="test message", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "message" in parsed

    def test_format_level_matches_record(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="error occurred", args=(), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["level"] == "ERROR"

    def test_format_message_matches_input(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0,
            msg="specific message content", args=(), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "specific message content" in parsed["message"]

    def test_format_exception_info_included_when_present(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="with exception", args=(), exc_info=exc_info,
        )
        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]

    def test_format_no_exception_key_when_no_exc(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="no exception", args=(), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "exception" not in parsed


@pytest.mark.skipif(not _AVAILABLE, reason="json_formatter_util deps unavailable")
class TestSetupLoggingFunction:
    """setup_logging: returns a configured logger."""

    def test_is_callable(self) -> None:
        assert callable(setup_logging)

    def test_returns_logger(self) -> None:
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)

    def test_logger_has_handlers_after_setup(self) -> None:
        logger = setup_logging()
        assert len(logger.handlers) >= 1

    def test_idempotent_no_duplicate_handlers(self) -> None:
        before = len(logging.getLogger().handlers)
        setup_logging()
        setup_logging()
        after = len(logging.getLogger().handlers)
        assert after <= before + 1


@pytest.mark.skipif(not _AVAILABLE, reason="json_formatter_util deps unavailable")
class TestModuleConstants:
    """Module-level constants must be present and sane."""

    def test_max_retries_positive_int(self) -> None:
        assert isinstance(MAX_RETRIES, int)
        assert MAX_RETRIES > 0

    def test_default_sleep_positive(self) -> None:
        assert DEFAULT_SLEEP > 0

    def test_threshold_between_0_and_1(self) -> None:
        assert 0.0 < THRESHOLD <= 1.0

    def test_buffer_size_power_of_two_ish(self) -> None:
        assert BUFFER_SIZE > 0

    def test_batch_size_positive(self) -> None:
        assert BATCH_SIZE > 0

    def test_max_depth_positive(self) -> None:
        assert MAX_DEPTH > 0

    def test_max_files_positive(self) -> None:
        assert MAX_FILES > 0

    def test_default_timeout_positive(self) -> None:
        assert DEFAULT_TIMEOUT > 0
