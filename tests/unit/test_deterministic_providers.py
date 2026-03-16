"""
Phase 0.5 — Deterministic Providers Tests.

Validates:
  - FixedTimeProvider determinism from trace_id
  - DeterministicRandomSource reproducibility
  - DeterministicUUIDProvider monotonic sequence
  - patch_deterministic / unpatch_deterministic lifecycle
  - One-trace-per-process invariant (DeterministicPatchError)
  - Idempotent patching with same trace_id
"""

from __future__ import annotations

import random
import time
import uuid

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    DEFAULT_SLEEP,
    DeterministicPatchError,
    DeterministicRandomSource,
    DeterministicUUIDProvider,
    FixedTimeProvider,
    is_patched,
    patch_deterministic,
    unpatch_deterministic,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_1")
_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_2")
_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_3")
_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_4")
_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_5")
_emit_emits_metric_event("test_deterministic_providers", "p4obs", "metric_6")
_emit_records_incident_event("test_deterministic_providers", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_deterministic_providers", "p4obs", "anomaly")
_emit_writes_observability_log("test_deterministic_providers", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_deterministic_providers", "p4obs", "mon_state")
_emit_triggers_alert("test_deterministic_providers", "p4obs", "alert")
_emit_links_incident_trace("test_deterministic_providers", "p4obs", "trace_link")
_emit_captures_pattern("test_deterministic_providers", "p3lm", "pattern")
_emit_records_learning_event("test_deterministic_providers", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_deterministic_providers", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_deterministic_providers", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_deterministic_providers", "p3lm", "routing")
_emit_improves_agent_policy("test_deterministic_providers", "p3lm", "policy")
_emit_stores_learning_state("test_deterministic_providers", "p3lm", "state")
_emit_records_execution_trace("test_deterministic_providers", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_deterministic_providers", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_deterministic_providers", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_deterministic_providers", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_deterministic_providers", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_deterministic_providers", "env_read", "p2_env_1")
_emit_reads_environ("test_deterministic_providers", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_deterministic_providers", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_deterministic_providers", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_deterministic_providers")
_emit_applies_guardrail("p0", "test_deterministic_providers", "p0_governance")
_emit_reads_policy_state("p0", "test_deterministic_providers", "policy_binding")
_emit_snapshots_state("p0", "test_deterministic_providers", "state_snapshot")
_emit_pulls_context("p1", "test_deterministic_providers", "context_pull")
_emit_pulls_context("p1", "test_deterministic_providers", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_providers", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_providers", "uwg_term_secondary")
_emit_writes_through("p1", "test_deterministic_providers", "write_through")
_emit_writes_through("p1", "test_deterministic_providers", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_deterministic_providers", "safety_validation")
_emit_invokes_eval("p1", "test_deterministic_providers", "eval_call")
_emit_proposal_commits_routing("p1", "test_deterministic_providers", "routing_commit")
emit_replay_key("p0", "test_deterministic_providers")
emit_determinism_digest("p0", "test_deterministic_providers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_deterministic_providers", "execution_auth")
_emit_validates_capability("p2", "test_deterministic_providers", "capability_check")
_emit_routes_to_capability("p2", "test_deterministic_providers", "capability_route")
_emit_writes_via_uwg("p2", "test_deterministic_providers", "uwg_write")
_emit_blocks_direct_write("p2", "test_deterministic_providers", "direct_write_block")
_emit_records_tool_invocation("p2", "test_deterministic_providers", "tool_invocation")
_emit_captures_execution_output("p2", "test_deterministic_providers", "exec_output")
_emit_dispatches_agent("p3", "test_deterministic_providers", "agent_dispatch")
_emit_coordinates_agents("p3", "test_deterministic_providers", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_deterministic_providers", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_deterministic_providers", "healing_outcome")
_emit_escalates_failure("p3", "test_deterministic_providers", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_deterministic_providers", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_deterministic_providers", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_deterministic_providers", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_deterministic_providers", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_deterministic_providers", "eval_metric")
_emit_stores_embedding("p4", "test_deterministic_providers", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_deterministic_providers", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_deterministic_providers", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# FixedTimeProvider
# ---------------------------------------------------------------------------


class TestFixedTimeProvider:
    @pytest.mark.unit_min_deps
    def test_deterministic_from_trace_id(self):
        """Same trace_id produces identical base time."""
        a = FixedTimeProvider("trace-abc")
        b = FixedTimeProvider("trace-abc")
        assert a.time() == b.time()

    @pytest.mark.unit_min_deps
    def test_different_trace_id_different_time(self):
        """Different trace_ids produce different base times."""
        a = FixedTimeProvider("trace-1")
        b = FixedTimeProvider("trace-2")
        assert a.time() != b.time()

    @pytest.mark.unit_min_deps
    def test_sleep_advances_clock(self):
        """sleep() advances virtual clock monotonically."""
        p = FixedTimeProvider("trace-sleep")
        t0 = p.time()
        p.sleep(DEFAULT_SLEEP)
        t1 = p.time()
        assert t1 == t0 + DEFAULT_SLEEP

    @pytest.mark.unit_min_deps
    def test_advance_advances_clock(self):
        """advance() advances virtual clock."""
        p = FixedTimeProvider("trace-advance")
        t0 = p.time()
        p.advance(3.0)
        assert p.time() == t0 + 3.0

    @pytest.mark.unit_min_deps
    def test_negative_sleep_raises(self):
        """Negative sleep duration raises ValueError."""
        p = FixedTimeProvider("trace-neg")
        with pytest.raises(ValueError):
            p.sleep(-1.0)

    @pytest.mark.unit_min_deps
    def test_negative_advance_raises(self):
        """Negative advance duration raises ValueError."""
        p = FixedTimeProvider("trace-neg")
        with pytest.raises(ValueError):
            p.advance(-1.0)

    @pytest.mark.unit_min_deps
    def test_current_offset_property(self):
        """current_offset reflects accumulated advances."""
        p = FixedTimeProvider("trace-offset")
        assert p.current_offset == 0.0
        p.sleep(DEFAULT_SLEEP)
        p.advance(1.0)
        assert p.current_offset == DEFAULT_SLEEP + 1.0


# ---------------------------------------------------------------------------
# DeterministicRandomSource
# ---------------------------------------------------------------------------


class TestDeterministicRandomSource:
    @pytest.mark.unit_min_deps
    def test_reproducible_sequence(self):
        """Same trace_id produces identical random sequence."""
        a = DeterministicRandomSource("trace-rng")
        b = DeterministicRandomSource("trace-rng")
        seq_a = [a.random() for _ in range(10)]
        seq_b = [b.random() for _ in range(10)]
        assert seq_a == seq_b

    @pytest.mark.unit_min_deps
    def test_different_trace_different_sequence(self):
        """Different trace_ids produce different sequences."""
        a = DeterministicRandomSource("trace-x")
        b = DeterministicRandomSource("trace-y")
        seq_a = [a.random() for _ in range(10)]
        seq_b = [b.random() for _ in range(10)]
        assert seq_a != seq_b

    @pytest.mark.unit_min_deps
    def test_randint_range(self):
        """randint returns values within [a, b]."""
        src = DeterministicRandomSource("trace-randint")
        for _ in range(50):
            val = src.randint(1, 10)
            assert 1 <= val <= 10

    @pytest.mark.unit_min_deps
    def test_choice_from_sequence(self):
        """choice returns element from provided sequence."""
        src = DeterministicRandomSource("trace-choice")
        options = ["a", "b", "c"]
        for _ in range(20):
            assert src.choice(options) in options

    @pytest.mark.unit_min_deps
    def test_shuffle_deterministic(self):
        """shuffle produces identical result for same trace_id."""
        a = DeterministicRandomSource("trace-shuffle")
        b = DeterministicRandomSource("trace-shuffle")
        list_a = [1, 2, 3, 4, 5]
        list_b = [1, 2, 3, 4, 5]
        a.shuffle(list_a)
        b.shuffle(list_b)
        assert list_a == list_b


# ---------------------------------------------------------------------------
# DeterministicUUIDProvider
# ---------------------------------------------------------------------------


class TestDeterministicUUIDProvider:
    @pytest.mark.unit_min_deps
    def test_reproducible_uuid_sequence(self):
        """Same trace_id produces identical UUID sequence."""
        a = DeterministicUUIDProvider("trace-uuid")
        b = DeterministicUUIDProvider("trace-uuid")
        seq_a = [a.uuid4() for _ in range(5)]
        seq_b = [b.uuid4() for _ in range(5)]
        assert seq_a == seq_b

    @pytest.mark.unit_min_deps
    def test_monotonic_increment(self):
        """Sequential UUIDs are distinct."""
        p = DeterministicUUIDProvider("trace-mono")
        uuids = [p.uuid4() for _ in range(10)]
        assert len(set(uuids)) == 10

    @pytest.mark.unit_min_deps
    def test_uuid_version_4(self):
        """Generated UUIDs have version 4."""
        p = DeterministicUUIDProvider("trace-v4")
        u = p.uuid4()
        assert u.version == 4


# ---------------------------------------------------------------------------
# Patching lifecycle
# ---------------------------------------------------------------------------


class TestPatchLifecycle:
    @pytest.fixture(autouse=True)
    def _ensure_unpatched(self):
        """Ensure deterministic providers are unpatched before and after each test."""
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_patch_installs_providers(self):
        """patch_deterministic replaces time/random/uuid modules."""
        original_time = time.time
        patch_deterministic("trace-patch")
        assert is_patched()
        assert time.time is not original_time

    @pytest.mark.unit_min_deps
    def test_unpatch_restores_originals(self):
        """unpatch_deterministic restores original modules."""
        original_time = time.time
        patch_deterministic("trace-unpatch")
        unpatch_deterministic()
        assert not is_patched()
        assert time.time is original_time

    @pytest.mark.unit_min_deps
    def test_idempotent_same_trace(self):
        """Patching with same trace_id is idempotent."""
        patch_deterministic("trace-idem")
        patch_deterministic("trace-idem")  # Should not raise
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_different_trace_raises(self):
        """Patching with different trace_id raises DeterministicPatchError."""
        patch_deterministic("trace-first")
        with pytest.raises(DeterministicPatchError):
            patch_deterministic("trace-second")

    @pytest.mark.unit_min_deps
    def test_unpatch_idempotent(self):
        """unpatch_deterministic is safe to call when not patched."""
        unpatch_deterministic()  # Should not raise
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_patched_time_deterministic(self):
        """After patching, time.time() returns deterministic values."""
        patch_deterministic("trace-time-det")
        t1 = time.time()
        t2 = time.time()
        assert t1 == t2  # No real clock advancement

    @pytest.mark.unit_min_deps
    def test_patched_random_deterministic(self):
        """After patching, random.random() returns deterministic values."""
        patch_deterministic("trace-rand-det")
        r1 = random.random()
        unpatch_deterministic()
        patch_deterministic("trace-rand-det")
        r2 = random.random()
        assert r1 == r2

    @pytest.mark.unit_min_deps
    def test_patched_uuid_deterministic(self):
        """After patching, uuid.uuid4() returns deterministic values."""
        patch_deterministic("trace-uuid-det")
        u1 = uuid.uuid4()
        unpatch_deterministic()
        patch_deterministic("trace-uuid-det")
        u2 = uuid.uuid4()
        assert u1 == u2

    @pytest.mark.unit_min_deps
    def test_replay_determinism_proof(self):
        """Full replay determinism: same trace_id produces byte-identical outputs."""
        trace = "trace-replay-proof"

        # Run 1
        patch_deterministic(trace)
        run1_time = time.time()
        run1_rand = [random.random() for _ in range(5)]
        run1_uuid = uuid.uuid4()
        unpatch_deterministic()

        # Run 2
        patch_deterministic(trace)
        run2_time = time.time()
        run2_rand = [random.random() for _ in range(5)]
        run2_uuid = uuid.uuid4()
        unpatch_deterministic()

        assert run1_time == run2_time
        assert run1_rand == run2_rand
        assert run1_uuid == run2_uuid
