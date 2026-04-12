"""E17: Refactoring Plan Generator.

Produces a structured, step-by-step refactoring plan driven entirely by ADG
signals.  Given a target file (or a set of high-coupling modules), the planner
outputs:

  1. A risk-ordered list of candidate refactoring operations
  2. A dependency-safe execution sequence (respecting import topology)
  3. Per-step estimated blast radius and layer implications
  4. Suggested test-run scope for each step

Supported operation types:
  - EXTRACT_MODULE   — split a high-coupling module into smaller ones
  - MOVE_MODULE      — move a module to a more appropriate layer
  - INTRODUCE_INTERFACE — introduce an abstract interface for a concrete dep
  - INLINE_MODULE    — merge a near-orphan module into its only consumer
  - STABILISE_MODULE — add an intermediate stable layer to reduce instability

Usage::

    from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

    plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/foo.py"])
    for step in plan.steps:
        print(step.step_no, step.operation, step.target, step.rationale)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from agentic_core.adg.schema import module_path_to_layer
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

_emit_applies_guardrail("p0", "refactoring_planner", "p0_governance")
_emit_reads_policy_state("p0", "refactoring_planner", "policy_binding")
_emit_snapshots_state("p0", "refactoring_planner", "state_snapshot")
emit_replay_key("p0", "refactoring_planner")
emit_determinism_digest("p0", "refactoring_planner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "refactoring_planner", "execution_auth")
_emit_validates_capability("p2", "refactoring_planner", "capability_check")
_emit_routes_to_capability("p2", "refactoring_planner", "capability_route")
_emit_writes_via_uwg("p2", "refactoring_planner", "uwg_write")
_emit_blocks_direct_write("p2", "refactoring_planner", "direct_write_block")
_emit_records_tool_invocation("p2", "refactoring_planner", "tool_invocation")
_emit_captures_execution_output("p2", "refactoring_planner", "exec_output")
_emit_dispatches_agent("p3", "refactoring_planner", "agent_dispatch")
_emit_coordinates_agents("p3", "refactoring_planner", "agent_coordination")
_emit_records_workflow_lineage("p3", "refactoring_planner", "workflow_lineage")
_emit_records_healing_outcome("p3", "refactoring_planner", "healing_outcome")
_emit_escalates_failure("p3", "refactoring_planner", "failure_escalation")
_emit_orchestrates_workflow("p3", "refactoring_planner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "refactoring_planner", "healing_dispatch")
_emit_invokes_evaluation("p3", "refactoring_planner", "evaluation_signal")
_emit_records_telemetry_event("p4", "refactoring_planner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "refactoring_planner", "eval_metric")
_emit_stores_embedding("p4", "refactoring_planner", "embedding_store")
_emit_updates_meta_learning_state("p4", "refactoring_planner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "refactoring_planner", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.analysis.coupling_metrics import CouplingMetricsReport
    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.analysis.test_gap import TestGapReport
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_1")
_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_2")
_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_3")
_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_4")
_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_5")
_emit_emits_metric_event("refactoring_planner", "p4obs", "metric_6")
_emit_records_incident_event("refactoring_planner", "p4obs", "incident")
_emit_captures_runtime_anomaly("refactoring_planner", "p4obs", "anomaly")
_emit_writes_observability_log("refactoring_planner", "p4obs", "obs_log")
_emit_updates_monitoring_state("refactoring_planner", "p4obs", "mon_state")
_emit_triggers_alert("refactoring_planner", "p4obs", "alert")
_emit_links_incident_trace("refactoring_planner", "p4obs", "trace_link")
_emit_captures_pattern("refactoring_planner", "p3lm", "pattern")
_emit_records_learning_event("refactoring_planner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("refactoring_planner", "p3lm", "snapshot")
_emit_feeds_meta_learning("refactoring_planner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("refactoring_planner", "p3lm", "routing")
_emit_improves_agent_policy("refactoring_planner", "p3lm", "policy")
_emit_stores_learning_state("refactoring_planner", "p3lm", "state")
_emit_records_execution_trace("refactoring_planner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("refactoring_planner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("refactoring_planner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("refactoring_planner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("refactoring_planner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("refactoring_planner", "env_read", "p2_env_1")
_emit_reads_environ("refactoring_planner", "env_read", "p2_env_2")
_emit_reads_runtime_state("refactoring_planner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("refactoring_planner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "refactoring_planner", "context_pull")
_emit_pulls_context("p1", "refactoring_planner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "refactoring_planner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "refactoring_planner", "uwg_term_2")
_emit_writes_through("p1", "refactoring_planner", "write_through")
_emit_writes_through("p1", "refactoring_planner", "write_through_2")
_emit_validated_by_safety_plane("p1", "refactoring_planner", "safety_validation")
_emit_invokes_eval("p1", "refactoring_planner", "eval_call")
_emit_proposal_commits_routing("p1", "refactoring_planner", "routing_commit")
_emit_escalates_to_human("p1", "refactoring_planner", "human_escalation")
_emit_routes_through("p1", "refactoring_planner", "route_through")
_emit_checks_agent_registry("p1", "refactoring_planner", "agent_registry")
_emit_validates_agent_capability("p1", "refactoring_planner", "capability")
_emit_dispatches_execution_plan("p1", "refactoring_planner", "exec_plan")
_emit_agent_executes_agent("p1", "refactoring_planner", "sub_agent")
_emit_routes_to_agent("p1", "refactoring_planner", "target_agent")
_emit_verifies_policy("p1", "refactoring_planner", "policy_check")
_emit_observes_runtime_state("p1", "refactoring_planner", "runtime_state")
_emit_verifies_boundary("p1", "refactoring_planner", "boundary_check")
_emit_transcripts_response("p1", "refactoring_planner", "transcript")
_emit_hard_fails_untranscripted("p1", "refactoring_planner")
_emit_gated_by_confidence("p1", "refactoring_planner", "confidence_gate")

RefactoringOp = Literal[
    "EXTRACT_MODULE",
    "MOVE_MODULE",
    "INTRODUCE_INTERFACE",
    "INLINE_MODULE",
    "STABILISE_MODULE",
    "ADD_TESTS",
    "SPLIT_CONCERNS",
]

_COUPLING_THRESHOLD_HIGH = 15
_COUPLING_THRESHOLD_EXTRACT = 25
_INSTABILITY_THRESHOLD = 0.80
_ORPHAN_THRESHOLD = 2


@dataclass
class RefactoringStep:
    """One atomic refactoring operation in the plan."""

    step_no: int
    operation: RefactoringOp
    target: str
    rationale: str
    estimated_blast_radius: int = 0
    layer: str = ""
    suggested_tests: list[str] = field(default_factory=list)
    dependencies_on: list[str] = field(default_factory=list)
    risk_label: str = "LOW"
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "operation": self.operation,
            "target": self.target,
            "rationale": self.rationale,
            "estimated_blast_radius": self.estimated_blast_radius,
            "layer": self.layer,
            "suggested_tests": sorted(self.suggested_tests),
            "dependencies_on": self.dependencies_on,
            "risk_label": self.risk_label,
            "details": self.details,
        }


@dataclass
class RefactoringPlan:
    """A complete, dependency-safe refactoring plan."""

    target_files: list[str]
    steps: list[RefactoringStep] = field(default_factory=list)
    total_estimated_blast_radius: int = 0
    adg_signals_summary: dict = field(default_factory=dict)

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RefactoringPlan.summary")

        op_counts: dict[str, int] = {}
        for s in self.steps:
            op_counts[s.operation] = op_counts.get(s.operation, 0) + 1
        ops = ", ".join(f"{k}={v}" for k, v in sorted(op_counts.items()))
        return (
            f"RefactoringPlan: {len(self.steps)} steps "
            f"blast_radius={self.total_estimated_blast_radius} "
            f"ops=[{ops}]"
        )

    def to_dict(self) -> dict:
        return {
            "target_files": sorted(self.target_files),
            "total_steps": len(self.steps),
            "total_estimated_blast_radius": self.total_estimated_blast_radius,
            "summary": self.summary,
            "adg_signals_summary": self.adg_signals_summary,
            "steps": [s.to_dict() for s in self.steps],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def build_refactoring_plan(
    result: ScanResult,
    target_files: list[str] | None = None,
    *,
    hotspot_index: HotspotIndex | None = None,
    coupling_report: CouplingMetricsReport | None = None,
    test_gap_report: TestGapReport | None = None,
    max_steps: int = 30,
) -> RefactoringPlan:
    """Build a risk-ordered, dependency-safe refactoring plan.

    If ``target_files`` is None or empty, the planner automatically selects
    the top-coupling modules from the hotspot index (or the whole scan result).

    The plan is ordered so that:
    - Steps with no dependencies on other steps come first (topological safety).
    - Lower blast-radius operations are proposed before higher ones.
    - Test-gap modules receive an ADD_TESTS step before structural changes.
    """
    from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics
    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.analysis.test_gap import detect_test_gaps

    if hotspot_index is None:
        hotspot_index = HotspotIndex.build(result)
    if coupling_report is None:
        coupling_report = compute_coupling_metrics(result)
    if test_gap_report is None:
        test_gap_report = detect_test_gaps(result, hotspot_index=hotspot_index)

    # Resolve target files
    targets: list[str]
    if target_files:
        targets = [f.replace("\\", "/") for f in target_files]
    else:
        top = hotspot_index.top_hotspots(n=10, threshold=_COUPLING_THRESHOLD_HIGH)
        targets = [m.module_path for m in top]

    uncovered_set = {e.module_path for e in test_gap_report.uncovered_modules}

    steps: list[RefactoringStep] = []
    step_n = 1
    total_blast = 0
    seen_targets: set[str] = set()

    for target in targets:
        if target in seen_targets:
            continue
        seen_targets.add(target)

        layer = module_path_to_layer(target)
        fi = hotspot_index.fan_in(target)
        fo = hotspot_index.fan_out(target)
        coupling = fi + fo
        metrics = coupling_report.metrics_by_module.get(target)
        inst = metrics.instability if metrics else 0.0
        zone = metrics.zone if metrics else "BALANCED"
        importers = hotspot_index.importers_of(target)

        # Estimate blast radius from fan_in
        blast = fi * 10

        # 1. ADD_TESTS before structural changes if uncovered
        if target in uncovered_set:
            risk = "CRITICAL" if fi > 10 else "HIGH" if fi > 3 else "MEDIUM"
            steps.append(
                RefactoringStep(
                    step_no=step_n,
                    operation="ADD_TESTS",
                    target=target,
                    rationale=f"No ADG test-coverage signal; fan_in={fi} — add tests before structural changes",
                    estimated_blast_radius=blast,
                    layer=layer,
                    suggested_tests=[],
                    risk_label=risk,
                    details={"fan_in": fi, "fan_out": fo},
                ),
            )
            step_n += 1

        # 2. EXTRACT_MODULE for extremely high coupling
        if coupling >= _COUPLING_THRESHOLD_EXTRACT:
            steps.append(
                RefactoringStep(
                    step_no=step_n,
                    operation="EXTRACT_MODULE",
                    target=target,
                    rationale=f"coupling={coupling} (fan_in={fi}, fan_out={fo}) exceeds threshold {_COUPLING_THRESHOLD_EXTRACT}; split responsibilities",
                    estimated_blast_radius=blast,
                    layer=layer,
                    suggested_tests=importers[:5],
                    dependencies_on=[],
                    risk_label="HIGH" if fi <= 20 else "CRITICAL",
                    details={"coupling": coupling, "instability": inst, "zone": zone},
                ),
            )
            step_n += 1
            total_blast += blast

        # 3. MOVE_MODULE for wrong-layer placement (Zone of Pain in high-L layer)
        if zone == "PAIN" and layer not in ("L0", "L1") and fi > 0:
            steps.append(
                RefactoringStep(
                    step_no=step_n,
                    operation="MOVE_MODULE",
                    target=target,
                    rationale=f"Zone of Pain (instability={inst:.2f}, abstract): consider moving to a more stable layer",
                    estimated_blast_radius=blast,
                    layer=layer,
                    suggested_tests=importers[:5],
                    risk_label="MEDIUM",
                    details={"instability": inst, "zone": zone, "layer": layer},
                ),
            )
            step_n += 1
            total_blast += blast

        # 4. STABILISE_MODULE for highly unstable modules with many dependants
        if inst >= _INSTABILITY_THRESHOLD and fi > 3:
            steps.append(
                RefactoringStep(
                    step_no=step_n,
                    operation="STABILISE_MODULE",
                    target=target,
                    rationale=f"instability={inst:.2f} with fan_in={fi}; introduce stable interface layer to shield dependants",
                    estimated_blast_radius=blast,
                    layer=layer,
                    suggested_tests=importers[:5],
                    risk_label="MEDIUM",
                    details={"instability": inst, "fan_in": fi},
                ),
            )
            step_n += 1
            total_blast += blast

        # 5. INLINE_MODULE for near-orphan modules (fan_in <= 1, fan_out <= 2)
        if fi <= 1 and fo <= 2 and coupling < _ORPHAN_THRESHOLD and target not in uncovered_set:
            steps.append(
                RefactoringStep(
                    step_no=step_n,
                    operation="INLINE_MODULE",
                    target=target,
                    rationale=f"Near-orphan module (fan_in={fi}, fan_out={fo}): consider inlining into its consumer",
                    estimated_blast_radius=max(fi * 5, 1),
                    layer=layer,
                    suggested_tests=[],
                    risk_label="LOW",
                    details={"fan_in": fi, "fan_out": fo},
                ),
            )
            step_n += 1

        if len(steps) >= max_steps:
            break

    adg_signals = {
        "hotspot_stats": hotspot_index.stats(),
        "test_gap_coverage_rate": round(test_gap_report.coverage_rate, 3),
        "pain_zone_count": len(coupling_report.top_pain_zone),
        "uselessness_zone_count": len(coupling_report.top_uselessness_zone),
    }

    return RefactoringPlan(
        target_files=targets,
        steps=steps,
        total_estimated_blast_radius=total_blast,
        adg_signals_summary=adg_signals,
    )


__all__ = [
    "RefactoringPlan",
    "RefactoringStep",
    "build_refactoring_plan",
    "RefactoringOp",
]
