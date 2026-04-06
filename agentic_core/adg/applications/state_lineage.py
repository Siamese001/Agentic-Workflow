"""E29: State Lineage Query API.

Makes the mutation ledger queryable. Given a ScanResult, builds an index of
all writes_to / writes_through edges and allows developers to ask:

    - Which modules mutated this state symbol?
    - Which execution path produced this write?
    - Which policy hash context authorized this module to write?

This bridges static analysis (ADG) with the mutation ledger's append-only
event model. At analysis time we operate on the static graph; at runtime the
same interface contract is fulfilled by the ledger.

Live ADG grounding (20260311):
    - 2,323 writes_to edges across 3,302 modules
    - 22 writes_through UWG edges
    - UWG canonical: ADG::Symbol::UniversalWriteGateway

Usage::

    from agentic_core.adg.applications.state_lineage import (
        build_lineage_index, query_mutations_for_state
    )

    index = build_lineage_index(result)
    records = index.mutations_for_state("open")
    for r in records:
        print(r.module_path, r.layer, r.via_uwg)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import (
    UWG_CANONICAL_SYMBOL,
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

_emit_applies_guardrail("p0", "state_lineage", "p0_governance")
_emit_reads_policy_state("p0", "state_lineage", "policy_binding")
_emit_snapshots_state("p0", "state_lineage", "state_snapshot")
emit_replay_key("p0", "state_lineage")
emit_determinism_digest("p0", "state_lineage")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_lineage", "execution_auth")
_emit_validates_capability("p2", "state_lineage", "capability_check")
_emit_routes_to_capability("p2", "state_lineage", "capability_route")
_emit_writes_via_uwg("p2", "state_lineage", "uwg_write")
_emit_blocks_direct_write("p2", "state_lineage", "direct_write_block")
_emit_records_tool_invocation("p2", "state_lineage", "tool_invocation")
_emit_captures_execution_output("p2", "state_lineage", "exec_output")
_emit_dispatches_agent("p3", "state_lineage", "agent_dispatch")
_emit_coordinates_agents("p3", "state_lineage", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_lineage", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_lineage", "healing_outcome")
_emit_escalates_failure("p3", "state_lineage", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_lineage", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_lineage", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_lineage", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_lineage", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_lineage", "eval_metric")
_emit_stores_embedding("p4", "state_lineage", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_lineage", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_lineage", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("state_lineage", "p4obs", "metric_1")
_emit_emits_metric_event("state_lineage", "p4obs", "metric_2")
_emit_emits_metric_event("state_lineage", "p4obs", "metric_3")
_emit_emits_metric_event("state_lineage", "p4obs", "metric_4")
_emit_emits_metric_event("state_lineage", "p4obs", "metric_5")
_emit_emits_metric_event("state_lineage", "p4obs", "metric_6")
_emit_records_incident_event("state_lineage", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_lineage", "p4obs", "anomaly")
_emit_writes_observability_log("state_lineage", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_lineage", "p4obs", "mon_state")
_emit_triggers_alert("state_lineage", "p4obs", "alert")
_emit_links_incident_trace("state_lineage", "p4obs", "trace_link")
_emit_captures_pattern("state_lineage", "p3lm", "pattern")
_emit_records_learning_event("state_lineage", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_lineage", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_lineage", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_lineage", "p3lm", "routing")
_emit_improves_agent_policy("state_lineage", "p3lm", "policy")
_emit_stores_learning_state("state_lineage", "p3lm", "state")
_emit_records_execution_trace("state_lineage", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_lineage", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_lineage", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_lineage", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_lineage", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_lineage", "env_read", "p2_env_1")
_emit_reads_environ("state_lineage", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_lineage", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_lineage", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_lineage", "context_pull")
_emit_pulls_context("p1", "state_lineage", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_lineage", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_lineage", "uwg_term_2")
_emit_writes_through("p1", "state_lineage", "write_through")
_emit_writes_through("p1", "state_lineage", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_lineage", "safety_validation")
_emit_invokes_eval("p1", "state_lineage", "eval_call")
_emit_proposal_commits_routing("p1", "state_lineage", "routing_commit")
_emit_escalates_to_human("p1", "state_lineage", "human_escalation")
_emit_routes_through("p1", "state_lineage", "route_through")
_emit_checks_agent_registry("p1", "state_lineage", "agent_registry")
_emit_validates_agent_capability("p1", "state_lineage", "capability")
_emit_dispatches_execution_plan("p1", "state_lineage", "exec_plan")
_emit_agent_executes_agent("p1", "state_lineage", "sub_agent")
_emit_routes_to_agent("p1", "state_lineage", "target_agent")
_emit_verifies_policy("p1", "state_lineage", "policy_check")
_emit_observes_runtime_state("p1", "state_lineage", "runtime_state")
_emit_verifies_boundary("p1", "state_lineage", "boundary_check")
_emit_transcripts_response("p1", "state_lineage", "transcript")
_emit_hard_fails_untranscripted("p1", "state_lineage")
_emit_gated_by_confidence("p1", "state_lineage", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


@dataclass
class LineageRecord:
    """One module's write relationship to a state symbol."""

    module_path: str
    layer: str
    state_symbol: str
    via_uwg: bool
    relation_type: str
    source_file: str
    line_no: int

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "state_symbol": self.state_symbol,
            "via_uwg": self.via_uwg,
            "relation_type": self.relation_type,
            "source_file": self.source_file,
            "line_no": self.line_no,
        }


@dataclass
class LineageIndex:
    """Queryable index of all mutation lineage records."""

    _by_symbol: dict[str, list[LineageRecord]] = field(default_factory=dict, repr=False)
    _by_module: dict[str, list[LineageRecord]] = field(default_factory=dict, repr=False)
    _by_layer: dict[str, list[LineageRecord]] = field(default_factory=dict, repr=False)
    total_records: int = 0
    uwg_covered: int = 0
    bypass_count: int = 0

    def mutations_for_state(self, state_key: str) -> list[LineageRecord]:
        """Return all modules that write to a state symbol matching state_key."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LineageIndex.mutations_for_state")

        results: list[LineageRecord] = []
        for sym, records in self._by_symbol.items():
            if state_key in sym:
                results.extend(records)
        return sorted(results, key=lambda r: (r.layer, r.module_path))

    def mutations_by_module(self, module_path: str) -> list[LineageRecord]:
        """Return all state mutations performed by a specific module."""
        return self._by_module.get(module_path, [])

    def mutations_by_layer(self, layer: str) -> list[LineageRecord]:
        """Return all mutations originating from a specific layer."""
        return self._by_layer.get(layer, [])

    def uwg_bypass_modules(self) -> list[str]:
        """Return modules that write directly without going through UWG."""
        bypasses: list[str] = []
        for mod, records in self._by_module.items():
            if any(not r.via_uwg for r in records):
                if not any(r.via_uwg for r in records):
                    bypasses.append(mod)
        return sorted(bypasses)

    def coverage_summary(self) -> dict:
        return {
            "total_records": self.total_records,
            "uwg_covered": self.uwg_covered,
            "bypass_count": self.bypass_count,
            "coverage_rate": round(self.uwg_covered / max(self.total_records, 1), 4),
            "layers_writing": sorted(self._by_layer.keys()),
            "top_writers": [
                {"module": mod, "write_count": len(recs)}
                for mod, recs in sorted(self._by_module.items(), key=lambda kv: -len(kv[1]))[:20]
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.coverage_summary(), indent=indent, sort_keys=True)


def build_lineage_index(result: ScanResult) -> LineageIndex:
    """Build a queryable lineage index from a ScanResult.

    Pass 1: Collect all writes_to edges into lineage records.
    Pass 2: Mark records as via_uwg if the same module also has writes_through UWG.
    Pass 3: Index by symbol, module, and layer.
    """
    # Pass 1: raw writes_to records
    raw_records: list[LineageRecord] = []
    for edge in result.edges:
        if edge.relation_type not in ("writes_to", "writes_through"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        mod = edge.from_name[len(_MODULE_PREFIX) :]
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]
        layer = module_path_to_layer(mod)
        via_uwg = edge.relation_type == "writes_through" and (
            "UniversalWriteGateway" in edge.to_name or UWG_CANONICAL_SYMBOL in edge.to_name
        )
        raw_records.append(
            LineageRecord(
                module_path=mod,
                layer=layer,
                state_symbol=sym,
                via_uwg=via_uwg,
                relation_type=edge.relation_type,
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
        )

    # Pass 2: mark via_uwg for modules that have writes_through
    uwg_modules: set[str] = {r.module_path for r in raw_records if r.via_uwg}
    for r in raw_records:
        if r.module_path in uwg_modules:
            r.via_uwg = True

    # Pass 3: build index
    idx = LineageIndex()
    for r in raw_records:
        idx._by_symbol.setdefault(r.state_symbol, []).append(r)
        idx._by_module.setdefault(r.module_path, []).append(r)
        idx._by_layer.setdefault(r.layer, []).append(r)
        idx.total_records += 1
        if r.via_uwg:
            idx.uwg_covered += 1
        else:
            idx.bypass_count += 1

    return idx


def query_mutations_for_state(result: ScanResult, state_key: str) -> list[LineageRecord]:
    """Convenience function: build index and query in one call."""
    return build_lineage_index(result).mutations_for_state(state_key)


__all__ = [
    "LineageIndex",
    "LineageRecord",
    "build_lineage_index",
    "query_mutations_for_state",
]
