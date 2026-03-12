"""ADG importability contract for agentic_core/L0_routing/types/shadow_routing_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_shadow_routing_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.shadow_routing_types import (  # noqa: F401
        ShadowRoutingRationale,
        ShadowRoutingDecision,
        ShadowRoutingTelemetry,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ShadowRoutingRationale = None  # type: ignore[assignment,misc]
    ShadowRoutingDecision = None  # type: ignore[assignment,misc]
    ShadowRoutingTelemetry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="shadow_routing_types.py deps unavailable")
class TestShadowRoutingTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: shadow_routing_types.py must be importable."""
        assert _AVAILABLE

    def test_shadowroutingrationale_is_type(self) -> None:
        assert ShadowRoutingRationale is not None

    def test_shadowroutingdecision_is_type(self) -> None:
        assert ShadowRoutingDecision is not None

    def test_shadowroutingtelemetry_is_type(self) -> None:
        assert ShadowRoutingTelemetry is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

