"""R1-R7 Runtime acceleration benchmarks.

Verifies that ADG-indexed queries are faster than equivalent filesystem scans
and that the GraphAwareCache provides precise invalidation.

Plan ref: tests/performance/test_adg_runtime_acceleration.py
"""

from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    ScanResult,
)
from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.cache.graph_aware_cache import GraphAwareCache
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_runtime_acceleration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_runtime_acceleration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_runtime_acceleration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_runtime_acceleration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_runtime_acceleration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_runtime_acceleration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_runtime_acceleration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_runtime_acceleration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_runtime_acceleration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_runtime_acceleration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_runtime_acceleration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_runtime_acceleration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_runtime_acceleration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_runtime_acceleration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_runtime_acceleration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_runtime_acceleration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_runtime_acceleration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_runtime_acceleration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_runtime_acceleration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_runtime_acceleration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_runtime_acceleration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_runtime_acceleration", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_runtime_acceleration")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_runtime_acceleration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_runtime_acceleration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_runtime_acceleration", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_adg_runtime_acceleration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_runtime_acceleration", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_runtime_acceleration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_runtime_acceleration", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_adg_runtime_acceleration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_runtime_acceleration", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_runtime_acceleration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_runtime_acceleration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_runtime_acceleration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_runtime_acceleration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_runtime_acceleration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_runtime_acceleration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_runtime_acceleration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_runtime_acceleration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_runtime_acceleration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_runtime_acceleration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_runtime_acceleration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_runtime_acceleration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_runtime_acceleration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_runtime_acceleration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_runtime_acceleration")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_runtime_acceleration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_runtime_acceleration")
# REMOVED: emit_determinism_digest("p0", "test_adg_runtime_acceleration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_runtime_acceleration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_runtime_acceleration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_runtime_acceleration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_runtime_acceleration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_runtime_acceleration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_runtime_acceleration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_runtime_acceleration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_runtime_acceleration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_runtime_acceleration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_runtime_acceleration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_runtime_acceleration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_runtime_acceleration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_runtime_acceleration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_runtime_acceleration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_runtime_acceleration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_runtime_acceleration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_runtime_acceleration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_runtime_acceleration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_runtime_acceleration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_runtime_acceleration", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_scan_result() -> ScanResult:
    scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=True)
    return scanner.scan()


@pytest.fixture(scope="module")
def qe() -> ADGRuntimeQueryEngine:
    result = _make_scan_result()
    return ADGRuntimeQueryEngine(result)


@pytest.fixture(scope="module")
def cache(qe: ADGRuntimeQueryEngine) -> GraphAwareCache:
    return GraphAwareCache(qe)


# ---------------------------------------------------------------------------
# R1: ADG indexed queries — correctness
# ---------------------------------------------------------------------------


class TestADGQueryEngineCorrectness:
    def test_find_agents_by_base_class_returns_list(self, qe):
        agents = qe.find_agents_by_base_class("SovereignBaseAgent")
        assert isinstance(agents, list)

    def test_inheritance_index_populated(self, qe):
        assert len(qe._inheritance_index) > 0

    def test_reverse_deps_index_populated(self, qe):
        assert len(qe._reverse_deps) > 0

    def test_composition_index_populated(self, qe):
        assert len(qe._composition_index) > 0

    def test_compute_blast_radius_returns_dict(self, qe):
        result = qe.compute_blast_radius(["agentic_core/L0_routing/engines/execution_orchestrator.py"])
        assert isinstance(result, dict)

    def test_get_reverse_dependencies_returns_set(self, qe):
        some_module = next(iter(qe._reverse_deps), None)
        if some_module is None:
            pytest.skip("No reverse deps in index")
        deps = qe.get_reverse_dependencies(some_module)
        assert isinstance(deps, set)


# ---------------------------------------------------------------------------
# R1: Speedup benchmarks (10x minimum — relaxed for CI cold-start)
# ---------------------------------------------------------------------------


def _scan_filesystem_for_agents(base_class: str) -> list[str]:
    """Baseline: filesystem scan + AST parse per query."""
    agents: list[str] = []
    for py_file in sorted(_REPO_ROOT.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    name = base.id if isinstance(base, ast.Name) else ""
                    if name == base_class:
                        agents.append(str(py_file))
    return agents


class TestRuntimeSpeedup:
    """R1: ADG queries must be at least 10x faster than filesystem scan."""

    def test_agent_discovery_speedup(self, qe):
        # Warm up the query engine index
        _ = qe.find_agents_by_base_class("SovereignBaseAgent")

        # Baseline: filesystem scan (expensive)
        start = time.perf_counter()
        _ = _scan_filesystem_for_agents("SovereignBaseAgent")
        fs_time = time.perf_counter() - start

        # ADG: indexed query (fast)
        start = time.perf_counter()
        _ = qe.find_agents_by_base_class("SovereignBaseAgent")
        adg_time = time.perf_counter() - start

        if fs_time > 0.001:  # Only assert speedup if baseline was measurable
            speedup = fs_time / max(adg_time, 1e-9)
            assert speedup >= 10, (
                f"Expected ≥10x speedup, got {speedup:.1f}x "
                f"(fs={fs_time * 1000:.1f}ms, adg={adg_time * 1000:.3f}ms)"
            )

    def test_blast_radius_faster_than_full_scan(self, qe):
        changed = ["agentic_core/L0_routing/engines/execution_orchestrator.py"]

        # ADG blast radius
        start = time.perf_counter()
        blast = qe.compute_blast_radius(changed)
        adg_time = time.perf_counter() - start

        assert adg_time < 0.1, f"Blast radius took {adg_time * 1000:.1f}ms — expected <100ms"
        assert isinstance(blast, dict)


# ---------------------------------------------------------------------------
# R7: GraphAwareCache precision
# ---------------------------------------------------------------------------


class TestGraphAwareCachePrecision:
    def test_cache_set_and_get(self, cache):
        cache.set("key_test", "value_test", depends_on=["module_a"])
        assert cache.get("key_test") == "value_test"

    def test_cache_miss_returns_none(self, cache):
        assert cache.get("nonexistent_key_xyz") is None

    def test_precise_invalidation(self):
        """Graph-based invalidation should be precise, not blind."""
        result = _make_scan_result()
        engine = ADGRuntimeQueryEngine(result)
        gc = GraphAwareCache(engine)

        # Set 100 cache entries with 10 different dependency groups
        for i in range(100):
            gc.set(f"key_{i}", f"value_{i}", depends_on=[f"module_{i % 10}"])

        # Invalidate for one module key
        invalidated = gc.invalidate_for_change("module_5")

        # Should invalidate ~10 entries (those depending on module_5)
        assert 8 <= invalidated <= 15, f"Expected ~10 precise invalidations, got {invalidated}"
        # Remaining 90 should still be cached
        surviving = gc.size()
        assert surviving >= 85, f"Too many entries invalidated: only {surviving} remain"

    def test_invalidate_all(self):
        result = _make_scan_result()
        engine = ADGRuntimeQueryEngine(result)
        gc = GraphAwareCache(engine)
        for i in range(10):
            gc.set(f"k_{i}", f"v_{i}", depends_on=["mod_a"])
        gc.invalidate_all()
        assert gc.size() == 0

    def test_cache_stats(self, cache):
        stats = cache.stats()
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
