"""Redact credential-bearing fields before persisting runtime proof artifacts (apps_rg-only)."""

from __future__ import annotations

import copy
import re
from typing import Any
from urllib.parse import urlparse, urlunparse

# Dict keys (case-insensitive) dropped or replaced when serializing request-shaped blobs.
_SENSITIVE_KEY_FRAGMENTS: frozenset[str] = frozenset(
    {
        "api_key",
        "access_token",
        "authorization",
        "client_secret",
        "refresh_token",
        "password",
        "secret",
    }
)

_EXACT_SENSITIVE_KEYS: frozenset[str] = frozenset({"auth", "token", "key"})

_BEARING_RE = re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*")


def redact_http_url_for_artifact(url: str) -> str:
    """Strip URL query and fragment — common location for signed tokens / API keys."""
    raw = str(url or "").strip()
    if not raw:
        return raw
    parsed = urlparse(raw)
    if not parsed.query and not parsed.fragment:
        return raw
    return urlunparse(parsed._replace(query="", fragment=""))


def _key_is_sensitive(key: str) -> bool:
    k = str(key or "").strip().lower()
    if not k:
        return False
    if k in _EXACT_SENSITIVE_KEYS:
        return True
    return any(frag in k for frag in _SENSITIVE_KEY_FRAGMENTS)


def redact_sensitive_mapping(obj: Any) -> Any:
    """Deep-copy and redact secrets from dict/list/str structures."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            ks = str(k)
            if _key_is_sensitive(ks):
                out[ks] = "[REDACTED]"
                continue
            lv = redact_sensitive_mapping(v)
            if ks.lower() == "provider_url" and isinstance(lv, str):
                lv = redact_http_url_for_artifact(lv)
            out[ks] = lv
        return out
    if isinstance(obj, list):
        return [redact_sensitive_mapping(x) for x in obj]
    if isinstance(obj, str):
        return _BEARING_RE.sub("Bearer [REDACTED]", obj)
    return copy.deepcopy(obj)


__all__ = [
    "redact_http_url_for_artifact",
    "redact_sensitive_mapping",
]
