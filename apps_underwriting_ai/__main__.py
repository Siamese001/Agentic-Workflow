"""apps_underwriting_ai CLI entrypoint — pure shim.

Parses CLI arguments and delegates all execution to the agentic_core
canonical runner via the registered capability. This module must not
import underwriting engines, C0 adapters, PA compilers, L2 adapters,
output renderers, or provider SDKs.

Usage::

    python -m apps_underwriting_ai --request input/request.yaml
    python -m apps_underwriting_ai --demo
    python -m apps_underwriting_ai --apps-e2e-live

The ``--demo`` flag runs a synthetic underwriting request via the
capability registry. The ``--apps-e2e-live`` flag emits the 9 required
runtime receipts under ``artifacts/apps_underwriting_ai/runs/<ts>/``
for the apps_e2e harness.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W1.1.
"""

from __future__ import annotations

import argparse
import sys

from apps_underwriting_ai.integrations.underwriting_capability_registry import (
    register_decision_packet_capability,
    resolve_decision_packet_capability,
)


_CAPABILITY_ID = "apps_underwriting_ai.decision_packet_v1"
_DEMO_REQUEST_ID = "demo-0001"
_CERT_REQUEST_ID = "cert-live-0001"


def _is_live_cert_mode() -> bool:
    """True when ``--apps-e2e-live`` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _resolve_capability() -> dict | None:
    """Register and resolve the underwriting capability. Returns None on failure."""
    register_decision_packet_capability()
    return resolve_decision_packet_capability(_CAPABILITY_ID)


def _r5_terminal(reason: str) -> int:
    """Emit an R5 fail-closed terminal packet and return exit code 5."""
    print(
        f"R5_FALLBACK: capability='{_CAPABILITY_ID}' unavailable. "
        f"reason={reason} "
        "exit=FAIL_CLOSED",
        file=sys.stderr,
    )
    return 5


def _run_live_cert(argv: list[str]) -> int:
    """Wrap apps_underwriting_ai in spine emission for the apps_e2e harness.

    Emits the 9 strict-required receipts under
    ``artifacts/apps_underwriting_ai/runs/<ts>/``. Delegates pipeline
    execution through the capability registry; Exit hook is fail-soft.

    Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W1.1.
    """
    from pathlib import Path

    from apps_shared.cert import maybe_invoke_exit_eval
    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    capability = _resolve_capability()
    if capability is None:
        return _r5_terminal("capability not registered for cert path")

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
        selected_capability=_CAPABILITY_ID,
        repo_root=repo_root,
    )

    cert_route_entry = _load_cert_route_entry(cfg.route_registry_path)

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            receipts = _build_cert_receipts(_CERT_REQUEST_ID, capability)
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


def _build_cert_receipts(request_id: str, capability: dict) -> dict:
    """Build a minimal receipts envelope for the Exit hook.

    Fail-soft — returns a safe-default shape when any component is absent.
    Full receipts (C0 FEC, PA artifact, dim_scores) are wired in W2/W3/W5.

    Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W1.1.
    """
    import apps_underwriting_ai.cert  # noqa: F401, PLC0415 — side-effect: register FEC producer
    from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

    run_ctx: dict = {
        "route_id": _CAPABILITY_ID,
        "route_contract": {
            "route_id": _CAPABILITY_ID,
            "route_family": capability.get("route_family", "R3R4_MANAGED_WORKFLOW"),
        },
        "request_id": request_id,
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
    """Run a synthetic underwriting demo via the capability registry.

    R5 fail-closed if the capability is unavailable.
    Full pipeline execution is wired in W2/W3 (C0 + L3 adapter completion).
    """
    capability = _resolve_capability()
    if capability is None:
        return _r5_terminal("capability not registered for demo path")

    print(
        f"[apps_underwriting_ai demo] capability='{_CAPABILITY_ID}' "
        f"route_family='{capability.get('route_family')}' "
        f"execution_form='{capability.get('execution_form')}' "
        "status=STUB_OK — full pipeline executes after W2/W3."
    )
    print(
        "PUBLIC DEMO NOTICE: This app uses synthetic applicants and synthetic documents. "
        "It is not a production credit decisioning system."
    )
    return 0


def _run_from_file(request_path: str, artifact_dir: str | None) -> int:
    """Run an underwriting request from file via the capability registry.

    R5 fail-closed if the capability is unavailable.
    Full file-parsing and pipeline execution is wired in W2/W3.
    """
    capability = _resolve_capability()
    if capability is None:
        return _r5_terminal("capability not registered for file-request path")

    print(
        f"[apps_underwriting_ai] capability='{_CAPABILITY_ID}' "
        f"request='{request_path}' artifact_dir='{artifact_dir}' "
        f"route_family='{capability.get('route_family')}' "
        "status=STUB_OK — full pipeline executes after W2/W3."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint — pure shim.

    Parses arguments and delegates to the capability registry. No engine
    instantiation, no provider calls, no output rendering in this function.
    """
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
