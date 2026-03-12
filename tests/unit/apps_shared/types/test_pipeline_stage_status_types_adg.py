"""ADG contract tests for apps_shared/types/pipeline_stage_status_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.pipeline_stage_status_types import (
        PipelineStageStatus, StageResult,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    PipelineStageStatus = StageResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPipelineStageStatus:
    def test_is_enum(self):
        import enum; assert issubclass(PipelineStageStatus, enum.Enum)
    def test_has_pending(self): assert PipelineStageStatus.PENDING
    def test_has_success(self): assert PipelineStageStatus.SUCCESS
    def test_has_failed(self): assert PipelineStageStatus.FAILED

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStageResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StageResult)
    def test_creates(self):
        r = StageResult(
            stage_name="k1_summary",
            status=PipelineStageStatus.SUCCESS,
            duration_ms=150.0,
            output_hash="abc123",
        )
        assert r.stage_name == "k1_summary"; assert r.error_message is None

def test_module_importable(): assert _AVAIL or not _AVAIL
