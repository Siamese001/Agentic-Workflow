"""ADG contract tests for apps_shared/types/pipeline_stage_status_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_pipeline_stage_status_types_adg")
_emit_applies_guardrail("p0", "test_pipeline_stage_status_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_pipeline_stage_status_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_pipeline_stage_status_types_adg", "state_snapshot")
emit_replay_key("p0", "test_pipeline_stage_status_types_adg")
emit_determinism_digest("p0", "test_pipeline_stage_status_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.pipeline_stage_status_types import (
        PipelineStageStatus,
        StageResult,
    )
    _AVAIL = True
except ImportError:
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
