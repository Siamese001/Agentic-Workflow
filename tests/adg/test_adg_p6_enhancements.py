"""P6/P7 ADG Enhancement Tests — E20 through E25.

Tests for:
  E20: Prompt lifecycle nodes (_PromptSlotVisitor in static_scanner)
  E21: Prompt authority DAG enforcement (prompt_authority.py)
  E22: CLI subcommands (prompt-authority, prompt-lifecycle, prompt-impact)
  E24: Prompt impact analyzer (prompt_impact.py)
  E25: Prompt drift detector (prompt_drift.py)
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_p6_enhancements")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_p6_enhancements", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_p6_enhancements", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_p6_enhancements", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_p6_enhancements", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_p6_enhancements", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_p6_enhancements", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_p6_enhancements", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_p6_enhancements", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_p6_enhancements", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_p6_enhancements", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_p6_enhancements", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_p6_enhancements", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_p6_enhancements", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_p6_enhancements", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_p6_enhancements", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_p6_enhancements", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_p6_enhancements", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_p6_enhancements", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_p6_enhancements", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_p6_enhancements", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_p6_enhancements", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_p6_enhancements", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_p6_enhancements", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_p6_enhancements", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_p6_enhancements", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_p6_enhancements", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_p6_enhancements", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_p6_enhancements", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_p6_enhancements", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_p6_enhancements", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_p6_enhancements", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_p6_enhancements", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_p6_enhancements", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_p6_enhancements", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_p6_enhancements", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_p6_enhancements", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_p6_enhancements", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_p6_enhancements", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_p6_enhancements", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_p6_enhancements", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_p6_enhancements", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_p6_enhancements", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_p6_enhancements", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_p6_enhancements", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_p6_enhancements", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_p6_enhancements", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_p6_enhancements")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_p6_enhancements", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_p6_enhancements")
# REMOVED: emit_determinism_digest("p0", "test_adg_p6_enhancements")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_p6_enhancements", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_p6_enhancements", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_p6_enhancements", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_p6_enhancements", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_p6_enhancements", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_p6_enhancements", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_p6_enhancements", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_p6_enhancements", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_p6_enhancements", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_p6_enhancements", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_p6_enhancements", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_p6_enhancements", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_p6_enhancements", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_p6_enhancements", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_p6_enhancements", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_p6_enhancements", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_p6_enhancements", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_p6_enhancements", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_p6_enhancements", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_p6_enhancements", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers: build minimal ScanResult / Edge fixtures without full scanner
# ---------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class _Edge:
    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""


@dataclass
class _ScanResult:
    edges: list[_Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = "test-digest"
    commit_sha: str = "abc123"

    def print_digest(self) -> None:
        pass


def _make_edge(
    from_mod: str,
    relation: str,
    to_name: str,
    edge_kind: str = "prompt_generation",
    source_file: str = "test.py",
    line_no: int = 1,
    symbol: str = "",
) -> _Edge:
    return _Edge(
        from_name=f"ADG::Module::{from_mod}",
        relation_type=relation,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=line_no,
        symbol=symbol,
    )


# ---------------------------------------------------------------------------
# E20: _PromptSlotVisitor tests
# ---------------------------------------------------------------------------


class TestPromptSlotVisitor:
    """Tests for _PromptSlotVisitor AST visitor."""

    def _run_visitor(self, code: str, source_file: str = "test_module.py") -> list:
        from agentic_core.adg.extraction.static_scanner import _PromptSlotVisitor
        from agentic_core.adg.schema_util import canonical_name

        module_adg = canonical_name("Module", source_file)
        tree = ast.parse(code)
        visitor = _PromptSlotVisitor(module_adg, source_file)
        visitor.visit(tree)
        return visitor.edges

    def test_assemble_call_with_slot_kwargs_emits_generates_prompt(self):
        code = """
AirlockAssembler.assemble(
    s0_system="You are an agent.",
    i0_instructional="Follow rules.",
    c0_context="Some context.",
    u0_user_prompt="User request.",
)
"""
        edges = self._run_visitor(code)
        relations = {e.relation_type for e in edges}
        assert "generates_prompt" in relations

    def test_assemble_detects_all_slot_types(self):
        code = """
AirlockAssembler.assemble(
    s0_system="sys",
    d0_injections="fence",
    i0_instructional="instr",
    c0_context="ctx",
    u0_user_prompt="user",
)
"""
        edges = self._run_visitor(code)
        slots_found = set()
        for e in edges:
            if e.relation_type == "generates_prompt":
                sym = e.symbol
                slot = sym.split(":")[0] if ":" in sym else ""
                if slot:
                    slots_found.add(slot)
        assert "S0" in slots_found
        assert "I0" in slots_found
        assert "C0" in slots_found
        assert "U0" in slots_found

    def test_get_prompt_call_emits_consumes_prompt(self):
        code = """
content = get_prompt("SOVEREIGN_SYSTEM_CORE")
"""
        edges = self._run_visitor(code)
        relations = {e.relation_type for e in edges}
        assert "consumes_prompt" in relations

    def test_get_constitution_call_emits_consumes_prompt(self):
        code = """
const = get_constitution()
"""
        edges = self._run_visitor(code)
        relations = {e.relation_type for e in edges}
        assert "consumes_prompt" in relations

    def test_plain_function_no_prompt_edges(self):
        code = """
def foo():
    x = 1 + 2
    return x
"""
        edges = self._run_visitor(code)
        assert len(edges) == 0

    def test_assembler_without_slot_kwargs_emits_assembles_into(self):
        code = """
GovernedPayload(s0_system="sys", i0_instructional="instr", c0_context="ctx", u0_user_prompt="u")
"""
        edges = self._run_visitor(code)
        # Should emit generates_prompt for each recognized kwarg
        gen_edges = [e for e in edges if e.relation_type == "generates_prompt"]
        assert len(gen_edges) >= 1

    def test_consumes_prompt_symbol_captures_key(self):
        code = """
get_prompt("TITANIUM_RESEARCHER_SYSTEM")
"""
        edges = self._run_visitor(code)
        consume_edges = [e for e in edges if e.relation_type == "consumes_prompt"]
        assert len(consume_edges) == 1
        assert "TITANIUM_RESEARCHER_SYSTEM" in consume_edges[0].symbol


# ---------------------------------------------------------------------------
# E21: Prompt authority DAG enforcement tests
# ---------------------------------------------------------------------------


class TestPromptAuthorityDetector:
    """Tests for detect_prompt_authority_violations."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)  # type: ignore[arg-type]

    def test_clean_assembly_no_violations(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        # Each module generates only ONE slot type → no cross-authority violations
        result = self._make_result(
            [
                _make_edge(
                    "agentic_core/prompt_governance/constitution.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::agentic_core/prompt_governance/constitution.py",
                    symbol="S0:s0_system",
                ),
                _make_edge(
                    "agentic_core/L0_routing/assembler.py",
                    "generates_prompt",
                    "ADG::PromptSlot::I0::agentic_core/L0_routing/assembler.py",
                    symbol="I0:i0_instructional",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert report.violation_count == 0

    def test_u0_also_generates_s0_is_violation(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        # One module generates BOTH S0 and U0 → U0_MUTATES_S0
        result = self._make_result(
            [
                _make_edge(
                    "apps_rg/agents/bad_agent.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::apps_rg/agents/bad_agent.py",
                    symbol="S0:s0_system",
                    source_file="apps_rg/agents/bad_agent.py",
                ),
                _make_edge(
                    "apps_rg/agents/bad_agent.py",
                    "generates_prompt",
                    "ADG::PromptSlot::U0::apps_rg/agents/bad_agent.py",
                    symbol="U0:u0_user_prompt",
                    source_file="apps_rg/agents/bad_agent.py",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert report.violation_count > 0
        vtypes = {v.violation_type for v in report.violations}
        assert "U0_MUTATES_S0" in vtypes

    def test_c0_generates_s0_is_violation(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        result = self._make_result(
            [
                _make_edge(
                    "apps_rg/rag/context_builder.py",
                    "generates_prompt",
                    "ADG::PromptSlot::C0::apps_rg/rag/context_builder.py",
                    symbol="C0:c0_context",
                ),
                _make_edge(
                    "apps_rg/rag/context_builder.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::apps_rg/rag/context_builder.py",
                    symbol="S0:s0_system",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert report.violation_count > 0
        vtypes = {v.violation_type for v in report.violations}
        assert "C0_MUTATES_S0" in vtypes

    def test_missing_d0_fence_detected(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        # Assembles S0 + U0 but no D0
        result = self._make_result(
            [
                _make_edge(
                    "agentic_core/L0_routing/no_fence.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::agentic_core/L0_routing/no_fence.py",
                    symbol="S0:s0_system",
                ),
                _make_edge(
                    "agentic_core/L0_routing/no_fence.py",
                    "generates_prompt",
                    "ADG::PromptSlot::U0::agentic_core/L0_routing/no_fence.py",
                    symbol="U0:u0_user_prompt",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert "agentic_core/L0_routing/no_fence.py" in report.missing_fences

    def test_slot_generators_index_populated(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        result = self._make_result(
            [
                _make_edge(
                    "agentic_core/prompt_governance/constitution.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::agentic_core/prompt_governance/constitution.py",
                    symbol="S0:s0_system",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert "agentic_core/prompt_governance/constitution.py" in report.slot_generators.get("S0", [])

    def test_severity_critical_for_s0_violations(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        result = self._make_result(
            [
                _make_edge(
                    "apps_rg/agents/risky.py",
                    "generates_prompt",
                    "ADG::PromptSlot::S0::apps_rg/agents/risky.py",
                    symbol="S0:s0_system",
                ),
                _make_edge(
                    "apps_rg/agents/risky.py",
                    "generates_prompt",
                    "ADG::PromptSlot::U0::apps_rg/agents/risky.py",
                    symbol="U0:u0_user_prompt",
                ),
            ]
        )
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        # Only check direct authority-inversion violations (not MISSING_D0_FENCE which is "high")
        authority_inversion_violations = [v for v in report.violations if v.violation_type == "U0_MUTATES_S0"]
        assert len(authority_inversion_violations) >= 1
        assert all(v.severity == "critical" for v in authority_inversion_violations)

    def test_report_to_dict_serializable(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        result = self._make_result([])
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        d = report.to_dict()
        assert "violation_count" in d
        assert "violations" in d
        assert "missing_fences" in d
        # Must be JSON serializable
        json.dumps(d)

    def test_report_summary_string(self):
        from agentic_core.adg.analysis.prompt_authority_types import detect_prompt_authority_violations

        result = self._make_result([])
        report = detect_prompt_authority_violations(result)  # type: ignore[arg-type]
        assert "violations" in report.summary
        assert "missing_d0_fences" in report.summary


# ---------------------------------------------------------------------------
# E24: Prompt impact analyzer tests
# ---------------------------------------------------------------------------


class TestPromptImpactAnalyzer:
    """Tests for analyze_prompt_impact."""

    def _make_result(self, edges: list[_Edge]) -> _ScanResult:
        return _ScanResult(edges=edges)  # type: ignore[arg-type]

    def test_empty_changed_files_no_impact(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        result = self._make_result([])
        report = analyze_prompt_impact(result, changed_files=[])  # type: ignore[arg-type]
        assert report.impacted_count == 0
        assert report.risk_label == "LOW"

    def test_changed_generator_module_shows_impact(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        edges = [
            _make_edge(
                "agentic_core/prompt_governance/core/prompt_entry_types.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::agentic_core/prompt_governance/core/prompt_entry_types.py",
                symbol="S0:s0_system",
                source_file="agentic_core/prompt_governance/core/prompt_entry_types.py",
            ),
        ]
        result = self._make_result(edges)
        report = analyze_prompt_impact(
            result,  # type: ignore[arg-type]
            changed_files=["agentic_core/prompt_governance/core/prompt_entry_types.py"],
        )
        assert report.impacted_count >= 1

    def test_s0_slot_gives_high_risk_score(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        edges = [
            _make_edge(
                "agentic_core/prompt_governance/core/prompt_entry_types.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::agentic_core/prompt_governance/core/prompt_entry_types.py",
                symbol="S0:s0_system",
                source_file="agentic_core/prompt_governance/core/prompt_entry_types.py",
            ),
        ]
        result = self._make_result(edges)
        report = analyze_prompt_impact(
            result,  # type: ignore[arg-type]
            changed_files=["agentic_core/prompt_governance/core/prompt_entry_types.py"],
        )
        assert report.risk_score > 0.5

    def test_u0_slot_lower_risk_than_s0(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        edges_s0 = [
            _make_edge(
                "mod_a.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::mod_a.py",
                symbol="S0:s0_system",
                source_file="mod_a.py",
            ),
        ]
        edges_u0 = [
            _make_edge(
                "mod_b.py",
                "generates_prompt",
                "ADG::PromptSlot::U0::mod_b.py",
                symbol="U0:u0_user_prompt",
                source_file="mod_b.py",
            ),
        ]
        r_s0 = analyze_prompt_impact(
            _ScanResult(edges=edges_s0),  # type: ignore[arg-type]
            changed_files=["mod_a.py"],
        )
        r_u0 = analyze_prompt_impact(
            _ScanResult(edges=edges_u0),  # type: ignore[arg-type]
            changed_files=["mod_b.py"],
        )
        assert r_s0.risk_score > r_u0.risk_score

    def test_consumers_traced_through_edges(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        tmpl_node = "ADG::PromptTemplate::TITANIUM_RESEARCHER_SYSTEM"
        edges = [
            _make_edge(
                "agentic_core/prompt_governance/core/prompt_entry_types.py",
                "generates_prompt",
                tmpl_node,
                symbol="S0:s0_system",
                source_file="agentic_core/prompt_governance/core/prompt_entry_types.py",
            ),
            _make_edge(
                "apps_rg/agents/titanium_agent.py",
                "consumes_prompt",
                tmpl_node,
                edge_kind="prompt_consumption",
                source_file="apps_rg/agents/titanium_agent.py",
            ),
        ]
        result = self._make_result(edges)
        report = analyze_prompt_impact(
            result,  # type: ignore[arg-type]
            changed_files=["agentic_core/prompt_governance/core/prompt_entry_types.py"],
        )
        impacted_mods = {e.module_path for e in report.impacted_modules}
        assert "apps_rg/agents/titanium_agent.py" in impacted_mods

    def test_report_to_dict_json_serializable(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        result = self._make_result([])
        report = analyze_prompt_impact(result, changed_files=[])  # type: ignore[arg-type]
        json.dumps(report.to_dict())

    def test_affected_slot_types_ordered_by_authority(self):
        from agentic_core.adg.applications.prompt_impact_config import analyze_prompt_impact

        edges = [
            _make_edge(
                "m.py",
                "generates_prompt",
                "ADG::PromptSlot::U0::m.py",
                symbol="U0:u0_user_prompt",
                source_file="m.py",
            ),
            _make_edge(
                "m.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::m.py",
                symbol="S0:s0_system",
                source_file="m.py",
            ),
        ]
        report = analyze_prompt_impact(
            _ScanResult(edges=edges),  # type: ignore[arg-type]
            changed_files=["m.py"],
        )
        if len(report.affected_slot_types) >= 2:
            # S0 should appear before U0 (lower authority rank = higher importance)
            assert report.affected_slot_types.index("S0") < report.affected_slot_types.index("U0")


# ---------------------------------------------------------------------------
# E25: Prompt drift detector tests
# ---------------------------------------------------------------------------


class TestPromptDriftDetector:
    """Tests for detect_prompt_drift."""

    def test_identical_scans_no_drift(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        edge = _make_edge(
            "agentic_core/prompt_governance/core/prompt_entry_types.py",
            "generates_prompt",
            "ADG::PromptSlot::S0::test.py",
            symbol="S0:s0_system",
        )
        r1 = _ScanResult(edges=[edge])
        r2 = _ScanResult(edges=[edge])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert report.total_added == 0
        assert report.total_removed == 0

    def test_added_generator_detected(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        old_edge = _make_edge(
            "mod_a.py", "generates_prompt", "ADG::PromptSlot::S0::mod_a.py", symbol="S0:s0_system"
        )
        new_edge = _make_edge(
            "mod_b.py", "generates_prompt", "ADG::PromptSlot::I0::mod_b.py", symbol="I0:i0_instructional"
        )
        r1 = _ScanResult(edges=[old_edge])
        r2 = _ScanResult(edges=[old_edge, new_edge])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert report.total_added == 1
        assert len(report.added_generators) == 1
        assert report.added_generators[0].from_module == "mod_b.py"

    def test_removed_generator_detected(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        edge = _make_edge(
            "mod_a.py", "generates_prompt", "ADG::PromptSlot::S0::mod_a.py", symbol="S0:s0_system"
        )
        r1 = _ScanResult(edges=[edge])
        r2 = _ScanResult(edges=[])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert report.total_removed == 1
        assert len(report.removed_generators) == 1

    def test_s0_removal_is_high_risk(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        edge = _make_edge(
            "agentic_core/constitution.py",
            "generates_prompt",
            "ADG::PromptSlot::S0::agentic_core/constitution.py",
            symbol="S0:s0_system",
        )
        r1 = _ScanResult(edges=[edge])
        r2 = _ScanResult(edges=[])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert len(report.high_risk_changes) >= 1

    def test_consumer_added_detected(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        old_edge = _make_edge(
            "agent_a.py",
            "consumes_prompt",
            "ADG::PromptTemplate::SOVEREIGN_SYSTEM_CORE",
            edge_kind="prompt_consumption",
        )
        new_edge = _make_edge(
            "agent_b.py",
            "consumes_prompt",
            "ADG::PromptTemplate::SOVEREIGN_SYSTEM_CORE",
            edge_kind="prompt_consumption",
        )
        r1 = _ScanResult(edges=[old_edge])
        r2 = _ScanResult(edges=[old_edge, new_edge])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert len(report.added_consumers) == 1
        assert report.added_consumers[0].from_module == "agent_b.py"

    def test_summary_string_contains_counts(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        r1 = _ScanResult(edges=[])
        r2 = _ScanResult(edges=[])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        assert "generators" in report.summary
        assert "consumers" in report.summary

    def test_report_to_dict_json_serializable(self):
        from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

        r1 = _ScanResult(edges=[])
        r2 = _ScanResult(edges=[])
        report = detect_prompt_drift(r1, r2)  # type: ignore[arg-type]
        json.dumps(report.to_dict())


# ---------------------------------------------------------------------------
# Schema constants tests
# ---------------------------------------------------------------------------


class TestSchemaExtensions:
    """Validate P6/P7 schema additions are correct."""

    def test_prompt_entity_types_in_schema(self):
        # Get the type args from the Literal
        import typing

        from agentic_core.adg import schema

        entity_args = typing.get_args(schema.EntityType)
        assert "prompt_slot" in entity_args
        assert "prompt_template" in entity_args
        assert "prompt_assembly" in entity_args
        assert "execution_trace" in entity_args

    def test_prompt_relation_types_in_schema(self):
        import typing

        from agentic_core.adg import schema

        rel_args = typing.get_args(schema.RelationType)
        assert "generates_prompt" in rel_args
        assert "consumes_prompt" in rel_args
        assert "assembles_into" in rel_args
        assert "injects_into" in rel_args
        assert "overrides_prompt" in rel_args
        assert "executed_with_prompt" in rel_args

    def test_prompt_edge_kinds_in_schema(self):
        import typing

        from agentic_core.adg import schema

        ek_args = typing.get_args(schema.EdgeKind)
        assert "prompt_generation" in ek_args
        assert "prompt_consumption" in ek_args
        assert "prompt_assembly" in ek_args
        assert "prompt_injection" in ek_args
        assert "prompt_authority_violation" in ek_args

    def test_prompt_slot_authority_ordering(self):
        from agentic_core.adg.schema_util import PROMPT_SLOT_AUTHORITY

        # S0 must be highest authority (lowest rank number)
        assert PROMPT_SLOT_AUTHORITY["S0"] < PROMPT_SLOT_AUTHORITY["D0"]
        assert PROMPT_SLOT_AUTHORITY["D0"] < PROMPT_SLOT_AUTHORITY["I0"]
        assert PROMPT_SLOT_AUTHORITY["I0"] < PROMPT_SLOT_AUTHORITY["C0"]
        assert PROMPT_SLOT_AUTHORITY["C0"] < PROMPT_SLOT_AUTHORITY["U0"]

    def test_prompt_authority_rules_correct_direction(self):
        from agentic_core.adg.schema_util import PROMPT_AUTHORITY_RULES, PROMPT_SLOT_AUTHORITY

        for low_slot, high_slot in PROMPT_AUTHORITY_RULES:
            low_rank = PROMPT_SLOT_AUTHORITY[low_slot]
            high_rank = PROMPT_SLOT_AUTHORITY[high_slot]
            assert low_rank > high_rank, (
                f"Rule ({low_slot}, {high_slot}) is inverted: "
                f"{low_slot} has rank {low_rank}, {high_slot} has rank {high_rank}"
            )

    def test_prompt_field_to_slot_complete(self):
        from agentic_core.adg.schema_util import PROMPT_FIELD_TO_SLOT, PROMPT_SLOT_TYPES

        mapped_slots = set(PROMPT_FIELD_TO_SLOT.values())
        for slot in PROMPT_SLOT_TYPES:
            assert slot in mapped_slots, f"Slot {slot} not mapped in PROMPT_FIELD_TO_SLOT"

    def test_canonical_name_prompt_slot(self):
        from agentic_core.adg.schema_util import canonical_name

        name = canonical_name("PromptSlot", "S0", "agentic_core/test.py")
        assert name == "ADG::PromptSlot::S0::agentic_core/test.py"

    def test_canonical_name_prompt_template(self):
        from agentic_core.adg.schema_util import canonical_name

        name = canonical_name("PromptTemplate", "SOVEREIGN_SYSTEM_CORE")
        assert name == "ADG::PromptTemplate::SOVEREIGN_SYSTEM_CORE"


# ---------------------------------------------------------------------------
# E23: Execution trace → prompt linkage tests
# ---------------------------------------------------------------------------


class TestExecutionTraceVisitor:
    """Tests for _ExecutionTraceVisitor AST visitor."""

    def _run_visitor(self, code: str, source_file: str = "test_trace.py") -> list:
        from agentic_core.adg.extraction.static_scanner import _ExecutionTraceVisitor
        from agentic_core.adg.schema_util import canonical_name

        module_adg = canonical_name("Module", source_file)
        tree = ast.parse(code)
        visitor = _ExecutionTraceVisitor(module_adg, source_file)
        visitor.visit(tree)
        return visitor.edges

    def test_record_trace_emits_triggered_telemetry(self):
        code = """
record_trace(outcome="success", model="gpt-4o")
"""
        edges = self._run_visitor(code)
        assert len(edges) == 1
        assert edges[0].relation_type == "triggered_telemetry"
        assert edges[0].edge_kind == "trace_prompt_link"

    def test_emit_telemetry_emits_triggered_telemetry(self):
        code = """
# REMOVED: emit_telemetry(event="run_complete")
"""
        edges = self._run_visitor(code)
        assert len(edges) == 1
        assert edges[0].relation_type == "triggered_telemetry"

    def test_trace_id_kwarg_captured_in_symbol(self):
        code = """
record_trace(trace_id="trace-abc-123", outcome="pass")
"""
        edges = self._run_visitor(code)
        assert len(edges) == 1
        assert "trace-abc-123" in edges[0].symbol

    def test_trace_node_uses_execution_trace_prefix(self):
        code = """
record_trace(trace_id="t-001", outcome="pass")
"""
        edges = self._run_visitor(code)
        assert any(e.to_name.startswith("ADG::ExecutionTrace::") for e in edges)

    def test_plain_function_no_trace_edges(self):
        code = """
def foo():
    x = compute_result()
    return x
"""
        edges = self._run_visitor(code)
        assert len(edges) == 0

    def test_run_id_kwarg_also_captured(self):
        code = """
log_run(run_id="run-xyz", status="ok")
"""
        edges = self._run_visitor(code)
        assert len(edges) == 1
        assert "run-xyz" in edges[0].symbol

    def test_execution_trace_entity_type_in_schema(self):
        import typing

        from agentic_core.adg import schema

        entity_args = typing.get_args(schema.EntityType)
        assert "execution_trace" in entity_args

    def test_triggered_telemetry_relation_in_schema(self):
        import typing

        from agentic_core.adg import schema

        rel_args = typing.get_args(schema.RelationType)
        assert "triggered_telemetry" in rel_args

    def test_trace_prompt_link_edge_kind_in_schema(self):
        import typing

        from agentic_core.adg import schema

        ek_args = typing.get_args(schema.EdgeKind)
        assert "trace_prompt_link" in ek_args


# ---------------------------------------------------------------------------
# Integration: authority rules cover all defined authority pairs
# ---------------------------------------------------------------------------


class TestAuthorityRulesCompleteness:
    """Verify that all authority violation type strings are valid."""

    def test_all_authority_rules_have_violation_type(self):
        from agentic_core.adg.analysis.prompt_authority_types import _violation_type_for
        from agentic_core.adg.schema_util import PROMPT_AUTHORITY_RULES

        for low_slot, high_slot in PROMPT_AUTHORITY_RULES:
            vtype = _violation_type_for(low_slot, high_slot)
            assert vtype is not None, f"No violation type defined for ({low_slot}, {high_slot})"

    def test_suggested_fixes_non_empty(self):
        from agentic_core.adg.analysis.prompt_authority_types import _suggested_fix
        from agentic_core.adg.schema_util import PROMPT_AUTHORITY_RULES

        for low_slot, high_slot in PROMPT_AUTHORITY_RULES:
            fix = _suggested_fix(low_slot, high_slot)
            assert isinstance(fix, str) and len(fix) > 0
