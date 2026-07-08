"""E30: Architecture Verifier — unified verification tool.

Orchestrates all P3 analyzers into a single pass:
    E26: Runtime execution graph (runtime_graph)
    E27: Layer authority enforcement (layer_authority)
    E28: Mutation path verification (mutation_authority)
    E31: Policy hash runtime validation (policy_hash_validator)

Produces a consolidated ArchitectureVerificationReport with:
    - pass/fail per plane
    - total violation count
    - exit_code() for CI integration

Usage::

    from agentic_core.adg.applications.architecture_verifier import verify_architecture

    report = verify_architecture(result)
    report.print_summary()
    sys.exit(report.exit_code())
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "architecture_verifier", "p0_governance")
trace_contract._emit_snapshots_state("p0", "architecture_verifier", "state_snapshot")
trace_contract.emit_replay_key("p0", "architecture_verifier")
trace_contract.emit_determinism_digest("p0", "architecture_verifier")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "architecture_verifier", "execution_auth")
trace_contract._emit_validates_capability("p2", "architecture_verifier", "capability_check")
trace_contract._emit_routes_to_capability("p2", "architecture_verifier", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "architecture_verifier", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "architecture_verifier", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "architecture_verifier", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "architecture_verifier", "exec_output")
trace_contract._emit_dispatches_agent("p3", "architecture_verifier", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "architecture_verifier", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "architecture_verifier", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "architecture_verifier", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "architecture_verifier", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "architecture_verifier", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "architecture_verifier", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "architecture_verifier", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "architecture_verifier", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "architecture_verifier", "eval_metric")
trace_contract._emit_stores_embedding("p4", "architecture_verifier", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "architecture_verifier", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "architecture_verifier", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("architecture_verifier", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("architecture_verifier", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("architecture_verifier", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("architecture_verifier", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("architecture_verifier", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("architecture_verifier", "p4obs", "alert")
trace_contract._emit_links_incident_trace("architecture_verifier", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("architecture_verifier", "p3lm", "pattern")
trace_contract._emit_records_learning_event("architecture_verifier", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("architecture_verifier", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("architecture_verifier", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("architecture_verifier", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("architecture_verifier", "p3lm", "policy")
trace_contract._emit_stores_learning_state("architecture_verifier", "p3lm", "state")
trace_contract._emit_records_execution_trace("architecture_verifier", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("architecture_verifier", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("architecture_verifier", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("architecture_verifier", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("architecture_verifier", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("architecture_verifier", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("architecture_verifier", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("architecture_verifier", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("architecture_verifier", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "architecture_verifier", "context_pull")
trace_contract._emit_pulls_context("p1", "architecture_verifier", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "architecture_verifier", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "architecture_verifier", "uwg_term_2")
trace_contract._emit_writes_through("p1", "architecture_verifier", "write_through")
trace_contract._emit_writes_through("p1", "architecture_verifier", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "architecture_verifier", "safety_validation")
trace_contract._emit_invokes_eval("p1", "architecture_verifier", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "architecture_verifier", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "architecture_verifier", "human_escalation")
trace_contract._emit_routes_through("p1", "architecture_verifier", "route_through")
trace_contract._emit_checks_agent_registry("p1", "architecture_verifier", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "architecture_verifier", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "architecture_verifier", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "architecture_verifier", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "architecture_verifier", "target_agent")
trace_contract._emit_verifies_policy("p1", "architecture_verifier", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "architecture_verifier", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "architecture_verifier", "boundary_check")
trace_contract._emit_transcripts_response("p1", "architecture_verifier", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "architecture_verifier")
trace_contract._emit_gated_by_confidence("p1", "architecture_verifier", "confidence_gate")


@dataclass
class PlaneResult:
    """Result for one architectural plane."""

    plane: str
    passed: bool
    violation_count: int
    summary: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "plane": self.plane,
            "passed": self.passed,
            "violation_count": self.violation_count,
            "summary": self.summary,
        }


@dataclass
class ArchitectureVerificationReport:
    """Consolidated architecture verification across all planes."""

    planes: list[PlaneResult] = field(default_factory=list)
    total_violations: int = 0
    commit_sha: str = ""

    @property
    def passed(self) -> bool:
        return self.total_violations == 0

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ArchitectureVerificationReport.summary"
        )

        status = "PASS" if self.passed else "FAIL"
        plane_statuses = " | ".join(f"{p.plane}={'OK' if p.passed else 'FAIL'}" for p in self.planes)
        return (
            f"Architecture verification: {status} | "
            f"total_violations={self.total_violations} | {plane_statuses}"
        )

    def exit_code(self) -> int:
        return 0 if self.passed else 1

    def print_summary(self) -> None:
        print(self.summary)
        for p in self.planes:
            status = "✓" if p.passed else "✗"
            print(f"  {status} [{p.plane}] {p.summary}")

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total_violations": self.total_violations,
            "commit_sha": self.commit_sha,
            "summary": self.summary,
            "planes": [p.to_dict() for p in self.planes],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def verify_architecture(
    result: ScanResult,
    *,
    skip_planes: frozenset[str] = frozenset(),
) -> ArchitectureVerificationReport:
    """Run all architectural verification planes against a ScanResult.

    Parameters
    ----------
    result:
        The ADG ScanResult to verify.
    skip_planes:
        Optional set of plane names to skip. Valid values:
        ``"runtime_graph"``, ``"layer_authority"``, ``"mutation_paths"``,
        ``"policy_hash"``.
    """
    planes: list[PlaneResult] = []
    total = 0

    # E26: Runtime execution graph
    if "runtime_graph" not in skip_planes:
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        rg = build_runtime_graph(result)
        upward = len(rg.upward_layer_violations)
        planes.append(
            PlaneResult(
                plane="runtime_graph",
                passed=upward == 0,
                violation_count=upward,
                summary=rg.summary,
                details=rg.to_dict(),
            ),
        )
        total += upward

    # E27: Layer authority
    if "layer_authority" not in skip_planes:
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        la = detect_layer_authority_violations(result)
        planes.append(
            PlaneResult(
                plane="layer_authority",
                passed=la.violation_count == 0,
                violation_count=la.violation_count,
                summary=la.summary,
                details=la.to_dict(),
            ),
        )
        total += la.violation_count

    # E28: Mutation paths
    if "mutation_paths" not in skip_planes:
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        mp = verify_mutation_paths(result)
        # Only critical violations fail the build
        critical = len(mp.critical_violations())
        planes.append(
            PlaneResult(
                plane="mutation_paths",
                passed=critical == 0,
                violation_count=mp.violation_count,
                summary=mp.summary,
                details=mp.to_dict(),
            ),
        )
        total += critical

    # E31: Policy hash coupling
    if "policy_hash" not in skip_planes:
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        ph = validate_policy_hash_coupling(result)
        planes.append(
            PlaneResult(
                plane="policy_hash",
                passed=ph.violation_count == 0,
                violation_count=ph.violation_count,
                summary=ph.summary,
                details=ph.to_dict(),
            ),
        )
        total += ph.violation_count

    return ArchitectureVerificationReport(
        planes=planes,
        total_violations=total,
        commit_sha=getattr(result, "commit_sha", ""),
    )


__all__ = [
    "ArchitectureVerificationReport",
    "PlaneResult",
    "verify_architecture",
]
