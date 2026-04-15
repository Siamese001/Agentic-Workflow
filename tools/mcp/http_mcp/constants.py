"""Constants for the enhanced HTTP MCP server."""

from __future__ import annotations

DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MAX_RESPONSE_SIZE = 1_000_000  # 1MB
MAX_REDIRECTS = 5
MAX_BATCH_REQUESTS = 20
MAX_BATCH_CONCURRENCY = 10
CONNECT_TIMEOUT = 10
DEFAULT_USER_AGENT = "Enhanced-HTTP-MCP/1.0"
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTNAMES = {
    "localhost",
    "internal",
    "intranet",
    "corp",
    "private",
}
SENSITIVE_HEADERS = {
    "set-cookie",
    "authorization",
    "proxy-authorization",
    "www-authenticate",
}
