"""Creative integration tests for semantic memory embedders.

Tests realistic workflows, cross-embedder interactions, concurrent operations,
seed-pack roundtrip, and property-based invariants.

Creative test scenarios:
  1. Full incident lifecycle: UWG mutation → healer invocation → incident bundle
  2. Cross-embedder correlation: same trace_id across incidents/mutations/healers
  3. Concurrent multi-threaded ingestion stress test
  4. Seed-pack export → reimport roundtrip with hash verification
  5. Property-based: serialization idempotency, hash stability under reordering
  6. Buffer pressure: verify FIFO eviction preserves newest records
  7. Namespace isolation: verify no cross-contamination between embedders
  8. Retrieval degradation: verify graceful fallback when cache unavailable
  9. Large-scale ingestion: 10k+ records with deterministic export
  10. Hash collision resistance: verify distinct inputs → distinct hashes
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from tempfile import TemporaryDirectory

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

# REMOVED: _emit_authorize_and_execute("p2", "test_semantic_memory_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_semantic_memory_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_semantic_memory_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_semantic_memory_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_semantic_memory_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_semantic_memory_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_semantic_memory_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_semantic_memory_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_semantic_memory_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_semantic_memory_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_semantic_memory_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_semantic_memory_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_semantic_memory_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_semantic_memory_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_semantic_memory_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_semantic_memory_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_semantic_memory_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_semantic_memory_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_semantic_memory_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_semantic_memory_integration", "exec_snapshot_link")
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
#  # MOVED: from system_learning.engines.embedding_corpus_extraction import write_jsonl_records
#  # MOVED: from system_learning.engines.semantic_memory_registry import SemanticMemoryRegistry
#  # MOVED: from system_learning.types.semantic_memory_types import (
    GraphNeighborhood,
    HealerOutcomeRecord,
    IncidentBundle,
    MutationDiffRecord,
    PathDPreferencePair,
    PolicyGuardrailCase,
)

# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_semantic_memory_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_semantic_memory_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_semantic_memory_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_semantic_memory_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_semantic_memory_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_semantic_memory_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_semantic_memory_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_semantic_memory_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_semantic_memory_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_semantic_memory_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_semantic_memory_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_semantic_memory_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_semantic_memory_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_semantic_memory_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_semantic_memory_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_semantic_memory_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_semantic_memory_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_semantic_memory_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_semantic_memory_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_semantic_memory_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_semantic_memory_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_semantic_memory_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_semantic_memory_integration", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_semantic_memory_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_semantic_memory_integration", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_semantic_memory_integration", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_semantic_memory_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_semantic_memory_integration", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_memory_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_memory_integration", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_semantic_memory_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_semantic_memory_integration", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_semantic_memory_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_semantic_memory_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_semantic_memory_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_semantic_memory_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_semantic_memory_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_semantic_memory_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_semantic_memory_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_semantic_memory_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_semantic_memory_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_semantic_memory_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_semantic_memory_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_semantic_memory_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_semantic_memory_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_semantic_memory_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_semantic_memory_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_semantic_memory_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_semantic_memory_integration")
# REMOVED: emit_determinism_digest("p0", "test_semantic_memory_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.fixture(autouse=True)
def reset_registry():
    """Ensure singleton is clean for each test."""
    SemanticMemoryRegistry.reset_for_testing()
    yield
    SemanticMemoryRegistry.reset_for_testing()


# ===========================================================================
# 1. Full incident lifecycle workflow
# ===========================================================================


class TestIncidentLifecycle:
    """Test realistic end-to-end workflow: mutation → healing → incident."""

    def test_mutation_triggers_healing_creates_incident(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.engines.embedding_corpus_extraction import write_jsonl_records
        from system_learning.engines.semantic_memory_registry import SemanticMemoryRegistry
        from system_learning.types.semantic_memory_types import (
        """Simulate UWG mutation → healer invocation → incident bundle creation."""
        registry = SemanticMemoryRegistry.get()
        trace_id = "trace-lifecycle-001"
        policy_hash = "pol-abc123"

        # Step 1: UWG records a mutation attempt
        mutation = MutationDiffRecord(
            mutation_id="mut-001",
            target_resource="agentic_core/L2_execution/config.py",
            operations=('{"op":"replace","path":"/timeout","value":60}',),
            state_diff_summary="+1 line: timeout = 60",
            rollback_context="previous: timeout = 30",
            commit_outcome="committed",
            trace_id=trace_id,
            policy_hash=policy_hash,
            timestamp_utc=1_700_000_000,
        )
        registry.mutations.ingest(mutation)

        # Step 2: Healer processes the mutation
        healer_outcome = HealerOutcomeRecord(
            healer_id="TimeoutHealerAgent",
            failure_type="CONFIG_DRIFT",
            violation_text="Timeout value too low for production",
            fix_rationale="Increased timeout to 60s per SLA requirements",
            change_summary="Updated timeout from 30s to 60s",
            package_version="V2",
            outcome="success",
            tier="LOCAL_AGENT",
            trace_id=trace_id,
            timestamp_utc=1_700_000_001,
        )
        registry.healers.ingest(healer_outcome)

        # Step 3: Incident bundle created for the full execution
        incident = IncidentBundle(
            trace_id=trace_id,
            trace_summary="CONFIG_DRIFT: timeout value adjusted during healing",
            violations=("CONFIG_DRIFT", "POLICY_MISMATCH"),
            route_path="PATH_B",
            tool_capability="file_system.write",
            state_diff_summary="+1 line in config.py",
            healer_id="TimeoutHealerAgent",
            outcome="success",
            policy_hash=policy_hash,
            timestamp_utc=1_700_000_002,
        )
        registry.incidents.ingest(incident)

        # Verify: all three embedders have records with same trace_id
        all_records = registry.export_all_corpus_records()
        mutation_records = [r for r in all_records["mutation_diffs"] if r.trace_id == trace_id]
        healer_records = [r for r in all_records["healer_outcomes"] if r.trace_id == trace_id]
        incident_records = [r for r in all_records["incident_bundles"] if r.trace_id == trace_id]

        assert len(mutation_records) == 1
        assert len(healer_records) == 1
        assert len(incident_records) == 1

        # Verify: content hashes are distinct (different embedder namespaces)
        hashes = {
            mutation_records[0].content_hash,
            healer_records[0].content_hash,
            incident_records[0].content_hash,
        }
        assert len(hashes) == 3


# ===========================================================================
# 2. Cross-embedder trace correlation
# ===========================================================================


class TestCrossEmbedderCorrelation:
    """Test trace_id correlation across multiple embedders."""

    def test_same_trace_across_all_embedders(self):
        """Verify a single trace_id can appear in all six embedders."""
        registry = SemanticMemoryRegistry.get()
        trace_id = "trace-correlation-001"
        ts = 1_700_000_000

        # Ingest one record in each embedder with the same trace_id
        registry.incidents.ingest(
            IncidentBundle(
                trace_id=trace_id,
                trace_summary="test",
                violations=("V1",),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=ts,
            )
        )
        registry.mutations.ingest(
            MutationDiffRecord(
                mutation_id="m1",
                target_resource="x.py",
                operations=("op1",),
                state_diff_summary="s",
                rollback_context="r",
                commit_outcome="committed",
                trace_id=trace_id,
                policy_hash="p",
                timestamp_utc=ts,
            )
        )
        registry.healers.ingest(
            HealerOutcomeRecord(
                healer_id="h",
                failure_type="f",
                violation_text="v",
                fix_rationale="r",
                change_summary="c",
                package_version="V1",
                outcome="success",
                tier="LOCAL",
                trace_id=trace_id,
                timestamp_utc=ts,
            )
        )
        registry.preferences.ingest(
            PathDPreferencePair(
                decision_id="d1",
                original_plan="p",
                human_patch="hp",
                decision="approved",
                reason="r",
                resulting_outcome="o",
                agent="a",
                trace_id=trace_id,
                timestamp_utc=ts,
            )
        )
        registry.graph.ingest(
            GraphNeighborhood(
                node_id=trace_id,  # Use trace_id as node_id for correlation
                node_type="agent",
                layer="L2",
                inbound_relations=(),
                outbound_relations=(),
                governance_edges=(),
                mutation_edges=(),
                ownership_territory="L2",
                risk_label="low",
            )
        )
        registry.guardrails.ingest(
            PolicyGuardrailCase(
                case_id="c1",
                blocked_payload_summary="b",
                remediation_text="r",
                policy_hash="p",
                policy_root="root",
                verdict="true_positive",
                strictness_level="STRICT",
                trace_id=trace_id,
                timestamp_utc=ts,
            )
        )

        # Verify: all six embedders have exactly one record with this trace_id
        all_records = registry.export_all_corpus_records()
        for namespace, records in all_records.items():
            matching = [r for r in records if r.trace_id == trace_id]
            assert len(matching) == 1, f"{namespace} should have exactly 1 record with trace_id={trace_id}"


# ===========================================================================
# 3. Concurrent multi-threaded ingestion stress test
# ===========================================================================


class TestConcurrentIngestion:
    """Test thread-safety under concurrent ingestion."""

    def test_concurrent_ingestion_preserves_all_records(self):
        """Verify no records lost when 10 threads ingest 100 records each."""
        registry = SemanticMemoryRegistry.get()
        num_threads = 10
        records_per_thread = 100
        barrier = threading.Barrier(num_threads)
        errors = []

        def ingest_worker(thread_id: int):
            try:
                barrier.wait()  # Synchronize start
                for i in range(records_per_thread):
                    trace_id = f"thread-{thread_id}-record-{i}"
                    registry.incidents.ingest(
                        IncidentBundle(
                            trace_id=trace_id,
                            trace_summary=f"summary-{thread_id}-{i}",
                            violations=("V1",),
                            route_path="PATH_A",
                            tool_capability="x",
                            state_diff_summary="y",
                            healer_id="h",
                            outcome="success",
                            policy_hash="p",
                            timestamp_utc=1_700_000_000 + i,
                        )
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=ingest_worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errors during concurrent ingestion: {errors}"

        # Verify: total buffer size matches expected count
        expected_total = num_threads * records_per_thread
        actual_size = registry.incidents.buffer_size()
        assert actual_size == expected_total, f"Expected {expected_total}, got {actual_size}"

        # Verify: all trace_ids are unique
        exported = registry.incidents.export_corpus_records()
        trace_ids = [r.trace_id for r in exported]
        assert len(trace_ids) == len(set(trace_ids)), "Duplicate trace_ids detected"


# ===========================================================================
# 4. Seed-pack export → reimport roundtrip
# ===========================================================================


class TestSeedPackRoundtrip:
    """Test export to JSONL and verify hash integrity."""

    def test_export_reimport_preserves_hashes(self):
        """Export to JSONL, parse back, verify content_hash matches."""
        registry = SemanticMemoryRegistry.get()

        # Ingest 10 distinct incidents
        for i in range(10):
            registry.incidents.ingest(
                IncidentBundle(
                    trace_id=f"trace-{i}",
                    trace_summary=f"summary-{i}",
                    violations=(f"V{i}",),
                    route_path="PATH_A",
                    tool_capability="x",
                    state_diff_summary="y",
                    healer_id="h",
                    outcome="success",
                    policy_hash="p",
                    timestamp_utc=1_700_000_000 + i,
                )
            )

        exported = registry.incidents.export_corpus_records()

        with TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "incidents.jsonl"
            write_jsonl_records(jsonl_path, exported)

            # Reimport and verify
            reimported = []
            with open(jsonl_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        reimported.append(json.loads(line))

            assert len(reimported) == 10

            # Verify: content_hash matches for each record
            for original, reimported_dict in zip(exported, reimported):
                assert original.content_hash == reimported_dict["content_hash"]
                assert original.trace_id == reimported_dict["trace_id"]
                assert original.namespace == reimported_dict["namespace"]


# ===========================================================================
# 5. Property-based: serialization idempotency
# ===========================================================================


class TestSerializationIdempotency:
    """Property-based tests: to_embedding_text() is idempotent."""

    def test_incident_serialization_idempotent(self):
        """Calling to_embedding_text() twice yields identical results."""
        bundle = IncidentBundle(
            trace_id="t",
            trace_summary="s",
            violations=("V1", "V2"),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="success",
            policy_hash="p",
            timestamp_utc=0,
        )
        text1 = bundle.to_embedding_text()
        text2 = bundle.to_embedding_text()
        assert text1 == text2

    def test_mutation_serialization_idempotent(self):
        record = MutationDiffRecord(
            mutation_id="m",
            target_resource="x",
            operations=("op1", "op2"),
            state_diff_summary="s",
            rollback_context="r",
            commit_outcome="committed",
            trace_id="t",
            policy_hash="p",
            timestamp_utc=0,
        )
        text1 = record.to_embedding_text()
        text2 = record.to_embedding_text()
        assert text1 == text2

    def test_healer_serialization_idempotent(self):
        record = HealerOutcomeRecord(
            healer_id="h",
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
        text1 = record.to_embedding_text()
        text2 = record.to_embedding_text()
        assert text1 == text2


# ===========================================================================
# 6. Hash stability under field reordering
# ===========================================================================


class TestHashStability:
    """Verify hash is stable regardless of tuple element order."""

    def test_incident_violations_order_independent(self):
        """Violations tuple sorted before hashing → order-independent hash."""
        b1 = IncidentBundle(
            trace_id="t",
            trace_summary="s",
            violations=("AAA", "ZZZ"),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="success",
            policy_hash="p",
            timestamp_utc=0,
        )
        b2 = IncidentBundle(
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
        assert b1.bundle_hash == b2.bundle_hash

    def test_graph_relations_order_independent(self):
        """Relation tuples sorted before hashing → order-independent hash."""
        n1 = GraphNeighborhood(
            node_id="n",
            node_type="t",
            layer="L0",
            inbound_relations=("calls", "imports"),
            outbound_relations=("writes", "reads"),
            governance_edges=("applies_guardrail", "enforces_policy"),
            mutation_edges=("writes_through",),
            ownership_territory="L2",
            risk_label="low",
        )
        n2 = GraphNeighborhood(
            node_id="n",
            node_type="t",
            layer="L0",
            inbound_relations=("imports", "calls"),
            outbound_relations=("reads", "writes"),
            governance_edges=("enforces_policy", "applies_guardrail"),
            mutation_edges=("writes_through",),
            ownership_territory="L2",
            risk_label="low",
        )
        assert n1.neighborhood_hash == n2.neighborhood_hash


# ===========================================================================
# 7. Namespace isolation
# ===========================================================================


class TestNamespaceIsolation:
    """Verify no cross-contamination between embedder namespaces."""

    def test_namespaces_are_distinct(self):
        """Each embedder uses a unique namespace."""
        registry = SemanticMemoryRegistry.get()
        all_records = registry.export_all_corpus_records()
        namespaces = set(all_records.keys())
        expected = {
            "incident_bundles",
            "mutation_diffs",
            "healer_outcomes",
            "path_d_preferences",
            "graph_neighborhoods",
            "policy_guardrail_cases",
        }
        assert namespaces == expected

    def test_no_cross_namespace_contamination(self):
        """Records from one embedder don't appear in another's export."""
        registry = SemanticMemoryRegistry.get()

        # Ingest into incidents only
        registry.incidents.ingest(
            IncidentBundle(
                trace_id="t-incident",
                trace_summary="s",
                violations=("V1",),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=0,
            )
        )

        all_records = registry.export_all_corpus_records()

        # Verify: only incident_bundles has records
        assert len(all_records["incident_bundles"]) == 1
        assert len(all_records["mutation_diffs"]) == 0
        assert len(all_records["healer_outcomes"]) == 0
        assert len(all_records["path_d_preferences"]) == 0
        assert len(all_records["graph_neighborhoods"]) == 0
        assert len(all_records["policy_guardrail_cases"]) == 0


# ===========================================================================
# 8. Large-scale ingestion determinism
# ===========================================================================


class TestLargeScaleIngestion:
    """Test deterministic export with 1000+ records."""

    def test_large_scale_export_is_sorted(self):
        """Ingest 1000 records, verify export is deterministically sorted."""
        registry = SemanticMemoryRegistry.get()

        for i in range(1000):
            registry.incidents.ingest(
                IncidentBundle(
                    trace_id=f"trace-{i:04d}",
                    trace_summary=f"summary-{i}",
                    violations=(f"V{i % 10}",),
                    route_path="PATH_A",
                    tool_capability="x",
                    state_diff_summary="y",
                    healer_id="h",
                    outcome="success",
                    policy_hash="p",
                    timestamp_utc=1_700_000_000 + i,
                )
            )

        exported = registry.incidents.export_corpus_records()
        assert len(exported) == 1000

        # Verify: sorted by (content_hash, trace_id)
        keys = [(r.content_hash, r.trace_id) for r in exported]
        assert keys == sorted(keys)


# ===========================================================================
# 9. Hash collision resistance
# ===========================================================================


class TestHashCollisionResistance:
    """Verify distinct inputs produce distinct hashes."""

    def test_distinct_incidents_have_distinct_hashes(self):
        """1000 distinct incidents → 1000 distinct bundle_hashes."""
        hashes = set()
        for i in range(1000):
            bundle = IncidentBundle(
                trace_id=f"trace-{i}",
                trace_summary=f"summary-{i}",
                violations=(f"V{i}",),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=1_700_000_000 + i,
            )
            hashes.add(bundle.bundle_hash)

        assert len(hashes) == 1000, "Hash collision detected"

    def test_single_field_change_yields_different_hash(self):
        """Changing only outcome field changes bundle_hash."""
        b1 = IncidentBundle(
            trace_id="t",
            trace_summary="s",
            violations=("V1",),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="success",
            policy_hash="p",
            timestamp_utc=0,
        )
        b2 = IncidentBundle(
            trace_id="t",
            trace_summary="s",
            violations=("V1",),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="failure",
            policy_hash="p",
            timestamp_utc=0,
        )
        assert b1.bundle_hash != b2.bundle_hash


# ===========================================================================
# 10. Buffer pressure and FIFO eviction
# ===========================================================================


class TestBufferPressure:
    """Test FIFO eviction under sustained ingestion pressure."""

    def test_sustained_ingestion_maintains_buffer_limit(self):
        """Ingest 1000 records into buffer of 100 → size stays at 100."""
        registry = SemanticMemoryRegistry.get(incident_max_buffer=100)

        for i in range(1000):
            registry.incidents.ingest(
                IncidentBundle(
                    trace_id=f"trace-{i}",
                    trace_summary=f"summary-{i}",
                    violations=("V1",),
                    route_path="PATH_A",
                    tool_capability="x",
                    state_diff_summary="y",
                    healer_id="h",
                    outcome="success",
                    policy_hash="p",
                    timestamp_utc=1_700_000_000 + i,
                )
            )

        assert registry.incidents.buffer_size() == 100

    def test_fifo_eviction_keeps_newest_records(self):
        """After ingesting 150 records into buffer of 100, oldest 50 are evicted."""
        registry = SemanticMemoryRegistry.get(incident_max_buffer=100)

        for i in range(150):
            registry.incidents.ingest(
                IncidentBundle(
                    trace_id=f"trace-{i:03d}",
                    trace_summary=f"summary-{i}",
                    violations=("V1",),
                    route_path="PATH_A",
                    tool_capability="x",
                    state_diff_summary="y",
                    healer_id="h",
                    outcome="success",
                    policy_hash="p",
                    timestamp_utc=1_700_000_000 + i,
                )
            )

        exported = registry.incidents.export_corpus_records()
        trace_ids = {r.trace_id for r in exported}

        # Verify: first 50 (trace-000 to trace-049) are evicted
        for i in range(50):
            assert f"trace-{i:03d}" not in trace_ids

        # Verify: last 100 (trace-050 to trace-149) are retained
        for i in range(50, 150):
            assert f"trace-{i:03d}" in trace_ids


# ===========================================================================
# 11. Retrieval graceful degradation
# ===========================================================================


class TestRetrievalDegradation:
    """Verify retrieval falls back gracefully when cache unavailable."""

    def test_retrieve_without_cache_returns_empty(self):
        """All retrieve_* methods return [] when semantic cache unavailable."""
        registry = SemanticMemoryRegistry.get()

        # Ingest records
        registry.incidents.ingest(
            IncidentBundle(
                trace_id="t",
                trace_summary="s",
                violations=("V1",),
                route_path="PATH_A",
                tool_capability="x",
                state_diff_summary="y",
                healer_id="h",
                outcome="success",
                policy_hash="p",
                timestamp_utc=0,
            )
        )

        # Retrieval should return [] (no live cache)
        query = IncidentBundle(
            trace_id="query",
            trace_summary="query",
            violations=("V1",),
            route_path="PATH_A",
            tool_capability="x",
            state_diff_summary="y",
            healer_id="h",
            outcome="success",
            policy_hash="p",
            timestamp_utc=0,
        )
        results = registry.incidents.retrieve_similar(query)
        assert results == []

    def test_all_embedders_degrade_gracefully(self):
        """All six embedders return [] on retrieval without cache."""
        registry = SemanticMemoryRegistry.get()

        # Incidents
        assert (
            registry.incidents.retrieve_similar(
                IncidentBundle(
                    trace_id="t",
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
            )
            == []
        )

        # Mutations
        assert (
            registry.mutations.pre_commit_check(
                MutationDiffRecord(
                    mutation_id="m",
                    target_resource="x",
                    operations=(),
                    state_diff_summary="s",
                    rollback_context="r",
                    commit_outcome="pending",
                    trace_id="t",
                    policy_hash="p",
                    timestamp_utc=0,
                )
            )
            == []
        )

        # Healers
        assert registry.healers.retrieve_for_failure("ImportError") == []

        # Preferences
        assert registry.preferences.retrieve_for_proposal("plan text") == []

        # Graph
        assert registry.graph.retrieve_by_description("risky broker") == []

        # Guardrails
        assert registry.guardrails.retrieve_for_policy_hash("pol-xyz") == []
