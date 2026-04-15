"""Bounded response reading to prevent memory exhaustion."""

from __future__ import annotations

import aiohttp

from tools.mcp.http_mcp.constants import MAX_RESPONSE_SIZE


async def read_response_bounded(response: aiohttp.ClientResponse) -> str:
    """Read response body with size limit to prevent memory exhaustion."""
    content: list[str] = []
    total_read = 0
    chunk_size = 65536  # 64KB chunks

    async for chunk in response.content.iter_chunked(chunk_size):
        total_read += len(chunk)
        if total_read > MAX_RESPONSE_SIZE:
            excess = total_read - MAX_RESPONSE_SIZE
            content.append(chunk[: len(chunk) - excess].decode("utf-8", errors="replace"))
            break
        content.append(chunk.decode("utf-8", errors="replace"))

    result = "".join(content)
    if total_read > MAX_RESPONSE_SIZE:
        result = result[:MAX_RESPONSE_SIZE] + "\n... (content truncated)"

    return result
