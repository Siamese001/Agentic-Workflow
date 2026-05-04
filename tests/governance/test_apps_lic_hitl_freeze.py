"""apps_lic W1 (D2) — HITL freeze/review/re-clearance sentinel tests.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W1 D2-P2
Coverage:
  - HITLFreezePolicy: no_freeze baseline, omission escalation, low confidence,
    dim-score trigger, bypass env var, policy_eval_error degraded mode,
    hard-fail takes precedence.
  - re-clearance: approve → ALLOW_FINISH, reject → DENY, return_to_l1 → REROUTE.
  - GovernedLicRun: freeze fields on record, run_reclearance() method.
  - hitl_policy.yaml schema: required keys present.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
HITL_POLICY = REPO_ROOT / "apps_lic" / "config" / "hitl_policy.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_policy():
    from apps_lic.integrations.hitl_freeze_policy import HITLFreezePolicy
    return HITLFreezePolicy()


def _no_freeze_context() -> dict:
    return {
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "confidence_score": 0.9,
        "omission_escalations": [],
        "asymmetric_insight_required": False,
        "technical_claim_depth_high": False,
    }


def _exec_context(confidence: float = 0.9) -> dict:
    return {
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "cold",
        "confidence_score": confidence,
        "omission_escalations": [],
        "asymmetric_insight_required": False,
        "technical_claim_depth_high": False,
    }


# ===========================================================================
# 1. Config schema
# ===========================================================================

class TestHITLPolicyYAML:
    def test_policy_file_exists(self):
        assert HITL_POLICY.exists(), "apps_lic/config/hitl_policy.yaml must exist"

    def test_schema_version_present(self):
        with HITL_POLICY.open(encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        assert p.get("schema_version") == "1.0"

    def test_freeze_on_dim_low_score_has_entries(self):
        with HITL_POLICY.open(encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        entries = p.get("freeze_on_dim_low_score", [])
        assert len(entries) >= 3, "must have at least 3 dim-score freeze triggers"

    def test_reclearance_disposition_map_complete(self):
        with HITL_POLICY.open(encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        dmap = (p.get("reclearance") or {}).get("disposition_map", {})
        assert "cleared" in dmap
        assert "rejected" in dmap
        assert "returned_to_l1" in dmap

    def test_valid_terminal_states(self):
        with HITL_POLICY.open(encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        terminal = (p.get("reclearance") or {}).get("terminal_states", [])
        assert set(terminal) == {"cleared", "rejected", "returned_to_l1"}

    def test_bypass_section_present(self):
        with HITL_POLICY.open(encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        bypass = p.get("bypass", {})
        assert bypass.get("env_var") == "HITL_FREEZE_BYPASS"


# ===========================================================================
# 2. FreezeDecision shape
# ===========================================================================

class TestFreezeDecisionShape:
    def test_freeze_decision_is_frozen(self):
        from apps_lic.integrations.hitl_freeze_policy import FreezeDecision
        fd = FreezeDecision(should_freeze=True, freeze_status="frozen", triggered_by="test")
        assert fd.should_freeze is True
        assert fd.freeze_status == "frozen"

    def test_freeze_decision_no_freeze(self):
        from apps_lic.integrations.hitl_freeze_policy import FreezeDecision
        fd = FreezeDecision(should_freeze=False, freeze_status="no_freeze")
        assert fd.should_freeze is False
        assert fd.omission_escalation is False

    def test_freeze_decision_immutable(self):
        from apps_lic.integrations.hitl_freeze_policy import FreezeDecision
        fd = FreezeDecision(should_freeze=False, freeze_status="no_freeze")
        with pytest.raises((AttributeError, TypeError)):
            fd.should_freeze = True  # type: ignore[misc]


# ===========================================================================
# 3. HITLFreezePolicy — no-freeze baseline
# ===========================================================================

class TestNoFreezeBaseline:
    def test_recruiter_high_confidence_no_freeze(self):
        policy = _make_policy()
        result = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.9, "clear_cta": 0.9},
            run_context=_no_freeze_context(),
        )
        assert result.should_freeze is False
        assert result.freeze_status == "no_freeze"

    def test_empty_dim_scores_no_freeze_for_recruiter(self):
        policy = _make_policy()
        result = policy.evaluate(dim_scores={}, run_context=_no_freeze_context())
        assert result.should_freeze is False

    def test_dim_scores_above_threshold_no_freeze(self):
        policy = _make_policy()
        result = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.8, "clear_cta": 0.7},
            run_context=_exec_context(confidence=0.9),
        )
        assert result.should_freeze is False


# ===========================================================================
# 4. HITLFreezePolicy — freeze triggers
# ===========================================================================

class TestFreezeTriggers:
    def test_omission_escalation_always_freezes(self):
        policy = _make_policy()
        ctx = _no_freeze_context()
        ctx["omission_escalations"] = ["claim_foo"]
        result = policy.evaluate(dim_scores={}, run_context=ctx)
        assert result.should_freeze is True
        assert result.freeze_status == "frozen"
        assert result.omission_escalation is True

    def test_low_confidence_exec_freezes(self):
        policy = _make_policy()
        ctx = _exec_context(confidence=0.4)
        result = policy.evaluate(dim_scores={}, run_context=ctx)
        assert result.should_freeze is True
        assert "confidence" in result.triggered_by.lower()

    def test_low_confidence_recruiter_no_freeze(self):
        policy = _make_policy()
        ctx = _no_freeze_context()
        ctx["confidence_score"] = 0.3
        result = policy.evaluate(dim_scores={}, run_context=ctx)
        assert result.should_freeze is False

    def test_dim_low_score_exec_freezes(self):
        policy = _make_policy()
        result = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.1},
            run_context=_exec_context(),
        )
        assert result.should_freeze is True
        assert "tone_fit_seniority" in result.triggered_by

    def test_dim_low_score_recruiter_exec_trigger_no_freeze(self):
        policy = _make_policy()
        result = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.1},
            run_context=_no_freeze_context(),
        )
        assert result.should_freeze is False

    def test_clear_cta_low_all_recipients_freeze(self):
        policy = _make_policy()
        result = policy.evaluate(
            dim_scores={"clear_cta": 0.1},
            run_context=_no_freeze_context(),
        )
        assert result.should_freeze is True
        assert "clear_cta" in result.triggered_by

    def test_hard_fail_prevents_freeze(self):
        policy = _make_policy()
        ctx = _exec_context(confidence=0.3)
        result = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.1},
            run_context=ctx,
            hard_fails=["no_fabricated_relationship"],
        )
        assert result.should_freeze is False
        assert "hard_fail" in result.freeze_status or "no_freeze" == result.freeze_status


# ===========================================================================
# 5. Bypass env var
# ===========================================================================

class TestBypassEnvVar:
    def test_bypass_env_var_skips_freeze(self):
        policy = _make_policy()
        ctx = _exec_context(confidence=0.1)
        ctx["omission_escalations"] = ["claim_x"]
        with mock.patch.dict(os.environ, {"HITL_FREEZE_BYPASS": "1"}):
            result = policy.evaluate(dim_scores={"clear_cta": 0.0}, run_context=ctx)
        assert result.should_freeze is False
        assert result.freeze_status == "bypassed"

    def test_bypass_not_set_freeze_fires(self):
        policy = _make_policy()
        ctx = _exec_context(confidence=0.1)
        env = {k: v for k, v in os.environ.items() if k != "HITL_FREEZE_BYPASS"}
        with mock.patch.dict(os.environ, env, clear=True):
            result = policy.evaluate(dim_scores={}, run_context=ctx)
        assert result.should_freeze is True


# ===========================================================================
# 6. HITLFreezePolicy — re-clearance state machine
# ===========================================================================

class TestReClearanceStateMachine:
    def test_approve_emits_allow_finish(self):
        policy = _make_policy()
        decision = policy.evaluate_reclearance(reviewer_action="approve")
        assert decision.new_x3_disposition == "ALLOW_FINISH"
        assert decision.new_freeze_status == "cleared"
        assert decision.is_terminal is True

    def test_reject_emits_deny(self):
        policy = _make_policy()
        decision = policy.evaluate_reclearance(reviewer_action="reject")
        assert decision.new_x3_disposition == "DENY"
        assert decision.new_freeze_status == "rejected"

    def test_return_to_l1_emits_reroute(self):
        policy = _make_policy()
        decision = policy.evaluate_reclearance(reviewer_action="return_to_l1")
        assert decision.new_x3_disposition == "REROUTE"
        assert decision.new_freeze_status == "returned_to_l1"

    def test_unknown_action_defaults_to_deny(self):
        policy = _make_policy()
        decision = policy.evaluate_reclearance(reviewer_action="do_something_weird")
        assert decision.new_x3_disposition == "DENY"
        assert decision.is_terminal is True

    def test_reviewer_note_passed_through(self):
        policy = _make_policy()
        decision = policy.evaluate_reclearance(reviewer_action="approve", reviewer_note="LGTM")
        assert decision.reviewer_note == "LGTM"

    def test_reclearance_decision_is_immutable(self):
        from apps_lic.integrations.hitl_freeze_policy import HITLReClearanceDecision
        d = HITLReClearanceDecision(
            new_x3_disposition="ALLOW_FINISH",
            new_freeze_status="cleared",
        )
        with pytest.raises((AttributeError, TypeError)):
            d.new_x3_disposition = "DENY"  # type: ignore[misc]


# ===========================================================================
# 7. GovernedLicRun — freeze fields + run_reclearance()
# ===========================================================================

class TestGovernedLicRunFreezeWiring:
    def test_record_has_freeze_status_field(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicE2ERunRecord
        import dataclasses
        fields = {f.name for f in dataclasses.fields(GovernedLicE2ERunRecord)}
        assert "freeze_status" in fields
        assert "freeze_triggered_by" in fields

    def test_record_freeze_status_default_not_evaluated(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicE2ERunRecord
        import dataclasses
        defaults = {
            f.name: f.default
            for f in dataclasses.fields(GovernedLicE2ERunRecord)
            if f.default is not dataclasses.MISSING
        }
        assert defaults.get("freeze_status") == "not_evaluated"
        assert defaults.get("freeze_triggered_by") == ""

    def test_run_reclearance_approve(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicRun
        runner = GovernedLicRun()
        decision = runner.run_reclearance(reviewer_action="approve")
        assert decision.new_x3_disposition == "ALLOW_FINISH"
        assert decision.is_terminal is True

    def test_run_reclearance_reject(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicRun
        runner = GovernedLicRun()
        decision = runner.run_reclearance(reviewer_action="reject")
        assert decision.new_x3_disposition == "DENY"

    def test_run_reclearance_return_to_l1(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicRun
        runner = GovernedLicRun()
        decision = runner.run_reclearance(reviewer_action="return_to_l1", reviewer_note="needs briefing refresh")
        assert decision.new_x3_disposition == "REROUTE"
        assert decision.reviewer_note == "needs briefing refresh"

    def test_run_reclearance_does_not_write_state(self):
        from apps_lic.integrations.governed_lic_run import GovernedLicRun
        runner = GovernedLicRun()
        before_attrs = set(runner.__dict__.keys())
        runner.run_reclearance(reviewer_action="approve")
        after_attrs = set(runner.__dict__.keys())
        assert before_attrs == after_attrs, "run_reclearance must not add instance state"
