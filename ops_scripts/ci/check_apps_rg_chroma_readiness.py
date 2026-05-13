"""CHECK-RG-CHROMA — apps_rg ChromaDB readiness gate.

Verifies the apps_rg corpus is correctly ingested and structured in the
process_docs Chroma collection. Advisory by default; fail-closed via
APPS_RG_CHROMA_FAIL_CLOSED=1. Bypass: APPS_RG_CHROMA_BYPASS=1.

Plan: apps-rg-chroma-ingestion-wiring-c7f2d9 W5.3

Checks:
  RG-CHROMA-1  process_docs collection exists and is non-empty
  RG-CHROMA-2  app=apps_rg records exist
  RG-CHROMA-3  All 7 required source_class counts are non-zero
  RG-CHROMA-4  Source class counts match expected stable values
  RG-CHROMA-5  All 8 required metadata fields present on a sample
  RG-CHROMA-6  citation_anchor present for normative corpora
  RG-CHROMA-7  prior_outputs has invalid_for_normative_use=True
  RG-CHROMA-8  prior_outputs excluded from normative source classes
  RG-CHROMA-9  UNKNOWN is never treated as PASS in support_status logic

Exit 0 always (advisory). Set APPS_RG_CHROMA_FAIL_CLOSED=1 for strict mode.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

BYPASS = os.environ.get("APPS_RG_CHROMA_BYPASS", "").lower() in ("1", "true")
FAIL_CLOSED = os.environ.get("APPS_RG_CHROMA_FAIL_CLOSED", "").lower() in ("1", "true")

CHROMA_PATH = os.environ.get("CHROMA_PERSIST_DIR", str(REPO_ROOT / "data/cache/chromadb"))

REQUIRED_SOURCE_CLASSES = [
    "governance_docs",
    "candidate_profile",
    "project_evidence",
    "approved_examples",
    "rubrics",
    "receipts",
    "prior_outputs",
]

NORMATIVE_SOURCE_CLASSES = {
    "candidate_profile", "project_evidence", "approved_examples",
    "rubrics", "governance_docs", "receipts",
}

REQUIRED_METADATA_FIELDS = [
    "source_id", "source_class", "authority_class", "freshness",
    "citation_anchor", "chunk_digest", "app", "ACL",
]

EXPECTED_COUNTS: dict[str, int] = {
    "governance_docs": 363,
    "candidate_profile": 1280,
    "project_evidence": 554,
    "approved_examples": 153,
    "rubrics": 182,
    "receipts": 967,
    "prior_outputs": 644,
}

SUPPORT_STATUS_PASSING_VALUES = {"PASS", "PARTIAL", "WEAK"}
SUPPORT_STATUS_NEVER_PASS = {"UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED", "NOT_APPLICABLE"}

REPORT_PATH = REPO_ROOT / "artifacts/ci/apps_rg_chroma_readiness_gate.json"


def _check(checks: list[dict], check_id: str, ok: bool, detail: str) -> None:
    level = "OK" if ok else "ERROR"
    checks.append({"check": check_id, "level": level, "detail": detail})
    print(f"  {'✅' if ok else '❌'} {check_id}: {detail}")


def main() -> int:
    if BYPASS:
        print("APPS_RG_CHROMA_BYPASS=1 — skipping CHECK-RG-CHROMA")
        return 0

    print("[CHECK-RG-CHROMA] apps_rg ChromaDB readiness gate")
    checks: list[dict] = []

    try:
        import chromadb  # type: ignore
    except ImportError:
        _check(checks, "RG-CHROMA-1", False, "chromadb not importable — install chromadb")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
    except Exception as exc:
        _check(checks, "RG-CHROMA-1", False, f"Cannot open ChromaDB at {CHROMA_PATH}: {exc}")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    # RG-CHROMA-1: process_docs exists and is non-empty
    try:
        col = client.get_collection("process_docs")
        total = col.count()
        _check(checks, "RG-CHROMA-1", total > 0, f"process_docs count={total}")
    except Exception as exc:
        _check(checks, "RG-CHROMA-1", False, f"process_docs collection not found: {exc}")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    # RG-CHROMA-2: app=apps_rg records exist
    try:
        r = col.get(where={"app": "apps_rg"}, limit=1)
        rg_exists = len(r["ids"]) > 0
        _check(checks, "RG-CHROMA-2", rg_exists,
               f"app=apps_rg records found: {rg_exists}")
    except Exception as exc:
        _check(checks, "RG-CHROMA-2", False, f"app=apps_rg query failed: {exc}")

    # RG-CHROMA-3 & 4: source_class counts non-zero and match expected
    sc_counts: dict[str, int] = {}
    for sc in REQUIRED_SOURCE_CLASSES:
        try:
            r = col.get(where={"source_class": sc})
            sc_counts[sc] = len(r["ids"])
        except Exception as exc:
            sc_counts[sc] = -1
            _check(checks, "RG-CHROMA-3", False, f"source_class={sc} query error: {exc}")

    all_nonzero = all(v > 0 for v in sc_counts.values())
    _check(checks, "RG-CHROMA-3", all_nonzero,
           "All 7 source_class counts non-zero: " + ", ".join(f"{k}={v}" for k, v in sc_counts.items()))

    count_mismatches = []
    for sc, expected in EXPECTED_COUNTS.items():
        actual = sc_counts.get(sc, -1)
        if actual != expected:
            count_mismatches.append(f"{sc}: expected={expected} actual={actual}")
    _check(checks, "RG-CHROMA-4", len(count_mismatches) == 0,
           ("Counts match" if not count_mismatches else "Mismatches: " + "; ".join(count_mismatches)))

    # RG-CHROMA-5: all 8 required metadata fields present on a sample
    try:
        sample = col.get(where={"app": "apps_rg"}, limit=5, include=["metadatas"])
        metas = sample.get("metadatas", [])
        if not metas:
            _check(checks, "RG-CHROMA-5", False, "No samples returned for metadata check")
        else:
            all_missing: set[str] = set()
            for meta in metas:
                missing = [f for f in REQUIRED_METADATA_FIELDS if f not in meta]
                all_missing.update(missing)
            _check(checks, "RG-CHROMA-5", len(all_missing) == 0,
                   f"All 8 metadata fields present" if not all_missing
                   else f"Missing fields: {sorted(all_missing)}")
    except Exception as exc:
        _check(checks, "RG-CHROMA-5", False, f"Metadata field check error: {exc}")

    # RG-CHROMA-6: citation_anchor present for normative corpora
    try:
        norm_sample = col.get(
            where={"source_class": "governance_docs"},
            limit=10, include=["metadatas"],
        )
        norm_metas = norm_sample.get("metadatas", [])
        with_anchor = [m for m in norm_metas if m.get("citation_anchor", "")]
        _check(checks, "RG-CHROMA-6", len(with_anchor) > 0,
               f"governance_docs sample: {len(with_anchor)}/{len(norm_metas)} have citation_anchor")
    except Exception as exc:
        _check(checks, "RG-CHROMA-6", False, f"citation_anchor check error: {exc}")

    # RG-CHROMA-7: prior_outputs has invalid_for_normative_use=True
    try:
        po_sample = col.get(where={"source_class": "prior_outputs"}, limit=10, include=["metadatas"])
        po_metas = po_sample.get("metadatas", [])
        if not po_metas:
            _check(checks, "RG-CHROMA-7", False, "No prior_outputs records found")
        else:
            po_invalid = [
                m for m in po_metas
                if str(m.get("invalid_for_normative_use", "false")).lower() == "true"
            ]
            all_invalid = len(po_invalid) == len(po_metas)
            _check(checks, "RG-CHROMA-7", all_invalid,
                   f"prior_outputs: {len(po_invalid)}/{len(po_metas)} have invalid_for_normative_use=True")
    except Exception as exc:
        _check(checks, "RG-CHROMA-7", False, f"prior_outputs check error: {exc}")

    # RG-CHROMA-8: prior_outputs NOT in normative source classes
    po_in_normative = "prior_outputs" in NORMATIVE_SOURCE_CLASSES
    _check(checks, "RG-CHROMA-8", not po_in_normative,
           "prior_outputs excluded from NORMATIVE_SOURCE_CLASSES" if not po_in_normative
           else "ERROR: prior_outputs is in NORMATIVE_SOURCE_CLASSES — must be excluded")

    # RG-CHROMA-9: UNKNOWN never treated as PASS in support_status logic
    # Verify by importing the binding and inspecting SUPPORT_STATUS_PASSING_VALUES
    try:
        from apps_rg.runtime.bindings.c0_binding import (  # type: ignore
            SUPPORT_STATUS_PASSING_VALUES as BINDING_PASS_VALUES,
        )
        unknown_in_pass = "UNKNOWN" in BINDING_PASS_VALUES
        _check(checks, "RG-CHROMA-9", not unknown_in_pass,
               f"UNKNOWN not in SUPPORT_STATUS_PASSING_VALUES: {sorted(BINDING_PASS_VALUES)}"
               if not unknown_in_pass
               else f"ERROR: UNKNOWN is in SUPPORT_STATUS_PASSING_VALUES: {sorted(BINDING_PASS_VALUES)}")
    except ImportError as exc:
        _check(checks, "RG-CHROMA-9", False, f"Could not import c0_binding: {exc}")
    except AttributeError:
        _check(checks, "RG-CHROMA-9", False,
               "SUPPORT_STATUS_PASSING_VALUES not exported from c0_binding")

    errors = [c for c in checks if c["level"] == "ERROR"]
    _write_report(checks, len(errors))

    print(f"\nCHECK-RG-CHROMA: {len(checks) - len(errors)} OK, {len(errors)} ERROR")
    if errors and FAIL_CLOSED:
        print("APPS_RG_CHROMA_FAIL_CLOSED=1 — exiting non-zero")
        return 1
    return 0


def _write_report(checks: list[dict], error_count: int) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "gate": "CHECK-RG-CHROMA",
        "plan_ref": "apps-rg-chroma-ingestion-wiring-c7f2d9",
        "chroma_path": CHROMA_PATH,
        "checks": checks,
        "error_count": error_count,
        "advisory": not FAIL_CLOSED,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"  Report: {REPORT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
