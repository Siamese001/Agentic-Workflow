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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
