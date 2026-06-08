"""Distinct CLI exit codes for apps_rg operator diagnostics (Brown RCA R3.2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Section-lane / full-run process exits (``python -m apps_rg``).
EXIT_SUCCESS = 0
EXIT_GENERIC_FAILURE = 1
EXIT_CONFIG_ERROR = 2
EXIT_TOKEN_BUDGET_BLOCKED = 3
EXIT_JUDGE_REVIEW_REQUIRED = 4
EXIT_WIZARD_SENTINEL = 7

TOKEN_BUDGET_FAIL_REASONS = frozenset(
    {
        "TOKEN_BUDGET_EXCEEDED_FIRST_PASS_95PCT",
        "TOKEN_BUDGET_EXCEEDED_AFTER_TRIM",
    }
)


def exit_code_for_executive_summary_artifact(
    artifact_dir: Path,
    *,
    fault: str = "",
    x3_code: str = "",
    fail_closed_reason: str = "",
) -> int:
    """Map persisted exec-summary lane artifacts to a process exit code."""
    if fault == "temperature_range":
        return EXIT_CONFIG_ERROR
    reason = str(fail_closed_reason or "").strip()
    if artifact_dir.is_dir():
        tb = artifact_dir / "token_budget_receipt.json"
        if tb.is_file():
            import json

            try:
                doc = json.loads(tb.read_text(encoding="utf-8"))
                if isinstance(doc, dict):
                    if not reason:
                        reason = str(doc.get("fail_closed_reason") or "").strip()
                    if reason in TOKEN_BUDGET_FAIL_REASONS or not doc.get("dispatch_allowed", True):
                        return EXIT_TOKEN_BUDGET_BLOCKED
            except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
    elif reason in TOKEN_BUDGET_FAIL_REASONS:
        return EXIT_TOKEN_BUDGET_BLOCKED
    code = str(x3_code or "").strip()
    if not code and artifact_dir.is_dir():
        x3p = artifact_dir / "x3_disposition.json"
        if x3p.is_file():
            import json

            try:
                doc = json.loads(x3p.read_text(encoding="utf-8"))
                if isinstance(doc, dict):
                    code = str(doc.get("x3_code") or "").strip()
            except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
    if code == "X3_REVIEW_JUDGE_SOFT_FAIL":
        return EXIT_JUDGE_REVIEW_REQUIRED
    if fault:
        return EXIT_GENERIC_FAILURE
    return EXIT_SUCCESS


def exit_code_from_whole_run_result(result: Any) -> int:
    """Derive the integrated *whole-run* process exit code (``python -m apps_rg`` with no --section).

    Unlike a standalone lane, a whole-run failure MUST NEVER collapse to ``EXIT_SUCCESS``
    just because one section's local artifact happens to lack a fault marker. The prior
    inline path delegated the whole-run code to ``exit_code_for_executive_summary_artifact``,
    which returns ``EXIT_SUCCESS`` for an ``X3_BLOCK`` exec-summary artifact that carries no
    temperature fault / token-budget receipt / judge soft-fail — so an all-lanes-blocked run
    masked to exit 0 (gap G4, plan apps-rg-e2e-gap-remediation-7e2d9c).

    Contract: ``EXIT_SUCCESS`` requires the run to report ``exit_status == "success"`` AND
    ``outcome_authorized``. Otherwise the code is non-zero, refined to a more specific reason
    where one is observable (token budget, judge soft-fail), defaulting to
    ``EXIT_GENERIC_FAILURE``.
    """
    if not isinstance(result, dict):
        return EXIT_GENERIC_FAILURE
    status = str(result.get("exit_status") or "unknown")
    authorized = bool(result.get("outcome_authorized"))
    if status == "success" and authorized:
        return EXIT_SUCCESS
    # Failure path: pick the most specific non-zero code; never downgrade to EXIT_SUCCESS.
    if str(result.get("token_budget_operator_message") or "").strip():
        return EXIT_TOKEN_BUDGET_BLOCKED
    ad = str(result.get("artifact_dir") or "").strip()
    if ad:
        es_ad = Path(ad) / "lanes" / "executive_summary"
        if es_ad.is_dir():
            refined = exit_code_for_executive_summary_artifact(es_ad)
            # Only adopt the refinement when it is itself a failure code. A whole-run
            # failure must not be silenced by a section artifact that looks locally clean.
            if refined != EXIT_SUCCESS:
                return refined
    x3 = str(result.get("x3_disposition") or "")
    if "JUDGE_SOFT_FAIL" in x3:
        return EXIT_JUDGE_REVIEW_REQUIRED
    return EXIT_GENERIC_FAILURE


def exit_code_from_lane_result(result: dict[str, Any], *, section_id: str) -> int:
    """Derive exit code from a section runner result dict."""
    if str(section_id or "").strip().lower() != "executive_summary":
        status = str(result.get("exit_status") or "unknown")
        authorized = bool(result.get("outcome_authorized"))
        if status == "success" and authorized:
            return EXIT_SUCCESS
        return EXIT_GENERIC_FAILURE
    ad_raw = str(result.get("artifact_dir") or "").strip()
    if ad_raw:
        return exit_code_for_executive_summary_artifact(
            Path(ad_raw),
            fault=str(result.get("fault") or ""),
            x3_code=str(result.get("x3_disposition") or ""),
        )
    if str(result.get("token_budget_operator_message") or "").strip():
        return EXIT_TOKEN_BUDGET_BLOCKED
    status = str(result.get("exit_status") or "unknown")
    authorized = bool(result.get("outcome_authorized"))
    if status == "success" and authorized:
        return EXIT_SUCCESS
    x3 = str(result.get("x3_disposition") or "")
    if x3 == "X3_REVIEW_JUDGE_SOFT_FAIL":
        return EXIT_JUDGE_REVIEW_REQUIRED
    return EXIT_GENERIC_FAILURE


__all__ = [
    "EXIT_CONFIG_ERROR",
    "EXIT_GENERIC_FAILURE",
    "EXIT_JUDGE_REVIEW_REQUIRED",
    "EXIT_SUCCESS",
    "EXIT_TOKEN_BUDGET_BLOCKED",
    "EXIT_WIZARD_SENTINEL",
    "TOKEN_BUDGET_FAIL_REASONS",
    "exit_code_for_executive_summary_artifact",
    "exit_code_from_lane_result",
    "exit_code_from_whole_run_result",
]
