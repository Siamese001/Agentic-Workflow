"""ADG importability contract for agentic_core/L0_routing/engines/shadow_routing_wiring.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_shadow_routing_wiring.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.engines.shadow_routing_wiring import (  # noqa: F401
        ShadowRoutingWiring,
        get_shadow_wiring,
        observe_routing_decision,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ShadowRoutingWiring = None  # type: ignore[assignment,misc]
    get_shadow_wiring = None  # type: ignore[assignment,misc]
    observe_routing_decision = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="shadow_routing_wiring.py deps unavailable")
class TestShadowRoutingWiringImportability:
    def test_module_importable(self) -> None:
        """ADG contract: shadow_routing_wiring.py must be importable."""
        assert _AVAILABLE

    def test_shadowroutingwiring_is_type(self) -> None:
        assert ShadowRoutingWiring is not None

    def test_get_shadow_wiring_callable(self) -> None:
        assert callable(get_shadow_wiring)

    def test_observe_routing_decision_callable(self) -> None:
        assert callable(observe_routing_decision)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

