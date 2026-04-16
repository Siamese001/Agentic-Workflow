"""Header preparation and redaction helpers."""

from __future__ import annotations

import json
from typing import Any

import aiohttp

from tools.mcp.http_mcp.constants import DEFAULT_USER_AGENT, SENSITIVE_BODY_KEYS, SENSITIVE_HEADERS


def prepare_auth(auth_config: dict[str, Any]) -> aiohttp.BasicAuth | None:
    """Prepare aiohttp auth objects for supported auth modes."""
    if not auth_config:
        return None

    auth_type = str(auth_config.get("type", "")).lower().strip()
    if auth_type != "basic":
        return None

    username = auth_config.get("username")
    password = auth_config.get("password")
    if username is None or password is None:
        return None

    return aiohttp.BasicAuth(login=str(username), password=str(password))


def prepare_headers(headers: dict[str, Any], auth_config: dict[str, Any]) -> dict[str, str]:
    """Prepare headers including bearer auth and default user-agent."""
    prepared_headers: dict[str, str] = {}

    if headers:
        for key, value in headers.items():
            prepared_headers[str(key)] = str(value)

    if auth_config and str(auth_config.get("type", "")).lower().strip() == "bearer":
        token = auth_config.get("token")
        if token and "Authorization" not in prepared_headers:
            prepared_headers["Authorization"] = f"Bearer {token}"

    if "User-Agent" not in prepared_headers:
        prepared_headers["User-Agent"] = DEFAULT_USER_AGENT

    return prepared_headers


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive headers from request and response logging."""
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def _redact_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested_value in value.items():
            if str(key).lower() in SENSITIVE_BODY_KEYS:
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = _redact_json_like(nested_value)
        return redacted
    if isinstance(value, list):
        return [_redact_json_like(item) for item in value]
    return value


def summarize_request_data(data: Any, limit: int = 500) -> str | None:
    """Return a compact, redacted preview of a request body for safe logging."""
    if data is None:
        return None

    preview_obj = _redact_json_like(data)
    if isinstance(preview_obj, (dict, list)):
        preview = json.dumps(preview_obj, ensure_ascii=False)
    else:
        preview = str(preview_obj)

    if len(preview) > limit:
        return preview[:limit] + "..."
    return preview


def prepare_request_data(data: Any, json_mode: bool, headers: dict[str, str]) -> Any:
    """Prepare request body and set Content-Type when needed."""
    if data is None:
        return None
    if json_mode:
        headers.setdefault("Content-Type", "application/json")
        return json.dumps(data)
    if isinstance(data, dict):
        return data
    return str(data)
