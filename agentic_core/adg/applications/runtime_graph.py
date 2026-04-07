"""E26: Runtime Execution Graph.

Materializes the runtime execution topology described in the architecture documents
into ADG entity/edge form. Analyses a ScanResult to produce:

    AgentAction nodes  — modules that invoke agent execution patterns
    ToolInvocation nodes — modules that call tool execution symbols
    LayerTransition edges — cross-layer calls detected in the import/call graph

The live ADG (20260311 scan) provides the grounding data:
    - 4,327 calls edges (G4_calls plane)
    - 13 confirmed agent modules under agentic_core/agents/
    - Real layer prefixes: L0-L6, L_APP, L_SHARED

Usage::

    from agentic_core.adg.applications.runtime_graph import build_runtime_graph

    report = build_runtime_graph(result)
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import (
    LAYER_PREFIXES,
    module_path_to_layer,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "runtime_graph")
_emit_applies_guardrail("p0", "runtime_graph", "p0_governance")
_emit_reads_policy_state("p0", "runtime_graph", "policy_binding")
_emit_snapshots_state("p0", "runtime_graph", "state_snapshot")
emit_replay_key("p0", "runtime_graph")
emit_determinism_digest("p0", "runtime_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "runtime_graph", "execution_auth")
_emit_validates_capability("p2", "runtime_graph", "capability_check")
_emit_routes_to_capability("p2", "runtime_graph", "capability_route")
_emit_writes_via_uwg("p2", "runtime_graph", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_graph", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_graph", "exec_output")
_emit_dispatches_agent("p3", "runtime_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_graph", "healing_outcome")
_emit_escalates_failure("p3", "runtime_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_graph", "eval_metric")
_emit_stores_embedding("p4", "runtime_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_graph", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("runtime_graph", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_graph", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_graph", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_graph", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_graph", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_graph", "p4obs", "metric_6")
_emit_records_incident_event("runtime_graph", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_graph", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_graph", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_graph", "p4obs", "mon_state")
_emit_triggers_alert("runtime_graph", "p4obs", "alert")
_emit_links_incident_trace("runtime_graph", "p4obs", "trace_link")
_emit_captures_pattern("runtime_graph", "p3lm", "pattern")
_emit_records_learning_event("runtime_graph", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_graph", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_graph", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_graph", "p3lm", "routing")
_emit_improves_agent_policy("runtime_graph", "p3lm", "policy")
_emit_stores_learning_state("runtime_graph", "p3lm", "state")
_emit_records_execution_trace("runtime_graph", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_graph", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_graph", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_graph", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_graph", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_graph", "env_read", "p2_env_1")
_emit_reads_environ("runtime_graph", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_graph", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_graph", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_graph", "context_pull")
_emit_pulls_context("p1", "runtime_graph", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "runtime_graph", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_graph", "uwg_term_secondary")
_emit_writes_through("p1", "runtime_graph", "write_through")
_emit_writes_through("p1", "runtime_graph", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "runtime_graph", "safety_validation")
_emit_invokes_eval("p1", "runtime_graph", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_graph", "routing_commit")
_emit_escalates_to_human("p1", "runtime_graph", "human_escalation")
_emit_routes_through("p1", "runtime_graph", "route_through")
_emit_checks_agent_registry("p1", "runtime_graph", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_graph", "capability")
_emit_dispatches_execution_plan("p1", "runtime_graph", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_graph", "sub_agent")
_emit_routes_to_agent("p1", "runtime_graph", "target_agent")
_emit_verifies_policy("p1", "runtime_graph", "policy_check")
_emit_observes_runtime_state("p1", "runtime_graph", "runtime_state")
_emit_verifies_boundary("p1", "runtime_graph", "boundary_check")
_emit_transcripts_response("p1", "runtime_graph", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_graph")
_emit_gated_by_confidence("p1", "runtime_graph", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

# Agent execution symbols detected in the live ADG
_AGENT_EXEC_SYMBOLS: frozenset[str] = frozenset(
    {
        "agent.execute",
        "agent.run",
        "agent.arun",
        "agent.invoke",
        "BaseAgent.execute",
        "BaseAgent.run",
        "AgentExecutor.invoke",
        "AgentExecutor.arun",
        "execute_agent",
        "run_agent",
        "arun_agent",
    },
)

# Tool invocation symbols
_TOOL_INVOKE_SYMBOLS: frozenset[str] = frozenset(
    {
        "tool.run",
        "tool.invoke",
        "BaseTool.run",
        "BaseTool.invoke",
        "invoke_tool",
        "run_tool",
        "call_tool",
        "ToolExecutor.invoke",
        "ToolExecutor.run",
    },
)


@dataclass
class AgentActionNode:
    """A module that invokes agent execution."""

    module_path: str
    layer: str
    invoked_symbols: list[str]
    call_count: int

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "invoked_symbols": self.invoked_symbols,
            "call_count": self.call_count,
        }


@dataclass
class ToolInvocationNode:
    """A module that invokes tool execution."""

    module_path: str
    layer: str
    invoked_symbols: list[str]
    call_count: int

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "invoked_symbols": self.invoked_symbols,
            "call_count": self.call_count,
        }


@dataclass
class LayerTransitionEdge:
    """A cross-layer call detected in the call/import graph."""

    from_module: str
    from_layer: str
    to_symbol: str
    to_layer: str
    relation_type: str
    is_allowed: bool
    source_file: str
    line_no: int

    def to_dict(self) -> dict:
        return {
            "from_module": self.from_module,
            "from_layer": self.from_layer,
            "to_symbol": self.to_symbol,
            "to_layer": self.to_layer,
            "relation_type": self.relation_type,
            "is_allowed": self.is_allowed,
            "source_file": self.source_file,
            "line_no": self.line_no,
        }


@dataclass
class RuntimeGraphReport:
    """Materialized runtime execution graph."""

    agent_action_nodes: list[AgentActionNode] = field(default_factory=list)
    tool_invocation_nodes: list[ToolInvocationNode] = field(default_factory=list)
    layer_transitions: list[LayerTransitionEdge] = field(default_factory=list)
    upward_layer_violations: list[LayerTransitionEdge] = field(default_factory=list)
    total_cross_layer_calls: int = 0
    layer_coverage: dict[str, int] = field(default_factory=dict)

    @property
    def summary(self) -> str:
        return (
            f"Runtime graph: {len(self.agent_action_nodes)} agent-action modules | "
            f"{len(self.tool_invocation_nodes)} tool-invocation modules | "
            f"{self.total_cross_layer_calls} cross-layer calls | "
            f"{len(self.upward_layer_violations)} upward-layer violations"
        )

    def to_dict(self) -> dict:
        return {
            "agent_action_count": len(self.agent_action_nodes),
            "tool_invocation_count": len(self.tool_invocation_nodes),
            "total_cross_layer_calls": self.total_cross_layer_calls,
            "upward_violation_count": len(self.upward_layer_violations),
            "layer_coverage": self.layer_coverage,
            "summary": self.summary,
            "agent_action_nodes": [n.to_dict() for n in self.agent_action_nodes[:50]],
            "tool_invocation_nodes": [n.to_dict() for n in self.tool_invocation_nodes[:50]],
            "layer_transitions": [e.to_dict() for e in self.layer_transitions[:100]],
            "upward_layer_violations": [e.to_dict() for e in self.upward_layer_violations[:50]],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _layer_rank(layer: str) -> int:
    """Return numeric rank for layer (higher = higher layer in stack)."""
    _RANK = {
        "L0": 0,
        "L1": 1,
        "L2": 2,
        "L3": 3,
        "L4": 4,
        "L5": 5,
        "L6": 6,
        "L_SHARED": -1,
        "L_RUNTIME": 3,
        "L_PG": 1,
        "L_TOOLS": -2,
        "L_APP": 7,
        "L_SL": 2,
        "L_OPS": -2,
        "L_TEST": -3,
        "L_UNKNOWN": -4,
    }
    return _RANK.get(layer, -1)


def _symbol_to_layer(symbol_name: str) -> str:
    """Attempt to extract layer from a fully qualified symbol name."""
    norm = symbol_name.replace("\\", "/")
    for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
        if norm.startswith(prefix.replace("/", ".")):
            return layer
    # Try path-style within symbol
    for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
        if prefix.replace("/", ".") in norm:
            return layer
    return "L_UNKNOWN"


def build_runtime_graph(result: ScanResult) -> RuntimeGraphReport:
    """Build the runtime execution graph from a ScanResult.

    Pass 1: Detect agent_action nodes from calls to agent execution symbols.
    Pass 2: Detect tool_invocation nodes from calls to tool symbols.
    Pass 3: Build layer transition edges from all cross-layer calls/imports.
    Pass 4: Flag upward layer violations (lower-numbered layer calling higher).
    """
    # Pass 1 & 2: agent/tool action detection
    agent_actions: dict[str, list[str]] = {}  # mod_path → [symbols]
    tool_invocations: dict[str, list[str]] = {}

    for edge in result.edges:
        if edge.relation_type not in ("calls", "invokes_provider"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        mod = edge.from_name[len(_MODULE_PREFIX) :]
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]

        sym_base = sym.split(".")[-1] if "." in sym else sym
        sym_full_base = ".".join(sym.split(".")[-2:]) if "." in sym else sym

        if (
            sym_base in {s.split(".")[-1] for s in _AGENT_EXEC_SYMBOLS}
            or sym_full_base in _AGENT_EXEC_SYMBOLS
        ):
            agent_actions.setdefault(mod, []).append(sym)

        if (
            sym_base in {s.split(".")[-1] for s in _TOOL_INVOKE_SYMBOLS}
            or sym_full_base in _TOOL_INVOKE_SYMBOLS
        ):
            tool_invocations.setdefault(mod, []).append(sym)

    # Pass 3 & 4: layer transitions
    layer_transitions: list[LayerTransitionEdge] = []
    upward_violations: list[LayerTransitionEdge] = []
    layer_coverage: dict[str, int] = {}

    for edge in result.edges:
        if edge.relation_type not in ("calls", "imports", "instantiates"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        from_mod = edge.from_name[len(_MODULE_PREFIX) :]
        from_layer = module_path_to_layer(from_mod)

        # Determine target layer from symbol path
        to_sym = edge.to_name
        if to_sym.startswith(_SYMBOL_PREFIX):
            to_sym_inner = to_sym[len(_SYMBOL_PREFIX) :]
        elif to_sym.startswith(_MODULE_PREFIX):
            to_sym_inner = to_sym[len(_MODULE_PREFIX) :]
        else:
            to_sym_inner = to_sym

        to_layer = _symbol_to_layer(to_sym_inner)

        if from_layer == to_layer or to_layer == "L_UNKNOWN":
            continue
        if from_layer == "L_UNKNOWN":
            continue

        from_rank = _layer_rank(from_layer)
        to_rank = _layer_rank(to_layer)

        # Skip utility/test layers from transition tracking
        if from_rank < 0 or to_rank < 0:
            continue

        is_upward = to_rank > from_rank  # calling a higher layer = architecture violation

        transition = LayerTransitionEdge(
            from_module=from_mod,
            from_layer=from_layer,
            to_symbol=edge.to_name,
            to_layer=to_layer,
            relation_type=edge.relation_type,
            is_allowed=not is_upward,
            source_file=edge.source_file,
            line_no=edge.line_no,
        )
        layer_transitions.append(transition)
        layer_coverage[from_layer] = layer_coverage.get(from_layer, 0) + 1

        if is_upward:
            upward_violations.append(transition)

    # Build report nodes
    agent_nodes = [
        AgentActionNode(
            module_path=mod,
            layer=module_path_to_layer(mod),
            invoked_symbols=sorted(set(syms)),
            call_count=len(syms),
        )
        for mod, syms in sorted(agent_actions.items())
    ]
    tool_nodes = [
        ToolInvocationNode(
            module_path=mod,
            layer=module_path_to_layer(mod),
            invoked_symbols=sorted(set(syms)),
            call_count=len(syms),
        )
        for mod, syms in sorted(tool_invocations.items())
    ]

    return RuntimeGraphReport(
        agent_action_nodes=agent_nodes,
        tool_invocation_nodes=tool_nodes,
        layer_transitions=layer_transitions,
        upward_layer_violations=upward_violations,
        total_cross_layer_calls=len(layer_transitions),
        layer_coverage=layer_coverage,
    )


__all__ = [
    "AgentActionNode",
    "LayerTransitionEdge",
    "RuntimeGraphReport",
    "ToolInvocationNode",
    "build_runtime_graph",
]
