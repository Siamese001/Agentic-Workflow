"""Bounded response reading to prevent memory exhaustion."""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp

from tools.mcp.http_mcp.constants import MAX_RESPONSE_SIZE, TEXTUAL_CONTENT_TYPES


@dataclass(slots=True)
class ResponseReadResult:
    content: str
    total_read: int
    truncated: bool


def _is_textual_content_type(content_type: str) -> bool:
    normalized = (content_type or "").split(";", 1)[0].strip().lower()
    return normalized.startswith("text/") or normalized in TEXTUAL_CONTENT_TYPES


async def read_response_bounded(response: aiohttp.ClientResponse) -> ResponseReadResult:
    """Read response body with a size limit to prevent memory exhaustion."""
    chunks: list[bytes] = []
    total_read = 0
    truncated = False
    chunk_size = 65536  # 64KB

    async for chunk in response.content.iter_chunked(chunk_size):
        next_total = total_read + len(chunk)
        if next_total > MAX_RESPONSE_SIZE:
            allowed = MAX_RESPONSE_SIZE - total_read
            if allowed > 0:
                chunks.append(chunk[:allowed])
                total_read += allowed
            truncated = True
            break
        chunks.append(chunk)
        total_read = next_total

    raw = b"".join(chunks)
    charset = response.charset or "utf-8"
    if _is_textual_content_type(response.headers.get("Content-Type", "")):
        text = raw.decode(charset, errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")

    if truncated:
        text += "\n... (content truncated)"

    return ResponseReadResult(content=text, total_read=total_read, truncated=truncated)
