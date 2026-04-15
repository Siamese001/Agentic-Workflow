"""Header preparation and redaction helpers."""

from __future__ import annotations

import json
from typing import Any

from tools.mcp.http_mcp.constants import DEFAULT_USER_AGENT, SENSITIVE_HEADERS


def prepare_auth(auth_config: dict[str, Any]) -> tuple | None:
    """Prepare authentication."""
    if not auth_config:
        return None

    auth_type = auth_config.get("type", "").lower()

    if auth_type == "basic":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if username and password:
            return (username, password)

    return None


def prepare_headers(headers: dict[str, Any], auth_config: dict[str, Any]) -> dict[str, str]:
    """Prepare headers including auth."""
    prepared_headers: dict[str, str] = {}

    if headers:
        for key, value in headers.items():
            prepared_headers[str(key)] = str(value)

    if auth_config and auth_config.get("type", "").lower() == "bearer":
        token = auth_config.get("token")
        if token:
            prepared_headers["Authorization"] = f"Bearer {token}"

    if "User-Agent" not in prepared_headers:
        prepared_headers["User-Agent"] = DEFAULT_USER_AGENT

    return prepared_headers


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive headers from response logging."""
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def prepare_request_data(data: Any, json_mode: bool, headers: dict[str, str]) -> Any:
    """Prepare request body for POST/PUT, setting Content-Type when needed."""
    if data is None:
        return None
    if json_mode and isinstance(data, (dict, list)):
        headers["Content-Type"] = "application/json"
        return json.dumps(data)
    if isinstance(data, dict):
        return data
    return str(data)
