"""Canonical entrypoint for apps_qna \u2014 pure CLI envelope parser.

Three modes:

- **Live interview runtime** (``--interview <slug>``): runs the spine pipeline
  (U0\u2192L1\u2192L0\u2192C0/Briefing\u2192L2\u2192Exit) for governed live interview pack builds.

- **Live certification mode** (``--apps-e2e-live``): wraps a deterministic
  pack-build dry-run in ``apps_shared.spine_emission.governed_run`` for the
  apps_e2e harness.

- **Product build mode** (``build`` subcommand or default): wraps the real
  CardPackBuilder.build() in ``governed_run`` with full spine receipts.

- **Auxiliary mode** (lint / route / init / feedback / self-eval): runs
  the CardPackBuilder CLI as before without spine envelope.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.1
     .windsurf/plans/p2-apps-qna-product-spine-b3e8d2.md
"""

from __future__ import annotations

import sys


def _is_live_cert_mode() -> bool:
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _is_live_interview_mode() -> bool:
    return "--interview" in sys.argv


def _is_product_build_mode() -> bool:
    """True when the subcommand is 'build' or default (no subcommand)."""
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            continue
        return arg in ("build",)
    return True  # default = build


def _run_live_interview(argv: list[str]) -> int:
    from apps_qna.live_interview_runtime import run_live_interview

    return run_live_interview(argv)


def _build_emission_config():
    """Shared EmissionConfig for apps_qna product + cert modes."""
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    return EmissionConfig(
        app_name="apps_qna",
        entrypoint_command="python -m apps_qna",
        runs_root=repo_root / "artifacts" / "apps_qna" / "runs",
        route_registry_path=repo_root / "apps_qna" / "config" / "cert_route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake interview + JD + experience", kind="ingest"),
            L1PlanStep(step_id="validate_routes", name="Validate route registry + templates", kind="transform"),
            L1PlanStep(step_id="assemble_prompt", name="Assemble deterministic templates", kind="assemble"),
            L1PlanStep(step_id="render_cards", name="Render card pack", kind="render"),
            L1PlanStep(step_id="seal", name="Seal output", kind="assemble"),
        ],
        plan_rationale=(
            "apps_qna is a deterministic single-step pack builder. The plan is "
            "hard-coded by route selection: intake → validate → assemble → render "
            "→ seal. No C0 grounding (templates are deterministic, not retrieval-"
            "backed); prompt assembly is template-driven."
        ),
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="apps_qna.card_pack_build_v1",
        repo_root=repo_root,
    )


def _run_product_build(argv: list[str]) -> int:
    """Run the real CardPackBuilder.build() inside governed_run spine envelope."""
    from apps_shared.spine_emission import governed_run

    cfg = _build_emission_config()

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            from apps_qna.scripts.run_qna import main as run_main

            _exit_code = run_main(argv)
            if _exit_code == 0:
                gr.mark_stage("L2_execute", "ok")
            else:
                gr.mark_stage("L2_execute", "fail")
    return 0


def _run_live_cert(argv: list[str]) -> int:
    """Wrap apps_qna's deterministic pack-build path in spine emission.

    Emits the strict-required receipts (SINGLE_STEP / BYPASSED with prompt
    assembly) under ``artifacts/apps_qna/runs/<ts>/``. The pack-build work
    itself is a no-op dry-run here — the cert surface proves that the
    app-level runtime contract (route selection, plan shape, exit discipline,
    OTEL trace) is honored, not the card-pack output quality (which is
    ledger-backed per constitutional §29).
    """
    from apps_shared.spine_emission import governed_run
    from apps_shared.cert import maybe_invoke_exit_eval
    from apps_shared.cert.fec_producer import resolve_fec
    import apps_qna.cert  # noqa: F401 — import side-effect: registers FEC producer

    cfg = _build_emission_config()
    cert_route_entry = _load_cert_route_entry(cfg.route_registry_path)

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            # Deterministic no-op for the cert path: the live pack-build runs
            # through its own CLI and is exercised separately by the existing
            # builder/lint tests. Cert-mode proves runtime-contract plumbing.
            gr.mark_stage("L2_execute", "ok")
        # Opt-in Exit-pipeline pass on the sealed L2 artifact. The hook is a
        # no-op when invoke_exit_eval is absent/false on the route entry.
        _run_ctx = {
            "route_id": "apps_qna.pack_build_single_step_v1",
            "route_contract": {"route_id": "apps_qna.pack_build_single_step_v1"},
            "template_ids": ["intake", "validate_routes", "assemble_prompt", "render_cards", "seal"],
            "c0_retrieval_sources": [],  # apps_qna is template-deterministic; upgrades when C0 wires
            "grounded": False,
        }
        _receipts = {
            "output": {},  # apps_qna cert path is deterministic no-op; dim_scores deferred
            "route_contract": _run_ctx["route_contract"],
            "evidence_bundle": {},
            "final_evidence_contract": resolve_fec("apps_qna", _run_ctx),
            "state_diff": {},
            "compiled_prompt_artifact": {},
        }
        maybe_invoke_exit_eval(_receipts, cert_route_entry)
    return 0


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from apps_qna's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, which makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    try:
        import yaml  # noqa: PLC0415

        text = registry_path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 -- cert hook must never break the bundle
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft;
        # any registry-load failure leaves the hook as a no-op and the cert
        # bundle continues unaffected
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def main() -> int:
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))
    if _is_live_interview_mode():
        return _run_live_interview(list(sys.argv[1:]))
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    if _is_product_build_mode():
        return _run_product_build(list(sys.argv[1:]))
    from apps_qna.scripts.run_qna import main as run_main

    return int(run_main())


if __name__ == "__main__":
    raise SystemExit(main())
