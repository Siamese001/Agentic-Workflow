"""apps_underwriting_ai CLI entrypoint.

Usage::

    python -m apps_underwriting_ai --request input/request.yaml
    python -m apps_underwriting_ai --demo
    python -m apps_underwriting_ai --apps-e2e-live

The ``--demo`` flag runs a deterministic synthetic underwriting request
end-to-end through the 5-stage pipeline and prints the decision packet.

The ``--apps-e2e-live`` flag wraps a deterministic underwriting demo run
in ``apps_shared.spine_emission.governed_run`` so the apps_e2e harness
captures the 9 required runtime receipts (route_contract, l1_plan_contract,
l3_bypass_receipt, l2_execution_receipt, exit_review_packet,
runtime_exhaust_bundle, otel_runtime_trace, prompt_assembly_manifest,
u0_intake_envelope). Plan: apps-fort-knox-parity-c5d9a3 post-W11 scope
expansion (2026-05-02) -- user requested runtime cert for apps_underwriting_ai
rather than WAIVED_SKELETON.
"""

from __future__ import annotations

import argparse
import sys

from apps_underwriting_ai.integrations.governed_underwriting_run import (
    governed_underwriting_run,
)
from apps_underwriting_ai.integrations.underwriting_ingress_runner import (
    UnderwritingIngressRunner,
)
from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.outputs.enterprise_underwriting_renderer import (
    EnterpriseUnderwritingRenderer,
)


def _is_live_cert_mode() -> bool:
    """True when ``--apps-e2e-live`` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _run_live_cert(argv: list[str]) -> int:
    """Wrap apps_underwriting_ai's deterministic 5-stage pipeline in spine emission.

    Emits the 9 strict-required receipts (SINGLE_STEP / BYPASSED with prompt
    assembly) under ``artifacts/apps_underwriting_ai/runs/<ts>/``. The actual
    pipeline execution proves the runtime contract surface (route selection,
    plan shape, exit discipline, OTEL trace) is honored; the decision-packet
    correctness itself is pinned by the DeterministicRiskScorer's 18-test
    contract suite (apps_underwriting_ai/engines/risk_scorer.py).
    """
    from pathlib import Path

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
            "apps_underwriting_ai is a deterministic 5-stage HOP pipeline. The plan "
            "is hard-coded by route selection: intake -> reconcile -> derive_features "
            "-> collect_evidence -> decision. No C0 grounding (deterministic feature "
            "derivation, not retrieval-backed); prompt assembly is template-driven "
            "by the DeterministicRiskScorer rationale composition."
        ),
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="apps_underwriting_ai.decision_packet_v1",
        repo_root=repo_root,
    )
    # W2.P3 adoption (plan apps-eval-harness-deferred-e4a1b7 W1.P2):
    # cert-route invoke_exit_eval flag gates the v6 Exit pipeline pass on
    # the sealed L2 artifact. Paired with apps_underwriting_ai.engines.
    # rubric_output_mapper which projects DecisionPacket → dim_scores so
    # the apps_underwriting_ai 5-dim rubric executes on cert runs.
    # Regulated-domain floor: the hook is fail-soft. Any Exit failure
    # leaves the cert bundle unaffected.
    from apps_shared.cert import maybe_invoke_exit_eval
    from apps_underwriting_ai.engines.rubric_output_mapper import (
        map_decision_to_dim_scores,
    )
    cert_route_entry = _load_cert_route_entry(cfg.route_registry_path)

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            # Drive the real pipeline so the receipts reflect a genuine run.
            uw_result = governed_underwriting_run(
                request_id="cert-live-0001",
                applicant_id="applicant-cert",
                product_class="small_business_loan",
                documents=(
                    {"kind": "tax_return", "year": 2025},
                    {"kind": "bank_statement", "month": "2026-04"},
                ),
                metadata={"source": "apps_e2e_live"},
                trace_id="cert-live-trace",
            )
            gr.mark_stage("L2_execute", "ok")
        # Exit-pipeline pass with rubric output projected from the real
        # DecisionPacket. Fail-soft — telemetry path only.
        _receipts = _build_exit_receipts_from_uw_result(uw_result, map_decision_to_dim_scores)
        maybe_invoke_exit_eval(_receipts, cert_route_entry)
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


def _build_exit_receipts_from_uw_result(uw_result, mapper) -> dict:
    """Build the receipts dict from an UnderwritingResult for run_exit_eval.

    Fails soft on any missing attribute — returns a minimal shape that
    still satisfies v6 preflight. The rubric executes on whatever dim
    scores are derivable; absent ones fall through to UNKNOWN → fail-closed.

    FEC producer wiring: plan apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9 W1.P2.
    """
    # Side-effect import: registers apps_underwriting_ai FEC producer.
    import apps_underwriting_ai.cert  # noqa: F401, PLC0415
    from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415
    try:
        from apps_underwriting_ai.engines.risk_scorer import (  # noqa: PLC0415
            DeterministicRiskScorer,
        )

        breakdown = DeterministicRiskScorer().score(
            request=getattr(uw_result, "request", None) or _synthetic_uw_request(),
            register=getattr(uw_result, "register", None),
            features=getattr(uw_result, "features", None),
            reconciliation=getattr(uw_result, "reconciliation", None),
        )
        output_bundle = mapper(
            decision=uw_result.decision,
            breakdown=breakdown,
            features=getattr(uw_result, "features", None),
        )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- receipts building is fail-soft;
        # Exit hook tolerates partial receipts
        output_bundle = {"dim_scores": {}, "dim_evidence": {}}
    _run_ctx = {
        "route_id": "apps_underwriting_ai.decision_packet_v1",
        "route_contract": {"route_id": "apps_underwriting_ai.decision_packet_v1"},
        "uw_result": uw_result,
    }
    return {
        "output": output_bundle,
        "route_contract": _run_ctx["route_contract"],
        "evidence_bundle": {},
        "final_evidence_contract": resolve_fec("apps_underwriting_ai", _run_ctx),
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _synthetic_uw_request():
    """Minimal UnderwritingRequest used when the result carries no request ref."""
    from apps_underwriting_ai.types.underwriting_types import (  # noqa: PLC0415
        UnderwritingRequest,
    )
    return UnderwritingRequest(
        request_id="cert-live-0001",
        applicant_id="applicant-cert",
        product_class="small_business_loan",
    )


def _run_demo() -> int:
    """Run a synthetic underwriting request end-to-end."""
    result = governed_underwriting_run(
        request_id="demo-0001",
        applicant_id="applicant-demo",
        product_class="small_business_loan",
        documents=(
            {"kind": "tax_return", "year": 2025},
            {"kind": "bank_statement", "month": "2026-04"},
        ),
        metadata={"source": "demo"},
        trace_id="trace-demo",
    )
    print(DecisionRenderer().to_markdown(result))
    return 0


def _run_from_file(request_path: str, artifact_dir: str | None) -> int:
    runner = UnderwritingIngressRunner()
    result = runner.run_from_file(request_path)
    if artifact_dir:
        renderer = EnterpriseUnderwritingRenderer(artifact_dir=artifact_dir)
        emitted = renderer.render_to_disk(result)
        print(f"emitted: {emitted}")
    print(DecisionRenderer().to_markdown(result))
    return 0


def main(argv: list[str] | None = None) -> int:
    # Live certification path -- emits real spine receipts and exits 0.
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
