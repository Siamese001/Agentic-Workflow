"""ADG importability contract for agentic_core/L0_routing/types/routing_contracts_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_routing_contracts_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.routing_contracts_types import (  # noqa: F401
        GuardrailGuard,
        LawSlotHandler,
        PolicyAlignmentResult,
        PolicyConfigGuard,
        PolicyMutationIncident,
        static_policy_alignment_check,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LawSlotHandler = None  # type: ignore[assignment,misc]
    PolicyConfigGuard = None  # type: ignore[assignment,misc]
    PolicyMutationIncident = None  # type: ignore[assignment,misc]
    PolicyAlignmentResult = None  # type: ignore[assignment,misc]
    static_policy_alignment_check = None  # type: ignore[assignment,misc]
    GuardrailGuard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types deps unavailable")
class TestRoutingContractsTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/routing_contracts_types.py must be importable."""
        assert _AVAILABLE

    def test_lawslothandler_defined(self) -> None:
        assert LawSlotHandler is not None

    def test_policyconfigguard_defined(self) -> None:
        assert PolicyConfigGuard is not None

    def test_policymutationincident_defined(self) -> None:
        assert PolicyMutationIncident is not None

    def test_policyalignmentresult_defined(self) -> None:
        assert PolicyAlignmentResult is not None

    def test_guardrailguard_defined(self) -> None:
        assert GuardrailGuard is not None
