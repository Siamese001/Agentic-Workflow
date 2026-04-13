#!/usr/bin/env python3
"""
Enhanced HTTP MCP Server - Advanced HTTP client with auth, retries, and async support.

Provides comprehensive HTTP capabilities for Windsurf with enterprise features.
Uses the canonical mcp_bootstrap pattern (FastMCP + @mcp.tool() + run_server)
to avoid the Windows stdio transport hangs caused by low-level Server + anyio.run.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import sys
import time
from typing import Any
from urllib.parse import urlparse

from tools.mcp.mcp_bootstrap import create_mcp_server, run_server

try:
    import aiohttp
except ImportError:
    print("aiohttp not found. Install with: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MAX_RESPONSE_SIZE = 1000000  # 1MB
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTNAMES = {
    "localhost",
    "internal",
    "intranet",
    "corp",
    "private",
}

mcp = create_mcp_server(
    "http",
    "Advanced HTTP client with auth, retries, bounded responses, and batch requests.",
)


# ── Helpers (pure functions — no class state needed) ─────────────────────────


def _validate_url(url: str) -> bool:
    """Validate URL for safety - blocks private IPs, metadata endpoints, and unsafe hostnames"""
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Check for blocked hostnames (exact match only)
        if hostname.lower() in BLOCKED_HOSTNAMES:
            return False

        # Check IP addresses for private ranges
        try:
            ip = ipaddress.ip_address(hostname)

            # Block IPv4 private ranges
            if ip.version == 4:
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
                # Block cloud metadata endpoint
                if ip == ipaddress.IPv4Address("169.254.169.254"):
                    return False

            # Block IPv6 loopback and link-local
            if ip.version == 6:
                if ip.is_loopback or ip.is_link_local:
                    return False
        except ValueError:
            # Not an IP address, hostname already checked above
            pass

        return True
    except (ValueError, AttributeError):
        return False


def _prepare_auth(auth_config: dict[str, Any]) -> tuple | None:
    """Prepare authentication"""
    if not auth_config:
        return None

    auth_type = auth_config.get("type", "").lower()

    if auth_type == "basic":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if username and password:
            return (username, password)

    return None


def _prepare_headers(headers: dict[str, Any], auth_config: dict[str, Any]) -> dict[str, str]:
    """Prepare headers including auth"""
    prepared_headers = {}

    # Add custom headers
    if headers:
        for key, value in headers.items():
            prepared_headers[str(key)] = str(value)

    # Add bearer token
    if auth_config and auth_config.get("type", "").lower() == "bearer":
        token = auth_config.get("token")
        if token:
            prepared_headers["Authorization"] = f"Bearer {token}"

    # Set user agent
    if "User-Agent" not in prepared_headers:
        prepared_headers["User-Agent"] = "Enhanced-HTTP-MCP/1.0"

    return prepared_headers


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive headers from response logging"""
    sensitive_headers = {
        "set-cookie",
        "authorization",
        "proxy-authorization",
        "www-authenticate",
    }
    redacted = {}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


async def _read_response_bounded(response: aiohttp.ClientResponse) -> str:
    """Read response body with size limit to prevent memory exhaustion"""
    content: list[str] = []
    total_read = 0
    chunk_size = 65536  # 64KB chunks

    async for chunk in response.content.iter_chunked(chunk_size):
        total_read += len(chunk)
        if total_read > MAX_RESPONSE_SIZE:
            # Truncate to exactly MAX_RESPONSE_SIZE
            excess = total_read - MAX_RESPONSE_SIZE
            content.append(chunk[: len(chunk) - excess].decode("utf-8", errors="replace"))
            break
        content.append(chunk.decode("utf-8", errors="replace"))

    result = "".join(content)
    if total_read > MAX_RESPONSE_SIZE:
        result = result[:MAX_RESPONSE_SIZE] + "\n... (content truncated)"

    return result


def _prepare_request_data(data: Any, json_mode: bool, headers: dict[str, str]) -> Any:
    """Prepare request body for POST/PUT, setting Content-Type when needed."""
    if data is None:
        return None
    if json_mode and isinstance(data, (dict, list)):
        headers["Content-Type"] = "application/json"
        return json.dumps(data)
    if isinstance(data, dict):
        return data
    return str(data)


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def http_get(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: int = 30,
    follow_redirects: bool = True,
    verify_ssl: bool = True,
    auth: dict[str, Any] | None = None,
) -> str:
    """Perform HTTP GET request with advanced options"""
    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    req_headers = _prepare_headers(headers or {}, auth or {})
    timeout = min(timeout, MAX_TIMEOUT)

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.get(
                url,
                headers=req_headers,
                params=params or {},
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=verify_ssl,
                allow_redirects=follow_redirects,
                max_redirects=MAX_REDIRECTS if follow_redirects else 0,
            ) as response:
                content = await _read_response_bounded(response)
                response_time = time.time() - start_time

                result = f"GET {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n"
                result += f"Content length: {len(content)} bytes\n\n"
                result += "Response headers:\n"
                for k, v in _redact_headers(dict(response.headers)).items():
                    result += f"{k}: {v}\n"
                result += "\n"
                if content:
                    result += f"Response body:\n{content}"
                return result

    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"HTTP GET error: {e}"


@mcp.tool()
async def http_post(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    data: Any = None,
    json: bool = False,
    timeout: int = 30,
    verify_ssl: bool = True,
    auth: dict[str, Any] | None = None,
) -> str:
    """Perform HTTP POST request with body support"""
    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    req_headers = _prepare_headers(headers or {}, auth or {})
    timeout = min(timeout, MAX_TIMEOUT)
    request_data = _prepare_request_data(data, json, req_headers)

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.post(
                url,
                headers=req_headers,
                data=request_data,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=verify_ssl,
            ) as response:
                content = await _read_response_bounded(response)
                response_time = time.time() - start_time

                result = f"POST {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n"
                result += f"Content length: {len(content)} bytes\n\n"
                if request_data:
                    result += f"Request body: {str(request_data)[:500]}\n\n"
                result += "Response headers:\n"
                for k, v in _redact_headers(dict(response.headers)).items():
                    result += f"{k}: {v}\n"
                result += "\n"
                if content:
                    result += f"Response body:\n{content}"
                return result

    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"HTTP POST error: {e}"


@mcp.tool()
async def http_put(
    url: str,
    headers: dict[str, str] | None = None,
    data: Any = None,
    json: bool = False,
    timeout: int = 30,
    verify_ssl: bool = True,
    auth: dict[str, Any] | None = None,
) -> str:
    """Perform HTTP PUT request"""
    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    req_headers = _prepare_headers(headers or {}, auth or {})
    timeout = min(timeout, MAX_TIMEOUT)
    request_data = _prepare_request_data(data, json, req_headers)

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.put(
                url,
                headers=req_headers,
                data=request_data,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=verify_ssl,
            ) as response:
                content = await _read_response_bounded(response)
                response_time = time.time() - start_time

                result = f"PUT {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n"
                if content:
                    result += f"Response body:\n{content}"
                return result

    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"HTTP PUT error: {e}"


@mcp.tool()
async def http_delete(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    auth: dict[str, Any] | None = None,
) -> str:
    """Perform HTTP DELETE request"""
    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    req_headers = _prepare_headers(headers or {}, auth or {})
    timeout = min(timeout, MAX_TIMEOUT)

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.delete(
                url,
                headers=req_headers,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=verify_ssl,
            ) as response:
                content = await _read_response_bounded(response)
                response_time = time.time() - start_time

                result = f"DELETE {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n"
                if content:
                    result += f"Response body:\n{content}"
                return result

    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"HTTP DELETE error: {e}"


@mcp.tool()
async def http_head(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    verify_ssl: bool = True,
) -> str:
    """Perform HTTP HEAD request (headers only)"""
    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    req_headers = _prepare_headers(headers or {}, {})
    timeout = min(timeout, MAX_TIMEOUT)

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.head(
                url,
                headers=req_headers,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=verify_ssl,
            ) as response:
                response_time = time.time() - start_time

                result = f"HEAD {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n\n"
                result += "Response headers:\n"
                for k, v in _redact_headers(dict(response.headers)).items():
                    result += f"{k}: {v}\n"
                return result

    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"HTTP HEAD error: {e}"


@mcp.tool()
async def test_connectivity(
    url: str,
    timeout: int = 10,
) -> str:
    """Test HTTP connectivity to a URL"""
    timeout = min(timeout, 60)

    if not _validate_url(url):
        raise ValueError("Invalid or unsafe URL")

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.head(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=timeout),
                ssl=True,
            ) as response:
                response_time = time.time() - start_time

                result = f"Connectivity test for: {url}\n"
                result += f"Status: {response.status}\n"
                result += f"Response time: {response_time:.2f}s\n"
                result += f"Server: {response.headers.get('Server', 'Unknown')}\n"

                if response.status == 200:
                    result += "Result: Connection successful"
                else:
                    result += f"Result: Connection returned status {response.status}"
                return result

    except asyncio.TimeoutError:
        return f"Connection test timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as e:
        return f"Connection test failed: {e}"


@mcp.tool()
async def batch_requests(
    requests: list[dict[str, Any]],
    max_concurrent: int = 5,
) -> str:
    """Execute multiple HTTP requests in parallel"""
    max_concurrent = min(max_concurrent, 10)

    if len(requests) > 20:
        raise ValueError("Too many requests (max 20)")

    async def _execute_one(req: dict[str, Any]) -> dict[str, Any]:
        method = req["method"].upper()
        url = req["url"]

        if not _validate_url(url):
            return {"method": method, "url": url, "error": "Invalid or unsafe URL"}

        req_headers = _prepare_headers(req.get("headers", {}), req.get("auth", {}))
        req_timeout = min(req.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = req.get("verify_ssl", True)

        try:
            async with aiohttp.ClientSession(trust_env=False) as session:
                async with getattr(session, method.lower())(
                    url,
                    headers=req_headers,
                    data=req.get("data"),
                    timeout=aiohttp.ClientTimeout(total=req_timeout, connect=10, sock_read=req_timeout),
                    ssl=verify_ssl,
                ) as response:
                    content = await _read_response_bounded(response)
                    return {
                        "method": method,
                        "url": url,
                        "status": response.status,
                        "content_length": len(content),
                        "headers": _redact_headers(dict(response.headers)),
                    }
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
            return {"method": method, "url": url, "error": str(e)}

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _bounded(req: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await _execute_one(req)

    tasks = [_bounded(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    result_text = f"Batch HTTP requests ({len(requests)} total, {max_concurrent} concurrent)\n\n"
    for i, res in enumerate(results, 1):
        if isinstance(res, BaseException):
            result_text += f"Request {i}: ERROR\n  Error: {res}\n"
        elif "error" in res:
            result_text += f"Request {i}: {res['method']} {res['url']}\n  Error: {res['error']}\n"
        else:
            result_text += f"Request {i}: {res['method']} {res['url']}\n"
            result_text += f"  Status: {res['status']}\n"
            result_text += f"  Content: {res['content_length']} bytes\n"
        result_text += "\n"

    return result_text


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_server(mcp)
