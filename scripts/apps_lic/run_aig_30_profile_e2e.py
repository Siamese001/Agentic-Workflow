"""Reusable apps_lic AIG 30-profile E2E artifact runner.

This runner replays the committed AIG 30 fixture through deterministic W0/W4
acceptance and artifact shaping. It does not scrape, call providers, or claim
fake judge artifacts are live GPT proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_lic.engines.e2e_acceptance import (  # noqa: E402
    ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
    ACCEPTANCE_MODE_STRICT_TARGET_FIT,
    ACCEPTANCE_MODES,
    TARGET_ELIGIBLE,
    TARGET_NOT_TARGETABLE,
    evaluate_e2e_acceptance,
)
from apps_lic.engines.blocked_artifact_ux import (  # noqa: E402
    apply_blocked_artifact_ux,
    blocked_profile_report_lines,
    build_blocked_ux_summary,
    internal_blocked_draft_appendix,
)
from apps_lic.engines.governed_opportunity_ingestion import (  # noqa: E402
    C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS,
)
from apps_lic.engines.message_quality import (  # noqa: E402
    apply_message_quality_variants,
    validate_message_quality,
)
from apps_lic.engines.validation_exit import (  # noqa: E402
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    EXIT_CLEAR_DRAFT,
    INDEPENDENT_JUDGE,
    MODIFIER_PROVIDER_BACKED_GENERATION,
    MODIFIER_SIMILARITY_GATE_FLAGGED,
    required_x1d_judge_ids_for_context,
)
from apps_lic.engines.x1d_preflight import (  # noqa: E402
    X1D_MODE_FAKE,
    X1D_MODE_LIVE,
    X1D_MODE_UNAVAILABLE_EXPECTED,
    run_gpt_x1d_preflight,
)


RUN_ID = "e2e_aig_30_linkedin_profiles_20260608"
FIXED_GENERATED_AT = "2026-06-08T00:00:00+00:00"
DEFAULT_FIXTURE_PATH = REPO_ROOT / "tests" / "apps_lic" / "fixtures" / "aig_30_profiles.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "artifacts" / "apps_lic" / "e2e_aig_30_profile_w4"
FINAL_RETEST_MATRIX_ARTIFACT = "final_retest_matrix.json"
REQUIRED_ARTIFACTS = (
    "summary.json",
    "results.json",
    "messages_clear_drafts.md",
    "blocked_profiles.md",
    "internal_blocked_draft_appendix.md",
    "judge_receipts.json",
    "c0_readiness.json",
    FINAL_RETEST_MATRIX_ARTIFACT,
)


def _sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _load_fixture(path: Path) -> tuple[Mapping[str, Any], tuple[dict[str, Any], ...]]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    rows = tuple(dict(row) for row in fixture.get("profiles") or fixture.get("rows") or ())
    if fixture.get("schema_version") != "apps_lic.aig_30_profiles_fixture.v1":
        raise ValueError(f"Unsupported fixture schema: {fixture.get('schema_version')}")
    if len(rows) != 30:
        raise ValueError(f"AIG 30 fixture must contain 30 profiles, got {len(rows)}")
    return fixture, rows


def _blocked_target_eligibility(row: Mapping[str, Any]) -> str:
    if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT:
        return TARGET_ELIGIBLE
    return TARGET_NOT_TARGETABLE


def _normalize_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        materialized = dict(row)
        materialized.setdefault("profile_id", materialized.get("id"))
        materialized.setdefault("target_eligibility", _blocked_target_eligibility(materialized))
        materialized.setdefault("alternate_message_mode", "")
        materialized.setdefault("included_in_all_clear", True)
        materialized.setdefault("x1d_overrode_x2_or_c0", False)
        materialized.setdefault("sc_escalated_to_compensate_missing_evidence", False)
        normalized.append(materialized)
    return tuple(normalized)


def _apply_w6_judge_policy(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    policy_rows: list[dict[str, Any]] = []
    for row in rows:
        materialized = dict(row)
        if _clean(materialized.get("exit_disposition")) != EXIT_CLEAR_DRAFT:
            materialized["x1d_required_judges"] = []
            materialized["x1d_depth"] = 0
            materialized["x1d_policy_status"] = "blocked_rows_do_not_receive_judge_receipts"
            policy_rows.append(materialized)
            continue
        modifiers = {
            MODIFIER_PROVIDER_BACKED_GENERATION: bool(
                materialized.get("provider_backed_generation_enabled")
            ),
            MODIFIER_SIMILARITY_GATE_FLAGGED: bool(materialized.get("similarity_gate_flagged")),
        }
        required_judges = required_x1d_judge_ids_for_context(
            recipient_class=_clean(materialized.get("derived_class")),
            message_type=_clean(materialized.get("message_type")),
            modifiers=modifiers,
            proof_ids=materialized.get("claims_used") or (),
        )
        materialized["x1d_required_judges"] = list(required_judges)
        materialized["x1d_depth"] = len(required_judges)
        materialized["x1d_policy_status"] = "w6_policy_resolved"
        policy_rows.append(materialized)
    return tuple(policy_rows)


def _judge_preflight_packet(x1d_mode: str) -> dict[str, Any]:
    if x1d_mode == X1D_MODE_FAKE:
        return {
            "schema_version": "apps_lic.x1d_mode_preflight.v1",
            "mode": X1D_MODE_FAKE,
            "preflight_status": "FAKE_FIXTURE_MODE",
            "availability_status": "unavailable",
            "clearance_allowed": False,
            "live_claude_proof": False,
            "reason": "Fake mode is deterministic fixture replay only and cannot prove live GPT clearance.",
        }
    receipt = run_gpt_x1d_preflight(mode=x1d_mode)
    packet = receipt.to_packet()
    packet["live_claude_proof"] = bool(
        packet.get("preflight_status") == "CLAUDE_X1D_PREFLIGHT_READY"
        and packet.get("clearance_allowed") is True
    )
    return packet


def _judge_receipt_for_row(row: Mapping[str, Any], *, x1d_mode: str, judge_id: str) -> dict[str, Any]:
    rubric_passed = _clean(row.get("x1d_status")) == "X1D_VALIDATION_PASS"
    provider = DEFAULT_X1D_JUDGE_PROVIDER if x1d_mode == X1D_MODE_LIVE else "fixture"
    model = DEFAULT_X1D_JUDGE_MODEL if x1d_mode == X1D_MODE_LIVE else "Claude Sonnet 4.6-style fixture"
    availability = "unavailable" if x1d_mode != X1D_MODE_LIVE else "live_mode_not_run_by_fixture"
    raw_digest = _sha256(
        {
            "profile_id": row.get("id"),
            "judge_id": judge_id,
            "mode": x1d_mode,
            "rubric_passed": rubric_passed,
        }
    )
    return {
        "schema_version": "apps_lic.x1d_judge_receipt.v1",
        "profile_id": row.get("id"),
        "judge_id": judge_id,
        "provider": provider,
        "model": model,
        "score": 0.95 if rubric_passed else 0.0,
        "threshold": 0.86,
        "rubric_passed": rubric_passed,
        "passed": False,
        "availability_status": availability,
        "independence_status": INDEPENDENT_JUDGE if x1d_mode == X1D_MODE_LIVE else "not_live_fixture",
        "transport_provenance": "fake_fixture_transport" if x1d_mode == X1D_MODE_FAKE else x1d_mode,
        "transport_provider": "",
        "transport_call_id": "",
        "raw_response_digest": raw_digest,
        "issues": [] if rubric_passed else ["fixture_rubric_failed"],
        "required_repairs": [] if rubric_passed else ["repair_required_before_review"],
        "clearance": "fail",
        "live_claude_proof": False,
        "clearance_eligible": False,
        "normalized_result_contract": {
            "judge_id": judge_id,
            "model": model,
            "provider": provider,
            "score": 0.95 if rubric_passed else 0.0,
            "threshold": 0.86,
            "passed": False,
            "availability_status": availability,
            "independence_status": INDEPENDENT_JUDGE if x1d_mode == X1D_MODE_LIVE else "not_live_fixture",
            "transport_provenance": "fake_fixture_transport" if x1d_mode == X1D_MODE_FAKE else x1d_mode,
            "transport_provider": "",
            "transport_call_id": "",
            "raw_response_digest": raw_digest,
            "issues": [] if rubric_passed else ["fixture_rubric_failed"],
            "required_repairs": [] if rubric_passed else ["repair_required_before_review"],
            "clearance": "fail",
        },
        "note": "Deterministic fixture receipt only; not accepted by W1 live GPT Exit clearance.",
    }


def _build_judge_receipts(rows: Iterable[Mapping[str, Any]], *, x1d_mode: str) -> dict[str, Any]:
    row_receipts: list[dict[str, Any]] = []
    for row in rows:
        for judge_id in row.get("x1d_required_judges") or ():
            row_receipts.append(_judge_receipt_for_row(row, x1d_mode=x1d_mode, judge_id=judge_id))
    return {
        "schema_version": "apps_lic.aig_30_judge_receipts.v1",
        "run_id": RUN_ID,
        "x1d_mode": x1d_mode,
        "preflight": _judge_preflight_packet(x1d_mode),
        "live_claude_proof": False,
        "receipt_count": len(row_receipts),
        "receipts": row_receipts,
    }


def _source_snapshot_ids(profile_id: str, count: int) -> list[str]:
    return [f"{profile_id}:source_snapshot:{index + 1}" for index in range(max(0, count))]


def _build_c0_readiness(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    readiness_rows: list[dict[str, Any]] = []
    for row in rows:
        profile_id = _clean(row.get("id"))
        source_count = int(row.get("source_snapshot_count") or 0)
        readiness_rows.append(
            {
                "profile_id": profile_id,
                "status": row.get("ingestion_status") or "C0_READY",
                "ready": row.get("ingestion_status", "C0_READY") == "C0_READY",
                "source_count": source_count,
                "vector_collection_names": list(C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS),
                "source_snapshot_ids": _source_snapshot_ids(profile_id, source_count),
            }
        )
    return {
        "schema_version": "apps_lic.aig_30_c0_readiness.v1",
        "run_id": RUN_ID,
        "profile_count": len(readiness_rows),
        "ready_count": sum(1 for row in readiness_rows if row["ready"]),
        "rows": readiness_rows,
    }


def _build_judge_policy_summary(
    rows: Iterable[Mapping[str, Any]],
    judge_receipts: Mapping[str, Any],
) -> dict[str, Any]:
    clear_rows = [
        row for row in rows if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT
    ]
    receipts_by_profile: dict[str, set[str]] = {}
    for receipt in judge_receipts.get("receipts") or ():
        receipts_by_profile.setdefault(_clean(receipt.get("profile_id")), set()).add(
            _clean(receipt.get("judge_id"))
        )
    missing: list[dict[str, Any]] = []
    ceo_c_level_clear_count = 0
    ceo_c_level_two_judge_count = 0
    for row in clear_rows:
        profile_id = _clean(row.get("id"))
        required = set(_clean(item) for item in row.get("x1d_required_judges") or ())
        supplied = receipts_by_profile.get(profile_id, set())
        if missing_judges := sorted(required - supplied):
            missing.append({"profile_id": profile_id, "missing_judge_ids": missing_judges})
        if _clean(row.get("derived_class")) in {"CEO", "C_LEVEL"}:
            ceo_c_level_clear_count += 1
            if len(required) == 2:
                ceo_c_level_two_judge_count += 1
    return {
        "schema_version": "apps_lic.w6_judge_policy_summary.v1",
        "clear_draft_count": len(clear_rows),
        "required_judge_count": sum(
            len(row.get("x1d_required_judges") or ()) for row in clear_rows
        ),
        "receipt_count": judge_receipts.get("receipt_count", 0),
        "missing_required_judge_receipts": missing,
        "all_clear_drafts_have_required_receipts": not missing,
        "ceo_c_level_clear_count": ceo_c_level_clear_count,
        "ceo_c_level_two_judge_count": ceo_c_level_two_judge_count,
        "ceo_c_level_all_have_two_judges": ceo_c_level_clear_count == ceo_c_level_two_judge_count,
    }


def _acceptance_profile_ids(acceptance_report: Mapping[str, Any], status: str) -> list[str]:
    return sorted(
        _clean(row.get("profile_id"))
        for row in acceptance_report.get("rows") or ()
        if _clean(row.get("status")) == status
    )


def _live_candidate_receipts_ready(judge_receipts: Mapping[str, Any]) -> bool:
    receipts = list(judge_receipts.get("receipts") or ())
    return bool(receipts) and all(
        receipt.get("passed") is True
        and receipt.get("live_claude_proof") is True
        and _clean(receipt.get("availability_status")) == "available"
        and _clean(receipt.get("provider")) == DEFAULT_X1D_JUDGE_PROVIDER
        and _clean(receipt.get("model")) == DEFAULT_X1D_JUDGE_MODEL
        for receipt in receipts
    )


def _build_final_retest_matrix(
    *,
    mode: str,
    x1d_mode: str,
    rows: tuple[Mapping[str, Any], ...],
    acceptance_report: Mapping[str, Any],
    judge_receipts: Mapping[str, Any],
    c0_readiness: Mapping[str, Any],
    message_quality: Mapping[str, Any],
    judge_policy: Mapping[str, Any],
    blocked_ux: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize W8 retest expectations without changing Exit acceptance."""
    preflight = dict(judge_receipts.get("preflight") or {})
    no_weakening_violations = list(acceptance_report.get("no_weakening_violations") or ())
    live_preflight_ready = bool(
        x1d_mode == X1D_MODE_LIVE
        and preflight.get("clearance_allowed") is True
        and preflight.get("live_claude_proof") is True
    )
    live_receipts_ready = _live_candidate_receipts_ready(judge_receipts)
    unavailable_judge_artifact = bool(
        x1d_mode == X1D_MODE_LIVE
        and preflight.get("availability_status") == "unavailable"
        and preflight.get("clearance_allowed") is False
        and preflight.get("live_claude_proof") is not True
    )
    strict_fake_passed = bool(
        mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT
        and x1d_mode == X1D_MODE_FAKE
        and acceptance_report.get("passed") is True
        and acceptance_report.get("profile_count") == 30
        and acceptance_report.get("clear_draft_count") == 24
        and acceptance_report.get("policy_correct_block_count") == 6
        and acceptance_report.get("unexpected_gap_count") == 0
    )
    all_clear_fake_retest_passed = bool(
        mode == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE
        and x1d_mode == X1D_MODE_FAKE
        and acceptance_report.get("passed") is False
        and acceptance_report.get("clear_draft_count") == 24
        and acceptance_report.get("remediation_required_count") == 6
        and acceptance_report.get("unexpected_gap_count") == 0
    )
    live_mode_passed = bool(
        x1d_mode == X1D_MODE_LIVE
        and (
            (live_preflight_ready and live_receipts_ready)
            or (not live_preflight_ready and unavailable_judge_artifact)
        )
    )
    invariants = {
        "no_weakening_violations_absent": not no_weakening_violations,
        "x1d_did_not_override_c0_x2_or_exit": not any(
            bool(row.get("x1d_overrode_x2_or_c0")) for row in rows
        ),
        "sc_did_not_compensate_missing_c0_evidence": not any(
            bool(row.get("sc_escalated_to_compensate_missing_evidence")) for row in rows
        ),
        "fake_mode_does_not_claim_live_claude_proof": bool(
            x1d_mode != X1D_MODE_FAKE or judge_receipts.get("live_claude_proof") is False
        ),
        "blocked_drafts_suppressed_in_product_artifacts": bool(
            blocked_ux.get("product_facing_blocked_drafts_suppressed")
        ),
    }
    invariant_passed = all(invariants.values())

    if mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT and x1d_mode == X1D_MODE_FAKE:
        result = "strict_target_fit_fake_passed" if strict_fake_passed else "failed"
        matrix_passed = strict_fake_passed and invariant_passed
    elif mode == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE and x1d_mode == X1D_MODE_FAKE:
        result = (
            "expected_remediation_required"
            if all_clear_fake_retest_passed
            else "failed"
        )
        matrix_passed = all_clear_fake_retest_passed and invariant_passed
    elif mode == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE and x1d_mode == X1D_MODE_LIVE:
        if live_preflight_ready and live_receipts_ready:
            result = "live_claude_candidate_receipts_ready"
        elif unavailable_judge_artifact:
            result = "failed_closed_unavailable_judge"
        else:
            result = "live_preflight_ready_but_candidate_receipts_missing"
        matrix_passed = live_mode_passed and invariant_passed
    else:
        result = "unsupported_w8_retest_combination"
        matrix_passed = False

    gaps: list[str] = []
    if no_weakening_violations:
        gaps.append("no_weakening_violation_detected")
    if not blocked_ux.get("product_facing_blocked_drafts_suppressed"):
        gaps.append("blocked_draft_exposed_in_product_artifact")
    if mode == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE and x1d_mode == X1D_MODE_FAKE:
        if acceptance_report.get("remediation_required_count") != 6:
            gaps.append("unexpected_all_clear_remediation_count")
    if x1d_mode == X1D_MODE_LIVE and live_preflight_ready and not live_receipts_ready:
        gaps.append("live_candidate_judge_receipts_not_wired_for_clear_drafts")

    return {
        "schema_version": "apps_lic.w8_final_retest_matrix.v1",
        "run_id": RUN_ID,
        "generated_at": FIXED_GENERATED_AT,
        "mode": mode,
        "x1d_mode": x1d_mode,
        "result": result,
        "matrix_passed": matrix_passed,
        "strict_target_fit_fake": {
            "applicable": mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT
            and x1d_mode == X1D_MODE_FAKE,
            "passed": strict_fake_passed,
            "expected_profile_count": 30,
            "actual_profile_count": acceptance_report.get("profile_count"),
            "expected_clear_draft_count": 24,
            "actual_clear_draft_count": acceptance_report.get("clear_draft_count"),
            "expected_policy_correct_block_count": 6,
            "actual_policy_correct_block_count": acceptance_report.get(
                "policy_correct_block_count"
            ),
            "unexpected_gap_count": acceptance_report.get("unexpected_gap_count"),
            "primary_blocker_counts": dict(blocked_ux.get("primary_blocker_counts") or {}),
        },
        "all_clear_eligible": {
            "applicable": mode == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
            "fake_retest_passed": all_clear_fake_retest_passed,
            "generation_acceptance_passed": bool(acceptance_report.get("passed")),
            "expected_clear_only_after_remediation": True,
            "clear_draft_count": acceptance_report.get("clear_draft_count"),
            "remediation_required_count": acceptance_report.get(
                "remediation_required_count"
            ),
            "remediation_required_profile_ids": _acceptance_profile_ids(
                acceptance_report,
                "all_clear_remediation_required",
            ),
            "unexpected_gap_count": acceptance_report.get("unexpected_gap_count"),
        },
        "live_mode": {
            "applicable": x1d_mode == X1D_MODE_LIVE,
            "api_key_present": bool(preflight.get("api_key_present")),
            "preflight_status": preflight.get("preflight_status", ""),
            "availability_status": preflight.get("availability_status", ""),
            "live_preflight_ready": live_preflight_ready,
            "live_candidate_judge_receipts_ready": live_receipts_ready,
            "unavailable_judge_artifact_emitted": unavailable_judge_artifact,
            "fail_closed_without_live_candidate_receipts": bool(
                x1d_mode == X1D_MODE_LIVE
                and not live_receipts_ready
                and not judge_receipts.get("live_claude_proof")
            ),
            "passed": live_mode_passed,
        },
        "quality_and_policy": {
            "c0_ready_count": c0_readiness.get("ready_count", 0),
            "message_quality_passed": bool(message_quality.get("passed")),
            "judge_policy_required_receipts_present": bool(
                judge_policy.get("all_clear_drafts_have_required_receipts")
            ),
            "ceo_c_level_all_have_two_judges": bool(
                judge_policy.get("ceo_c_level_all_have_two_judges")
            ),
        },
        "invariants": invariants,
        "no_weakening_violations": no_weakening_violations,
        "gaps": gaps,
    }


def _summary(
    *,
    mode: str,
    x1d_mode: str,
    rows: tuple[Mapping[str, Any], ...],
    acceptance_report: Mapping[str, Any],
    judge_receipts: Mapping[str, Any],
    c0_readiness: Mapping[str, Any],
    message_quality: Mapping[str, Any],
    judge_policy: Mapping[str, Any],
    blocked_ux: Mapping[str, Any],
    final_retest_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    clear_rows = [row for row in rows if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT]
    blocked_rows = [row for row in rows if _clean(row.get("exit_disposition")) != EXIT_CLEAR_DRAFT]
    return {
        "schema_version": "apps_lic.aig_30_e2e_summary.v1",
        "run_id": RUN_ID,
        "generated_at": FIXED_GENERATED_AT,
        "mode": mode,
        "x1d_mode": x1d_mode,
        "profile_count": len(rows),
        "clear_draft_count": len(clear_rows),
        "blocked_or_review_count": len(blocked_rows),
        "blocked_or_review_ids": [row.get("id") for row in blocked_rows],
        "acceptance_passed": bool(acceptance_report.get("passed")),
        "acceptance": acceptance_report,
        "message_quality_passed": bool(message_quality.get("passed")),
        "message_quality": message_quality,
        "judge_policy_passed": bool(
            judge_policy.get("all_clear_drafts_have_required_receipts")
            and judge_policy.get("ceo_c_level_all_have_two_judges")
        ),
        "judge_policy": judge_policy,
        "blocked_ux_passed": bool(blocked_ux.get("product_facing_blocked_drafts_suppressed")),
        "blocked_ux": blocked_ux,
        "final_retest_matrix_passed": bool(final_retest_matrix.get("matrix_passed")),
        "final_retest_matrix_result": final_retest_matrix.get("result", ""),
        "final_retest_matrix": final_retest_matrix,
        "judge_receipt_count": judge_receipts.get("receipt_count", 0),
        "live_claude_proof": bool(judge_receipts.get("live_claude_proof")),
        "c0_ready_count": c0_readiness.get("ready_count", 0),
        "artifact_files": list(REQUIRED_ARTIFACTS),
    }


def _messages_clear_drafts(rows: Iterable[Mapping[str, Any]], *, mode: str, x1d_mode: str) -> str:
    lines = [
        f"# AIG 30 Clear Drafts - {mode} - {x1d_mode}",
        "",
        "Only Exit clear_draft rows are included.",
        "",
    ]
    index = 1
    for row in rows:
        if _clean(row.get("exit_disposition")) != EXIT_CLEAR_DRAFT:
            continue
        lines.extend(
            [
                f"## {index}. {row.get('name')} - {row.get('derived_class')}",
                "",
                f"Profile ID: `{row.get('id')}`",
                "",
                _clean(row.get("draft_text")),
                "",
            ]
        )
        index += 1
    return "\n".join(lines).rstrip() + "\n"


def _blocked_profiles(rows: Iterable[Mapping[str, Any]], *, mode: str, x1d_mode: str) -> str:
    lines = [
        f"# AIG 30 Blocked Profiles - {mode} - {x1d_mode}",
        "",
        "Blocked drafts are not exposed here. This artifact lists blockers only.",
        "Internal blocked draft text, when present, is isolated in `internal_blocked_draft_appendix.md` with an explicit no-send watermark.",
        "",
    ]
    index = 1
    for row in rows:
        if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT:
            continue
        failed = ", ".join(row.get("x2_failed_gates") or ()) or "n/a"
        lines.extend(
            [
                f"## {index}. {row.get('name')} - {row.get('derived_class')}",
                "",
                f"Profile ID: `{row.get('id')}`",
                f"Target eligibility: `{row.get('target_eligibility')}`",
                f"Exit disposition: `{row.get('exit_disposition')}`",
                f"Failed gates: `{failed}`",
                *blocked_profile_report_lines(row),
                "",
            ]
        )
        index += 1
    return "\n".join(lines).rstrip() + "\n"


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_aig_30_profile_e2e(
    *,
    mode: str,
    x1d_mode: str,
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run deterministic AIG 30 fixture replay and write artifact schema."""
    if mode not in ACCEPTANCE_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if x1d_mode not in {X1D_MODE_FAKE, X1D_MODE_LIVE, X1D_MODE_UNAVAILABLE_EXPECTED}:
        raise ValueError(f"Unsupported x1d-mode: {x1d_mode}")

    fixture, fixture_rows = _load_fixture(fixture_path)
    rows = apply_blocked_artifact_ux(
        _apply_w6_judge_policy(apply_message_quality_variants(_normalize_rows(fixture_rows)))
    )
    acceptance = evaluate_e2e_acceptance(
        rows,
        mode=mode,
        expected_profile_count=30,
        expected_clear_draft_count=24 if mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT else None,
        expected_policy_correct_block_count=6 if mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT else None,
    ).to_packet()
    judge_receipts = _build_judge_receipts(rows, x1d_mode=x1d_mode)
    c0_readiness = _build_c0_readiness(rows)
    message_quality = validate_message_quality(rows).to_packet()
    judge_policy = _build_judge_policy_summary(rows, judge_receipts)
    blocked_ux = build_blocked_ux_summary(rows)
    final_retest_matrix = _build_final_retest_matrix(
        mode=mode,
        x1d_mode=x1d_mode,
        rows=rows,
        acceptance_report=acceptance,
        judge_receipts=judge_receipts,
        c0_readiness=c0_readiness,
        message_quality=message_quality,
        judge_policy=judge_policy,
        blocked_ux=blocked_ux,
    )
    summary = _summary(
        mode=mode,
        x1d_mode=x1d_mode,
        rows=rows,
        acceptance_report=acceptance,
        judge_receipts=judge_receipts,
        c0_readiness=c0_readiness,
        message_quality=message_quality,
        judge_policy=judge_policy,
        blocked_ux=blocked_ux,
        final_retest_matrix=final_retest_matrix,
    )
    results = {
        "schema_version": "apps_lic.aig_30_e2e_results.v1",
        "fixture": {
            "fixture_id": fixture.get("fixture_id"),
            "fixture_path": str(fixture_path),
            "fixture_digest": _sha256(fixture),
        },
        "summary": summary,
        "acceptance": acceptance,
        "message_quality": message_quality,
        "judge_policy": judge_policy,
        "blocked_ux": blocked_ux,
        "final_retest_matrix": final_retest_matrix,
        "rows": list(rows),
    }

    target_dir = output_dir or DEFAULT_OUTPUT_ROOT / f"{mode}_{x1d_mode}"
    target_dir.mkdir(parents=True, exist_ok=True)
    _write_json(target_dir / "summary.json", summary)
    _write_json(target_dir / "results.json", results)
    _write_json(target_dir / "judge_receipts.json", judge_receipts)
    _write_json(target_dir / "c0_readiness.json", c0_readiness)
    _write_json(target_dir / FINAL_RETEST_MATRIX_ARTIFACT, final_retest_matrix)
    (target_dir / "messages_clear_drafts.md").write_text(
        _messages_clear_drafts(rows, mode=mode, x1d_mode=x1d_mode),
        encoding="utf-8",
    )
    (target_dir / "blocked_profiles.md").write_text(
        _blocked_profiles(rows, mode=mode, x1d_mode=x1d_mode),
        encoding="utf-8",
    )
    (target_dir / "internal_blocked_draft_appendix.md").write_text(
        internal_blocked_draft_appendix(rows, mode=mode, x1d_mode=x1d_mode),
        encoding="utf-8",
    )

    return {
        "output_dir": str(target_dir),
        "summary": summary,
        "artifact_files": list(REQUIRED_ARTIFACTS),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=ACCEPTANCE_MODES, default=ACCEPTANCE_MODE_STRICT_TARGET_FIT)
    parser.add_argument(
        "--x1d-mode",
        choices=(X1D_MODE_FAKE, X1D_MODE_LIVE, X1D_MODE_UNAVAILABLE_EXPECTED),
        default=X1D_MODE_FAKE,
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_aig_30_profile_e2e(
        mode=args.mode,
        x1d_mode=args.x1d_mode,
        fixture_path=args.fixture,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
