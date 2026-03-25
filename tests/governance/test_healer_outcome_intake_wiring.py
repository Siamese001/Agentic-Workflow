"""
Integration tests for L2 healer → system_learning outcome intake wiring (G17).

Verifies:
- HealingOutcomeAggregator → HealingOutcomeIntakeAdapter → InMemory store pipeline
- build_record produces deterministically sorted snapshots
- persist_record writes to store
- empty aggregator raises (snapshot cannot be empty)
- duplicate persist is additive (store grows)
- schema_version, window_size, source all correct
- determinism: identical aggregator state → identical record
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

# REMOVED: _emit_authorize_and_execute("p2", "test_healer_outcome_intake_wiring", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healer_outcome_intake_wiring", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healer_outcome_intake_wiring", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healer_outcome_intake_wiring", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healer_outcome_intake_wiring", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healer_outcome_intake_wiring", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healer_outcome_intake_wiring", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healer_outcome_intake_wiring", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healer_outcome_intake_wiring", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healer_outcome_intake_wiring", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healer_outcome_intake_wiring", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healer_outcome_intake_wiring", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healer_outcome_intake_wiring", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healer_outcome_intake_wiring", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healer_outcome_intake_wiring", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healer_outcome_intake_wiring", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healer_outcome_intake_wiring", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healer_outcome_intake_wiring", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healer_outcome_intake_wiring", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healer_outcome_intake_wiring", "exec_snapshot_link")
from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
from system_learning.types.healing_outcome_types import HealingOutcomeEvent

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healer_outcome_intake_wiring")
# REMOVED: _emit_applies_guardrail("p0", "test_healer_outcome_intake_wiring", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healer_outcome_intake_wiring", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healer_outcome_intake_wiring", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healer_outcome_intake_wiring", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healer_outcome_intake_wiring", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healer_outcome_intake_wiring", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healer_outcome_intake_wiring", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healer_outcome_intake_wiring", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healer_outcome_intake_wiring", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healer_outcome_intake_wiring", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healer_outcome_intake_wiring", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healer_outcome_intake_wiring", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healer_outcome_intake_wiring", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healer_outcome_intake_wiring", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healer_outcome_intake_wiring", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healer_outcome_intake_wiring", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healer_outcome_intake_wiring", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healer_outcome_intake_wiring", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healer_outcome_intake_wiring", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healer_outcome_intake_wiring", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healer_outcome_intake_wiring", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healer_outcome_intake_wiring", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healer_outcome_intake_wiring", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healer_outcome_intake_wiring", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healer_outcome_intake_wiring", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healer_outcome_intake_wiring", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healer_outcome_intake_wiring", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healer_outcome_intake_wiring", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healer_outcome_intake_wiring", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healer_outcome_intake_wiring", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healer_outcome_intake_wiring", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healer_outcome_intake_wiring", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healer_outcome_intake_wiring", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healer_outcome_intake_wiring", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healer_outcome_intake_wiring", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healer_outcome_intake_wiring", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healer_outcome_intake_wiring", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healer_outcome_intake_wiring", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healer_outcome_intake_wiring", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healer_outcome_intake_wiring", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healer_outcome_intake_wiring", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healer_outcome_intake_wiring", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healer_outcome_intake_wiring", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healer_outcome_intake_wiring", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healer_outcome_intake_wiring", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healer_outcome_intake_wiring", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healer_outcome_intake_wiring")
# REMOVED: _emit_gated_by_confidence("p1", "test_healer_outcome_intake_wiring", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healer_outcome_intake_wiring")
# REMOVED: emit_determinism_digest("p0", "test_healer_outcome_intake_wiring")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# In-memory store for testing (implements write() protocol)
# ---------------------------------------------------------------------------


class InMemoryHealingOutcomeIntakeStore(HealingOutcomeIntakeStore):
    """Simple in-memory store for tests."""

    def __init__(self):
        self._records = []

    def write(self, record):
        self._records.append(record)

    def read_all(self):
        return list(self._records)

    def count(self):
        return len(self._records)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_event(healer_id="healer_1", tier="T1", failure_type="OOM", success=True):
    return HealingOutcomeEvent(
        healer_id=healer_id,
        tier=tier,
        failure_type=failure_type,
        success=success,
        timestamp_utc=1234567890,
        trace_id="trace_001",
    )


def _populated_aggregator():
    agg = HealingOutcomeAggregator()
    agg.ingest(_make_event("healer_b", "T2", "IMPORT_ERROR", success=True))
    agg.ingest(_make_event("healer_a", "T1", "OOM", success=True))
    agg.ingest(_make_event("healer_a", "T1", "OOM", success=False))
    return agg


# ---------------------------------------------------------------------------
# TestAdapterBuildRecord
# ---------------------------------------------------------------------------


class TestAdapterBuildRecord:
    def test_build_record_returns_intake_record(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord

        assert isinstance(record, HealingOutcomeIntakeRecord)

    def test_build_record_schema_version_is_1(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.schema_version == 1

    def test_build_record_window_size_matches_snapshot_length(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.window_size == len(record.snapshot)

    def test_build_record_created_utc_matches_argument(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=9999999)
        assert record.created_utc == 9999999

    def test_build_record_default_source(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.source == "L2.3-healing"

    def test_build_record_custom_source(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000, source="test-source")
        assert record.source == "test-source"

    def test_build_record_snapshot_is_deterministically_sorted(self):
        """Snapshot entries must be sorted by (healer_id, tier, failure_type)."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        snap = record.snapshot
        sorted_snap = tuple(sorted(snap, key=lambda s: (s.healer_id, s.tier, s.failure_type)))
        assert snap == sorted_snap

    def test_build_record_deterministic_for_identical_aggregator(self):
        """Same aggregator state → same record content (no wall-clock)."""
        store1 = InMemoryHealingOutcomeIntakeStore()
        store2 = InMemoryHealingOutcomeIntakeStore()
        adapter1 = HealingOutcomeIntakeAdapter(store1)
        adapter2 = HealingOutcomeIntakeAdapter(store2)

        agg1 = _populated_aggregator()
        agg2 = _populated_aggregator()

        r1 = adapter1.build_record(agg1, created_utc=5000)
        r2 = adapter2.build_record(agg2, created_utc=5000)

        assert r1.window_size == r2.window_size
        assert r1.snapshot == r2.snapshot
        assert r1.schema_version == r2.schema_version


# ---------------------------------------------------------------------------
# TestAdapterPersistRecord
# ---------------------------------------------------------------------------


class TestAdapterPersistRecord:
    def test_persist_record_writes_to_store(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        adapter.persist_record(record)
        assert store.count() == 1

    def test_persist_record_multiple_writes_additive(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        for i in range(3):
            record = adapter.build_record(agg, created_utc=1000 + i)
            adapter.persist_record(record)
        assert store.count() == 3

    def test_persisted_record_retrievable(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=42)
        adapter.persist_record(record)
        retrieved = store.read_all()[0]
        assert retrieved.created_utc == 42
        assert retrieved.schema_version == 1

    def test_store_write_called_once_per_persist(self):
        from unittest.mock import MagicMock

        store_mock = MagicMock(spec=HealingOutcomeIntakeStore)
        adapter = HealingOutcomeIntakeAdapter(store_mock)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1)
        adapter.persist_record(record)
        store_mock.write.assert_called_once_with(record)


# ---------------------------------------------------------------------------
# TestEmptyAggregatorRejection
# ---------------------------------------------------------------------------


class TestEmptyAggregatorRejection:
    def test_empty_aggregator_build_record_raises_value_error(self):
        """Empty aggregator has window_size=0 after snapshot, which is invalid."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        empty_agg = HealingOutcomeAggregator()
        # Empty snapshot → window_size=0 → HealingOutcomeIntakeRecord.__post_init__ raises
        with pytest.raises(ValueError):
            adapter.build_record(empty_agg, created_utc=0)


# ---------------------------------------------------------------------------
# TestFullPipeline
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_full_pipeline_healer_to_store(self):
        """End-to-end: ingest events → aggregate → build record → persist."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        agg = HealingOutcomeAggregator()
        # Ingest 5 events for two healers
        for _ in range(3):
            agg.ingest(_make_event("healer_x", "T1", "TIMEOUT", success=True))
        for _ in range(2):
            agg.ingest(_make_event("healer_x", "T1", "TIMEOUT", success=False))
        agg.ingest(_make_event("healer_y", "T3", "OOM", success=True))

        record = adapter.build_record(agg, created_utc=2000, source="test-pipeline")
        adapter.persist_record(record)

        assert store.count() == 1
        r = store.read_all()[0]
        assert r.source == "test-pipeline"
        assert r.window_size >= 1
        # healer_x stats should show 3 successes, 2 failures
        healer_x_stats = [s for s in r.snapshot if s.healer_id == "healer_x"]
        assert len(healer_x_stats) == 1
        assert healer_x_stats[0].success_count == 3
        assert healer_x_stats[0].failure_count == 2
