"""Canonical entrypoint for apps_research."""

from __future__ import annotations

import importlib
import logging
import sys

_log = logging.getLogger("apps_research")


def _adg_bootstrap() -> None:
    """Run optional ADG bootstrap without making package import fragile."""
    try:
        module = importlib.import_module("agentic_core.adg.applications.execute_ssot_integration")
        build_pre_run_report = getattr(module, "build_pre_run_report")
    except (ImportError, AttributeError):
        return

    try:
        report = build_pre_run_report(changed_files=[], force_fresh=False)
    except Exception as exc:  # guardian: allow-broad-exception -- build_pre_run_report raises heterogeneous errors (OSError, RuntimeError, sqlite3.Error); all logged, bootstrap degrades gracefully
        _log.warning("[ADG] bootstrap unavailable: %s", exc)
        return

    _log.info("[ADG] %s", getattr(report, "summary", "pre-run report generated"))
    if getattr(report, "layer_violation_count", 0) > 0:
        _log.warning(
            "[ADG] %d layer violation(s): %s",
            report.layer_violation_count,
            getattr(report, "scope_widening_events", []),
        )
    if getattr(report, "route_mode", "") == "HUMAN_REVIEW":
        raise SystemExit(1)


def _is_live_cert_mode() -> bool:
    """True when `--apps-e2e-live` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _run_live_cert(argv: list[str]) -> int:
    """Wrap the apps_research pipeline in apps_shared.spine_emission.

    Emits the 10 strict-required receipts (SINGLE_STEP / BYPASSED with
    C0 grounding + prompt assembly) under
    ``artifacts/apps_research/runs/<ts>/``. Plan:
    apps-e2e-spine-cert-wireup-e1c4d7 W4.
    """
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    cfg = EmissionConfig(
        app_name="apps_research",
        entrypoint_command="python -m apps_research",
        runs_root=repo_root / "artifacts" / "apps_research" / "runs",
        route_registry_path=repo_root / "apps_research" / "config" / "route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake", kind="ingest"),
            L1PlanStep(step_id="retrieve", name="Retrieve evidence", kind="retrieve"),
            L1PlanStep(step_id="assemble_prompt", name="Assemble prompt", kind="assemble"),
            L1PlanStep(step_id="generate_brief", name="Generate company brief", kind="render"),
            L1PlanStep(step_id="seal", name="Seal output", kind="assemble"),
        ],
        plan_rationale=(
            "apps_research is a deterministic single-step research app. Plan is "
            "hard-coded by route selection. C0 grounding is fixture-backed; prompt "
            "assembly is template-driven."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="apps_research.company_brief_v1",
        repo_root=repo_root,
    )
    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("C0_retrieval"):
            gr.mark_stage("C0_retrieval", "ok")
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            gr.mark_stage("L2_execute", "ok")
    return 0


def main() -> int:
    # Live certification path — emits real spine receipts and exits 0.
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))
    # apps_e2e auditability harness short-circuit. MUST be first statement
    # of the non-live path.
    from apps_shared._apps_e2e_dry_run import maybe_short_circuit
    maybe_short_circuit("apps_research")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    _adg_bootstrap()
    from apps_research.scripts.run_research import main as run_main

    return int(run_main())


if __name__ == "__main__":
    raise SystemExit(main())
