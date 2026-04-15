"""
Focused tests for the enhanced HTTP MCP subpackage P0/P1 hardening invariants.
Tests cover: URL blocking, redirect cap, SSL verification, header redaction,
batch partial failure isolation, and bounded response reading.
All network calls are mocked.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from tools.mcp.http_mcp.batch import execute_batch_requests
from tools.mcp.http_mcp.client import execute_connectivity_test, execute_formatted_request
from tools.mcp.http_mcp.constants import MAX_REDIRECTS, MAX_RESPONSE_SIZE
from tools.mcp.http_mcp.headers import redact_headers
from tools.mcp.http_mcp.response_io import read_response_bounded
from tools.mcp.http_mcp.safety import validate_url


# ---------------------------------------------------------------------------
# 1. Private IP / metadata endpoint blocking
# ---------------------------------------------------------------------------
class TestValidateUrl:
    BLOCKED = [
        "http://127.0.0.1/secret",
        "http://127.0.0.2/x",
        "http://10.0.0.1/",
        "http://10.255.255.255/",
        "http://172.16.0.1/",
        "http://172.31.255.255/",
        "http://192.168.1.1/",
        "http://192.168.0.0/",
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.0.1/",
        "http://[::1]/",
        "http://[fe80::1]/",
        "ftp://example.com/",
        "http://localhost/",
        "http://internal/",
        "http://intranet/",
        "http://corp/",
        "http://private/",
        "",
        "not-a-url",
    ]

    ALLOWED = [
        "https://example.com/",
        "http://example.com/",
        "https://api.github.com/repos",
        "http://8.8.8.8/",
    ]

    def test_blocked_urls_are_rejected(self):
        for url in self.BLOCKED:
            assert validate_url(url) is False, f"Expected {url!r} to be blocked"

    def test_allowed_urls_are_accepted(self):
        for url in self.ALLOWED:
            assert validate_url(url) is True, f"Expected {url!r} to be allowed"


# ---------------------------------------------------------------------------
# 2. Redirect cap
# ---------------------------------------------------------------------------
class TestRedirectCap:
    def test_max_redirects_constant_is_bounded(self):
        assert MAX_REDIRECTS <= 10
        assert MAX_REDIRECTS >= 1

    @pytest.mark.asyncio
    async def test_http_get_passes_max_redirects_to_aiohttp(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([b"hello"]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.client.aiohttp.ClientSession", return_value=mock_session):
            await execute_formatted_request(
                method="GET",
                url="https://example.com/",
                headers={},
                timeout=30,
                verify_ssl=True,
                follow_redirects=True,
            )

        call_kwargs = mock_session.get.call_args.kwargs
        assert call_kwargs.get("max_redirects") == MAX_REDIRECTS


# ---------------------------------------------------------------------------
# 3. verify_ssl — test_connectivity always uses ssl=True
# ---------------------------------------------------------------------------
class TestVerifySslTestConnectivity:
    @pytest.mark.asyncio
    async def test_test_connectivity_uses_ssl_true(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Server": "nginx"}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.head = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.client.aiohttp.ClientSession", return_value=mock_session):
            await execute_connectivity_test(url="https://example.com/", timeout=10)

        call_kwargs = mock_session.head.call_args.kwargs
        assert call_kwargs.get("ssl") is True


# ---------------------------------------------------------------------------
# 4. verify_ssl — batch_requests honours per-request verify_ssl
# ---------------------------------------------------------------------------
class TestVerifySslBatchRequests:
    @pytest.mark.asyncio
    async def test_batch_requests_passes_verify_ssl_false(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([b"ok"]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.batch.aiohttp.ClientSession", return_value=mock_session):
            await execute_batch_requests(
                requests=[{"method": "GET", "url": "https://example.com/", "verify_ssl": False}]
            )

        call_kwargs = mock_session.get.call_args.kwargs
        assert call_kwargs.get("ssl") is False

    @pytest.mark.asyncio
    async def test_batch_requests_defaults_verify_ssl_true(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([b"ok"]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.batch.aiohttp.ClientSession", return_value=mock_session):
            await execute_batch_requests(requests=[{"method": "GET", "url": "https://example.com/"}])

        call_kwargs = mock_session.get.call_args.kwargs
        assert call_kwargs.get("ssl") is True


# ---------------------------------------------------------------------------
# 5. Header redaction
# ---------------------------------------------------------------------------
class TestHeaderRedaction:
    def test_sensitive_headers_are_redacted(self):
        headers = {
            "Content-Type": "application/json",
            "Set-Cookie": "session=abc123; Path=/",
            "Authorization": "Bearer secret-token",
            "Proxy-Authorization": "Basic dXNlcjpwYXNz",
            "WWW-Authenticate": "Bearer realm=example",
            "X-Request-Id": "req-123",
        }
        result = redact_headers(headers)

        assert result["Set-Cookie"] == "[REDACTED]"
        assert result["Authorization"] == "[REDACTED]"
        assert result["Proxy-Authorization"] == "[REDACTED]"
        assert result["WWW-Authenticate"] == "[REDACTED]"

    def test_non_sensitive_headers_are_preserved(self):
        headers = {
            "Content-Type": "application/json",
            "X-Request-Id": "req-123",
            "Content-Length": "42",
        }
        result = redact_headers(headers)

        assert result["Content-Type"] == "application/json"
        assert result["X-Request-Id"] == "req-123"
        assert result["Content-Length"] == "42"

    def test_redaction_is_case_insensitive(self):
        headers = {
            "set-cookie": "session=abc",
            "AUTHORIZATION": "Bearer token",
        }
        result = redact_headers(headers)

        assert result["set-cookie"] == "[REDACTED]"
        assert result["AUTHORIZATION"] == "[REDACTED]"

    @pytest.mark.asyncio
    async def test_batch_response_headers_are_redacted(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {
            "Content-Type": "application/json",
            "Set-Cookie": "session=abc; Path=/",
            "Authorization": "Bearer leak",
        }
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([b"body"]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.batch.aiohttp.ClientSession", return_value=mock_session):
            output = await execute_batch_requests(requests=[{"method": "GET", "url": "https://example.com/"}])

        assert "session=abc" not in output
        assert "Bearer leak" not in output


# ---------------------------------------------------------------------------
# 6. Batch partial failure isolation
# ---------------------------------------------------------------------------
class TestBatchPartialFailureIsolation:
    @pytest.mark.asyncio
    async def test_one_failed_request_does_not_abort_batch(self):
        """First request fails with network error; second should still succeed."""
        import aiohttp as _aiohttp

        def make_failing_cm():
            """Returns a context manager that raises on __aenter__."""
            cm = MagicMock()
            cm.__aenter__ = AsyncMock(side_effect=_aiohttp.ClientConnectionError("refused"))
            cm.__aexit__ = AsyncMock(return_value=False)
            return cm

        def make_ok_cm():
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.headers = {}
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=False)
            mock_resp.content = MagicMock()
            mock_resp.content.iter_chunked = MagicMock(return_value=_async_iter([b"ok"]))
            return mock_resp

        _calls = [0]

        def side_effect_get(*args, **kwargs):
            _calls[0] += 1
            if _calls[0] == 1:
                return make_failing_cm()
            return make_ok_cm()

        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=side_effect_get)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.batch.aiohttp.ClientSession", return_value=mock_session):
            text = await execute_batch_requests(
                requests=[
                    {"method": "GET", "url": "https://fail.example.com/"},
                    {"method": "GET", "url": "https://ok.example.com/"},
                ]
            )

        assert isinstance(text, str)
        assert "\u274c" in text
        assert "\u2705" in text

    @pytest.mark.asyncio
    async def test_blocked_url_in_batch_does_not_abort_batch(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([b"ok"]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.batch.aiohttp.ClientSession", return_value=mock_session):
            text = await execute_batch_requests(
                requests=[
                    {"method": "GET", "url": "http://127.0.0.1/steal"},
                    {"method": "GET", "url": "https://example.com/"},
                ]
            )

        assert isinstance(text, str)
        assert "Invalid or unsafe URL" in text
        assert "\u2705" in text


# ---------------------------------------------------------------------------
# 7. Bounded response reading / truncation
# ---------------------------------------------------------------------------
class TestBoundedResponseReading:
    @pytest.mark.asyncio
    async def test_response_within_limit_is_returned_fully(self):
        body = b"hello world"
        mock_response = MagicMock()
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([body]))

        result = await read_response_bounded(mock_response)
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_response_exceeding_limit_is_truncated(self):
        oversized = b"x" * (MAX_RESPONSE_SIZE + 5000)
        mock_response = MagicMock()
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([oversized]))

        result = await read_response_bounded(mock_response)
        assert "(content truncated)" in result
        assert len(result) <= MAX_RESPONSE_SIZE + 30  # small allowance for suffix

    @pytest.mark.asyncio
    async def test_response_exactly_at_limit_is_not_truncated(self):
        exact = b"y" * MAX_RESPONSE_SIZE
        mock_response = MagicMock()
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([exact]))

        result = await read_response_bounded(mock_response)
        assert "(content truncated)" not in result
        assert len(result) == MAX_RESPONSE_SIZE

    @pytest.mark.asyncio
    async def test_http_get_uses_bounded_read(self):
        oversized_chunk = b"z" * (MAX_RESPONSE_SIZE + 10000)
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_response.content = MagicMock()
        mock_response.content.iter_chunked = MagicMock(return_value=_async_iter([oversized_chunk]))

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("tools.mcp.http_mcp.client.aiohttp.ClientSession", return_value=mock_session):
            result = await execute_formatted_request(
                method="GET",
                url="https://example.com/",
                headers={},
                timeout=30,
                verify_ssl=True,
                include_content_length=True,
                include_headers=True,
            )

        assert "(content truncated)" in result


# ---------------------------------------------------------------------------
# Async generator helper for mocking iter_chunked
# ---------------------------------------------------------------------------
async def _async_gen(chunks):
    for chunk in chunks:
        yield chunk


def _async_iter(chunks):
    return _async_gen(chunks)
