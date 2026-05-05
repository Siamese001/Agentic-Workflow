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
from apps_qna.exit_wiring import emit_exit_review
from apps_qna.types.spine_contracts import X3Disposition

_LOGGER = logging.getLogger(__name__)


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
    args = parser.parse_args(argv)

    interview_slug: str = args.interview
    briefing_path: str | None = args.briefing
    dry_run: bool = args.dry_run

    _LOGGER.info("Live interview runtime: slug=%s briefing=%s dry_run=%s",
                  interview_slug, briefing_path, dry_run)

    try:
        result = _run_pipeline(
            interview_slug=interview_slug,
            briefing_path=briefing_path,
            dry_run=dry_run,
        )
    except Exception:
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
) -> dict[str, Any]:
    """Execute the full spine pipeline.

    Returns a dict with exit_disposition and reason_codes.
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

    return {
        "exit_disposition": exit_packet.x3_disposition,
        "reason_codes": exit_packet.reason_codes,
        "route_id": route.route_id,
        "manifest": exit_packet.manifest,
    }


__all__ = ["run_live_interview"]
