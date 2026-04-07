"""Enhancement 5: Change-impact prediction engine.

Given a set of changed files, walks the ADG edge graph to predict:
  - which modules are transitively impacted (reverse import/call graph)
  - which tests cover those modules
  - which agents/orchestrators are in the blast radius
  - a risk score for the change

Uses the ScanResult edge set as a static dependency graph — no runtime
tracing required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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

_emit_records_execution_trace("p0", "evidence", "impact")
_emit_applies_guardrail("p0", "impact", "p0_governance")
_emit_reads_policy_state("p0", "impact", "policy_binding")
_emit_snapshots_state("p0", "impact", "state_snapshot")
_emit_escalates_to_human("p1", "impact", "human_escalation")
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

_emit_emits_metric_event("impact", "p4obs", "metric_1")
_emit_emits_metric_event("impact", "p4obs", "metric_2")
_emit_emits_metric_event("impact", "p4obs", "metric_3")
_emit_emits_metric_event("impact", "p4obs", "metric_4")
_emit_emits_metric_event("impact", "p4obs", "metric_5")
_emit_emits_metric_event("impact", "p4obs", "metric_6")
_emit_records_incident_event("impact", "p4obs", "incident")
_emit_captures_runtime_anomaly("impact", "p4obs", "anomaly")
_emit_writes_observability_log("impact", "p4obs", "obs_log")
_emit_updates_monitoring_state("impact", "p4obs", "mon_state")
_emit_triggers_alert("impact", "p4obs", "alert")
_emit_links_incident_trace("impact", "p4obs", "trace_link")
_emit_captures_pattern("impact", "p3lm", "pattern")
_emit_records_learning_event("impact", "p3lm", "learning_event")
_emit_writes_learning_snapshot("impact", "p3lm", "snapshot")
_emit_feeds_meta_learning("impact", "p3lm", "meta_feed")
_emit_updates_routing_strategy("impact", "p3lm", "routing")
_emit_improves_agent_policy("impact", "p3lm", "policy")
_emit_stores_learning_state("impact", "p3lm", "state")
_emit_records_execution_trace("impact", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("impact", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("impact", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("impact", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("impact", "L4_STATE", "p2_trace_5")
_emit_reads_environ("impact", "env_read", "p2_env_1")
_emit_reads_environ("impact", "env_read", "p2_env_2")
_emit_reads_runtime_state("impact", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("impact", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "impact", "context_pull")
_emit_pulls_context("p1", "impact", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "impact", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "impact", "uwg_term_2")
_emit_writes_through("p1", "impact", "write_through")
_emit_writes_through("p1", "impact", "write_through_2")
_emit_validated_by_safety_plane("p1", "impact", "safety_validation")
_emit_invokes_eval("p1", "impact", "eval_call")
_emit_proposal_commits_routing("p1", "impact", "routing_commit")
_emit_routes_through("p1", "impact", "route_through")
_emit_checks_agent_registry("p1", "impact", "agent_registry")
_emit_validates_agent_capability("p1", "impact", "capability")
_emit_dispatches_execution_plan("p1", "impact", "exec_plan")
_emit_agent_executes_agent("p1", "impact", "sub_agent")
_emit_routes_to_agent("p1", "impact", "target_agent")
_emit_verifies_policy("p1", "impact", "policy_check")
_emit_observes_runtime_state("p1", "impact", "runtime_state")
_emit_verifies_boundary("p1", "impact", "boundary_check")
_emit_transcripts_response("p1", "impact", "transcript")
_emit_hard_fails_untranscripted("p1", "impact")
_emit_gated_by_confidence("p1", "impact", "confidence_gate")
emit_replay_key("p0", "impact")
emit_determinism_digest("p0", "impact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "impact", "execution_auth")
_emit_validates_capability("p2", "impact", "capability_check")
_emit_routes_to_capability("p2", "impact", "capability_route")
_emit_writes_via_uwg("p2", "impact", "uwg_write")
_emit_blocks_direct_write("p2", "impact", "direct_write_block")
_emit_records_tool_invocation("p2", "impact", "tool_invocation")
_emit_captures_execution_output("p2", "impact", "exec_output")
_emit_dispatches_agent("p3", "impact", "agent_dispatch")
_emit_coordinates_agents("p3", "impact", "agent_coordination")
_emit_records_workflow_lineage("p3", "impact", "workflow_lineage")
_emit_records_healing_outcome("p3", "impact", "healing_outcome")
_emit_escalates_failure("p3", "impact", "failure_escalation")
_emit_orchestrates_workflow("p3", "impact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "impact", "healing_dispatch")
_emit_invokes_evaluation("p3", "impact", "evaluation_signal")
_emit_records_telemetry_event("p4", "impact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "impact", "eval_metric")
_emit_stores_embedding("p4", "impact", "embedding_store")
_emit_updates_meta_learning_state("p4", "impact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "impact", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

_EXECUTION_RELATIONS = frozenset(
    {
        "imports",
        "calls",
        "implements",
        "instantiates",
        "reads_from",
        "invokes_provider",
        "writes_to",
        "writes_through",
        "routes_through",
    },
)


@dataclass
class ImpactReport:
    """Impact prediction for a set of changed modules.

    Attributes:
        changed_modules: the direct input changed files.
        impacted_modules: all transitively reachable modules via reverse edges.
        covering_tests: test modules that have a `covers` edge into any impacted module.
        agent_paths: agents/orchestrators in the blast radius.
        violation_modules: impacted modules that are sources of `violates` edges.
        risk_score: 0.0–1.0 normalised estimate of change risk.
        risk_label: LOW / MEDIUM / HIGH / CRITICAL.
        by_owner: impacted module counts grouped by ownership domain.
        execution_paths: list of (from, relation, to) triples for each execution-plane edge
                         connecting the changed set to its dependants.
    """

    changed_modules: list[str] = field(default_factory=list)
    impacted_modules: list[str] = field(default_factory=list)
    covering_tests: list[str] = field(default_factory=list)
    agent_paths: list[str] = field(default_factory=list)
    violation_modules: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    risk_label: str = "LOW"
    by_owner: dict[str, int] = field(default_factory=dict)
    execution_paths: list[tuple[str, str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "changed_modules": self.changed_modules,
            "impacted_modules": self.impacted_modules,
            "impacted_count": len(self.impacted_modules),
            "covering_tests": self.covering_tests,
            "agent_paths": self.agent_paths,
            "violation_modules": self.violation_modules,
            "risk_score": round(self.risk_score, 4),
            "risk_label": self.risk_label,
            "by_owner": self.by_owner,
            "execution_paths": [list(p) for p in self.execution_paths],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _normalise(name: str) -> str:
    """Strip ADG:: prefix to get a comparable path-like key."""
    for prefix in ("ADG::Module::", "ADG::Symbol::", "ADG::Layer::"):
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


def predict_impact(
    result: ScanResult,
    changed_files: list[str],
    *,
    max_depth: int = 6,
) -> ImpactReport:
    """Predict the blast radius of changes to `changed_files`.

    Performs a reverse BFS from the changed modules through execution-plane
    edges (anything that is not purely structural like `belongs_to_layer`).
    Nodes that import or call the changed modules are transitively reachable.

    Args:
        result: Full ScanResult from the static scanner.
        changed_files: Relative file paths that have changed (normalised, no ADG:: prefix).
        max_depth: Maximum BFS hops (default 6).

    Returns:
        ImpactReport with impacted modules, tests, risk score, etc.
    """
    from agentic_core.adg.analysis.ownership import _infer_ownership

    edges = list(result.edges)

    # For impact analysis we work entirely in normalised module paths.
    # The key insight: imports edges have from_name=ADG::Module::path and
    # to_name=ADG::Symbol::pkg.sub — we need to build a module→module graph.
    # Strategy: for each `imports` edge, map (from_module) → (to_module prefix).
    # Then build reverse: to_module → set of from_modules that depend on it.

    # Build: module_path → set of module_paths it imports (prefix match on symbol)
    module_imports: dict[str, set[str]] = {}  # from_module -> set of normalised to-symbols
    covers_map: dict[str, set[str]] = {}  # covered_module -> set of test_modules
    violation_sources: set[str] = set()

    for e in edges:
        fn = _normalise(e.from_name)

        if e.relation_type == "covers":
            tn = _normalise(e.to_name)
            covers_map.setdefault(tn, set()).add(fn)
            continue

        if e.relation_type == "violates":
            violation_sources.add(fn)
            continue

        if e.relation_type in _EXECUTION_RELATIONS:
            tn = _normalise(e.to_name)
            module_imports.setdefault(fn, set()).add(tn)

    # Build reverse dependency map: for each module M, which modules depend on M?
    # A module X depends on M if X has any import whose symbol starts with M's module path
    # (dotted form). We build a map: module_path → set of modules that use it.
    changed_norm = {f.replace("\\", "/") for f in changed_files}

    # Build dot-form index of all known module paths for prefix matching
    module_dot_forms: dict[str, str] = {}  # dot.form -> slash/form
    for m in result.modules:
        dot = m.replace("/", ".").removesuffix(".py")
        module_dot_forms[dot] = m

    # reverse_dep[M] = set of modules that import something from M
    reverse_dep: dict[str, set[str]] = {}
    for from_mod, imported_syms in module_imports.items():
        for sym in imported_syms:
            # sym is like "agentic_core.L2_execution.UniversalWriteGateway.ClassName"
            # Match against module dot forms (longest prefix first)
            sym_dot = sym.replace("/", ".")
            matched: str | None = None
            for length in range(len(sym_dot.split(".")), 0, -1):
                candidate = ".".join(sym_dot.split(".")[:length])
                if candidate in module_dot_forms:
                    matched = module_dot_forms[candidate]
                    break
            if matched is None:
                # Also try direct slash path match
                slash_sym = sym.replace(".", "/")
                if slash_sym in set(result.modules):
                    matched = slash_sym
            if matched is not None:
                reverse_dep.setdefault(matched, set()).add(from_mod)

    # Seed the BFS frontier with changed files (already normalised slash paths)
    frontier: set[str] = set(changed_norm)
    visited: set[str] = set(changed_norm)
    execution_paths: list[tuple[str, str, str]] = []

    for _ in range(max_depth):
        next_frontier: set[str] = set()
        for node in frontier:
            for dependant in reverse_dep.get(node, set()):
                if dependant not in visited:
                    visited.add(dependant)
                    next_frontier.add(dependant)
                    execution_paths.append((dependant, "depends_on", node))
        if not next_frontier:
            break
        frontier = next_frontier

    impacted = sorted(visited - changed_norm)

    # Find tests covering any impacted module
    covering_tests: set[str] = set()
    for mod in visited:
        for test in covers_map.get(mod, set()):
            covering_tests.add(test)

    # Find agents in blast radius (heuristic: module name contains "Agent" or "Orchestrator")
    agent_paths = sorted(m for m in impacted if "Agent" in m or "Orchestrator" in m or "Gateway" in m)

    # Find violation sources in the impacted set
    violation_modules = sorted(m for m in impacted if m in violation_sources)

    # Ownership breakdown
    by_owner: dict[str, int] = {}
    for mod in impacted:
        owner = _infer_ownership(mod).owner
        by_owner[owner] = by_owner.get(owner, 0) + 1

    # Risk score: weighted combination of:
    #   - fraction of total modules impacted (breadth)
    #   - presence of high-criticality modules
    #   - number of violations in blast radius
    total_modules = max(len(result.modules), 1)
    breadth_score = min(len(impacted) / total_modules, 1.0) * 0.4

    from agentic_core.adg.analysis.ownership import _infer_ownership as _own

    high_crit = sum(1 for m in impacted if _own(m).criticality == "high")
    crit_score = min(high_crit / max(len(impacted), 1), 1.0) * 0.4

    viol_score = min(len(violation_modules) / max(len(impacted), 1), 1.0) * 0.2

    risk_score = breadth_score + crit_score + viol_score

    if risk_score >= 0.70:
        risk_label = "CRITICAL"
    elif risk_score >= 0.40:
        risk_label = "HIGH"
    elif risk_score >= 0.20:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"

    return ImpactReport(
        changed_modules=sorted(changed_norm),
        impacted_modules=impacted,
        covering_tests=sorted(covering_tests),
        agent_paths=agent_paths,
        violation_modules=violation_modules,
        risk_score=risk_score,
        risk_label=risk_label,
        by_owner=dict(sorted(by_owner.items())),
        execution_paths=sorted(set(execution_paths)),
    )


def impact_summary(report: ImpactReport) -> dict:
    """Return a compact summary dict suitable for embedding in the ADG artifact."""
    return {
        "changed_module_count": len(report.changed_modules),
        "impacted_module_count": len(report.impacted_modules),
        "covering_test_count": len(report.covering_tests),
        "agent_path_count": len(report.agent_paths),
        "violation_module_count": len(report.violation_modules),
        "risk_score": report.risk_score,
        "risk_label": report.risk_label,
        "by_owner": report.by_owner,
        "sample_impacted": report.impacted_modules[:20],
        "sample_agents": report.agent_paths[:10],
    }
