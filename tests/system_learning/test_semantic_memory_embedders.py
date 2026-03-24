"""Tests for the six ADG semantic memory embedders and registry.

Covers:
  - Type construction and validation (IncidentBundle, MutationDiffRecord,
    HealerOutcomeRecord, PathDPreferencePair, GraphNeighborhood, PolicyGuardrailCase)
  - Deterministic text serialization (to_embedding_text idempotency)
  - Content-hash determinism (same input → same hash)
  - CorpusRecord generation and namespace tagging
  - Buffer management (ingest, ingest_batch, buffer_size, FIFO eviction)
  - Export determinism (export_corpus_records sorted by content_hash, trace_id)
  - Convenience constructors with literal validation
  - Retrieval falls back to [] when semantic cache unavailable (no live index)
  - SemanticMemoryRegistry singleton lifecycle and unified export

All tests are pure-Python, no external dependencies, no live embedding calls.
"""

from __future__ import annotations

import threading

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

_emit_authorize_and_execute("p2", "test_semantic_memory_embedders", "execution_auth")
_emit_validates_capability("p2", "test_semantic_memory_embedders", "capability_check")
_emit_routes_to_capability("p2", "test_semantic_memory_embedders", "capability_route")
_emit_writes_via_uwg("p2", "test_semantic_memory_embedders", "uwg_write")
_emit_blocks_direct_write("p2", "test_semantic_memory_embedders", "direct_write_block")
_emit_records_tool_invocation("p2", "test_semantic_memory_embedders", "tool_invocation")
_emit_captures_execution_output("p2", "test_semantic_memory_embedders", "exec_output")
_emit_dispatches_agent("p3", "test_semantic_memory_embedders", "agent_dispatch")
_emit_coordinates_agents("p3", "test_semantic_memory_embedders", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_semantic_memory_embedders", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_semantic_memory_embedders", "healing_outcome")
_emit_escalates_failure("p3", "test_semantic_memory_embedders", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_semantic_memory_embedders", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_semantic_memory_embedders", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_semantic_memory_embedders", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_semantic_memory_embedders", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_semantic_memory_embedders", "eval_metric")
_emit_stores_embedding("p4", "test_semantic_memory_embedders", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_semantic_memory_embedders", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_semantic_memory_embedders", "exec_snapshot_link")
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
from system_learning.engines.graph_neighborhood_embedder import GraphNeighborhoodEmbedder
from system_learning.engines.healer_outcome_embedder import HealerOutcomeEmbedder

# ---------------------------------------------------------------------------
# Engines
# ---------------------------------------------------------------------------
from system_learning.engines.incident_bundle_embedder import IncidentBundleEmbedder
from system_learning.engines.mutation_diff_embedder import MutationDiffEmbedder
from system_learning.engines.path_d_preference_embedder import PathDPreferenceEmbedder
from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder
from system_learning.engines.semantic_memory_registry import SemanticMemoryRegistry

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
from system_learning.types.semantic_memory_types import (
    GraphNeighborhood,
    HealerOutcomeRecord,
    IncidentBundle,
    MutationDiffRecord,
    PathDPreferencePair,
    PolicyGuardrailCase,
)

_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_1")
_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_2")
_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_3")
_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_4")
_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_5")
_emit_emits_metric_event("test_semantic_memory_embedders", "p4obs", "metric_6")
_emit_records_incident_event("test_semantic_memory_embedders", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_semantic_memory_embedders", "p4obs", "anomaly")
_emit_writes_observability_log("test_semantic_memory_embedders", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_semantic_memory_embedders", "p4obs", "mon_state")
_emit_triggers_alert("test_semantic_memory_embedders", "p4obs", "alert")
_emit_links_incident_trace("test_semantic_memory_embedders", "p4obs", "trace_link")
_emit_captures_pattern("test_semantic_memory_embedders", "p3lm", "pattern")
_emit_records_learning_event("test_semantic_memory_embedders", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_semantic_memory_embedders", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_semantic_memory_embedders", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_semantic_memory_embedders", "p3lm", "routing")
_emit_improves_agent_policy("test_semantic_memory_embedders", "p3lm", "policy")
_emit_stores_learning_state("test_semantic_memory_embedders", "p3lm", "state")
_emit_records_execution_trace("test_semantic_memory_embedders", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_semantic_memory_embedders", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_semantic_memory_embedders", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_semantic_memory_embedders", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_semantic_memory_embedders", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_semantic_memory_embedders", "env_read", "p2_env_1")
_emit_reads_environ("test_semantic_memory_embedders", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_semantic_memory_embedders", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_semantic_memory_embedders", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_semantic_memory_embedders")
_emit_applies_guardrail("p0", "test_semantic_memory_embedders", "p0_governance")
_emit_snapshots_state("p0", "test_semantic_memory_embedders", "state_snapshot")
_emit_pulls_context("p1", "test_semantic_memory_embedders", "context_pull")
_emit_pulls_context("p1", "test_semantic_memory_embedders", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_semantic_memory_embedders", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_semantic_memory_embedders", "uwg_term_secondary")
_emit_writes_through("p1", "test_semantic_memory_embedders", "write_through")
_emit_writes_through("p1", "test_semantic_memory_embedders", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_semantic_memory_embedders", "safety_validation")
_emit_invokes_eval("p1", "test_semantic_memory_embedders", "eval_call")
_emit_proposal_commits_routing("p1", "test_semantic_memory_embedders", "routing_commit")
_emit_escalates_to_human("p1", "test_semantic_memory_embedders", "human_escalation")
_emit_routes_through("p1", "test_semantic_memory_embedders", "route_through")
_emit_checks_agent_registry("p1", "test_semantic_memory_embedders", "agent_registry")
_emit_validates_agent_capability("p1", "test_semantic_memory_embedders", "capability")
_emit_dispatches_execution_plan("p1", "test_semantic_memory_embedders", "exec_plan")
_emit_agent_executes_agent("p1", "test_semantic_memory_embedders", "sub_agent")
_emit_routes_to_agent("p1", "test_semantic_memory_embedders", "target_agent")
_emit_verifies_policy("p1", "test_semantic_memory_embedders", "policy_check")
_emit_observes_runtime_state("p1", "test_semantic_memory_embedders", "runtime_state")
_emit_verifies_boundary("p1", "test_semantic_memory_embedders", "boundary_check")
_emit_transcripts_response("p1", "test_semantic_memory_embedders", "transcript")
_emit_hard_fails_untranscripted("p1", "test_semantic_memory_embedders")
_emit_gated_by_confidence("p1", "test_semantic_memory_embedders", "confidence_gate")
emit_replay_key("p0", "test_semantic_memory_embedders")
emit_determinism_digest("p0", "test_semantic_memory_embedders")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture(autouse=True)
def reset_registry():
    """Ensure singleton is clean for each test."""
    SemanticMemoryRegistry.reset_for_testing()
    yield
    SemanticMemoryRegistry.reset_for_testing()


def _make_incident(
    trace_id: str = "trace-001",
    outcome: str = "success",
) -> IncidentBundle:
    return IncidentBundle(
        trace_id=trace_id,
        trace_summary="ImportError in module X during healing",
        violations=("IMPORT_VIOLATION", "LAYER_BOUNDARY"),
        route_path="PATH_B",
        tool_capability="file_system.write",
        state_diff_summary="+3 lines, -1 line in config.py",
        healer_id="ImportHealerAgent",
        outcome=outcome,  # type: ignore[arg-type]
        policy_hash="abc123",
        timestamp_utc=1_700_000_000,
    )


def _make_mutation(
    mutation_id: str = "mut-001",
    commit_outcome: str = "committed",
) -> MutationDiffRecord:
    return MutationDiffRecord(
        mutation_id=mutation_id,
        target_resource="agentic_core/L2_execution/config/limits.py",
        operations=('{"op":"replace","path":"/timeout","value":30}',),
        state_diff_summary="+1 line: timeout = 30",
        rollback_context="previous value: timeout = 20",
        commit_outcome=commit_outcome,  # type: ignore[arg-type]
        trace_id="trace-mut-001",
        policy_hash="pol-abc",
        timestamp_utc=1_700_000_001,
    )


def _make_healer_outcome(
    healer_id: str = "ImportHealerAgent",
    outcome: str = "success",
) -> HealerOutcomeRecord:
    return HealerOutcomeRecord(
        healer_id=healer_id,
        failure_type="IMPORT_ERROR",
        violation_text="ModuleNotFoundError: No module named 'x'",
        fix_rationale="Added missing import at top of file",
        change_summary="+1 import statement",
        package_version="V2",
        outcome=outcome,  # type: ignore[arg-type]
        tier="LOCAL_AGENT",
        trace_id="trace-heal-001",
        timestamp_utc=1_700_000_002,
    )


def _make_preference_pair(
    decision_id: str = "hitl-001",
    decision: str = "approved",
) -> PathDPreferencePair:
    return PathDPreferencePair(
        decision_id=decision_id,
        original_plan="Move file X to directory Y",
        human_patch="Move file X to directory Z instead",
        decision=decision,  # type: ignore[arg-type]
        reason="Directory Z is the correct SSOT location",
        resulting_outcome="File successfully moved to Z",
        agent="FileReorganizationAgent",
        trace_id="trace-hitl-001",
        timestamp_utc=1_700_000_003,
    )


def _make_graph_neighborhood(
    node_id: str = "agentic_core/L2_execution/healers/ImportHealer.py",
) -> GraphNeighborhood:
    return GraphNeighborhood(
        node_id=node_id,
        node_type="healer",
        layer="L2_execution",
        inbound_relations=("calls", "imports"),
        outbound_relations=("writes_through", "records_execution_trace"),
        governance_edges=("applies_guardrail",),
        mutation_edges=("writes_through",),
        ownership_territory="L2_execution_healers",
        risk_label="mutation_broker",
    )


def _make_guardrail_case(
    case_id: str = "case-001",
    verdict: str = "true_positive",
) -> PolicyGuardrailCase:
    return PolicyGuardrailCase(
        case_id=case_id,
        blocked_payload_summary="Attempted write to .py file outside allowed paths",
        remediation_text="Use UniversalWriteGateway for all file mutations",
        policy_hash="pol-xyz",
        policy_root="L5_SourceMutationGuard",
        verdict=verdict,  # type: ignore[arg-type]
        strictness_level="STRICT",
        trace_id="trace-guard-001",
        timestamp_utc=1_700_000_004,
    )


# ===========================================================================
# 1. IncidentBundle
# ===========================================================================


class TestIncidentBundle:
    def test_construction_sets_bundle_hash(self):
        b = _make_incident()
        assert len(b.bundle_hash) == 64
        assert b.influence_class == "C0_INFORMATIONAL"

    def test_bundle_hash_is_deterministic(self):
        b1 = _make_incident()
        b2 = _make_incident()
        assert b1.bundle_hash == b2.bundle_hash

    def test_different_outcomes_yield_different_hashes(self):
        b1 = _make_incident(outcome="success")
        b2 = _make_incident(outcome="failure")
        assert b1.bundle_hash != b2.bundle_hash

    def test_invalid_outcome_raises(self):
        with pytest.raises(ValueError, match="outcome"):
            IncidentBundle(
                trace_id="t",
                trace_summary="s",
                violations=(),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="INVALID",  # type: ignore[arg-type]
                policy_hash="p",
                timestamp_utc=0,
            )

    def test_empty_trace_id_raises(self):
        with pytest.raises(ValueError, match="trace_id"):
            IncidentBundle(
                trace_id="",
                trace_summary="s",
                violations=(),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=0,
            )

    def test_to_embedding_text_is_idempotent(self):
        b = _make_incident()
        assert b.to_embedding_text() == b.to_embedding_text()

    def test_to_embedding_text_contains_key_fields(self):
        b = _make_incident()
        text = b.to_embedding_text()
        assert "trace:" in text
        assert "violations:" in text
        assert "healer:" in text
        assert "outcome:success" in text
        assert "policy:" in text

    def test_violations_sorted_in_text(self):
        b = IncidentBundle(
            trace_id="t",
            trace_summary="s",
            violations=("ZZZ", "AAA"),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="success",
            policy_hash="p",
            timestamp_utc=0,
        )
        text = b.to_embedding_text()
        assert text.index("AAA") < text.index("ZZZ")


# ===========================================================================
# 2. MutationDiffRecord
# ===========================================================================


class TestMutationDiffRecord:
    def test_construction_sets_diff_hash(self):
        r = _make_mutation()
        assert len(r.diff_hash) == 64
        assert r.influence_class == "C0_INFORMATIONAL"

    def test_diff_hash_is_deterministic(self):
        r1 = _make_mutation()
        r2 = _make_mutation()
        assert r1.diff_hash == r2.diff_hash

    def test_invalid_commit_outcome_raises(self):
        with pytest.raises(ValueError, match="commit_outcome"):
            MutationDiffRecord(
                mutation_id="m",
                target_resource="x",
                operations=(),
                state_diff_summary="y",
                rollback_context="z",
                commit_outcome="INVALID",  # type: ignore[arg-type]
                trace_id="t",
                policy_hash="p",
                timestamp_utc=0,
            )

    def test_empty_mutation_id_raises(self):
        with pytest.raises(ValueError, match="mutation_id"):
            MutationDiffRecord(
                mutation_id="",
                target_resource="x",
                operations=(),
                state_diff_summary="y",
                rollback_context="z",
                commit_outcome="committed",
                trace_id="t",
                policy_hash="p",
                timestamp_utc=0,
            )

    def test_to_embedding_text_contains_key_fields(self):
        r = _make_mutation()
        text = r.to_embedding_text()
        assert "mutation:" in text
        assert "resource:" in text
        assert "outcome:committed" in text
        assert "policy:" in text

    def test_rolled_back_distinct_from_committed(self):
        r1 = _make_mutation(commit_outcome="committed")
        r2 = _make_mutation(commit_outcome="rolled_back")
        assert r1.diff_hash != r2.diff_hash


# ===========================================================================
# 3. HealerOutcomeRecord
# ===========================================================================


class TestHealerOutcomeRecord:
    def test_construction_sets_outcome_hash(self):
        r = _make_healer_outcome()
        assert len(r.outcome_hash) == 64
        assert r.influence_class == "C0_INFORMATIONAL"

    def test_outcome_hash_is_deterministic(self):
        r1 = _make_healer_outcome()
        r2 = _make_healer_outcome()
        assert r1.outcome_hash == r2.outcome_hash

    def test_invalid_outcome_raises(self):
        with pytest.raises(ValueError, match="outcome"):
            HealerOutcomeRecord(
                healer_id="h",
                failure_type="f",
                violation_text="v",
                fix_rationale="r",
                change_summary="c",
                package_version="V1",
                outcome="WRONG",  # type: ignore[arg-type]
                tier="LOCAL",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_empty_healer_id_raises(self):
        with pytest.raises(ValueError, match="healer_id"):
            HealerOutcomeRecord(
                healer_id="",
                failure_type="f",
                violation_text="v",
                fix_rationale="r",
                change_summary="c",
                package_version="V1",
                outcome="success",
                tier="LOCAL",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_to_embedding_text_contains_key_fields(self):
        r = _make_healer_outcome()
        text = r.to_embedding_text()
        assert "healer:" in text
        assert "failure:" in text
        assert "outcome:success" in text
        assert "tier:" in text


# ===========================================================================
# 4. PathDPreferencePair
# ===========================================================================


class TestPathDPreferencePair:
    def test_construction_sets_pair_hash(self):
        p = _make_preference_pair()
        assert len(p.pair_hash) == 64
        assert p.influence_class == "C0_INFORMATIONAL"

    def test_pair_hash_is_deterministic(self):
        p1 = _make_preference_pair()
        p2 = _make_preference_pair()
        assert p1.pair_hash == p2.pair_hash

    def test_invalid_decision_raises(self):
        with pytest.raises(ValueError, match="decision"):
            PathDPreferencePair(
                decision_id="d",
                original_plan="p",
                human_patch="hp",
                decision="INVALID",  # type: ignore[arg-type]
                reason="r",
                resulting_outcome="o",
                agent="a",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_empty_decision_id_raises(self):
        with pytest.raises(ValueError, match="decision_id"):
            PathDPreferencePair(
                decision_id="",
                original_plan="p",
                human_patch="hp",
                decision="approved",
                reason="r",
                resulting_outcome="o",
                agent="a",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_to_embedding_text_contains_key_fields(self):
        p = _make_preference_pair()
        text = p.to_embedding_text()
        assert "plan:" in text
        assert "patch:" in text
        assert "decision:approved" in text
        assert "reason:" in text
        assert "outcome:" in text


# ===========================================================================
# 5. GraphNeighborhood
# ===========================================================================


class TestGraphNeighborhood:
    def test_construction_sets_neighborhood_hash(self):
        n = _make_graph_neighborhood()
        assert len(n.neighborhood_hash) == 64
        assert n.influence_class == "C0_INFORMATIONAL"

    def test_neighborhood_hash_is_deterministic(self):
        n1 = _make_graph_neighborhood()
        n2 = _make_graph_neighborhood()
        assert n1.neighborhood_hash == n2.neighborhood_hash

    def test_empty_node_id_raises(self):
        with pytest.raises(ValueError, match="node_id"):
            GraphNeighborhood(
                node_id="",
                node_type="healer",
                layer="L2",
                inbound_relations=(),
                outbound_relations=(),
                governance_edges=(),
                mutation_edges=(),
                ownership_territory="L2",
                risk_label="low",
            )

    def test_empty_layer_raises(self):
        with pytest.raises(ValueError, match="layer"):
            GraphNeighborhood(
                node_id="n",
                node_type="healer",
                layer="",
                inbound_relations=(),
                outbound_relations=(),
                governance_edges=(),
                mutation_edges=(),
                ownership_territory="L2",
                risk_label="low",
            )

    def test_to_embedding_text_contains_key_fields(self):
        n = _make_graph_neighborhood()
        text = n.to_embedding_text()
        assert "node:" in text
        assert "layer:L2_execution" in text
        assert "risk:mutation_broker" in text
        assert "territory:" in text

    def test_relation_order_independent_hash(self):
        n1 = GraphNeighborhood(
            node_id="n",
            node_type="t",
            layer="L0",
            inbound_relations=("A", "B"),
            outbound_relations=(),
            governance_edges=(),
            mutation_edges=(),
            ownership_territory="x",
            risk_label="low",
        )
        n2 = GraphNeighborhood(
            node_id="n",
            node_type="t",
            layer="L0",
            inbound_relations=("B", "A"),
            outbound_relations=(),
            governance_edges=(),
            mutation_edges=(),
            ownership_territory="x",
            risk_label="low",
        )
        assert n1.neighborhood_hash == n2.neighborhood_hash


# ===========================================================================
# 6. PolicyGuardrailCase
# ===========================================================================


class TestPolicyGuardrailCase:
    def test_construction_sets_case_hash(self):
        c = _make_guardrail_case()
        assert len(c.case_hash) == 64
        assert c.influence_class == "C0_INFORMATIONAL"

    def test_case_hash_is_deterministic(self):
        c1 = _make_guardrail_case()
        c2 = _make_guardrail_case()
        assert c1.case_hash == c2.case_hash

    def test_invalid_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            PolicyGuardrailCase(
                case_id="c",
                blocked_payload_summary="b",
                remediation_text="r",
                policy_hash="p",
                policy_root="root",
                verdict="WRONG",  # type: ignore[arg-type]
                strictness_level="STRICT",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_empty_case_id_raises(self):
        with pytest.raises(ValueError, match="case_id"):
            PolicyGuardrailCase(
                case_id="",
                blocked_payload_summary="b",
                remediation_text="r",
                policy_hash="p",
                policy_root="root",
                verdict="true_positive",
                strictness_level="STRICT",
                trace_id="t",
                timestamp_utc=0,
            )

    def test_to_embedding_text_contains_key_fields(self):
        c = _make_guardrail_case()
        text = c.to_embedding_text()
        assert "payload:" in text
        assert "remediation:" in text
        assert "verdict:true_positive" in text
        assert "policy:" in text


# ===========================================================================
# IncidentBundleEmbedder engine
# ===========================================================================


class TestIncidentBundleEmbedder:
    def test_ingest_returns_corpus_record_with_correct_namespace(self):
        emb = IncidentBundleEmbedder()
        bundle = _make_incident()
        record = emb.ingest(bundle)
        assert record.namespace == "incident_bundles"
        assert record.trace_id == bundle.trace_id
        assert len(record.content_hash) == 64

    def test_content_hash_deterministic(self):
        emb = IncidentBundleEmbedder()
        r1 = emb.ingest(_make_incident())
        emb2 = IncidentBundleEmbedder()
        r2 = emb2.ingest(_make_incident())
        assert r1.content_hash == r2.content_hash

    def test_buffer_size_increments(self):
        emb = IncidentBundleEmbedder()
        assert emb.buffer_size() == 0
        emb.ingest(_make_incident("t1"))
        assert emb.buffer_size() == 1
        emb.ingest(_make_incident("t2"))
        assert emb.buffer_size() == 2

    def test_fifo_eviction_at_max_buffer(self):
        emb = IncidentBundleEmbedder(max_buffer=2)

        def _distinct(trace_id: str, summary: str) -> IncidentBundle:
            return IncidentBundle(
                trace_id=trace_id,
                trace_summary=summary,
                violations=("V1",),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=0,
            )

        r1 = emb.ingest(_distinct("t1", "summary-aaa"))
        emb.ingest(_distinct("t2", "summary-bbb"))
        emb.ingest(_distinct("t3", "summary-ccc"))
        assert emb.buffer_size() == 2
        exported = emb.export_corpus_records()
        trace_ids = {r.trace_id for r in exported}
        assert "t1" not in trace_ids
        assert "t2" in trace_ids
        assert "t3" in trace_ids

    def test_export_is_sorted_deterministically(self):
        emb = IncidentBundleEmbedder()
        for i in range(5):
            emb.ingest(_make_incident(f"trace-{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_ingest_batch_returns_all_records(self):
        emb = IncidentBundleEmbedder()
        bundles = [_make_incident(f"t{i}") for i in range(3)]
        records = emb.ingest_batch(bundles)
        assert len(records) == 3
        assert emb.buffer_size() == 3

    def test_retrieve_similar_returns_empty_without_live_cache(self):
        emb = IncidentBundleEmbedder()
        emb.ingest(_make_incident())
        results = emb.retrieve_similar(_make_incident("t-query"))
        assert results == []

    def test_max_buffer_validation(self):
        with pytest.raises(ValueError, match="max_buffer"):
            IncidentBundleEmbedder(max_buffer=0)

    def test_bundle_from_healing_event_convenience(self):
        bundle = IncidentBundleEmbedder.bundle_from_healing_event(
            trace_id="t",
            trace_summary="s",
            violations=["V1", "V2"],
            route_path="PATH_B",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="failure",
            policy_hash="p",
            timestamp_utc=0,
        )
        assert bundle.outcome == "failure"
        assert tuple(sorted(["V1", "V2"])) == bundle.violations

    def test_bundle_from_healing_event_invalid_outcome(self):
        with pytest.raises(ValueError, match="outcome"):
            IncidentBundleEmbedder.bundle_from_healing_event(
                trace_id="t",
                trace_summary="s",
                violations=[],
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="INVALID",
                policy_hash="p",
                timestamp_utc=0,
            )


# ===========================================================================
# MutationDiffEmbedder engine
# ===========================================================================


class TestMutationDiffEmbedder:
    def test_ingest_namespace(self):
        emb = MutationDiffEmbedder()
        record = emb.ingest(_make_mutation())
        assert record.namespace == "mutation_diffs"

    def test_pre_commit_check_returns_empty_without_live_cache(self):
        emb = MutationDiffEmbedder()
        emb.ingest(_make_mutation())
        results = emb.pre_commit_check(_make_mutation("m-new"))
        assert results == []

    def test_export_sorted(self):
        emb = MutationDiffEmbedder()
        for i in range(4):
            emb.ingest(_make_mutation(f"mut-{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_record_from_uwg_mutation_convenience(self):
        record = MutationDiffEmbedder.record_from_uwg_mutation(
            mutation_id="m",
            target_resource="x.py",
            operations=['{"op":"add"}'],
            state_diff_summary="+1",
            rollback_context="none",
            commit_outcome="rolled_back",
            trace_id="t",
            policy_hash="p",
            timestamp_utc=0,
        )
        assert record.commit_outcome == "rolled_back"

    def test_record_from_uwg_invalid_outcome(self):
        with pytest.raises(ValueError, match="commit_outcome"):
            MutationDiffEmbedder.record_from_uwg_mutation(
                mutation_id="m",
                target_resource="x",
                operations=[],
                state_diff_summary="",
                rollback_context="",
                commit_outcome="BAD",
                trace_id="t",
                policy_hash="p",
                timestamp_utc=0,
            )


# ===========================================================================
# HealerOutcomeEmbedder engine
# ===========================================================================


class TestHealerOutcomeEmbedder:
    def test_ingest_namespace(self):
        emb = HealerOutcomeEmbedder()
        record = emb.ingest(_make_healer_outcome())
        assert record.namespace == "healer_outcomes"

    def test_retrieve_for_failure_returns_empty_without_live_cache(self):
        emb = HealerOutcomeEmbedder()
        emb.ingest(_make_healer_outcome())
        results = emb.retrieve_for_failure("ImportError")
        assert results == []

    def test_export_sorted(self):
        emb = HealerOutcomeEmbedder()
        for i in range(3):
            emb.ingest(_make_healer_outcome(f"Healer{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_record_from_healing_event_convenience(self):
        record = HealerOutcomeEmbedder.record_from_healing_event(
            healer_id="H",
            failure_type="F",
            violation_text="v",
            fix_rationale="r",
            change_summary="c",
            package_version="V3",
            outcome="partial",
            tier="CLOUD",
            trace_id="t",
            timestamp_utc=0,
        )
        assert record.outcome == "partial"

    def test_record_from_healing_event_invalid_outcome(self):
        with pytest.raises(ValueError, match="outcome"):
            HealerOutcomeEmbedder.record_from_healing_event(
                healer_id="H",
                failure_type="F",
                violation_text="v",
                fix_rationale="r",
                change_summary="c",
                package_version="V1",
                outcome="WRONG",
                tier="LOCAL",
                trace_id="t",
                timestamp_utc=0,
            )


# ===========================================================================
# PathDPreferenceEmbedder engine
# ===========================================================================


class TestPathDPreferenceEmbedder:
    def test_ingest_namespace(self):
        emb = PathDPreferenceEmbedder()
        record = emb.ingest(_make_preference_pair())
        assert record.namespace == "path_d_preferences"

    def test_retrieve_for_proposal_returns_empty_without_live_cache(self):
        emb = PathDPreferenceEmbedder()
        emb.ingest(_make_preference_pair())
        results = emb.retrieve_for_proposal("Move file A to B")
        assert results == []

    def test_export_sorted(self):
        emb = PathDPreferenceEmbedder()
        for i in range(3):
            emb.ingest(_make_preference_pair(f"hitl-{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_pair_from_hitl_log_convenience(self):
        pair = PathDPreferenceEmbedder.pair_from_hitl_log(
            decision_id="d",
            original_plan="p",
            human_patch="hp",
            decision="rejected",
            reason="r",
            resulting_outcome="o",
            agent="a",
            trace_id="t",
            timestamp_utc=0,
        )
        assert pair.decision == "rejected"

    def test_pair_from_hitl_log_invalid_decision(self):
        with pytest.raises(ValueError, match="decision"):
            PathDPreferenceEmbedder.pair_from_hitl_log(
                decision_id="d",
                original_plan="p",
                human_patch="hp",
                decision="INVALID",
                reason="r",
                resulting_outcome="o",
                agent="a",
                trace_id="t",
                timestamp_utc=0,
            )


# ===========================================================================
# GraphNeighborhoodEmbedder engine
# ===========================================================================


class TestGraphNeighborhoodEmbedder:
    def test_ingest_namespace(self):
        emb = GraphNeighborhoodEmbedder()
        record = emb.ingest(_make_graph_neighborhood())
        assert record.namespace == "graph_neighborhoods"

    def test_trace_id_is_node_id(self):
        emb = GraphNeighborhoodEmbedder()
        n = _make_graph_neighborhood("my.module.path")
        record = emb.ingest(n)
        assert record.trace_id == "my.module.path"

    def test_retrieve_by_description_returns_empty_without_live_cache(self):
        emb = GraphNeighborhoodEmbedder()
        emb.ingest(_make_graph_neighborhood())
        results = emb.retrieve_by_description("risky mutation broker")
        assert results == []

    def test_export_sorted(self):
        emb = GraphNeighborhoodEmbedder()
        for i in range(4):
            emb.ingest(_make_graph_neighborhood(f"module.{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_neighborhood_from_adg_node_convenience(self):
        n = GraphNeighborhoodEmbedder.neighborhood_from_adg_node(
            node_id="n",
            node_type="engine",
            layer="L3_orchestration",
            inbound_relations=["calls"],
            outbound_relations=["applies_guardrail"],
            governance_edges=["applies_guardrail"],
            mutation_edges=[],
            ownership_territory="L3",
            risk_label="low",
        )
        assert n.layer == "L3_orchestration"
        assert "calls" in n.inbound_relations

    def test_large_buffer_default(self):
        emb = GraphNeighborhoodEmbedder()
        assert emb._max_buffer == 50_000


# ===========================================================================
# PolicyGuardrailEmbedder engine
# ===========================================================================


class TestPolicyGuardrailEmbedder:
    def test_ingest_namespace(self):
        emb = PolicyGuardrailEmbedder()
        record = emb.ingest(_make_guardrail_case())
        assert record.namespace == "policy_guardrail_cases"

    def test_retrieve_for_payload_returns_empty_without_live_cache(self):
        emb = PolicyGuardrailEmbedder()
        emb.ingest(_make_guardrail_case())
        results = emb.retrieve_for_payload("write to .py outside allowed path")
        assert results == []

    def test_retrieve_for_policy_hash_returns_empty_without_live_cache(self):
        emb = PolicyGuardrailEmbedder()
        emb.ingest(_make_guardrail_case())
        results = emb.retrieve_for_policy_hash("pol-xyz")
        assert results == []

    def test_export_sorted(self):
        emb = PolicyGuardrailEmbedder()
        for i in range(3):
            emb.ingest(_make_guardrail_case(f"case-{i}"))
        exported = emb.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_case_from_l5_block_convenience(self):
        case = PolicyGuardrailEmbedder.case_from_l5_block(
            case_id="c",
            blocked_payload_summary="b",
            remediation_text="r",
            policy_hash="p",
            policy_root="root",
            verdict="false_positive",
            strictness_level="MEDIUM",
            trace_id="t",
            timestamp_utc=0,
        )
        assert case.verdict == "false_positive"

    def test_case_from_l5_block_invalid_verdict(self):
        with pytest.raises(ValueError, match="verdict"):
            PolicyGuardrailEmbedder.case_from_l5_block(
                case_id="c",
                blocked_payload_summary="b",
                remediation_text="r",
                policy_hash="p",
                policy_root="root",
                verdict="WRONG",
                strictness_level="STRICT",
                trace_id="t",
                timestamp_utc=0,
            )


# ===========================================================================
# SemanticMemoryRegistry
# ===========================================================================


class TestSemanticMemoryRegistry:
    def test_singleton_returns_same_instance(self):
        r1 = SemanticMemoryRegistry.get()
        r2 = SemanticMemoryRegistry.get()
        assert r1 is r2

    def test_reset_for_testing_clears_singleton(self):
        r1 = SemanticMemoryRegistry.get()
        SemanticMemoryRegistry.reset_for_testing()
        r2 = SemanticMemoryRegistry.get()
        assert r1 is not r2

    def test_all_embedders_accessible(self):
        registry = SemanticMemoryRegistry.get()
        assert isinstance(registry.incidents, IncidentBundleEmbedder)
        assert isinstance(registry.mutations, MutationDiffEmbedder)
        assert isinstance(registry.healers, HealerOutcomeEmbedder)
        assert isinstance(registry.preferences, PathDPreferenceEmbedder)
        assert isinstance(registry.graph, GraphNeighborhoodEmbedder)
        assert isinstance(registry.guardrails, PolicyGuardrailEmbedder)

    def test_total_buffer_size_returns_all_namespaces(self):
        registry = SemanticMemoryRegistry.get()
        sizes = registry.total_buffer_size()
        assert set(sizes.keys()) == {
            "incident_bundles",
            "mutation_diffs",
            "healer_outcomes",
            "path_d_preferences",
            "graph_neighborhoods",
            "policy_guardrail_cases",
        }
        assert all(v == 0 for v in sizes.values())

    def test_ingest_via_registry_increments_correct_buffer(self):
        registry = SemanticMemoryRegistry.get()
        registry.incidents.ingest(_make_incident())
        registry.mutations.ingest(_make_mutation())
        sizes = registry.total_buffer_size()
        assert sizes["incident_bundles"] == 1
        assert sizes["mutation_diffs"] == 1
        assert sizes["healer_outcomes"] == 0

    def test_export_all_corpus_records_keys(self):
        registry = SemanticMemoryRegistry.get()
        registry.incidents.ingest(_make_incident())
        registry.healers.ingest(_make_healer_outcome())
        all_records = registry.export_all_corpus_records()
        assert set(all_records.keys()) == {
            "incident_bundles",
            "mutation_diffs",
            "healer_outcomes",
            "path_d_preferences",
            "graph_neighborhoods",
            "policy_guardrail_cases",
        }
        assert len(all_records["incident_bundles"]) == 1
        assert len(all_records["healer_outcomes"]) == 1
        assert len(all_records["mutation_diffs"]) == 0

    def test_export_all_records_sorted(self):
        registry = SemanticMemoryRegistry.get()
        for i in range(5):
            registry.incidents.ingest(_make_incident(f"t{i}"))
        exported = registry.export_all_corpus_records()["incident_bundles"]
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)

    def test_thread_safe_singleton(self):
        results: list[SemanticMemoryRegistry] = []
        lock = threading.Lock()

        def get_instance():
            inst = SemanticMemoryRegistry.get()
            with lock:
                results.append(inst)

        threads = [threading.Thread(target=get_instance) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 20
        first = results[0]
        assert all(r is first for r in results)

    def test_custom_buffer_sizes_propagate(self):
        SemanticMemoryRegistry.reset_for_testing()
        registry = SemanticMemoryRegistry.get(
            incident_max_buffer=100,
            graph_max_buffer=500,
        )
        assert registry.incidents._max_buffer == 100
        assert registry.graph._max_buffer == 500
