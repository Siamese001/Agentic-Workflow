"""Core HTTP execution functions."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any

import aiohttp

from tools.mcp.http_mcp.constants import (
    CONNECT_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TRUST_ENV,
    MAX_REDIRECTS,
    MAX_RETRY_ATTEMPTS,
    MAX_RETRY_DELAY_SECONDS,
    MAX_TIMEOUT,
    RETRYABLE_STATUS_CODES,
    RETRY_BASE_DELAY_SECONDS,
)
from tools.mcp.http_mcp.formatters import (
    format_connectivity_response,
    format_error_response,
    format_head_response,
    format_http_response,
)
from tools.mcp.http_mcp.headers import redact_headers, summarize_request_data
from tools.mcp.http_mcp.response_io import ResponseReadResult, read_response_bounded


@dataclass(slots=True)
class RequestExecutionResult:
    method: str
    url: str
    status: int
    response_time: float
    headers: dict[str, str]
    body: str
    attempts: int
    truncated: bool


_SESSION_LOCK = asyncio.Lock()
_SESSION_CACHE: dict[bool, aiohttp.ClientSession] = {}


def clamp_timeout(timeout: int) -> int:
    return min(max(1, int(timeout)), MAX_TIMEOUT)


def clamp_retries(retries: int | None) -> int:
    if retries is None:
        return DEFAULT_RETRY_ATTEMPTS
    return min(max(1, int(retries)), MAX_RETRY_ATTEMPTS)


def normalize_trust_env(trust_env: bool | None) -> bool:
    if trust_env is None:
        return DEFAULT_TRUST_ENV
    return bool(trust_env)


def build_timeout(total: int) -> aiohttp.ClientTimeout:
    total = clamp_timeout(total)
    connect_timeout = min(CONNECT_TIMEOUT, total)
    return aiohttp.ClientTimeout(
        total=total,
        connect=connect_timeout,
        sock_connect=connect_timeout,
        sock_read=total,
    )


async def get_client_session(trust_env: bool) -> aiohttp.ClientSession:
    async with _SESSION_LOCK:
        session = _SESSION_CACHE.get(trust_env)
        if session is not None and not session.closed:
            return session

        session = aiohttp.ClientSession(
            trust_env=trust_env,
            raise_for_status=False,
            auto_decompress=True,
        )
        _SESSION_CACHE[trust_env] = session
        return session


async def close_all_sessions() -> None:
    async with _SESSION_LOCK:
        sessions = list(_SESSION_CACHE.values())
        _SESSION_CACHE.clear()
    for session in sessions:
        if not session.closed:
            await session.close()


def should_retry_status(status: int) -> bool:
    return status in RETRYABLE_STATUS_CODES


def should_retry_exception(exc: BaseException) -> bool:
    return isinstance(
        exc,
        (
            asyncio.TimeoutError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientConnectorError,
            aiohttp.ClientOSError,
            aiohttp.ServerDisconnectedError,
            aiohttp.ServerTimeoutError,
        ),
    )


def _parse_retry_after_seconds(value: str) -> float | None:
    try:
        return max(0.0, float(value.strip()))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        return max(0.0, dt.timestamp() - time.time())


def compute_retry_delay(attempt: int, headers: dict[str, str] | None = None) -> float:
    if headers:
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after:
            parsed = _parse_retry_after_seconds(retry_after)
            if parsed is not None:
                return float(min(parsed, MAX_RETRY_DELAY_SECONDS))

        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        if remaining == "0" and reset:
            try:
                seconds = max(0.0, float(reset) - time.time())
            except ValueError:
                seconds = 0.0
            if seconds > 0:
                return float(min(seconds, MAX_RETRY_DELAY_SECONDS))

    base: float = min(RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)), MAX_RETRY_DELAY_SECONDS)
    jitter = random.uniform(0.0, 0.25)
    return float(min(base + jitter, MAX_RETRY_DELAY_SECONDS))


async def execute_request_structured(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    timeout: int,
    verify_ssl: bool,
    params: dict[str, str] | None = None,
    data: Any = None,
    auth: aiohttp.BasicAuth | None = None,
    follow_redirects: bool = True,
    retries: int | None = None,
    trust_env: bool | None = None,
) -> RequestExecutionResult:
    timeout = clamp_timeout(timeout)
    retries = clamp_retries(retries)
    trust_env = normalize_trust_env(trust_env)

    request_kwargs: dict[str, Any] = {
        "headers": headers,
        "timeout": build_timeout(timeout),
        "ssl": verify_ssl,
        "allow_redirects": follow_redirects,
    }
    if params is not None:
        request_kwargs["params"] = params
    if data is not None:
        request_kwargs["data"] = data
    if auth is not None:
        request_kwargs["auth"] = auth
    if follow_redirects:
        request_kwargs["max_redirects"] = MAX_REDIRECTS

    last_error: BaseException | None = None
    start_time = time.time()

    for attempt in range(1, retries + 1):
        try:
            session = await get_client_session(trust_env)
            request = getattr(session, method.lower())
            async with request(url, **request_kwargs) as response:
                read_result: ResponseReadResult = await read_response_bounded(response)
                headers_out = redact_headers(dict(response.headers))
                if should_retry_status(response.status) and attempt < retries:
                    await asyncio.sleep(compute_retry_delay(attempt, dict(response.headers)))
                    continue
                return RequestExecutionResult(
                    method=method,
                    url=url,
                    status=response.status,
                    response_time=time.time() - start_time,
                    headers=headers_out,
                    body=read_result.content,
                    attempts=attempt,
                    truncated=read_result.truncated,
                )
        except BaseException as exc:  # guardian: allow-broad-exception -- retry loop; filtered by should_retry_exception below, non-retryables re-raised via last_error
            last_error = exc
            if should_retry_exception(exc) and attempt < retries:
                await asyncio.sleep(compute_retry_delay(attempt))
                continue
            break

    response_time = time.time() - start_time
    message = _format_exception_message(last_error, timeout)
    raise RuntimeError(
        format_error_response(method, url, message, attempts=retries, response_time=response_time)
    )


def _format_exception_message(exc: BaseException | None, timeout: int) -> str:
    if exc is None:
        return "Request failed for an unknown reason"
    if isinstance(exc, asyncio.TimeoutError):
        return f"Request timed out after {timeout}s"
    if isinstance(exc, aiohttp.ClientConnectorCertificateError):
        return f"TLS certificate validation failed: {exc}"
    if isinstance(exc, aiohttp.ClientConnectorError):
        return f"Connection failed: {exc}"
    if isinstance(exc, aiohttp.ClientProxyConnectionError):
        return f"Proxy connection failed: {exc}"
    if isinstance(exc, aiohttp.ClientError):
        return f"HTTP client error: {exc}"
    return f"Unhandled error: {type(exc).__name__}: {exc}"


async def execute_formatted_request(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    timeout: int,
    verify_ssl: bool,
    params: dict[str, str] | None = None,
    data: Any = None,
    auth: aiohttp.BasicAuth | None = None,
    follow_redirects: bool = True,
    include_content_length: bool = False,
    include_headers: bool = False,
    include_request_body: bool = False,
    retries: int | None = None,
    trust_env: bool | None = None,
) -> str:
    try:
        result = await execute_request_structured(
            method=method,
            url=url,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            params=params,
            data=data,
            auth=auth,
            follow_redirects=follow_redirects,
            retries=retries,
            trust_env=trust_env,
        )
        request_body = summarize_request_data(data) if include_request_body else None
        return format_http_response(
            method=method,
            url=url,
            status=result.status,
            response_time=result.response_time,
            content=result.body,
            response_headers=result.headers,
            request_data=request_body,
            include_content_length=include_content_length,
            include_headers=include_headers,
            attempts=result.attempts,
            retries_applied=result.attempts > 1,
            truncated=result.truncated,
        )
    except RuntimeError as exc:
        return str(exc)


async def execute_head(
    url: str,
    headers: dict[str, str],
    timeout: int,
    verify_ssl: bool,
    *,
    retries: int | None = None,
    trust_env: bool | None = None,
) -> str:
    try:
        result = await execute_request_structured(
            method="HEAD",
            url=url,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            follow_redirects=True,
            retries=retries,
            trust_env=trust_env,
        )
        return format_head_response(
            url=url,
            status=result.status,
            response_time=result.response_time,
            response_headers=result.headers,
            attempts=result.attempts,
            retries_applied=result.attempts > 1,
        )
    except RuntimeError as exc:
        return str(exc)


async def execute_connectivity_test(
    url: str,
    timeout: int,
    *,
    retries: int | None = None,
    trust_env: bool | None = None,
) -> str:
    try:
        result = await execute_request_structured(
            method="HEAD",
            url=url,
            headers={},
            timeout=min(timeout, 60),
            verify_ssl=True,
            follow_redirects=True,
            retries=retries,
            trust_env=trust_env,
        )
        return format_connectivity_response(
            url=url,
            status=result.status,
            response_time=result.response_time,
            server=result.headers.get("Server", "Unknown"),
            attempts=result.attempts,
            retries_applied=result.attempts > 1,
        )
    except RuntimeError as exc:
        return str(exc)
