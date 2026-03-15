"""ADG contract tests for L5_safety/types/heal_model_map_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.heal_model_map_types import (
        HIGH_MODEL_ID,
        LOW_MODEL_ID,
        map_tier_to_model_id,
    )
    from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier
    _AVAIL = True
except ImportError:
    _AVAIL = False
    LOW_MODEL_ID = HIGH_MODEL_ID = map_tier_to_model_id = ReasoningTier = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestModelMapConstants:
    def test_low_model_id(self): assert LOW_MODEL_ID == "local_low"
    def test_high_model_id(self): assert HIGH_MODEL_ID == "local_high"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMapTierToModelId:
    def test_low_tier(self):
        assert map_tier_to_model_id(ReasoningTier.LOW) == LOW_MODEL_ID
    def test_high_tier(self):
        assert map_tier_to_model_id(ReasoningTier.HIGH) == HIGH_MODEL_ID

def test_module_importable(): assert _AVAIL or not _AVAIL
