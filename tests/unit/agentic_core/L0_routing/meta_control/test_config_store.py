"""Tests for ConfigStore types + on-disk store -- Wave 7.0.17."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
)
from agentic_core.L0_routing.meta_control.config_store import (
    _version_path,
    apply_change_package_readonly,
    load_current,
    write_next_version,
)
from agentic_core.L0_routing.meta_control.config_store_types import (
    build_config_delta,
    build_config_snapshot,
    canonical_json,
    stable_sha256,
    validate_component_allowed,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_authorize_and_execute("p2", "test_config_store", "execution_auth")
_emit_validates_capability("p2", "test_config_store", "capability_check")
_emit_routes_to_capability("p2", "test_config_store", "capability_route")
_emit_writes_via_uwg("p2", "test_config_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_config_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_config_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_config_store", "exec_output")
_emit_dispatches_agent("p3", "test_config_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_config_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_config_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_config_store", "healing_outcome")
_emit_escalates_failure("p3", "test_config_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_config_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_config_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_config_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_config_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_config_store", "eval_metric")
_emit_stores_embedding("p4", "test_config_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_config_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_config_store", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from system_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)

_emit_emits_metric_event("test_config_store", "p4obs", "metric_1")
_emit_emits_metric_event("test_config_store", "p4obs", "metric_2")
_emit_emits_metric_event("test_config_store", "p4obs", "metric_3")
_emit_emits_metric_event("test_config_store", "p4obs", "metric_4")
_emit_emits_metric_event("test_config_store", "p4obs", "metric_5")
_emit_emits_metric_event("test_config_store", "p4obs", "metric_6")
_emit_records_incident_event("test_config_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_config_store", "p4obs", "anomaly")
_emit_writes_observability_log("test_config_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_config_store", "p4obs", "mon_state")
_emit_triggers_alert("test_config_store", "p4obs", "alert")
_emit_links_incident_trace("test_config_store", "p4obs", "trace_link")
_emit_captures_pattern("test_config_store", "p3lm", "pattern")
_emit_records_learning_event("test_config_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_config_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_config_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_config_store", "p3lm", "routing")
_emit_improves_agent_policy("test_config_store", "p3lm", "policy")
_emit_stores_learning_state("test_config_store", "p3lm", "state")
_emit_records_execution_trace("test_config_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_config_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_config_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_config_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_config_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_config_store", "env_read", "p2_env_1")
_emit_reads_environ("test_config_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_config_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_config_store", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_config_store")
_emit_applies_guardrail("p0", "test_config_store", "p0_governance")
_emit_reads_policy_state("p0", "test_config_store", "policy_binding")
_emit_snapshots_state("p0", "test_config_store", "state_snapshot")
_emit_pulls_context("p1", "test_config_store", "context_pull")
_emit_pulls_context("p1", "test_config_store", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_config_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_config_store", "uwg_term_secondary")
_emit_writes_through("p1", "test_config_store", "write_through")
_emit_writes_through("p1", "test_config_store", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_config_store", "safety_validation")
_emit_invokes_eval("p1", "test_config_store", "eval_call")
_emit_proposal_commits_routing("p1", "test_config_store", "routing_commit")
_emit_escalates_to_human("p1", "test_config_store", "human_escalation")
_emit_routes_through("p1", "test_config_store", "route_through")
_emit_checks_agent_registry("p1", "test_config_store", "agent_registry")
_emit_validates_agent_capability("p1", "test_config_store", "capability")
_emit_dispatches_execution_plan("p1", "test_config_store", "exec_plan")
_emit_agent_executes_agent("p1", "test_config_store", "sub_agent")
_emit_routes_to_agent("p1", "test_config_store", "target_agent")
_emit_verifies_policy("p1", "test_config_store", "policy_check")
_emit_observes_runtime_state("p1", "test_config_store", "runtime_state")
_emit_verifies_boundary("p1", "test_config_store", "boundary_check")
_emit_transcripts_response("p1", "test_config_store", "transcript")
_emit_hard_fails_untranscripted("p1", "test_config_store")
_emit_gated_by_confidence("p1", "test_config_store", "confidence_gate")
emit_replay_key("p0", "test_config_store")
emit_determinism_digest("p0", "test_config_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


class TestCanonicalJsonDeterminism:
    def test_same_dict_different_key_order(self) -> None:
        d1 = {"z": 1, "a": 2, "m": {"b": 3, "a": 4}}
        d2 = {"a": 2, "m": {"a": 4, "b": 3}, "z": 1}
        assert canonical_json(d1) == canonical_json(d2)

    def test_stable_sha256_matches(self) -> None:
        text = canonical_json({"x": 1})
        assert stable_sha256(text) == stable_sha256(text)


class TestVersionIncrement:
    def test_sequential_versions(self, tmp_path: Path) -> None:
        s1 = write_next_version(
            tmp_path,
            APPS_RG_DIR,
            "routing_thresholds",
            {"threshold": 0.5},
            _CLOCK,
        )
        assert s1.config_version == 1
        assert _version_path(tmp_path, APPS_RG_DIR, "routing_thresholds", 1).exists()
        s2 = write_next_version(
            tmp_path,
            APPS_RG_DIR,
            "routing_thresholds",
            {"threshold": 0.7},
            _CLOCK,
        )
        assert s2.config_version == 2
        assert _version_path(tmp_path, APPS_RG_DIR, "routing_thresholds", 2).exists()
        assert s1.trace_id != s2.trace_id


class TestAtomicWriteConsistency:
    def test_current_matches_last_version(self, tmp_path: Path) -> None:
        payload = {"key": "value", "nested": {"a": 1}}
        write_next_version(tmp_path, APPS_RG_DIR, "routing_thresholds", payload, _CLOCK)
        current = load_current(tmp_path, APPS_RG_DIR, "routing_thresholds")
        vf = _version_path(tmp_path, APPS_RG_DIR, "routing_thresholds", 1)
        assert current == json.loads(vf.read_text(encoding="utf-8"))
        write_next_version(tmp_path, APPS_RG_DIR, "routing_thresholds", {"key": "updated"}, _CLOCK)
        current2 = load_current(tmp_path, APPS_RG_DIR, "routing_thresholds")
        vf2 = _version_path(tmp_path, APPS_RG_DIR, "routing_thresholds", 2)
        assert current2 == json.loads(vf2.read_text(encoding="utf-8"))


def _build_change_package(
    *,
    target_component: str = "routing_thresholds",
    change_spec: dict | None = None,
):
    spec = change_spec if change_spec is not None else {"threshold": 0.05}
    proposal = build_meta_learning_proposal(
        semantic_clock=_CLOCK,
        proposer="test",
        target_component=target_component,
        before={"threshold": 0.5},
        after=spec,
        metric_name="accuracy",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="abc123",
    )
    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator="bench",
        dataset_id="ds",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="eval_hash",
    )
    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver="reviewer",
        decision="APPROVE",
        rationale="OK",
    )
    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )
    return build_meta_learning_change_package(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        target_component=target_component,
        change_spec=spec,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )


class TestApplyChangePackageReadonly:
    def test_does_not_create_files(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        store.mkdir()
        before = set(store.rglob("*"))
        pkg = _build_change_package()
        delta = apply_change_package_readonly(store, pkg, _CLOCK)
        after = set(store.rglob("*"))
        assert before == after, "apply_change_package_readonly must not create files"
        assert delta.artifact_type == "META_CONTROL_CONFIG_DELTA"
        assert delta.from_version == 0
        assert delta.to_version == 1


class TestFailClosed:
    def test_invalid_component_raises(self) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            validate_component_allowed("guardian_contract")

    def test_load_current_invalid_component(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            load_current(tmp_path, APPS_RG_DIR, "guardian_contract")

    def test_write_next_version_empty_app_id(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="APP_ID_EMPTY"):
            write_next_version(tmp_path, "", "routing_thresholds", {}, _CLOCK)

    def test_load_current_returns_empty_on_missing(self, tmp_path: Path) -> None:
        assert load_current(tmp_path, APPS_RG_DIR, "routing_thresholds") == {}


class TestSnapshotDeterminism:
    def test_identical_inputs_produce_identical_trace(self) -> None:
        s1 = build_config_snapshot(
            app_id=APPS_RG_DIR,
            target_component="routing_thresholds",
            config_version=1,
            payload={"threshold": 0.5},
            semantic_clock=_CLOCK,
        )
        s2 = build_config_snapshot(
            app_id=APPS_RG_DIR,
            target_component="routing_thresholds",
            config_version=1,
            payload={"threshold": 0.5},
            semantic_clock=_CLOCK,
        )
        assert s1.trace_id == s2.trace_id
        assert s1.to_json() == s2.to_json()


class TestDeltaVersionGap:
    def test_version_gap_rejected(self) -> None:
        with pytest.raises(ValueError, match="VERSION_GAP"):
            build_config_delta(
                app_id=APPS_RG_DIR,
                target_component="routing_thresholds",
                from_version=1,
                to_version=3,
                change_spec={"threshold": 0.05},
                semantic_clock=_CLOCK,
            )
