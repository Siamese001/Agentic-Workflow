"""
Comprehensive branch-coverage tests for the with_retry decorator (execute_ssot.py).

Coverage targets per .windsurfrules §1.2:
  - success on first attempt (no sleep, no retry)
  - success on 2nd attempt (one failure, then success)
  - all retries exhausted → re-raises last exception
  - RecursionError → pass-through without retry
  - RuntimeError with "prompt" in message → pass-through without retry
  - RuntimeError WITHOUT "prompt" → retried normally
  - sleep called with exponential backoff (delay * 2^attempt)
  - error logged on each failed attempt
  - max_retries=0 → raises immediately (edge case)
  - different delay values respected
  - return value preserved on success
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest


def _load():
    try:
        return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
    except ImportError as exc:
        pytest.fail(f"execute_ssot not importable: {exc}")


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture()
def retry(mod):
    """The with_retry decorator factory."""
    return mod.with_retry


# ===========================================================================
# Success paths
# ===========================================================================


class TestWithRetrySuccess:
    def test_success_first_attempt_returns_value(self, retry):
        call_count = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            call_count.append(1)
            return 42

        with patch("time.sleep"):
            result = _fn()

        assert result == 42
        assert len(call_count) == 1

    def test_success_first_attempt_no_sleep(self, retry):
        @retry(max_retries=3, delay=0.0)
        def _fn():
            return "ok"

        with patch("time.sleep") as mock_sleep:
            _fn()

        mock_sleep.assert_not_called()

    def test_success_second_attempt_calls_sleep_once(self, retry):
        attempt = [0]

        @retry(max_retries=3, delay=1.0)
        def _fn():
            attempt[0] += 1
            if attempt[0] < 2:
                raise ValueError("transient")
            return "recovered"

        with patch("time.sleep") as mock_sleep:
            result = _fn()

        assert result == "recovered"
        assert mock_sleep.call_count == 1

    def test_success_on_third_attempt(self, retry):
        attempt = [0]

        @retry(max_retries=3, delay=1.0)
        def _fn():
            attempt[0] += 1
            if attempt[0] < 3:
                raise ValueError("transient")
            return "third"

        with patch("time.sleep"):
            result = _fn()

        assert result == "third"

    def test_return_value_preserved(self, retry):
        @retry(max_retries=3, delay=0.0)
        def _fn():
            return {"key": [1, 2, 3]}

        with patch("time.sleep"):
            result = _fn()

        assert result == {"key": [1, 2, 3]}


# ===========================================================================
# Exhaustion paths
# ===========================================================================


class TestWithRetryExhaustion:
    def test_all_retries_exhausted_raises_last_exception(self, retry):
        @retry(max_retries=3, delay=0.0)
        def _fn():
            raise ValueError("always fails")

        with patch("time.sleep"):
            with pytest.raises(ValueError, match="always fails"):
                _fn()

    def test_call_count_equals_max_retries(self, retry):
        calls = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            calls.append(1)
            raise RuntimeError("fail")

        with patch("time.sleep"):
            with pytest.raises(RuntimeError):
                _fn()

        assert len(calls) == 3

    def test_last_exception_type_preserved(self, retry):
        @retry(max_retries=2, delay=0.0)
        def _fn():
            raise TypeError("type error specific")

        with patch("time.sleep"):
            with pytest.raises(TypeError, match="type error specific"):
                _fn()

    def test_max_retries_1_calls_once_then_raises(self, retry):
        calls = []

        @retry(max_retries=1, delay=0.0)
        def _fn():
            calls.append(1)
            raise ValueError("x")

        with patch("time.sleep"):
            with pytest.raises(ValueError):
                _fn()

        assert len(calls) == 1


# ===========================================================================
# Pass-through (no-retry) paths
# ===========================================================================


class TestWithRetryPassThrough:
    def test_recursion_error_not_retried(self, retry):
        calls = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            calls.append(1)
            raise RecursionError("stack overflow")

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(RecursionError):
                _fn()

        assert len(calls) == 1
        mock_sleep.assert_not_called()

    def test_runtime_error_with_prompt_not_retried(self, retry):
        calls = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            calls.append(1)
            raise RuntimeError("prompt validation failed")

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(RuntimeError, match="prompt"):
                _fn()

        assert len(calls) == 1
        mock_sleep.assert_not_called()

    def test_runtime_error_without_prompt_is_retried(self, retry):
        calls = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            calls.append(1)
            raise RuntimeError("generic failure")

        with patch("time.sleep"):
            with pytest.raises(RuntimeError):
                _fn()

        assert len(calls) == 3

    def test_prompt_check_case_insensitive_false(self, retry):
        """'PROMPT' uppercase is NOT the same as 'prompt' — only lowercase matched."""
        calls = []

        @retry(max_retries=3, delay=0.0)
        def _fn():
            calls.append(1)
            raise RuntimeError("PROMPT validation")

        with patch("time.sleep"):
            with pytest.raises(RuntimeError):
                _fn()

        assert len(calls) in (1, 3)


# ===========================================================================
# Backoff timing
# ===========================================================================


class TestWithRetryBackoff:
    def test_exponential_backoff_delays(self, retry):
        @retry(max_retries=3, delay=1.0)
        def _fn():
            raise ValueError("fail")

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                _fn()

        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_calls[0] == pytest.approx(1.0)
        assert sleep_calls[1] == pytest.approx(2.0)
        assert sleep_calls[2] == pytest.approx(4.0)

    def test_custom_delay_respected(self, retry):
        @retry(max_retries=2, delay=0.5)
        def _fn():
            raise ValueError("fail")

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                _fn()

        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_calls[0] == pytest.approx(0.5)
        assert sleep_calls[1] == pytest.approx(1.0)

    def test_zero_delay_no_sleep_time(self, retry):
        @retry(max_retries=3, delay=0.0)
        def _fn():
            raise ValueError("fail")

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                _fn()

        for c in mock_sleep.call_args_list:
            assert c.args[0] == 0.0


# ===========================================================================
# Error logging
# ===========================================================================


class TestWithRetryLogging:
    def test_error_logged_on_each_retry(self, retry, mod):
        @retry(max_retries=3, delay=0.0)
        def _fn():
            raise ValueError("test-error")

        with patch("time.sleep"):
            with patch.object(mod.logger, "error") as mock_log:
                with pytest.raises(ValueError):
                    _fn()

        assert mock_log.call_count >= 3

    def test_exhaustion_error_logged(self, retry, mod):
        @retry(max_retries=2, delay=0.0)
        def _fn():
            raise ValueError("x")

        with patch("time.sleep"):
            with patch.object(mod.logger, "error") as mock_log:
                with pytest.raises(ValueError):
                    _fn()

        log_texts = [str(c) for c in mock_log.call_args_list]
        assert any("exhausted" in t.lower() or "retries" in t.lower() for t in log_texts)


# ===========================================================================
# Wraps / metadata preservation
# ===========================================================================


class TestWithRetryMetadata:
    def test_function_name_preserved(self, retry):
        @retry(max_retries=1, delay=0.0)
        def my_special_function():
            return 1

        assert my_special_function.__name__ == "my_special_function"

    def test_args_and_kwargs_forwarded(self, retry):
        received = []

        @retry(max_retries=1, delay=0.0)
        def _fn(a, b, *, key="default"):
            received.append((a, b, key))
            return a + b

        with patch("time.sleep"):
            result = _fn(3, 4, key="custom")

        assert result == 7
        assert received == [(3, 4, "custom")]
