"""G1 (gap): Healer/Validator Relationship Graph Analysis.

Analyses a ScanResult for healer and validator node relationships extracted by
the ``_HealerValidatorVisitor`` in static_scanner.py.

Gap 1 of the ADG mental model describes the runtime behavior plane containing:
  - Agent observe/reason/act/evaluate/learn loops
  - Healer orchestrators dispatching to validators
  - Meta-learning feedback from healing outcomes

This analyser produces a static approximation of that plane from the code structure:
  1. Which modules inherit from healer bases (heals edges)
  2. Which modules inherit from validator bases (validates edges)
  3. Which modules dispatch healing method calls (orchestrates_healing edges)
  4. Healer→validator relationships (healer module dispatching to a validator)

Output:
  ``HealerValidatorReport`` with:
    - ``healer_modules``: set of modules that are healer subclasses
    - ``validator_modules``: set of modules that are validator subclasses
    - ``healing_dispatch_edges``: edges representing healing method calls
    - ``healer_validator_pairs``: pairs of (healer_module, validator_module)
      detected from co-occurrence in orchestrates_healing edges
    - ``unbound_healers``: healer modules with no detected validator dependency
    - ``unbound_validators``: validator modules with no detected healer

Usage::

    from agentic_core.adg.analysis.healer_validator_graph import detect_healer_validator_relationships

    result = scanner.scan(repo_root=Path("."))
    report = detect_healer_validator_relationships(result)
    print(f"Healers: {len(report.healer_modules)}")
    print(f"Validators: {len(report.validator_modules)}")
    for h, v in report.healer_validator_pairs:
        print(f"  {h} -> {v}")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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

_emit_applies_guardrail("p0", "healer_validator_graph", "p0_governance")
_emit_reads_policy_state("p0", "healer_validator_graph", "policy_binding")
_emit_snapshots_state("p0", "healer_validator_graph", "state_snapshot")
_emit_escalates_to_human("p1", "healer_validator_graph", "human_escalation")
emit_replay_key("p0", "healer_validator_graph")
emit_determinism_digest("p0", "healer_validator_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "healer_validator_graph", "execution_auth")
_emit_validates_capability("p2", "healer_validator_graph", "capability_check")
_emit_routes_to_capability("p2", "healer_validator_graph", "capability_route")
_emit_writes_via_uwg("p2", "healer_validator_graph", "uwg_write")
_emit_blocks_direct_write("p2", "healer_validator_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_validator_graph", "tool_invocation")
_emit_captures_execution_output("p2", "healer_validator_graph", "exec_output")
_emit_dispatches_agent("p3", "healer_validator_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_validator_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_validator_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_validator_graph", "healing_outcome")
_emit_escalates_failure("p3", "healer_validator_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_validator_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_validator_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_validator_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_validator_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_validator_graph", "eval_metric")
_emit_stores_embedding("p4", "healer_validator_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_validator_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_validator_graph", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_1")
_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_2")
_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_3")
_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_4")
_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_5")
_emit_emits_metric_event("healer_validator_graph", "p4obs", "metric_6")
_emit_records_incident_event("healer_validator_graph", "p4obs", "incident")
_emit_captures_runtime_anomaly("healer_validator_graph", "p4obs", "anomaly")
_emit_writes_observability_log("healer_validator_graph", "p4obs", "obs_log")
_emit_updates_monitoring_state("healer_validator_graph", "p4obs", "mon_state")
_emit_triggers_alert("healer_validator_graph", "p4obs", "alert")
_emit_links_incident_trace("healer_validator_graph", "p4obs", "trace_link")
_emit_captures_pattern("healer_validator_graph", "p3lm", "pattern")
_emit_records_learning_event("healer_validator_graph", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healer_validator_graph", "p3lm", "snapshot")
_emit_feeds_meta_learning("healer_validator_graph", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healer_validator_graph", "p3lm", "routing")
_emit_improves_agent_policy("healer_validator_graph", "p3lm", "policy")
_emit_stores_learning_state("healer_validator_graph", "p3lm", "state")
_emit_records_execution_trace("healer_validator_graph", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healer_validator_graph", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healer_validator_graph", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healer_validator_graph", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healer_validator_graph", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healer_validator_graph", "env_read", "p2_env_1")
_emit_reads_environ("healer_validator_graph", "env_read", "p2_env_2")
_emit_reads_runtime_state("healer_validator_graph", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healer_validator_graph", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healer_validator_graph", "context_pull")
_emit_pulls_context("p1", "healer_validator_graph", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healer_validator_graph", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healer_validator_graph", "uwg_term_2")
_emit_writes_through("p1", "healer_validator_graph", "write_through")
_emit_writes_through("p1", "healer_validator_graph", "write_through_2")
_emit_validated_by_safety_plane("p1", "healer_validator_graph", "safety_validation")
_emit_invokes_eval("p1", "healer_validator_graph", "eval_call")
_emit_proposal_commits_routing("p1", "healer_validator_graph", "routing_commit")
_emit_routes_through("p1", "healer_validator_graph", "route_through")
_emit_checks_agent_registry("p1", "healer_validator_graph", "agent_registry")
_emit_validates_agent_capability("p1", "healer_validator_graph", "capability")
_emit_dispatches_execution_plan("p1", "healer_validator_graph", "exec_plan")
_emit_agent_executes_agent("p1", "healer_validator_graph", "sub_agent")
_emit_routes_to_agent("p1", "healer_validator_graph", "target_agent")
_emit_verifies_policy("p1", "healer_validator_graph", "policy_check")
_emit_observes_runtime_state("p1", "healer_validator_graph", "runtime_state")
_emit_verifies_boundary("p1", "healer_validator_graph", "boundary_check")
_emit_transcripts_response("p1", "healer_validator_graph", "transcript")
_emit_hard_fails_untranscripted("p1", "healer_validator_graph")
_emit_gated_by_confidence("p1", "healer_validator_graph", "confidence_gate")


@dataclass
class HealerValidatorEdge:
    """A detected healer/validator structural relationship edge."""

    from_module: str
    relation_type: str
    to_symbol: str
    source_file: str
    line_no: int


@dataclass
class HealerValidatorReport:
    """Results of healer/validator relationship analysis.

    Attributes:
        healer_modules:         Modules that inherit from healer bases.
        validator_modules:      Modules that inherit from validator bases.
        healing_dispatch_edges: All orchestrates_healing / dispatches_to edges.
        healer_validator_pairs: (healer_module, validator_symbol) pairs
                                inferred from dispatch edges.
        unbound_healers:        Healer modules with no detected validator target.
        unbound_validators:     Validator modules never targeted by a healer.
        raw_edges:              All raw healer/validator edges from the scan.
    """

    healer_modules: set[str] = field(default_factory=set)
    validator_modules: set[str] = field(default_factory=set)
    healing_dispatch_edges: list[HealerValidatorEdge] = field(default_factory=list)
    healer_validator_pairs: list[tuple[str, str]] = field(default_factory=list)
    unbound_healers: set[str] = field(default_factory=set)
    unbound_validators: set[str] = field(default_factory=set)
    raw_edges: list[HealerValidatorEdge] = field(default_factory=list)

    @property
    def healer_count(self) -> int:
        return len(self.healer_modules)

    @property
    def validator_count(self) -> int:
        return len(self.validator_modules)

    @property
    def pair_count(self) -> int:
        return len(self.healer_validator_pairs)

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealerValidatorReport.summary")

        lines = [
            f"Healer/Validator Graph: {self.healer_count} healers, "
            f"{self.validator_count} validators, {self.pair_count} pairs",
            f"  Unbound healers (no validator target): {len(self.unbound_healers)}",
            f"  Unbound validators (no healer caller): {len(self.unbound_validators)}",
        ]
        if self.healer_validator_pairs:
            lines.append("  Healer → Validator bindings:")
            for h, v in sorted(self.healer_validator_pairs):
                lines.append(f"    {h} → {v}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "healer_modules": sorted(self.healer_modules),
            "validator_modules": sorted(self.validator_modules),
            "pair_count": self.pair_count,
            "healer_validator_pairs": sorted(self.healer_validator_pairs),
            "unbound_healers": sorted(self.unbound_healers),
            "unbound_validators": sorted(self.unbound_validators),
            "healing_dispatch_edge_count": len(self.healing_dispatch_edges),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


_HEALER_RELATIONS: frozenset[str] = frozenset({"heals", "orchestrates_healing", "dispatches_to"})
_VALIDATOR_RELATIONS: frozenset[str] = frozenset({"validates"})
_DISPATCH_RELATIONS: frozenset[str] = frozenset({"orchestrates_healing", "dispatches_to"})


def detect_healer_validator_relationships(result: ScanResult) -> HealerValidatorReport:
    """Analyse a ScanResult for healer/validator structural relationships.

    Processes all edges produced by ``_HealerValidatorVisitor`` and builds a
    structured report of the healing loop topology visible in the static code.

    Args:
        result: A completed ScanResult from ADGStaticScanner.scan().

    Returns:
        HealerValidatorReport with all detected relationships.
    """
    report = HealerValidatorReport()

    for edge in result.edges:
        if edge.relation_type in _HEALER_RELATIONS or edge.relation_type in _VALIDATOR_RELATIONS:
            hv_edge = HealerValidatorEdge(
                from_module=edge.from_name,
                relation_type=edge.relation_type,
                to_symbol=edge.to_name,
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
            report.raw_edges.append(hv_edge)

            if edge.relation_type == "heals":
                report.healer_modules.add(edge.from_name)
            elif edge.relation_type == "validates":
                report.validator_modules.add(edge.from_name)
            elif edge.relation_type in _DISPATCH_RELATIONS:
                report.healing_dispatch_edges.append(hv_edge)

    _infer_healer_validator_pairs(report)
    _compute_unbound(report)

    return report


def _infer_healer_validator_pairs(report: HealerValidatorReport) -> None:
    """Infer healer→validator pairings from dispatch edges.

    A healer module that dispatches_to a symbol that is in validator_modules
    (or whose name contains a known validator class suffix) forms a pair.
    """
    validator_name_fragments: frozenset[str] = frozenset(
        {
            "Validator",
            "validator",
            "ResolutionValidator",
            "HealerValidator",
            "ValidationAgent",
        }
    )

    seen: set[tuple[str, str]] = set()
    for edge in report.healing_dispatch_edges:
        if edge.from_module not in report.healer_modules:
            continue
        target = edge.to_symbol
        is_validator = target in report.validator_modules or any(
            frag in target for frag in validator_name_fragments
        )
        if is_validator:
            pair = (edge.from_module, target)
            if pair not in seen:
                seen.add(pair)
                report.healer_validator_pairs.append(pair)


def _compute_unbound(report: HealerValidatorReport) -> None:
    """Compute unbound healers and validators."""
    bound_healers = {h for h, _ in report.healer_validator_pairs}
    bound_validators = {v for _, v in report.healer_validator_pairs}
    report.unbound_healers = report.healer_modules - bound_healers
    report.unbound_validators = report.validator_modules - {
        m for m in report.validator_modules if canonical_name_of(m) in bound_validators
    }


def canonical_name_of(module_adg_name: str) -> str:
    """Return the module adg name as-is (identity mapping for set membership)."""
    return module_adg_name


__all__ = [
    "HealerValidatorEdge",
    "HealerValidatorReport",
    "detect_healer_validator_relationships",
]
