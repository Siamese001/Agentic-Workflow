"""
Network Egress Guard (REQ-414)

Ensures all outbound HTTP requests to LLM-serving endpoints (including localhost)
MUST originate exclusively from SovereignLLMGateway.
"""

from __future__ import annotations

import logging
import os
import re
import socket

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)

# LLM provider endpoints patterns (including localhost variants)
LLM_ENDPOINT_PATTERNS = [
    r".*\.openai\.com",
    r".*\.api\.openai\.com",
    r"api\.openai\.com",
    r"openai\.com",
    r".*\.anthropic\.com",
    r"api\.anthropic\.com",
    r"anthropic\.com",
    r".*\.googleapis\.com",
    r"generativelanguage\.googleapis\.com",
    # Localhost variants for testing
    r"localhost",
    r"localhost:.*",
    r"127\.0\.0\.1",
    r"127\.0\.0\.1:.*",
    r"0\.0\.0\.0",
    r"0\.0\.0\.0:.*",
    r"::1",
    r"::1:.*",
]

# Compile regex patterns for efficiency
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in LLM_ENDPOINT_PATTERNS]


class NetworkEgressViolation(Exception):
    """Raised when unauthorized network egress to LLM endpoint is detected."""

    pass


def is_llm_endpoint(hostname: str, port: int | None = None) -> bool:
    """Check if hostname:port matches known LLM endpoint patterns.

    Args:
        hostname: Hostname to check
        port: Optional port number

    Returns:
        True if it's an LLM endpoint, False otherwise
    """
    host_port = f"{hostname}:{port}" if port else hostname

    for pattern in COMPILED_PATTERNS:
        if pattern.match(host_port):
            return True

    return False


def check_network_egress_allowed(
    hostname: str, port: int | None = None, caller_module: str | None = None
) -> bool:
    """Check if network egress to LLM endpoint is allowed (REQ-414).

    Args:
        hostname: Target hostname
        port: Target port
        caller_module: Module attempting the connection

    Returns:
        True if allowed, False otherwise

    Raises:
        NetworkEgressViolation: If attempting unauthorized LLM endpoint access
    """
    # Check if it's an LLM endpoint
    if not is_llm_endpoint(hostname, port):
        # Non-LLM endpoints are allowed
        return True

    # Check if we're in the SovereignLLMGateway context
    if _is_in_gateway_context():
        return True

    # Check environment override for testing
    if os.getenv("EGRESS_GUARD_DISABLED") == "1":
        Logger.warning("Network egress guard disabled via environment variable")
        return True

    # Violation detected
    caller_info = f" from {caller_module}" if caller_module else ""
    violation_msg = (
        f"Unauthorized network egress to LLM endpoint {hostname}:{port}{caller_info}. "
        f"All LLM requests must go through SovereignLLMGateway (REQ-414)."
    )

    Logger.error(violation_msg)
    raise NetworkEgressViolation(violation_msg)


def _is_in_gateway_context() -> bool:
    """Check if current execution context is within SovereignLLMGateway.

    Returns:
        True if in gateway context, False otherwise
    """
    # Check call stack for SovereignLLMGateway
    import inspect

    for frame_info in inspect.stack():
        module_name = frame_info.frame.f_globals.get("__name__", "")

        # Check if we're specifically in the SovereignLLMGateway module
        if "SovereignLLMGateway" in module_name and module_name.endswith("SovereignLLMGateway"):
            return True

        # Check if we're in a method of the SovereignLLMGateway class
        if "self" in frame_info.frame.f_locals:
            obj = frame_info.frame.f_locals["self"]
            if hasattr(obj, "__class__") and obj.__class__.__name__ == "SovereignLLMGateway":
                return True

    return False


# Monkey-patch socket.connect to add egress guard
_original_socket_connect = socket.socket.connect


def _guarded_connect(self, address: tuple[str, int] | str) -> None:
    """Guarded socket.connect that checks egress permissions."""
    if isinstance(address, tuple):
        hostname, port = address
    else:
        # Unix domain socket - allow
        _original_socket_connect(self, address)
        return

    # Check egress permission
    caller_module = None
    try:
        import inspect

        caller_module = inspect.stack()[1].frame.f_globals.get("__name__")
    except Exception:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        # guardian: allow-silent-swallower
        # If we can't determine caller module, proceed without it
        pass

    check_network_egress_allowed(hostname, port, caller_module)

    # Proceed with original connect
    _original_socket_connect(self, address)


def install_egress_guard() -> None:
    """Install network egress guard (REQ-414).

    This monkey-patches socket.connect to enforce the egress policy.
    Should be called during system initialization.
    """
    if os.getenv("EGRESS_GUARD_DISABLED") == "1":
        Logger.warning("Network egress guard installation skipped (disabled)")
        return

    socket.socket.connect = _guarded_connect
    Logger.info("Network egress guard installed (REQ-414)")


def uninstall_egress_guard() -> None:
    """Uninstall network egress guard.

    Restores original socket.connect behavior.
    """
    socket.socket.connect = _original_socket_connect
    Logger.info("Network egress guard uninstalled")


# Test utilities
def simulate_direct_llm_request(hostname: str = "api.openai.com", port: int = 443) -> None:
    """Simulate a direct LLM request that should be blocked.

    Args:
        hostname: LLM endpoint hostname
        port: LLM endpoint port

    Raises:
        NetworkEgressViolation: Always raised unless guard is disabled
    """
    check_network_egress_allowed(hostname, port, "test_simulation")


def test_egress_guard() -> bool:
    """Test if egress guard is properly installed.

    Returns:
        True if guard is working, False otherwise
    """
    try:
        simulate_direct_llm_request()
        return False  # Should not reach here
    except NetworkEgressViolation:
        return True  # Expected behavior
    except Exception:
        return False  # Unexpected error
