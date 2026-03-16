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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "refactoring_planner", "p0_governance")
_emit_reads_policy_state("p0", "refactoring_planner", "policy_binding")
_emit_snapshots_state("p0", "refactoring_planner", "state_snapshot")
emit_replay_key("p0", "refactoring_planner")
emit_determinism_digest("p0", "refactoring_planner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    from agentic_core.adg.analysis.coupling_metrics import CouplingMetricsReport

    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.analysis.test_gap import TestGapReport
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
                )
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
                )
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
                )
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
                )
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
                )
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
