"""Unit tests for HealingOutcomeAggregator — determinism proofs.

Tests:
  - order invariance: shuffled ingest yields identical snapshot
  - window determinism: oldest-drop is deterministic
  - proposal no-op: default build_proposal returns empty/neutral proposal
  - stats rounding: stable round-half-up to 4 decimals
  - type immutability: frozen dataclasses reject mutation
"""

from __future__ import annotations

import random

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_outcome_aggregator")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_outcome_aggregator", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_outcome_aggregator", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_outcome_aggregator", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_healing_outcome_aggregator")
# REMOVED: emit_determinism_digest("p0", "test_healing_outcome_aggregator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_healing_outcome_aggregator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_outcome_aggregator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_outcome_aggregator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_outcome_aggregator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_outcome_aggregator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_outcome_aggregator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_outcome_aggregator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_outcome_aggregator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_outcome_aggregator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_outcome_aggregator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_outcome_aggregator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_outcome_aggregator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_outcome_aggregator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_outcome_aggregator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_outcome_aggregator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_outcome_aggregator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_outcome_aggregator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_outcome_aggregator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_outcome_aggregator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_outcome_aggregator", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

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
from system_learning.engines.healing_outcome_aggregator import (
    HealingOutcomeAggregator,
    InvocationRecord,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
)
from system_learning.types.healing_outcome_types import (
    HealingOutcomeEvent,
    HealingOutcomeProposal,
    HealingOutcomeStats,
)

# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_outcome_aggregator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_outcome_aggregator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_outcome_aggregator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_outcome_aggregator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_outcome_aggregator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_outcome_aggregator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_outcome_aggregator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_outcome_aggregator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_outcome_aggregator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_outcome_aggregator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_outcome_aggregator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_outcome_aggregator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_outcome_aggregator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_outcome_aggregator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_aggregator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_aggregator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_aggregator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_aggregator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_outcome_aggregator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_outcome_aggregator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_outcome_aggregator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_outcome_aggregator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_outcome_aggregator", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_outcome_aggregator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_outcome_aggregator", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_outcome_aggregator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_outcome_aggregator", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_outcome_aggregator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_outcome_aggregator", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_outcome_aggregator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_outcome_aggregator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_outcome_aggregator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_outcome_aggregator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_outcome_aggregator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_outcome_aggregator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_outcome_aggregator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_outcome_aggregator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_outcome_aggregator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_outcome_aggregator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_outcome_aggregator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_outcome_aggregator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_outcome_aggregator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_outcome_aggregator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_outcome_aggregator")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_outcome_aggregator", "confidence_gate")

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------


def _event(
    healer_id: str = "h1",
    tier: str = "LOCAL_AGENT",
    failure_type: str = "syntax_error",
    success: bool = True,
    ts: int = 1000,
    trace_id: str | None = None,
) -> HealingOutcomeEvent:
    return HealingOutcomeEvent(
        healer_id=healer_id,
        tier=tier,
        failure_type=failure_type,
        success=success,
        timestamp_utc=ts,
        trace_id=trace_id,
    )


# -------------------------------------------------------------------------
# Event contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeEvent:
    """HealingOutcomeEvent validation and immutability."""

    def test_valid_event_creation(self) -> None:
        ev = _event()
        assert ev.healer_id == "h1"
        assert ev.tier == "LOCAL_AGENT"
        assert ev.success is True

    def test_empty_healer_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="healer_id"):
            _event(healer_id="")

    def test_empty_tier_rejected(self) -> None:
        with pytest.raises(ValueError, match="tier"):
            _event(tier="")

    def test_empty_failure_type_rejected(self) -> None:
        with pytest.raises(ValueError, match="failure_type"):
            _event(failure_type="")

    def test_frozen(self) -> None:
        ev = _event()
        with pytest.raises(AttributeError):
            ev.healer_id = "changed"  # type: ignore[misc]


# -------------------------------------------------------------------------
# Stats contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeStats:
    """HealingOutcomeStats stable rounding."""

    def test_from_counts_basic(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 3, 1)
        assert stats.total_count == 4
        assert stats.success_count == 3
        assert stats.failure_count == 1
        assert stats.success_rate == 0.75

    def test_from_counts_zero_denominator(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 0, 0)
        assert stats.success_rate == 0.0

    def test_stable_rounding_half_up(self) -> None:
        # 1/3 = 0.33333... -> round-half-up to 4 decimals = 0.3333
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 1, 2)
        assert stats.success_rate == 0.3333

    def test_stable_rounding_2_of_3(self) -> None:
        # 2/3 = 0.66666... -> round-half-up to 4 decimals = 0.6667
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 2, 1)
        assert stats.success_rate == 0.6667

    def test_frozen(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 1, 0)
        with pytest.raises(AttributeError):
            stats.success_rate = 0.5  # type: ignore[misc]


# -------------------------------------------------------------------------
# Proposal contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeProposal:
    """HealingOutcomeProposal — Phase 1 no-op contract."""

    def test_default_proposal_is_empty(self) -> None:
        p = HealingOutcomeProposal()
        assert p.stats == ()
        assert p.recommended_actions == ()

    def test_frozen(self) -> None:
        p = HealingOutcomeProposal()
        with pytest.raises(AttributeError):
            p.recommended_actions = ("x",)  # type: ignore[misc]


# -------------------------------------------------------------------------
# Aggregator tests
# -------------------------------------------------------------------------


class TestAggregatorDeterminism:
    """Deterministic behaviour proofs for HealingOutcomeAggregator."""

    def test_window_size_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="window_size"):
            HealingOutcomeAggregator(window_size=0)

    def test_empty_snapshot(self) -> None:
        agg = HealingOutcomeAggregator(window_size=10)
        assert agg.snapshot() == []

    def test_single_event_snapshot(self) -> None:
        agg = HealingOutcomeAggregator(window_size=10)
        agg.ingest(_event(success=True))
        stats = agg.snapshot()
        assert len(stats) == 1
        assert stats[0].success_count == 1
        assert stats[0].failure_count == 0
        assert stats[0].success_rate == 1.0

    def test_order_invariance_shuffled_ingest_yields_identical_snapshot(self) -> None:
        """Shuffled ingest order MUST produce identical snapshot."""
        events = (
            [
                _event(healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax_error", success=True, ts=i)
                for i in range(5)
            ]
            + [
                _event(
                    healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax_error", success=False, ts=i + 100
                )
                for i in range(3)
            ]
            + [
                _event(
                    healer_id="h2", tier="QWEN_VLLM", failure_type="import_cycle", success=True, ts=i + 200
                )
                for i in range(2)
            ]
        )

        # Canonical order
        agg_canonical = HealingOutcomeAggregator(window_size=100)
        for ev in events:
            agg_canonical.ingest(ev)
        snap_canonical = agg_canonical.snapshot()

        # Shuffled order (fixed seed for reproducibility)
        rng = random.Random(42)
        shuffled = list(events)
        rng.shuffle(shuffled)
        agg_shuffled = HealingOutcomeAggregator(window_size=100)
        for ev in shuffled:
            agg_shuffled.ingest(ev)
        snap_shuffled = agg_shuffled.snapshot()

        assert snap_canonical == snap_shuffled

    def test_window_determinism_oldest_dropped(self) -> None:
        """When window overflows, oldest events are dropped deterministically."""
        agg = HealingOutcomeAggregator(window_size=3)
        agg.ingest(_event(success=True, ts=1))
        agg.ingest(_event(success=True, ts=2))
        agg.ingest(_event(success=True, ts=3))
        # Window full: 3 successes
        assert agg.snapshot()[0].success_count == 3

        # Ingest failure -> drops ts=1 (oldest success)
        agg.ingest(_event(success=False, ts=4))
        stats = agg.snapshot()
        assert len(stats) == 1
        assert stats[0].success_count == 2
        assert stats[0].failure_count == 1
        assert stats[0].total_count == 3

    def test_snapshot_sort_key(self) -> None:
        """Stats MUST be sorted by (healer_id, tier, failure_type)."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(healer_id="z_healer", tier="A_tier", failure_type="a_type"))
        agg.ingest(_event(healer_id="a_healer", tier="Z_tier", failure_type="z_type"))
        agg.ingest(_event(healer_id="a_healer", tier="A_tier", failure_type="z_type"))
        stats = agg.snapshot()
        keys = [(s.healer_id, s.tier, s.failure_type) for s in stats]
        assert keys == sorted(keys)

    def test_proposal_noop_carries_snapshot(self) -> None:
        """build_proposal returns no-op proposal with snapshot data."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(success=True))
        agg.ingest(_event(success=False))
        proposal = agg.build_proposal()
        assert isinstance(proposal, HealingOutcomeProposal)
        assert len(proposal.stats) == 1
        assert proposal.stats[0].total_count == 2
        assert proposal.recommended_actions == ()

    def test_event_count_property(self) -> None:
        agg = HealingOutcomeAggregator(window_size=5)
        assert agg.event_count == 0
        agg.ingest(_event())
        assert agg.event_count == 1
        for i in range(10):
            agg.ingest(_event(ts=i))
        assert agg.event_count == 5  # capped at window_size

    def test_multiple_keys_in_snapshot(self) -> None:
        """Multiple (healer_id, tier, failure_type) keys tracked independently."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax"))
        agg.ingest(_event(healer_id="h1", tier="QWEN_VLLM", failure_type="syntax"))
        agg.ingest(_event(healer_id="h2", tier="LOCAL_AGENT", failure_type="import"))
        stats = agg.snapshot()
        assert len(stats) == 3


# -------------------------------------------------------------------------
# Phase 6 Tests - New Learning Types
# -------------------------------------------------------------------------


class TestPhase6Aggregation:
    """Test Phase 6 functionality with new learning types."""

    def test_aggregate_deterministic_same_sequence(self):
        """Test that same sequence produces identical aggregates."""
        aggregator1 = HealingOutcomeAggregator()
        aggregator2 = HealingOutcomeAggregator()

        # Same sequence of records
        records = [
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", True, 1000),
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", False, 1001),
            InvocationRecord("healer2", "REMOTE_AGENT", "failure2", True, 1002),
        ]

        for record in records:
            aggregator1.ingest_invocation(record)
            aggregator2.ingest_invocation(record)

        # Check success rates
        key1 = HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1")
        key2 = HealingOutcomeAggregateKey("healer2", "REMOTE_AGENT", "failure2")

        assert aggregator1.compute_success_rate(key1) == 0.5
        assert aggregator2.compute_success_rate(key1) == 0.5
        assert aggregator1.compute_success_rate(key2) == 1.0
        assert aggregator2.compute_success_rate(key2) == 1.0

        # Check snapshots
        snapshot1 = aggregator1.create_snapshot(2000)
        snapshot2 = aggregator2.create_snapshot(2000)

        assert snapshot1.content_hash() == snapshot2.content_hash()
        assert len(snapshot1.aggregates) == 2
        assert len(snapshot2.aggregates) == 2

    def test_aggregate_permutation_invariant(self):
        """Test that order of ingestion doesn't affect results."""
        aggregator1 = HealingOutcomeAggregator()
        aggregator2 = HealingOutcomeAggregator()

        # Same records in different order
        records1 = [
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", True, 1000),
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", False, 1001),
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", True, 1002),
        ]

        records2 = [
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", True, 1002),
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", False, 1001),
            InvocationRecord("healer1", "LOCAL_AGENT", "failure1", True, 1000),
        ]

        for record in records1:
            aggregator1.ingest_invocation(record)

        for record in records2:
            aggregator2.ingest_invocation(record)

        # Should produce identical results
        key = HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1")
        assert aggregator1.compute_success_rate(key) == aggregator2.compute_success_rate(key)
        assert aggregator1.compute_success_rate(key) == 0.6667  # 2/3 rounded

        snapshot1 = aggregator1.create_snapshot(2000)
        snapshot2 = aggregator2.create_snapshot(2000)

        assert snapshot1.content_hash() == snapshot2.content_hash()

    def test_success_rate_correctness(self):
        """Test success rate calculations with various inputs."""
        aggregator = HealingOutcomeAggregator()

        # Test empty case
        key = HealingOutcomeAggregateKey("healer", "LOCAL_AGENT", "failure")
        assert aggregator.compute_success_rate(key) == 0.0

        # Test all successes
        for i in range(10):
            aggregator.ingest_invocation(InvocationRecord("healer", "LOCAL_AGENT", "failure", True, 1000 + i))
        assert aggregator.compute_success_rate(key) == 1.0

        # Clear and test all failures
        aggregator.clear_aggregates()
        for i in range(10):
            aggregator.ingest_invocation(
                InvocationRecord("healer", "LOCAL_AGENT", "failure", False, 1000 + i)
            )
        assert aggregator.compute_success_rate(key) == 0.0

        # Test mixed case with rounding
        aggregator.clear_aggregates()
        # 7 successes, 3 failures = 0.7
        for i in range(7):
            aggregator.ingest_invocation(InvocationRecord("healer", "LOCAL_AGENT", "failure", True, 1000 + i))
        for i in range(3):
            aggregator.ingest_invocation(
                InvocationRecord("healer", "LOCAL_AGENT", "failure", False, 1010 + i)
            )
        assert aggregator.compute_success_rate(key) == 0.7

    def test_canonical_bytes_stable(self):
        """Test that canonical_bytes produces stable output."""
        aggregate = HealingOutcomeAggregate(success_count=10, failure_count=5, total_count=15)

        bytes1 = aggregate.canonical_bytes()
        bytes2 = aggregate.canonical_bytes()

        assert bytes1 == bytes2
        assert isinstance(bytes1, bytes)

        # Verify it's valid JSON
        import json

        data = json.loads(bytes1.decode("utf-8"))
        assert data == {"success_count": 10, "failure_count": 5, "total_count": 15}
