"""Core HTTP execution functions."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import aiohttp

from tools.mcp.http_mcp.constants import CONNECT_TIMEOUT, MAX_REDIRECTS, MAX_TIMEOUT
from tools.mcp.http_mcp.formatters import (
    format_connectivity_response,
    format_head_response,
    format_http_response,
)
from tools.mcp.http_mcp.headers import redact_headers
from tools.mcp.http_mcp.response_io import read_response_bounded


def clamp_timeout(timeout: int) -> int:
    return min(timeout, MAX_TIMEOUT)


def build_timeout(total: int) -> aiohttp.ClientTimeout:
    return aiohttp.ClientTimeout(total=total, connect=CONNECT_TIMEOUT, sock_read=total)


async def execute_formatted_request(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    timeout: int,
    verify_ssl: bool,
    params: dict[str, str] | None = None,
    data: Any = None,
    follow_redirects: bool = True,
    include_content_length: bool = False,
    include_headers: bool = False,
    include_request_body: bool = False,
) -> str:
    timeout = clamp_timeout(timeout)

    request_kwargs: dict[str, Any] = {
        "headers": headers,
        "timeout": build_timeout(timeout),
        "ssl": verify_ssl,
    }
    if params is not None:
        request_kwargs["params"] = params
    if data is not None:
        request_kwargs["data"] = data
    if method == "GET":
        request_kwargs["allow_redirects"] = follow_redirects
        request_kwargs["max_redirects"] = MAX_REDIRECTS if follow_redirects else 0

    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            request = getattr(session, method.lower())
            async with request(url, **request_kwargs) as response:
                content = await read_response_bounded(response)
                response_time = time.time() - start_time
                request_body = data if include_request_body else None
                return format_http_response(
                    method=method,
                    url=url,
                    status=response.status,
                    response_time=response_time,
                    content=content,
                    response_headers=redact_headers(dict(response.headers)),
                    request_data=request_body,
                    include_content_length=include_content_length,
                    include_headers=include_headers,
                )
    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as exc:
        return f"HTTP {method} error: {exc}"


async def execute_head(url: str, headers: dict[str, str], timeout: int, verify_ssl: bool) -> str:
    timeout = clamp_timeout(timeout)
    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.head(
                url,
                headers=headers,
                timeout=build_timeout(timeout),
                ssl=verify_ssl,
            ) as response:
                response_time = time.time() - start_time
                return format_head_response(
                    url=url,
                    status=response.status,
                    response_time=response_time,
                    response_headers=redact_headers(dict(response.headers)),
                )
    except asyncio.TimeoutError:
        return f"Error: Request timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as exc:
        return f"HTTP HEAD error: {exc}"


async def execute_connectivity_test(url: str, timeout: int) -> str:
    timeout = min(timeout, 60)
    try:
        start_time = time.time()
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.head(
                url,
                timeout=build_timeout(timeout),
                ssl=True,
            ) as response:
                response_time = time.time() - start_time
                return format_connectivity_response(
                    url=url,
                    status=response.status,
                    response_time=response_time,
                    server=response.headers.get("Server", "Unknown"),
                )
    except asyncio.TimeoutError:
        return f"Connection test timed out after {timeout}s"
    except (aiohttp.ClientError, ValueError) as exc:
        return f"Connection test failed: {exc}"
