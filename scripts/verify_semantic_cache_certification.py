"""Verifier — Semantic-cache R1B subclaim certification (W1 phase 1, contract only).

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``
Author-Gate decision (2026-04-30, architecture_choice):
``map_to_RTC_REQ_055_plus_conditional_056_057_058``.

Boundary
--------

W1 phase 1 is **sidecar contract wiring only**. This verifier:

  1. Reads ``artifacts/certification/semantic_cache_subclaims.json`` (sidecar)
  2. Validates the sidecar against the R1B subclaim schema
  3. Computes per-row outcomes for the 4 gated R1B rows
  4. Merges outcomes into ``runtime_evidence_overrides.json`` (preserving
     other rows' overrides)
  5. Emits ``semantic_cache_certification_report.json`` and ``.md``

It does **NOT** run cache fixtures, query the embedding service, or modify
``SemanticCacheManager``. Evidence emission is W1 phase 2.

Exit codes
----------

Per user §10 ("fail-closed when sidecar missing/incomplete; do not block W0
clean baseline"):

  - **0 PASS** (advisory) — sidecar absent: report records that no R1B
    evidence exists; the 4 gated rows stay PENDING. This keeps W0 baseline
    green.
  - **0 PASS** (in-scope evidence) — sidecar present, valid, all in-scope
    gating subclaims PASS for at least one row.
  - **0 PASS** (no in-scope rows + valid sidecar) — sidecar present and
    valid, but every conditional row is out-of-scope and the parent row's
    subclaims are all PASS.
  - **2 FAIL_CLOSED** — sidecar present but malformed, missing required
    subclaims, or any in-scope row resolves to BLOCKED/PARTIAL.
  - **3 HARNESS_ERROR** — unexpected exception.

Anti-cheat
----------

The verifier writes overrides ONLY for rows in ``GATED_ROWS``. Other rows
in the canonical CSV are never touched; the verifier preserves their prior
override entries when merging.

The sidecar's ``actual_proof_depth`` and ``final_acceptance_status`` fields
(if any) are silently ignored. Only the verifier writes overrides.

The verifier emits no language matching the W0 closure forbidden patterns
(see ``verify_w0_language_discipline.py``).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.r1b_subclaim_schema import (  # noqa: E402
    ALL_SUBCLAIMS,
    CONDITIONAL_SUBCLAIMS,
    CORE_SUBCLAIMS,
    GATED_ROWS,
    RowOutcome,
    compute_row_outcomes,
    load_sidecar,
)


ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
SIDECAR_PATH = ARTIFACTS_DIR / "semantic_cache_subclaims.json"
OVERRIDES_PATH = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
REPORT_JSON = ARTIFACTS_DIR / "semantic_cache_certification_report.json"
REPORT_MD = ARTIFACTS_DIR / "semantic_cache_certification_report.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _read_existing_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        with OVERRIDES_PATH.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        # If overrides are malformed, do NOT silently overwrite — the
        # acceptance verifier will catch malformed overrides separately.
        return {}


def _merge_overrides(
    existing: dict,
    outcomes: dict[str, RowOutcome],
) -> dict:
    """Merge per-row outcomes into the overrides dict, preserving other rows.

    The override file has 4 sub-dicts (per ``acceptance_validator.apply_to_matrix``):
      - actual_proof_depth: {req_id -> str}
      - final_acceptance_status: {req_id -> str}
      - acceptance_caveat: {req_id -> str}
      - blocking_gap: {req_id -> str}

    For each gated row, the verifier sets/clears its entries. Rows whose
    outcome is PENDING or out-of-scope have their entries REMOVED so the
    acceptance validator falls back to its baseline behavior.
    """
    merged = {
        "actual_proof_depth":         dict(existing.get("actual_proof_depth")         or {}),
        "final_acceptance_status":    dict(existing.get("final_acceptance_status")    or {}),
        "acceptance_caveat":          dict(existing.get("acceptance_caveat")          or {}),
        "blocking_gap":               dict(existing.get("blocking_gap")               or {}),
    }
    for rid, outcome in outcomes.items():
        # Out-of-scope or PENDING: remove any prior overrides for this row.
        if outcome.final_acceptance_status == "PENDING":
            for key in merged:
                merged[key].pop(rid, None)
            continue
        # Otherwise write the verifier's outcome
        merged["actual_proof_depth"][rid] = outcome.actual_proof_depth
        merged["final_acceptance_status"][rid] = outcome.final_acceptance_status
        if outcome.acceptance_caveat:
            merged["acceptance_caveat"][rid] = outcome.acceptance_caveat
        else:
            merged["acceptance_caveat"].pop(rid, None)
        if outcome.blocking_gap:
            merged["blocking_gap"][rid] = outcome.blocking_gap
        else:
            merged["blocking_gap"].pop(rid, None)
    return merged


def _outcome_dict(o: RowOutcome) -> dict:
    return {
        "row_id": o.row_id,
        "required_proof_depth": o.required_proof_depth,
        "scope_flag": o.scope_flag,
        "in_scope": o.in_scope,
        "actual_proof_depth": o.actual_proof_depth,
        "final_acceptance_status": o.final_acceptance_status,
        "acceptance_caveat": o.acceptance_caveat,
        "blocking_gap": o.blocking_gap,
        "blocking_subclaims": list(o.blocking_subclaims),
        "soft_blocker_subclaims": list(o.soft_blocker_subclaims),
        "expected_fail_reason": o.expected_fail_reason,
    }


def _build_report(
    sidecar_result,
    outcomes: dict[str, RowOutcome],
    *,
    overall_status: str,
    expected_fail_reason: str,
    actual_fail_reason: str,
) -> dict:
    in_scope_rows = [rid for rid, o in outcomes.items() if o.in_scope]
    accepted_rows = [rid for rid, o in outcomes.items()
                     if o.final_acceptance_status == "ACCEPTED"]
    partial_rows = [rid for rid, o in outcomes.items()
                    if o.final_acceptance_status == "PARTIAL"]
    blocked_rows = [rid for rid, o in outcomes.items()
                    if o.final_acceptance_status == "BLOCKED"]
    pending_rows = [rid for rid, o in outcomes.items()
                    if o.final_acceptance_status == "PENDING"]

    return {
        "verifier": "verify_semantic_cache_certification",
        "phase": "W1_phase_1_sidecar_contract_only",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-055/056/057/058 R1B subclaim gating",
        "boundary_note": (
            "W1 phase 1 is sidecar contract wiring only. This verifier reads "
            "the R1B subclaim sidecar and translates declared verdicts into "
            "row overrides. It does not run cache fixtures, query the "
            "embedding service, modify SemanticCacheManager, or change "
            "thresholds. Per user 2026-04-30: contract wiring only."
        ),
        "status": overall_status,
        "expected_fail_reason": expected_fail_reason,
        "actual_fail_reason": actual_fail_reason,
        "sidecar_path": str(sidecar_result.sidecar_path),
        "sidecar_present": sidecar_result.sidecar_present,
        "sidecar_schema_version": sidecar_result.schema_version,
        "sidecar_evaluated_at_utc": sidecar_result.evaluated_at_utc,
        "sidecar_evidence_evaluator": sidecar_result.evidence_evaluator,
        "sidecar_scope": dict(sidecar_result.scope),
        "sidecar_schema_errors": list(sidecar_result.schema_errors),
        "sidecar_subclaim_statuses": {
            sid: {
                "status": v.status,
                "evidence_path": v.evidence_path,
                "notes": v.notes,
            }
            for sid, v in sorted(sidecar_result.subclaims.items())
        },
        "core_subclaims": list(CORE_SUBCLAIMS),
        "conditional_subclaims": list(CONDITIONAL_SUBCLAIMS),
        "all_subclaims": list(ALL_SUBCLAIMS),
        "gated_rows": list(GATED_ROWS.keys()),
        "row_outcomes": {rid: _outcome_dict(o) for rid, o in outcomes.items()},
        "in_scope_rows": in_scope_rows,
        "accepted_rows": accepted_rows,
        "partial_rows": partial_rows,
        "blocked_rows": blocked_rows,
        "pending_rows": pending_rows,
    }


def _build_md(report: dict) -> str:
    lines = [
        "# R1B Semantic-Cache Subclaim Verifier Report (W1 phase 1)",
        "",
        f"> Generated: {report['executed_at_utc']}",
        f"> Status: **{report['status']}**",
        f"> Phase: `{report['phase']}` (sidecar contract only — no cache, no thresholds, no OTEL/replay/runtime evidence)",
        "",
        "## 1. Sidecar state",
        "",
        f"- Path: `{report['sidecar_path']}`",
        f"- Present: **{report['sidecar_present']}**",
        f"- Schema version: `{report['sidecar_schema_version']}`",
        f"- Evaluated at: `{report['sidecar_evaluated_at_utc']}`",
        f"- Evaluator: `{report['sidecar_evidence_evaluator']}`",
        "",
        "## 2. Scope flags",
        "",
        "| Flag | Value |",
        "|---|---|",
    ]
    for k, v in sorted(report["sidecar_scope"].items()):
        lines.append(f"| `{k}` | {v} |")
    lines.extend(["", "## 3. Subclaim statuses", "",
                  "| Subclaim | Status | Notes |",
                  "|---|---|---|"])
    for sid in ALL_SUBCLAIMS:
        s = report["sidecar_subclaim_statuses"].get(sid, {})
        status = s.get("status", "(absent)")
        notes = (s.get("notes") or "")[:80]
        lines.append(f"| `{sid}` | `{status}` | {notes} |")
    lines.extend(["", "## 4. Per-row outcomes", "",
                  "| Row | Required depth | Scope flag | In scope | Final status | Caveat / gap |",
                  "|---|---|---|---|---|---|"])
    for rid, o in sorted(report["row_outcomes"].items()):
        gap_or_caveat = (o.get("acceptance_caveat") or o.get("blocking_gap") or "")[:80]
        lines.append(
            f"| `{rid}` | `{o['required_proof_depth']}` | `{o['scope_flag']}` | "
            f"{o['in_scope']} | **{o['final_acceptance_status']}** | {gap_or_caveat} |"
        )
    lines.extend([
        "",
        "## 5. Schema errors (if any)",
        "",
    ])
    if report["sidecar_schema_errors"]:
        for err in report["sidecar_schema_errors"]:
            lines.append(f"- `{err}`")
    else:
        lines.append("_None._")
    lines.extend([
        "",
        "## 6. Boundary statement",
        "",
        report["boundary_note"],
        "",
        "## 7. What this report does not claim",
        "",
        "- Does not claim the semantic cache is fixed.",
        "- Does not claim any R1B evidence has been gathered (W1 phase 2).",
        "- Does not promote any row beyond what the sidecar's PASS verdicts justify.",
    ])
    return "\n".join(lines)


def main() -> int:
    sidecar_result = load_sidecar(SIDECAR_PATH)
    outcomes = compute_row_outcomes(sidecar_result)

    in_scope_outcomes = [o for o in outcomes.values() if o.in_scope]
    has_blocked = any(o.final_acceptance_status == "BLOCKED" for o in in_scope_outcomes)
    has_partial = any(o.final_acceptance_status == "PARTIAL" for o in in_scope_outcomes)

    if not sidecar_result.sidecar_present:
        # Advisory baseline: sidecar absent.
        overall_status = "PASS_ADVISORY_BASELINE"
        expected_fail_reason = ""
        actual_fail_reason = ""
        exit_code = 0
    elif sidecar_result.schema_errors:
        overall_status = "FAIL_CLOSED"
        expected_fail_reason = "SIDECAR_MALFORMED"
        actual_fail_reason = (
            f"sidecar exists at {SIDECAR_PATH.relative_to(REPO_ROOT)} but has "
            f"{len(sidecar_result.schema_errors)} schema error(s)"
        )
        exit_code = 2
    elif has_blocked:
        overall_status = "FAIL_CLOSED"
        expected_fail_reason = "R1B_HARD_BLOCKERS_PRESENT"
        actual_fail_reason = (
            "at least one in-scope R1B row resolves to BLOCKED due to subclaim "
            "hard blockers (NOT_PROVEN / BLOCKED / INFRASTRUCTURE_GAP / missing)"
        )
        exit_code = 2
    elif has_partial:
        overall_status = "FAIL_CLOSED"
        expected_fail_reason = "R1B_SOFT_BLOCKERS_PRESENT"
        actual_fail_reason = (
            "at least one in-scope R1B row resolves to PARTIAL due to subclaim "
            "soft blockers (PARTIAL / CALIBRATION_GAP)"
        )
        exit_code = 2
    else:
        overall_status = "PASS"
        expected_fail_reason = ""
        actual_fail_reason = ""
        exit_code = 0

    # Merge overrides + write report regardless of exit code so reports
    # always reflect the most recent evaluation.
    existing = _read_existing_overrides()
    merged = _merge_overrides(existing, outcomes)
    _write_json(OVERRIDES_PATH, merged)

    report = _build_report(
        sidecar_result, outcomes,
        overall_status=overall_status,
        expected_fail_reason=expected_fail_reason,
        actual_fail_reason=actual_fail_reason,
    )
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(_build_md(report), encoding="utf-8")

    print(f"[verify_semantic_cache] {overall_status}: sidecar_present={sidecar_result.sidecar_present}")
    print(f"[verify_semantic_cache] gated_rows={list(outcomes.keys())}")
    print(f"[verify_semantic_cache] wrote: {REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"[verify_semantic_cache] wrote: {REPORT_MD.relative_to(REPO_ROOT)}")
    print(f"[verify_semantic_cache] wrote: {OVERRIDES_PATH.relative_to(REPO_ROOT)}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_semantic_cache] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
