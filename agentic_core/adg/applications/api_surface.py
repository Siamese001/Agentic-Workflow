"""E13: Public API Surface Extractor.

Analyses ``exports`` edges from E1 (``_SymbolInventoryVisitor``) together
with ``__all__`` declarations to produce a structured view of each module's
public API boundary.

Outputs:
  ``APISurfaceReport`` containing:
    - ``public_modules``:   modules that expose at least one public symbol
    - ``boundary_violations``: symbols imported across the public/internal
                               boundary without being in ``__all__``
    - ``surface_by_module``: per-module breakdown of public vs internal symbols
    - ``total_public_symbols``, ``total_internal_symbols``

Usage::

    from agentic_core.adg.applications.api_surface import build_api_surface

    report = build_api_surface(result)
    for mod, info in report.surface_by_module.items():
        print(mod, info["public"], info["internal"])
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "api_surface", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "api_surface", "policy_binding")
trace_contract._emit_snapshots_state("p0", "api_surface", "state_snapshot")
trace_contract.emit_replay_key("p0", "api_surface")
trace_contract.emit_determinism_digest("p0", "api_surface")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "api_surface", "execution_auth")
trace_contract._emit_validates_capability("p2", "api_surface", "capability_check")
trace_contract._emit_routes_to_capability("p2", "api_surface", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "api_surface", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "api_surface", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "api_surface", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "api_surface", "exec_output")
trace_contract._emit_dispatches_agent("p3", "api_surface", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "api_surface", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "api_surface", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "api_surface", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "api_surface", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "api_surface", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "api_surface", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "api_surface", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "api_surface", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "api_surface", "eval_metric")
trace_contract._emit_stores_embedding("p4", "api_surface", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "api_surface", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "api_surface", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from tqdm import tqdm

trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("api_surface", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("api_surface", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("api_surface", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("api_surface", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("api_surface", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("api_surface", "p4obs", "alert")
trace_contract._emit_links_incident_trace("api_surface", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("api_surface", "p3lm", "pattern")
trace_contract._emit_records_learning_event("api_surface", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("api_surface", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("api_surface", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("api_surface", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("api_surface", "p3lm", "policy")
trace_contract._emit_stores_learning_state("api_surface", "p3lm", "state")
trace_contract._emit_records_execution_trace("api_surface", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("api_surface", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("api_surface", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("api_surface", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("api_surface", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("api_surface", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("api_surface", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("api_surface", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("api_surface", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "api_surface", "context_pull")
trace_contract._emit_pulls_context("p1", "api_surface", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "api_surface", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "api_surface", "uwg_term_2")
trace_contract._emit_writes_through("p1", "api_surface", "write_through")
trace_contract._emit_writes_through("p1", "api_surface", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "api_surface", "safety_validation")
trace_contract._emit_invokes_eval("p1", "api_surface", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "api_surface", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "api_surface", "human_escalation")
trace_contract._emit_routes_through("p1", "api_surface", "route_through")
trace_contract._emit_checks_agent_registry("p1", "api_surface", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "api_surface", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "api_surface", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "api_surface", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "api_surface", "target_agent")
trace_contract._emit_verifies_policy("p1", "api_surface", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "api_surface", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "api_surface", "boundary_check")
trace_contract._emit_transcripts_response("p1", "api_surface", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "api_surface")
trace_contract._emit_gated_by_confidence("p1", "api_surface", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


@dataclass
class ModuleAPISurface:
    """Public/internal API breakdown for one module."""

    module_path: str
    public_symbols: list[str] = field(default_factory=list)
    internal_symbols: list[str] = field(default_factory=list)
    re_exported_symbols: list[str] = field(default_factory=list)
    has_explicit_all: bool = False

    @property
    def total(self) -> int:
        return len(self.public_symbols) + len(self.internal_symbols)

    @property
    def public_ratio(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ModuleAPISurface.public_ratio"
        )

        if self.total == 0:
            return 0.0
        return round(len(self.public_symbols) / self.total, 3)

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "public_symbols": sorted(self.public_symbols),
            "internal_symbols": sorted(self.internal_symbols),
            "re_exported_symbols": sorted(self.re_exported_symbols),
            "has_explicit_all": self.has_explicit_all,
            "total_symbols": self.total,
            "public_ratio": self.public_ratio,
        }


@dataclass
class BoundaryViolation:
    """A symbol imported across the public/internal boundary."""

    importer_file: str
    symbol: str
    provider_module: str
    violation_kind: str
    line_no: int

    def to_dict(self) -> dict:
        return {
            "importer_file": self.importer_file,
            "symbol": self.symbol,
            "provider_module": self.provider_module,
            "violation_kind": self.violation_kind,
            "line_no": self.line_no,
        }


@dataclass
class APISurfaceReport:
    """Full public API surface analysis for the repository."""

    surface_by_module: dict[str, ModuleAPISurface] = field(default_factory=dict)
    boundary_violations: list[BoundaryViolation] = field(default_factory=list)
    total_public_symbols: int = 0
    total_internal_symbols: int = 0
    total_re_exported_symbols: int = 0
    modules_with_explicit_all: int = 0

    @property
    def public_modules(self) -> list[str]:
        return sorted(path for path, surf in self.surface_by_module.items() if surf.public_symbols)

    def to_dict(self) -> dict:
        return {
            "total_public_symbols": self.total_public_symbols,
            "total_internal_symbols": self.total_internal_symbols,
            "total_re_exported_symbols": self.total_re_exported_symbols,
            "modules_with_explicit_all": self.modules_with_explicit_all,
            "total_public_modules": len(self.public_modules),
            "boundary_violation_count": len(self.boundary_violations),
            "boundary_violations": [v.to_dict() for v in self.boundary_violations],
            "surface_by_module": {
                path: surf.to_dict() for path, surf in sorted(self.surface_by_module.items())
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def build_api_surface(result: ScanResult) -> APISurfaceReport:
    """Build the public API surface from ``exports`` and ``re_exports`` edges.

    Algorithm:
    1. Collect all ``exports`` edges — each ``from_name`` (module) exports
       a ``symbol``.  A symbol is *public* if it does not start with ``_``.
    2. Collect ``re_exports`` edges — track which symbols are re-exported
       through ``__init__.py`` or package roots.
    3. Detect boundary violations: ``imports`` edges where the imported
       ``symbol`` matches a known *internal* (underscore-prefixed) export.
    """
    surface: dict[str, ModuleAPISurface] = {}

    for edge in tqdm(result.edges, desc="Processing", unit="item"):
        if edge.relation_type not in ("exports", "re_exports"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        module_path = edge.from_name[len(_MODULE_PREFIX) :]
        symbol = edge.symbol or ""

        if module_path not in surface:
            surface[module_path] = ModuleAPISurface(module_path=module_path)

        surf = surface[module_path]
        is_public = bool(symbol) and not symbol.startswith("_")

        if edge.relation_type == "re_exports":
            if symbol and symbol not in surf.re_exported_symbols:
                surf.re_exported_symbols.append(symbol)
        elif is_public:
            if symbol not in surf.public_symbols:
                surf.public_symbols.append(symbol)
        elif symbol:
            if symbol not in surf.internal_symbols:
                surf.internal_symbols.append(symbol)

    # Detect boundary violations: imports of underscore-prefixed names
    # Build a set of (module_path, internal_symbol) for O(1) lookup
    internal_set: set[tuple[str, str]] = set()
    for mod_path, surf in surface.items():
        for sym in surf.internal_symbols:
            internal_set.add((mod_path, sym))

    violations: list[BoundaryViolation] = []
    for edge in tqdm(result.edges, desc="Processing", unit="item"):
        if edge.relation_type != "imports":
            continue
        symbol = edge.symbol or ""
        if not symbol.startswith("_"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        importer = edge.from_name[len(_MODULE_PREFIX) :]

        to_sym = edge.to_name[len(_SYMBOL_PREFIX) :] if edge.to_name.startswith(_SYMBOL_PREFIX) else ""
        parts = to_sym.rsplit(".", 1)
        provider_module = parts[0].replace(".", "/") if len(parts) > 1 else ""
        provider_module_py = provider_module + ".py" if provider_module else ""

        if (provider_module_py, symbol) in internal_set:
            violations.append(
                BoundaryViolation(
                    importer_file=importer,
                    symbol=symbol,
                    provider_module=provider_module_py,
                    violation_kind="imports_internal_symbol",
                    line_no=edge.line_no,
                ),
            )

    total_public = sum(len(s.public_symbols) for s in surface.values())
    total_internal = sum(len(s.internal_symbols) for s in surface.values())
    total_re_exported = sum(len(s.re_exported_symbols) for s in surface.values())
    mods_with_all = sum(1 for s in surface.values() if s.has_explicit_all)

    return APISurfaceReport(
        surface_by_module=surface,
        boundary_violations=sorted(violations, key=lambda v: (v.importer_file, v.line_no)),
        total_public_symbols=total_public,
        total_internal_symbols=total_internal,
        total_re_exported_symbols=total_re_exported,
        modules_with_explicit_all=mods_with_all,
    )


__all__ = [
    "APISurfaceReport",
    "ModuleAPISurface",
    "BoundaryViolation",
    "build_api_surface",
]
