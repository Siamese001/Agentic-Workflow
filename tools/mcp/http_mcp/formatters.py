"""Response formatting helpers for the enhanced HTTP MCP server."""

from __future__ import annotations

from typing import Any


def format_http_response(
    method: str,
    url: str,
    status: int,
    response_time: float,
    content: str,
    response_headers: dict[str, str] | None = None,
    request_data: Any = None,
    include_content_length: bool = False,
    include_headers: bool = False,
    attempts: int = 1,
    retries_applied: bool = False,
    truncated: bool = False,
) -> str:
    lines: list[str] = [
        f"{method} {url}",
        f"Status: {status}",
        f"Response time: {response_time:.2f}s",
        f"Attempts: {attempts}",
    ]

    if retries_applied:
        lines.append("Retries applied: yes")

    if include_content_length:
        lines.append(f"Content length: {len(content)} bytes")

    if truncated:
        lines.append("Body truncated: yes")

    lines.append("")

    if request_data:
        lines.append(f"Request body: {request_data}")
        lines.append("")

    if include_headers and response_headers is not None:
        lines.append("Response headers:")
        for key, value in response_headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")

    if content:
        lines.append(f"Response body:\n{content}")

    return "\n".join(lines)


def format_error_response(
    method: str,
    url: str,
    message: str,
    *,
    attempts: int,
    response_time: float | None = None,
) -> str:
    lines = [
        f"{method} {url}",
        f"Error: {message}",
        f"Attempts: {attempts}",
    ]
    if response_time is not None:
        lines.append(f"Response time: {response_time:.2f}s")
    return "\n".join(lines)


def format_head_response(
    url: str,
    status: int,
    response_time: float,
    response_headers: dict[str, str],
    *,
    attempts: int = 1,
    retries_applied: bool = False,
) -> str:
    lines = [
        f"HEAD {url}",
        f"Status: {status}",
        f"Response time: {response_time:.2f}s",
        f"Attempts: {attempts}",
    ]
    if retries_applied:
        lines.append("Retries applied: yes")
    lines.extend(["", "Response headers:"])
    for key, value in response_headers.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def format_connectivity_response(
    url: str,
    status: int,
    response_time: float,
    server: str,
    *,
    attempts: int = 1,
    retries_applied: bool = False,
) -> str:
    result = [
        f"Connectivity test for: {url}",
        f"Status: {status}",
        f"Response time: {response_time:.2f}s",
        f"Server: {server}",
        f"Attempts: {attempts}",
    ]
    if retries_applied:
        result.append("Retries applied: yes")
    if status == 200:
        result.append("Result: Connection successful")
    else:
        result.append(f"Result: Connection returned status {status}")
    return "\n".join(result)


def format_batch_results(
    requests: list[dict[str, Any]],
    max_concurrent: int,
    results: list[dict[str, Any] | BaseException],
) -> str:
    result_text = f"Batch HTTP requests ({len(requests)} total, {max_concurrent} concurrent)\n\n"
    for i, res in enumerate(results, 1):
        if isinstance(res, BaseException):
            result_text += f"❌ Request {i}: ERROR\n  Error: {res}\n"
        elif "error" in res:
            result_text += f"❌ Request {i}: {res['method']} {res['url']}\n"
            result_text += f"  Error: {res['error']}\n"
            result_text += f"  Attempts: {res.get('attempts', 1)}\n"
        else:
            result_text += f"✅ Request {i}: {res['method']} {res['url']}\n"
            result_text += f"  Status: {res['status']}\n"
            result_text += f"  Attempts: {res.get('attempts', 1)}\n"
            result_text += f"  Content: {res['content_length']} bytes\n"
            if res.get("truncated"):
                result_text += "  Truncated: yes\n"
        result_text += "\n"
    return result_text
