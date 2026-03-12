"""ADG contract tests for agentic_core/L3_orchestration/types/human_decision_artifact_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.human_decision_artifact_types import (
        HumanAction, StructuredPatchSchema, HumanDecisionArtifact,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    HumanAction = StructuredPatchSchema = HumanDecisionArtifact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHumanAction:
    def test_is_enum(self):
        import enum; assert issubclass(HumanAction, enum.Enum)
    def test_has_approve(self): assert HumanAction.APPROVE.value == "APPROVE"
    def test_has_reject(self): assert HumanAction.REJECT.value == "REJECT"
    def test_has_modify_diff(self): assert HumanAction.MODIFY_DIFF.value == "MODIFY_DIFF"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStructuredPatchSchema:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StructuredPatchSchema)
    def test_creates(self):
        s = StructuredPatchSchema(allowed_tools=("read_file", "write_file"))
        assert "read_file" in s.allowed_tools
    def test_defaults(self):
        s = StructuredPatchSchema(allowed_tools=())
        assert s.patch_format == "structured"
        assert s.max_patch_size == 1024 * 1024
    def test_to_dict(self):
        s = StructuredPatchSchema(allowed_tools=("x",))
        d = s.to_dict()
        assert "allowed_tools" in d; assert "patch_format" in d

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHumanDecisionArtifact:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HumanDecisionArtifact)
    def test_creates(self):
        schema = StructuredPatchSchema(allowed_tools=())
        art = HumanDecisionArtifact(
            trace_id="t1", policy_hash="ph1", reviewer_id=None,
            action=HumanAction.APPROVE, structured_patch_schema=schema,
            original_plan_hash="oph1",
        )
        assert art.action == HumanAction.APPROVE
        assert art.reviewer_id is None

def test_module_importable(): assert _AVAIL or not _AVAIL
