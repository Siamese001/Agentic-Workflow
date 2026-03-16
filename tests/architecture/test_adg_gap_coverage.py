"""Architecture tests for ADG gap-coverage additions (Gaps 1-5).

Covers:
  G4  - Inter-module call graph (_InternalCallGraphVisitor)        [Gap 1]
  GT  - Test traceability graph (_TestTraceabilityVisitor)          [Gap 2]
  GV  - Layer violation graph (_emit_layer_violation_edges)         [Gap 3+4]
  GG  - Governance plane graph (_GovernancePlaneVisitor)            [Gap 5]
  ScanManifest new fields: layer_violation_count, test_covers_count,
                            inter_module_call_count, governance_plane_count
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanResult,
    _emit_layer_violation_edges,
    _GovernancePlaneVisitor,
    _InternalCallGraphVisitor,
    _TestTraceabilityVisitor,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_gap_coverage")
_emit_applies_guardrail("p0", "test_adg_gap_coverage", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_gap_coverage", "policy_binding")
_emit_snapshots_state("p0", "test_adg_gap_coverage", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_gap_coverage", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_gap_coverage", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_gap_coverage", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_gap_coverage", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_gap_coverage", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_gap_coverage", "p4obs", "alert")
_emit_links_incident_trace("test_adg_gap_coverage", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_gap_coverage", "p3lm", "pattern")
_emit_records_learning_event("test_adg_gap_coverage", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_gap_coverage", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_gap_coverage", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_gap_coverage", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_gap_coverage", "p3lm", "policy")
_emit_stores_learning_state("test_adg_gap_coverage", "p3lm", "state")
_emit_records_execution_trace("test_adg_gap_coverage", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_gap_coverage", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_gap_coverage", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_gap_coverage", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_gap_coverage", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_gap_coverage", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_gap_coverage", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_gap_coverage", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_gap_coverage", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_gap_coverage", "context_pull")
_emit_pulls_context("p1", "test_adg_gap_coverage", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_coverage", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_coverage", "uwg_term_2")
_emit_writes_through("p1", "test_adg_gap_coverage", "write_through")
_emit_writes_through("p1", "test_adg_gap_coverage", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_gap_coverage", "safety_validation")
_emit_invokes_eval("p1", "test_adg_gap_coverage", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_gap_coverage", "routing_commit")
emit_replay_key("p0", "test_adg_gap_coverage")
emit_determinism_digest("p0", "test_adg_gap_coverage")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_gap_coverage", "execution_auth")
_emit_validates_capability("p2", "test_adg_gap_coverage", "capability_check")
_emit_routes_to_capability("p2", "test_adg_gap_coverage", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_gap_coverage", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_gap_coverage", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_gap_coverage", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_gap_coverage", "exec_output")
_emit_dispatches_agent("p3", "test_adg_gap_coverage", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_gap_coverage", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_gap_coverage", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_gap_coverage", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_gap_coverage", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_gap_coverage", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_gap_coverage", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_gap_coverage", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_gap_coverage", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_gap_coverage", "eval_metric")
_emit_stores_embedding("p4", "test_adg_gap_coverage", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_gap_coverage", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_gap_coverage", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(source: str) -> ast.Module:
    return ast.parse(source)


def _run_icg(source: str, source_file: str = "agentic_core/some/mod.py") -> list[Edge]:
    tree = _parse(source)
    visitor = _InternalCallGraphVisitor("ADG::Module::agentic_core/some/mod.py", source_file)
    visitor.visit(tree)
    return visitor.edges


def _run_tt(source: str, source_file: str = "tests/unit/test_foo.py") -> list[Edge]:
    tree = _parse(source)
    visitor = _TestTraceabilityVisitor("ADG::Module::tests/unit/test_foo.py", source_file)
    visitor.visit(tree)
    return visitor.edges


def _run_gov(source: str, source_file: str = "agentic_core/some/mod.py") -> list[Edge]:
    tree = _parse(source)
    visitor = _GovernancePlaneVisitor("ADG::Module::agentic_core/some/mod.py", source_file)
    visitor.visit(tree)
    return visitor.edges


def _make_scan_result_with_edges(edges: list[Edge]) -> ScanResult:
    return ScanResult(edges=sorted(set(edges)), modules=[])


# ---------------------------------------------------------------------------
# Gap 1: Inter-module call graph (G4)
# ---------------------------------------------------------------------------


class TestInternalCallGraphVisitor:
    """G4: Calls between internal modules."""

    def test_calls_edge_emitted_for_imported_internal_symbol(self):
        src = """
from agentic_core.adg.schema import canonical_name
result = canonical_name("Module", "foo.py")
"""
        edges = _run_icg(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "calls"
        assert e.edge_kind == "call"
        assert "canonical_name" in e.symbol

    def test_calls_edge_for_import_alias(self):
        src = """
from agentic_core.adg.schema import canonical_name as cn
x = cn("Layer", "L0")
"""
        edges = _run_icg(src)
        assert any(e.relation_type == "calls" for e in edges)

    def test_no_calls_edge_for_stdlib(self):
        src = """
from pathlib import Path
p = Path("/tmp")
"""
        edges = _run_icg(src)
        assert not edges

    def test_no_calls_edge_for_external_sdk(self):
        src = """
import openai
openai.ChatCompletion.create(model="gpt-4", messages=[])
"""
        edges = _run_icg(src)
        assert not edges

    def test_calls_edge_for_apps_rg_import(self):
        src = """
from apps_rg.engines.ats_compatibility_engine import run_check
run_check()
"""
        edges = _run_icg(src)
        assert any(e.relation_type == "calls" for e in edges)

    def test_multiple_calls_same_symbol_deduplicated_on_set(self):
        src = """
from agentic_core.adg.schema import canonical_name
x = canonical_name("Module", "a.py")
y = canonical_name("Module", "b.py")
"""
        edges = _run_icg(src)
        # Two calls at different line_nos → two edges (frozen dataclass, different line_no)
        calls = [e for e in edges if e.relation_type == "calls"]
        assert len(calls) == 2

    def test_calls_edge_for_plain_import(self):
        src = """
import agentic_core
agentic_core.something()
"""
        edges = _run_icg(src)
        # `agentic_core` mapped via plain `import agentic_core` → local name `agentic_core`
        assert any(e.relation_type == "calls" for e in edges)

    def test_line_number_captured(self):
        src = """
from agentic_core.adg.schema import canonical_name

result = canonical_name("Module", "x.py")
"""
        edges = _run_icg(src)
        assert edges[0].line_no == 4


# ---------------------------------------------------------------------------
# Gap 2: Test traceability graph (GT)
# ---------------------------------------------------------------------------


class TestTestTraceabilityVisitor:
    """GT: covers edges from test files to production modules."""

    def test_covers_edge_for_internal_import_from(self):
        src = """
from agentic_core.adg.schema import canonical_name
"""
        edges = _run_tt(src)
        assert len(edges) == 1
        assert edges[0].relation_type == "covers"
        assert edges[0].symbol == "agentic_core.adg.schema"

    def test_covers_edge_for_plain_import(self):
        src = """
import agentic_core
"""
        edges = _run_tt(src)
        assert any(e.relation_type == "covers" for e in edges)

    def test_no_covers_edge_for_non_test_file(self):
        src = """
from agentic_core.adg.schema import canonical_name
"""
        tree = _parse(src)
        visitor = _TestTraceabilityVisitor(
            "ADG::Module::agentic_core/some/production.py",
            "agentic_core/some/production.py",  # NOT a test file
        )
        visitor.visit(tree)
        assert not visitor.edges

    def test_no_covers_edge_for_stdlib_in_test(self):
        src = """
import os
from pathlib import Path
"""
        edges = _run_tt(src)
        assert not edges

    def test_covers_edge_for_apps_shared_import(self):
        src = """
from apps_shared.reasoning import InfrastructureOrchestrator
"""
        edges = _run_tt(src)
        assert any(e.relation_type == "covers" for e in edges)

    def test_covers_edge_uses_module_not_symbol(self):
        src = """
from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
"""
        edges = _run_tt(src)
        assert len(edges) == 1
        # symbol should be the module path, not the class name
        assert edges[0].symbol == "agentic_core.L2_execution.UniversalWriteGateway"

    def test_test_file_under_nested_path(self):
        src = """
from agentic_core.adg.schema import canonical_name
"""
        tree = _parse(src)
        visitor = _TestTraceabilityVisitor(
            "ADG::Module::tests/integration/test_foo.py",
            "tests/integration/test_foo.py",
        )
        visitor.visit(tree)
        assert any(e.relation_type == "covers" for e in visitor.edges)


# ---------------------------------------------------------------------------
# Gap 3+4: Layer violation edges (GV)
# ---------------------------------------------------------------------------


class TestLayerViolationEdges:
    """GV: violates edges for forbidden cross-layer imports."""

    def _make_import_edge(
        self,
        from_rel: str,
        sym: str,
        line_no: int = 1,
    ) -> Edge:
        from agentic_core.adg.schema import canonical_name

        return Edge(
            from_name=canonical_name("Module", from_rel),
            relation_type="imports",
            to_name=canonical_name("Symbol", sym),
            edge_kind="import",
            source_file=from_rel,
            line_no=line_no,
            symbol=sym,
        )

    def test_violation_emitted_for_upward_import(self):
        """L0 importing from L5 is forbidden."""
        edge = self._make_import_edge(
            "agentic_core/L0_routing/engines/router.py",
            "agentic_core.L5_safety.config.something",
        )
        result = _make_scan_result_with_edges([edge])
        violations = _emit_layer_violation_edges(result)
        assert len(violations) >= 1
        assert all(v.relation_type == "violates" for v in violations)

    def test_no_violation_for_allowed_downward_import(self):
        """L5 importing from L0 is allowed."""
        edge = self._make_import_edge(
            "agentic_core/L5_safety/config/something.py",
            "agentic_core.L0_routing.engines.path_router",
        )
        result = _make_scan_result_with_edges([edge])
        violations = _emit_layer_violation_edges(result)
        assert not violations

    def test_no_violation_for_same_layer_import(self):
        edge = self._make_import_edge(
            "agentic_core/L2_execution/audit/ledger.py",
            "agentic_core.L2_execution.config.something",
        )
        result = _make_scan_result_with_edges([edge])
        violations = _emit_layer_violation_edges(result)
        assert not violations

    def test_violation_deduplication(self):
        """Two imports from same module to same forbidden layer → one violation edge."""
        edge1 = self._make_import_edge(
            "agentic_core/L0_routing/engines/router.py",
            "agentic_core.L5_safety.config.foo",
            line_no=1,
        )
        edge2 = self._make_import_edge(
            "agentic_core/L0_routing/engines/router.py",
            "agentic_core.L5_safety.config.bar",
            line_no=2,
        )
        result = _make_scan_result_with_edges([edge1, edge2])
        violations = _emit_layer_violation_edges(result)
        # Deduplicated: same from_name + violates + to_layer
        assert len(violations) == 1

    def test_violation_symbol_encodes_layer_pair(self):
        edge = self._make_import_edge(
            "agentic_core/L0_routing/engines/router.py",
            "agentic_core.L5_safety.config.foo",
        )
        result = _make_scan_result_with_edges([edge])
        violations = _emit_layer_violation_edges(result)
        assert violations[0].symbol == "L0->L5"

    def test_non_import_edges_ignored(self):
        from agentic_core.adg.schema import canonical_name

        non_import = Edge(
            from_name=canonical_name("Module", "agentic_core/L0_routing/engines/router.py"),
            relation_type="implements",
            to_name=canonical_name("Symbol", "agentic_core.L5_safety.SomeBase"),
            edge_kind="import",
            source_file="agentic_core/L0_routing/engines/router.py",
            line_no=1,
            symbol="agentic_core.L5_safety.SomeBase",
        )
        result = _make_scan_result_with_edges([non_import])
        violations = _emit_layer_violation_edges(result)
        assert not violations

    def test_l_unknown_edges_skipped(self):
        """Edges whose layer resolves to L_UNKNOWN are skipped, not misclassified."""
        edge = self._make_import_edge(
            "some_random_root/module.py",  # → L_UNKNOWN
            "agentic_core.L5_safety.config.foo",
        )
        result = _make_scan_result_with_edges([edge])
        violations = _emit_layer_violation_edges(result)
        assert not violations


# ---------------------------------------------------------------------------
# Gap 5: Governance plane graph (GG)
# ---------------------------------------------------------------------------


class TestGovernancePlaneVisitor:
    """GG: writes_through and routes_through edges for mutation governance."""

    def test_writes_through_for_uwg_call(self):
        src = """
from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
uwg = UniversalWriteGateway()
uwg.execute_write("foo", b"data")
"""
        edges = _run_gov(src)
        wt = [e for e in edges if e.relation_type == "writes_through"]
        assert len(wt) >= 1
        assert all("UniversalWriteGateway" in e.to_name for e in wt)

    def test_writes_through_for_submit_instruction(self):
        src = """
submit_instruction(packet)
"""
        edges = _run_gov(src)
        assert any(e.relation_type == "writes_through" for e in edges)

    def test_routes_through_for_sovereign_gateway(self):
        src = """
sovereign_gateway.run(prompt)
"""
        edges = _run_gov(src)
        rt = [e for e in edges if e.relation_type == "routes_through"]
        assert len(rt) >= 1

    def test_routes_through_for_healing_orchestrator(self):
        src = """
HealingOrchestrator().run()
"""
        edges = _run_gov(src)
        rt = [e for e in edges if e.relation_type == "routes_through"]
        assert len(rt) >= 1

    def test_routes_through_for_run_healing(self):
        src = """
run_healing(context)
"""
        edges = _run_gov(src)
        assert any(e.relation_type == "routes_through" for e in edges)

    def test_no_governance_edge_for_unrelated_call(self):
        src = """
some_random_function(arg)
"""
        edges = _run_gov(src)
        assert not edges

    def test_governance_edge_kind(self):
        src = """
submit_instruction(pkt)
"""
        edges = _run_gov(src)
        wt = [e for e in edges if e.relation_type == "writes_through"]
        assert all(e.edge_kind == "write" for e in wt)

    def test_routes_through_edge_kind(self):
        src = """
replay_run(session_id)
"""
        edges = _run_gov(src)
        rt = [e for e in edges if e.relation_type == "routes_through"]
        assert all(e.edge_kind == "call" for e in rt)


# ---------------------------------------------------------------------------
# ScanManifest new field tests
# ---------------------------------------------------------------------------


class TestScanManifestNewFields:
    """Verify new manifest fields exist and are initialized correctly."""

    def test_manifest_has_layer_violation_count(self):
        from agentic_core.adg.extraction.static_scanner import ScanManifest

        m = ScanManifest()
        assert hasattr(m, "layer_violation_count")
        assert m.layer_violation_count == 0

    def test_manifest_has_test_covers_count(self):
        from agentic_core.adg.extraction.static_scanner import ScanManifest

        m = ScanManifest()
        assert hasattr(m, "test_covers_count")
        assert m.test_covers_count == 0

    def test_manifest_has_inter_module_call_count(self):
        from agentic_core.adg.extraction.static_scanner import ScanManifest

        m = ScanManifest()
        assert hasattr(m, "inter_module_call_count")
        assert m.inter_module_call_count == 0

    def test_manifest_has_governance_plane_count(self):
        from agentic_core.adg.extraction.static_scanner import ScanManifest

        m = ScanManifest()
        assert hasattr(m, "governance_plane_count")
        assert m.governance_plane_count == 0

    def test_manifest_to_dict_includes_new_fields(self):
        from agentic_core.adg.extraction.static_scanner import ScanManifest

        m = ScanManifest(
            layer_violation_count=3,
            test_covers_count=10,
            inter_module_call_count=42,
            governance_plane_count=5,
        )
        d = m.to_dict()
        assert d["layer_violation_count"] == 3
        assert d["test_covers_count"] == 10
        assert d["inter_module_call_count"] == 42
        assert d["governance_plane_count"] == 5


# ---------------------------------------------------------------------------
# Self-test coverage
# ---------------------------------------------------------------------------


class TestScannerSelfTest:
    """Verify that run_scanner_self_test still passes with new graph types."""

    def test_self_test_passes(self):
        from agentic_core.adg.extraction.static_scanner import run_scanner_self_test

        assert run_scanner_self_test() is True
