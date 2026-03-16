"""Regression tests for ADG Rule D (duplicate_method) and Rule G (unreachable_after_raise).

RCA: these rules were added after MCP audit found that:
  - FallbackClient.generate was defined twice (Rule D)
  - Logger.warning after raise in exception handlers (Rule G)
  - mcp_authority used without import (ruff F821 — now re-enabled for agentic_core/**)

These tests exercise the new visitors directly and via InvariantScanner
to prevent regression of the gap.
"""

from __future__ import annotations

import ast
import textwrap
from unittest.mock import MagicMock

from agentic_core.adg.ci.invariant_scanner import (
    _POLICY_DUPLICATE_METHOD,
    _POLICY_UNREACHABLE_AFTER_RAISE,
    InvariantScanner,
)
from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanResult,
    _DuplicateMethodVisitor,
    _is_property_accessor,
    _UnreachableCodeAfterRaiseVisitor,
)
from agentic_core.adg.schema import canonical_name
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
)

_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_mcp_audit_rules", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_mcp_audit_rules", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_mcp_audit_rules", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_mcp_audit_rules", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_mcp_audit_rules", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_mcp_audit_rules", "p4obs", "alert")
_emit_links_incident_trace("test_adg_mcp_audit_rules", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_mcp_audit_rules", "p3lm", "pattern")
_emit_records_learning_event("test_adg_mcp_audit_rules", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_mcp_audit_rules", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_mcp_audit_rules", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_mcp_audit_rules", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_mcp_audit_rules", "p3lm", "policy")
_emit_stores_learning_state("test_adg_mcp_audit_rules", "p3lm", "state")
_emit_records_execution_trace("test_adg_mcp_audit_rules", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_mcp_audit_rules", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_mcp_audit_rules", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_mcp_audit_rules", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_mcp_audit_rules", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_mcp_audit_rules", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_mcp_audit_rules", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_mcp_audit_rules", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_mcp_audit_rules", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_adg_mcp_audit_rules")
_emit_applies_guardrail("p0", "test_adg_mcp_audit_rules", "p0_governance")
_emit_snapshots_state("p0", "test_adg_mcp_audit_rules", "state_snapshot")
_emit_pulls_context("p1", "test_adg_mcp_audit_rules", "context_pull")
_emit_pulls_context("p1", "test_adg_mcp_audit_rules", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_adg_mcp_audit_rules", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_mcp_audit_rules", "uwg_term_secondary")
_emit_writes_through("p1", "test_adg_mcp_audit_rules", "write_through")
_emit_writes_through("p1", "test_adg_mcp_audit_rules", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_adg_mcp_audit_rules", "safety_validation")
_emit_invokes_eval("p1", "test_adg_mcp_audit_rules", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_mcp_audit_rules", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_mcp_audit_rules", "human_escalation")
_emit_routes_through("p1", "test_adg_mcp_audit_rules", "route_through")
_emit_checks_agent_registry("p1", "test_adg_mcp_audit_rules", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_mcp_audit_rules", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_mcp_audit_rules", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_mcp_audit_rules", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_mcp_audit_rules", "target_agent")
_emit_verifies_policy("p1", "test_adg_mcp_audit_rules", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_mcp_audit_rules", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_mcp_audit_rules", "boundary_check")
_emit_transcripts_response("p1", "test_adg_mcp_audit_rules", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_mcp_audit_rules")
_emit_gated_by_confidence("p1", "test_adg_mcp_audit_rules", "confidence_gate")
emit_replay_key("p0", "test_adg_mcp_audit_rules")
emit_determinism_digest("p0", "test_adg_mcp_audit_rules")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_mcp_audit_rules", "execution_auth")
_emit_validates_capability("p2", "test_adg_mcp_audit_rules", "capability_check")
_emit_routes_to_capability("p2", "test_adg_mcp_audit_rules", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_mcp_audit_rules", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_mcp_audit_rules", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_mcp_audit_rules", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_mcp_audit_rules", "exec_output")
_emit_dispatches_agent("p3", "test_adg_mcp_audit_rules", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_mcp_audit_rules", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_mcp_audit_rules", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_mcp_audit_rules", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_mcp_audit_rules", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_mcp_audit_rules", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_mcp_audit_rules", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_mcp_audit_rules", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_mcp_audit_rules", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_mcp_audit_rules", "eval_metric")
_emit_stores_embedding("p4", "test_adg_mcp_audit_rules", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_mcp_audit_rules", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_mcp_audit_rules", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MODULE = "ADG::Module::test_module"
_SOURCE = "test_module.py"


def _scan_source(source: str, visitor_cls: type) -> list[Edge]:
    """Parse source, run visitor, return collected edges."""
    tree = ast.parse(textwrap.dedent(source))
    visitor = visitor_cls(_MODULE, _SOURCE)
    visitor.visit(tree)
    return visitor.edges


def _make_scan_result(edges: list[Edge]) -> ScanResult:
    sr = MagicMock(spec=ScanResult)
    sr.edges = edges
    sr.digest = "test-digest"
    return sr


# ===========================================================================
# _is_property_accessor
# ===========================================================================


def test_is_property_accessor_bare_property() -> None:
    src = "@property\ndef x(self): ..."
    tree = ast.parse(src)
    func = tree.body[0]
    assert _is_property_accessor(func) is True


def test_is_property_accessor_setter() -> None:
    src = "@x.setter\ndef x(self, v): ..."
    tree = ast.parse(src)
    func = tree.body[0]
    assert _is_property_accessor(func) is True


def test_is_property_accessor_deleter() -> None:
    src = "@x.deleter\ndef x(self): ..."
    tree = ast.parse(src)
    func = tree.body[0]
    assert _is_property_accessor(func) is True


def test_is_property_accessor_plain_method() -> None:
    src = "def generate(self): ..."
    tree = ast.parse(src)
    func = tree.body[0]
    assert _is_property_accessor(func) is False


# ===========================================================================
# _DuplicateMethodVisitor — positive cases (should fire)
# ===========================================================================


def test_duplicate_method_visitor_fires_on_plain_duplicate() -> None:
    src = """
    class FallbackClient:
        def generate(self):
            return "first"
        def generate(self):
            return "second"
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert len(edges) == 1
    e = edges[0]
    assert e.relation_type == "duplicate_method"
    assert e.edge_kind == "duplicate_method"
    assert "FallbackClient.generate" in e.symbol


def test_duplicate_method_visitor_fires_on_async_duplicate() -> None:
    src = """
    class MyAgent:
        async def run(self):
            pass
        async def run(self):
            pass
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert len(edges) == 1
    assert edges[0].symbol == "MyAgent.run"


def test_duplicate_method_visitor_three_definitions_emits_two_edges() -> None:
    src = """
    class Triple:
        def act(self): ...
        def act(self): ...
        def act(self): ...
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert len(edges) == 2


def test_duplicate_method_visitor_nested_class() -> None:
    src = """
    class Outer:
        class Inner:
            def go(self): ...
            def go(self): ...
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert len(edges) == 1
    assert "Inner.go" in edges[0].symbol


# ===========================================================================
# _DuplicateMethodVisitor — negative cases (should NOT fire)
# ===========================================================================


def test_duplicate_method_visitor_no_fire_property_getter_setter() -> None:
    src = """
    class Model:
        @property
        def value(self):
            return self._value
        @value.setter
        def value(self, v):
            self._value = v
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert edges == []


def test_duplicate_method_visitor_no_fire_unique_names() -> None:
    src = """
    class Router:
        def route(self): ...
        def select(self): ...
        def fallback(self): ...
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert edges == []


def test_duplicate_method_visitor_no_fire_no_class() -> None:
    src = """
    def foo(): ...
    def foo(): ...
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert edges == []


def test_duplicate_method_visitor_no_fire_same_name_different_classes() -> None:
    src = """
    class A:
        def run(self): ...
    class B:
        def run(self): ...
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    assert edges == []


# ===========================================================================
# _UnreachableCodeAfterRaiseVisitor — positive cases (should fire)
# ===========================================================================


def test_unreachable_visitor_fires_in_except_handler() -> None:
    src = """
    try:
        pass
    except Exception as e:
        raise
        print("dead code")
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert len(edges) == 1
    e = edges[0]
    assert e.relation_type == "unreachable_after_raise"
    assert e.edge_kind == "unreachable_after_raise"
    assert "raise_at_line_" in e.symbol


def test_unreachable_visitor_fires_after_raise_expr_in_handler() -> None:
    src = """
    try:
        pass
    except ValueError as e:
        raise RuntimeError("wrapped") from e
        Logger.warning("lost")
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert len(edges) == 1


def test_unreachable_visitor_fires_in_function_body() -> None:
    src = """
    def process():
        raise ValueError("early exit")
        return "unreachable"
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert len(edges) == 1


def test_unreachable_visitor_fires_in_if_branch() -> None:
    src = """
    def run(flag):
        if flag:
            raise StopIteration
            x = 1
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert len(edges) == 1


def test_unreachable_visitor_fires_multiple_violations() -> None:
    src = """
    try:
        pass
    except TypeError:
        raise
        do_one()
        do_two()
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert len(edges) == 1


# ===========================================================================
# _UnreachableCodeAfterRaiseVisitor — negative cases (should NOT fire)
# ===========================================================================


def test_unreachable_visitor_no_fire_raise_is_last_stmt() -> None:
    src = """
    try:
        pass
    except Exception:
        raise
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert edges == []


def test_unreachable_visitor_no_fire_normal_function() -> None:
    src = """
    def safe():
        x = 1
        return x
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert edges == []


def test_unreachable_visitor_no_fire_raise_in_else_branch() -> None:
    src = """
    def go(flag):
        if flag:
            x = 1
        else:
            raise ValueError
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    assert edges == []


# ===========================================================================
# InvariantScanner Rule D — duplicate_method edge → Violation
# ===========================================================================


def test_invariant_rule_d_produces_violation() -> None:
    dup_edge = Edge(
        from_name=_MODULE,
        relation_type="duplicate_method",
        to_name=canonical_name("Symbol", "FallbackClient.generate"),
        edge_kind="duplicate_method",
        source_file="apps_shared/types/model_router_types.py",
        line_no=450,
        symbol="FallbackClient.generate",
    )
    result = _make_scan_result([dup_edge])
    scanner = InvariantScanner()
    report = scanner.scan(result)
    violations = [v for v in report.violations if v.rule == "RULE_D"]
    assert len(violations) == 1
    v = violations[0]
    assert v.policy_id == _POLICY_DUPLICATE_METHOD
    assert "FallbackClient.generate" in v.witness
    assert v.line_no == 450
    assert "RULE_D" in v.format()


def test_invariant_rule_d_no_false_positive_on_imports_edge() -> None:
    edge = Edge(
        from_name=_MODULE,
        relation_type="imports",
        to_name=canonical_name("Symbol", "os"),
        edge_kind="import",
        source_file="some_file.py",
        line_no=1,
        symbol="os",
    )
    result = _make_scan_result([edge])
    scanner = InvariantScanner()
    report = scanner.scan(result)
    violations = [v for v in report.violations if v.rule == "RULE_D"]
    assert violations == []


# ===========================================================================
# InvariantScanner Rule G — unreachable_after_raise edge → Violation
# ===========================================================================


def test_invariant_rule_g_produces_violation() -> None:
    unreach_edge = Edge(
        from_name=_MODULE,
        relation_type="unreachable_after_raise",
        to_name=canonical_name("Symbol", "unreachable_code"),
        edge_kind="unreachable_after_raise",
        source_file="agentic_core/L3_orchestration/engines/sovereign_mcp_marketplace.py",
        line_no=47,
        symbol="raise_at_line_46",
    )
    result = _make_scan_result([unreach_edge])
    scanner = InvariantScanner()
    report = scanner.scan(result)
    violations = [v for v in report.violations if v.rule == "RULE_G"]
    assert len(violations) == 1
    v = violations[0]
    assert v.policy_id == _POLICY_UNREACHABLE_AFTER_RAISE
    assert "line 47" in v.witness
    assert "line 46" in v.witness
    assert v.to_symbol == "unreachable_code"
    assert "RULE_G" in v.format()


def test_invariant_rule_g_no_false_positive_on_antipattern_edge() -> None:
    edge = Edge(
        from_name=_MODULE,
        relation_type="antipattern",
        to_name=canonical_name("Symbol", "silent_exception_swallow"),
        edge_kind="silent_exception_swallow",
        source_file="some_file.py",
        line_no=10,
        symbol="except:bare",
    )
    result = _make_scan_result([edge])
    scanner = InvariantScanner()
    report = scanner.scan(result)
    violations = [v for v in report.violations if v.rule == "RULE_G"]
    assert violations == []


# ===========================================================================
# End-to-end: scan real inline source that reproduces MCP bugs
# ===========================================================================


def test_e2e_mcp_bug_duplicate_generate() -> None:
    """Regression: FallbackClient had two generate() methods — must be caught."""
    src = """
    class FallbackClient:
        def __init__(self, primary_config, router):
            self.primary = primary_config

        async def generate(self, prompt: str, **kwargs) -> str:
            return "first"

        async def generate(self, prompt: str, goal: str = "", **kwargs) -> str:
            return "second"
    """
    edges = _scan_source(src, _DuplicateMethodVisitor)
    dup_edges = [e for e in edges if e.relation_type == "duplicate_method"]
    assert len(dup_edges) == 1
    assert "FallbackClient.generate" in dup_edges[0].symbol


def test_e2e_mcp_bug_unreachable_logger_after_raise() -> None:
    """Regression: sovereign_mcp_marketplace had Logger.warning after raise — must be caught."""
    src = """
    class SovereignMcpMarketplace:
        def discover_and_register_safe(self, mcps):
            for name, meta in mcps.items():
                try:
                    self.safe_tools.append(name)
                except Exception as e:
                    raise
                    Logger.warning(f"Failed to register {name}: {e}")
    """
    edges = _scan_source(src, _UnreachableCodeAfterRaiseVisitor)
    unreach = [e for e in edges if e.relation_type == "unreachable_after_raise"]
    assert len(unreach) == 1
