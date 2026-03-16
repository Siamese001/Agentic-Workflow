"""Contract tests for HumanDecisionArtifact (Path D spec [5])."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_human_decision_artifact")
_emit_applies_guardrail("p0", "test_human_decision_artifact", "p0_governance")
_emit_snapshots_state("p0", "test_human_decision_artifact", "state_snapshot")
emit_replay_key("p0", "test_human_decision_artifact")
emit_determinism_digest("p0", "test_human_decision_artifact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps
from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    HumanDecisionViolation,
)

SECRET = b"test-l5-secret"


def _make(**kwargs) -> HumanDecisionArtifact:
    defaults = {
        "trace_id": "t1",
        "policy_hash": "ph1",
        "reviewer_id": "r1",
        "action": "APPROVE",
        "structured_patch_schema": {},
        "original_plan_hash": "default-plan-hash",
    }
    return HumanDecisionArtifact(**{**defaults, **kwargs})


def test_approve_roundtrip():
    art = _make().sign(SECRET)
    art.verify(SECRET)  # must not raise
    assert art.action == "APPROVE"


def test_reject_roundtrip():
    art = _make(action="REJECT").sign(SECRET)
    art.verify(SECRET)
    assert art.action == "REJECT"


def test_modify_diff_empty_patch_schema_rejected():
    with pytest.raises(HumanDecisionViolation, match="structured_patch_schema"):
        _make(action="MODIFY_DIFF", structured_patch_schema={})


def test_modify_diff_roundtrip():
    art = _make(
        action="MODIFY_DIFF",
        structured_patch_schema={"file": "x.py", "patch": "@@..."},
    ).sign(SECRET)
    art.verify(SECRET)
    assert art.l5_reclear_required


def test_tampered_sig_rejected():
    art = _make().sign(SECRET)
    tampered = HumanDecisionArtifact(
        trace_id=art.trace_id,
        policy_hash=art.policy_hash,
        reviewer_id=art.reviewer_id,
        action=art.action,
        original_plan_hash=art.original_plan_hash,
        structured_patch_schema=art.structured_patch_schema,
        reviewer_sig="deadbeef" * 8,
    )
    with pytest.raises(HumanDecisionViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_empty_trace_id_rejected():
    with pytest.raises(HumanDecisionViolation, match="trace_id"):
        _make(trace_id="")


def test_approve_does_not_set_reclear():
    art = _make(action="APPROVE")
    assert not art.l5_reclear_required


def test_plan_hash_mismatch_raises():
    art = _make(original_plan_hash="plan-A")
    with pytest.raises(HumanDecisionViolation, match="original_plan_hash"):
        art.assert_plan_hash_matches("plan-B")
