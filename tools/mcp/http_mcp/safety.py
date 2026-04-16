"""URL safety validation for the enhanced HTTP MCP server."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from tools.mcp.http_mcp.constants import ALLOWED_SCHEMES, BLOCKED_HOSTNAMES, BLOCKED_HOSTNAME_SUFFIXES


def validate_url(url: str) -> bool:
    """Validate URL for safety by blocking unsafe schemes and obvious private targets."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        normalized = hostname.lower().strip(".")
        if normalized in BLOCKED_HOSTNAMES:
            return False
        if any(normalized.endswith(suffix) for suffix in BLOCKED_HOSTNAME_SUFFIXES):
            return False

        try:
            ip = ipaddress.ip_address(normalized)
        except ValueError:
            return True

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
        if ip.version == 4 and ip == ipaddress.IPv4Address("169.254.169.254"):
            return False
        return True
    except (ValueError, AttributeError):
        return False
