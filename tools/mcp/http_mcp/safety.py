"""URL safety validation for the enhanced HTTP MCP server."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from tools.mcp.http_mcp.constants import ALLOWED_SCHEMES, BLOCKED_HOSTNAMES


def validate_url(url: str) -> bool:
    """Validate URL for safety - blocks private IPs, metadata endpoints, and unsafe hostnames."""
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname.lower() in BLOCKED_HOSTNAMES:
            return False

        try:
            ip = ipaddress.ip_address(hostname)

            if ip.version == 4:
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
                if ip == ipaddress.IPv4Address("169.254.169.254"):
                    return False

            if ip.version == 6:
                if ip.is_loopback or ip.is_link_local:
                    return False
        except ValueError:
            pass

        return True
    except (ValueError, AttributeError):
        return False
