"""Enhancement 10: Repair recommendation / routing layer.

Maps ADG violations and graph anomalies to the correct repair agent,
healing flow, CI lane, or human reviewer.

Routing table:
  violates (layer boundary)   -> ArchitectureGovernorAgent  / CI: layer_guard
  missing coverage (no covers)-> TestRepairAgent             / CI: test_coverage
  governance drift             -> HealingOrchestrator        / CI: governance
  call to undeclared dep       -> DependencyRepairAgent      / CI: dep_check
  dynamic exec                 -> DynamicExecReviewAgent     / CI: dynamic_exec
  graph drift (new violations) -> DriftGovernorAgent         / CI: drift_check
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from agentic_core.adg.analysis.GraphDiff import GraphDiff
    from agentic_core.adg.extraction.static_scanner import Edge
from tqdm import tqdm

RepairAgent = Literal[
    "ArchitectureGovernorAgent",
    "TestRepairAgent",
    "HealingOrchestrator",
    "DependencyRepairAgent",
    "DynamicExecReviewAgent",
    "DriftGovernorAgent",
    "ManualReview",
]

CILane = Literal[
    "layer_guard",
    "test_coverage",
    "governance",
    "dep_check",
    "dynamic_exec",
    "drift_check",
    "none",
]

Severity = Literal["critical", "high", "medium", "low"]


@dataclass
class RepairRoute:
    """A single repair recommendation for a detected violation or anomaly."""

    violation_type: str
    description: str
    recommended_agent: RepairAgent
    ci_lane: CILane
    severity: Severity
    source_file: str = ""
    from_name: str = ""
    to_name: str = ""
    symbol: str = ""
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "violation_type": self.violation_type,
            "description": self.description,
            "recommended_agent": self.recommended_agent,
            "ci_lane": self.ci_lane,
            "severity": self.severity,
            "source_file": self.source_file,
            "from_name": self.from_name,
            "to_name": self.to_name,
            "symbol": self.symbol,
            "evidence": self.evidence,
        }


_RELATION_TO_ROUTE: dict[str, tuple[RepairAgent, CILane, Severity, str]] = {
    "violates": (
        "ArchitectureGovernorAgent",
        "layer_guard",
        "critical",
        "Layer boundary violation: upward import across forbidden layer boundary",
    ),
    "dynamic_exec": (
        "DynamicExecReviewAgent",
        "dynamic_exec",
        "high",
        "Dynamic execution detected (eval/exec/importlib): requires manual audit",
    ),
    "invokes_provider": (
        "DependencyRepairAgent",
        "dep_check",
        "medium",
        "Direct provider SDK invocation bypasses gateway abstraction",
    ),
    "writes_through": (
        "HealingOrchestrator",
        "governance",
        "medium",
        "Mutation routed through Universal Write Gateway: verify governance contract",
    ),
    "routes_through": (
        "HealingOrchestrator",
        "governance",
        "medium",
        "Execution routed through healing/governance plane: verify replay safety",
    ),
    "in_cycle": (
        "ArchitectureGovernorAgent",
        "layer_guard",
        "high",
        "Circular import detected: module participates in a strongly connected component",
    ),
    "dead_imports": (
        "DependencyRepairAgent",
        "dep_check",
        "low",
        "Dead import: name is imported but never referenced in the file body",
    ),
    "broad_exception_catch": (
        "ManualReview",
        "governance",
        "high",
        "Broad exception catch: hides bugs and error propagation failures",
    ),
    "silent_exception_swallow": (
        "ManualReview",
        "governance",
        "high",
        "Silent exception swallow: suppresses failures without signalling callers",
    ),
    "log_and_swallow": (
        "ManualReview",
        "governance",
        "high",
        "Log-and-swallow: logs but does not re-raise; callers see false success",
    ),
    "return_none_swallow": (
        "ManualReview",
        "governance",
        "high",
        "Return-None-swallow: caller cannot distinguish error from valid None result",
    ),
}


def route_violations(edges: list[Edge]) -> list[RepairRoute]:
    """Generate RepairRoute recommendations for a list of violation/anomaly edges.

    Processes all edges and returns routes for those that require attention,
    sorted by severity then source_file for deterministic output.
    """
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    routes: list[RepairRoute] = []

    for edge in tqdm(edges, desc="Processing", unit="item"):
        entry = _RELATION_TO_ROUTE.get(edge.relation_type)
        if entry is None:
            entry = _RELATION_TO_ROUTE.get(edge.edge_kind)
        if entry is None:
            continue

        agent, lane, severity, desc = entry
        routes.append(
            RepairRoute(
                violation_type=edge.relation_type,
                description=desc,
                recommended_agent=agent,
                ci_lane=lane,
                severity=severity,
                source_file=edge.source_file,
                from_name=edge.from_name,
                to_name=edge.to_name,
                symbol=edge.symbol,
                evidence={
                    "line_no": edge.line_no,
                    "edge_kind": edge.edge_kind,
                },
            ),
        )

    return sorted(routes, key=lambda r: (severity_order[r.severity], r.source_file, r.from_name))


def route_diff_violations(diff: GraphDiff) -> list[RepairRoute]:
    """Generate RepairRoute recommendations from a GraphDiff.

    Focuses on newly introduced violations and governance regressions.
    """

    routes: list[RepairRoute] = []

    for from_name, relation, to_name in tqdm(diff.new_violations, desc="Processing", unit="item"):
        routes.append(
            RepairRoute(
                violation_type="violates",
                description=f"NEW layer boundary violation introduced in this change: {from_name} -> {to_name}",
                recommended_agent="ArchitectureGovernorAgent",
                ci_lane="layer_guard",
                severity="critical",
                from_name=from_name,
                to_name=to_name,
                evidence={"commit_after": diff.commit_after, "drift": True},
            ),
        )

    if diff.risk_delta > 0:
        routes.append(
            RepairRoute(
                violation_type="graph_drift",
                description=f"ADG risk_delta=+{diff.risk_delta}: architecture regressed, {len(diff.new_violations)} new violation(s)",
                recommended_agent="DriftGovernorAgent",
                ci_lane="drift_check",
                severity="high",
                evidence={
                    "risk_delta": diff.risk_delta,
                    "new_violations": len(diff.new_violations),
                    "commit_before": diff.commit_before,
                    "commit_after": diff.commit_after,
                },
            ),
        )

    if not diff.new_coverage and diff.new_calls:
        routes.append(
            RepairRoute(
                violation_type="missing_test_coverage",
                description=f"{len(diff.new_calls)} new call edges added but no new test coverage edges detected",
                recommended_agent="TestRepairAgent",
                ci_lane="test_coverage",
                severity="medium",
                evidence={
                    "new_calls": len(diff.new_calls),
                    "new_coverage": len(diff.new_coverage),
                },
            ),
        )

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(routes, key=lambda r: (severity_order[r.severity], r.from_name))


def repair_routing_summary(routes: list[RepairRoute]) -> dict:
    """Summarise repair routes by agent and CI lane."""
    by_agent: dict[str, int] = {}
    by_lane: dict[str, int] = {}
    by_severity: dict[str, int] = {}

    for r in routes:
        by_agent[r.recommended_agent] = by_agent.get(r.recommended_agent, 0) + 1
        by_lane[r.ci_lane] = by_lane.get(r.ci_lane, 0) + 1
        by_severity[r.severity] = by_severity.get(r.severity, 0) + 1

    return {
        "total_routes": len(routes),
        "by_agent": dict(sorted(by_agent.items())),
        "by_ci_lane": dict(sorted(by_lane.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "routes": [r.to_dict() for r in routes],
    }
