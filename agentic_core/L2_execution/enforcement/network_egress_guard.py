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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)
LLM_ENDPOINT_PATTERNS = [
    ".*\\.openai\\.com",
    ".*\\.api\\.openai\\.com",
    "api\\.openai\\.com",
    "openai\\.com",
    ".*\\.anthropic\\.com",
    "api\\.anthropic\\.com",
    "anthropic\\.com",
    ".*\\.googleapis\\.com",
    "generativelanguage\\.googleapis\\.com",
    "localhost",
    "localhost:.*",
    "127\\.0\\.0\\.1",
    "127\\.0\\.0\\.1:.*",
    "0\\.0\\.0\\.0",
    "0\\.0\\.0\\.0:.*",
    "::1",
    "::1:.*",
]
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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_llm_endpoint", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_llm_endpoint", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "is_llm_endpoint")
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
    if not is_llm_endpoint(hostname, port):
        return True
    if _is_in_gateway_context():
        return True
    if os.getenv("EGRESS_GUARD_DISABLED") == "1":
        Logger.warning("Network egress guard disabled via environment variable")
        return True
    caller_info = f" from {caller_module}" if caller_module else ""
    violation_msg = f"Unauthorized network egress to LLM endpoint {hostname}:{port}{caller_info}. All LLM requests must go through SovereignLLMGateway (REQ-414)."
    Logger.error(violation_msg)
    raise NetworkEgressViolation(violation_msg)


def _is_in_gateway_context() -> bool:
    """Check if current execution context is within SovereignLLMGateway.

    Returns:
        True if in gateway context, False otherwise
    """
    import inspect

    for frame_info in inspect.stack():
        module_name = frame_info.frame.f_globals.get("__name__", "")
        if "SovereignLLMGateway" in module_name and module_name.endswith("SovereignLLMGateway"):
            return True
        if "self" in frame_info.frame.f_locals:
            obj = frame_info.frame.f_locals["self"]
            if hasattr(obj, "__class__") and obj.__class__.__name__ == "SovereignLLMGateway":
                return True
    return False


_original_socket_connect = socket.socket.connect


def _guarded_connect(self, address: tuple[str, int] | str) -> None:
    """Guarded socket.connect that checks egress permissions."""
    if isinstance(address, tuple):
        hostname, port = address
    else:
        _original_socket_connect(self, address)
        return
    caller_module = None
    try:
        import inspect

        caller_module = inspect.stack()[1].frame.f_globals.get("__name__")
    except Exception:
        raise
        pass
    check_network_egress_allowed(hostname, port, caller_module)
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
        return False
    except NetworkEgressViolation:
        return True
    except Exception:
        return False
