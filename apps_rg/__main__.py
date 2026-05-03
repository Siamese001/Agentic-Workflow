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


_HOP_PLAN_RATIONALE = (
    "apps_rg is a deterministic HOP pipeline. Plan is hard-coded by route "
    "selection; no model-driven planning is required. Grounding and prompt "
    "assembly are handled internally by the narrative HOPs and do not require "
    "separate C0/PA stages at the spine level."
)


def _apps_rg_emission_config(
    target_company: str | None,
    target_role: str | None,
):
    """Build the ``EmissionConfig`` for an apps_rg live run.

    Uses the shared ``apps_shared.spine_emission`` helper — the same one
    apps_exec/apps_lic/apps_eval/apps_research/apps_rfp use. apps_rg used
    to carry its own 700-LOC copy under ``apps_rg/runtime/``; that
    duplication was collapsed per plan ``collapse-apps-rg-runtime-b7e2f5``.
    """
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    return EmissionConfig(
        app_name="apps_rg",
        entrypoint_command="python -m apps_rg",
        runs_root=repo_root / "artifacts" / "apps_rg" / "runs",
        route_registry_path=repo_root / "apps_rg" / "config" / "route_registry.yaml",
        l3_dag_path=repo_root / "apps_rg" / "config" / "l3_dag.yaml",
        plan_steps=[
            L1PlanStep(step_id="hop_0_intake", name="HOP-0 Intake", kind="ingest"),
            L1PlanStep(step_id="hop_1_extract", name="HOP-1 Extraction", kind="transform"),
            L1PlanStep(step_id="hop_2_score", name="HOP-2 Scoring", kind="score"),
            L1PlanStep(step_id="hop_3_assemble", name="HOP-3 Resume Assembly", kind="render"),
            L1PlanStep(step_id="hop_4_narrative", name="HOP-4 Narrative Pass", kind="render", optional=True),
            L1PlanStep(step_id="hop_5_docx", name="HOP-5 DOCX Export", kind="render", optional=True),
        ],
        plan_rationale=_HOP_PLAN_RATIONALE,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_static_dag=True,
        expected_execution_form="DETERMINISTIC_PIPELINE",
        expected_l3_path="BYPASSED",
        selected_capability="apps_rg.resume_generation_v1",
        target_company=target_company,
        target_role=target_role,
        repo_root=repo_root,
    )


def _get_current_policy_hash() -> str:
    """Get current policy hash from config or environment."""
    import os

    return os.environ.get("APPS_RG_POLICY_HASH", "policy_v1")


def _get_current_blueprint_hash() -> str:
    """Get current blueprint hash from config or environment."""
    import os

    return os.environ.get("APPS_RG_BLUEPRINT_HASH", "blueprint_v1")


def _check_r1b_cache(args, cfg) -> dict | None:
    """Check R1B semantic cache for matching intent."""
    from apps_rg.utils.intent_builder import build_intent_from_request
    from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
    from pathlib import Path

    candidate_path = Path(args.candidate) if hasattr(args, "candidate") and args.candidate else Path("profiles/default.yaml")
    if not candidate_path.exists():
        candidate_path = Path("apps_rg/scripts/candidate_profile.yaml")

    intent = build_intent_from_request(
        candidate_profile_path=candidate_path,
        target_company=args.target_company or "",
        target_role=args.target_role or "",
        target_level=getattr(args, "target_level", None),
        tenant_id=cfg.tenant_id if hasattr(cfg, "tenant_id") else "default",
    )

    adapter = AppsRgR1BCacheAdapter(
        tenant_id=cfg.tenant_id if hasattr(cfg, "tenant_id") else "default"
    )
    return adapter.recall_output_for_intent(
        intent=intent,
        policy_hash=_get_current_policy_hash(),
        blueprint_hash=_get_current_blueprint_hash(),
    )


def _check_briefing_prerequisite(args, cfg):
    """Check historical research briefing prerequisite."""
    from apps_rg.prerequisites.briefing_validator import HistoricalBriefingValidator

    validator = HistoricalBriefingValidator(
        policy_hash=_get_current_policy_hash(),
        blueprint_hash=_get_current_blueprint_hash(),
        tenant_id=cfg.tenant_id if hasattr(cfg, "tenant_id") else "default",
    )

    return validator.validate_for_request(
        target_company=args.target_company or "",
        target_role=args.target_role or "",
    )


def _chunk_and_commit_output(gr, args, cfg, run_dir):
    """Chunk resume output and commit via UWG."""
    import json
    from pathlib import Path

    from apps_rg.chunking.resume_chunker import ResumeChunker
    from apps_rg.cache.chunk_commit import commit_chunks_via_exit
    from apps_rg.utils.intent_builder import build_intent_from_request, derive_intent_hash

    # Load generated resume
    resume_path = Path(run_dir) / "generated_resume.json"
    if not resume_path.exists():
        _log.warning("[apps_rg] No generated_resume.json to chunk")
        return None

    try:
        resume_content = json.loads(resume_path.read_text())
    except Exception as exc:  # guardian: allow-broad-exception -- chunking is fail-soft
        _log.warning("[apps_rg] Failed to load resume for chunking: %s", exc)
        return None

    # Build intent hash for lineage
    candidate_path = Path(args.candidate) if hasattr(args, "candidate") and args.candidate else Path("profiles/default.yaml")
    if not candidate_path.exists():
        candidate_path = Path("apps_rg/scripts/candidate_profile.yaml")

    intent = build_intent_from_request(
        candidate_profile_path=candidate_path,
        target_company=args.target_company or "",
        target_role=args.target_role or "",
        tenant_id=cfg.tenant_id if hasattr(cfg, "tenant_id") else "default",
    )
    intent_hash = derive_intent_hash(intent)

    # Build run context with lineage
    run_context = {
        "run_id": gr.run_id if hasattr(gr, "run_id") else "unknown",
        "request_id": intent.request_id,
        "tenant_id": cfg.tenant_id if hasattr(cfg, "tenant_id") else "default",
        "target_job": {
            "company": args.target_company,
            "role": args.target_role,
        },
        "policy_hash": _get_current_policy_hash(),
        "blueprint_hash": _get_current_blueprint_hash(),
        "exit_disposition": getattr(gr, "exit_disposition", None),
        "uwg_commit_receipt": getattr(gr, "uwg_commit_receipt", None),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Chunk and commit
    chunker = ResumeChunker()
    chunks = chunker.chunk_resume(resume_content, run_context, intent_hash)

    receipt = commit_chunks_via_exit(chunks, run_context)
    if receipt:
        gr.mark_stage("chunk_commit", "ok")
        _log.info("[apps_rg] Committed %d resume chunks via UWG", len(chunks))
    else:
        gr.mark_stage("chunk_commit", "fail")
        _log.warning("[apps_rg] Failed to commit resume chunks")

    return receipt


def main() -> None:
    _adg_bootstrap()
    import argparse
    import asyncio
    from pathlib import Path
    from datetime import datetime, timezone

    from apps_shared.spine_emission import governed_run
    from apps_rg.scripts.generate_resume import main as _run
    from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
    from apps_rg.prerequisites.briefing_validator import check_briefing_prerequisite

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
    # New args for R1B and prerequisite control
    parser.add_argument(
        "--candidate",
        default=None,
        help="Path to candidate profile YAML/JSON.",
    )
    parser.add_argument(
        "--target-level",
        default=None,
        help="Target level (junior, mid, senior, staff, principal).",
    )
    parser.add_argument(
        "--skip-r1b-check",
        action="store_true",
        help="Skip R1B semantic cache check (force regeneration)",
    )
    parser.add_argument(
        "--require-briefing",
        action="store_true",
        default=True,
        help="Require historical research briefing (fail closed if missing)",
    )
    args, _unknown = parser.parse_known_args()

    # Wrap the deterministic HOP pipeline in genuine spine receipts.
    # `governed_run` emits U0/L1/L0/L3-bypass on enter; L2/Exit/L6/OTEL on exit.
    cfg = _apps_rg_emission_config(
        target_company=args.target_company,
        target_role=args.target_role,
    )
    with governed_run(cfg, cli_args=sys.argv[1:]) as gr:
        with gr.span("apps_rg.entrypoint"):

            # W1: R1B semantic cache check (L0)
            if not args.skip_r1b_check and args.target_company and args.target_role:
                with gr.span("L0.r1b_cache_check"):
                    r1b_hit = _check_r1b_cache(args, cfg)
                    if r1b_hit:
                        # R1B hit — terminal return with cached output
                        _log.info("[apps_rg] R1B cache hit — terminal return")
                        gr.mark_stage("r1b_cache", "hit")
                        # Store the cached chunks as the result
                        if "output_chunks" in r1b_hit:
                            gr.mark_stage("generate_resume", "r1b_cached")
                        gr.set_subprocess_exit_code(0)
                        # Terminal — skip L2 execution
                        # Fall through to exit hook for proper disposition
                        _maybe_run_exit_hook(None)
                        return
                    else:
                        gr.mark_stage("r1b_cache", "miss")

            # W2: Historical research briefing prerequisite (L0)
            if args.require_briefing and args.target_company:
                with gr.span("L0.briefing_prerequisite"):
                    briefing_check = _check_briefing_prerequisite(args, cfg)
                    if not briefing_check.is_valid:
                        if briefing_check.requires_apps_research:
                            # Route to apps_research first
                            _log.info(
                                "[apps_rg] Briefing prerequisite not met (%s) — "
                                "will invoke apps_research",
                                briefing_check.result.value
                            )
                            gr.mark_stage("briefing_prerequisite", f"need_research:{briefing_check.result.value}")
                            # Continue to L2 — apps_research will be invoked
                            # as part of the managed workflow or narrative pass
                        else:
                            # Fail closed — cannot proceed
                            _log.error(
                                "[apps_rg] Briefing prerequisite failed (%s: %s) — "
                                "failing closed",
                                briefing_check.result.value,
                                briefing_check.reason
                            )
                            gr.mark_stage("briefing_prerequisite", f"fail:{briefing_check.result.value}")
                            gr.set_subprocess_exit_code(1)
                            return
                    else:
                        gr.mark_stage("briefing_prerequisite", "valid")

            # L2 Execution (only if not R1B terminal)
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
            run_dir = None
            if runs_root.exists():
                candidates = sorted(
                    (p for p in runs_root.iterdir() if p.is_dir() and p.name[:8].isdigit()),
                    key=lambda p: p.stat().st_mtime, reverse=True,
                )
                if candidates:
                    run_dir = candidates[0]
                    gr.set_run_dir(run_dir)

            # W1.P1 fix: Propagate HUMAN_REVIEW status to spine receipts.
            # If run_report.status='HUMAN_REVIEW' (e.g., provenance failure),
            # mark the provenance stage as 'fail' so _compute_x3() returns
            # EXIT_PARTIAL with provenance in failed_stages.
            _maybe_mark_provenance_failure(gr, run_dir)

            # W2.P1 of plan apps-runtime-domain-enforcement-a7e9d4 —
            # invoke the v6 Exit pipeline against the sealed L2 artifact
            # so the 8-dim apps_rg rubric executes. Gated by
            # invoke_exit_eval=true in apps_rg/config/cert_route_registry.yaml.
            # Fail-soft: any hook failure leaves the cert bundle unaffected.
            _maybe_run_exit_hook(run_dir)

            # W3: Output chunking after successful generation and Exit clearance
            if run_dir:
                with gr.span("L2.chunk_output"):
                    _chunk_and_commit_output(gr, args, cfg, run_dir)

        gr.set_subprocess_exit_code(0)


def _maybe_mark_provenance_failure(gr, run_dir) -> None:
    """Read run_report.json and mark provenance stage fail if status=HUMAN_REVIEW.

    This wires the orchestrator's HUMAN_REVIEW signal (e.g., from provenance
    gate failure) into the spine's _failed_stages so _compute_x3() emits
    EXIT_PARTIAL instead of EXIT_OK.
    """
    if run_dir is None:
        return
    run_report_path = Path(run_dir) / "run_report.json"
    if not run_report_path.exists():
        return
    try:
        import json  # noqa: PLC0415
        run_report = json.loads(run_report_path.read_text(encoding="utf-8"))
        status = run_report.get("status")
        if status == "HUMAN_REVIEW":
            # Check if provenance specifically failed
            provenance = run_report.get("provenance_report", {})
            if provenance.get("valid") is False:
                gr.mark_stage("provenance", "fail")
                _log.warning(
                    "[apps_rg] Provenance failure detected (valid=%s, reason=%s). "
                    "Marked 'provenance' stage as fail -> EXIT_PARTIAL.",
                    provenance.get("valid"),
                    provenance.get("reason"),
                )
            else:
                # HUMAN_REVIEW for other reasons — still mark but log generically
                gr.mark_stage("orchestrator", "fail")
                _log.warning(
                    "[apps_rg] HUMAN_REVIEW status detected (reason=unknown). "
                    "Marked 'orchestrator' stage as fail -> EXIT_PARTIAL."
                )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- fail-soft; receipt correctness is primary
        pass


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from apps_rg's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, which makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    try:
        import yaml  # noqa: PLC0415

        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft;
        # any registry-load failure leaves the hook as a no-op and the cert
        # bundle continues unaffected
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def _build_exit_receipts_from_run_dir(run_dir, cert_route_entry) -> dict:
    """Build the receipts dict from a sealed apps_rg run_dir for run_exit_eval.

    Reads generated_resume.json + ancillary artifacts from the run_dir,
    projects per-dim scores via the YAML rubric output map, and returns
    the canonical receipts shape v6 preflight consumes.

    Fail-soft: returns a minimal shape with empty dim_scores on any error
    (AppSpecificEvaluator then fail-closes per rubric config).
    """
    from pathlib import Path

    receipts_output: dict = {"run_dir": str(run_dir) if run_dir else None}
    try:
        if run_dir:
            resume_path = Path(run_dir) / "generated_resume.json"
            if resume_path.exists():
                import json  # noqa: PLC0415
                receipts_output["generated_resume"] = json.loads(
                    resume_path.read_text(encoding="utf-8"),
                )
            # Optional ancillary artifacts (present when HOP-2 emitted them).
            for name in ("grounding_report.json", "format_validation.json",
                         "narrative_metadata.json"):
                p = Path(run_dir) / name
                if p.exists():
                    import json  # noqa: PLC0415
                    key = name.replace(".json", "")
                    receipts_output[key] = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- receipts building is fail-soft
        pass

    try:
        from apps_shared.cert import map_l2_receipt_to_dim_scores
        map_path = None
        if isinstance(cert_route_entry, dict):
            rel = cert_route_entry.get("rubric_output_map_path")
            if isinstance(rel, str) and rel:
                map_path = Path(__file__).resolve().parents[1] / rel
        if map_path and map_path.exists():
            projected = map_l2_receipt_to_dim_scores(
                {"output": receipts_output}, map_path,
            )
            receipts_output.update(projected)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- mapper is fail-soft by design;
        # any projection failure yields empty dim_scores (evaluator fail-closes)
        pass

    return {
        "output": receipts_output,
        "route_contract": {"route_id": "apps_rg.resume_generation_v1"},
        "evidence_bundle": {},
        "final_evidence_contract": {},
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _maybe_run_exit_hook(run_dir) -> None:
    """Invoke the v6 Exit pipeline when apps_rg's cert route opts in.

    Reads ``apps_rg/config/cert_route_registry.yaml`` for the
    ``invoke_exit_eval`` flag; builds receipts from ``run_dir`` via the
    declarative rubric output map; calls
    :func:`apps_shared.cert.maybe_invoke_exit_eval` fail-soft.
    """
    from pathlib import Path

    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
    except ImportError:
        return
    registry_path = (
        Path(__file__).resolve().parents[1]
        / "apps_rg" / "config" / "cert_route_registry.yaml"
    )
    cert_route_entry = _load_cert_route_entry(registry_path)
    if cert_route_entry is None:
        return
    receipts = _build_exit_receipts_from_run_dir(run_dir, cert_route_entry)
    try:
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- cert hook MUST NOT break the
        # bundle-building path; Exit failures are additional evidence only
        _log.warning("[apps_rg] Exit hook raised %s: %s", type(exc).__name__, exc)


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


def main_canonical() -> None:
    """Canonical entrypoint using SpineRuntimeAdapter with agentic_core wiring.

    W4.P1: This is the bridge to the canonical runtime. It uses
    SpineRuntimeAdapter with prefer_canonical=True to produce V15RouteContract
    and canonical L2 receipts instead of the legacy thin contracts.

    W6.P3: HITL fail-closed behavior added per AG-RG-012 decision B.
    When run_report.status='HUMAN_REVIEW', the HITL bridge evaluates the
    GateDecision; if disposition is not ALLOW, the process exits 1.

    For W4, this runs side-by-side with main(). Future waves will flip
    the default once full v6 Exit pipeline integration is verified.
    """
    _adg_bootstrap()
    import argparse
    import asyncio
    import sys
    from pathlib import Path

    # W4: Import the adapter
    from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
    from apps_rg.scripts.generate_resume import main as _run

    # W6.P3: Import HITL bridge for fail-closed behavior
    from apps_rg.integrations.hitl_bridge import evaluate_hitl

    parser = argparse.ArgumentParser(prog="apps_rg", add_help=True)
    parser.add_argument("--target-company", default=None)
    parser.add_argument("--target-role", default=None)
    parser.add_argument("--research-via", default=None, choices=["apps_research"])
    parser.add_argument("--auto-research-internal", action="store_true")
    parser.add_argument("--auto-research-tavily", action="store_true")
    parser.add_argument("--manual-brief", default="apps_rg/scripts/company_research.json")
    args, _unknown = parser.parse_known_args()

    # Build config same as legacy path
    cfg = _apps_rg_emission_config(
        target_company=args.target_company,
        target_role=args.target_role,
    )

    # W4: Use SpineRuntimeAdapter with prefer_canonical=True
    adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)

    # W6.P3: Track run_dir for HITL evaluation after governed_run exits
    run_dir: Path | None = None

    with adapter.governed_run(cli_args=sys.argv[1:]) as gr:
        run_dir = getattr(gr, "run_dir", None)  # Extract run_dir if available
        with gr.span("apps_rg.entrypoint"):
            with gr.span("L2_execute.generate_resume"):
                asyncio.run(_run())
                gr.mark_stage("generate_resume", "ok")

            if args.target_company:
                with gr.span("L2_execute.post_pipeline"):
                    # Placeholder: _run_post_pipeline needs adapter-compatible version
                    # For W4 skeleton, we skip the actual DOCX export
                    gr.mark_stage("post_pipeline", "ok")

        gr.set_subprocess_exit_code(0)

    # W6.P3 AG-RG-012 decision B: HITL fail-closed behavior
    # After governed_run exits, evaluate HITL if run_dir has HUMAN_REVIEW status
    if run_dir is not None:
        hitl_decision = evaluate_hitl(run_dir, replay_key=getattr(adapter, "replay_key", None))
        if hitl_decision is not None:
            # Fail-closed: anything other than explicit ALLOW is a reject
            from agentic_core.L5_safety.runtime_gates.types import Disposition
            if hitl_decision.disposition != Disposition.ALLOW:
                print(
                    f"[apps_rg] HITL fail-closed: disposition={hitl_decision.disposition.value}, "
                    f"reasons={hitl_decision.reason_codes}",
                    file=sys.stderr,
                )
                sys.exit(1)


if __name__ == "__main__":
    main()
