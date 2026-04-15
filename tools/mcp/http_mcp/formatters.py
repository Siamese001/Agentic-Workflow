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
) -> str:
    lines: list[str] = [f"{method} {url}", f"Status: {status}", f"Response time: {response_time:.2f}s"]

    if include_content_length:
        lines.append(f"Content length: {len(content)} bytes")

    lines.append("")

    if request_data:
        lines.append(f"Request body: {str(request_data)[:500]}")
        lines.append("")

    if include_headers and response_headers is not None:
        lines.append("Response headers:")
        for key, value in response_headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")

    if content:
        lines.append(f"Response body:\n{content}")

    return "\n".join(lines)


def format_head_response(
    url: str, status: int, response_time: float, response_headers: dict[str, str]
) -> str:
    lines = [
        f"HEAD {url}",
        f"Status: {status}",
        f"Response time: {response_time:.2f}s",
        "",
        "Response headers:",
    ]
    for key, value in response_headers.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def format_connectivity_response(url: str, status: int, response_time: float, server: str) -> str:
    result = [
        f"Connectivity test for: {url}",
        f"Status: {status}",
        f"Response time: {response_time:.2f}s",
        f"Server: {server}",
    ]
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
            result_text += f"\u274c Request {i}: ERROR\n  Error: {res}\n"
        elif "error" in res:
            result_text += f"\u274c Request {i}: {res['method']} {res['url']}\n  Error: {res['error']}\n"
        else:
            result_text += f"\u2705 Request {i}: {res['method']} {res['url']}\n"
            result_text += f"  Status: {res['status']}\n"
            result_text += f"  Content: {res['content_length']} bytes\n"
        result_text += "\n"
    return result_text
