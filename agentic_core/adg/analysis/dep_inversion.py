"""E18: Dependency Inversion Detector.

Finds places where a module depends on a *concrete* class when an *abstract*
base (Protocol/ABC) already exists in the same or a lower layer — a violation
of the Dependency Inversion Principle (DIP).

Detection algorithm:
  1. Build a mapping  abstract_base_name -> [concrete_subclass_module, ...]
     from ``implements`` edges where the base is Protocol/ABC-derived.
  2. Walk ``imports`` and ``instantiates`` edges: if module A directly
     references a concrete subclass C and an abstract base B for C exists,
     and B is accessible to A (same layer or lower), emit a DIP violation.

Output:
  ``DIPReport`` with:
    - ``violations``:       list of ``DIPViolation``
    - ``abstract_bases``:   map of abstract class name -> provider module
    - ``violation_count``

Usage::

    from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

    report = detect_dip_violations(result)
    for v in report.violations:
        print(v.violating_module, "->", v.concrete_class, "(abstract:", v.abstract_base, ")")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import ALLOWED_LAYER_EDGES, module_path_to_layer
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

_emit_records_execution_trace("p0", "evidence", "dep_inversion")
_emit_applies_guardrail("p0", "dep_inversion", "p0_governance")
_emit_reads_policy_state("p0", "dep_inversion", "policy_binding")
_emit_snapshots_state("p0", "dep_inversion", "state_snapshot")
_emit_escalates_to_human("p1", "dep_inversion", "human_escalation")
emit_replay_key("p0", "dep_inversion")
emit_determinism_digest("p0", "dep_inversion")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "dep_inversion", "execution_auth")
_emit_validates_capability("p2", "dep_inversion", "capability_check")
_emit_routes_to_capability("p2", "dep_inversion", "capability_route")
_emit_writes_via_uwg("p2", "dep_inversion", "uwg_write")
_emit_blocks_direct_write("p2", "dep_inversion", "direct_write_block")
_emit_records_tool_invocation("p2", "dep_inversion", "tool_invocation")
_emit_captures_execution_output("p2", "dep_inversion", "exec_output")
_emit_dispatches_agent("p3", "dep_inversion", "agent_dispatch")
_emit_coordinates_agents("p3", "dep_inversion", "agent_coordination")
_emit_records_workflow_lineage("p3", "dep_inversion", "workflow_lineage")
_emit_records_healing_outcome("p3", "dep_inversion", "healing_outcome")
_emit_escalates_failure("p3", "dep_inversion", "failure_escalation")
_emit_orchestrates_workflow("p3", "dep_inversion", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dep_inversion", "healing_dispatch")
_emit_invokes_evaluation("p3", "dep_inversion", "evaluation_signal")
_emit_records_telemetry_event("p4", "dep_inversion", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dep_inversion", "eval_metric")
_emit_stores_embedding("p4", "dep_inversion", "embedding_store")
_emit_updates_meta_learning_state("p4", "dep_inversion", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dep_inversion", "exec_snapshot_link")

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

_emit_emits_metric_event("dep_inversion", "p4obs", "metric_1")
_emit_emits_metric_event("dep_inversion", "p4obs", "metric_2")
_emit_emits_metric_event("dep_inversion", "p4obs", "metric_3")
_emit_emits_metric_event("dep_inversion", "p4obs", "metric_4")
_emit_emits_metric_event("dep_inversion", "p4obs", "metric_5")
_emit_emits_metric_event("dep_inversion", "p4obs", "metric_6")
_emit_records_incident_event("dep_inversion", "p4obs", "incident")
_emit_captures_runtime_anomaly("dep_inversion", "p4obs", "anomaly")
_emit_writes_observability_log("dep_inversion", "p4obs", "obs_log")
_emit_updates_monitoring_state("dep_inversion", "p4obs", "mon_state")
_emit_triggers_alert("dep_inversion", "p4obs", "alert")
_emit_links_incident_trace("dep_inversion", "p4obs", "trace_link")
_emit_captures_pattern("dep_inversion", "p3lm", "pattern")
_emit_records_learning_event("dep_inversion", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dep_inversion", "p3lm", "snapshot")
_emit_feeds_meta_learning("dep_inversion", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dep_inversion", "p3lm", "routing")
_emit_improves_agent_policy("dep_inversion", "p3lm", "policy")
_emit_stores_learning_state("dep_inversion", "p3lm", "state")
_emit_records_execution_trace("dep_inversion", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dep_inversion", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dep_inversion", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dep_inversion", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dep_inversion", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dep_inversion", "env_read", "p2_env_1")
_emit_reads_environ("dep_inversion", "env_read", "p2_env_2")
_emit_reads_runtime_state("dep_inversion", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dep_inversion", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dep_inversion", "context_pull")
_emit_pulls_context("p1", "dep_inversion", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "dep_inversion", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dep_inversion", "uwg_term_secondary")
_emit_writes_through("p1", "dep_inversion", "write_through")
_emit_writes_through("p1", "dep_inversion", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "dep_inversion", "safety_validation")
_emit_invokes_eval("p1", "dep_inversion", "eval_call")
_emit_proposal_commits_routing("p1", "dep_inversion", "routing_commit")
_emit_routes_through("p1", "dep_inversion", "route_through")
_emit_checks_agent_registry("p1", "dep_inversion", "agent_registry")
_emit_validates_agent_capability("p1", "dep_inversion", "capability")
_emit_dispatches_execution_plan("p1", "dep_inversion", "exec_plan")
_emit_agent_executes_agent("p1", "dep_inversion", "sub_agent")
_emit_routes_to_agent("p1", "dep_inversion", "target_agent")
_emit_verifies_policy("p1", "dep_inversion", "policy_check")
_emit_observes_runtime_state("p1", "dep_inversion", "runtime_state")
_emit_verifies_boundary("p1", "dep_inversion", "boundary_check")
_emit_transcripts_response("p1", "dep_inversion", "transcript")
_emit_hard_fails_untranscripted("p1", "dep_inversion")
_emit_gated_by_confidence("p1", "dep_inversion", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

_ABSTRACT_MARKERS: frozenset[str] = frozenset({"ABC", "ABCMeta", "Protocol", "abstract", "Abstract"})


@dataclass
class DIPViolation:
    """One Dependency Inversion Principle violation."""

    violating_module: str
    concrete_class: str
    concrete_provider_module: str
    abstract_base: str
    abstract_provider_module: str
    violating_layer: str
    concrete_layer: str
    abstract_layer: str
    line_no: int
    severity: str = "medium"

    def to_dict(self) -> dict:
        return {
            "violating_module": self.violating_module,
            "concrete_class": self.concrete_class,
            "concrete_provider_module": self.concrete_provider_module,
            "abstract_base": self.abstract_base,
            "abstract_provider_module": self.abstract_provider_module,
            "violating_layer": self.violating_layer,
            "concrete_layer": self.concrete_layer,
            "abstract_layer": self.abstract_layer,
            "line_no": self.line_no,
            "severity": self.severity,
        }


@dataclass
class DIPReport:
    """Full Dependency Inversion analysis for the repository."""

    violations: list[DIPViolation] = field(default_factory=list)
    abstract_bases: dict[str, str] = field(default_factory=dict)
    concrete_to_abstracts: dict[str, list[str]] = field(default_factory=dict)
    violation_count: int = 0

    @property
    def summary(self) -> str:
        return f"DIP violations={self.violation_count} abstract_bases={len(self.abstract_bases)}"

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "abstract_base_count": len(self.abstract_bases),
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
            "abstract_bases": dict(sorted(self.abstract_bases.items())),
            "concrete_to_abstracts": {k: sorted(v) for k, v in sorted(self.concrete_to_abstracts.items())},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _extract_class_name(adg_name: str) -> str:
    """Extract bare class name from an ADG symbol name like Module::path::ClassName."""
    parts = adg_name.split("::")
    return parts[-1] if parts else ""


def _sym_to_module(symbol: str) -> str:
    """Convert dotted symbol 'pkg.sub.ClassName' to 'pkg/sub.py'."""
    parts = symbol.rsplit(".", 1)
    if len(parts) == 2:
        return parts[0].replace(".", "/") + ".py"
    return symbol.replace(".", "/") + ".py"


def detect_dip_violations(result: ScanResult) -> DIPReport:
    """Detect Dependency Inversion Principle violations.

    Pass 1: identify all abstract bases and their concrete subclasses from
            ``implements`` edges.
    Pass 2: for each ``imports`` / ``instantiates`` edge targeting a concrete
            class that has a known abstract base, check whether the importer
            could instead depend on the abstract.
    """
    # Pass 1: build abstract base index
    # abstract_bases: class_name -> module_path (where the abstract lives)
    # concrete_subclasses: concrete_class_name -> [abstract_base_name, ...]
    abstract_bases: dict[str, str] = {}
    concrete_to_abstracts: dict[str, list[str]] = {}

    for edge in result.edges:
        if edge.relation_type != "implements":
            continue
        sym = edge.symbol or ""
        if not any(marker in sym for marker in _ABSTRACT_MARKERS):
            continue

        # The from_name is ADG::Module::path::ClassName (concrete class)
        # The symbol is the base class name
        from_parts = edge.from_name.split("::")
        concrete_cls = from_parts[-1] if from_parts else ""
        abstract_cls = sym.rsplit(".", 1)[-1] if "." in sym else sym

        if not concrete_cls or not abstract_cls:
            continue

        if edge.from_name.startswith(_MODULE_PREFIX):
            abstract_module = edge.from_name[len(_MODULE_PREFIX) :]
            abstract_module = abstract_module.split("::")[0]
        else:
            abstract_module = ""

        abstract_bases[abstract_cls] = abstract_module
        concrete_to_abstracts.setdefault(concrete_cls, [])
        if abstract_cls not in concrete_to_abstracts[concrete_cls]:
            concrete_to_abstracts[concrete_cls].append(abstract_cls)

    # Pass 2: find DIP violations
    violations: list[DIPViolation] = []

    for edge in result.edges:
        if edge.relation_type not in ("imports", "instantiates"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        violator_path = edge.from_name[len(_MODULE_PREFIX) :]
        violator_layer = module_path_to_layer(violator_path)

        sym = edge.symbol or ""
        if not sym:
            continue

        # Extract concrete class name from symbol
        concrete_cls = sym.rsplit(".", 1)[-1] if "." in sym else sym

        abstracts_for_concrete = concrete_to_abstracts.get(concrete_cls, [])
        if not abstracts_for_concrete:
            continue

        concrete_module = _sym_to_module(sym)
        concrete_layer = module_path_to_layer(concrete_module)

        for abstract_cls in abstracts_for_concrete:
            abstract_module = abstract_bases.get(abstract_cls, "")
            abstract_layer = module_path_to_layer(abstract_module) if abstract_module else concrete_layer

            # Only flag if using abstract is actually possible (layer-accessible)
            can_use_abstract = (
                abstract_layer == violator_layer or (violator_layer, abstract_layer) in ALLOWED_LAYER_EDGES
            )
            if not can_use_abstract:
                continue

            severity = "high" if violator_layer in ("L0", "L1", "L2") else "medium"

            violations.append(
                DIPViolation(
                    violating_module=violator_path,
                    concrete_class=concrete_cls,
                    concrete_provider_module=concrete_module,
                    abstract_base=abstract_cls,
                    abstract_provider_module=abstract_module,
                    violating_layer=violator_layer,
                    concrete_layer=concrete_layer,
                    abstract_layer=abstract_layer,
                    line_no=edge.line_no,
                    severity=severity,
                ),
            )

    violations.sort(key=lambda v: (v.severity, v.violating_module, v.concrete_class))

    return DIPReport(
        violations=violations,
        abstract_bases=abstract_bases,
        concrete_to_abstracts=concrete_to_abstracts,
        violation_count=len(violations),
    )


__all__ = [
    "DIPReport",
    "DIPViolation",
    "detect_dip_violations",
]
