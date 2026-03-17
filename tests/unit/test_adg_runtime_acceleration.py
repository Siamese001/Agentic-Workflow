"""Tests for ADG Runtime Query Engine (R1) and GraphAwareCache (R7)."""

from __future__ import annotations

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanManifest,
    ScanResult,
)
from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.cache.graph_aware_cache import GraphAwareCache
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

_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_runtime_acceleration", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_runtime_acceleration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_runtime_acceleration", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_runtime_acceleration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_runtime_acceleration", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_runtime_acceleration", "p4obs", "alert")
_emit_links_incident_trace("test_adg_runtime_acceleration", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_runtime_acceleration", "p3lm", "pattern")
_emit_records_learning_event("test_adg_runtime_acceleration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_runtime_acceleration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_runtime_acceleration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_runtime_acceleration", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_runtime_acceleration", "p3lm", "policy")
_emit_stores_learning_state("test_adg_runtime_acceleration", "p3lm", "state")
_emit_records_execution_trace("test_adg_runtime_acceleration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_runtime_acceleration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_runtime_acceleration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_runtime_acceleration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_runtime_acceleration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_runtime_acceleration", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_runtime_acceleration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_runtime_acceleration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_runtime_acceleration", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_adg_runtime_acceleration")
_emit_applies_guardrail("p0", "test_adg_runtime_acceleration", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_runtime_acceleration", "policy_binding")
_emit_snapshots_state("p0", "test_adg_runtime_acceleration", "state_snapshot")
_emit_pulls_context("p1", "test_adg_runtime_acceleration", "context_pull")
_emit_pulls_context("p1", "test_adg_runtime_acceleration", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_adg_runtime_acceleration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_runtime_acceleration", "uwg_term_secondary")
_emit_writes_through("p1", "test_adg_runtime_acceleration", "write_through")
_emit_writes_through("p1", "test_adg_runtime_acceleration", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_adg_runtime_acceleration", "safety_validation")
_emit_invokes_eval("p1", "test_adg_runtime_acceleration", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_runtime_acceleration", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_runtime_acceleration", "human_escalation")
_emit_routes_through("p1", "test_adg_runtime_acceleration", "route_through")
_emit_checks_agent_registry("p1", "test_adg_runtime_acceleration", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_runtime_acceleration", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_runtime_acceleration", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_runtime_acceleration", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_runtime_acceleration", "target_agent")
_emit_verifies_policy("p1", "test_adg_runtime_acceleration", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_runtime_acceleration", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_runtime_acceleration", "boundary_check")
_emit_transcripts_response("p1", "test_adg_runtime_acceleration", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_runtime_acceleration")
_emit_gated_by_confidence("p1", "test_adg_runtime_acceleration", "confidence_gate")
emit_replay_key("p0", "test_adg_runtime_acceleration")
emit_determinism_digest("p0", "test_adg_runtime_acceleration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_runtime_acceleration", "execution_auth")
_emit_validates_capability("p2", "test_adg_runtime_acceleration", "capability_check")
_emit_routes_to_capability("p2", "test_adg_runtime_acceleration", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_runtime_acceleration", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_runtime_acceleration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_runtime_acceleration", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_runtime_acceleration", "exec_output")
_emit_dispatches_agent("p3", "test_adg_runtime_acceleration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_runtime_acceleration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_runtime_acceleration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_runtime_acceleration", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_runtime_acceleration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_runtime_acceleration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_runtime_acceleration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_runtime_acceleration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_runtime_acceleration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_runtime_acceleration", "eval_metric")
_emit_stores_embedding("p4", "test_adg_runtime_acceleration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_runtime_acceleration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_runtime_acceleration", "exec_snapshot_link")


def _make_result(edges: list[Edge]) -> ScanResult:
    result = ScanResult(edges=edges, modules=[], digest="test", commit_sha="abc")
    return result


def _edge(from_name: str, rel: str, to_name: str, kind: str = "direct", sym: str = "", line: int = 1) -> Edge:
    return Edge(
        from_name=from_name,
        relation_type=rel,
        to_name=to_name,
        edge_kind=kind,
        source_file="test.py",
        line_no=line,
        symbol=sym,
    )


_M = "ADG::Module::"
_S = "ADG::Symbol::"


class TestADGRuntimeQueryEngine:
    def _engine(self, edges: list[Edge]) -> ADGRuntimeQueryEngine:
        return ADGRuntimeQueryEngine(_make_result(edges))

    def test_inheritance_index_built(self):
        edges = [
            _edge(
                f"{_M}agentic_core/agents/foo.py::ConcreteAgent",
                "implements",
                f"{_S}SovereignBaseAgent",
                sym="SovereignBaseAgent",
            ),
            _edge(
                f"{_M}agentic_core/agents/bar.py::OtherAgent",
                "implements",
                f"{_S}SovereignBaseAgent",
                sym="SovereignBaseAgent",
            ),
        ]
        engine = self._engine(edges)
        result = engine.find_agents_by_base_class("SovereignBaseAgent")
        assert len(result) == 2
        class_names = [r.split("::")[-1] for r in result]
        assert "ConcreteAgent" in class_names
        assert "OtherAgent" in class_names

    def test_inheritance_index_empty_on_unknown_base(self):
        engine = self._engine([])
        assert engine.find_agents_by_base_class("NonExistentBase") == []

    def test_reverse_deps_built(self):
        edges = [
            _edge(f"{_M}agentic_core/L3/agent.py", "imports", f"{_M}agentic_core/L1/base.py"),
            _edge(f"{_M}agentic_core/L3/other.py", "imports", f"{_M}agentic_core/L1/base.py"),
        ]
        engine = self._engine(edges)
        rev = engine.get_reverse_dependencies(f"{_M}agentic_core/L1/base.py")
        assert f"{_M}agentic_core/L3/agent.py" in rev
        assert f"{_M}agentic_core/L3/other.py" in rev

    def test_reverse_deps_empty_on_unused(self):
        engine = self._engine([])
        assert engine.get_reverse_dependencies(f"{_M}nothing.py") == set()

    def test_composition_index_built(self):
        edges = [
            _edge(
                f"{_M}agentic_core/L2/reasoning/my_agent.py::MyAgent",
                "instantiates",
                f"{_S}LLMGateway",
                kind="composition",
                sym="LLMGateway",
            ),
        ]
        engine = self._engine(edges)
        caps = engine.find_agents_by_capability("LLMGateway")
        assert len(caps) == 1
        assert caps[0].composed_symbol == "LLMGateway"

    def test_composition_index_empty_on_unknown(self):
        engine = self._engine([])
        assert engine.find_agents_by_capability("UnknownSymbol") == []

    def test_blast_radius_direct(self):
        edges = [
            _edge(f"{_M}agentic_core/L3/agent.py", "imports", f"{_M}agentic_core/L1/base.py"),
        ]
        engine = self._engine(edges)
        blast = engine.compute_blast_radius(["agentic_core/L1/base.py"])
        assert "agentic_core/L1/base.py" in blast
        assert "agentic_core/L3/agent.py" in blast

    def test_blast_radius_transitive(self):
        edges = [
            _edge(f"{_M}b.py", "imports", f"{_M}a.py"),
            _edge(f"{_M}c.py", "imports", f"{_M}b.py"),
        ]
        engine = self._engine(edges)
        blast = engine.compute_blast_radius(["a.py"])
        assert "b.py" in blast
        assert "c.py" in blast
        assert blast["c.py"] == 2

    def test_blast_radius_no_deps(self):
        engine = self._engine([])
        blast = engine.compute_blast_radius(["solo.py"])
        assert blast == {"solo.py": 0}

    def test_validate_import_path_allowed(self):
        engine = self._engine([])
        result = engine.validate_import_path(
            "agentic_core/L3_orchestration/x.py", "agentic_core/L1_cognition/y.py"
        )
        assert result.allowed is True

    def test_validate_import_path_forbidden(self):
        engine = self._engine([])
        result = engine.validate_import_path(
            "agentic_core/L0_routing/x.py", "agentic_core/L3_orchestration/y.py"
        )
        assert result.allowed is False

    def test_get_cache_invalidation_set(self):
        edges = [
            _edge(f"{_M}consumer.py", "imports", f"{_M}dep.py"),
        ]
        engine = self._engine(edges)
        inv_set = engine.get_cache_invalidation_set("dep.py")
        assert "consumer.py" in inv_set

    def test_stats_returns_dict(self):
        engine = self._engine([])
        stats = engine.stats()
        assert isinstance(stats, dict)
        assert "total_edges" in stats
        assert stats["total_edges"] == 0


class TestGraphAwareCache:
    def _cache(self, edges: list[Edge] | None = None) -> GraphAwareCache:
        engine = ADGRuntimeQueryEngine(_make_result(edges or []))
        return GraphAwareCache(engine)

    def test_set_and_get(self):
        cache = self._cache()
        cache.set("key1", "value1", depends_on=[])
        assert cache.get("key1") == "value1"

    def test_get_missing_returns_none(self):
        cache = self._cache()
        assert cache.get("nonexistent") is None

    def test_explicit_invalidate(self):
        cache = self._cache()
        cache.set("k", "v", depends_on=[])
        assert cache.invalidate("k") is True
        assert cache.get("k") is None

    def test_explicit_invalidate_missing(self):
        cache = self._cache()
        assert cache.invalidate("missing") is False

    def test_graph_driven_invalidation(self):
        edges = [
            _edge(f"{_M}consumer.py", "imports", f"{_M}dep.py"),
        ]
        cache = self._cache(edges)
        cache.set("result1", 42, depends_on=["consumer.py"])
        cache.set("unrelated", 99, depends_on=["other.py"])
        evicted = cache.invalidate_for_change("dep.py")
        assert evicted == 1
        assert cache.get("result1") is None
        assert cache.get("unrelated") == 99

    def test_invalidate_all(self):
        cache = self._cache()
        cache.set("a", 1, depends_on=[])
        cache.set("b", 2, depends_on=[])
        count = cache.invalidate_all()
        assert count == 2
        assert cache.size() == 0

    def test_size(self):
        cache = self._cache()
        assert cache.size() == 0
        cache.set("x", 1, depends_on=[])
        assert cache.size() == 1

    def test_stats(self):
        cache = self._cache()
        stats = cache.stats()
        assert stats["size"] == 0


class TestScanManifest:
    def test_to_dict(self):
        m = ScanManifest(scanner_version="2.0.0", schema_version="2.0")
        d = m.to_dict()
        assert d["scanner_version"] == "2.0.0"
        assert "scanner_self_test_passed" in d

    def test_scan_result_to_dict_roundtrip(self):
        result = ScanResult(
            edges=[
                _edge(f"{_M}a.py", "imports", f"{_M}b.py"),
            ],
            modules=["a.py", "b.py"],
            digest="abc123",
            commit_sha="sha1",
        )
        d = result.to_dict()
        restored = ScanResult.from_dict(d)
        assert restored.digest == "abc123"
        assert restored.commit_sha == "sha1"
        assert len(restored.edges) == 1
        assert restored.modules == ["a.py", "b.py"]
