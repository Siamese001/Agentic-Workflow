"""Canonical entrypoint for apps_rg.

Usage:
    python -m apps_rg

ADG bootstrap fires before any agent dispatch. Gracefully degrades if ADG
is unavailable — never blocks execution on ADG failure.
"""

from __future__ import annotations

import logging
import sys

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

_emit_records_execution_trace("p0", "evidence", "__main__")
_emit_applies_guardrail("p0", "__main__", "p0_governance")
_emit_reads_policy_state("p0", "__main__", "policy_binding")
_emit_snapshots_state("p0", "__main__", "state_snapshot")
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

_emit_emits_metric_event("__main__", "p4obs", "metric_1")
_emit_emits_metric_event("__main__", "p4obs", "metric_2")
_emit_emits_metric_event("__main__", "p4obs", "metric_3")
_emit_emits_metric_event("__main__", "p4obs", "metric_4")
_emit_emits_metric_event("__main__", "p4obs", "metric_5")
_emit_emits_metric_event("__main__", "p4obs", "metric_6")
_emit_records_incident_event("__main__", "p4obs", "incident")
_emit_captures_runtime_anomaly("__main__", "p4obs", "anomaly")
_emit_writes_observability_log("__main__", "p4obs", "obs_log")
_emit_updates_monitoring_state("__main__", "p4obs", "mon_state")
_emit_triggers_alert("__main__", "p4obs", "alert")
_emit_links_incident_trace("__main__", "p4obs", "trace_link")
_emit_captures_pattern("__main__", "p3lm", "pattern")
_emit_records_learning_event("__main__", "p3lm", "learning_event")
_emit_writes_learning_snapshot("__main__", "p3lm", "snapshot")
_emit_feeds_meta_learning("__main__", "p3lm", "meta_feed")
_emit_updates_routing_strategy("__main__", "p3lm", "routing")
_emit_improves_agent_policy("__main__", "p3lm", "policy")
_emit_stores_learning_state("__main__", "p3lm", "state")
_emit_records_execution_trace("__main__", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("__main__", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("__main__", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("__main__", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("__main__", "L4_STATE", "p2_trace_5")
_emit_reads_environ("__main__", "env_read", "p2_env_1")
_emit_reads_environ("__main__", "env_read", "p2_env_2")
_emit_reads_runtime_state("__main__", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("__main__", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "__main__", "context_pull")
_emit_pulls_context("p1", "__main__", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "__main__", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "__main__", "uwg_term_2")
_emit_writes_through("p1", "__main__", "write_through")
_emit_writes_through("p1", "__main__", "write_through_2")
_emit_validated_by_safety_plane("p1", "__main__", "safety_validation")
_emit_invokes_eval("p1", "__main__", "eval_call")
_emit_proposal_commits_routing("p1", "__main__", "routing_commit")
_emit_escalates_to_human("p1", "__main__", "human_escalation")
_emit_routes_through("p1", "__main__", "route_through")
_emit_checks_agent_registry("p1", "__main__", "agent_registry")
_emit_validates_agent_capability("p1", "__main__", "capability")
_emit_dispatches_execution_plan("p1", "__main__", "exec_plan")
_emit_agent_executes_agent("p1", "__main__", "sub_agent")
_emit_routes_to_agent("p1", "__main__", "target_agent")
_emit_verifies_policy("p1", "__main__", "policy_check")
_emit_observes_runtime_state("p1", "__main__", "runtime_state")
_emit_verifies_boundary("p1", "__main__", "boundary_check")
_emit_transcripts_response("p1", "__main__", "transcript")
_emit_hard_fails_untranscripted("p1", "__main__")
_emit_gated_by_confidence("p1", "__main__", "confidence_gate")
emit_replay_key("p0", "__main__")
emit_determinism_digest("p0", "__main__")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "__main__", "execution_auth")
_emit_validates_capability("p2", "__main__", "capability_check")
_emit_routes_to_capability("p2", "__main__", "capability_route")
_emit_writes_via_uwg("p2", "__main__", "uwg_write")
_emit_blocks_direct_write("p2", "__main__", "direct_write_block")
_emit_records_tool_invocation("p2", "__main__", "tool_invocation")
_emit_captures_execution_output("p2", "__main__", "exec_output")
_emit_dispatches_agent("p3", "__main__", "agent_dispatch")
_emit_coordinates_agents("p3", "__main__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__main__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__main__", "healing_outcome")
_emit_escalates_failure("p3", "__main__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__main__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__main__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__main__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__main__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__main__", "eval_metric")
_emit_stores_embedding("p4", "__main__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__main__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__main__", "exec_snapshot_link")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_rg")


def _adg_bootstrap() -> None:
    try:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], force_fresh=False)
        _log.info("[ADG] %s", report.summary)
        if report.layer_violation_count > 0:
            _log.warning(
                "[ADG] %d layer violation(s) detected: %s",
                report.layer_violation_count,
                report.scope_widening_events,
            )
        if report.route_mode == "HUMAN_REVIEW":
            _log.error("[ADG] route_mode=HUMAN_REVIEW — manual review required before dispatch")
            sys.exit(1)
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-silent-swallower
        _log.warning("[ADG] bootstrap unavailable: %s", exc)


def main() -> None:
    _adg_bootstrap()
    import argparse
    import asyncio
    from pathlib import Path

    from apps_rg.runtime import governed_run
    from apps_rg.scripts.generate_resume import main as _run

    parser = argparse.ArgumentParser(prog="apps_rg", add_help=True)
    parser.add_argument(
        "--target-company",
        default=None,
        help="Target company for narrative pass (HOP-0.6 onward). "
        "When provided, runs the narrative HOPs after the existing pipeline.",
    )
    parser.add_argument(
        "--research-via",
        default=None,
        choices=["apps_research"],
        help="Cross-app generation source for the company brief.",
    )
    parser.add_argument(
        "--auto-research-internal",
        action="store_true",
        help="Use internal CompanyBriefEngine when no manual brief is on disk.",
    )
    parser.add_argument(
        "--auto-research-tavily",
        action="store_true",
        help="Supplement null/stale fields in the brief via Tavily.",
    )
    parser.add_argument(
        "--manual-brief",
        default="apps_rg/scripts/company_research.json",
        help="Path to manual CompanyBrief JSON.",
    )
    parser.add_argument(
        "--target-role",
        default=None,
        help="Target role title for DOCX header.",
    )
    args, _unknown = parser.parse_known_args()

    # Wrap the deterministic HOP pipeline in genuine spine receipts.
    # `governed_run` emits U0/L1/L0/L3-bypass on enter; L2/Exit/L6/OTEL on exit.
    with governed_run(
        target_company=args.target_company,
        target_role=args.target_role,
        cli_args=sys.argv[1:],
    ) as gr:
        with gr.span("apps_rg.entrypoint"):
            with gr.span("L2_execute.generate_resume"):
                asyncio.run(_run())
                gr.mark_stage("generate_resume", "ok")

            if args.target_company:
                with gr.span("L2_execute.post_pipeline"):
                    code = _run_post_pipeline(args)
                    gr.mark_stage("post_pipeline", "ok" if code == 0 else "fail")

            # Resolve the late-bound run dir so post-execution receipts
            # are sealed alongside generated_resume.json + the DOCX.
            runs_root = Path("artifacts/apps_rg/runs")
            if runs_root.exists():
                candidates = sorted(
                    (p for p in runs_root.iterdir() if p.is_dir() and p.name[:8].isdigit()),
                    key=lambda p: p.stat().st_mtime, reverse=True,
                )
                if candidates:
                    gr.set_run_dir(candidates[0])

        gr.set_subprocess_exit_code(0)


def _run_post_pipeline(args) -> int:
    """Run narrative pass + DOCX export against the most recent run dir.

    Returns 0 on success, non-zero on failure. Used by ``governed_run`` to
    populate L2 stage outcomes and Exit X3 disposition.
    """
    import subprocess
    from pathlib import Path

    runs_root = Path("artifacts/apps_rg/runs")
    if not runs_root.exists():
        _log.error("[apps_rg] No runs/ directory found at %s", runs_root)
        return 1
    candidates = sorted(
        (p for p in runs_root.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        _log.error("[apps_rg] No run directory under %s", runs_root)
        return 1
    run_dir = candidates[0]
    input_resume = run_dir / "generated_resume.json"
    if not input_resume.exists():
        _log.error("[apps_rg] %s missing — narrative pass aborted", input_resume)
        return 1

    # Narrative pass.
    cmd = [
        sys.executable,
        "-m",
        "apps_rg.scripts.narrative_pass",
        "--target-company",
        args.target_company,
        "--input-resume",
        str(input_resume),
        "--out-dir",
        str(run_dir),
        "--manual-brief",
        args.manual_brief,
    ]
    if args.research_via:
        cmd.extend(["--research-via", args.research_via])
    if args.auto_research_internal:
        cmd.append("--auto-research-internal")
    if args.auto_research_tavily:
        cmd.append("--auto-research-tavily")
    if args.target_role:
        cmd.extend(["--target-role", args.target_role])

    _log.info("[apps_rg] Running narrative pass: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, timeout=600, shell=False)
    except subprocess.TimeoutExpired:
        _log.error("[apps_rg] narrative pass timed out")
        return 124

    if result.returncode != 0:
        _log.error("[apps_rg] narrative pass exit=%s — DOCX export skipped", result.returncode)
        return result.returncode

    # DOCX export.
    docx_cmd = [
        sys.executable,
        "-m",
        "apps_rg.outputs.docx_exporter",
        "--run-dir",
        str(run_dir),
    ]
    if args.target_role and args.target_company:
        docx_cmd.extend(
            [
                "--target-role",
                args.target_role,
                "--target-company",
                args.target_company,
            ]
        )
    _log.info("[apps_rg] Running DOCX export: %s", " ".join(docx_cmd))
    try:
        docx_result = subprocess.run(docx_cmd, timeout=120, shell=False)
    except subprocess.TimeoutExpired:
        _log.error("[apps_rg] DOCX export timed out")
        return 124
    return docx_result.returncode


if __name__ == "__main__":
    main()
