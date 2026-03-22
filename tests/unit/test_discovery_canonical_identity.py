"""Unit tests for discovery canonical identity fields.

Ensures every ACTIVE agent record emitted by full_agent_discovery has:
  - canonical_class (AST-verified, non-empty)
  - canonical_file (forward-slash normalized, no backslashes)
  - canonical_agent_id (non-empty)

Outcome 1 of post-consolidation hardening.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.scripts.full_agent_discovery import (
    perform_deep_integrity_scan,
)
from agentic_core.L0_routing.utils.ssot_discovery_util import (
    load_agent_discovery,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_1")
_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_2")
_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_3")
_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_4")
_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_5")
_emit_emits_metric_event("test_discovery_canonical_identity", "p4obs", "metric_6")
_emit_records_incident_event("test_discovery_canonical_identity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_discovery_canonical_identity", "p4obs", "anomaly")
_emit_writes_observability_log("test_discovery_canonical_identity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_discovery_canonical_identity", "p4obs", "mon_state")
_emit_triggers_alert("test_discovery_canonical_identity", "p4obs", "alert")
_emit_links_incident_trace("test_discovery_canonical_identity", "p4obs", "trace_link")
_emit_captures_pattern("test_discovery_canonical_identity", "p3lm", "pattern")
_emit_records_learning_event("test_discovery_canonical_identity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_discovery_canonical_identity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_discovery_canonical_identity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_discovery_canonical_identity", "p3lm", "routing")
_emit_improves_agent_policy("test_discovery_canonical_identity", "p3lm", "policy")
_emit_stores_learning_state("test_discovery_canonical_identity", "p3lm", "state")
_emit_records_execution_trace("test_discovery_canonical_identity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_discovery_canonical_identity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_discovery_canonical_identity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_discovery_canonical_identity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_discovery_canonical_identity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_discovery_canonical_identity", "env_read", "p2_env_1")
_emit_reads_environ("test_discovery_canonical_identity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_discovery_canonical_identity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_discovery_canonical_identity", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_discovery_canonical_identity")
_emit_applies_guardrail("p0", "test_discovery_canonical_identity", "p0_governance")
_emit_reads_policy_state("p0", "test_discovery_canonical_identity", "policy_binding")
_emit_snapshots_state("p0", "test_discovery_canonical_identity", "state_snapshot")
_emit_pulls_context("p1", "test_discovery_canonical_identity", "context_pull")
_emit_pulls_context("p1", "test_discovery_canonical_identity", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_discovery_canonical_identity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_discovery_canonical_identity", "uwg_term_secondary")
_emit_writes_through("p1", "test_discovery_canonical_identity", "write_through")
_emit_writes_through("p1", "test_discovery_canonical_identity", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_discovery_canonical_identity", "safety_validation")
_emit_invokes_eval("p1", "test_discovery_canonical_identity", "eval_call")
_emit_proposal_commits_routing("p1", "test_discovery_canonical_identity", "routing_commit")
_emit_escalates_to_human("p1", "test_discovery_canonical_identity", "human_escalation")
_emit_routes_through("p1", "test_discovery_canonical_identity", "route_through")
_emit_checks_agent_registry("p1", "test_discovery_canonical_identity", "agent_registry")
_emit_validates_agent_capability("p1", "test_discovery_canonical_identity", "capability")
_emit_dispatches_execution_plan("p1", "test_discovery_canonical_identity", "exec_plan")
_emit_agent_executes_agent("p1", "test_discovery_canonical_identity", "sub_agent")
_emit_routes_to_agent("p1", "test_discovery_canonical_identity", "target_agent")
_emit_verifies_policy("p1", "test_discovery_canonical_identity", "policy_check")
_emit_observes_runtime_state("p1", "test_discovery_canonical_identity", "runtime_state")
_emit_verifies_boundary("p1", "test_discovery_canonical_identity", "boundary_check")
_emit_transcripts_response("p1", "test_discovery_canonical_identity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_discovery_canonical_identity")
_emit_gated_by_confidence("p1", "test_discovery_canonical_identity", "confidence_gate")
emit_replay_key("p0", "test_discovery_canonical_identity")
emit_determinism_digest("p0", "test_discovery_canonical_identity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_discovery_canonical_identity", "execution_auth")
_emit_validates_capability("p2", "test_discovery_canonical_identity", "capability_check")
_emit_routes_to_capability("p2", "test_discovery_canonical_identity", "capability_route")
_emit_writes_via_uwg("p2", "test_discovery_canonical_identity", "uwg_write")
_emit_blocks_direct_write("p2", "test_discovery_canonical_identity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_discovery_canonical_identity", "tool_invocation")
_emit_captures_execution_output("p2", "test_discovery_canonical_identity", "exec_output")
_emit_dispatches_agent("p3", "test_discovery_canonical_identity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_discovery_canonical_identity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_discovery_canonical_identity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_discovery_canonical_identity", "healing_outcome")
_emit_escalates_failure("p3", "test_discovery_canonical_identity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_discovery_canonical_identity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_discovery_canonical_identity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_discovery_canonical_identity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_discovery_canonical_identity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_discovery_canonical_identity", "eval_metric")
_emit_stores_embedding("p4", "test_discovery_canonical_identity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_discovery_canonical_identity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_discovery_canonical_identity", "exec_snapshot_link")


@pytest.fixture(scope="module")
def verified_agents():
    """Run discovery once and return verified agent list."""
    project_root = get_validated_project_root()
    raw = load_agent_discovery(project_root, force_reload=True)
    verified, _stats = perform_deep_integrity_scan(raw, project_root)
    return verified


class TestCanonicalClassPresent:
    """Every verified agent must have canonical_class."""

    def test_all_records_have_canonical_class(self, verified_agents):
        missing = [
            a.get("class_name", a.get("canonical_file", "?"))
            for a in verified_agents
            if not a.get("canonical_class")
        ]
        assert not missing, f"{len(missing)} agent(s) missing canonical_class: {missing[:10]}"

    def test_canonical_class_matches_verification_status(self, verified_agents):
        mismatches = []
        for a in verified_agents:
            vs_class = (a.get("verification_status") or {}).get("class", "")
            cc = a.get("canonical_class", "")
            if cc and vs_class and cc != vs_class:
                mismatches.append((cc, vs_class))
        assert not mismatches, f"canonical_class != verification_status.class: {mismatches[:10]}"


class TestCanonicalFileNormalized:
    """canonical_file must be forward-slash normalized (§20)."""

    def test_all_records_have_canonical_file(self, verified_agents):
        missing = [a.get("canonical_class", "?") for a in verified_agents if not a.get("canonical_file")]
        assert not missing, f"{len(missing)} agent(s) missing canonical_file: {missing[:10]}"

    def test_no_backslashes_in_canonical_file(self, verified_agents):
        bad = [a["canonical_file"] for a in verified_agents if "\\" in a.get("canonical_file", "")]
        assert not bad, f"{len(bad)} canonical_file(s) contain backslashes: {bad[:10]}"

    def test_no_dot_segments_in_canonical_file(self, verified_agents):
        bad = [
            a["canonical_file"]
            for a in verified_agents
            if a.get("canonical_file", "").startswith("./") or "/../" in a.get("canonical_file", "")
        ]
        assert not bad, f"{len(bad)} canonical_file(s) contain dot segments: {bad[:10]}"


class TestCanonicalAgentId:
    """canonical_agent_id must be present and non-empty."""

    def test_all_records_have_canonical_agent_id(self, verified_agents):
        missing = [a.get("canonical_class", "?") for a in verified_agents if not a.get("canonical_agent_id")]
        assert not missing, f"{len(missing)} agent(s) missing canonical_agent_id: {missing[:10]}"


class TestClassNameDivergence:
    """If class_name differs from canonical_class, canonical_class must still exist."""

    def test_divergent_class_name_still_has_canonical(self, verified_agents):
        divergent_missing = []
        for a in verified_agents:
            cn = a.get("class_name", "")
            cc = a.get("canonical_class", "")
            if cn and cn != cc and not cc:
                divergent_missing.append(cn)
        assert not divergent_missing, (
            f"class_name != canonical_class but canonical_class missing: {divergent_missing[:10]}"
        )
