#!/usr/bin/env python3
"""test_retry.py — Unit tests for _notion_retry module."""
import time
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from tools.notion._notion_retry import (
    MAX_BACKOFF_SECONDS,
    MAX_RETRIES,
    NON_RETRYABLE_STATUS_CODES,
    RETRYABLE_STATUS_CODES,
    HTTPResponse,
    RetryContext,
    RetryResult,
    _calculate_backoff,
    _extract_retry_after,
    _extract_status_code,
    _is_retryable,
    _urlopen_with_retry,
    add_idempotency_header,
    make_idempotency_key,
    urlopen_with_retry,
    with_retry,
)


class TestStatusCodeExtraction:
    """Tests for _extract_status_code."""
    
    def test_extract_from_http_error(self):
        error = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None,
        )
        assert _extract_status_code(error) == 429
    
    def test_extract_from_wrapped_error(self):
        inner = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=None,
        )
        outer = Exception("Wrapped")
        outer.__cause__ = inner
        assert _extract_status_code(outer) == 503
    
    def test_none_for_non_http_error(self):
        assert _extract_status_code(ValueError("Not HTTP")) is None


class TestRetryAfterExtraction:
    """Tests for _extract_retry_after."""
    
    def test_extract_retry_after_header(self):
        class MockHeaders:
            def get(self, key):
                return "2" if key == "Retry-After" else None
        
        error = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=429,
            msg="Too Many Requests",
            hdrs=MockHeaders(),
            fp=None,
        )
        assert _extract_retry_after(error) == 2.0
    
    def test_none_when_header_missing(self):
        error = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None,
        )
        assert _extract_retry_after(error) is None


class TestIsRetryable:
    """Tests for _is_retryable."""
    
    def test_retryable_status_codes(self):
        for code in RETRYABLE_STATUS_CODES:
            error = urllib.error.HTTPError(
                url="https://api.notion.com/v1/pages",
                code=code,
                msg="Error",
                hdrs={},
                fp=None,
            )
            assert _is_retryable(error) is True, f"Status {code} should be retryable"
    
    def test_non_retryable_status_codes(self):
        for code in NON_RETRYABLE_STATUS_CODES:
            error = urllib.error.HTTPError(
                url="https://api.notion.com/v1/pages",
                code=code,
                msg="Error",
                hdrs={},
                fp=None,
            )
            assert _is_retryable(error) is False, f"Status {code} should not be retryable"
    
    def test_5xx_is_retryable(self):
        error = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=500,
            msg="Internal Error",
            hdrs={},
            fp=None,
        )
        assert _is_retryable(error) is True
    
    def test_network_errors_are_retryable(self):
        # Non-HTTP errors (timeouts, connection issues) are retryable
        assert _is_retryable(TimeoutError("Connection timed out")) is True
        assert _is_retryable(ConnectionError("Connection reset")) is True


class TestBackoffCalculation:
    """Tests for _calculate_backoff."""
    
    def test_exponential_backoff(self):
        # 1s, 2s, 4s
        assert _calculate_backoff(0) == 1.0
        assert _calculate_backoff(1) == 2.0
        assert _calculate_backoff(2) == 4.0
    
    def test_max_backoff_cap(self):
        # Should cap at MAX_BACKOFF_SECONDS
        delay = _calculate_backoff(10)
        assert delay <= MAX_BACKOFF_SECONDS
    
    def test_respects_retry_after_header(self):
        class MockHeaders:
            def get(self, key):
                return "5" if key == "Retry-After" else None
        
        error = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=429,
            msg="Too Many Requests",
            hdrs=MockHeaders(),
            fp=None,
        )
        delay = _calculate_backoff(0, error)
        assert delay == 5.0


class TestRetryDecorator:
    """Tests for @with_retry decorator."""
    
    def test_success_on_first_attempt(self):
        call_count = 0
        
        @with_retry(max_retries=2)
        def succeed_immediately():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = succeed_immediately()
        
        assert result.success is True
        assert result.result == "success"
        assert result.context.attempt == 0
        assert call_count == 1
    
    def test_retry_then_success(self):
        call_count = 0
        
        @with_retry(max_retries=2)
        def succeed_on_third():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = succeed_on_third()
        
        assert result.success is True
        assert call_count == 3
        assert result.context.attempt == 2
    
    def test_fail_after_max_retries(self):
        call_count = 0
        
        @with_retry(max_retries=2)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent failure")
        
        result = always_fail()
        
        assert result.success is False
        assert call_count == 3  # Initial + 2 retries
        assert result.error is not None
    
    def test_non_retryable_fails_fast(self):
        call_count = 0
        
        @with_retry(max_retries=2)
        def fail_non_retryable():
            nonlocal call_count
            call_count += 1
            raise urllib.error.HTTPError(
                url="https://api.notion.com/v1/pages",
                code=400,
                msg="Bad Request",
                hdrs={},
                fp=None,
            )
        
        result = fail_non_retryable()
        
        assert result.success is False
        assert call_count == 1  # No retries for 400
    
    def test_retry_callback_invoked(self):
        callback_calls = []
        
        def on_retry(error, attempt, delay):
            callback_calls.append((type(error).__name__, attempt, delay))
        
        @with_retry(max_retries=1, on_retry=on_retry)
        def fail_once():
            raise ConnectionError("Temporary")
        
        fail_once()
        
        assert len(callback_calls) == 1
        assert callback_calls[0][0] == "ConnectionError"
        assert callback_calls[0][1] == 0


class TestIdempotencyKey:
    """Tests for idempotency key generation."""
    
    def test_make_idempotency_key_unique(self):
        key1 = make_idempotency_key()
        key2 = make_idempotency_key()
        assert key1 != key2
        assert len(key1) == 36  # UUID length
    
    def test_add_idempotency_header(self):
        headers = {"Content-Type": "application/json"}
        new_headers = add_idempotency_header(headers)
        
        assert "Idempotency-Key" in new_headers
        assert len(new_headers["Idempotency-Key"]) == 36
        # Original headers unchanged
        assert "Idempotency-Key" not in headers


class TestRetryResult:
    """Tests for RetryResult data class."""
    
    def test_to_dict_success(self):
        context = RetryContext(
            attempt=0,
            max_retries=2,
            succeeded=True,
            total_delay_ms=0.0,
        )
        result = RetryResult(
            success=True,
            result="data",
            context=context,
        )
        
        d = result.to_dict()
        assert d["success"] is True
        assert d["context"]["succeeded"] is True
        assert d["context"]["attempt"] == 0
        assert d["error"] is None
    
    def test_to_dict_failure(self):
        error = ValueError("Test error")
        context = RetryContext(
            attempt=2,
            max_retries=2,
            succeeded=False,
            total_delay_ms=3000.0,
        )
        result = RetryResult(
            success=False,
            error=error,
            context=context,
        )
        
        d = result.to_dict()
        assert d["success"] is False
        assert d["error"] == "Test error"
        assert d["context"]["total_delay_ms"] == 3000.0


class TestUrlopenWithRetry:
    """Tests for urlopen_with_retry function."""
    
    @patch('urllib.request.urlopen')
    def test_success_no_retry(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"id": "page-123"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_urlopen.return_value = mock_response
        
        request = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=b'{}',
            headers={"Authorization": "Bearer token"},
        )
        
        result = urlopen_with_retry(request)
        
        assert result.status == 200
        assert result.body == b'{"id": "page-123"}'
        assert mock_urlopen.call_count == 1
    
    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_retry_on_429(self, mock_sleep, mock_urlopen):
        # First two calls fail with 429, third succeeds
        mock_urlopen.side_effect = [
            urllib.error.HTTPError(
                url="https://api.notion.com/v1/pages",
                code=429,
                msg="Too Many Requests",
                hdrs={"Retry-After": "1"},
                fp=None,
            ),
            urllib.error.HTTPError(
                url="https://api.notion.com/v1/pages",
                code=429,
                msg="Too Many Requests",
                hdrs={"Retry-After": "1"},
                fp=None,
            ),
            MagicMock(status=200, read=lambda: b'{}', headers={}),
        ]
        
        request = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=b'{}',
            headers={"Authorization": "Bearer token"},
        )
        
        result = urlopen_with_retry(request)
        
        assert result.status == 200
        assert mock_urlopen.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries with sleep
    
    @patch('urllib.request.urlopen')
    def test_fail_fast_on_400(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.notion.com/v1/pages",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=None,
        )
        
        request = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=b'{}',
            headers={"Authorization": "Bearer token"},
        )
        
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urlopen_with_retry(request)
        
        assert exc_info.value.code == 400
        assert mock_urlopen.call_count == 1  # No retries
