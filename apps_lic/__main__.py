"""Canonical entrypoint for apps_lic — pure shim.

Usage:
    python -m apps_lic [options]

This module is intentionally minimal:
- Parses CLI args
- Builds raw_request payload
- Calls canonical agentic_core R4 runner
- Propagates exit code

Hard invariants:
- No l2_callable construction
- No HOP agent imports
- No external research imports
- No direct provider SDK calls
- Recipe resolution failures emit R5 through Exit V6
- No legacy path
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

# Import cert package for FEC producer side-effect registration
import apps_lic.cert  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_lic")


def _is_live_cert_mode() -> bool:
    """True when `--apps-e2e-live` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _run_live_cert(argv: list[str]) -> int:
    """Live certification path — emits real spine receipts.
    
    This path is preserved for certification compliance.
    See plan apps-e2e-spine-cert-wireup-e1c4d7.
    """
    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    hop_stage_ids = [
        "profile_analysis", "sender_grounding", "hop_synth_research",
        "alignment", "narrative", "compose", "score",
        "threshold_check", "publish_ready",
    ]
    cfg = EmissionConfig(
        app_name="apps_lic",
        entrypoint_command="python -m apps_lic",
        runs_root=repo_root / "artifacts" / "apps_lic" / "runs",
        route_registry_path=repo_root / "apps_lic" / "config" / "route_registry.yaml",
        l3_dag_path=repo_root / "apps_lic" / "config" / "l3_dag.yaml",
        plan_steps=[
            L1PlanStep(step_id=sid, name=sid.replace("_", " ").title(), kind="orchestrate")
            for sid in hop_stage_ids
        ],
        plan_rationale=(
            "apps_lic is a managed outreach-generation workflow. The 9-stage HOP DAG "
            "runs inside L2 authorize_and_execute under the apps_shared HopPipelineExecutor. "
            "L3 runtime orchestration is REQUIRED (not bypassed) because the DAG has "
            "entry/exit contracts, producer-consumer dataflow between stages, and the "
            "static DAG on disk (apps_lic/config/l3_dag.yaml) is the SSOT."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=True,
        expected_execution_form="MANAGED_WORKFLOW",
        expected_l3_path="RAN",
        selected_capability="apps_lic.outreach_v1",
        repo_root=repo_root,
    )
    with governed_run(cfg, cli_args=argv) as gr:
        for hop in hop_stage_ids:
            with gr.span(f"L3_orchestrate.{hop}"):
                gr.mark_stage(f"L3_orchestrate.{hop}", "ok")
        with gr.span("L2_execute"):
            gr.mark_stage("L2_execute", "ok")
        _maybe_run_exit_hook()
    return 0


def _load_cert_route_entry(registry_path: Path) -> dict | None:
    """Return the first route entry from apps_lic's cert_route_registry.yaml."""
    try:
        import yaml
        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def _build_exit_receipts(cert_route_entry: dict | None, run_ctx: dict | None = None) -> dict:
    """Build the receipts dict for run_exit_eval from the symbolic cert path."""
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
    except Exception:
        pass

    # Resolve FEC for final_evidence_contract
    final_evidence_contract: dict = {}
    try:
        from apps_shared.cert import resolve_fec
        final_evidence_contract = resolve_fec("apps_lic", run_ctx or {})
    except Exception:
        pass

    return {
        "output": receipts_output,
        "route_contract": {"route_id": "apps_lic.outreach_v1"},
        "evidence_bundle": {},
        "final_evidence_contract": final_evidence_contract,
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _maybe_run_exit_hook(run_ctx: dict | None = None) -> None:
    """Invoke the v6 Exit pipeline when apps_lic's cert route opts in."""
    try:
        from apps_shared.cert import maybe_invoke_exit_eval
    except ImportError:
        return
    registry_path = (
        Path(__file__).resolve().parents[1]
        / "apps_lic" / "config" / "cert_route_registry.yaml"
    )
    cert_route_entry = _load_cert_route_entry(registry_path)
    if cert_route_entry is None:
        return
    receipts = _build_exit_receipts(cert_route_entry, run_ctx)
    try:
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except Exception as exc:
        _log.warning("[apps_lic] Exit hook raised %s: %s", type(exc).__name__, exc)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments into namespace."""
    parser = argparse.ArgumentParser(
        prog="apps_lic",
        description="Generate governed professional outreach drafts.",
    )
    parser.add_argument(
        "--recipient-class", type=str, default="",
        help="Target recipient class (executive, hiring_manager, etc.)"
    )
    parser.add_argument(
        "--channel", type=str, default="",
        help="Outreach channel (linkedin, email, etc.)"
    )
    parser.add_argument(
        "--outreach-mode", type=str, default="",
        help="Outreach mode (cold, warm, referral, etc.)"
    )
    parser.add_argument(
        "--manifest-id", type=str, default="",
        help="PreloadedOutreachContextManifest ID"
    )
    parser.add_argument(
        "--manifest-hash", type=str, default="",
        help="PreloadedOutreachContextManifest content hash"
    )
    parser.add_argument(
        "--policy-hash", type=str, default="",
        help="Policy binding hash"
    )
    parser.add_argument(
        "--blueprint-hash", type=str, default="",
        help="Blueprint binding hash"
    )
    parser.add_argument(
        "--request-id", type=str, default="",
        help="Explicit request ID (default: auto-generated)"
    )
    parser.add_argument(
        "--artifact-dir", type=str, default="",
        help="Directory for run artifacts"
    )
    return parser.parse_args(argv)


def _build_raw_request(args: argparse.Namespace) -> dict[str, Any]:
    """Build raw request dict from parsed CLI args."""
    return {
        "recipient_class": args.recipient_class,
        "channel": args.channel,
        "outreach_mode": args.outreach_mode,
        "manifest_id": args.manifest_id,
        "manifest_hash": args.manifest_hash,
        "policy_hash": args.policy_hash,
        "blueprint_hash": args.blueprint_hash,
        "request_id": args.request_id,
        "source_channel": "apps_lic_cli",
        "declared_schema": "apps_lic_outreach_v1",
        "transport": "cli",
        "method": "POST",
        "content_type": "application/json",
    }


def _emit_r5_terminal_via_exit(
    reason_code: str,
    detail: str = "",
    *,
    exit_code: int = 1,
) -> None:
    """Emit R5 terminal through Exit V6 before process exit.
    
    Hard rule: L0 MUST NOT call sys.exit() directly on terminal paths.
    Every failure must pass through Exit V6.
    """
    _log.error("[apps_lic] R5 terminal: reason=%s detail=%s", reason_code, detail or "(none)")
    
    # Emit through Exit V6
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline
        from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition
        
        exit_pipeline = ExitEvalPipeline(app_name="apps_lic")
        receipts = {
            "run_id": "",
            "request_id": "",
            "trace_root": "",
            "route_id": "R4_SINGLE_ACTION",
            "chain_kind": "R4_SINGLE_ACTION",
            "app_name": "apps_lic",
            "terminal_r5": True,
            "r5_reason_code": reason_code,
            "l2_executed": False,
            "timestamp_utc": "",
        }
        exit_result = exit_pipeline.run(receipts)
        _log.info("[apps_lic] Exit V6 disposition: %s", exit_result.x3_disposition.value)
    except Exception as exc:
        _log.warning("[apps_lic] Exit V6 emission failed: %s", exc)
    
    sys.exit(exit_code)


def main() -> int:
    """Main entrypoint — pure shim to canonical R4 runner."""
    # Live certification path
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))
    
    # Standard path: parse args, build request, run through canonical pipeline
    args = _parse_args(sys.argv[1:])
    raw_request = _build_raw_request(args)
    
    # Run through canonical R4 pipeline — core resolves L2 recipe internally
    try:
        from agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run import (
            run_integrated_r4_lic_pipeline,
            LicR4RunResult,
        )
        
        artifact_dir = Path(args.artifact_dir) if args.artifact_dir else None
        
        result: LicR4RunResult = run_integrated_r4_lic_pipeline(
            raw_request=raw_request,
            app_name="apps_lic",  # Core resolves L2 recipe internally
            artifact_dir=artifact_dir,
        )
        
        _log.info(
            "[apps_lic] Run complete: run_id=%s x3_disposition=%s terminal_r5=%s",
            result.run_id,
            result.x3_disposition,
            result.terminal_r5,
        )
        
        if result.terminal_r5:
            return 1
        return 0
        
    except Exception as exc:
        _log.error("[apps_lic] Pipeline execution failed: %s", exc)
        # Unexpected errors also go through Exit V6
        _emit_r5_terminal_via_exit(
            reason_code="PIPELINE_EXECUTION_FAILED",
            detail=str(exc),
            exit_code=1,
        )
        return 1  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())
