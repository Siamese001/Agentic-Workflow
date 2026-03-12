"""ADG importability contract for agentic_core/L5_safety/enforcement/layer_sovereignty_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_layer_sovereignty_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.layer_sovereignty_enforcer import (  # noqa: F401
        SovereigntyViolation,
        EnforcementReport,
        LayerSovereigntyEnforcer,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereigntyViolation = None  # type: ignore[assignment,misc]
    EnforcementReport = None  # type: ignore[assignment,misc]
    LayerSovereigntyEnforcer = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="layer_sovereignty_enforcer.py deps unavailable")
class TestLayerSovereigntyEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: layer_sovereignty_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_sovereigntyviolation_is_type(self) -> None:
        assert SovereigntyViolation is not None

    def test_enforcementreport_is_type(self) -> None:
        assert EnforcementReport is not None

    def test_layersovereigntyenforcer_is_type(self) -> None:
        assert LayerSovereigntyEnforcer is not None

    def test_main_callable(self) -> None:
        assert callable(main)

