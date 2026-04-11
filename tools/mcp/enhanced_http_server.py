#!/usr/bin/env python3
"""
Enhanced HTTP MCP Server - Advanced HTTP client with auth, retries, and async support
Provides comprehensive HTTP capabilities for Windsurf with enterprise features
"""

import asyncio
import ipaddress
import json
import logging
import sys
import time
from typing import Any
from urllib.parse import urlparse

import anyio
from tqdm import tqdm

# HTTP libraries
try:
    import aiohttp
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("HTTP libraries not found. Install with: pip install aiohttp requests", file=sys.stderr)
    sys.exit(1)

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.lowlevel.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolResult,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging - use stderr to avoid interfering with MCP protocol on stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MAX_RESPONSE_SIZE = 1000000  # 1MB
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTNAMES = {
    "localhost",
    "internal",
    "intranet",
    "corp",
    "private",
}


class EnhancedHTTPMCPServer:
    def __init__(self):
        self.server = Server("http")
        self.session = None
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available HTTP tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="http_get",
                        description="Perform HTTP GET request with advanced options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to fetch",
                                },
                                "headers": {
                                    "type": "object",
                                    "description": "HTTP headers",
                                    "additionalProperties": {"type": "string"},
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Query parameters",
                                    "additionalProperties": {"type": "string"},
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds (max 300)",
                                    "default": 30,
                                    "maximum": 300,
                                },
                                "follow_redirects": {
                                    "type": "boolean",
                                    "description": "Follow redirects",
                                    "default": True,
                                },
                                "verify_ssl": {
                                    "type": "boolean",
                                    "description": "Verify SSL certificates",
                                    "default": True,
                                },
                                "auth": {
                                    "type": "object",
                                    "description": "Authentication (basic or bearer)",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["basic", "bearer"]},
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                        "token": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="http_post",
                        description="Perform HTTP POST request with body support",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to post to",
                                },
                                "headers": {
                                    "type": "object",
                                    "description": "HTTP headers",
                                    "additionalProperties": {"type": "string"},
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Query parameters",
                                    "additionalProperties": {"type": "string"},
                                },
                                "data": {
                                    "description": "Request body (string, object, or form data)",
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "object"},
                                        {"type": "array", "items": {}},
                                    ],
                                },
                                "json": {
                                    "type": "boolean",
                                    "description": "Send data as JSON",
                                    "default": False,
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds (max 300)",
                                    "default": 30,
                                    "maximum": 300,
                                },
                                "verify_ssl": {
                                    "type": "boolean",
                                    "description": "Verify SSL certificates",
                                    "default": True,
                                },
                                "auth": {
                                    "type": "object",
                                    "description": "Authentication (basic or bearer)",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["basic", "bearer"]},
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                        "token": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="http_put",
                        description="Perform HTTP PUT request",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to PUT to",
                                },
                                "headers": {
                                    "type": "object",
                                    "description": "HTTP headers",
                                    "additionalProperties": {"type": "string"},
                                },
                                "data": {
                                    "description": "Request body",
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "object"},
                                        {"type": "array", "items": {}},
                                    ],
                                },
                                "json": {
                                    "type": "boolean",
                                    "description": "Send data as JSON",
                                    "default": False,
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds",
                                    "default": 30,
                                    "maximum": 300,
                                },
                                "verify_ssl": {
                                    "type": "boolean",
                                    "description": "Verify SSL certificates",
                                    "default": True,
                                },
                                "auth": {
                                    "type": "object",
                                    "description": "Authentication",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["basic", "bearer"]},
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                        "token": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="http_delete",
                        description="Perform HTTP DELETE request",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to DELETE",
                                },
                                "headers": {
                                    "type": "object",
                                    "description": "HTTP headers",
                                    "additionalProperties": {"type": "string"},
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds",
                                    "default": 30,
                                    "maximum": 300,
                                },
                                "verify_ssl": {
                                    "type": "boolean",
                                    "description": "Verify SSL certificates",
                                    "default": True,
                                },
                                "auth": {
                                    "type": "object",
                                    "description": "Authentication",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["basic", "bearer"]},
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                        "token": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="http_head",
                        description="Perform HTTP HEAD request (headers only)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to HEAD",
                                },
                                "headers": {
                                    "type": "object",
                                    "description": "HTTP headers",
                                    "additionalProperties": {"type": "string"},
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds",
                                    "default": 30,
                                    "maximum": 300,
                                },
                                "verify_ssl": {
                                    "type": "boolean",
                                    "description": "Verify SSL certificates",
                                    "default": True,
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="test_connectivity",
                        description="Test HTTP connectivity to a URL",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to test connectivity",
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds",
                                    "default": 10,
                                    "maximum": 60,
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    Tool(
                        name="batch_requests",
                        description="Execute multiple HTTP requests in parallel",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "requests": {
                                    "type": "array",
                                    "description": "Array of HTTP requests",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "method": {
                                                "type": "string",
                                                "enum": ["GET", "POST", "PUT", "DELETE", "HEAD"],
                                            },
                                            "url": {"type": "string"},
                                            "headers": {"type": "object"},
                                            "data": {},
                                            "timeout": {"type": "integer", "maximum": 300},
                                            "verify_ssl": {"type": "boolean", "default": True},
                                        },
                                        "required": ["method", "url"],
                                    },
                                },
                                "max_concurrent": {
                                    "type": "integer",
                                    "description": "Maximum concurrent requests",
                                    "default": 5,
                                    "maximum": 10,
                                },
                            },
                            "required": ["requests"],
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "http_get":
                    return await self._http_get(arguments)
                elif name == "http_post":
                    return await self._http_post(arguments)
                elif name == "http_put":
                    return await self._http_put(arguments)
                elif name == "http_delete":
                    return await self._http_delete(arguments)
                elif name == "http_head":
                    return await self._http_head(arguments)
                elif name == "test_connectivity":
                    return await self._test_connectivity(arguments)
                elif name == "batch_requests":
                    return await self._batch_requests(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    def _validate_url(self, url: str) -> bool:
        """Validate URL for safety - blocks private IPs, metadata endpoints, and unsafe hostnames"""
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ALLOWED_SCHEMES:
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Check for blocked hostnames (exact match only)
            if hostname.lower() in BLOCKED_HOSTNAMES:
                return False

            # Check IP addresses for private ranges
            try:
                ip = ipaddress.ip_address(hostname)

                # Block IPv4 private ranges
                if ip.version == 4:
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return False
                    # Block cloud metadata endpoint
                    if ip == ipaddress.IPv4Address("169.254.169.254"):
                        return False

                # Block IPv6 loopback and link-local
                if ip.version == 6:
                    if ip.is_loopback or ip.is_link_local:
                        return False
            except ValueError:
                # Not an IP address, hostname already checked above
                pass

            return True
        except (ValueError, AttributeError):
            return False

    def _prepare_auth(self, auth_config: dict[str, Any]) -> tuple | None:
        """Prepare authentication"""
        if not auth_config:
            return None

        auth_type = auth_config.get("type", "").lower()

        if auth_type == "basic":
            username = auth_config.get("username")
            password = auth_config.get("password")
            if username and password:
                return (username, password)

        return None

    def _prepare_headers(self, headers: dict[str, Any], auth_config: dict[str, Any]) -> dict[str, str]:
        """Prepare headers including auth"""
        prepared_headers = {}

        # Add custom headers
        if headers:
            for key, value in headers.items():
                prepared_headers[str(key)] = str(value)

        # Add bearer token
        if auth_config and auth_config.get("type", "").lower() == "bearer":
            token = auth_config.get("token")
            if token:
                prepared_headers["Authorization"] = f"Bearer {token}"

        # Set user agent
        if "User-Agent" not in prepared_headers:
            prepared_headers["User-Agent"] = "Enhanced-HTTP-MCP/1.0"

        return prepared_headers

    def _redact_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Redact sensitive headers from response logging"""
        sensitive_headers = {
            "set-cookie",
            "authorization",
            "proxy-authorization",
            "www-authenticate",
        }
        redacted = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = value
        return redacted

    async def _read_response_bounded(self, response) -> str:
        """Read response body with size limit to prevent memory exhaustion"""
        content = []
        total_read = 0
        chunk_size = 65536  # 64KB chunks

        async for chunk in response.content.iter_chunked(chunk_size):
            total_read += len(chunk)
            if total_read > MAX_RESPONSE_SIZE:
                # Truncate to exactly MAX_RESPONSE_SIZE
                excess = total_read - MAX_RESPONSE_SIZE
                content.append(chunk[: len(chunk) - excess].decode("utf-8", errors="replace"))
                break
            content.append(chunk.decode("utf-8", errors="replace"))

        result = "".join(content)
        if total_read > MAX_RESPONSE_SIZE:
            result = result[:MAX_RESPONSE_SIZE] + "\n... (content truncated)"

        return result

    async def _http_get(self, args: dict[str, Any]) -> CallToolResult:
        """Perform HTTP GET request"""
        url = args["url"]

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        headers = self._prepare_headers(args.get("headers", {}), args.get("auth", {}))
        params = args.get("params", {})
        timeout = min(args.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = args.get("verify_ssl", True)
        follow_redirects = args.get("follow_redirects", True)

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=verify_ssl,
                    allow_redirects=follow_redirects,
                    max_redirects=MAX_REDIRECTS if follow_redirects else 0,
                ) as response:
                    content = await self._read_response_bounded(response)
                    response_time = time.time() - start_time

                    result = f"GET {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n"
                    result += f"Content length: {len(content)} bytes\n\n"

                    # Add headers with redaction
                    result += "Response headers:\n"
                    redacted_headers = self._redact_headers(dict(response.headers))
                    for key, value in redacted_headers.items():
                        result += f"{key}: {value}\n"
                    result += "\n"

                    # Add content
                    if content:
                        result += f"Response body:\n{content}"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Request timed out after {timeout}s")],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"HTTP GET error: {str(e)}")],
                isError=True,
            )

    async def _http_post(self, args: dict[str, Any]) -> CallToolResult:
        """Perform HTTP POST request"""
        url = args["url"]

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        headers = self._prepare_headers(args.get("headers", {}), args.get("auth", {}))
        data = args.get("data")
        json_mode = args.get("json", False)
        timeout = min(args.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = args.get("verify_ssl", True)

        # Prepare request body
        request_data = None
        if data is not None:
            if json_mode and isinstance(data, (dict, list)):
                request_data = json.dumps(data)
                headers["Content-Type"] = "application/json"
            elif isinstance(data, dict):
                request_data = data
            else:
                request_data = str(data)

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    data=request_data,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=verify_ssl,
                ) as response:
                    content = await self._read_response_bounded(response)
                    response_time = time.time() - start_time

                    result = f"POST {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n"
                    result += f"Content length: {len(content)} bytes\n\n"

                    if request_data:
                        result += f"Request body: {str(request_data)[:500]}\n\n"

                    result += "Response headers:\n"
                    redacted_headers = self._redact_headers(dict(response.headers))
                    for key, value in redacted_headers.items():
                        result += f"{key}: {value}\n"
                    result += "\n"

                    if content:
                        result += f"Response body:\n{content}"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Request timed out after {timeout}s")],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"HTTP POST error: {str(e)}")],
                isError=True,
            )

    async def _http_put(self, args: dict[str, Any]) -> CallToolResult:
        """Perform HTTP PUT request"""
        url = args["url"]

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        headers = self._prepare_headers(args.get("headers", {}), args.get("auth", {}))
        data = args.get("data")
        json_mode = args.get("json", False)
        timeout = min(args.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = args.get("verify_ssl", True)

        request_data = None
        if data is not None:
            if json_mode and isinstance(data, (dict, list)):
                request_data = json.dumps(data)
                headers["Content-Type"] = "application/json"
            elif isinstance(data, dict):
                request_data = data
            else:
                request_data = str(data)

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    headers=headers,
                    data=request_data,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=verify_ssl,
                ) as response:
                    content = await self._read_response_bounded(response)
                    response_time = time.time() - start_time

                    result = f"PUT {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n"

                    if content:
                        result += f"Response body:\n{content}"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Request timed out after {timeout}s")],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"HTTP PUT error: {str(e)}")],
                isError=True,
            )

    async def _http_delete(self, args: dict[str, Any]) -> CallToolResult:
        """Perform HTTP DELETE request"""
        url = args["url"]

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        headers = self._prepare_headers(args.get("headers", {}), args.get("auth", {}))
        timeout = min(args.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = args.get("verify_ssl", True)

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=verify_ssl,
                ) as response:
                    content = await self._read_response_bounded(response)
                    response_time = time.time() - start_time

                    result = f"DELETE {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n"

                    if content:
                        result += f"Response body:\n{content}"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Request timed out after {timeout}s")],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"HTTP DELETE error: {str(e)}")],
                isError=True,
            )

    async def _http_head(self, args: dict[str, Any]) -> CallToolResult:
        """Perform HTTP HEAD request"""
        url = args["url"]

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        headers = self._prepare_headers(args.get("headers", {}), {})
        timeout = min(args.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
        verify_ssl = args.get("verify_ssl", True)

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=verify_ssl,
                ) as response:
                    response_time = time.time() - start_time

                    result = f"HEAD {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n\n"
                    result += "Response headers:\n"

                    redacted_headers = self._redact_headers(dict(response.headers))
                    for key, value in redacted_headers.items():
                        result += f"{key}: {value}\n"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Request timed out after {timeout}s")],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"HTTP HEAD error: {str(e)}")],
                isError=True,
            )

    async def _test_connectivity(self, args: dict[str, Any]) -> CallToolResult:
        """Test HTTP connectivity to a URL"""
        url = args["url"]
        timeout = min(args.get("timeout", 10), 60)

        if not self._validate_url(url):
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid or unsafe URL")],
                isError=True,
            )

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=True,
                ) as response:
                    response_time = time.time() - start_time

                    result = f"Connectivity test for: {url}\n"
                    result += f"Status: {response.status}\n"
                    result += f"Response time: {response_time:.2f}s\n"
                    result += f"Server: {response.headers.get('Server', 'Unknown')}\n"

                    if response.status == 200:
                        result += "Result: ✅ Connection successful"
                    else:
                        result += f"Result: ⚠️ Connection returned status {response.status}"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result)],
                    )

        except asyncio.TimeoutError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Connection test timed out after {timeout}s",
                    )
                ],
                isError=True,
            )
        except (aiohttp.ClientError, ValueError) as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Connection test failed: {str(e)}",
                    )
                ],
                isError=True,
            )

    async def _batch_requests(self, args: dict[str, Any]) -> CallToolResult:
        """Execute multiple HTTP requests in parallel"""
        requests = args["requests"]
        max_concurrent = min(args.get("max_concurrent", 5), 10)

        if len(requests) > 20:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Too many requests (max 20)",
                    )
                ],
                isError=True,
            )

        async def execute_request(req):
            method = req["method"].upper()
            url = req["url"]

            if not self._validate_url(url):
                return {
                    "method": method,
                    "url": url,
                    "error": "Invalid or unsafe URL",
                }

            headers = self._prepare_headers(req.get("headers", {}), req.get("auth", {}))
            timeout = min(req.get("timeout", DEFAULT_TIMEOUT), MAX_TIMEOUT)
            verify_ssl = req.get("verify_ssl", True)

            try:
                async with aiohttp.ClientSession() as session:
                    async with getattr(session, method.lower())(
                        url,
                        headers=headers,
                        data=req.get("data"),
                        timeout=aiohttp.ClientTimeout(total=timeout),
                        ssl=verify_ssl,
                    ) as response:
                        content = await self._read_response_bounded(response)
                        redacted = self._redact_headers(dict(response.headers))

                        return {
                            "method": method,
                            "url": url,
                            "status": response.status,
                            "content_length": len(content),
                            "headers": redacted,
                        }
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
                return {
                    "method": method,
                    "url": url,
                    "error": str(e),
                }

        try:
            # Execute requests with semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)

            async def bounded_execute(req):
                async with semaphore:
                    return await execute_request(req)

            tasks = [bounded_execute(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Format results
            result_text = f"Batch HTTP requests ({len(requests)} total, {max_concurrent} concurrent)\n\n"

            for i, res in tqdm(
                enumerate(results, 1), total=len(results), desc="Formatting results", unit="req", leave=False
            ):
                if isinstance(res, BaseException):
                    result_text += f"Request {i}: ERROR\n"
                    result_text += f"  ❌ Error: {str(res)}\n"
                elif "error" in res:
                    result_text += f"Request {i}: {res['method']} {res['url']}\n"
                    result_text += f"  ❌ Error: {res['error']}\n"
                else:
                    result_text += f"Request {i}: {res['method']} {res['url']}\n"
                    result_text += f"  ✅ Status: {res['status']}\n"
                    result_text += f"  📏 Content: {res['content_length']} bytes\n"

                result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
            )

        except (ValueError, TypeError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Batch request error: {str(e)}")],
                isError=True,
            )


async def main():
    """Main entry point"""
    server_instance = EnhancedHTTPMCPServer()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="http",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Enhanced HTTP MCP Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
