"""Live Interview Runtime — orchestrates the full spine pipeline.

W1.1: Entrypoint purity — this module is the single delegation target
from __main__.py for live interview mode. It runs the full pipeline:
U0→L1→L0→C0/Briefing→L2→Exit.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.1
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from apps_qna.u0_intake import intake_interview_request
from apps_qna.l1_planner import plan_live_interview
from apps_qna.l0_router import select_route
from apps_qna.c0_adapter import call_c0
from apps_qna.briefing_validator import validate_briefing
from apps_qna.l2.e1_prep import prep_workspace
from apps_qna.l2.e2_valid import validate_build_inputs
from apps_qna.l2.e3_exec import execute_build
from apps_qna.exit_wiring import emit_exit_review, emit_uwg_pack_record
from apps_qna.types.spine_contracts import X3Disposition

# E4.1: Exit-eval hook wiring (plan apps-qna-deferred-e5-f7a2b1)
from apps_shared.cert import maybe_invoke_exit_eval
from apps_shared.cert.fec_producer import resolve_fec
import apps_qna.cert  # noqa: F401 — side-effect: registers FEC producer

_LOGGER = logging.getLogger(__name__)


def _load_cert_route_entry() -> dict | None:
    """Return the first route entry from apps_qna's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, which makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    from pathlib import Path

    try:
        import yaml  # noqa: PLC0415

        registry_path = Path(__file__).resolve().parent / "config" / "cert_route_registry.yaml"
        text = registry_path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 -- cert hook must never break the pipeline
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft;
        # any registry-load failure leaves the hook as a no-op and the
        # pipeline continues unaffected
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def run_live_interview(argv: list[str]) -> int:
    """Run the full spine pipeline for a live interview pack build.

    Args:
        argv: CLI arguments after the script name.

    Returns:
        0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(prog="apps_qna --interview")
    parser.add_argument("--interview", required=True, help="Interview slug")
    parser.add_argument("--briefing", default=None, help="Path to uploaded briefing")
    parser.add_argument("--company", default=None, help="Company name")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    parser.add_argument("--uwg-enabled", action="store_true", help="Enable UWG durable write of sealed manifest")
    args = parser.parse_args(argv)

    interview_slug: str = args.interview
    briefing_path: str | None = args.briefing
    dry_run: bool = args.dry_run
    uwg_enabled: bool = args.uwg_enabled

    _LOGGER.info("Live interview runtime: slug=%s briefing=%s dry_run=%s uwg=%s",
                  interview_slug, briefing_path, dry_run, uwg_enabled)

    try:
        result = _run_pipeline(
            interview_slug=interview_slug,
            briefing_path=briefing_path,
            dry_run=dry_run,
            uwg_enabled=uwg_enabled,
        )
    except Exception:  # guardian: allow-broad-except -- CLI entry point catches all pipeline failures to log and return clean exit code 1
        _LOGGER.exception("Live interview pipeline failed")
        return 1

    if result["exit_disposition"] == X3Disposition.ALLOW_FINISH:
        _LOGGER.info("Pipeline complete: %s", result["exit_disposition"].value)
        return 0

    _LOGGER.warning("Pipeline aborted: %s reason=%s",
                     result["exit_disposition"].value,
                     result.get("reason_codes", ()))
    return 1


def _run_pipeline(
    *,
    interview_slug: str,
    briefing_path: str | None = None,
    dry_run: bool = False,
    uwg_enabled: bool = False,
) -> dict[str, Any]:
    """Execute the full spine pipeline.

    Args:
        interview_slug: The interview slug to build for.
        briefing_path: Optional path to uploaded briefing.
        dry_run: If True, skip actual build and return ALLOW_FINISH.
        uwg_enabled: If True, attempt UWG durable write of sealed manifest.

    Returns:
        A dict with exit_disposition, reason_codes, route_id, manifest,
        and optionally exit_eval_result and uwg_write_result.
    """
    # U0: Intake
    validated = intake_interview_request(
        interview_slug=interview_slug,
        briefing_path=briefing_path,
    )

    # Validate briefing if provided
    briefing_contract = validate_briefing(briefing_path=briefing_path)
    has_valid_briefing = (
        briefing_contract.validation_state.value == "SUFFICIENT"
    )

    # L1: Plan
    plan = plan_live_interview(
        request_id=validated.request_id,
        has_briefing=briefing_path is not None,
        briefing_valid=has_valid_briefing,
    )

    # L0: Route
    route = select_route(
        grounding_required=plan.grounding_required,
        has_valid_briefing=has_valid_briefing,
    )

    # Evidence: C0 or Briefing
    if route.c0_required:
        evidence_contract = call_c0(
            interview_slug=interview_slug,
            route_id=route.route_id,
        )
    else:
        evidence_contract = briefing_contract.to_dict()

    if dry_run:
        return {
            "exit_disposition": X3Disposition.ALLOW_FINISH,
            "reason_codes": ("dry_run",),
            "route_id": route.route_id,
        }

    # L2: E1-E3
    workspace = prep_workspace(
        interview_slug=interview_slug,
        route_id=route.route_id,
    )
    validation = validate_build_inputs(workspace, evidence_contract=evidence_contract)
    if not validation["valid"]:
        return {
            "exit_disposition": X3Disposition.SAFE_ABSTAIN,
            "reason_codes": validation.get("errors", ()),
        }

    manifest = execute_build(workspace, evidence_contract=evidence_contract)

    # Exit
    exit_packet = emit_exit_review(
        manifest=manifest,
        evidence_contract=evidence_contract,
        build_valid=validation["valid"],
    )

    # E4.1: Invoke exit-eval hook if cert route opts in (plan apps-qna-deferred-e5-f7a2b1)
    # Fail-soft: any hook failure leaves the pipeline unaffected
    exit_eval_result = None
    try:
        cert_route_entry = _load_cert_route_entry()
        if cert_route_entry:
            run_ctx = {
                "route_id": route.route_id,
                "route_contract": {"route_id": route.route_id},
                "template_ids": [interview_slug],
                "c0_retrieval_sources": evidence_contract.get("retrieval_sources", []),
                "grounded": evidence_contract.get("grounded", False),
            }
            _receipts = {
                "output": {},
                "route_contract": run_ctx["route_contract"],
                "evidence_bundle": {},
                "final_evidence_contract": resolve_fec("apps_qna", run_ctx),
                "state_diff": {},
                "compiled_prompt_artifact": {},
            }
            exit_eval_result = maybe_invoke_exit_eval(_receipts, cert_route_entry)
    except Exception as exc:  # noqa: BLE001 -- fail-soft by design
        _LOGGER.warning("Exit-eval hook failed (fail-soft): %s", exc)

    # E4.2: Optional UWG durable write (plan apps-qna-deferred-e5-f7a2b1)
    # Fail-soft: any UWG failure is logged but does not block pipeline
    uwg_result = None
    if uwg_enabled and exit_packet.x3_disposition == X3Disposition.ALLOW_FINISH:
        try:
            uwg_result = emit_uwg_pack_record(
                manifest=manifest,
                exit_packet=exit_packet,
                enabled=True,
            )
            if uwg_result.committed:
                _LOGGER.info("UWG pack record committed: %s", uwg_result.commit_receipt_id)
            elif uwg_result.blocked:
                _LOGGER.warning("UWG pack record blocked: %s", uwg_result.reason)
            else:
                _LOGGER.debug("UWG pack record skipped: %s", uwg_result.reason)
        except Exception as exc:  # noqa: BLE001 -- fail-soft by design
            _LOGGER.warning("UWG pack record failed (fail-soft): %s", exc)

    return {
        "exit_disposition": exit_packet.x3_disposition,
        "reason_codes": exit_packet.reason_codes,
        "route_id": route.route_id,
        "manifest": exit_packet.manifest,
        "exit_eval_result": exit_eval_result,
        "uwg_write_result": uwg_result,
    }


__all__ = ["run_live_interview"]
