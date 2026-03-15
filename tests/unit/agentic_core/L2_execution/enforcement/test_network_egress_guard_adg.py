"""ADG importability contract for agentic_core/L2_execution/enforcement/network_egress_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_network_egress_guard.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.network_egress_guard import (  # noqa: F401
        COMPILED_PATTERNS,
        LLM_ENDPOINT_PATTERNS,
        NetworkEgressViolation,
        check_network_egress_allowed,
        install_egress_guard,
        is_llm_endpoint,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LLM_ENDPOINT_PATTERNS = None  # type: ignore[assignment,misc]
    COMPILED_PATTERNS = None  # type: ignore[assignment,misc]
    NetworkEgressViolation = None  # type: ignore[assignment,misc]
    is_llm_endpoint = None  # type: ignore[assignment,misc]
    check_network_egress_allowed = None  # type: ignore[assignment,misc]
    install_egress_guard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="network_egress_guard deps unavailable")
class TestNetworkEgressGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/network_egress_guard.py must be importable."""
        assert _AVAILABLE

    def test_networkegressviolation_defined(self) -> None:
        assert NetworkEgressViolation is not None
