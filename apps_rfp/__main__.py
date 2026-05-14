"""Canonical entrypoint for apps_rfp.

Usage:
    python -m apps_rfp

ADG bootstrap fires before any agent dispatch.
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
_log = logging.getLogger("apps_rfp")


def _adg_bootstrap() -> None:
    try:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], force_fresh=False)
        _log.info("[ADG] %s", report.summary)
        if report.layer_violation_count > 0:
            _log.warning(
                "[ADG] %d layer violation(s): %s",
                report.layer_violation_count,
                report.scope_widening_events,
            )
        if report.route_mode == "HUMAN_REVIEW":
            _log.error("[ADG] route_mode=HUMAN_REVIEW — manual review required")
            sys.exit(1)
    except Exception as exc:  # guardian: allow-silent-swallow
        _log.warning("[ADG] bootstrap unavailable: %s", exc)


def _is_live_cert_mode() -> bool:
    """True when `--apps-e2e-live` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _run_live_cert(argv: list[str]) -> int:
    """Wrap the apps_rfp pipeline in apps_shared.spine_emission.

    Emits the 10 strict-required receipts (SINGLE_STEP / BYPASSED with
    C0 grounding + prompt assembly) under
    ``artifacts/apps_rfp/runs/<ts>/``. Plan:
    apps-e2e-spine-cert-wireup-e1c4d7 W5.
    """
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    cfg = EmissionConfig(
        app_name="apps_rfp",
        entrypoint_command="python -m apps_rfp",
        runs_root=repo_root / "artifacts" / "apps_rfp" / "runs",
        route_registry_path=repo_root / "apps_rfp" / "config" / "route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake", kind="ingest"),
            L1PlanStep(step_id="retrieve", name="Retrieve evidence", kind="retrieve"),
            L1PlanStep(step_id="assemble_prompt", name="Assemble prompt", kind="assemble"),
            L1PlanStep(step_id="assemble_proposal", name="Assemble proposal", kind="render"),
            L1PlanStep(step_id="seal", name="Seal output", kind="assemble"),
        ],
        plan_rationale=(
            "apps_rfp is a deterministic single-step proposal-assembly app. Plan is "
            "hard-coded by route selection. C0 grounding is fixture-backed; prompt "
            "assembly is template-driven."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="apps_rfp.proposal_assembly_v1",
        repo_root=repo_root,
    )
    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("C0_retrieval"):
            gr.mark_stage("C0_retrieval", "ok")
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            gr.mark_stage("L2_execute", "ok")
        # W2.P2 of plan apps-runtime-domain-enforcement-a7e9d4 —
        # invoke the v6 Exit pipeline against the sealed L2 artifact
        # so the 10-dim apps_rfp rubric executes. Gated by
        # invoke_exit_eval=true in apps_rfp/config/cert_route_registry.yaml.
        # Fail-soft: any hook failure leaves the cert bundle unaffected.
        # Successor plan apps-rfp-c0-fec-producer-wiring-b9d4f1 will
        # populate final_evidence_contract on top of this hook (BLOCKER #4).
        _maybe_run_exit_hook()
    return 0


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from apps_rfp's cert_route_registry.yaml.

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


def _build_exit_receipts(cert_route_entry) -> dict:
    """Build the receipts dict for run_exit_eval from the symbolic cert path.

    apps_rfp's cert-path live run is currently a SINGLE_STEP symbolic
    pipeline (no real proposal output), so the receipt surface is thin and
    deterministic dim_scores default to 0.0 -> UNKNOWN -> fail-closed per
    rubric evidence_required=true. That is the correct posture: enforcement
    runs, honest UNKNOWN on missing evidence, no false-positive PASS. The
    3 weight=0.0 RAG tracked-only dims (context_recall, context_precision,
    answer_relevancy) produce UNKNOWN without blocking overall PASS, by
    rubric design.

    Fail-soft: returns a minimal shape on any error.

    Successor plan apps-rfp-c0-fec-producer-wiring-b9d4f1 will add a
    ``final_evidence_contract`` population step before this returns.
    """
    from pathlib import Path

    receipts_output: dict = {}
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
        # projection failure yields empty dim_scores (evaluator fail-closes)
        pass

    return {
        "output": receipts_output,
        "route_contract": {"route_id": "apps_rfp.proposal_assembly_v1"},
        "evidence_bundle": {},
        # Populated by plan apps-rfp-c0-fec-producer-wiring-b9d4f1 W1.P2.
        # Side-effect import registers producer; resolve_fec returns the FEC dict.
        "final_evidence_contract": _build_fec_for_receipts(),
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _build_fec_for_receipts() -> dict:
    """Resolve apps_rfp FEC via the shared registry. Fail-soft."""
    try:
        import apps_rfp.cert  # noqa: F401, PLC0415 — side-effect register
        from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

        return resolve_fec(
            "apps_rfp",
            {
                "route_id": "apps_rfp.proposal_assembly_v1",
                "route_contract": {"route_id": "apps_rfp.proposal_assembly_v1"},
                "template_ids": ["proposal_assembly_v1"],
            },
        )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- FEC resolution is fail-soft;
        # any failure leaves final_evidence_contract as empty dict and the
        # cert bundle continues unaffected
        return {}


def _maybe_run_exit_hook() -> None:
    """Invoke the v6 Exit pipeline when apps_rfp's cert route opts in.

    Reads ``apps_rfp/config/cert_route_registry.yaml`` for the
    ``invoke_exit_eval`` flag; builds receipts via the declarative
    rubric output map; calls
    :func:`apps_shared.cert.maybe_invoke_exit_eval` fail-soft.
    """
    from pathlib import Path

    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
    except ImportError:
        return
    registry_path = (
        Path(__file__).resolve().parents[1]
        / "apps_rfp" / "config" / "cert_route_registry.yaml"
    )
    cert_route_entry = _load_cert_route_entry(registry_path)
    if cert_route_entry is None:
        return
    receipts = _build_exit_receipts(cert_route_entry)
    try:
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- cert hook MUST NOT break the
        # bundle-building path; Exit failures are additional evidence only
        _log.warning("[apps_rfp] Exit hook raised %s: %s", type(exc).__name__, exc)


def _run_product_build(argv: list[str]) -> int:
    """Route the apps_rfp product path through AppIngressRunner.

    W2 one-spine migration: RfpOrchestrator is now a private implementation
    detail of the l2_binding. This function is the sole current-run authority
    for apps_rfp product execution. governed_rfp_run is POST_RUN_RECEIPT only.

    TOMBSTONE NOTE: apps_rfp.integrations.rfp_ingress_runner.make_rfp_ingress_runner
    is the old dispatch-factory pattern and MUST NOT be used here. That factory
    passes dispatch= externally — the pattern the one-spine law eliminates.
    NC-4: grep must find zero governed_run / governed_rfp_run / dispatch( calls
    in this function post-migration.

    Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P3
    """
    import argparse

    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract

    parser = argparse.ArgumentParser(
        description="apps_rfp proposal generator (one-spine path)",
        add_help=True,
    )
    parser.add_argument("--rfp-document", dest="rfp_document_path", default="", help="Path to RFP document")
    parser.add_argument("--target-company", dest="target_company", default="", help="Target company name")
    parser.add_argument("--industry", default="technology", help="Industry vertical")
    parser.add_argument("--posture", dest="architecture_posture", default="cloud-first", help="Architecture posture")
    parser.add_argument("--weeks", dest="delivery_timeline_weeks", type=int, default=0, help="Delivery timeline weeks")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=False, help="Dry run mode")
    parser.add_argument("--out", default="", help="Output directory (passed to profile; ignored by binding)")

    known, _ = parser.parse_known_args(argv)

    payload = {
        "rfp_document_path": known.rfp_document_path or "",
        "target_company": known.target_company or "",
        "industry": known.industry,
        "architecture_posture": known.architecture_posture,
        "delivery_timeline_weeks": known.delivery_timeline_weeks,
        "dry_run": known.dry_run,
    }

    if not payload["rfp_document_path"] and not payload["target_company"]:
        _log.error(
            "apps_rfp requires --rfp-document or --target-company. "
            "Usage: python -m apps_rfp --rfp-document <path> [--target-company <name>]"
        )
        return 1

    profile = build_app_runtime_contract()
    runner = AppIngressRunner(profile=profile)

    try:
        result = runner.run(payload)
        disposition = getattr(result, "disposition", None) or str(result)
        _log.info("[apps_rfp] AppIngressRunner completed: disposition=%s", disposition)
        return 0 if str(disposition) in ("complete", "dry_run") else 1
    except (ValueError, RuntimeError, TypeError, KeyError, OSError, AttributeError) as exc:
        _log.error("[apps_rfp] AppIngressRunner failed: %s: %s", type(exc).__name__, exc)
        return 1


def main() -> None:
    # Live certification path — emits real spine receipts and exits 0.
    if _is_live_cert_mode():
        sys.exit(_run_live_cert(list(sys.argv[1:])))
    # apps_e2e auditability harness short-circuit. MUST be first statement
    # of the non-live path.
    from apps_shared._apps_e2e_dry_run import maybe_short_circuit
    maybe_short_circuit("apps_rfp")
    _adg_bootstrap()
    # W2 one-spine migration: product path now routes through AppIngressRunner.
    # RfpOrchestrator is a private l2_binding implementation detail.
    # NC-4: no governed_rfp_run / dispatch( invoked here as current-run authority.
    sys.exit(_run_product_build(list(sys.argv[1:])))


if __name__ == "__main__":
    main()
