"""Constants for the enhanced HTTP MCP server."""

from __future__ import annotations

import os

DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MAX_RESPONSE_SIZE = 1_000_000  # 1MB
MAX_REDIRECTS = 5
MAX_BATCH_REQUESTS = 20
MAX_BATCH_CONCURRENCY = 5
CONNECT_TIMEOUT = 20
DEFAULT_USER_AGENT = "Enhanced-HTTP-MCP/1.1"
DEFAULT_RETRY_ATTEMPTS = 3
MAX_RETRY_ATTEMPTS = 5
RETRY_BASE_DELAY_SECONDS = 1.0
MAX_RETRY_DELAY_SECONDS = 8.0
RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
TEXTUAL_CONTENT_TYPES = {
    "application/json",
    "application/javascript",
    "application/problem+json",
    "application/xml",
    "application/x-ndjson",
    "application/x-www-form-urlencoded",
    "application/yaml",
    "application/x-yaml",
    "application/vnd.github.raw",
}
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTNAMES = {
    "localhost",
    "internal",
    "intranet",
    "corp",
    "private",
}
BLOCKED_HOSTNAME_SUFFIXES = (
    ".internal",
    ".intranet",
    ".corp",
    ".local",
    ".lan",
    ".home",
)
SENSITIVE_HEADERS = {
    "set-cookie",
    "authorization",
    "proxy-authorization",
    "www-authenticate",
    "x-api-key",
    "api-key",
}
SENSITIVE_BODY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "client_secret",
    "password",
    "proxy_password",
    "refresh_token",
    "secret",
    "token",
}


def env_truthy(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_TRUST_ENV = env_truthy("HTTP_MCP_TRUST_ENV", True)
