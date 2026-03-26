"""V15 P10.2 — Policy Pack + Validator Tests.

Validates schema enforcement, duplicate detection, enum checks,
forward-compat (unknown fields), and the real committed policy pack.
"""

from __future__ import annotations

import json
from pathlib import Path

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_policy_pack_validator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_policy_pack_validator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_policy_pack_validator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_policy_pack_validator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_policy_pack_validator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_policy_pack_validator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_policy_pack_validator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_policy_pack_validator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_policy_pack_validator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_policy_pack_validator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_policy_pack_validator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_policy_pack_validator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_policy_pack_validator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_policy_pack_validator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_policy_pack_validator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_policy_pack_validator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_policy_pack_validator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_policy_pack_validator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_policy_pack_validator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_policy_pack_validator", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from ops_scripts.policy.validate_v15_policy_pack import validate_policy_pack

# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_policy_pack_validator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_policy_pack_validator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_policy_pack_validator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_policy_pack_validator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_policy_pack_validator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_policy_pack_validator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_policy_pack_validator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_policy_pack_validator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_policy_pack_validator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_policy_pack_validator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_policy_pack_validator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_policy_pack_validator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_policy_pack_validator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_policy_pack_validator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_policy_pack_validator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_policy_pack_validator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_policy_pack_validator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_policy_pack_validator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_policy_pack_validator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_policy_pack_validator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_policy_pack_validator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_policy_pack_validator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_policy_pack_validator", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_policy_pack_validator")
# REMOVED: _emit_applies_guardrail("p0", "test_policy_pack_validator", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_policy_pack_validator", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_policy_pack_validator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_policy_pack_validator", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_pack_validator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_pack_validator", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_policy_pack_validator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_policy_pack_validator", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_policy_pack_validator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_policy_pack_validator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_policy_pack_validator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_policy_pack_validator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_policy_pack_validator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_policy_pack_validator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_policy_pack_validator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_policy_pack_validator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_policy_pack_validator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_policy_pack_validator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_policy_pack_validator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_policy_pack_validator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_policy_pack_validator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_policy_pack_validator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_policy_pack_validator")
# REMOVED: _emit_gated_by_confidence("p1", "test_policy_pack_validator", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_policy_pack_validator")
# REMOVED: emit_determinism_digest("p0", "test_policy_pack_validator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_PACK = REPO_ROOT / L0_ROUTING_DIR / "policy" / "v15_policy_pack.json"


def _valid_rule(rule_id: str = "TEST_001", **overrides):
    """Return a minimal valid rule dict."""
    base = {
        "rule_id": rule_id,
        "applies_to": "PIPE",
        "severity": "WARN",
        "description": "Test rule",
        "enabled": True,
    }
    base.update(overrides)
    return base


def _valid_pack(**overrides):
    """Return a minimal valid policy pack dict."""
    base = {
        "version": "1.0.0",
        "rules": [_valid_rule()],
    }
    base.update(overrides)
    return base


# ===========================================================================
# A) Valid Pack
# ===========================================================================


class TestValidPack:
    """Valid policy packs must pass."""

    def test_minimal_valid(self):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        code, errors, warnings = validate_policy_pack(_valid_pack())
        assert code == 0
        assert errors == []

    def test_multiple_rules(self):
        pack = _valid_pack(
            rules=[
                _valid_rule("R1"),
                _valid_rule("R2", applies_to="POLICY"),
                _valid_rule("R3", severity="HARD_FAIL", applies_to="HASH"),
            ],
        )
        code, errors, _ = validate_policy_pack(pack)
        assert code == 0
        assert errors == []

    def test_all_applies_to_values(self):
        rules = [
            _valid_rule(f"R_{at}", applies_to=at) for at in ["PIPE", "POLICY", "HASH", "CLOCK", "GENERAL"]
        ]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0

    def test_all_severity_values(self):
        rules = [_valid_rule(f"R_{s}", severity=s) for s in ["WARN", "SOFT_FAIL", "HARD_FAIL"]]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0

    def test_metadata_optional(self):
        rule = _valid_rule(metadata={"key": "value"})
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 0

    def test_real_committed_pack(self):
        """The actual committed policy pack must pass validation."""
        assert REAL_PACK.is_file(), f"Real pack not found: {REAL_PACK}"
        data = json.loads(REAL_PACK.read_text(encoding="utf-8"))
        code, errors, _ = validate_policy_pack(data)
        assert code == 0, f"Real pack validation failed: {errors}"


# ===========================================================================
# B) Missing Required Fields (exit 2)
# ===========================================================================


class TestMissingFields:
    """Missing required fields must fail with exit 2."""

    def test_missing_version(self):
        pack = _valid_pack()
        del pack["version"]
        code, errors, _ = validate_policy_pack(pack)
        assert code == 2
        assert any("version" in e for e in errors)

    def test_missing_rules(self):
        pack = _valid_pack()
        del pack["rules"]
        code, errors, _ = validate_policy_pack(pack)
        assert code == 2
        assert any("rules" in e for e in errors)

    def test_empty_rules(self):
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[]))
        assert code == 2
        assert any("at least one" in e for e in errors)

    def test_missing_rule_id(self):
        rule = _valid_rule()
        del rule["rule_id"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("rule_id" in e for e in errors)

    def test_missing_applies_to(self):
        rule = _valid_rule()
        del rule["applies_to"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("applies_to" in e for e in errors)

    def test_missing_severity(self):
        rule = _valid_rule()
        del rule["severity"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("severity" in e for e in errors)

    def test_missing_description(self):
        rule = _valid_rule()
        del rule["description"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("description" in e for e in errors)

    def test_missing_enabled(self):
        rule = _valid_rule()
        del rule["enabled"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("enabled" in e for e in errors)


# ===========================================================================
# C) Bad Enum Values (exit 2)
# ===========================================================================


class TestBadEnums:
    """Invalid enum values must fail with exit 2."""

    def test_bad_applies_to(self):
        rule = _valid_rule(applies_to="INVALID")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("applies_to" in e and "INVALID" in e for e in errors)

    def test_bad_severity(self):
        rule = _valid_rule(severity="CRITICAL")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("severity" in e and "CRITICAL" in e for e in errors)

    def test_bad_enabled_type(self):
        rule = _valid_rule(enabled="yes")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("enabled" in e and "boolean" in e for e in errors)


# ===========================================================================
# D) Duplicate rule_id (exit 3)
# ===========================================================================


class TestDuplicateRuleId:
    """Duplicate rule_ids must fail with exit 3."""

    def test_duplicate_detected(self):
        rules = [_valid_rule("DUP_001"), _valid_rule("DUP_001")]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 3
        assert any("Duplicate" in e and "DUP_001" in e for e in errors)

    def test_three_duplicates(self):
        rules = [_valid_rule("A"), _valid_rule("B"), _valid_rule("A")]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 3


# ===========================================================================
# E) Forward Compatibility (unknown fields -> warn, not fail)
# ===========================================================================


class TestForwardCompat:
    """Unknown fields must produce warnings but not errors."""

    def test_unknown_top_level_field(self):
        pack = _valid_pack()
        pack["future_field"] = "something"
        code, errors, warnings = validate_policy_pack(pack)
        assert code == 0
        assert any("future_field" in w for w in warnings)

    def test_unknown_rule_field(self):
        rule = _valid_rule()
        rule["new_feature"] = 42
        code, errors, warnings = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 0
        assert any("new_feature" in w for w in warnings)

    def test_updated_at_not_warned(self):
        """updated_at is a known optional field — no warning."""
        pack = _valid_pack()
        pack["updated_at"] = "2026-02-10"
        code, _, warnings = validate_policy_pack(pack)
        assert code == 0
        assert not any("updated_at" in w for w in warnings)


# ===========================================================================
# F) Ordering Warning
# ===========================================================================


class TestOrderingWarning:
    """Unsorted rule_ids should produce a warning (not an error)."""

    def test_sorted_no_warning(self):
        rules = [_valid_rule("A_001"), _valid_rule("B_002"), _valid_rule("C_003")]
        _, _, warnings = validate_policy_pack(_valid_pack(rules=rules))
        assert not any("sorted" in w.lower() for w in warnings)

    def test_unsorted_warns(self):
        rules = [_valid_rule("Z_001"), _valid_rule("A_002")]
        code, _, warnings = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0
        assert any("sorted" in w.lower() for w in warnings)
