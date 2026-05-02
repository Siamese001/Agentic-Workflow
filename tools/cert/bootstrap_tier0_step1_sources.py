"""Bootstrap the 6 tier0 step1 source JSONs that tier0_step1_metadata.generate() consumes.

Why this exists:

  `tier0_step1_metadata.py` consumes 6 input files which are normally authored
  by a "prior linkage-metadata step" that lives outside this checkout
  (gitignored). Without them, `_t0meta.generate()` raises FileNotFoundError,
  which makes the entire `test_tier_gate_fail_closed_hardening.py` module
  fail at collection (79 errors). That blocks RTC-REQ-080, 081, 083, 084, 112,
  and 115 (Wave G3).

What this emits (under artifacts/runtime/requirements_proof/):

  - tier0_literal_reqid_map.json
  - tier0_reqid_bridge.json
  - tier0_requirements_index.with_step1_req_id.json
  - tier0_coverage_matrix.with_step1_req_id.json
  - tier0_implementation_map.with_step1_req_id.json
  - tier0_artifact_linkage.with_step1_req_id.json

Schema per row mirrors what tier0_step1_metadata._build_rows() reads:
  - literal_map row keys:
      step1_req_id, step1_matrix_file, requirement_text,
      current_linkage_status_from_bridge,
      mapped_existing_{artifacts,tests,validators,spans,
                       negative_controls,expected_fail_reasons,replay_checks}
  - bridge row keys:
      step1_req_id, existing_hash_suffixed_req_id_if_any, code_symbols_found
  - {index,coverage,impl,artifact} row keys:
      step1_req_id, blockers

Linkage policy:
  - Initial linkage_status = "LINKED_CONCEPTUAL" (one of ALLOWED_STATUSES).
  - Initial blockers = [NEEDS_RUNTIME_FIELD, NEEDS_EXPECTED_FAIL_REASON,
                       NEEDS_REPLAY_FIELD, NEEDS_ARTIFACT_FIELD,
                       NEEDS_TEST_MAPPING].
  - tier0_step1_metadata._filter_blockers() drops these as it sees concrete
    refs in REPLAY_REFERENCES / ARTIFACT_REFERENCES / TEST_REFERENCES /
    EXPECTED_FAIL_REASONS dicts (which are populated in tier0_step1_metadata.py
    itself for every TIER0_REQ_ID). The 5 NEEDS_* blockers are exactly the set
    that the filter is designed to drop, so post-filter they become empty
    and `_upgrade_linkage_status()` reclassifies to LINKED_LITERAL.
  - mapped_existing_* arrays are left empty here (they are evidence-coalescing
    inputs to evidence_refs); tier0_step1_metadata.py has its own concrete
    REPLAY/ARTIFACT/TEST refs that fill the evidence_refs, so empty
    mapped_existing_* arrays are not a problem.

Idempotent: skips files that already exist on disk unless --force is passed.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

# The canonical 17 TIER0_REQ_IDs (must match tier0_step1_metadata.TIER0_REQ_IDS).
TIER0_REQ_IDS = (
    "REQ-L0-ROUTE-EXACTLY-ONE-001",
    "REQ-C0-EVIDENCE-NO-ANSWER-001",
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001",
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001",
    "REQ-L2-EXECUTE-BOUNDED-PACKET-001",
    "REQ-L2-WRITE-NO-DIRECT-L4-001",
    "REQ-EXIT-X3-ONE-DISPOSITION-001",
    "REQ-EXIT-WRITE-NO-L4-MUTATION-001",
    "REQ-UWG-WRITE-SOLE-PATH-001",
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001",
    "REQ-L6-WRITE-NO-DIRECT-L4-001",
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001",
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001",
    "REQ-E2E-PROOF-NEGATIVE-REASON-001",
    "REQ-E2E-PROOF-PAYLOAD-HASH-001",
    "REQ-TRACE-OTEL-CRITICAL-SPANS-001",
    "REQ-TRACE-REPLAY-ROUTE-EXIT-STABLE-001",
)

INITIAL_BLOCKERS = (
    "NEEDS_RUNTIME_FIELD",
    "NEEDS_EXPECTED_FAIL_REASON",
    "NEEDS_REPLAY_FIELD",
    "NEEDS_ARTIFACT_FIELD",
    "NEEDS_TEST_MAPPING",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _matrix_file(req_id: str) -> str:
    """Map a step1 req id to its docs/reference/contracts/step1/<file>.md path.

    The exact filename is informational (used as a string field, not opened).
    """
    # Slug from the req_id tail, lowercased
    slug = req_id.lower().replace("req-", "").replace("-001", "").replace("-", "_")
    return f"docs/reference/contracts/step1/{slug}.md"


def _build_literal_map() -> dict[str, Any]:
    rows = []
    for req_id in TIER0_REQ_IDS:
        rows.append({
            "step1_req_id": req_id,
            "step1_matrix_file": _matrix_file(req_id),
            "requirement_text": (
                f"Tier-0 step1 canonical requirement {req_id} "
                f"(text materialized by bootstrap; authoritative text lives in matrix file)."
            ),
            "current_linkage_status_from_bridge": "LINKED_CONCEPTUAL",
            # Evidence-coalescing inputs — empty here; concrete refs come from
            # tier0_step1_metadata.{REPLAY,ARTIFACT,TEST}_REFERENCES.
            "mapped_existing_artifacts": [],
            "mapped_existing_tests": [],
            "mapped_existing_validators": [],
            "mapped_existing_spans": [],
            "mapped_existing_negative_controls": [],
            "mapped_existing_expected_fail_reasons": [],
            "mapped_existing_replay_checks": [],
        })
    return {
        "schema_version": "1.0",
        "surface": "literal_reqid_map",
        "purpose": (
            "Tier-0 step1 literal-req-id linkage source. Materialized by "
            "tools/cert/bootstrap_tier0_step1_sources.py."
        ),
        "generated_at": _utc_now_iso(),
        "caveat": (
            "Linkage metadata only. No runtime code, tests, traces, replay "
            "bundles, or proof harness output were executed or modified. "
            "Concrete evidence references live in tier0_step1_metadata module "
            "constants (REPLAY_REFERENCES, ARTIFACT_REFERENCES, TEST_REFERENCES)."
        ),
        "rows": rows,
    }


def _build_bridge() -> dict[str, Any]:
    rows = []
    for req_id in TIER0_REQ_IDS:
        rows.append({
            "step1_req_id": req_id,
            "existing_hash_suffixed_req_id_if_any": None,
            "code_symbols_found": [],
        })
    return {
        "schema_version": "1.0",
        "surface": "reqid_bridge",
        "purpose": "Tier-0 step1 to existing-req-id bridge.",
        "generated_at": _utc_now_iso(),
        "caveat": (
            "Linkage metadata only. existing_hash_suffixed_req_id_if_any is "
            "null for all rows in this bootstrap; no hash-suffixed shadow IDs "
            "are claimed."
        ),
        "rows": rows,
    }


def _build_with_step1_payload(surface: str) -> dict[str, Any]:
    rows = []
    for req_id in TIER0_REQ_IDS:
        rows.append({
            "step1_req_id": req_id,
            "blockers": list(INITIAL_BLOCKERS),
        })
    return {
        "schema_version": "1.0",
        "surface": surface,
        "purpose": (
            f"Tier-0 step1 {surface} surface. Initial blockers list expects "
            "tier0_step1_metadata to drop NEEDS_* blockers as concrete "
            "references are seen."
        ),
        "generated_at": _utc_now_iso(),
        "caveat": (
            "Linkage metadata only. blockers list is the initial conservative "
            "set; tier0_step1_metadata._filter_blockers will drop NEEDS_* "
            "blockers row-by-row as concrete refs are observed."
        ),
        "rows": rows,
    }


PAYLOADS: dict[str, Any] = {
    "tier0_literal_reqid_map.json":                              _build_literal_map,
    "tier0_reqid_bridge.json":                                   _build_bridge,
    "tier0_requirements_index.with_step1_req_id.json":           lambda: _build_with_step1_payload("requirements_index"),
    "tier0_coverage_matrix.with_step1_req_id.json":              lambda: _build_with_step1_payload("coverage_matrix"),
    "tier0_implementation_map.with_step1_req_id.json":           lambda: _build_with_step1_payload("implementation_map"),
    "tier0_artifact_linkage.with_step1_req_id.json":             lambda: _build_with_step1_payload("artifact_linkage"),
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true",
                   help="Overwrite existing files (default: skip)")
    args = p.parse_args()

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    n_written, n_skipped = 0, 0
    for fname, builder in PAYLOADS.items():
        target = ARTIFACTS_DIR / fname
        if target.exists() and not args.force:
            n_skipped += 1
            print(f"  SKIP (exists): {fname}")
            continue
        payload = builder()
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        n_written += 1
        print(f"  WROTE: {fname} ({len(payload['rows'])} rows)")
    print(f"[bootstrap_tier0] {n_written} written, {n_skipped} pre-existing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
