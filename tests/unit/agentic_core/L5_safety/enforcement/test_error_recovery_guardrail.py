"""Standalone contracts for the error recovery guardrail test harness."""

from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


def test_threshold_is_unit_interval() -> None:
    assert 0.0 < THRESHOLD <= 1.0


def test_operational_budgets_are_positive() -> None:
    assert MAX_RETRIES > 0
    assert DEFAULT_SLEEP > 0
    assert BUFFER_SIZE > 0
    assert BATCH_SIZE > 0
    assert MAX_DEPTH > 0
    assert MAX_FILES > 0
    assert DEFAULT_TIMEOUT > 0


def test_operational_budgets_are_conservative() -> None:
    assert MAX_RETRIES <= 5
    assert BATCH_SIZE <= 128
    assert DEFAULT_TIMEOUT >= 60


def test_buffer_size_is_power_of_two() -> None:
    assert BUFFER_SIZE & (BUFFER_SIZE - 1) == 0
