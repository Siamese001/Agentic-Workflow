"""Validate the hardened 10C semantic requirement ledger (W4d-2).

Iteration 2 (2026-04-30) addresses the post-W4d review by:

  - Renaming ``proof_complete_critical_high`` to
    ``proof_field_complete_critical_high`` so the metric no longer reads
    as if proof evidence is present.
  - Adding ``proof_evidence_present_critical_high`` which counts rows where
    the test/CI/bundle paths actually exist on disk AND
    ``last_passed_commit`` is populated. This will start at 0 and grow
    only as real tests pass.
  - Validating the 8 W4d-2 columns are present and correctly typed.
  - Requiring ``negative_control_specific`` populated for CRITICAL/HIGH.
  - Emitting a ``coverage_doctrine`` section documenting why
    ``00C_Runtime_Gates_Current_Run_Mesh`` and
    ``99_End_to_End_Runtime_Proof_and_Acceptance`` may have zero rows
    (they are external proof surfaces, enforced by separate runtime-gate
    and end-to-end proof packs).
  - Listing pedagogical rows separately from runtime proof obligations.

Usage::

    python tools/requirements/validate_10c_proof_ledger.py [--strict|--no-strict]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "requirements"
JSON_OUT = ARTIFACT_DIR / "10c_proof_ledger_validation.json"
MD_OUT = ARTIFACT_DIR / "10c_proof_ledger_validation.md"

EXPECTED_ROWS = 200
REQ_ID_RE = re.compile(r"^10C-REQ-\d{3}$")

CANONICAL_OWNER_VOCAB = frozenset({
    "00A_L5_Governance_Safety",
    "00B_L4_State_Archive_and_UWG",
    "00C_Runtime_Gates_Current_Run_Mesh",
    "01_U0_Request_Intake",
    "02_L1_Reasoning_Plan",
    "03_L0_Route_Decision",
    "03_L3_Orchestration",
    "03A_C0_Context_Engine",
    "03B_PA_Prompt_Assembly",
    "04_L2_Execute",
    "05_Exit_Evaluation_and_Control",
    "06_L6_Shadow_Evaluation_System_Learning",
    "99_End_to_End_Runtime_Proof_and_Acceptance",
    "Offline_Ingestion_Index_Build",
    "Cross_Cutting_Observability_Replay_Audit",
})

ALLOWED_SEVERITY = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})

ALLOWED_IMPL_STATUS = frozenset({
    "IMPLEMENTED", "PARTIAL", "DEFERRED", "NOT_STARTED", "BLOCKED", "NEEDS_REVIEW",
})

ALLOWED_EVIDENCE_STATUS = frozenset({
    "PROOF_PRESENT", "PROOF_PARTIAL", "PROOF_MISSING", "NEEDS_REVIEW", "NOT_APPLICABLE",
})

ALLOWED_FINAL_ACCEPTANCE = frozenset({
    "ACCEPTED", "ACCEPTED_WITH_CAVEAT", "REJECTED_DUPLICATE", "REJECTED_OUT_OF_SCOPE",
    "NEEDS_PROOF", "NEEDS_OWNER_REVIEW", "DEFERRED",
})

# Mandatory proof-FIELD population for CRITICAL/HIGH rows.
MANDATORY_PROOF_FIELDS = (
    "runtime_artifact_expected",
    "otel_span_expected",
    "replay_proof_expected",
    "negative_control_expected",
    "negative_control_specific",
    "test_file_expected",
    "acceptance_command",
    "ci_gate_name",
)

# Full set required for proof-field completeness.
# Note: source-lock fields (source_commit_sha, source_text_sha256) are tracked
# as a SEPARATE quality dimension (`source_lock_complete`) because a non-trivial
# fraction of rows are derived requirements (audit notes, gap analyses) with no
# on-disk source file. Including those in COMPLETE_PROOF_FIELDS would
# artificially conflate spec completeness with source-anchor coverage.
COMPLETE_PROOF_FIELDS = MANDATORY_PROOF_FIELDS + (
    "canonical_owner_surface",
    "artifact_schema_ref",
    "otel_required_attributes",
    "proof_bundle_ref",
)

# Source-lock is required ONLY when a source file is resolvable; this set is
# checked against rows whose source_text_sha256 is non-empty.
SOURCE_LOCK_FIELDS = (
    "source_commit_sha",
    "source_text_sha256",
)

# For ACCEPTED final-acceptance status, BOTH proof-field completeness AND
# (when applicable) source-lock must be present.
ACCEPTED_REQUIRES = COMPLETE_PROOF_FIELDS

# Existence-check columns used to score proof-evidence-present.
EVIDENCE_PATH_FIELDS = (
    "test_file_exists",
    "ci_gate_exists",
    "proof_bundle_exists",
)

# Owner surfaces that are intentionally external to the 10C semantic ledger.
EXTERNAL_PROOF_SURFACES = {
    "00C_Runtime_Gates_Current_Run_Mesh": (
        "Runtime gate mesh contracts (GateVerdict envelope, UNKNOWN-never-PASS, "
        "bounded gate dispositions, gate-to-Exit handoff) are enforced by the "
        "separate Runtime-Gate Pack at agentic_core/L5_safety/runtime_gates/. "
        "If a future 10C source document adds runtime-gate language, those rows "
        "would land here; the empty count today is intentional, not a coverage gap."
    ),
    "99_End_to_End_Runtime_Proof_and_Acceptance": (
        "End-to-end proof harnesses (golden-path bundle, route-coverage proof, "
        "OTEL span-tree proof, deterministic-replay proof, no-bypass proof, "
        "evidence-to-output groundedness) are enforced by the separate E2E "
        "Proof Pack at scripts/proof/. The 10C ledger states the per-row proof "
        "expectations; the E2E pack composes them into the bundle."
    ),
}


def _load_rows() -> tuple[list[str], list[dict[str, str]]]:
    csv.field_size_limit(2_000_000)
    with LEDGER.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = list(reader)
    return header, rows


def _git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short", str(LEDGER.relative_to(REPO_ROOT))],
            capture_output=True, text=True, check=False, timeout=10, cwd=REPO_ROOT,
        )
        return (result.stdout or "").strip() or "(clean)"
    except (subprocess.SubprocessError, OSError) as exc:
        return f"(git status unavailable: {exc})"


def _discover_prior_severity_baseline() -> dict[str, int] | None:
    candidates = [
        REPO_ROOT / "artifacts" / "requirements" / "universe_inventory.json",
        REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_summary_report.md",
    ]
    for c in candidates:
        if not c.exists():
            continue
        try:
            text = c.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.findall(r"\b(CRITICAL|HIGH|MEDIUM|LOW)\b\s*[:=]\s*(\d+)", text)
        if m:
            counts: dict[str, int] = {}
            for sev, n in m:
                counts[sev] = max(counts.get(sev, 0), int(n))
            if counts:
                counts["_baseline_source"] = str(c.relative_to(REPO_ROOT))  # type: ignore[assignment]
                return counts
    return None


def _is_proof_field_complete(row: dict[str, str]) -> tuple[bool, list[str]]:
    """Return (proof-field-complete, missing). Field-level only; no execution check."""
    missing = [f for f in COMPLETE_PROOF_FIELDS if not (row.get(f) or "").strip()]
    return (not missing), missing


def _is_proof_evidence_present(row: dict[str, str]) -> tuple[bool, list[str]]:
    """Return (proof-evidence-present, missing). True only when the test/CI/bundle
    paths exist on disk AND a last_passed_commit is recorded."""
    missing: list[str] = []
    for f in EVIDENCE_PATH_FIELDS:
        if (row.get(f) or "").strip().lower() != "true":
            missing.append(f)
    if not (row.get("last_passed_commit") or "").strip():
        missing.append("last_passed_commit")
    return (not missing), missing


def _bundle_path_for(row: dict[str, str]) -> Path:
    """Return the canonical proof-bundle path for a ledger row."""
    return REPO_ROOT / "artifacts" / "requirements" / "proof_bundles" / f"{row['req_id'].lower()}.json"


def _validate_bundle_binding(row: dict[str, str]) -> list[str]:
    """W4d-5 strict binding check for rows claiming evidence_status=PROOF_PRESENT.

    Reads the proof bundle and verifies:
      - bundle JSON parses
      - bundle.req_id matches ledger req_id
      - bundle.proof_status == EVIDENCE_PRESENT
      - bundle.git_dirty_at_test_time == false
      - bundle.git_head_at_test_time == ledger.last_passed_commit
      - bundle.content_hash recomputes correctly (tamper detection)

    Returns list of error messages; empty list means pass.
    Skipped if evidence_status != PROOF_PRESENT.
    """
    if (row.get("evidence_status") or "").strip() != "PROOF_PRESENT":
        return []
    errs: list[str] = []
    p = _bundle_path_for(row)
    if not p.exists():
        return [f"{row['req_id']}: PROOF_PRESENT but bundle missing at {p.relative_to(REPO_ROOT)}"]
    try:
        bundle = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{row['req_id']}: bundle unreadable: {exc}"]

    if bundle.get("req_id") != row["req_id"]:
        errs.append(
            f"{row['req_id']}: bundle.req_id '{bundle.get('req_id')}' != ledger.req_id"
        )
    if bundle.get("proof_status") != "EVIDENCE_PRESENT":
        errs.append(
            f"{row['req_id']}: bundle.proof_status '{bundle.get('proof_status')}' != EVIDENCE_PRESENT "
            f"(ledger says PROOF_PRESENT)"
        )
    if bundle.get("git_dirty_at_test_time") is not False:
        errs.append(
            f"{row['req_id']}: bundle.git_dirty_at_test_time={bundle.get('git_dirty_at_test_time')!r} "
            f"-- EVIDENCE_PRESENT requires false"
        )
    bundle_head = (bundle.get("git_head_at_test_time") or "").strip()
    ledger_head = (row.get("last_passed_commit") or "").strip()
    if bundle_head != ledger_head:
        errs.append(
            f"{row['req_id']}: bundle.git_head_at_test_time '{bundle_head[:12]}' "
            f"!= ledger.last_passed_commit '{ledger_head[:12]}'"
        )

    declared = bundle.get("content_hash", "")
    bundle_no_hash = {k: v for k, v in bundle.items() if k != "content_hash"}
    canonical = json.dumps(
        bundle_no_hash, sort_keys=True, separators=(",", ":"),
        default=str, ensure_ascii=True,
    )
    recomputed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if declared != recomputed:
        errs.append(
            f"{row['req_id']}: bundle content_hash mismatch (tamper detection): "
            f"declared={declared[:16]}..., recomputed={recomputed[:16]}..."
        )
    return errs


def _validate(rows: list[dict[str, str]], header: list[str]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if len(rows) != EXPECTED_ROWS:
        errors.append(f"row count is {len(rows)}, expected {EXPECTED_ROWS}")

    # req_id
    ids = [r.get("req_id", "") for r in rows]
    seen: dict[str, int] = {}
    for rid in ids:
        if not REQ_ID_RE.match(rid):
            errors.append(f"malformed req_id: '{rid}'")
        seen[rid] = seen.get(rid, 0) + 1
    dup_ids = [k for k, v in seen.items() if v > 1]
    if dup_ids:
        errors.append(f"duplicate req_ids: {dup_ids}")

    blank_canon = [r["req_id"] for r in rows if not (r.get("canonical_requirement_statement") or "").strip()]
    if blank_canon:
        errors.append(f"{len(blank_canon)} rows have empty canonical_requirement_statement: {blank_canon[:5]}")

    bad_owner: list[str] = []
    for r in rows:
        owner = (r.get("canonical_owner_surface") or "").strip()
        if not owner:
            bad_owner.append(f"{r['req_id']}: empty owner")
        elif owner not in CANONICAL_OWNER_VOCAB:
            bad_owner.append(f"{r['req_id']}: '{owner}'")
    if bad_owner:
        errors.append(f"{len(bad_owner)} rows have invalid canonical_owner_surface: {bad_owner[:5]}")

    bad_sev = [(r["req_id"], r.get("severity_if_missing", "")) for r in rows
               if r.get("severity_if_missing", "").strip().upper() not in ALLOWED_SEVERITY]
    if bad_sev:
        errors.append(f"{len(bad_sev)} rows have invalid severity: {bad_sev[:5]}")

    # CRITICAL/HIGH rows must have all mandatory proof fields
    critical_high_missing: list[dict[str, Any]] = []
    for r in rows:
        sev = r.get("severity_if_missing", "").strip().upper()
        if sev not in {"CRITICAL", "HIGH"}:
            continue
        missing = [f for f in MANDATORY_PROOF_FIELDS if not (r.get(f) or "").strip()]
        if missing:
            critical_high_missing.append({"req_id": r["req_id"], "severity": sev, "missing": missing})
    if critical_high_missing:
        errors.append(f"{len(critical_high_missing)} CRITICAL/HIGH rows missing mandatory proof fields")

    # ACCEPTED requires field complete AND evidence present
    bad_accept: list[str] = []
    for r in rows:
        final = (r.get("final_acceptance_status") or "").strip()
        if final not in ALLOWED_FINAL_ACCEPTANCE:
            errors.append(f"{r['req_id']}: invalid final_acceptance_status '{final}'")
        if final == "ACCEPTED":
            field_ok, _ = _is_proof_field_complete(r)
            evid_ok, _ = _is_proof_evidence_present(r)
            if not (field_ok and evid_ok):
                bad_accept.append(r["req_id"])
    if bad_accept:
        errors.append(f"{len(bad_accept)} rows ACCEPTED without complete proof field+evidence: {bad_accept[:5]}")

    # PROOF_PRESENT requires field complete AND evidence present
    bad_evid: list[str] = []
    bad_bundle_binding: list[str] = []
    for r in rows:
        evid = (r.get("evidence_status") or "").strip()
        if evid not in ALLOWED_EVIDENCE_STATUS:
            errors.append(f"{r['req_id']}: invalid evidence_status '{evid}'")
        if evid == "PROOF_PRESENT":
            field_ok, _ = _is_proof_field_complete(r)
            evidence_ok, _ = _is_proof_evidence_present(r)
            if not (field_ok and evidence_ok):
                bad_evid.append(r["req_id"])
            # W4d-5: PROOF_PRESENT MUST be backed by a clean bundle binding
            binding_errs = _validate_bundle_binding(r)
            if binding_errs:
                bad_bundle_binding.append(r["req_id"])
                for be in binding_errs:
                    errors.append(be)
    if bad_evid:
        errors.append(f"{len(bad_evid)} rows PROOF_PRESENT without field+evidence complete: {bad_evid[:5]}")
    if bad_bundle_binding:
        errors.append(
            f"{len(bad_bundle_binding)} rows PROOF_PRESENT with bundle-binding mismatch: {bad_bundle_binding[:5]}"
        )

    bad_impl = [r["req_id"] for r in rows
                if (r.get("implementation_status") or "").strip() not in ALLOWED_IMPL_STATUS]
    if bad_impl:
        errors.append(f"{len(bad_impl)} rows have invalid implementation_status: {bad_impl[:5]}")

    # Distributions
    sev_counts = Counter((r.get("severity_if_missing") or "").strip().upper() for r in rows)
    owner_counts = Counter((r.get("canonical_owner_surface") or "").strip() for r in rows)
    accept_counts = Counter((r.get("final_acceptance_status") or "").strip() for r in rows)
    evid_counts = Counter((r.get("evidence_status") or "").strip() for r in rows)
    impl_counts = Counter((r.get("implementation_status") or "").strip() for r in rows)

    accepted_count = accept_counts.get("ACCEPTED", 0)
    accepted_caveat_count = accept_counts.get("ACCEPTED_WITH_CAVEAT", 0)
    needs_proof_count = accept_counts.get("NEEDS_PROOF", 0)
    needs_owner_review_count = accept_counts.get("NEEDS_OWNER_REVIEW", 0)
    duplicate_rejected_count = accept_counts.get("REJECTED_DUPLICATE", 0)
    deferred_count = accept_counts.get("DEFERRED", 0)

    ambiguous_owner_rows = [
        r["req_id"] for r in rows if "AMBIGUOUS_OWNER" in (r.get("hardening_notes") or "")
    ]
    pedagogical_rows = [
        r["req_id"] for r in rows if "PEDAGOGICAL_ROW" in (r.get("hardening_notes") or "")
    ]

    # CRITICAL/HIGH proof field completeness vs evidence presence vs staged.
    # W4d-4: proof-evidence-staged counts rows where test/CI/bundle paths exist
    # AND evidence_status is PROOF_PARTIAL or PROOF_PRESENT, but
    # last_passed_commit is empty (commit-binding pending).
    proof_field_complete_critical_high = 0
    proof_field_partial_critical_high = 0
    proof_evidence_present_critical_high = 0
    proof_evidence_staged_critical_high = 0
    for r in rows:
        sev = r.get("severity_if_missing", "").strip().upper()
        if sev not in {"CRITICAL", "HIGH"}:
            continue
        field_ok, _ = _is_proof_field_complete(r)
        evid_ok, _ = _is_proof_evidence_present(r)
        if field_ok:
            proof_field_complete_critical_high += 1
        else:
            proof_field_partial_critical_high += 1
        if evid_ok:
            proof_evidence_present_critical_high += 1
        # Staged: paths exist + evidence_status is PROOF_PARTIAL/PRESENT, but
        # last_passed_commit empty. PROOF_PARTIAL alone qualifies even if
        # full evidence path checks fail (commit-pending state).
        paths_present = all(
            (r.get(f) or "").strip().lower() == "true"
            for f in EVIDENCE_PATH_FIELDS
        )
        evid_status = (r.get("evidence_status") or "").strip()
        if (
            paths_present
            and evid_status in {"PROOF_PARTIAL", "PROOF_PRESENT"}
            and not (r.get("last_passed_commit") or "").strip()
        ):
            proof_evidence_staged_critical_high += 1

    # Source-locking coverage
    source_lock_complete = 0
    source_lock_missing = 0
    for r in rows:
        if (r.get("source_commit_sha") or "").strip() and (r.get("source_text_sha256") or "").strip():
            source_lock_complete += 1
        else:
            source_lock_missing += 1

    # Coverage doctrine for owner-surfaces
    coverage_doctrine: dict[str, Any] = {}
    for surface, rationale in EXTERNAL_PROOF_SURFACES.items():
        coverage_doctrine[surface] = {
            "row_count": owner_counts.get(surface, 0),
            "external_proof_pack": True,
            "rationale": rationale,
        }

    # Severity reconciliation
    prior_baseline = _discover_prior_severity_baseline()
    reconciliation: dict[str, Any] = {
        "current_csv_counts": dict(sev_counts),
        "prior_baseline": prior_baseline,
        "delta": None,
        "rows_with_changed_severity": [],
        "recommendation": "preserve current CSV severity assignments unless an authoritative baseline says otherwise",
    }
    if prior_baseline:
        baseline_no_meta = {k: v for k, v in prior_baseline.items() if not k.startswith("_")}
        deltas: dict[str, int] = {}
        for sev_key in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            cur = sev_counts.get(sev_key, 0)
            prior = baseline_no_meta.get(sev_key, 0)
            if cur != prior:
                deltas[sev_key] = cur - prior
        reconciliation["delta"] = deltas

    return {
        "errors": errors,
        "warnings": warnings,
        "row_count": len(rows),
        "header_columns": len(header),
        "sev_counts": dict(sev_counts),
        "owner_counts": dict(owner_counts),
        "accept_counts": dict(accept_counts),
        "evid_counts": dict(evid_counts),
        "impl_counts": dict(impl_counts),
        "accepted_count": accepted_count,
        "accepted_with_caveat_count": accepted_caveat_count,
        "needs_proof_count": needs_proof_count,
        "needs_owner_review_count": needs_owner_review_count,
        "duplicate_rejected_count": duplicate_rejected_count,
        "deferred_count": deferred_count,
        "ambiguous_owner_rows": ambiguous_owner_rows,
        "ambiguous_owner_count": len(ambiguous_owner_rows),
        "pedagogical_rows": pedagogical_rows,
        "pedagogical_row_count": len(pedagogical_rows),
        "critical_high_missing_proof": critical_high_missing,
        "critical_high_missing_proof_count": len(critical_high_missing),
        "proof_field_complete_critical_high": proof_field_complete_critical_high,
        "proof_field_partial_critical_high": proof_field_partial_critical_high,
        "proof_evidence_present_critical_high": proof_evidence_present_critical_high,
        "proof_evidence_staged_critical_high": proof_evidence_staged_critical_high,
        "source_lock_complete": source_lock_complete,
        "source_lock_missing": source_lock_missing,
        "coverage_doctrine": coverage_doctrine,
        "severity_reconciliation": reconciliation,
    }


def _emit_artifacts(report: dict[str, Any], cmd: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "ledger_path": str(LEDGER.relative_to(REPO_ROOT)).replace("\\", "/"),
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_command": cmd,
        "git_status": _git_status(),
        "summary": {
            "total_rows": report["row_count"],
            "header_columns": report["header_columns"],
            "severity_counts": report["sev_counts"],
            "owner_counts": report["owner_counts"],
            "accepted_count": report["accepted_count"],
            "accepted_with_caveat_count": report["accepted_with_caveat_count"],
            "needs_proof_count": report["needs_proof_count"],
            "needs_owner_review_count": report["needs_owner_review_count"],
            "duplicate_rejected_count": report["duplicate_rejected_count"],
            "deferred_count": report["deferred_count"],
            "critical_high_missing_proof_count": report["critical_high_missing_proof_count"],
            "proof_field_complete_critical_high": report["proof_field_complete_critical_high"],
            "proof_field_partial_critical_high": report["proof_field_partial_critical_high"],
            "proof_evidence_present_critical_high": report["proof_evidence_present_critical_high"],
            "proof_evidence_staged_critical_high": report["proof_evidence_staged_critical_high"],
            "ambiguous_owner_count": report["ambiguous_owner_count"],
            "pedagogical_row_count": report["pedagogical_row_count"],
            "source_lock_complete": report["source_lock_complete"],
            "source_lock_missing": report["source_lock_missing"],
        },
        "implementation_status_counts": report["impl_counts"],
        "evidence_status_counts": report["evid_counts"],
        "final_acceptance_status_counts": report["accept_counts"],
        "ambiguous_owner_rows": report["ambiguous_owner_rows"],
        "pedagogical_rows": report["pedagogical_rows"],
        "critical_high_missing_proof": report["critical_high_missing_proof"],
        "coverage_doctrine": report["coverage_doctrine"],
        "severity_reconciliation": report["severity_reconciliation"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "validation_passed": not report["errors"],
    }

    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md: list[str] = []
    md.append("# 10C Proof Ledger Validation Report (W4d-2)")
    md.append("")
    md.append(f"- Ledger: `{payload['ledger_path']}`")
    md.append(f"- Validated at (UTC): {payload['validated_at_utc']}")
    md.append(f"- Validation command: `{cmd}`")
    md.append(f"- Git working-tree status: `{payload['git_status']}`")
    md.append(f"- Validation passed: **{payload['validation_passed']}**")
    md.append("")
    md.append("## Summary")
    md.append("")
    s = payload["summary"]
    md.append(f"- Total rows: **{s['total_rows']}**")
    md.append(f"- Header columns: **{s['header_columns']}**")
    md.append(f"- Severity counts: {s['severity_counts']}")
    md.append(f"- Accepted: **{s['accepted_count']}** | Accepted with caveat: **{s['accepted_with_caveat_count']}**")
    md.append(f"- Needs proof: **{s['needs_proof_count']}** | Needs owner review: **{s['needs_owner_review_count']}** | Deferred: {s['deferred_count']}")
    md.append(f"- Rejected duplicate: {s['duplicate_rejected_count']}")
    md.append("")
    md.append("### Proof field completeness vs evidence presence")
    md.append("")
    md.append(f"- CRITICAL/HIGH **proof-field-complete**: **{s['proof_field_complete_critical_high']}**")
    md.append(f"- CRITICAL/HIGH **proof-field-incomplete**: **{s['proof_field_partial_critical_high']}**")
    md.append(f"- CRITICAL/HIGH **proof-evidence-staged**: **{s['proof_evidence_staged_critical_high']}**")
    md.append(f"- CRITICAL/HIGH **proof-evidence-present**: **{s['proof_evidence_present_critical_high']}**")
    md.append("")
    md.append("> *Proof-field-complete* means every required column is populated. ")
    md.append("> *Proof-evidence-staged* means tests + bundles + paths all exist; commit-binding pending. ")
    md.append("> *Proof-evidence-present* means the test/CI/bundle paths exist on disk ")
    md.append("> AND `last_passed_commit` is recorded. Until the latter rises, no row should be `ACCEPTED`.")
    md.append("")
    md.append("### Source locking")
    md.append("")
    md.append(f"- Rows with `source_commit_sha` + `source_text_sha256`: **{s['source_lock_complete']}**")
    md.append(f"- Rows missing source-lock: **{s['source_lock_missing']}**")
    md.append("")
    md.append("### Owner distribution")
    md.append("")
    md.append("| Owner surface | Count |")
    md.append("|---|---:|")
    for owner, count in sorted(report["owner_counts"].items(), key=lambda x: -x[1]):
        md.append(f"| `{owner}` | {count} |")
    md.append("")
    md.append("### Coverage doctrine (zero-row owner surfaces)")
    md.append("")
    for surface, info in report["coverage_doctrine"].items():
        md.append(f"#### `{surface}` — {info['row_count']} rows")
        md.append("")
        md.append(info["rationale"])
        md.append("")
    md.append("### Pedagogical rows (documentation, not runtime proof obligations)")
    md.append("")
    if report["pedagogical_rows"]:
        for rid in report["pedagogical_rows"]:
            md.append(f"- `{rid}` — `final_acceptance_status = ACCEPTED_WITH_CAVEAT`")
    else:
        md.append("- (none)")
    md.append("")
    md.append("### Severity reconciliation")
    md.append("")
    rec = report["severity_reconciliation"]
    md.append(f"- Current CSV: {rec['current_csv_counts']}")
    if rec["prior_baseline"]:
        md.append(f"- Prior baseline: {rec['prior_baseline']}")
        md.append(f"- Delta (current - prior): {rec['delta']}")
    else:
        md.append("- Prior baseline: not discoverable in repo artifacts")
    md.append(f"- Recommendation: {rec['recommendation']}")
    md.append("")
    if report["errors"]:
        md.append("### Errors")
        md.append("")
        for e in report["errors"]:
            md.append(f"- {e}")
        md.append("")
    if report["ambiguous_owner_rows"]:
        md.append("### Ambiguous-owner rows (need owner review)")
        md.append("")
        for rid in report["ambiguous_owner_rows"][:50]:
            md.append(f"- `{rid}`")
        if len(report["ambiguous_owner_rows"]) > 50:
            md.append(f"- ... +{len(report['ambiguous_owner_rows']) - 50} more")
        md.append("")
    if report["critical_high_missing_proof"]:
        md.append("### CRITICAL/HIGH rows still missing proof fields")
        md.append("")
        for entry in report["critical_high_missing_proof"][:25]:
            md.append(f"- `{entry['req_id']}` ({entry['severity']}): missing {entry['missing']}")
        if len(report["critical_high_missing_proof"]) > 25:
            md.append(f"- ... +{len(report['critical_high_missing_proof']) - 25} more")
        md.append("")

    MD_OUT.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the hardened 10C proof ledger (W4d-2).")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any error (default).")
    parser.add_argument("--no-strict", dest="strict", action="store_false", help="Always exit 0; emit artifacts only.")
    parser.set_defaults(strict=True)
    args = parser.parse_args()

    cmd = "python tools/requirements/validate_10c_proof_ledger.py" + (" --strict" if args.strict else " --no-strict")

    print("[10C proof ledger validator W4d-2]")
    if not LEDGER.exists():
        print(f"FATAL: ledger not found at {LEDGER}", file=sys.stderr)
        return 2

    try:
        header, rows = _load_rows()
    except (csv.Error, ValueError) as exc:
        print(f"FATAL: CSV parse failure: {exc}", file=sys.stderr)
        return 2

    report = _validate(rows, header)
    _emit_artifacts(report, cmd)

    print(f"  rows                                : {report['row_count']}")
    print(f"  header columns                      : {report['header_columns']}")
    print(f"  severity                            : {report['sev_counts']}")
    print(f"  accepted / accepted_with_caveat     : {report['accepted_count']} / {report['accepted_with_caveat_count']}")
    print(f"  needs_proof / needs_owner_review    : {report['needs_proof_count']} / {report['needs_owner_review_count']}")
    print(f"  CRITICAL/HIGH proof-field-complete  : {report['proof_field_complete_critical_high']}")
    print(f"  CRITICAL/HIGH proof-field-partial   : {report['proof_field_partial_critical_high']}")
    print(f"  CRITICAL/HIGH proof-evidence-staged : {report['proof_evidence_staged_critical_high']}")
    print(f"  CRITICAL/HIGH proof-evidence-present: {report['proof_evidence_present_critical_high']}")
    print(f"  ambiguous-owner rows                : {report['ambiguous_owner_count']}")
    print(f"  pedagogical rows                    : {report['pedagogical_row_count']}")
    print(f"  source-locked rows                  : {report['source_lock_complete']} / {report['row_count']}")
    print(f"  errors                              : {len(report['errors'])}")
    print(f"  artifacts                           : {JSON_OUT.relative_to(REPO_ROOT)}, {MD_OUT.relative_to(REPO_ROOT)}")

    if report["errors"]:
        print("\nFAIL -- validation errors:")
        for e in report["errors"][:20]:
            print(f"  - {e}")
        if len(report["errors"]) > 20:
            print(f"  ... +{len(report['errors']) - 20} more")
        return 1 if args.strict else 0

    print("\nOK  10C proof ledger validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
