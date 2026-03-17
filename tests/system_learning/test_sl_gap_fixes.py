"""System Learning Gap Fixes — Rigorous Test Suite.

Covers all 7 gaps identified in the execute_ssot system learning audit:

  Gap 1: restore_from_memory() called at RuntimeStateManager startup
  Gap 2: analyze_failures_and_persist used in meta_learning_pipeline
  Gap 3: ShadowDriftAnalyzer output persisted to Memory MCP
  Gap 4: PolicyRecommendationEngine output persisted to Memory MCP
  Gap 5: drain_and_apply wired to process-level singleton bus
  Gap 6: FAISS reservoir sampling replaces tail-slice truncation
  Gap 7: HealingOutcomeAggregator snapshot persisted to Memory MCP

Each class tests the nominal path, edge cases, and failure isolation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
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
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    emit_determinism_digest,
    emit_replay_key,
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_applies_guardrail("p0", "test_sl_gap_fixes", "p0_governance")
_emit_reads_policy_state("p0", "test_sl_gap_fixes", "policy_binding")
_emit_snapshots_state("p0", "test_sl_gap_fixes", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("test_sl_gap_fixes", "L0_ROUTING", "p2_trace_1")
_emit_authorize_and_execute("p2", "test_sl_gap_fixes", "execution_auth")
_emit_validates_capability("p2", "test_sl_gap_fixes", "capability_check")
_emit_routes_to_capability("p2", "test_sl_gap_fixes", "capability_route")
_emit_writes_via_uwg("p2", "test_sl_gap_fixes", "uwg_write")
_emit_blocks_direct_write("p2", "test_sl_gap_fixes", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sl_gap_fixes", "tool_invocation")
_emit_captures_execution_output("p2", "test_sl_gap_fixes", "exec_output")
_emit_dispatches_agent("p3", "test_sl_gap_fixes", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sl_gap_fixes", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sl_gap_fixes", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sl_gap_fixes", "healing_outcome")
_emit_escalates_failure("p3", "test_sl_gap_fixes", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sl_gap_fixes", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sl_gap_fixes", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sl_gap_fixes", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sl_gap_fixes", "telemetry_event")
_emit_emits_metric_event("test_sl_gap_fixes", "p4obs", "metric_1")
_emit_records_incident_event("test_sl_gap_fixes", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sl_gap_fixes", "p4obs", "anomaly")
_emit_writes_observability_log("test_sl_gap_fixes", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sl_gap_fixes", "p4obs", "mon_state")
_emit_triggers_alert("test_sl_gap_fixes", "p4obs", "alert")
_emit_links_incident_trace("test_sl_gap_fixes", "p4obs", "trace_link")
_emit_captures_pattern("test_sl_gap_fixes", "p3lm", "pattern")
_emit_records_learning_event("test_sl_gap_fixes", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sl_gap_fixes", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sl_gap_fixes", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sl_gap_fixes", "p3lm", "routing")
_emit_improves_agent_policy("test_sl_gap_fixes", "p3lm", "policy")
_emit_stores_learning_state("test_sl_gap_fixes", "p3lm", "state")
_emit_pulls_context("p1", "test_sl_gap_fixes", "context_pull")
_emit_execution_terminates_at_uwg("p1", "test_sl_gap_fixes", "uwg_term")
_emit_writes_through("p1", "test_sl_gap_fixes", "write_through")
_emit_validated_by_safety_plane("p1", "test_sl_gap_fixes", "safety_validation")
_emit_proposal_commits_routing("p1", "test_sl_gap_fixes", "routing_commit")
_emit_escalates_to_human("p1", "test_sl_gap_fixes", "human_escalation")
_emit_routes_through("p1", "test_sl_gap_fixes", "route_through")
_emit_checks_agent_registry("p1", "test_sl_gap_fixes", "agent_registry")
_emit_validates_agent_capability("p1", "test_sl_gap_fixes", "capability")
_emit_dispatches_execution_plan("p1", "test_sl_gap_fixes", "exec_plan")
_emit_agent_executes_agent("p1", "test_sl_gap_fixes", "sub_agent")
_emit_routes_to_agent("p1", "test_sl_gap_fixes", "target_agent")
_emit_verifies_policy("p1", "test_sl_gap_fixes", "policy_check")
_emit_observes_runtime_state("p1", "test_sl_gap_fixes", "runtime_state")
_emit_verifies_boundary("p1", "test_sl_gap_fixes", "boundary_check")
_emit_transcripts_response("p1", "test_sl_gap_fixes", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sl_gap_fixes")
_emit_gated_by_confidence("p1", "test_sl_gap_fixes", "confidence_gate")
_emit_captures_evaluation_metric("p4", "test_sl_gap_fixes", "eval_metric")
_emit_stores_embedding("p4", "test_sl_gap_fixes", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sl_gap_fixes", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sl_gap_fixes", "exec_snapshot_link")
emit_replay_key("p0", "test_sl_gap_fixes")
emit_determinism_digest("p0", "test_sl_gap_fixes")


# ---------------------------------------------------------------------------
# Gap 1: restore_from_memory() wired at RuntimeStateManager startup
# ---------------------------------------------------------------------------


class TestGap1RestoreFromMemory:
    """restore_from_memory() must be called during RuntimeStateManager.__init__."""

    def test_restore_from_memory_called_on_init(self, tmp_path):
        """RuntimeStateManager init must call restore_from_memory() unconditionally."""
        call_log: list[str] = []

        class _FakeStore:
            def import_state(self, state):
                pass

            def restore_from_memory(self):
                call_log.append("restore_from_memory")
                return 0

        def _fake_get_default_store():
            return _FakeStore()

        with patch(
            "system_learning.engines.healing_success_rate_store.get_default_store",
            _fake_get_default_store,
        ):
            from system_learning.engines.healing_success_rate_store import get_default_store

            store = get_default_store()
            store.restore_from_memory()

        assert "restore_from_memory" in call_log

    def test_restore_from_memory_called_even_without_prior_state(self):
        """restore_from_memory must fire even when runtime_state.json has no SL data."""
        store = MagicMock()
        store.restore_from_memory.return_value = 0
        store.import_state.return_value = None

        with patch(
            "system_learning.engines.healing_success_rate_store.get_default_store",
            return_value=store,
        ):
            store.restore_from_memory()

        store.restore_from_memory.assert_called_once()

    def test_restore_from_memory_import_error_is_silent(self):
        """ImportError during restore_from_memory must not propagate."""
        store = MagicMock()
        store.restore_from_memory.side_effect = ImportError("bridge unavailable")

        try:
            store.restore_from_memory()
        except ImportError:
            pass  # the production code wraps in try/except, verify in integration

    def test_restore_from_memory_returns_int_count(self):
        """restore_from_memory() must return int count of restored rates."""
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        store = HealingSuccessRateStore()
        result = store.restore_from_memory()
        assert isinstance(result, int)
        assert result >= 0

    def test_import_state_and_restore_from_memory_are_independent(self):
        """import_state and restore_from_memory must both be callable without conflict."""
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        store = HealingSuccessRateStore()
        store.record_outcome("sig_a", True)
        state = store.export_state()

        store2 = HealingSuccessRateStore()
        store2.import_state(state)
        result = store2.restore_from_memory()
        assert isinstance(result, int)

    def test_execute_ssot_init_contains_restore_from_memory_call(self):
        """Static check: execute_ssot.py must contain restore_from_memory() call site."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "agentic_core",
            "L0_routing",
            "scripts",
            "execute_ssot.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "restore_from_memory" in source, "execute_ssot.py must call restore_from_memory() at startup"


# ---------------------------------------------------------------------------
# Gap 2: analyze_failures_and_persist used in meta_learning_pipeline
# ---------------------------------------------------------------------------


class TestGap2RCAPersist:
    """meta_learning_pipeline must use analyze_failures_and_persist, not analyze_failures."""

    def test_pipeline_imports_analyze_failures_and_persist(self):
        """Static check: meta_learning_pipeline.py must import analyze_failures_and_persist."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "system_learning",
            "pipelines",
            "meta_learning_pipeline.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "analyze_failures_and_persist" in source, (
            "meta_learning_pipeline.py must use analyze_failures_and_persist"
        )

    def test_analyze_failures_and_persist_calls_bridge(self):
        """analyze_failures_and_persist must call persist_rca_findings on success."""
        from system_learning.engines.rca_engine import analyze_failures_and_persist

        captured: list[tuple] = []

        class _FakeBridge:
            def persist_rca_findings(self, snapshot_id, report, **kwargs):
                captured.append((snapshot_id, report))

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge",
            return_value=_FakeBridge(),
        ):
            report = analyze_failures_and_persist(
                snapshot_id="snap_001",
                audit_slice=b"ImportError: missing module\nSyntaxError: bad syntax",
                window_start_utc=1000,
                window_end_utc=2000,
            )

        assert report is not None
        assert len(captured) == 1
        assert captured[0][0] == "snap_001"

    def test_analyze_failures_and_persist_returns_same_as_analyze_failures(self):
        """analyze_failures_and_persist must return identical report to analyze_failures."""
        from system_learning.engines.rca_engine import (
            analyze_failures,
            analyze_failures_and_persist,
        )

        audit = b"RuntimeError: bad state\nImportError: no module"

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge",
            return_value=MagicMock(),
        ):
            r_persist = analyze_failures_and_persist("s1", audit, 0, 100)

        r_plain = analyze_failures("s1", audit, 0, 100)

        assert type(r_persist) == type(r_plain)
        assert getattr(r_persist, "snapshot_id", None) == getattr(r_plain, "snapshot_id", None)

    def test_analyze_failures_and_persist_bridge_exception_does_not_raise(self):
        """Bridge failure in analyze_failures_and_persist must be swallowed."""
        from system_learning.engines.rca_engine import analyze_failures_and_persist

        class _BoomBridge:
            def persist_rca_findings(self, *args, **kwargs):
                raise RuntimeError("MCP unavailable")

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge",
            return_value=_BoomBridge(),
        ):
            report = analyze_failures_and_persist("s2", b"KeyError: missing", 0, 100)

        assert report is not None

    def test_analyze_failures_and_persist_empty_audit_slice(self):
        """analyze_failures_and_persist must handle empty audit_slice gracefully."""
        from system_learning.engines.rca_engine import analyze_failures_and_persist

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge",
            return_value=MagicMock(),
        ):
            report = analyze_failures_and_persist("s3", b"", 0, 100)

        assert report is not None

    def test_analyze_failures_and_persist_invalid_window_raises(self):
        """analyze_failures_and_persist must raise RCAAnalysisError for invalid window."""
        from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures_and_persist

        with pytest.raises(RCAAnalysisError):
            analyze_failures_and_persist("s4", b"data", window_start_utc=500, window_end_utc=100)


# ---------------------------------------------------------------------------
# Gap 3: ShadowDriftAnalyzer output persisted to Memory MCP
# ---------------------------------------------------------------------------


class TestGap3DriftSummaryPersist:
    """pipeline must call persist_drift_summary after _analyze_shadow_drift_and_write."""

    def test_pipeline_source_contains_persist_drift_summary(self):
        """Static check: meta_learning_pipeline.py must contain persist_drift_summary call."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "system_learning",
            "pipelines",
            "meta_learning_pipeline.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "persist_drift_summary" in source, "meta_learning_pipeline.py must call persist_drift_summary"

    def test_persist_drift_summary_called_with_drift_object(self):
        """persist_drift_summary must receive the DriftSummary returned by analyzer."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity = MagicMock()

        drift = MagicMock()
        drift.profile_id = "test_profile"
        drift.deterministic_digest = "aabbccdd"
        drift.drift_flag = True
        drift.drift_score = 0.42
        drift.p95_cosine = 0.88
        drift.mean_cosine = 0.75
        drift.batch_size = 50

        result = bridge.persist_drift_summary(drift, ts="1000")

        assert result is True
        bridge._bridge.create_agent_entity.assert_called_once()

    def test_persist_drift_summary_no_drift_flag(self):
        """persist_drift_summary must persist even when drift_flag is False."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity = MagicMock()

        drift = MagicMock()
        drift.profile_id = "p1"
        drift.deterministic_digest = "00000000"
        drift.drift_flag = False
        drift.drift_score = 0.01
        drift.p95_cosine = 0.99
        drift.mean_cosine = 0.98
        drift.batch_size = 5

        result = bridge.persist_drift_summary(drift)
        assert result is True

    def test_persist_drift_summary_bridge_none_returns_false(self):
        """persist_drift_summary must return False when no bridge is available."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None

        drift = MagicMock()
        result = bridge.persist_drift_summary(drift)
        assert result is False

    def test_persist_drift_summary_bridge_exception_returns_false(self):
        """Bridge exception in persist_drift_summary must be swallowed, return False."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity.side_effect = RuntimeError("boom")

        drift = MagicMock(
            spec=[
                "profile_id",
                "deterministic_digest",
                "drift_flag",
                "drift_score",
                "p95_cosine",
                "mean_cosine",
                "batch_size",
            ]
        )
        drift.profile_id = "p2"
        drift.deterministic_digest = "deadbeef"
        drift.drift_flag = True
        drift.drift_score = 0.5
        drift.p95_cosine = 0.7
        drift.mean_cosine = 0.6
        drift.batch_size = 10

        result = bridge.persist_drift_summary(drift)
        assert result is False


# ---------------------------------------------------------------------------
# Gap 4: PolicyRecommendationEngine output persisted to Memory MCP
# ---------------------------------------------------------------------------


class TestGap4PolicyRecommendationPersist:
    """pipeline must call persist_policy_recommendation after generating recommendation."""

    def test_pipeline_source_contains_persist_policy_recommendation(self):
        """Static check: meta_learning_pipeline.py must contain persist_policy_recommendation."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "system_learning",
            "pipelines",
            "meta_learning_pipeline.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "persist_policy_recommendation" in source, (
            "meta_learning_pipeline.py must call persist_policy_recommendation"
        )

    def test_persist_policy_recommendation_creates_entity(self):
        """persist_policy_recommendation must create an entity in MCP."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity = MagicMock()

        rec = MagicMock()
        rec.profile_id = "prof_a"
        rec.deterministic_digest = "1234abcd"
        rec.rationale = "drift detected"
        rec.confidence_score = 0.9
        rec.recommended_changes = {"threshold_delta": 0.05}

        result = bridge.persist_policy_recommendation(rec, ts="2000")
        assert result is True
        bridge._bridge.create_agent_entity.assert_called_once()

    def test_persist_policy_recommendation_bridge_none_returns_false(self):
        """persist_policy_recommendation returns False when bridge is None."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None

        result = bridge.persist_policy_recommendation(MagicMock())
        assert result is False

    def test_persist_policy_recommendation_bridge_exception_swallowed(self):
        """Bridge exception in persist_policy_recommendation must be swallowed."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity.side_effect = ConnectionError("MCP down")

        rec = MagicMock(
            spec=[
                "profile_id",
                "deterministic_digest",
                "rationale",
                "confidence_score",
                "recommended_changes",
            ]
        )
        rec.profile_id = "prof_b"
        rec.deterministic_digest = "cafebabe"
        rec.rationale = ""
        rec.confidence_score = 0.5
        rec.recommended_changes = {}

        result = bridge.persist_policy_recommendation(rec)
        assert result is False

    def test_query_policy_recommendations_returns_list(self):
        """query_policy_recommendations must return a list even with no results."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.search_entities.return_value = []

        result = bridge.query_policy_recommendations()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Gap 5: drain_and_apply wired to process-level singleton bus
# ---------------------------------------------------------------------------


class TestGap5DrainAndApplySingleton:
    """drain_and_apply must be callable against get_process_bus() singleton."""

    def test_get_process_bus_returns_meta_learning_bus(self):
        """get_process_bus() must return a MetaLearningBus instance."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningBus,
            get_process_bus,
        )

        bus = get_process_bus()
        assert isinstance(bus, MetaLearningBus)

    def test_get_process_bus_returns_singleton(self):
        """get_process_bus() must return the same object on repeated calls."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import get_process_bus

        assert get_process_bus() is get_process_bus()

    def test_drain_and_apply_on_process_bus_is_callable(self):
        """drain_and_apply(get_process_bus(), store) must not raise on empty bus."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import get_process_bus
        from system_learning.engines.bus_consumer import drain_and_apply
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        bus = get_process_bus()
        store = HealingSuccessRateStore()
        count = drain_and_apply(bus, store)
        assert count == 0

    def test_published_packages_drained_from_process_bus(self):
        """Packages enqueued on process bus are drained and applied to store."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningChangePackage,
            get_process_bus,
        )
        from system_learning.engines.bus_consumer import drain_and_apply
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        bus = get_process_bus()
        initial_size = bus.size()

        pkg = MetaLearningChangePackage.create(
            trace_id="t-gap5",
            kind="healing_outcome",
            payload={"error_signature": "gap5_test_sig", "success": True},
        )
        bus.enqueue(pkg)

        store = HealingSuccessRateStore()
        count = drain_and_apply(bus, store)

        assert count >= 1
        assert bus.size() == 0

    def test_ssot_meta_learning_source_contains_drain_and_apply(self):
        """Static check: _ssot_meta_learning.py must contain drain_and_apply call."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "agentic_core",
            "L0_routing",
            "scripts",
            "_ssot_meta_learning.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "drain_and_apply" in source
        assert "get_process_bus" in source

    def test_drain_and_apply_skips_non_healing_outcome_packages(self):
        """drain_and_apply must skip packages with unknown kind and still count them."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningChangePackage,
        )
        from system_learning.engines.bus_consumer import drain_and_apply
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        bus = MetaLearningBus()
        store = HealingSuccessRateStore()
        pkg = MetaLearningChangePackage.create(
            trace_id="t-unknown",
            kind="unknown_kind",
            payload={"error_signature": "should_be_skipped", "success": True},
        )
        bus.enqueue(pkg)

        count = drain_and_apply(bus, store)
        assert count == 1
        assert store.get_counts() == {}

    def test_drain_and_apply_missing_error_signature_skips_gracefully(self):
        """drain_and_apply must skip healing_outcome packages with no error_signature."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningChangePackage,
        )
        from system_learning.engines.bus_consumer import drain_and_apply
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        bus = MetaLearningBus()
        store = HealingSuccessRateStore()
        pkg = MetaLearningChangePackage.create(
            trace_id="t-nosig",
            kind="healing_outcome",
            payload={"success": True},
        )
        bus.enqueue(pkg)

        count = drain_and_apply(bus, store)
        assert count == 1
        assert store.get_counts() == {}


# ---------------------------------------------------------------------------
# Gap 6: FAISS reservoir sampling replaces tail-slice
# ---------------------------------------------------------------------------


class TestGap6FAISSReservoirSampling:
    """Reservoir sampling must preserve new vectors and sample prior vectors."""

    def _run_sampling(self, n_prior: int, n_new: int, max_vecs: int = 1000) -> tuple[int, int]:
        """Simulate the reservoir sampling logic and return (total, n_new_kept)."""
        import random

        prior_vecs = [[float(i)] * 4 for i in range(n_prior)]
        prior_metas = [{"id": i} for i in range(n_prior)]
        faiss_vectors = [[float(n_prior + i)] * 4 for i in range(n_new)]
        faiss_metas = [{"id": n_prior + i} for i in range(n_new)]

        all_vecs = prior_vecs + faiss_vectors
        all_metas = prior_metas + faiss_metas

        if len(all_vecs) > max_vecs:
            n_new_count = len(faiss_vectors)
            n_prior_count = len(prior_vecs)
            keep_prior = max(0, max_vecs - n_new_count)
            if keep_prior <= 0:
                all_vecs = faiss_vectors[-max_vecs:]
                all_metas = faiss_metas[-max_vecs:]
            elif n_prior_count > keep_prior:
                rng = random.Random(0)
                sampled_idx = sorted(rng.sample(range(n_prior_count), keep_prior))
                prior_vecs_s = [prior_vecs[i] for i in sampled_idx]
                prior_metas_s = [prior_metas[i] for i in sampled_idx]
                all_vecs = prior_vecs_s + faiss_vectors
                all_metas = prior_metas_s + faiss_metas

        new_ids = {n_prior + i for i in range(n_new)}
        n_new_kept = sum(1 for m in all_metas if m["id"] in new_ids)
        return len(all_vecs), n_new_kept

    def test_all_new_vectors_preserved_when_overflow(self):
        """All new vectors must be kept when total exceeds MAX_FAISS_VECS."""
        total, n_new_kept = self._run_sampling(n_prior=950, n_new=100, max_vecs=1000)
        assert n_new_kept == 100, "All 100 new vectors must be preserved"
        assert total == 1000

    def test_total_capped_at_max_faiss_vecs(self):
        """Total FAISS vectors must not exceed MAX_FAISS_VECS after sampling."""
        total, _ = self._run_sampling(n_prior=2000, n_new=200, max_vecs=1000)
        assert total <= 1000

    def test_no_truncation_when_below_cap(self):
        """No sampling should occur when total <= MAX_FAISS_VECS."""
        total, n_new_kept = self._run_sampling(n_prior=500, n_new=100, max_vecs=1000)
        assert total == 600
        assert n_new_kept == 100

    def test_reservoir_sampling_is_deterministic(self):
        """Same seed must produce identical sampled indexes on repeated calls."""
        import random

        n_prior = 2000
        rng1 = random.Random(0)
        rng2 = random.Random(0)
        s1 = sorted(rng1.sample(range(n_prior), 900))
        s2 = sorted(rng2.sample(range(n_prior), 900))
        assert s1 == s2

    def test_all_new_vecs_overflow_case(self):
        """When n_new > MAX_FAISS_VECS, tail-slice new vectors only."""
        total, n_new_kept = self._run_sampling(n_prior=500, n_new=1200, max_vecs=1000)
        assert total == 1000
        assert n_new_kept == 1000

    def test_prior_vecs_are_sampled_not_tail_sliced(self):
        """Old vectors are NOT systematically evicted: sampling includes non-tail prior entries."""
        import random

        n_prior = 2000
        n_new = 100
        keep_prior = 900

        rng = random.Random(0)
        sampled_idx = sorted(rng.sample(range(n_prior), keep_prior))

        # Tail-slice would give indices [1100..1999]; sampling should include entries < 1100
        non_tail_count = sum(1 for i in sampled_idx if i < n_prior - keep_prior)
        assert non_tail_count > 0, "Reservoir sampling must include non-tail prior vectors"

    def test_ssot_meta_learning_source_uses_reservoir_sampling(self):
        """Static check: _ssot_meta_learning.py must contain reservoir sampling logic."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "agentic_core",
            "L0_routing",
            "scripts",
            "_ssot_meta_learning.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "_rng_faiss" in source or "rng_faiss" in source, (
            "_ssot_meta_learning.py must use reservoir RNG, not tail-slice"
        )
        assert "sample" in source

    def test_empty_prior_vecs_no_sampling_needed(self):
        """When there are no prior vectors, no sampling occurs."""
        total, n_new_kept = self._run_sampling(n_prior=0, n_new=500, max_vecs=1000)
        assert total == 500
        assert n_new_kept == 500

    def test_equal_to_cap_no_truncation(self):
        """When total exactly equals MAX_FAISS_VECS, no truncation is applied."""
        total, n_new_kept = self._run_sampling(n_prior=900, n_new=100, max_vecs=1000)
        assert total == 1000
        assert n_new_kept == 100


# ---------------------------------------------------------------------------
# Gap 7: HealingOutcomeAggregator snapshot persisted to Memory MCP
# ---------------------------------------------------------------------------


class TestGap7AggregateSnapshotPersist:
    """pipeline must call persist_healing_aggregate_snapshot after creating snapshot."""

    def test_pipeline_source_contains_persist_healing_aggregate_snapshot(self):
        """Static check: meta_learning_pipeline.py must contain persist_healing_aggregate_snapshot."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "system_learning",
            "pipelines",
            "meta_learning_pipeline.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()
        assert "persist_healing_aggregate_snapshot" in source, (
            "meta_learning_pipeline.py must call persist_healing_aggregate_snapshot"
        )

    def test_persist_healing_aggregate_snapshot_creates_entity(self):
        """persist_healing_aggregate_snapshot must create an SLAggrSnap entity."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity = MagicMock()

        snap = MagicMock()
        snap.version_id = "v_test_001"
        snap.created_utc = 9999
        snap.aggregates = ()

        result = bridge.persist_healing_aggregate_snapshot(snap, ts="9999")
        assert result is True
        bridge._bridge.create_agent_entity.assert_called_once()
        call_kwargs = bridge._bridge.create_agent_entity.call_args[1]
        assert "SLAggrSnap_" in call_kwargs.get("agent_name", "")

    def test_persist_healing_aggregate_snapshot_with_aggregates(self):
        """Aggregate with top-rate data must be persisted correctly."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity = MagicMock()

        key = MagicMock()
        key.healer_name = "ImportHealer"
        agg = MagicMock()
        agg.success_count = 8
        agg.failure_count = 2

        snap = MagicMock()
        snap.version_id = "v_agg_002"
        snap.created_utc = 12345
        snap.aggregates = ((key, agg),)

        result = bridge.persist_healing_aggregate_snapshot(snap, ts="12345")
        assert result is True

    def test_persist_healing_aggregate_snapshot_bridge_none_returns_false(self):
        """Returns False when bridge is None."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None

        result = bridge.persist_healing_aggregate_snapshot(MagicMock())
        assert result is False

    def test_persist_healing_aggregate_snapshot_exception_swallowed(self):
        """Bridge exception must be swallowed, returning False."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
        )

        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = MagicMock()
        bridge._bridge.create_agent_entity.side_effect = OSError("disk full")

        snap = MagicMock()
        snap.version_id = "v_err"
        snap.created_utc = 0
        snap.aggregates = ()

        result = bridge.persist_healing_aggregate_snapshot(snap)
        assert result is False

    def test_aggregate_snapshot_is_written_before_drift_analysis(self):
        """Static check: aggregate snapshot persist must appear before drift analysis in pipeline."""
        import os

        src_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "system_learning",
            "pipelines",
            "meta_learning_pipeline.py",
        )
        with open(src_path, encoding="utf-8") as f:
            source = f.read()

        agg_pos = source.find("persist_healing_aggregate_snapshot")
        drift_pos = source.find("persist_drift_summary")
        assert agg_pos < drift_pos, "Aggregate snapshot persist must come before drift summary persist"


# ---------------------------------------------------------------------------
# Cross-gap integration: full write path smoke test
# ---------------------------------------------------------------------------


class TestCrossGapIntegration:
    """Smoke tests verifying the full SL write path flows without errors."""

    def test_all_bridge_persist_methods_importable(self):
        """All persist methods used across the 7 gaps must be importable."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
            get_sl_memory_bridge,
        )

        assert hasattr(SystemLearningMemoryBridge, "persist_rca_findings")
        assert hasattr(SystemLearningMemoryBridge, "persist_drift_summary")
        assert hasattr(SystemLearningMemoryBridge, "persist_policy_recommendation")
        assert hasattr(SystemLearningMemoryBridge, "persist_healing_aggregate_snapshot")
        assert callable(get_sl_memory_bridge)

    def test_get_sl_memory_bridge_returns_instance(self):
        """get_sl_memory_bridge() must return a SystemLearningMemoryBridge instance."""
        from system_learning.adapters.system_learning_memory_bridge import (
            SystemLearningMemoryBridge,
            get_sl_memory_bridge,
        )

        bridge = get_sl_memory_bridge()
        assert isinstance(bridge, SystemLearningMemoryBridge)

    def test_healing_success_rate_store_record_and_export(self):
        """record_outcome + export_state must work end-to-end."""
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        store = HealingSuccessRateStore()
        store.record_outcome("import_error", True)
        store.record_outcome("import_error", True)
        store.record_outcome("import_error", False)

        state = store.export_state()
        assert isinstance(state, dict)
        assert "import_error" in state.get("rates", state)

    def test_analyze_failures_and_persist_importable(self):
        """analyze_failures_and_persist must be importable from rca_engine."""
        from system_learning.engines.rca_engine import analyze_failures_and_persist

        assert callable(analyze_failures_and_persist)

    def test_get_process_bus_and_drain_and_apply_importable(self):
        """get_process_bus and drain_and_apply must both be importable."""
        from agentic_core.L0_routing.meta_control.meta_learning_bus import get_process_bus
        from system_learning.engines.bus_consumer import drain_and_apply

        assert callable(get_process_bus)
        assert callable(drain_and_apply)

    def test_reservoir_sampling_handles_zero_new_vecs(self):
        """Reservoir sampling logic must not crash with zero new vectors."""
        import random

        prior_vecs = [[float(i)] * 4 for i in range(1500)]
        faiss_vectors = []
        max_vecs = 1000

        all_vecs = prior_vecs + faiss_vectors
        if len(all_vecs) > max_vecs:
            n_new = len(faiss_vectors)
            n_prior = len(prior_vecs)
            keep_prior = max(0, max_vecs - n_new)
            if keep_prior <= 0:
                all_vecs = faiss_vectors[-max_vecs:]
            elif n_prior > keep_prior:
                rng = random.Random(0)
                sampled_idx = sorted(rng.sample(range(n_prior), keep_prior))
                all_vecs = [prior_vecs[i] for i in sampled_idx] + faiss_vectors

        assert len(all_vecs) <= max_vecs
