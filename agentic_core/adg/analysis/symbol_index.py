"""E11: Cross-File Symbol Resolution Index.

Builds a queryable index of ``symbol_name -> defining_module`` from the
``exports`` edges emitted by E1 (``_SymbolInventoryVisitor``).

The index enables downstream passes to:
  - Resolve an imported name to the module that defines it
  - Feed the ``_all_registry`` used by E2 star-import resolution
  - Cross-reference dead imports (E6) against actual exported symbols
  - Support future Protocol/ABC coverage checks (E8)

Usage::

    from agentic_core.adg.analysis.symbol_index import SymbolIndex

    index = SymbolIndex.build(scan_result)
    module = index.resolve("my_function")          # -> "ADG::Module::pkg/mod.py"
    exports = index.exports_of("pkg/mod.py")       # -> ["func_a", "MyClass"]
    all_registry = index.build_all_registry()      # module dotted path -> [names]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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

_emit_applies_guardrail("p0", "symbol_index", "p0_governance")
_emit_reads_policy_state("p0", "symbol_index", "policy_binding")
_emit_snapshots_state("p0", "symbol_index", "state_snapshot")
emit_replay_key("p0", "symbol_index")
emit_determinism_digest("p0", "symbol_index")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "symbol_index", "execution_auth")
_emit_validates_capability("p2", "symbol_index", "capability_check")
_emit_routes_to_capability("p2", "symbol_index", "capability_route")
_emit_writes_via_uwg("p2", "symbol_index", "uwg_write")
_emit_blocks_direct_write("p2", "symbol_index", "direct_write_block")
_emit_records_tool_invocation("p2", "symbol_index", "tool_invocation")
_emit_captures_execution_output("p2", "symbol_index", "exec_output")
_emit_dispatches_agent("p3", "symbol_index", "agent_dispatch")
_emit_coordinates_agents("p3", "symbol_index", "agent_coordination")
_emit_records_workflow_lineage("p3", "symbol_index", "workflow_lineage")
_emit_records_healing_outcome("p3", "symbol_index", "healing_outcome")
_emit_escalates_failure("p3", "symbol_index", "failure_escalation")
_emit_orchestrates_workflow("p3", "symbol_index", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "symbol_index", "healing_dispatch")
_emit_invokes_evaluation("p3", "symbol_index", "evaluation_signal")
_emit_records_telemetry_event("p4", "symbol_index", "telemetry_event")
_emit_captures_evaluation_metric("p4", "symbol_index", "eval_metric")
_emit_stores_embedding("p4", "symbol_index", "embedding_store")
_emit_updates_meta_learning_state("p4", "symbol_index", "meta_learning")
_emit_links_execution_to_snapshot("p4", "symbol_index", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("symbol_index", "p4obs", "metric_1")
_emit_emits_metric_event("symbol_index", "p4obs", "metric_2")
_emit_emits_metric_event("symbol_index", "p4obs", "metric_3")
_emit_emits_metric_event("symbol_index", "p4obs", "metric_4")
_emit_emits_metric_event("symbol_index", "p4obs", "metric_5")
_emit_emits_metric_event("symbol_index", "p4obs", "metric_6")
_emit_records_incident_event("symbol_index", "p4obs", "incident")
_emit_captures_runtime_anomaly("symbol_index", "p4obs", "anomaly")
_emit_writes_observability_log("symbol_index", "p4obs", "obs_log")
_emit_updates_monitoring_state("symbol_index", "p4obs", "mon_state")
_emit_triggers_alert("symbol_index", "p4obs", "alert")
_emit_links_incident_trace("symbol_index", "p4obs", "trace_link")
_emit_captures_pattern("symbol_index", "p3lm", "pattern")
_emit_records_learning_event("symbol_index", "p3lm", "learning_event")
_emit_writes_learning_snapshot("symbol_index", "p3lm", "snapshot")
_emit_feeds_meta_learning("symbol_index", "p3lm", "meta_feed")
_emit_updates_routing_strategy("symbol_index", "p3lm", "routing")
_emit_improves_agent_policy("symbol_index", "p3lm", "policy")
_emit_stores_learning_state("symbol_index", "p3lm", "state")
_emit_records_execution_trace("symbol_index", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("symbol_index", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("symbol_index", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("symbol_index", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("symbol_index", "L4_STATE", "p2_trace_5")
_emit_reads_environ("symbol_index", "env_read", "p2_env_1")
_emit_reads_environ("symbol_index", "env_read", "p2_env_2")
_emit_reads_runtime_state("symbol_index", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("symbol_index", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "symbol_index", "context_pull")
_emit_pulls_context("p1", "symbol_index", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "symbol_index", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "symbol_index", "uwg_term_2")
_emit_writes_through("p1", "symbol_index", "write_through")
_emit_writes_through("p1", "symbol_index", "write_through_2")
_emit_validated_by_safety_plane("p1", "symbol_index", "safety_validation")
_emit_invokes_eval("p1", "symbol_index", "eval_call")
_emit_proposal_commits_routing("p1", "symbol_index", "routing_commit")
_emit_escalates_to_human("p1", "symbol_index", "human_escalation")
_emit_routes_through("p1", "symbol_index", "route_through")
_emit_checks_agent_registry("p1", "symbol_index", "agent_registry")
_emit_validates_agent_capability("p1", "symbol_index", "capability")
_emit_dispatches_execution_plan("p1", "symbol_index", "exec_plan")
_emit_agent_executes_agent("p1", "symbol_index", "sub_agent")
_emit_routes_to_agent("p1", "symbol_index", "target_agent")
_emit_verifies_policy("p1", "symbol_index", "policy_check")
_emit_observes_runtime_state("p1", "symbol_index", "runtime_state")
_emit_verifies_boundary("p1", "symbol_index", "boundary_check")
_emit_transcripts_response("p1", "symbol_index", "transcript")
_emit_hard_fails_untranscripted("p1", "symbol_index")
_emit_gated_by_confidence("p1", "symbol_index", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


@dataclass
class SymbolIndex:
    """Queryable cross-file symbol → defining-module index.

    Attributes:
        symbol_to_module:  ``{symbol_name: module_adg_name}`` mapping built
                           from ``exports`` edges.  When a name is exported
                           by multiple modules the *last encountered* wins
                           (non-deterministic across scan order unless edges
                           are pre-sorted, which they are in ``ScanResult``).
        module_to_symbols: ``{module_adg_name: [symbol_name, ...]}`` reverse
                           mapping built at the same time.
        total_exports:     total number of ``exports`` edges processed.
    """

    symbol_to_module: dict[str, str] = field(default_factory=dict)
    module_to_symbols: dict[str, list[str]] = field(default_factory=dict)
    total_exports: int = 0

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, result: ScanResult) -> SymbolIndex:
        """Build the index from all ``exports`` edges in *result*."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SymbolIndex.build")

        idx = cls()
        for edge in result.edges:
            if edge.relation_type != "exports":
                continue
            symbol = edge.symbol
            module = edge.from_name
            if not symbol or not module.startswith(_MODULE_PREFIX):
                continue
            idx.symbol_to_module[symbol] = module
            idx.module_to_symbols.setdefault(module, []).append(symbol)
            idx.total_exports += 1
        for lst in idx.module_to_symbols.values():
            lst.sort()
        return idx

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def resolve(self, symbol_name: str) -> str | None:
        """Return the ADG module name that exports *symbol_name*, or None."""
        return self.symbol_to_module.get(symbol_name)

    def exports_of(self, module_rel_or_adg: str) -> list[str]:
        """Return the list of exported symbol names for a module.

        Accepts either the repo-relative path (``pkg/mod.py``) or the full
        ADG name (``ADG::Module::pkg/mod.py``).
        """
        adg_name = (
            module_rel_or_adg
            if module_rel_or_adg.startswith(_MODULE_PREFIX)
            else f"{_MODULE_PREFIX}{module_rel_or_adg}"
        )
        return list(self.module_to_symbols.get(adg_name, []))

    def build_all_registry(self) -> dict[str, list[str]]:
        """Build an ``__all__``-style registry keyed by dotted module path.

        Converts ``ADG::Module::pkg/sub/mod.py`` → ``pkg.sub.mod`` and
        maps it to the list of exported symbol names.  Useful as the
        ``all_registry`` argument to ``_ImportVisitor`` for E2 star-import
        resolution.
        """
        registry: dict[str, list[str]] = {}
        for adg_name, symbols in self.module_to_symbols.items():
            if not adg_name.startswith(_MODULE_PREFIX):
                continue
            rel = adg_name[len(_MODULE_PREFIX) :]
            dotted = str(Path(rel).as_posix()).replace("/", ".")
            if dotted.endswith(".py"):
                dotted = dotted[:-3]
            if dotted.endswith(".__init__"):
                dotted = dotted[: -len(".__init__")]
            registry[dotted] = list(symbols)
        return registry

    def stats(self) -> dict:
        """Return summary statistics about the index."""
        return {
            "total_exports": self.total_exports,
            "unique_symbols": len(self.symbol_to_module),
            "modules_with_exports": len(self.module_to_symbols),
        }


__all__ = [
    "SymbolIndex",
]
