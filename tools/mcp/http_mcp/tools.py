"""MCP tool registration for the enhanced HTTP server."""

from __future__ import annotations

from typing import Any

from tools.mcp.http_mcp.batch import execute_batch_requests
from tools.mcp.http_mcp.client import execute_connectivity_test, execute_formatted_request, execute_head
from tools.mcp.http_mcp.headers import prepare_headers, prepare_request_data
from tools.mcp.http_mcp.safety import validate_url


def register_http_tools(mcp: Any) -> None:
    """Register all HTTP tools onto the provided MCP server."""

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
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, auth or {})
        return await execute_formatted_request(
            method="GET",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            params=params,
            follow_redirects=follow_redirects,
            include_content_length=True,
            include_headers=True,
        )

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
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, auth or {})
        request_data = prepare_request_data(data, json, req_headers)
        return await execute_formatted_request(
            method="POST",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            params=params,
            data=request_data,
            include_content_length=True,
            include_headers=True,
            include_request_body=True,
        )

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
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, auth or {})
        request_data = prepare_request_data(data, json, req_headers)
        return await execute_formatted_request(
            method="PUT",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            data=request_data,
        )

    @mcp.tool()
    async def http_delete(
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        auth: dict[str, Any] | None = None,
    ) -> str:
        """Perform HTTP DELETE request"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, auth or {})
        return await execute_formatted_request(
            method="DELETE",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

    @mcp.tool()
    async def http_head(
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ) -> str:
        """Perform HTTP HEAD request (headers only)"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, {})
        return await execute_head(url=url, headers=req_headers, timeout=timeout, verify_ssl=verify_ssl)

    @mcp.tool()
    async def test_connectivity(
        url: str,
        timeout: int = 10,
    ) -> str:
        """Test HTTP connectivity to a URL"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        return await execute_connectivity_test(url=url, timeout=timeout)

    @mcp.tool()
    async def batch_requests(
        requests: list[dict[str, Any]],
        max_concurrent: int = 5,
    ) -> str:
        """Execute multiple HTTP requests in parallel"""
        return await execute_batch_requests(requests=requests, max_concurrent=max_concurrent)
