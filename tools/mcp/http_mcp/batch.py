"""Batch HTTP request execution."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from tools.mcp.http_mcp.client import build_timeout
from tools.mcp.http_mcp.constants import (
    DEFAULT_TIMEOUT,
    MAX_BATCH_CONCURRENCY,
    MAX_BATCH_REQUESTS,
    MAX_TIMEOUT,
)
from tools.mcp.http_mcp.formatters import format_batch_results
from tools.mcp.http_mcp.headers import prepare_headers, redact_headers
from tools.mcp.http_mcp.response_io import read_response_bounded
from tools.mcp.http_mcp.safety import validate_url


async def execute_batch_requests(requests: list[dict[str, Any]], max_concurrent: int = 5) -> str:
    max_concurrent = min(max_concurrent, MAX_BATCH_CONCURRENCY)

    if len(requests) > MAX_BATCH_REQUESTS:
        raise ValueError(f"Too many requests (max {MAX_BATCH_REQUESTS})")

    async def _execute_one(req: dict[str, Any]) -> dict[str, Any]:
        method = req["method"].upper()
        url = req["url"]

        if not validate_url(url):
            return {"method": method, "url": url, "error": "Invalid or unsafe URL"}

        req_headers = prepare_headers(req.get("headers", {}), req.get("auth", {}))
        req_timeout = min(req.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = req.get("verify_ssl", True)

        try:
            async with aiohttp.ClientSession(trust_env=False) as session:
                async with getattr(session, method.lower())(
                    url,
                    headers=req_headers,
                    data=req.get("data"),
                    timeout=build_timeout(req_timeout),
                    ssl=verify_ssl,
                ) as response:
                    content = await read_response_bounded(response)
                    return {
                        "method": method,
                        "url": url,
                        "status": response.status,
                        "content_length": len(content),
                        "headers": redact_headers(dict(response.headers)),
                    }
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            return {"method": method, "url": url, "error": str(exc)}

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _bounded(req: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await _execute_one(req)

    tasks = [_bounded(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return format_batch_results(requests, max_concurrent, results)
