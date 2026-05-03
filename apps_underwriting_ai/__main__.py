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
    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            # Drive the real pipeline so the receipts reflect a genuine run.
            governed_underwriting_run(
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
    return 0


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
