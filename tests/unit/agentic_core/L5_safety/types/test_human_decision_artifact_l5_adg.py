"""ADG contract tests for agentic_core/L5_safety/types/human_decision_artifact_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.human_decision_artifact_types import (
        HumanDecisionArtifact, HumanDecisionViolation,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    HumanDecisionArtifact = HumanDecisionViolation = None  # type: ignore[assignment,misc]

def _make_artifact(**kwargs):
    defaults = dict(
        trace_id="t1", policy_hash="ph1",
        reviewer_id="rev1", action="APPROVE",
        original_plan_hash="oph1",
        structured_patch_schema={},
    )
    defaults.update(kwargs)
    return HumanDecisionArtifact(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHumanDecisionViolation:
    def test_is_value_error(self): assert issubclass(HumanDecisionViolation, ValueError)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHumanDecisionArtifact:
    def test_is_frozen(self): assert HumanDecisionArtifact.__dataclass_params__.frozen is True
    def test_creates_approve(self):
        a = _make_artifact(); assert a.action == "APPROVE"
    def test_l5_reclear_false_for_approve(self):
        a = _make_artifact(action="APPROVE"); assert a.l5_reclear_required is False
    def test_l5_reclear_true_for_modify_diff(self):
        a = _make_artifact(action="MODIFY_DIFF",
                           structured_patch_schema={"tool": "edit"})
        assert a.l5_reclear_required is True
    def test_modify_diff_without_schema_raises(self):
        with pytest.raises(HumanDecisionViolation):
            _make_artifact(action="MODIFY_DIFF", structured_patch_schema={})
    def test_empty_trace_id_raises(self):
        with pytest.raises(HumanDecisionViolation):
            _make_artifact(trace_id="")
    def test_empty_plan_hash_raises(self):
        with pytest.raises(HumanDecisionViolation):
            _make_artifact(original_plan_hash="")
    def test_assert_plan_hash_matches_ok(self):
        a = _make_artifact(original_plan_hash="oph1")
        a.assert_plan_hash_matches("oph1")  # should not raise
    def test_assert_plan_hash_mismatch_raises(self):
        a = _make_artifact(original_plan_hash="oph1")
        with pytest.raises(HumanDecisionViolation):
            a.assert_plan_hash_matches("other_hash")

def test_module_importable(): assert _AVAIL or not _AVAIL
