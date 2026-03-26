"""V15 P8.2c — Enforcement Mode Transition Safety Matrix.

Proves the exactly-one rule for every valid/invalid V15_ENFORCEMENT value:
- UNSET:     enforced=True (fail-closed default), soft=False, hard=False (log mode)
- OFF:       enforced=False, soft=False, hard=False  (explicit opt-out only)
- LOG_ONLY:  enforced=True,  soft=False, hard=False
- SOFT_FAIL: enforced=True,  soft=True,  hard=False
- HARD_FAIL: enforced=True,  soft=False, hard=True
- INVALID:   ValueError raised (deterministic misconfig rejection)

Covers case variants, whitespace, synonyms, and invalid inputs.
"""

from __future__ import annotations

import pytest

#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import (
    is_v15_enforced,
    is_v15_hard_fail,
    is_v15_soft_fail,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_enforcement_mode_transition_matrix", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_enforcement_mode_transition_matrix", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_enforcement_mode_transition_matrix", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_enforcement_mode_transition_matrix", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_enforcement_mode_transition_matrix", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_enforcement_mode_transition_matrix", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_enforcement_mode_transition_matrix", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_enforcement_mode_transition_matrix", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_enforcement_mode_transition_matrix", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_enforcement_mode_transition_matrix", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_enforcement_mode_transition_matrix", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_enforcement_mode_transition_matrix", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_enforcement_mode_transition_matrix", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_enforcement_mode_transition_matrix", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_enforcement_mode_transition_matrix", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_enforcement_mode_transition_matrix", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_enforcement_mode_transition_matrix", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_enforcement_mode_transition_matrix", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_enforcement_mode_transition_matrix", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_enforcement_mode_transition_matrix", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_enforcement_mode_transition_matrix", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_enforcement_mode_transition_matrix", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_enforcement_mode_transition_matrix", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_enforcement_mode_transition_matrix")
# REMOVED: _emit_applies_guardrail("p0", "test_enforcement_mode_transition_matrix", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_enforcement_mode_transition_matrix", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_enforcement_mode_transition_matrix", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_enforcement_mode_transition_matrix", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_enforcement_mode_transition_matrix", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_enforcement_mode_transition_matrix", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_enforcement_mode_transition_matrix", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_enforcement_mode_transition_matrix", "write_through")
# REMOVED: _emit_writes_through("p1", "test_enforcement_mode_transition_matrix", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_enforcement_mode_transition_matrix", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_enforcement_mode_transition_matrix", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_enforcement_mode_transition_matrix", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_enforcement_mode_transition_matrix", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_enforcement_mode_transition_matrix", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_enforcement_mode_transition_matrix", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_enforcement_mode_transition_matrix", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_enforcement_mode_transition_matrix", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_enforcement_mode_transition_matrix", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_enforcement_mode_transition_matrix", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_enforcement_mode_transition_matrix", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_enforcement_mode_transition_matrix", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_enforcement_mode_transition_matrix", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_enforcement_mode_transition_matrix", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_enforcement_mode_transition_matrix")
# REMOVED: _emit_gated_by_confidence("p1", "test_enforcement_mode_transition_matrix", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_enforcement_mode_transition_matrix")
# REMOVED: emit_determinism_digest("p0", "test_enforcement_mode_transition_matrix")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_enforcement_mode_transition_matrix", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_enforcement_mode_transition_matrix", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_enforcement_mode_transition_matrix", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_enforcement_mode_transition_matrix", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_enforcement_mode_transition_matrix", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_enforcement_mode_transition_matrix", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_enforcement_mode_transition_matrix", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_enforcement_mode_transition_matrix", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_enforcement_mode_transition_matrix", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_enforcement_mode_transition_matrix", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_enforcement_mode_transition_matrix", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_enforcement_mode_transition_matrix", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_enforcement_mode_transition_matrix", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_enforcement_mode_transition_matrix", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_enforcement_mode_transition_matrix", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_enforcement_mode_transition_matrix", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_enforcement_mode_transition_matrix", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_enforcement_mode_transition_matrix", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_enforcement_mode_transition_matrix", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_enforcement_mode_transition_matrix", "exec_snapshot_link")

# ===========================================================================
# Parametrized mode matrix
# ===========================================================================

# (env_value, expected_enforced, expected_soft, expected_hard, label)
DEFAULT_ON_CASES = [
    (None, True, False, False, "unset_default_on"),
]

OFF_CASES = [
    ("0", False, False, False, "zero"),
    ("false", False, False, False, "false_lower"),
    ("FALSE", False, False, False, "false_upper"),
    ("off", False, False, False, "off_lower"),
    ("OFF", False, False, False, "off_upper"),
    ("no", False, False, False, "no_lower"),
    ("NO", False, False, False, "no_upper"),
]

LOG_CASES = [
    ("log", True, False, False, "log_lower"),
    ("LOG", True, False, False, "log_upper"),
    ("Log", True, False, False, "log_title"),
    ("on", True, False, False, "on_lower"),
    ("ON", True, False, False, "on_upper"),
]

SOFT_CASES = [
    ("soft", True, True, False, "soft_lower"),
    ("SOFT", True, True, False, "soft_upper"),
    ("Soft", True, True, False, "soft_title"),
]

HARD_CASES = [
    ("1", True, False, True, "one"),
    ("true", True, False, True, "true_lower"),
    ("TRUE", True, False, True, "true_upper"),
    ("True", True, False, True, "true_title"),
    ("yes", True, False, True, "yes_lower"),
    ("YES", True, False, True, "yes_upper"),
    ("Yes", True, False, True, "yes_title"),
]

# Whitespace variants — these MUST parse identically after normalization
WHITESPACE_CASES = [
    (" log ", True, False, False, "log_padded"),
    (" soft ", True, True, False, "soft_padded"),
    (" True ", True, False, True, "true_padded"),
    (" 1 ", True, False, True, "one_padded"),
    ("\tsoft\t", True, True, False, "soft_tabbed"),
    ("\nlog\n", True, False, False, "log_newline"),
    (" 0 ", False, False, False, "zero_padded"),
    (" off ", False, False, False, "off_padded"),
]

# Invalid values — must raise ValueError (deterministic misconfig rejection)
INVALID_CASES = [
    ("", "empty"),
    ("garbage", "garbage"),
    ("2", "two"),
    ("enabled", "enabled"),
    ("disable", "disable"),
]

ALL_CASES = DEFAULT_ON_CASES + OFF_CASES + LOG_CASES + SOFT_CASES + HARD_CASES + WHITESPACE_CASES


def _set_env(monkeypatch, value):
    """Set or unset V15_ENFORCEMENT."""
    if value is None:
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
    else:
        monkeypatch.setenv("V15_ENFORCEMENT", value)


# ===========================================================================
# A) Full Matrix
# ===========================================================================


class TestModeMatrix:
    """Exhaustive mode matrix: every input → exactly one mode selected."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        ALL_CASES,
        ids=[c[4] for c in ALL_CASES],
    )
    def test_mode_selection(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        from agentic_core.L0_routing.types.guardian_contract_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        _set_env(monkeypatch, env_val)
        enforced = is_v15_enforced()
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()

        assert enforced == exp_enforced, f"[{label}] enforced: got {enforced}, expected {exp_enforced}"
        assert soft == exp_soft, f"[{label}] soft: got {soft}, expected {exp_soft}"
        assert hard == exp_hard, f"[{label}] hard: got {hard}, expected {exp_hard}"


# ===========================================================================
# B) Exactly-One Rule
# ===========================================================================


class TestExactlyOneRule:
    """When enforced, exactly one of (log, soft, hard) must be active."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        [c for c in ALL_CASES if c[1]],  # only enforced cases
        ids=[c[4] for c in ALL_CASES if c[1]],
    )
    def test_exactly_one_active_mode(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        _set_env(monkeypatch, env_val)
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()
        log_only = not soft and not hard

        # Exactly one must be True
        active = sum([log_only, soft, hard])
        assert active == 1, (
            f"[{label}] Expected exactly 1 active mode, got {active} (log={log_only}, soft={soft}, hard={hard})"
        )

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        [c for c in ALL_CASES if not c[1]],  # only OFF cases
        ids=[c[4] for c in ALL_CASES if not c[1]],
    )
    def test_off_means_all_false(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        _set_env(monkeypatch, env_val)
        assert not is_v15_enforced()
        assert not is_v15_soft_fail()
        assert not is_v15_hard_fail()


# ===========================================================================
# C) Mutual Exclusion
# ===========================================================================


class TestMutualExclusion:
    """soft and hard must never both be True simultaneously."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        ALL_CASES,
        ids=[c[4] for c in ALL_CASES],
    )
    def test_soft_and_hard_never_both_true(
        self,
        monkeypatch,
        env_val,
        exp_enforced,
        exp_soft,
        exp_hard,
        label,
    ):
        _set_env(monkeypatch, env_val)
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()
        assert not (soft and hard), f"[{label}] soft and hard both True — mode ambiguity!"


# ===========================================================================
# D) Determinism
# ===========================================================================


class TestDeterminism:
    """Same input must always produce same output."""

    @pytest.mark.parametrize("env_val", ["log", "soft", "1", "0", "off"])
    def test_idempotent_across_calls(self, monkeypatch, env_val):
        monkeypatch.setenv("V15_ENFORCEMENT", env_val)
        results = [(is_v15_enforced(), is_v15_soft_fail(), is_v15_hard_fail()) for _ in range(10)]
        assert len(set(results)) == 1, f"Non-deterministic for '{env_val}': {set(results)}"

    def test_idempotent_unset(self, monkeypatch):
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
        results = [(is_v15_enforced(), is_v15_soft_fail(), is_v15_hard_fail()) for _ in range(10)]
        assert len(set(results)) == 1, f"Non-deterministic for unset: {set(results)}"

    @pytest.mark.parametrize("env_val", ["garbage", "", "2"])
    def test_idempotent_invalid_raises(self, monkeypatch, env_val):
        monkeypatch.setenv("V15_ENFORCEMENT", env_val)
        for _ in range(5):
            with pytest.raises(ValueError):
                is_v15_enforced()


# ===========================================================================
# E) Invalid Value Rejection
# ===========================================================================


class TestInvalidValueRejection:
    """Unrecognized V15_ENFORCEMENT values must raise ValueError."""

    @pytest.mark.parametrize(
        "env_val, label",
        INVALID_CASES,
        ids=[c[1] for c in INVALID_CASES],
    )
    def test_invalid_value_raises_valueerror(self, monkeypatch, env_val, label):
        monkeypatch.setenv("V15_ENFORCEMENT", env_val)
        with pytest.raises(ValueError, match="not a recognized value"):
            is_v15_enforced()
