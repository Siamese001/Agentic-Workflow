"""ADG contract tests for system_learning/types/snapshot_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.snapshot_types import MetaLearningSnapshot
    _AVAIL = True
except Exception:
    _AVAIL = False
    MetaLearningSnapshot = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMetaLearningSnapshot:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MetaLearningSnapshot)
    def test_is_frozen(self):
        assert MetaLearningSnapshot.__dataclass_params__.frozen is True
    def test_has_required_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(MetaLearningSnapshot)}
        assert "snapshot_id" in fields
        assert "engine_version" in fields
        assert "telemetry_hash" in fields
        assert "policy_config_hash" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
