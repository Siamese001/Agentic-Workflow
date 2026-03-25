"""ADG-driven tests for L2 execution type modules — fan_in=1.

Covers: l2_phase_spec, replay_envelope_types, tool_args_types.
"""
from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_l2_types_adg")
# REMOVED: _emit_applies_guardrail("p0", "test_l2_types_adg", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_l2_types_adg", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_l2_types_adg", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_l2_types_adg")
# REMOVED: emit_determinism_digest("p0", "test_l2_types_adg")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_l2_types_adg", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_l2_types_adg", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_l2_types_adg", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_l2_types_adg", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_l2_types_adg", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_l2_types_adg", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_l2_types_adg", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_l2_types_adg", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_l2_types_adg", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_l2_types_adg", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_l2_types_adg", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_l2_types_adg", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_l2_types_adg", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_l2_types_adg", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_l2_types_adg", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_l2_types_adg", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_l2_types_adg", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_l2_types_adg", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_l2_types_adg", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_l2_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# l2_phase_spec
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.l2_phase_spec import (
    LEGACY_MIRROR_PLAN,
    L2ExecutionPlan,
    PhaseSpec,
)


class TestPhaseSpec:
    def test_creates_with_name_only(self):
        spec = PhaseSpec(name="pre_audit")
        assert spec.name == "pre_audit"

    def test_frozen_dataclass(self):
        spec = PhaseSpec(name="discovery")
        with pytest.raises((AttributeError, TypeError)):
            spec.name = "new_name"  # type: ignore[misc]

    def test_guardian_ids_default_empty(self):
        spec = PhaseSpec(name="healing")
        assert spec.guardian_ids == ()

    def test_healer_ids_default_empty(self):
        spec = PhaseSpec(name="healing")
        assert spec.healer_ids == ()

    def test_approval_required_default_false(self):
        spec = PhaseSpec(name="certification")
        assert spec.approval_required is False

    def test_creates_with_guardian_ids(self):
        spec = PhaseSpec(name="pre_audit", guardian_ids=("g1", "g2"))
        assert "g1" in spec.guardian_ids


class TestL2ExecutionPlan:
    def test_creates_with_phases(self):
        plan = L2ExecutionPlan(
            phases=(PhaseSpec(name="p1"), PhaseSpec(name="p2"))
        )
        assert len(plan.phases) == 2

    def test_frozen(self):
        plan = L2ExecutionPlan(phases=(PhaseSpec(name="p1"),))
        with pytest.raises((AttributeError, TypeError)):
            plan.phases = ()  # type: ignore[misc]


class TestLegacyMirrorPlan:
    def test_is_l2_execution_plan(self):
        assert isinstance(LEGACY_MIRROR_PLAN, L2ExecutionPlan)

    def test_has_phases(self):
        assert len(LEGACY_MIRROR_PLAN.phases) > 0

    def test_first_phase_pre_audit(self):
        assert LEGACY_MIRROR_PLAN.phases[0].name == "pre_audit"

    def test_contains_discovery(self):
        names = [p.name for p in LEGACY_MIRROR_PLAN.phases]
        assert "discovery" in names

    def test_contains_healing(self):
        names = [p.name for p in LEGACY_MIRROR_PLAN.phases]
        assert "healing" in names


# ---------------------------------------------------------------------------
# replay_envelope_types
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.replay_envelope_types import ReplayEnvelope


class TestReplayEnvelope:
    def _make_envelope(self, **kwargs):
        defaults = dict(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            allowed_model_policy_version="v1",
            policy_version="v1",
            gateway_version="v1",
            embedder_provider="openai",
            embedder_model="text-embedding-3-small",
            embedder_dim=1536,
            normalization_policy="l2",
            chunking_policy="fixed",
            distance_metric="cosine",
            retrieval_top_k=5,
            retrieval_similarity_cutoff=0.7,
            agent_registry_hash="xyz789",
            deterministic_engine_version="1.0.0",
        )
        defaults.update(kwargs)
        return ReplayEnvelope(**defaults)

    def test_creates_with_required_fields(self):
        env = self._make_envelope()
        assert env.model_id == "gpt-4"

    def test_frozen_dataclass(self):
        env = self._make_envelope()
        with pytest.raises((AttributeError, TypeError)):
            env.model_id = "other"  # type: ignore[misc]

    def test_code_commit_hash_optional(self):
        env = self._make_envelope(code_commit_hash=None)
        assert env.code_commit_hash is None

    def test_code_commit_hash_set(self):
        env = self._make_envelope(code_commit_hash="abc")
        assert env.code_commit_hash == "abc"


# ---------------------------------------------------------------------------
# tool_args_types
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.tool_args_types import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ExecuteCommandArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_l2_types_adg", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_l2_types_adg", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_l2_types_adg", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_l2_types_adg", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_l2_types_adg", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_l2_types_adg", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_l2_types_adg", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_l2_types_adg", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_l2_types_adg", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_l2_types_adg", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_l2_types_adg", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_l2_types_adg", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_l2_types_adg", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_l2_types_adg", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_l2_types_adg", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_l2_types_adg", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_l2_types_adg", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_l2_types_adg", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_l2_types_adg", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_l2_types_adg", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_l2_types_adg", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_l2_types_adg", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_l2_types_adg", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_l2_types_adg", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_l2_types_adg", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l2_types_adg", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l2_types_adg", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_l2_types_adg", "write_through")
# REMOVED: _emit_writes_through("p1", "test_l2_types_adg", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_l2_types_adg", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_l2_types_adg", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_l2_types_adg", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_l2_types_adg", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_l2_types_adg", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_l2_types_adg", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_l2_types_adg", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_l2_types_adg", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_l2_types_adg", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_l2_types_adg", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_l2_types_adg", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_l2_types_adg", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_l2_types_adg", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_l2_types_adg", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_l2_types_adg")
# REMOVED: _emit_gated_by_confidence("p1", "test_l2_types_adg", "confidence_gate")


class TestToolArgsTypes:
    def test_read_file_args_valid(self):
        a = ReadFileArgs(path="foo/bar.py")
        assert a.path == "foo/bar.py"

    def test_write_file_args_valid(self):
        a = WriteFileArgs(path="foo/bar.py", content="hello")
        assert a.content == "hello"

    def test_list_files_args_pattern_optional(self):
        a = ListFilesArgs(directory="src/")
        assert a.pattern is None

    def test_list_files_args_with_pattern(self):
        a = ListFilesArgs(directory="src/", pattern="*.py")
        assert a.pattern == "*.py"

    def test_move_file_args(self):
        a = MoveFileArgs(source="old.py", destination="new.py")
        assert a.source == "old.py"

    def test_delete_file_args(self):
        a = DeleteFileArgs(path="old.py")
        assert a.path == "old.py"

    def test_create_directory_args(self):
        a = CreateDirectoryArgs(path="new_dir/")
        assert a.path == "new_dir/"

    def test_execute_command_args_importable(self):
        assert callable(ExecuteCommandArgs)
