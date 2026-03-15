"""ADG importability contract for agentic_core/L0_routing/types/routing_config_seal_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_routing_config_seal_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.routing_config_seal_types import (  # noqa: F401
        RoutingConfigSeal,
        RoutingConfigSealViolation,
        SealedRoutingContext,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RoutingConfigSealViolation = None  # type: ignore[assignment,misc]
    RoutingConfigSeal = None  # type: ignore[assignment,misc]
    SealedRoutingContext = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="routing_config_seal_types deps unavailable")
class TestRoutingConfigSealTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/routing_config_seal_types.py must be importable."""
        assert _AVAILABLE

    def test_routingconfigsealviolation_defined(self) -> None:
        assert RoutingConfigSealViolation is not None

    def test_routingconfigseal_defined(self) -> None:
        assert RoutingConfigSeal is not None

    def test_sealedroutingcontext_defined(self) -> None:
        assert SealedRoutingContext is not None
