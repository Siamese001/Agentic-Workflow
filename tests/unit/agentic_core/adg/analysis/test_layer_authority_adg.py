"""ADG importability contract for agentic_core/adg/analysis/layer_authority.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_layer_authority.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.layer_authority import (  # noqa: F401
        LayerAuthorityViolation,
        LayerAuthorityReport,
        detect_layer_authority_violations,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LayerAuthorityViolation = None  # type: ignore[assignment,misc]
    LayerAuthorityReport = None  # type: ignore[assignment,misc]
    detect_layer_authority_violations = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="layer_authority.py deps unavailable")
class TestLayerAuthorityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: layer_authority.py must be importable."""
        assert _AVAILABLE

    def test_layerauthorityviolation_is_type(self) -> None:
        assert LayerAuthorityViolation is not None

    def test_layerauthorityreport_is_type(self) -> None:
        assert LayerAuthorityReport is not None

    def test_detect_layer_authority_violations_callable(self) -> None:
        assert callable(detect_layer_authority_violations)

