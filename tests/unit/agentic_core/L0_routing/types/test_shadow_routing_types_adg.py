"""ADG importability contract for agentic_core/L0_routing/types/shadow_routing_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_shadow_routing_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.shadow_routing_types import (  # noqa: F401
        ShadowRoutingDecision,
        ShadowRoutingRationale,
        ShadowRoutingTelemetry,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ShadowRoutingRationale = None  # type: ignore[assignment,misc]
    ShadowRoutingDecision = None  # type: ignore[assignment,misc]
    ShadowRoutingTelemetry = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="shadow_routing_types deps unavailable")
class TestShadowRoutingTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/shadow_routing_types.py must be importable."""
        assert _AVAILABLE

    def test_shadowroutingrationale_defined(self) -> None:
        assert ShadowRoutingRationale is not None

    def test_shadowroutingdecision_defined(self) -> None:
        assert ShadowRoutingDecision is not None

    def test_shadowroutingtelemetry_defined(self) -> None:
        assert ShadowRoutingTelemetry is not None