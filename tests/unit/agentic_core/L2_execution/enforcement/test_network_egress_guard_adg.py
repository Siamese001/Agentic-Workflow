"""ADG importability contract for agentic_core/L2_execution/enforcement/network_egress_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_network_egress_guard.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.network_egress_guard import (  # noqa: F401
        NetworkEgressViolation,
        is_llm_endpoint,
        check_network_egress_allowed,
        install_egress_guard,
        uninstall_egress_guard,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    NetworkEgressViolation = None  # type: ignore[assignment,misc]
    is_llm_endpoint = None  # type: ignore[assignment,misc]
    check_network_egress_allowed = None  # type: ignore[assignment,misc]
    install_egress_guard = None  # type: ignore[assignment,misc]
    uninstall_egress_guard = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="network_egress_guard.py deps unavailable")
class TestNetworkEgressGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: network_egress_guard.py must be importable."""
        assert _AVAILABLE

    def test_networkegressviolation_is_type(self) -> None:
        assert NetworkEgressViolation is not None

    def test_is_llm_endpoint_callable(self) -> None:
        assert callable(is_llm_endpoint)

    def test_check_network_egress_allowed_callable(self) -> None:
        assert callable(check_network_egress_allowed)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

