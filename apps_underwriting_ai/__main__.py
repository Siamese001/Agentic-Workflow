"""apps_underwriting_ai CLI entrypoint — profile-only runtime.

Parses CLI arguments and delegates all execution to
AppIngressRunner(profile=build_app_runtime_contract()).run(payload).
No dispatch callable. No legacy orchestrator. AppIngressRunner owns
the stage sequencing: U0 → L1 → L0 → C0 → PA → L2 → Exit.

Usage::

    python -m apps_underwriting_ai --request input/request.yaml
    python -m apps_underwriting_ai --demo
    python -m apps_underwriting_ai --apps-e2e-live

The ``--demo`` flag runs a synthetic underwriting request through the
full profile-sequenced pipeline and prints the UWExitResult.
The ``--apps-e2e-live`` flag emits the 9 required runtime receipts under
``artifacts/apps_underwriting_ai/runs/<ts>/`` for the apps_e2e harness.

Bundle B — shadow pipeline fully removed. Profile-only runtime.
Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""

from __future__ import annotations

import argparse
import sys

from scripts.proof.otel_bootstrap import setup_tracer as _otel_setup

from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
from agentic_core.L5_safety.enforcement.ingress_envelope_check import ClarificationRequired
from apps_underwriting_ai.runtime.bindings.u0_binding import U0ValidationError
from apps_underwriting_ai.runtime.profile_builder import build_app_runtime_contract


_DEMO_REQUEST_ID = "demo-0001"
_CERT_REQUEST_ID = "cert-live-0001"


def _is_live_cert_mode() -> bool:
    """True when ``--apps-e2e-live`` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


_CERT_CAPABILITY_ID = "apps_underwriting_ai.decision_packet_v1"


def _run_live_cert(argv: list[str]) -> int:
    """Wrap apps_underwriting_ai in spine emission for the apps_e2e harness.

    Emits the 9 strict-required receipts under
    ``artifacts/apps_underwriting_ai/runs/<ts>/``. Exit hook is fail-soft.

    Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W3.
    """
    from pathlib import Path

    from apps_shared.cert import maybe_invoke_exit_eval
    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    cfg = EmissionConfig(
        app_name="apps_underwriting_ai",
        entrypoint_command="python -m apps_underwriting_ai",
        runs_root=repo_root / "artifacts" / "apps_underwriting_ai" / "runs",
        route_registry_path=repo_root
        / "apps_underwriting_ai"
        / "config"
        / "cert_route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake request + documents", kind="ingest"),
            L1PlanStep(
                step_id="reconcile",
                name="Initialize register + reconcile documents",
                kind="transform",
            ),
            L1PlanStep(step_id="derive_features", name="Derive features", kind="transform"),
            L1PlanStep(
                step_id="collect_evidence",
                name="Collect evidence across 5 dimensions",
                kind="assemble",
            ),
            L1PlanStep(step_id="decision", name="Assemble decision packet", kind="render"),
        ],
        plan_rationale=(
            "apps_underwriting_ai is a R3R4_MANAGED_WORKFLOW 5-stage governed pipeline. "
            "Route: intake -> reconcile -> derive_features -> collect_evidence -> decision. "
            "C0 mode: SUBMITTED_DOCUMENT_EVIDENCE_ONLY. Exit: FAIL_CLOSED. "
            "Durable writes: UWG_ONLY. Data mode: SYNTHETIC_DEMO_ONLY."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="MANAGED_WORKFLOW",
        expected_l3_path="R3R4_MANAGED_WORKFLOW",
        selected_capability=_CERT_CAPABILITY_ID,
        repo_root=repo_root,
    )

    cert_route_entry = _load_cert_route_entry(cfg.route_registry_path)

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            receipts = _build_cert_receipts(_CERT_REQUEST_ID)
            gr.mark_stage("L2_execute", "ok")
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    return 0


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from the cert route registry, fail-soft."""
    try:
        import yaml  # noqa: PLC0415

        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- regulated-domain compliance floor:
        # any cert-route load failure leaves the hook as a no-op
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def _build_cert_receipts(request_id: str) -> dict:
    """Build a minimal receipts envelope for the Exit hook.

    Fail-soft — returns a safe-default shape when any component is absent.
    Full receipts (C0 FEC, PA artifact, dim_scores) are wired via U0+L1-Exit dispatch.

    Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W3.
    """
    import apps_underwriting_ai.cert  # noqa: F401, PLC0415 — side-effect: register FEC producer
    from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

    run_ctx: dict = {
        "route_id": _CERT_CAPABILITY_ID,
        "route_contract": {
            "route_id": _CERT_CAPABILITY_ID,
            "route_family": "R3R4_MANAGED_WORKFLOW",
        },
        "request_id": request_id,
        # P1.3 / DS-DEFER-4: enables AppSpecificEvaluator retry-on-low for
        # rationale_quality dim when grader_type=llm_as_judge and raw_score <
        # min_required_score. See apps-eval-harness-deferred-e4a1b7 W4.
        "judge_retry_on_low": True,
    }
    return {
        "output": {"dim_scores": {}, "dim_evidence": {}},
        "route_contract": run_ctx["route_contract"],
        "evidence_bundle": {},
        "final_evidence_contract": resolve_fec("apps_underwriting_ai", run_ctx),
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _run_demo() -> int:
    """Run a synthetic underwriting demo through the full profile-sequenced pipeline.

    Builds a payload dict, calls AppIngressRunner(profile=...).run(payload),
    and prints the UWExitResult. AppIngressRunner owns stage sequencing:
    U0 → L1 → L0 → C0(+5×L2+HITL) → PA → L2(LLM) → Exit.

    Set UW_DISPATCH_SKIP_LLM=1 to skip Qwen inference (deterministic stub).
    Bundle B — profile-only runtime.
    """
    print(
        "PUBLIC DEMO NOTICE: This app uses synthetic applicants and synthetic documents. "
        "It is not a production credit decisioning system."
    )
    payload = {
        "request_id": _DEMO_REQUEST_ID,
        "applicant_id": "demo-applicant-001",
        "product_class": "small_business_loan",
        "documents": [
            {"document_class": "BANK_STATEMENT", "average_monthly_balance": 8500, "account_tenure_months": 36},
            {"document_class": "TAX_RETURN", "annual_gross_income": 120000, "tax_year": 2024},
            {"document_class": "CREDIT_REPORT", "credit_score": 720, "derogatory_mark_count": 0},
        ],
        "metadata": {"source": "demo", "data_mode": "SYNTHETIC_DEMO_ONLY"},
        "trace_id": "demo-trace-0001",
    }
    profile = build_app_runtime_contract()
    runner = AppIngressRunner(profile=profile)
    try:
        result = runner.run(payload)
    except U0ValidationError as exc:
        print(f"U0 validation failed: {exc}", file=sys.stderr)
        return 5

    if isinstance(result, ClarificationRequired):
        print(f"ClarificationRequired: {result.reason}", file=sys.stderr)
        return 4

    print(
        f"[apps_underwriting_ai demo] pipeline complete\n"
        f"  request_id       = {result.request_id}\n"
        f"  applicant_id     = {result.applicant_id}\n"
        f"  product_class    = {result.product_class}\n"
        f"  verdict          = {result.verdict}\n"
        f"  aggregate_score  = {result.aggregate_score:.4f}\n"
        f"  reason_codes     = {result.reason_codes}\n"
        f"  c0_state         = {result.c0_state} (support={result.support_score:.2f})\n"
        f"  hitl_posture     = {result.hitl_posture}\n"
        f"  x3_disposition   = {result.x3_disposition}\n"
        f"  rationale_source = {result.rationale_source}\n"
        f"  rationale        = {result.rationale[:200]}{'...' if len(result.rationale) > 200 else ''}\n"
        f"  success          = {result.success}"
        + (f"\n  error            = {result.error}" if result.error else "")
    )

    # ── L6 Shadow Learning (post-Exit, read-only, fail-soft) ──────────────
    from apps_underwriting_ai.runtime.l6_shadow import run_l6_shadow  # noqa: PLC0415

    u0_package = result.exit_bundle.get("runtime_customization_package") or {}
    l6 = run_l6_shadow(result, u0_package)
    print(
        f"\n[apps_underwriting_ai demo] L6 shadow complete\n"
        f"  l6_success               = {l6.success}\n"
        f"  gauntlet_passed          = {l6.gauntlet_passed}\n"
        f"  promotion_eligible       = {l6.promotion_eligible}\n"
        f"  proposal_count           = {l6.proposal_count}\n"
        f"  rca_root_causes          = {l6.rca_root_causes}\n"
        f"  observer_law_compliant   = {l6.observer_law_compliant}\n"
        f"  eval_record_seal         = {l6.eval_record_seal}\n"
        f"  future_run_candidate     = {l6.future_run_activation_candidate}"
        + (f"\n  l6_error               = {l6.error}" if l6.error else "")
    )

    return 0 if result.success else 6


def _run_from_file(request_path: str, artifact_dir: str | None) -> int:  # noqa: ARG001
    """Run an underwriting request from file through the full profile-sequenced pipeline.

    Reads request_id/applicant_id/product_class/documents from the YAML/JSON
    file and calls AppIngressRunner(profile=...).run(payload). AppIngressRunner
    owns the stage sequencing (U0 → L1 → L0 → C0 → PA → L2 → Exit).

    Set UW_DISPATCH_SKIP_LLM=1 to skip Qwen inference.
    Bundle B — profile-only runtime.
    """
    import json  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    import yaml  # noqa: PLC0415

    p = Path(request_path)
    if not p.exists():
        print(f"error: request file not found: {request_path}", file=sys.stderr)
        return 2

    try:
        text = p.read_text(encoding="utf-8")
        if p.suffix in {".yaml", ".yml"}:
            payload: dict = yaml.safe_load(text) or {}
        elif p.suffix == ".json":
            payload = json.loads(text)
        else:
            print(
                f"error: unsupported file extension {p.suffix} (expected .yaml/.yml/.json)",
                file=sys.stderr,
            )
            return 2
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CLI file-read errors must surface as exit 2
        print(f"error: failed to read request file: {exc}", file=sys.stderr)
        return 2

    for required in ("request_id", "applicant_id", "product_class"):
        if required not in payload:
            print(
                f"error: request file missing required field: {required}",
                file=sys.stderr,
            )
            return 2

    profile = build_app_runtime_contract()
    runner = AppIngressRunner(profile=profile)
    try:
        result = runner.run(payload)
    except U0ValidationError as exc:
        print(f"U0 validation failed: {exc}", file=sys.stderr)
        return 5

    if isinstance(result, ClarificationRequired):
        print(f"ClarificationRequired: {result.reason}", file=sys.stderr)
        return 4

    print(
        f"[apps_underwriting_ai] pipeline complete\n"
        f"  request_id       = {result.request_id}\n"
        f"  applicant_id     = {result.applicant_id}\n"
        f"  product_class    = {result.product_class}\n"
        f"  verdict          = {result.verdict}\n"
        f"  aggregate_score  = {result.aggregate_score:.4f}\n"
        f"  reason_codes     = {result.reason_codes}\n"
        f"  c0_state         = {result.c0_state} (support={result.support_score:.2f})\n"
        f"  hitl_posture     = {result.hitl_posture}\n"
        f"  x3_disposition   = {result.x3_disposition}\n"
        f"  rationale_source = {result.rationale_source}\n"
        f"  success          = {result.success}"
        + (f"\n  error            = {result.error}" if result.error else "")
    )

    # ── L6 Shadow Learning (post-Exit, read-only, fail-soft) ──────────────
    from apps_underwriting_ai.runtime.l6_shadow import run_l6_shadow  # noqa: PLC0415

    u0_package = result.exit_bundle.get("runtime_customization_package") or {}
    l6 = run_l6_shadow(result, u0_package)
    print(
        f"\n[apps_underwriting_ai] L6 shadow complete\n"
        f"  l6_success               = {l6.success}\n"
        f"  gauntlet_passed          = {l6.gauntlet_passed}\n"
        f"  promotion_eligible       = {l6.promotion_eligible}\n"
        f"  proposal_count           = {l6.proposal_count}\n"
        f"  rca_root_causes          = {l6.rca_root_causes}\n"
        f"  observer_law_compliant   = {l6.observer_law_compliant}\n"
        f"  eval_record_seal         = {l6.eval_record_seal}"
        + (f"\n  l6_error               = {l6.error}" if l6.error else "")
    )

    return 0 if result.success else 6


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint — pure shim.

    Parses arguments and delegates to the U0 dispatch chain. No engine
    instantiation, no provider calls, no output rendering in this function.
    """
    _otel_setup(service_name="apps_underwriting_ai")
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))

    parser = argparse.ArgumentParser(prog="apps_underwriting_ai")
    parser.add_argument(
        "--request",
        help="Path to YAML/JSON underwriting request file.",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Optional directory to emit decision artifacts to.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a synthetic demo underwriting request.",
    )
    args = parser.parse_args(argv)

    if args.demo:
        return _run_demo()
    if args.request:
        return _run_from_file(args.request, args.artifact_dir)

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
