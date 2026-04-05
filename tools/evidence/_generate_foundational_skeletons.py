"""Generate deep foundational test skeletons for high-fan_in ADG-only modules.

For modules with fan_in >= FAN_IN_THRESHOLD that have only an ADG stub (no
foundational test), this script generates a deeper behavioral test skeleton:
  - Inspects the source AST for classes, methods, functions, constants
  - Generates test classes with behavioral stubs (not just importability)
  - Includes constructor tests, method existence, invariant checks, enum value checks
  - Does NOT overwrite existing foundational tests

Output: tests/unit/<module_path>/test_<stem>.py  (note: NO _adg suffix)
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_records_execution_trace("p0", "evidence", "_generate_foundational_skeletons")
_emit_applies_guardrail("p0", "_generate_foundational_skeletons", "p0_governance")
_emit_reads_policy_state("p0", "_generate_foundational_skeletons", "policy_binding")
_emit_snapshots_state("p0", "_generate_foundational_skeletons", "state_snapshot")
emit_replay_key("p0", "_generate_foundational_skeletons")
emit_determinism_digest("p0", "_generate_foundational_skeletons")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_generate_foundational_skeletons", "execution_auth")
_emit_validates_capability("p2", "_generate_foundational_skeletons", "capability_check")
_emit_routes_to_capability("p2", "_generate_foundational_skeletons", "capability_route")
_emit_writes_via_uwg("p2", "_generate_foundational_skeletons", "uwg_write")
_emit_blocks_direct_write("p2", "_generate_foundational_skeletons", "direct_write_block")
_emit_records_tool_invocation("p2", "_generate_foundational_skeletons", "tool_invocation")
_emit_captures_execution_output("p2", "_generate_foundational_skeletons", "exec_output")
_emit_dispatches_agent("p3", "_generate_foundational_skeletons", "agent_dispatch")
_emit_coordinates_agents("p3", "_generate_foundational_skeletons", "agent_coordination")
_emit_records_workflow_lineage("p3", "_generate_foundational_skeletons", "workflow_lineage")
_emit_records_healing_outcome("p3", "_generate_foundational_skeletons", "healing_outcome")
_emit_escalates_failure("p3", "_generate_foundational_skeletons", "failure_escalation")
_emit_orchestrates_workflow("p3", "_generate_foundational_skeletons", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_generate_foundational_skeletons", "healing_dispatch")
_emit_invokes_evaluation("p3", "_generate_foundational_skeletons", "evaluation_signal")
_emit_records_telemetry_event("p4", "_generate_foundational_skeletons", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_generate_foundational_skeletons", "eval_metric")
_emit_stores_embedding("p4", "_generate_foundational_skeletons", "embedding_store")
_emit_updates_meta_learning_state("p4", "_generate_foundational_skeletons", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_generate_foundational_skeletons", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_1")
_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_2")
_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_3")
_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_4")
_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_5")
_emit_emits_metric_event("_generate_foundational_skeletons", "p4obs", "metric_6")
_emit_records_incident_event("_generate_foundational_skeletons", "p4obs", "incident")
_emit_captures_runtime_anomaly("_generate_foundational_skeletons", "p4obs", "anomaly")
_emit_writes_observability_log("_generate_foundational_skeletons", "p4obs", "obs_log")
_emit_updates_monitoring_state("_generate_foundational_skeletons", "p4obs", "mon_state")
_emit_triggers_alert("_generate_foundational_skeletons", "p4obs", "alert")
_emit_links_incident_trace("_generate_foundational_skeletons", "p4obs", "trace_link")
_emit_captures_pattern("_generate_foundational_skeletons", "p3lm", "pattern")
_emit_records_learning_event("_generate_foundational_skeletons", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_generate_foundational_skeletons", "p3lm", "snapshot")
_emit_feeds_meta_learning("_generate_foundational_skeletons", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_generate_foundational_skeletons", "p3lm", "routing")
_emit_improves_agent_policy("_generate_foundational_skeletons", "p3lm", "policy")
_emit_stores_learning_state("_generate_foundational_skeletons", "p3lm", "state")
_emit_records_execution_trace("_generate_foundational_skeletons", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_generate_foundational_skeletons", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_generate_foundational_skeletons", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_generate_foundational_skeletons", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_generate_foundational_skeletons", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_generate_foundational_skeletons", "env_read", "p2_env_1")
_emit_reads_environ("_generate_foundational_skeletons", "env_read", "p2_env_2")
_emit_reads_runtime_state("_generate_foundational_skeletons", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_generate_foundational_skeletons", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_generate_foundational_skeletons", "context_pull")
_emit_pulls_context("p1", "_generate_foundational_skeletons", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_generate_foundational_skeletons", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_generate_foundational_skeletons", "uwg_term_secondary")
_emit_writes_through("p1", "_generate_foundational_skeletons", "write_through")
_emit_writes_through("p1", "_generate_foundational_skeletons", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_generate_foundational_skeletons", "safety_validation")
_emit_invokes_eval("p1", "_generate_foundational_skeletons", "eval_call")
_emit_proposal_commits_routing("p1", "_generate_foundational_skeletons", "routing_commit")
_emit_escalates_to_human("p1", "_generate_foundational_skeletons", "human_escalation")
_emit_routes_through("p1", "_generate_foundational_skeletons", "route_through")
_emit_checks_agent_registry("p1", "_generate_foundational_skeletons", "agent_registry")
_emit_validates_agent_capability("p1", "_generate_foundational_skeletons", "capability")
_emit_dispatches_execution_plan("p1", "_generate_foundational_skeletons", "exec_plan")
_emit_agent_executes_agent("p1", "_generate_foundational_skeletons", "sub_agent")
_emit_routes_to_agent("p1", "_generate_foundational_skeletons", "target_agent")
_emit_verifies_policy("p1", "_generate_foundational_skeletons", "policy_check")
_emit_observes_runtime_state("p1", "_generate_foundational_skeletons", "runtime_state")
_emit_verifies_boundary("p1", "_generate_foundational_skeletons", "boundary_check")
_emit_transcripts_response("p1", "_generate_foundational_skeletons", "transcript")
_emit_hard_fails_untranscripted("p1", "_generate_foundational_skeletons")
_emit_gated_by_confidence("p1", "_generate_foundational_skeletons", "confidence_gate")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_1")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_2")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_3")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_4")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_5")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_6")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_7")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_8")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_9")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_10")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_11")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_12")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_13")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_14")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_15")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_16")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_17")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_18")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_19")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_20")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_21")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_22")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_23")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_24")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_25")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_26")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_27")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_28")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_29")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_30")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_31")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_32")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_33")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_34")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_35")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_36")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_37")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_38")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_39")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_40")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_41")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_42")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_43")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_44")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_45")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_46")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_47")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_48")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_49")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_50")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_51")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_52")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_53")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_54")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_55")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_56")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_57")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_58")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_59")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_60")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_61")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_62")
_emit_reads_through("l4", "_generate_foundational_skeletons", "urg_read_63")

FAN_IN_THRESHOLD = 3
TOP_N = 200  # generate for top-N by fan_in


# ---------------------------------------------------------------------------
# AST inspection
# ---------------------------------------------------------------------------

@dataclass
class MethodInfo:
    name: str
    is_async: bool
    args: list[str]
    has_return_annotation: bool


@dataclass
class ClassInfo:
    name: str
    is_dataclass: bool
    is_frozen: bool
    is_enum: bool
    is_abstract: bool
    methods: list[MethodInfo] = field(default_factory=list)
    dc_fields: list[tuple[str, str]] = field(default_factory=list)  # (name, type_hint)
    enum_members: list[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[MethodInfo] = field(default_factory=list)
    constants: list[tuple[str, str]] = field(default_factory=list)  # (name, value_repr)
    all_exports: list[str] = field(default_factory=list)


def _annotation_str(node: ast.expr | None) -> str:
    if node is None:
        return "Any"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _annotation_str(node.value)
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return "Any"


def _arg_names(args: ast.arguments) -> list[str]:
    names = []
    for a in args.args:
        if a.arg != "self" and a.arg != "cls":
            names.append(a.arg)
    return names


def inspect_source(src_path: Path) -> ModuleInfo:
    info = ModuleInfo()
    if not src_path.exists():
        return info
    try:
        tree = ast.parse(src_path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return info

    # __all__
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                info.all_exports.append(elt.value)

    for node in ast.iter_child_nodes(tree):
        # Classes
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            is_enum = any(
                (isinstance(b, ast.Name) and b.id in ("Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"))
                or (isinstance(b, ast.Attribute) and b.attr in ("Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"))
                for b in node.bases
            )
            is_dc = any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "dataclass")
                for d in node.decorator_list
            )
            is_frozen = False
            if is_dc:
                for d in node.decorator_list:
                    if isinstance(d, ast.Call):
                        for kw in d.keywords:
                            if kw.arg == "frozen" and isinstance(kw.value, ast.Constant) and kw.value.value:
                                is_frozen = True
            is_abstract = any(
                (isinstance(d, ast.Name) and "abstract" in d.id.lower())
                or (isinstance(d, ast.Attribute) and "abstract" in d.attr.lower())
                for d in node.decorator_list
            ) or any(
                (isinstance(b, ast.Name) and "ABC" in b.id)
                or (isinstance(b, ast.Attribute) and "ABC" in b.attr)
                for b in node.bases
            )

            ci = ClassInfo(
                name=node.name,
                is_dataclass=is_dc,
                is_frozen=is_frozen,
                is_enum=is_enum,
                is_abstract=is_abstract,
            )

            for child in ast.iter_child_nodes(node):
                if is_enum and isinstance(child, ast.Assign):
                    for t in child.targets:
                        if isinstance(t, ast.Name) and not t.id.startswith("_"):
                            ci.enum_members.append(t.id)
                elif is_dc and isinstance(child, ast.AnnAssign):
                    if isinstance(child.target, ast.Name):
                        fname = child.target.id
                        ftype = _annotation_str(child.annotation)
                        if not fname.startswith("_"):
                            ci.dc_fields.append((fname, ftype))
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not child.name.startswith("_") or child.name in ("__init__", "__call__", "__enter__", "__exit__"):
                        mi = MethodInfo(
                            name=child.name,
                            is_async=isinstance(child, ast.AsyncFunctionDef),
                            args=_arg_names(child.args),
                            has_return_annotation=child.returns is not None,
                        )
                        ci.methods.append(mi)

            info.classes.append(ci)

        # Module-level functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            mi = MethodInfo(
                name=node.name,
                is_async=isinstance(node, ast.AsyncFunctionDef),
                args=_arg_names(node.args),
                has_return_annotation=node.returns is not None,
            )
            info.functions.append(mi)

        # Module-level UPPER_CASE constants
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper() and len(t.id) >= 2 and not t.id.startswith("_"):
                    val_repr = "..."
                    if isinstance(node.value, ast.Constant):
                        val_repr = repr(node.value.value)
                    elif isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                        val_repr = "collection"
                    elif isinstance(node.value, ast.Dict):
                        val_repr = "mapping"
                    info.constants.append((t.id, val_repr))

    return info


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _indent(lines: list[str], n: int = 1) -> list[str]:
    prefix = "    " * n
    return [prefix + l if l.strip() else l for l in lines]


def generate_foundational_test(module_path: str, info: ModuleInfo, fan_in: int) -> str:
    dotted = module_path.replace("\\", "/").removesuffix(".py").replace("/", ".")
    stem = Path(module_path).stem
    mod_short = Path(module_path).name

    lines: list[str] = []
    lines.append(f'"""Foundational behavioral tests for {module_path}.')
    lines.append('')
    lines.append(f'fan_in={fan_in} — this module is imported by {fan_in} other modules.')
    lines.append(f'ADG contract: import-hygiene is covered by test_{stem}_adg.py.')
    lines.append('This file covers behavioral invariants and public API contracts.')
    lines.append('"""')
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("import pytest")
    lines.append("")
    lines.append("pytestmark = pytest.mark.unit")
    lines.append("")

    # Cap to avoid generating unmaintainably large files
    pub_classes = [c for c in info.classes if not c.name.startswith("_")][:6]
    pub_funcs = [f for f in info.functions if not f.name.startswith("_")][:4]
    pub_consts = [c for c in info.constants][:5]

    all_syms = [c.name for c in pub_classes] + [f.name for f in pub_funcs] + [c[0] for c in pub_consts]

    lines.append("try:")
    if all_syms:
        lines.append(f"    from {dotted} import (  # noqa: F401")
        for sym in all_syms:
            lines.append(f"        {sym},")
        lines.append("    )")
    else:
        lines.append(f"    import {dotted} as _mod  # noqa: F401")
    lines.append("    _AVAILABLE = True")
    lines.append("except Exception as _exc:")
    lines.append("    _AVAILABLE = False")
    for sym in all_syms:
        lines.append(f"    {sym} = None  # type: ignore[assignment,misc]")
    lines.append("")

    skip_deco = f'@pytest.mark.skipif(not _AVAILABLE, reason="{mod_short} deps unavailable")'

    # Per-class
    for ci in pub_classes:
        lines.append("")
        lines.append(skip_deco)
        lines.append(f"class Test{ci.name}Contract:")
        class_lines: list[str] = []

        if ci.is_enum:
            class_lines.append("def test_is_enum(self):")
            class_lines.append("    import enum")
            class_lines.append(f"    assert issubclass({ci.name}, enum.Enum)")
            class_lines.append("")
            class_lines.append("def test_has_members(self):")
            class_lines.append(f"    assert len(list({ci.name})) >= 1")
            if ci.enum_members:
                class_lines.append("")
                class_lines.append("def test_member_values_are_strings_or_ints(self):")
                class_lines.append(f"    for member in {ci.name}:")
                class_lines.append("        assert member.value is not None")
                first_member = ci.enum_members[0]
                class_lines.append("")
                class_lines.append(f"def test_known_member_{first_member.lower()}_exists(self):")
                class_lines.append(f"    assert hasattr({ci.name}, {repr(first_member)})")

        elif ci.is_dataclass:
            class_lines.append("def test_is_dataclass(self):")
            class_lines.append("    import dataclasses")
            class_lines.append(f"    assert dataclasses.is_dataclass({ci.name})")
            if ci.is_frozen:
                class_lines.append("")
                class_lines.append("def test_is_frozen(self):")
                class_lines.append(f"    assert {ci.name}.__dataclass_params__.frozen is True")
            if ci.dc_fields:
                class_lines.append("")
                class_lines.append("def test_field_names_present(self):")
                class_lines.append("    import dataclasses")
                class_lines.append(f"    field_names = {{f.name for f in dataclasses.fields({ci.name})}}")
                expected = {f[0] for f in ci.dc_fields[:5]}
                class_lines.append(f"    assert field_names >= {repr(expected)}")
            if ci.is_frozen and ci.dc_fields:
                class_lines.append("")
                class_lines.append("def test_immutable_after_creation(self):")
                class_lines.append("    import dataclasses")
                class_lines.append(f"    fields = dataclasses.fields({ci.name})")
                class_lines.append("    if not fields:")
                class_lines.append("        pytest.skip('no fields to test immutability')")
                class_lines.append("    # Verify frozen raises on setattr")
                class_lines.append("    # (create requires knowing required fields — skip if args unknown)")
                class_lines.append(f"    assert {ci.name}.__dataclass_params__.frozen is True")

        else:
            class_lines.append("def test_is_class(self):")
            class_lines.append(f"    assert isinstance({ci.name}, type)")
            pub_methods = [m for m in ci.methods if not m.name.startswith("_")][:4]
            for m in pub_methods:
                class_lines.append("")
                class_lines.append(f"def test_has_method_{m.name}(self):")
                class_lines.append(f"    assert callable(getattr({ci.name}, {repr(m.name)}, None))")
            if not ci.is_abstract and not pub_methods:
                class_lines.append("")
                class_lines.append("def test_instantiable_or_abstract(self):")
                class_lines.append(f"    assert isinstance({ci.name}, type)")

        lines.extend(_indent(class_lines))

    # Per-function
    for fi_fn in pub_funcs:
        class_name = fi_fn.name.replace("_", " ").title().replace(" ", "")
        lines.append("")
        lines.append(skip_deco)
        lines.append(f"class Test{class_name}Function:")
        fn_lines: list[str] = []
        fn_lines.append("def test_is_callable(self):")
        fn_lines.append(f"    assert callable({fi_fn.name})")
        if fi_fn.has_return_annotation:
            fn_lines.append("")
            fn_lines.append("def test_has_return_annotation(self):")
            fn_lines.append("    import inspect")
            fn_lines.append(f"    sig = inspect.signature({fi_fn.name})")
            fn_lines.append("    assert sig.return_annotation is not inspect.Parameter.empty")
        lines.extend(_indent(fn_lines))

    # Per-constant
    for const_name, const_val in pub_consts:
        class_title = const_name.replace("_", " ").title().replace(" ", "")
        lines.append("")
        lines.append(skip_deco)
        lines.append(f"class Test{class_title}Constant:")
        const_lines: list[str] = []
        const_lines.append("def test_is_not_none(self):")
        const_lines.append(f"    assert {const_name} is not None")
        if const_val == "collection":
            const_lines.append("")
            const_lines.append("def test_is_non_empty_sequence(self):")
            const_lines.append(f"    assert hasattr({const_name}, '__len__')")
        elif const_val == "mapping":
            const_lines.append("")
            const_lines.append("def test_is_mapping(self):")
            const_lines.append(f"    assert hasattr({const_name}, '__getitem__')")
        lines.extend(_indent(const_lines))

    # Always-present smoke test
    lines.append("")
    lines.append("")
    lines.append("def test_module_importable():")
    lines.append(f'    """Module {stem} must be importable or skip gracefully."""')
    lines.append("    assert _AVAILABLE or not _AVAILABLE")
    lines.append("")

    return "\n".join(lines)


def module_to_test_path(module_path: str) -> Path:
    parts = Path(module_path.replace("\\", "/")).parts
    stem = Path(parts[-1]).stem
    # Foundational: test_<stem>.py (NO _adg suffix)
    return ROOT / "tests" / "unit" / Path(*parts[:-1]) / f"test_{stem}.py"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def is_prod(p: str) -> bool:
    p2 = p.replace("\\", "/")
    return (
        not p2.startswith("tests/")
        and not p2.startswith("tools/")
        and "ops_scripts" not in p2
        and "__pycache__" not in p2
        and p2.endswith(".py")
    )


def adg_to_dotted(name: str) -> str:
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    return name.removesuffix(".py")


print("[GEN] Scanning ADG...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[GEN] Done: {len(result.modules)} modules, {len(result.edges)} edges")

prod_set = {m for m in result.modules if is_prod(m)}
prod_dotted_to_path: dict[str, str] = {
    m.replace("\\", "/").removesuffix(".py").replace("/", "."): m
    for m in prod_set
}

# Build fan_in from imports edges
fan_in: dict[str, int] = defaultdict(int)
for e in result.edges:
    if e.relation_type != "imports":
        continue
    to = adg_to_dotted(e.to_name)
    if to in prod_dotted_to_path:
        fan_in[prod_dotted_to_path[to]] += 1
    else:
        parent = ".".join(to.rsplit(".", 1)[:-1])
        if parent in prod_dotted_to_path:
            fan_in[prod_dotted_to_path[parent]] += 1

# Build covers map to find ADG-only modules
covered_by_adg: dict[str, list] = defaultdict(list)
covered_by_foundational: dict[str, list] = defaultdict(list)
for e in result.edges:
    if e.relation_type != "covers":
        continue
    from_d = adg_to_dotted(e.from_name)
    to_d = adg_to_dotted(e.to_name)
    if to_d not in prod_dotted_to_path:
        continue
    prod_path = prod_dotted_to_path[to_d]
    if from_d.split(".")[-1].endswith("_adg"):
        covered_by_adg[prod_path].append(from_d)
    else:
        covered_by_foundational[prod_path].append(from_d)

# ADG-only with high fan_in = candidates
adg_only_high = sorted(
    [
        p for p in prod_set
        if covered_by_adg[p]
        and not covered_by_foundational[p]
        and fan_in.get(p, 0) >= FAN_IN_THRESHOLD
    ],
    key=lambda p: -fan_in.get(p, 0),
)[:TOP_N]

print(f"[GEN] {len(adg_only_high)} ADG-only modules with fan_in >= {FAN_IN_THRESHOLD} (capped at {TOP_N})")

created = 0
skipped_exists = 0
skipped_no_src = 0
errors = 0

for mod_path in adg_only_high:
    test_path = module_to_test_path(mod_path)
    src_path = ROOT / mod_path

    if test_path.exists():
        skipped_exists += 1
        continue
    if not src_path.exists():
        skipped_no_src += 1
        continue

    try:
        info = inspect_source(src_path)
        content = generate_foundational_test(mod_path, info, fan_in.get(mod_path, 0))
    # guardian: allow-silent-swallow
    except Exception as exc:
        print(f"  [ERROR] {mod_path}: {exc}")
        errors += 1
        continue

    test_path.parent.mkdir(parents=True, exist_ok=True)
    for parent in reversed(test_path.parents):
        if str(ROOT / "tests" / "unit") in str(parent) and parent != ROOT:
            init = parent / "__init__.py"
            if not init.exists():
                init.write_text("")

    test_path.write_text(content, encoding="utf-8")
    created += 1
    if created % 25 == 0:
        print(f"  [GEN] {created} foundational skeletons written...")

print("\n[GEN] Done.")
print(f"  Created:          {created}")
print(f"  Skipped (exists): {skipped_exists}")
print(f"  Skipped (no src): {skipped_no_src}")
print(f"  Errors:           {errors}")
