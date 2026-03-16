"""
REQ-085/086/HDA: Human-in-the-Loop bypass rejection tests.

Tests that HumanDecisionArtifact enforces:
  1. reviewer_sig must be present and valid before execution proceeds
  2. MODIFY_DIFF forces l5_reclear_required=True (automatically)
  3. original_plan_hash must match the submitted plan (anti-replay)
  4. Empty/missing fields are rejected at construction time (fail-closed)
  5. verify() raises on tampered or absent signature

§1 windsurfrules compliance:
- §1.3  Deterministic: fixed secret bytes, no wall-clock, no randomness
- §1.5  Edge cases: empty sig, empty trace_id, wrong plan hash, tampered sig
- §1.6  State transitions: unsigned→sign→verify PASS; unsigned→verify FAIL
- §1.7  Determinism: same inputs → same HMAC → same sig
- §1.8  Fail-closed: HumanDecisionViolation raised before execution
- §1.9  Matrix: action × sig-state × plan-hash-match
- §1.11 Regression: near-miss (valid sig on different payload)

ROBUSTNESS_MATRIX:
  Surface                        | success | edge | failure | recovery | determinism
  -------------------------------|---------|------|---------|----------|------------
  construction validation        |   ✅   |  ✅  |   ✅   |   N/A   |     ✅
  sign() produces valid sig      |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify() passes on valid sig   |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify() rejects absent sig    |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  verify() rejects tampered sig  |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  plan_hash mismatch rejected    |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  MODIFY_DIFF forces l5_reclear  |   ✅   |  ✅  |   N/A  |   N/A   |     ✅

DEFECT_MODEL:
  D1 - Empty reviewer_sig accepted — human bypass with no signature
  D2 - MODIFY_DIFF proceeds without L5 re-clear
  D3 - Tampered artifact passes verify() — replay/forgery attack
  D4 - Plan hash mismatch accepted — cross-plan replay
  D5 - HMAC non-deterministic (sign different results for same input)
  D6 - APPROVE with empty trace_id accepted — untraceable approval
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    HumanDecisionViolation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hil_bypass_rejection")
_emit_applies_guardrail("p0", "test_hil_bypass_rejection", "p0_governance")
_emit_snapshots_state("p0", "test_hil_bypass_rejection", "state_snapshot")
emit_replay_key("p0", "test_hil_bypass_rejection")
emit_determinism_digest("p0", "test_hil_bypass_rejection")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.governance

_SECRET = b"test-secret-key-32bytes-padded!!"
_TRACE = "trace-abc-123"
_POLICY = "policy-hash-xyz"
_REVIEWER = "reviewer-001"
_PLAN_HASH = "plan-hash-aaa"
_PATCH = {"op": "replace", "path": "/model", "value": "gpt-4o"}


def _make(
    action: str = "APPROVE",
    trace_id: str = _TRACE,
    policy_hash: str = _POLICY,
    reviewer_id: str = _REVIEWER,
    original_plan_hash: str = _PLAN_HASH,
    structured_patch_schema: dict | None = None,
    reviewer_sig: str = "",
) -> HumanDecisionArtifact:
    return HumanDecisionArtifact(
        trace_id=trace_id,
        policy_hash=policy_hash,
        reviewer_id=reviewer_id,
        action=action,
        original_plan_hash=original_plan_hash,
        structured_patch_schema=structured_patch_schema or {},
        reviewer_sig=reviewer_sig,
    )


# ---------------------------------------------------------------------------
# Construction validation — fail-closed (§1.8)
# ---------------------------------------------------------------------------


class TestConstructionValidation:
    def test_empty_trace_id_raises(self):
        with pytest.raises(HumanDecisionViolation, match="trace_id"):
            _make(trace_id="")

    def test_empty_original_plan_hash_raises(self):
        with pytest.raises(HumanDecisionViolation, match="original_plan_hash"):
            _make(original_plan_hash="")

    def test_modify_diff_without_patch_raises(self):
        with pytest.raises(HumanDecisionViolation, match="structured_patch_schema"):
            _make(action="MODIFY_DIFF", structured_patch_schema={})

    def test_modify_diff_with_patch_succeeds(self):
        artifact = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert artifact.action == "MODIFY_DIFF"

    def test_approve_without_patch_succeeds(self):
        artifact = _make(action="APPROVE")
        assert artifact.action == "APPROVE"

    def test_reject_without_patch_succeeds(self):
        artifact = _make(action="REJECT")
        assert artifact.action == "REJECT"

    def test_artifact_is_frozen(self):
        artifact = _make()
        with pytest.raises(AttributeError):
            artifact.reviewer_id = "hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# MODIFY_DIFF forces l5_reclear_required (§1.6 / D2)
# ---------------------------------------------------------------------------


class TestL5ReclearEnforcement:
    def test_modify_diff_sets_l5_reclear_true(self):
        artifact = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert artifact.l5_reclear_required is True

    def test_approve_does_not_set_l5_reclear(self):
        artifact = _make(action="APPROVE")
        assert artifact.l5_reclear_required is False

    def test_reject_does_not_set_l5_reclear(self):
        artifact = _make(action="REJECT")
        assert artifact.l5_reclear_required is False

    def test_l5_reclear_is_deterministic_across_instances(self):
        a = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        b = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert a.l5_reclear_required == b.l5_reclear_required is True


# ---------------------------------------------------------------------------
# Sign / verify lifecycle (§1.6 state transitions)
# ---------------------------------------------------------------------------


class TestSignVerifyLifecycle:
    def test_unsigned_verify_raises(self):
        artifact = _make()
        with pytest.raises(HumanDecisionViolation, match="reviewer_sig absent"):
            artifact.verify(_SECRET)

    def test_sign_then_verify_passes(self):
        artifact = _make().sign(_SECRET)
        artifact.verify(_SECRET)  # must not raise

    def test_sign_produces_nonempty_sig(self):
        artifact = _make().sign(_SECRET)
        assert artifact.reviewer_sig
        assert len(artifact.reviewer_sig) > 10

    def test_sign_is_deterministic(self):
        a = _make().sign(_SECRET)
        b = _make().sign(_SECRET)
        assert a.reviewer_sig == b.reviewer_sig

    def test_sign_different_secrets_different_sigs(self):
        a = _make().sign(b"secret-one")
        b = _make().sign(b"secret-two")
        assert a.reviewer_sig != b.reviewer_sig

    def test_verify_wrong_secret_raises(self):
        artifact = _make().sign(_SECRET)
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            artifact.verify(b"wrong-secret")


# ---------------------------------------------------------------------------
# Tampered artifact — D3 regression
# ---------------------------------------------------------------------------


class TestTamperedArtifact:
    def test_tampered_action_fails_verify(self):
        signed = _make(action="APPROVE").sign(_SECRET)
        # Reconstruct with different action but same sig
        tampered = HumanDecisionArtifact(
            trace_id=signed.trace_id,
            policy_hash=signed.policy_hash,
            reviewer_id=signed.reviewer_id,
            action="MODIFY_DIFF",
            original_plan_hash=signed.original_plan_hash,
            structured_patch_schema=_PATCH,
            reviewer_sig=signed.reviewer_sig,
        )
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            tampered.verify(_SECRET)

    def test_tampered_reviewer_id_fails_verify(self):
        signed = _make().sign(_SECRET)
        tampered = HumanDecisionArtifact(
            trace_id=signed.trace_id,
            policy_hash=signed.policy_hash,
            reviewer_id="attacker",
            action=signed.action,
            original_plan_hash=signed.original_plan_hash,
            structured_patch_schema=signed.structured_patch_schema,
            reviewer_sig=signed.reviewer_sig,
        )
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            tampered.verify(_SECRET)

    def test_tampered_trace_id_fails_verify(self):
        signed = _make().sign(_SECRET)
        tampered = HumanDecisionArtifact(
            trace_id="injected-trace",
            policy_hash=signed.policy_hash,
            reviewer_id=signed.reviewer_id,
            action=signed.action,
            original_plan_hash=signed.original_plan_hash,
            structured_patch_schema=signed.structured_patch_schema,
            reviewer_sig=signed.reviewer_sig,
        )
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            tampered.verify(_SECRET)


# ---------------------------------------------------------------------------
# Plan hash mismatch — cross-plan replay (D4)
# ---------------------------------------------------------------------------


class TestPlanHashMismatch:
    def test_correct_plan_hash_passes(self):
        artifact = _make(original_plan_hash="plan-aaa")
        artifact.assert_plan_hash_matches("plan-aaa")  # no raise

    def test_wrong_plan_hash_raises(self):
        artifact = _make(original_plan_hash="plan-aaa")
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            artifact.assert_plan_hash_matches("plan-bbb")

    def test_empty_submitted_hash_raises(self):
        artifact = _make(original_plan_hash="plan-aaa")
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("")

    def test_plan_hash_check_is_exact(self):
        artifact = _make(original_plan_hash="plan-aaa")
        # Near-miss: prefix match is not enough
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("plan-aa")


# ---------------------------------------------------------------------------
# Matrix: action × sig-state × plan-hash (§1.9)
# ---------------------------------------------------------------------------


class TestActionMatrix:
    @pytest.mark.parametrize(
        "action,patch,expect_l5",
        [
            ("APPROVE", {}, False),
            ("REJECT", {}, False),
            ("MODIFY_DIFF", _PATCH, True),
        ],
    )
    def test_l5_reclear_by_action(self, action, patch, expect_l5):
        artifact = _make(action=action, structured_patch_schema=patch)
        assert artifact.l5_reclear_required is expect_l5

    @pytest.mark.parametrize("action", ["APPROVE", "REJECT"])
    def test_unsigned_always_fails_verify(self, action):
        artifact = _make(action=action)
        with pytest.raises(HumanDecisionViolation):
            artifact.verify(_SECRET)

    @pytest.mark.parametrize("action", ["APPROVE", "REJECT"])
    def test_signed_always_passes_verify(self, action):
        artifact = _make(action=action).sign(_SECRET)
        artifact.verify(_SECRET)  # no raise


# ---------------------------------------------------------------------------
# Fail-closed: no side-effects before violation raised (§1.8)
# ---------------------------------------------------------------------------


class TestFailClosed:
    def test_verify_raises_before_any_side_effect(self):
        artifact = _make()
        sentinel = []
        with pytest.raises(HumanDecisionViolation):
            artifact.verify(_SECRET)
            sentinel.append("ran")
        assert sentinel == []

    def test_plan_hash_raises_before_any_side_effect(self):
        artifact = _make(original_plan_hash="correct")
        sentinel = []
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("wrong")
            sentinel.append("ran")
        assert sentinel == []
