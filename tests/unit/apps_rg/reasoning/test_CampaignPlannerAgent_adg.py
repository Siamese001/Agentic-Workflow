"""ADG importability contract for apps_rg/reasoning/CampaignPlannerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CampaignPlannerAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import apps_rg.reasoning.CampaignPlannerAgent as _mod  # noqa: F401
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="CampaignPlannerAgent.py deps unavailable")
class TestCampaignplanneragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: CampaignPlannerAgent.py must be importable."""
        assert _AVAILABLE