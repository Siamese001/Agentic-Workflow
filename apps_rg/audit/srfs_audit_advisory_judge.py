"""apps_rg-local advisory review of completed SRFS audit reports (no shared judge infra)."""

from __future__ import annotations

import os
from typing import Any

from apps_rg.audit.srfs_receipt_aggregator import FORBIDDEN_AFFIRMATIVE_PHRASES, PROOF_LEVEL

ADVISORY_SCOPE = "apps_rg_local_heuristic_audit_review_v1"
LIVE_ENV_GATE = "APPS_RG_SRFS_ADVISORY_JUDGE_LIVE"


def _collect_strings(obj: object, *, skip_keys: frozenset[str] | None = None) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if skip_keys and k in skip_keys:
                continue
            out.extend(_collect_strings(v, skip_keys=skip_keys))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(_collect_strings(item, skip_keys=skip_keys))
    elif isinstance(obj, str):
        out.append(("", obj))
    return out


def _forbidden_outside_non_claims(report: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for path, text in _collect_strings(report, skip_keys=frozenset({"explicit_non_claims"})):
        lower = text.lower()
        for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES:
            if phrase in lower and "does not assert" not in lower:
                findings.append(f"forbidden_language_risk:{phrase}")
    return findings


def _heuristic_mock_review(report: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    expected = report.get("expected_sections") or []
    section_results = report.get("section_results") or {}
    observed = report.get("observed_sections") or []

    if report.get("proof_level") != PROOF_LEVEL:
        findings.append("proof_level_not_canonical")

    decisive = str(report.get("decisive_reason") or "").strip()
    if len(decisive) < 10:
        findings.append("decisive_reason_too_short_for_human_audit")

    if len(expected) != 7:
        findings.append("expected_sections_count_not_seven")

    for sid in expected:
        if sid not in section_results:
            findings.append(f"section_matrix_missing:{sid}")

    if set(observed) != set(section_results.keys()) and observed:
        findings.append("observed_sections_inconsistent_with_section_results")

    non_claims = report.get("explicit_non_claims") or []
    if len(non_claims) < 6:
        findings.append("explicit_non_claims_insufficient")

    findings.extend(_forbidden_outside_non_claims(report))

    det = report.get("status")
    if det == "PASS" and report.get("missing_sections"):
        findings.append("internal_inconsistency:deterministic_pass_with_missing_sections")

    if any(f.startswith("forbidden_language_risk:") for f in findings):
        status = "FAIL"
    elif findings:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "enabled": True,
        "status": status,
        "mocked_or_live": "mocked",
        "can_change_deterministic_status": False,
        "findings": findings,
        "limitations": [
            "Mock heuristic advisory review only; non-certifying audit commentary.",
            "Does not invoke shared judge infrastructure or LLM providers.",
            "Does not override deterministic PASS/WARN/FAIL.",
        ],
        "scope": ADVISORY_SCOPE,
    }


def _not_run_block(*, limitations: list[str]) -> dict[str, Any]:
    return {
        "enabled": False,
        "status": "NOT_RUN",
        "mocked_or_live": "not_run",
        "can_change_deterministic_status": False,
        "findings": [],
        "limitations": limitations,
        "scope": ADVISORY_SCOPE,
    }


def build_advisory_judge_review(
    report: dict[str, Any],
    *,
    enable: bool,
    mock: bool,
) -> dict[str, Any]:
    """Build advisory review block without mutating deterministic status."""
    if not enable:
        return _not_run_block(
            limitations=["Advisory review disabled (default). Deterministic aggregator only."],
        )
    if mock:
        return _heuristic_mock_review(report)
    if os.environ.get(LIVE_ENV_GATE) == "1":
        return _not_run_block(
            limitations=[
                "Live advisory LLM judge not wired in W6; set --judge-mock for local heuristic review.",
                f"{LIVE_ENV_GATE}=1 ignored without apps_rg-local live adapter.",
            ],
        )
    return _not_run_block(
        limitations=[
            "Advisory review requested without --judge-mock; live path not implemented.",
            "Use --enable-advisory-judge --judge-mock for non-certifying heuristic commentary.",
        ],
    )


def attach_advisory_judge_review(
    report: dict[str, Any],
    *,
    enable: bool,
    mock: bool,
) -> dict[str, Any]:
    """Attach advisory block; deterministic ``status`` must remain unchanged."""
    deterministic_status = report["status"]
    report["advisory_judge_review"] = build_advisory_judge_review(report, enable=enable, mock=mock)
    if report["status"] != deterministic_status:
        raise RuntimeError("advisory review mutated deterministic status")
    return report
