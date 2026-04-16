"""MCP tool registration for the enhanced HTTP server."""

from __future__ import annotations

from typing import Any

from tools.mcp.http_mcp.batch import execute_batch_requests
from tools.mcp.http_mcp.client import execute_connectivity_test, execute_formatted_request, execute_head
from tools.mcp.http_mcp.constants import DEFAULT_RETRY_ATTEMPTS
from tools.mcp.http_mcp.headers import (
    prepare_auth,
    prepare_headers,
    prepare_request_data,
    summarize_request_data,
)
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
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Perform HTTP GET request with advanced options"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        auth_cfg = auth or {}
        req_headers = prepare_headers(headers or {}, auth_cfg)
        req_auth = prepare_auth(auth_cfg)
        return await execute_formatted_request(
            method="GET",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            params=params,
            auth=req_auth,
            follow_redirects=follow_redirects,
            include_content_length=True,
            include_headers=True,
            retries=retries,
            trust_env=trust_env,
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
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Perform HTTP POST request with body support"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        auth_cfg = auth or {}
        req_headers = prepare_headers(headers or {}, auth_cfg)
        req_auth = prepare_auth(auth_cfg)
        request_data = prepare_request_data(data, json, req_headers)
        return await execute_formatted_request(
            method="POST",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            params=params,
            data=request_data,
            auth=req_auth,
            include_content_length=True,
            include_headers=True,
            include_request_body=True,
            retries=retries,
            trust_env=trust_env,
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
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Perform HTTP PUT request"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        auth_cfg = auth or {}
        req_headers = prepare_headers(headers or {}, auth_cfg)
        req_auth = prepare_auth(auth_cfg)
        request_data = prepare_request_data(data, json, req_headers)
        return await execute_formatted_request(
            method="PUT",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            data=request_data,
            auth=req_auth,
            retries=retries,
            trust_env=trust_env,
        )

    @mcp.tool()
    async def http_delete(
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        auth: dict[str, Any] | None = None,
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Perform HTTP DELETE request"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        auth_cfg = auth or {}
        req_headers = prepare_headers(headers or {}, auth_cfg)
        req_auth = prepare_auth(auth_cfg)
        return await execute_formatted_request(
            method="DELETE",
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            auth=req_auth,
            retries=retries,
            trust_env=trust_env,
        )

    @mcp.tool()
    async def http_head(
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        auth: dict[str, Any] | None = None,
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Perform HTTP HEAD request (headers only)"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        auth_cfg = auth or {}
        req_headers = prepare_headers(headers or {}, auth_cfg)
        return await execute_head(
            url=url,
            headers=req_headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            retries=retries,
            trust_env=trust_env,
        )

    @mcp.tool()
    async def test_connectivity(
        url: str,
        timeout: int = 10,
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        trust_env: bool | None = None,
    ) -> str:
        """Test HTTP connectivity to a URL"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        return await execute_connectivity_test(url=url, timeout=timeout, retries=retries, trust_env=trust_env)

    @mcp.tool()
    async def batch_requests(
        requests: list[dict[str, Any]],
        max_concurrent: int = 5,
        trust_env: bool | None = None,
    ) -> str:
        """Execute multiple HTTP requests in parallel"""
        return await execute_batch_requests(
            requests=requests, max_concurrent=max_concurrent, trust_env=trust_env
        )

    @mcp.tool()
    async def http_auth_preview(
        url: str,
        auth: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> str:
        """Preview what auth headers would be sent for a request (no actual request made)"""
        if not validate_url(url):
            raise ValueError("Invalid or unsafe URL")
        req_headers = prepare_headers(headers or {}, auth)
        req_auth = prepare_auth(auth)
        lines = [
            f"Auth preview for: {url}",
            f"Auth type: {auth.get('type', 'none')}",
            "",
            "Headers that would be sent:",
        ]
        for key, value in req_headers.items():
            lines.append(f"  {key}: {value}")
        if req_auth is not None:
            lines.append(f"Basic auth: login={req_auth.login!r} (password redacted)")
        body_preview = summarize_request_data(auth)
        if body_preview:
            lines.append(f"\nAuth config preview (redacted): {body_preview}")
        return "\n".join(lines)
