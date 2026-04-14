"""Behavioral tests for execution_util_adg."""

from __future__ import annotations

import pytest

from agentic_core.execution_util_adg import clamp_retry_count, next_backoff_seconds


def test_retry_count_is_clamped_to_bounds():
    assert clamp_retry_count(-3) == 0
    assert clamp_retry_count(9, maximum=4) == 4


def test_backoff_grows_exponentially():
    assert next_backoff_seconds(0, base=0.5) == 0.5
    assert next_backoff_seconds(2, base=0.5) == 2.0


def test_negative_retry_count_rejected():
    with pytest.raises(ValueError):
        next_backoff_seconds(-1)
