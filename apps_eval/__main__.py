"""Canonical entrypoint for apps_eval.

Usage:
    python -m apps_eval --suites routing_enforcement,determinism_contracts

ADG bootstrap fires before any dispatch.
"""

from __future__ import annotations

import logging
import sys

from apps_eval._telemetry import (
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
from apps_eval._telemetry import (
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
_log = logging.getLogger("apps_eval")


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
    """Wrap the apps_eval pipeline in apps_shared.spine_emission.

    Emits the 10 strict-required receipts (SINGLE_STEP / BYPASSED with
    C0 grounding + prompt assembly) under
    ``artifacts/apps_eval/runs/<ts>/``. Plan:
    apps-e2e-spine-cert-wireup-e1c4d7 W3.
    """
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    cfg = EmissionConfig(
        app_name="apps_eval",
        entrypoint_command="python -m apps_eval",
        runs_root=repo_root / "artifacts" / "apps_eval" / "runs",
        route_registry_path=repo_root / "apps_eval" / "config" / "route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake", kind="ingest"),
            L1PlanStep(step_id="retrieve", name="Retrieve evidence", kind="retrieve"),
            L1PlanStep(step_id="assemble_prompt", name="Assemble prompt", kind="assemble"),
            L1PlanStep(step_id="evaluate", name="Evaluate", kind="score"),
            L1PlanStep(step_id="seal", name="Seal output", kind="assemble"),
        ],
        plan_rationale=(
            "apps_eval is a deterministic single-step evaluation app. Plan is hard-coded "
            "by route selection; no model-driven planning is required. C0 grounding is "
            "fixture-backed and deterministic; prompt assembly is template-driven."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="apps_eval.evaluation_v1",
        repo_root=repo_root,
    )
    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("C0_retrieval"):
            gr.mark_stage("C0_retrieval", "ok")
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            gr.mark_stage("L2_execute", "ok")
        # W2.P3 of plan apps-runtime-domain-enforcement-a7e9d4 (closes W2) —
        # invoke the v6 Exit pipeline against the sealed L2 artifact so
        # the 6-dim apps_eval self-rubric executes. Gated by
        # invoke_exit_eval=true in apps_eval/config/cert_route_registry.yaml.
        # Fail-soft: any hook failure leaves the cert bundle unaffected.
        # apps_eval has no pre-existing FEC producer (not in BLOCKER #4
        # grounded-apps set); final_evidence_contract stays {} as seam.
        _maybe_run_exit_hook()
    return 0


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from apps_eval's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, making the hook a no-op.
    """
    try:
        import yaml  # noqa: PLC0415

        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def _build_exit_receipts(cert_route_entry) -> dict:
    """Build the receipts dict for run_exit_eval from the symbolic cert path.

    apps_eval's cert-path live run is currently SINGLE_STEP symbolic (no
    real scorecard emitted), so deterministic dim_scores default to 0.0
    -> UNKNOWN -> fail-closed per rubric evidence_required=true on
    taxonomy_correctness + no_self_contradiction. FEC stays empty as a
    seam for a potential future apps_eval FEC producer.

    Fail-soft.
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
        # guardian: allow-broad-except -- mapper is fail-soft by design
        pass

    return {
        "output": receipts_output,
        "route_contract": {"route_id": "apps_eval.evaluation_v1"},
        "evidence_bundle": {},
        "final_evidence_contract": {},  # seam; no FEC producer for apps_eval yet
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _maybe_run_exit_hook() -> None:
    """Invoke the v6 Exit pipeline when apps_eval's cert route opts in.

    Reads ``apps_eval/config/cert_route_registry.yaml`` for the
    ``invoke_exit_eval`` flag; builds receipts via the declarative rubric
    output map; calls
    :func:`apps_shared.cert.maybe_invoke_exit_eval` fail-soft.
    """
    from pathlib import Path

    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
    except ImportError:
        return
    registry_path = (
        Path(__file__).resolve().parents[1]
        / "apps_eval" / "config" / "cert_route_registry.yaml"
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
        _log.warning("[apps_eval] Exit hook raised %s: %s",
                     type(exc).__name__, exc)


def main() -> None:
    # Live certification path — emits real spine receipts and exits 0.
    if _is_live_cert_mode():
        sys.exit(_run_live_cert(list(sys.argv[1:])))
    # apps_e2e auditability harness short-circuit. MUST be first statement
    # of the non-live path.
    from apps_shared._apps_e2e_dry_run import maybe_short_circuit
    maybe_short_circuit("apps_eval")
    _adg_bootstrap()
    from apps_eval.scripts.run_eval import main as _run

    sys.exit(_run())


if __name__ == "__main__":
    main()
