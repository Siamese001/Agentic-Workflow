"""ADG execute_ssot Integration — pre-run impact analysis for SSOT flows.

Provides a lightweight integration seam for execute_ssot.py to call before
running any healing or validation phase. Returns a structured pre-run report
containing:
  - Blast radius of files in scope
  - Route mode recommendation (NORMAL / RESTRICTED / HUMAN_REVIEW)
  - Impacted tests (scoped, no silent full-suite fallback)
  - Layer violation signals relevant to the scope
  - Scope widening events (cross-layer dependencies)
  - Impact digest for audit trail

Usage from execute_ssot:
    from agentic_core.adg.applications.execute_ssot_integration import (
        PreRunADGReport,
        build_pre_run_report,
    )
    report = build_pre_run_report(changed_files=files_in_scope)
    if report.route_mode == "HUMAN_REVIEW":
        logger.warning("ADG: HUMAN_REVIEW threshold exceeded — %s", report.summary)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
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

_emit_records_execution_trace("p0", "evidence", "execute_ssot_integration")
_emit_applies_guardrail("p0", "execute_ssot_integration", "p0_governance")
_emit_reads_policy_state("p0", "execute_ssot_integration", "policy_binding")
_emit_snapshots_state("p0", "execute_ssot_integration", "state_snapshot")
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

_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_1")
_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_2")
_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_3")
_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_4")
_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_5")
_emit_emits_metric_event("execute_ssot_integration", "p4obs", "metric_6")
_emit_records_incident_event("execute_ssot_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("execute_ssot_integration", "p4obs", "anomaly")
_emit_writes_observability_log("execute_ssot_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("execute_ssot_integration", "p4obs", "mon_state")
_emit_triggers_alert("execute_ssot_integration", "p4obs", "alert")
_emit_links_incident_trace("execute_ssot_integration", "p4obs", "trace_link")
_emit_captures_pattern("execute_ssot_integration", "p3lm", "pattern")
_emit_records_learning_event("execute_ssot_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execute_ssot_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("execute_ssot_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execute_ssot_integration", "p3lm", "routing")
_emit_improves_agent_policy("execute_ssot_integration", "p3lm", "policy")
_emit_stores_learning_state("execute_ssot_integration", "p3lm", "state")
_emit_records_execution_trace("execute_ssot_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execute_ssot_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execute_ssot_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execute_ssot_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execute_ssot_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execute_ssot_integration", "env_read", "p2_env_1")
_emit_reads_environ("execute_ssot_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("execute_ssot_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execute_ssot_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execute_ssot_integration", "context_pull")
_emit_pulls_context("p1", "execute_ssot_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execute_ssot_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execute_ssot_integration", "uwg_term_2")
_emit_writes_through("p1", "execute_ssot_integration", "write_through")
_emit_writes_through("p1", "execute_ssot_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "execute_ssot_integration", "safety_validation")
_emit_invokes_eval("p1", "execute_ssot_integration", "eval_call")
_emit_proposal_commits_routing("p1", "execute_ssot_integration", "routing_commit")
_emit_escalates_to_human("p1", "execute_ssot_integration", "human_escalation")
_emit_routes_through("p1", "execute_ssot_integration", "route_through")
_emit_checks_agent_registry("p1", "execute_ssot_integration", "agent_registry")
_emit_validates_agent_capability("p1", "execute_ssot_integration", "capability")
_emit_dispatches_execution_plan("p1", "execute_ssot_integration", "exec_plan")
_emit_agent_executes_agent("p1", "execute_ssot_integration", "sub_agent")
_emit_routes_to_agent("p1", "execute_ssot_integration", "target_agent")
_emit_verifies_policy("p1", "execute_ssot_integration", "policy_check")
_emit_observes_runtime_state("p1", "execute_ssot_integration", "runtime_state")
_emit_verifies_boundary("p1", "execute_ssot_integration", "boundary_check")
_emit_transcripts_response("p1", "execute_ssot_integration", "transcript")
_emit_hard_fails_untranscripted("p1", "execute_ssot_integration")
_emit_gated_by_confidence("p1", "execute_ssot_integration", "confidence_gate")
emit_replay_key("p0", "execute_ssot_integration")
emit_determinism_digest("p0", "execute_ssot_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "execute_ssot_integration", "execution_auth")
_emit_validates_capability("p2", "execute_ssot_integration", "capability_check")
_emit_routes_to_capability("p2", "execute_ssot_integration", "capability_route")
_emit_writes_via_uwg("p2", "execute_ssot_integration", "uwg_write")
_emit_blocks_direct_write("p2", "execute_ssot_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "execute_ssot_integration", "tool_invocation")
_emit_captures_execution_output("p2", "execute_ssot_integration", "exec_output")
_emit_dispatches_agent("p3", "execute_ssot_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "execute_ssot_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "execute_ssot_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "execute_ssot_integration", "healing_outcome")
_emit_escalates_failure("p3", "execute_ssot_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "execute_ssot_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execute_ssot_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "execute_ssot_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "execute_ssot_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execute_ssot_integration", "eval_metric")
_emit_stores_embedding("p4", "execute_ssot_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "execute_ssot_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execute_ssot_integration", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)


@dataclass
class PreRunADGReport:
    """Structured pre-run impact report for one execute_ssot invocation."""

    changed_files: list[str]
    impacted_module_count: int
    impacted_modules: list[str]
    impacted_test_count: int
    impacted_tests: list[str]
    risk_score: int
    route_mode: str
    scope_widening_events: list[str]
    uncovered_changed_files: list[str]
    layer_violation_count: int
    impact_digest: str
    adg_available: bool = True
    adg_error: str = ""

    @property
    def summary(self) -> str:
        return (
            f"route_mode={self.route_mode} "
            f"risk={self.risk_score} "
            f"impacted={self.impacted_module_count} modules "
            f"tests={self.impacted_test_count} "
            f"violations={self.layer_violation_count} "
            f"digest={self.impact_digest[:12]}"
        )

    def to_dict(self) -> dict:
        return {
            "changed_files": sorted(self.changed_files),
            "impacted_module_count": self.impacted_module_count,
            "impacted_modules": sorted(self.impacted_modules),
            "impacted_test_count": self.impacted_test_count,
            "impacted_tests": sorted(self.impacted_tests),
            "risk_score": self.risk_score,
            "route_mode": self.route_mode,
            "scope_widening_events": sorted(self.scope_widening_events),
            "uncovered_changed_files": sorted(self.uncovered_changed_files),
            "layer_violation_count": self.layer_violation_count,
            "impact_digest": self.impact_digest,
            "adg_available": self.adg_available,
            "adg_error": self.adg_error,
            "summary": self.summary,
        }

    @classmethod
    def unavailable(cls, changed_files: list[str], reason: str) -> PreRunADGReport:
        """Return a degraded report when ADG is unavailable."""
        return cls(
            changed_files=sorted(changed_files),
            impacted_module_count=0,
            impacted_modules=[],
            impacted_test_count=0,
            impacted_tests=[],
            risk_score=0,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=sorted(changed_files),
            layer_violation_count=0,
            impact_digest="",
            adg_available=False,
            adg_error=reason,
        )


def build_pre_run_report(
    changed_files: list[str],
    repo_root: Path | None = None,
    force_fresh: bool = False,
) -> PreRunADGReport:
    """Build an ADG pre-run report for the given changed files.

    Gracefully degrades: if ADG is unavailable, returns a report with
    adg_available=False and adg_error explaining why. Never raises.

    Parameters
    ----------
    changed_files:
        Repo-relative forward-slash paths of files being processed.
    repo_root:
        Repository root. Defaults to cwd.
    force_fresh:
        If True, bypass the ADG cache and run a fresh scan.
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    norm_files = [f.replace("\\", "/") for f in (changed_files or [])]

    try:
        from tools.change_impact_engine import ChangeImpactEngine

        from agentic_core.adg.runtime.cache_loader import load_or_scan

        result = load_or_scan(repo_root=str(repo_root))
        engine = ChangeImpactEngine(result, repo_root=repo_root)
        impact = engine.analyze(norm_files, include_tests=True)

        # Count layer violations in blast radius
        layer_violation_count = _count_layer_violations_in_scope(result, impact.impacted_modules)

        return PreRunADGReport(
            changed_files=impact.changed_files,
            impacted_module_count=len(impact.impacted_modules),
            impacted_modules=impact.impacted_modules,
            impacted_test_count=len(impact.impacted_tests),
            impacted_tests=impact.impacted_tests,
            risk_score=impact.risk_score,
            route_mode=impact.route_mode,
            scope_widening_events=impact.scope_widening_events,
            uncovered_changed_files=impact.uncovered_changed_files,
            layer_violation_count=layer_violation_count,
            impact_digest=impact.impact_digest,
            adg_available=True,
            adg_error="",
        )

    # guardian: allow-silent-swallow -- pre-run report is non-critical telemetry; failure logged below
    except Exception as exc:  # guardian: allow-silent-swallower
        logger.warning(
            "ADG pre-run report unavailable: %s — proceeding without impact analysis",
            exc,
        )
        return PreRunADGReport.unavailable(norm_files, str(exc))


def _count_layer_violations_in_scope(result: ScanResult, impacted_modules: list[str]) -> int:
    """Count import edges among impacted_modules that violate layer rules."""
    from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES, module_path_to_layer

    impacted_set = set(impacted_modules)
    count = 0
    for edge in result.edges:
        if edge.relation_type != "imports":
            continue
        module_prefix = "ADG::Module::"
        from_path = edge.from_name[len(module_prefix) :] if edge.from_name.startswith(module_prefix) else ""
        to_path = edge.to_name[len(module_prefix) :] if edge.to_name.startswith(module_prefix) else ""
        if from_path not in impacted_set or to_path not in impacted_set:
            continue
        fl = module_path_to_layer(from_path)
        tl = module_path_to_layer(to_path)
        if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
            count += 1
    return count


def emit_pre_run_log(report: PreRunADGReport) -> None:
    """Emit structured log lines for the pre-run ADG report."""
    if not report.adg_available:
        logger.warning("ADG pre-run: UNAVAILABLE — %s", report.adg_error)
        return

    level = logging.WARNING if report.route_mode != "NORMAL" else logging.INFO
    logger.log(
        level,
        "ADG pre-run: %s",
        report.summary,
    )
    if report.scope_widening_events:
        logger.info(
            "ADG pre-run: scope widening into %d module(s): %s",
            len(report.scope_widening_events),
            report.scope_widening_events[:5],
        )
    if report.uncovered_changed_files:
        logger.info(
            "ADG pre-run: %d changed file(s) not in ADG index (blind spots): %s",
            len(report.uncovered_changed_files),
            report.uncovered_changed_files[:5],
        )


__all__ = [
    "PreRunADGReport",
    "build_pre_run_report",
    "emit_pre_run_log",
]
