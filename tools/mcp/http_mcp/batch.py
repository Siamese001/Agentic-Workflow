"""Batch HTTP request execution."""

from __future__ import annotations

import asyncio
from typing import Any

from tools.mcp.http_mcp.client import execute_request_structured
from tools.mcp.http_mcp.constants import (
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT,
    MAX_BATCH_CONCURRENCY,
    MAX_BATCH_REQUESTS,
)
from tools.mcp.http_mcp.formatters import format_batch_results
from tools.mcp.http_mcp.headers import prepare_auth, prepare_headers, prepare_request_data
from tools.mcp.http_mcp.safety import validate_url


async def execute_batch_requests(
    requests: list[dict[str, Any]],
    max_concurrent: int = 3,
    *,
    trust_env: bool | None = None,
) -> str:
    max_concurrent = min(max(1, int(max_concurrent)), MAX_BATCH_CONCURRENCY)

    if len(requests) > MAX_BATCH_REQUESTS:
        raise ValueError(f"Too many requests (max {MAX_BATCH_REQUESTS})")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _bounded(req: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            method = str(req["method"]).upper()
            url = str(req["url"])

            if not validate_url(url):
                return {"method": method, "url": url, "error": "Invalid or unsafe URL", "attempts": 1}

            auth = req.get("auth", {}) or {}
            headers = prepare_headers(req.get("headers", {}) or {}, auth)
            req_auth = prepare_auth(auth)
            body = prepare_request_data(req.get("data"), bool(req.get("json", False)), headers)

            try:
                result = await execute_request_structured(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=int(req.get("timeout", DEFAULT_TIMEOUT)),
                    verify_ssl=bool(req.get("verify_ssl", True)),
                    params=req.get("params"),
                    data=body,
                    auth=req_auth,
                    follow_redirects=bool(req.get("follow_redirects", True)),
                    retries=int(req.get("retries", DEFAULT_RETRY_ATTEMPTS)),
                    trust_env=trust_env if trust_env is not None else req.get("trust_env"),
                )
                return {
                    "method": method,
                    "url": url,
                    "status": result.status,
                    "content_length": len(result.body),
                    "attempts": result.attempts,
                    "truncated": result.truncated,
                }
            except RuntimeError as exc:
                return {
                    "method": method,
                    "url": url,
                    "error": str(exc),
                    "attempts": int(req.get("retries", DEFAULT_RETRY_ATTEMPTS)),
                }

    results = await asyncio.gather(*[_bounded(req) for req in requests], return_exceptions=True)
    return format_batch_results(requests, max_concurrent, results)
