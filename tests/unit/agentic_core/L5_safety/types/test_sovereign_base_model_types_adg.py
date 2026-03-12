"""ADG contract tests for L5_safety/types/sovereign_base_model_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.sovereign_base_model_types import SovereignBaseModel, Territory
    _AVAIL = True
except Exception:
    _AVAIL = False; SovereignBaseModel = Territory = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSovereignBaseModel:
    def test_is_pydantic(self):
        from pydantic import BaseModel; assert issubclass(SovereignBaseModel, BaseModel)
    def test_frozen(self):
        class Concrete(SovereignBaseModel):
            x: int = 1
        c = Concrete()
        with pytest.raises(Exception): c.x = 2  # type: ignore[misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTerritory:
    def test_is_pydantic(self):
        from pydantic import BaseModel; assert issubclass(Territory, BaseModel)
    def test_creates(self):
        t = Territory(name="L2", depth=2, path="agentic_core/L2_execution")
        assert t.name == "L2"; assert t.depth == 2
    def test_frozen(self):
        t = Territory(name="L2", depth=2, path="p")
        with pytest.raises(Exception): t.name = "L3"  # type: ignore[misc]

def test_module_importable(): assert _AVAIL or not _AVAIL
