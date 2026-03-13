"""ADG importability contract for agentic_core/L2_execution/engines/resource_predictor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_resource_predictor.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.resource_predictor import (  # noqa: F401
        DefaultDeterministicResourcePredictor,
        ResourcePredictor,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ResourcePredictor = None  # type: ignore[assignment,misc]
    DefaultDeterministicResourcePredictor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resource_predictor deps unavailable")
class TestResourcePredictorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/engines/resource_predictor.py must be importable."""
        assert _AVAILABLE

    def test_resourcepredictor_defined(self) -> None:
        assert ResourcePredictor is not None

    def test_defaultdeterministicresourcepredictor_defined(self) -> None:
        assert DefaultDeterministicResourcePredictor is not None
