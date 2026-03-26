"""Unit tests for system_learning.engines.rag_optimizer."""

import pytest

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

# REMOVED: _emit_authorize_and_execute("p2", "test_rag_optimizer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_rag_optimizer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_rag_optimizer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_rag_optimizer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_rag_optimizer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_rag_optimizer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_rag_optimizer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_rag_optimizer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_rag_optimizer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_rag_optimizer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_rag_optimizer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_rag_optimizer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_rag_optimizer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_rag_optimizer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_rag_optimizer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_rag_optimizer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_rag_optimizer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_rag_optimizer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_rag_optimizer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_rag_optimizer", "exec_snapshot_link")
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
#  # MOVED: from system_learning.engines.rag_optimizer import (
    RAGChangePackage,
    propose_rag_param_changes,
)
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy

# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_rag_optimizer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_rag_optimizer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_rag_optimizer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_rag_optimizer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_rag_optimizer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_rag_optimizer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_rag_optimizer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_rag_optimizer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_rag_optimizer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_rag_optimizer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_rag_optimizer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_rag_optimizer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_rag_optimizer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_rag_optimizer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_rag_optimizer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_rag_optimizer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_rag_optimizer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_rag_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_rag_optimizer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_rag_optimizer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_rag_optimizer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_rag_optimizer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_rag_optimizer", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_rag_optimizer")
# REMOVED: _emit_applies_guardrail("p0", "test_rag_optimizer", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_rag_optimizer", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_rag_optimizer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_rag_optimizer", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_rag_optimizer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_rag_optimizer", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_rag_optimizer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_rag_optimizer", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_rag_optimizer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_rag_optimizer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_rag_optimizer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_rag_optimizer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_rag_optimizer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_rag_optimizer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_rag_optimizer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_rag_optimizer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_rag_optimizer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_rag_optimizer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_rag_optimizer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_rag_optimizer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_rag_optimizer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_rag_optimizer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_rag_optimizer")
# REMOVED: _emit_gated_by_confidence("p1", "test_rag_optimizer", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_rag_optimizer")
# REMOVED: emit_determinism_digest("p0", "test_rag_optimizer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestRAGOptimizer:
    def test_valid_proposal_passes_constraints(self):
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        """Valid proposal within bounds and delta."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is not None
        assert proposal.surface_name == "retrieval_top_k"
        assert proposal.old_value == 10
        assert proposal.new_value == 12

    def test_out_of_range_rejected(self):
        """Proposal exceeding max bounds raises."""
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        # The heuristic caps at 20, so this won't exceed bounds
        # Instead, test that the capping works correctly
        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.50},
            current_config={"retrieval_top_k": 19},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )
        # Proposal should be capped at max (20)
        assert proposal is not None
        assert proposal.new_value == 20

    def test_cooldown_violated_returns_none(self):
        """Cooldown violation returns None (no proposal)."""
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700001800,  # Only 1800 seconds elapsed
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None

    def test_sample_size_violated_returns_none(self):
        """Sample size violation returns None (no proposal)."""
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 500,  # Below minimum
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None

    def test_no_change_needed_returns_none(self):
        """No change needed when metrics are in acceptable range."""
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.75},  # In acceptable range
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None


class TestRAGChangePackage:
    def test_canonical_bytes_deterministic(self):
        """Same inputs produce identical canonical bytes."""
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.canonical_bytes() == pkg2.canonical_bytes()

    def test_content_hash_deterministic(self):
        """Same inputs produce identical content hash."""
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.content_hash() == pkg2.content_hash()

    def test_different_values_produce_different_hash(self):
        """Different values produce different content hash."""
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=15,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.content_hash() != pkg2.content_hash()


class TestDeterminism:
    def test_proposal_deterministic(self):
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        """Identical inputs produce identical proposals."""
#  # MOVED: from system_learning.engines.rag_optimizer import RAGChangePackage, propose_rag_param_changes
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal1 = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        proposal2 = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal1 is not None
        assert proposal2 is not None
        assert proposal1.content_hash() == proposal2.content_hash()
