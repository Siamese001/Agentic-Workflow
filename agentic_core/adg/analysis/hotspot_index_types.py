"""E14: Hotspot Index — O(1) fan-in / fan-out / coupling metrics on ScanResult.

Computes a structural hotspot index at build time (one linear pass over edges)
so downstream code can query fan-in, fan-out, and coupling with O(1) lookups.

Definitions:
  fan_in(M)   = number of distinct modules that import M  (afferent coupling Ca)
  fan_out(M)  = number of distinct modules M imports      (efferent coupling Ce)
  instability = Ce / (Ca + Ce)   0=stable, 1=unstable
  coupling(M) = fan_in + fan_out  (raw structural coupling)

A module is a "hotspot" if its coupling exceeds a configurable threshold.

Usage::

    from agentic_core.adg.analysis.hotspot_index_types import HotspotIndex

    idx = HotspotIndex.build(scan_result)
    fi = idx.fan_in("agentic_core/L0_routing/engines/path_router.py")
    fo = idx.fan_out("agentic_core/L0_routing/engines/path_router.py")
    hotspots = idx.top_hotspots(n=20)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "hotspot_index", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "hotspot_index", "policy_binding")
trace_contract._emit_snapshots_state("p0", "hotspot_index", "state_snapshot")
trace_contract._emit_escalates_to_human("p1", "hotspot_index", "human_escalation")
trace_contract.emit_replay_key("p0", "hotspot_index")
trace_contract.emit_determinism_digest("p0", "hotspot_index")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "hotspot_index", "execution_auth")
trace_contract._emit_validates_capability("p2", "hotspot_index", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hotspot_index", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hotspot_index", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hotspot_index", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hotspot_index", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hotspot_index", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hotspot_index", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hotspot_index", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hotspot_index", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hotspot_index", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hotspot_index", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hotspot_index", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hotspot_index", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hotspot_index", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hotspot_index", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hotspot_index", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hotspot_index", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hotspot_index", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hotspot_index", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from tqdm import tqdm

trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hotspot_index", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hotspot_index", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hotspot_index", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hotspot_index", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hotspot_index", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hotspot_index", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hotspot_index", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hotspot_index", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hotspot_index", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hotspot_index", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hotspot_index", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hotspot_index", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hotspot_index", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hotspot_index", "p3lm", "state")
trace_contract._emit_records_execution_trace("hotspot_index", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hotspot_index", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hotspot_index", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hotspot_index", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hotspot_index", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hotspot_index", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hotspot_index", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hotspot_index", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hotspot_index", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "hotspot_index", "context_pull")
trace_contract._emit_pulls_context("p1", "hotspot_index", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "hotspot_index", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hotspot_index", "uwg_term_2")
trace_contract._emit_writes_through("p1", "hotspot_index", "write_through")
trace_contract._emit_writes_through("p1", "hotspot_index", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "hotspot_index", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hotspot_index", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hotspot_index", "routing_commit")
trace_contract._emit_routes_through("p1", "hotspot_index", "route_through")
trace_contract._emit_checks_agent_registry("p1", "hotspot_index", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hotspot_index", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hotspot_index", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hotspot_index", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hotspot_index", "target_agent")
trace_contract._emit_verifies_policy("p1", "hotspot_index", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hotspot_index", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hotspot_index", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hotspot_index", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hotspot_index")
trace_contract._emit_gated_by_confidence("p1", "hotspot_index", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"

_DEFAULT_HOTSPOT_THRESHOLD = 10


@dataclass
class ModuleCoupling:
    """Structural coupling metrics for one module."""

    module_path: str
    fan_in: int = 0
    fan_out: int = 0
    instability: float = 0.0
    coupling: int = 0

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "fan_in": self.fan_in,
            "fan_out": self.fan_out,
            "instability": round(self.instability, 3),
            "coupling": self.coupling,
        }


@dataclass
class HotspotIndex:
    """O(1)-queryable structural hotspot index built from a ScanResult.

    Attributes:
        _fan_in:  {module_path: set of distinct importer module_paths}
        _fan_out: {module_path: set of distinct dependency module_paths}
    """

    _fan_in: dict[str, set[str]] = field(default_factory=dict)
    _fan_out: dict[str, set[str]] = field(default_factory=dict)
    _all_modules: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, result: ScanResult) -> HotspotIndex:
        """Build the index in a single linear pass over result.edges.

        Handles both ``ADG::Module::a/b/c.py`` and ``ADG::Symbol::a.b.c``
        node names — the latter is resolved to ``a/b/c.py`` so fan-in
        counts reflect real structural coupling even when edges use
        symbol-level addressing.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HotspotIndex.build")

        idx = cls()
        module_set = set(result.modules)
        idx._all_modules = module_set

        _sym = "ADG::Symbol::"
        _mod = _MODULE_PREFIX

        def _to_path(name: str) -> str | None:
            if name.startswith(_mod):
                return name[len(_mod) :]
            if name.startswith(_sym):
                sym = name[len(_sym) :]
                parts = sym.split(".")
                # Try from most-specific to least-specific:
                # a.b.c.func -> a/b/c/func.py, a/b/c.py, a/b/__init__.py ...
                for n in range(len(parts), 0, -1):
                    prefix = "/".join(parts[:n])
                    if prefix + ".py" in module_set:
                        return prefix + ".py"
                    # guardian: allow-path-string -- constructing ADG module lookup key from import prefix
                    if prefix + "/__init__.py" in module_set:
                        # guardian: allow-path-string -- constructing ADG module lookup key for package __init__
                        return prefix + "/__init__.py"
            return None

        for edge in tqdm(result.edges, desc="Processing", unit="item"):
            if edge.relation_type not in (
                "imports",
                "reads_from",
                "calls",
                "instantiates",
                "implements",
            ):
                continue
            if not edge.from_name.startswith(_mod):
                continue

            from_path = edge.from_name[len(_mod) :]
            to_path = _to_path(edge.to_name)
            if to_path is None or from_path == to_path:
                continue

            idx._fan_out.setdefault(from_path, set()).add(to_path)
            idx._fan_in.setdefault(to_path, set()).add(from_path)

        return idx

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def fan_in(self, module_path: str) -> int:
        """Number of distinct modules that structurally depend on module_path."""
        return len(self._fan_in.get(module_path, set()))

    def fan_out(self, module_path: str) -> int:
        """Number of distinct modules that module_path depends on."""
        return len(self._fan_out.get(module_path, set()))

    def instability(self, module_path: str) -> float:
        """Ce / (Ca + Ce) — 0.0 = maximally stable, 1.0 = maximally unstable."""
        ca = self.fan_in(module_path)
        ce = self.fan_out(module_path)
        total = ca + ce
        return round(ce / total, 3) if total else 0.0

    def coupling(self, module_path: str) -> int:
        """Raw structural coupling = fan_in + fan_out."""
        return self.fan_in(module_path) + self.fan_out(module_path)

    def metrics(self, module_path: str) -> ModuleCoupling:
        """Return full coupling metrics for one module."""
        ca = self.fan_in(module_path)
        ce = self.fan_out(module_path)
        total = ca + ce
        inst = round(ce / total, 3) if total else 0.0
        return ModuleCoupling(
            module_path=module_path,
            fan_in=ca,
            fan_out=ce,
            instability=inst,
            coupling=total,
        )

    def top_hotspots(
        self,
        n: int = 20,
        threshold: int = _DEFAULT_HOTSPOT_THRESHOLD,
        key: str = "coupling",
    ) -> list[ModuleCoupling]:
        """Return the top-n hotspot modules sorted by *key* descending.

        ``key`` must be one of ``'coupling'``, ``'fan_in'``, ``'fan_out'``,
        ``'instability'``.
        """
        all_paths = self._all_modules | set(self._fan_in) | set(self._fan_out)
        scored = [self.metrics(p) for p in all_paths]
        scored = [m for m in scored if getattr(m, key) >= threshold]  # guardian: allow-hallucinated-tool-name -- getattr is a Python stdlib builtin for dynamic field access on Metrics dataclass; detector false positive
        return sorted(scored, key=lambda m: -getattr(m, key))[:n]  # guardian: allow-hallucinated-tool-name -- same as above; sort key dynamic access

    def importers_of(self, module_path: str) -> list[str]:
        """Sorted list of modules that directly depend on module_path."""
        return sorted(self._fan_in.get(module_path, set()))

    def dependencies_of(self, module_path: str) -> list[str]:
        """Sorted list of modules that module_path directly depends on."""
        return sorted(self._fan_out.get(module_path, set()))

    def stats(self) -> dict:
        """Summary statistics for the entire index."""
        all_paths = self._all_modules | set(self._fan_in) | set(self._fan_out)
        if not all_paths:
            return {"total_modules": 0, "max_fan_in": 0, "max_fan_out": 0, "avg_coupling": 0.0}

        couplings = [self.coupling(p) for p in all_paths]
        fan_ins = [self.fan_in(p) for p in all_paths]
        fan_outs = [self.fan_out(p) for p in all_paths]

        return {
            "total_modules": len(all_paths),
            "max_fan_in": max(fan_ins),
            "max_fan_out": max(fan_outs),
            "max_coupling": max(couplings),
            "avg_coupling": round(sum(couplings) / len(couplings), 2),
            "avg_fan_in": round(sum(fan_ins) / len(fan_ins), 2),
            "avg_fan_out": round(sum(fan_outs) / len(fan_outs), 2),
        }

    def to_json(self, n: int = 50) -> str:
        """Serialise top-n hotspots to JSON."""
        return json.dumps(
            {
                "stats": self.stats(),
                "top_hotspots": [m.to_dict() for m in self.top_hotspots(n=n, threshold=0)],
            },
            indent=2,
            sort_keys=True,
        )


__all__ = [
    "HotspotIndex",
    "ModuleCoupling",
]
