from typing import Any, Optional, Protocol, Dict, List

import functools
import logging
import socket
from typing import List

logger = logging.getLogger("EgressFilter")  # GLOBAL: Review if this should be constant
logging.basicConfig(level=logging.WARNING)

class NetworkViolationError(Exception):
    """Raised when an unauthorized outbound connection is attempted."""

def strict_egress_filter(allowed_domains: List[str]):
    """
    Decorator that patches socket.getaddrinfo to enforce an Allow-List
    on all outbound network connections within the decorated function.
    """

    # Normalize allowed domains (e.g., remove 'www.' and force lowercase)
    normalized_allowed = {d.lower().lstrip('www.') for d in allowed_domains}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            original_getaddrinfo = socket.getaddrinfo

            def patched_getaddrinfo(host, port, family=0, socktype=0, proto=0, flags=0):
                """The function replacing the standard socket lookup."""

                if host is None:
                    # Allow internal/local connections (e.g., to Redis or Docker DNS)
                    return original_getaddrinfo(host, port, family, socktype, proto, flags)

                # 1. Host Normalization
                host_lower = host.lower().lstrip('www.')

                # 2. Enforcement Check
                if host_lower not in normalized_allowed:
                    logger.critical(f"[ALERT] PROTOCOL 8 VIOLATION! Blocked unauthorized egress to: {host}")
                    raise NetworkViolationError(
                        f"Egress Filter Blocked: Outbound connection to '{host}' is not on the Allow-List."
                    )

                # 3. Allow if on the list
                logger.info(f"Egress Filter Allowed: Connection to {host} is authorized.")
                return original_getaddrinfo(host, port, family, socktype, proto, flags)

            # --- Patching and Execution ---
            socket.getaddrinfo = patched_getaddrinfo
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore original function regardless of success or failure
                socket.getaddrinfo = original_getaddrinfo

            return result

        return wrapper
    return decorator

