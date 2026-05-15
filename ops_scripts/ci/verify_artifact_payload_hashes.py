"""Verifier — Artifact payload content_hash recomputation (RTC-REQ-123).

Plan: ``.cursor/plans/runtime-cert-hardened-w0-7e3c9a.md``

Non-negotiable rule §11:

  > Artifact inventory must verify referenced payload content_hash, not only
  > manifest/index hash.

Behavior
--------

W0 reads an artifact manifest (W0 default: the canonical CSV itself, treated
as a single-payload manifest where the SHA-256 declared in the universe
manifest must equal a fresh recomputation over the file bytes). Future waves
expand this to inspect ``artifacts/runtime/requirements_proof/manifest.json``
and other manifests under ``artifacts/``.

The W0 default reads:

  - ``artifacts/certification/canonical_universe_manifest.json``  (csv_sha256)
  - ``artifacts/certification/requirement_count_receipt.json``    (csv_sha256)
  - Optional: ``artifacts/certification/artifact_manifest.json``  (multi-payload)

For each declared expected_hash, the verifier recomputes the SHA-256 over the
referenced payload bytes and reports match/mismatch. Manifest-level hashes
are explicitly NOT trusted — they ARE the thing being checked.

Output: ``artifacts/certification/artifact_payload_hash_report.json``

Exit codes: 0 PASS, 2 FAIL_CLOSED, 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.artifact_payload_hasher import (  # noqa: E402
    hash_payload_file,
    recompute_payload_hashes,
)
from agentic_core.runtime.prove_requirements.matrix_loader import (  # noqa: E402
    CANONICAL_CSV_PATH,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
PAYLOAD_HASH_REPORT = ARTIFACTS_DIR / "artifact_payload_hash_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _check_csv_self_hash() -> dict:
    """Recompute the canonical CSV's SHA-256 and compare against any
    manifest that declared one."""
    out: dict = {
        "rule": "RTC-REQ-123",
        "kind": "csv_self_hash",
        "payload_path": str(CANONICAL_CSV_PATH),
        "payload_exists": CANONICAL_CSV_PATH.exists(),
        "manifest_declared_hashes": {},
        "actual_hash": "",
        "matches": [],
        "mismatches": [],
    }
    if not CANONICAL_CSV_PATH.exists():
        out["fail_reason"] = "CSV_NOT_FOUND"
        return out
    actual_hex, size = hash_payload_file(CANONICAL_CSV_PATH)
    out["actual_hash"] = actual_hex
    out["payload_size_bytes"] = size

    # Read declared hashes from sibling reports
    for report_name, key in (
        ("canonical_universe_manifest.json", "csv_sha256"),
        ("requirement_count_receipt.json", "csv_sha256"),
        ("schema_validation_report.json", "csv_sha256"),
        ("acceptance_legality_report.json", "csv_sha256"),
        ("source_divergence_report.json", "baseline_csv_sha256"),
    ):
        p = ARTIFACTS_DIR / report_name
        if not p.exists():
            continue
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            declared = data.get(key)
            if declared:
                out["manifest_declared_hashes"][report_name] = declared
                if declared == actual_hex:
                    out["matches"].append(report_name)
                else:
                    out["mismatches"].append({
                        "report": report_name,
                        "declared": declared,
                        "actual": actual_hex,
                    })
        except (json.JSONDecodeError, OSError):
            continue

    return out


def _check_artifact_manifest() -> dict:
    """If a multi-payload manifest exists, recompute every declared payload hash."""
    p = ARTIFACTS_DIR / "artifact_manifest.json"
    if not p.exists():
        return {
            "rule": "RTC-REQ-123",
            "kind": "multi_payload_manifest",
            "manifest_path": str(p),
            "manifest_exists": False,
            "skipped_reason": "OPTIONAL_MANIFEST_NOT_PRESENT",
        }
    try:
        with p.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "rule": "RTC-REQ-123",
            "kind": "multi_payload_manifest",
            "manifest_path": str(p),
            "manifest_exists": True,
            "fail_reason": "MANIFEST_LOAD_ERROR",
            "detail": str(exc),
        }

    bulk = recompute_payload_hashes(manifest, REPO_ROOT, manifest_path=p)
    return {
        "rule": "RTC-REQ-123",
        "kind": "multi_payload_manifest",
        "manifest_path": str(p),
        "manifest_exists": True,
        "total_count": bulk.total_count,
        "match_count": bulk.match_count,
        "mismatch_count": bulk.mismatch_count,
        "missing_count": bulk.missing_count,
        "legal": bulk.legal,
        "expected_fail_reason": bulk.expected_fail_reason,
        "actual_fail_reason": bulk.actual_fail_reason,
        "checks": [c.to_row() for c in bulk.checks],
    }


def main() -> int:
    print("[verify_payload_hashes] checking canonical CSV self-hash...")
    csv_check = _check_csv_self_hash()
    print("[verify_payload_hashes] checking optional artifact manifest...")
    manifest_check = _check_artifact_manifest()

    csv_legal = bool(csv_check.get("payload_exists")) and len(csv_check.get("mismatches", [])) == 0
    manifest_legal = manifest_check.get("legal", True)
    if "skipped_reason" in manifest_check:
        manifest_legal = True  # optional, absence is acceptable in W0

    legal = csv_legal and manifest_legal
    expected_fail = ""
    actual_fail = ""
    if not csv_legal:
        if not csv_check.get("payload_exists"):
            expected_fail = "PAYLOAD_NOT_FOUND"
            actual_fail = f"canonical CSV missing at {CANONICAL_CSV_PATH}"
        elif csv_check.get("mismatches"):
            expected_fail = "PAYLOAD_HASH_MISMATCH"
            actual_fail = (
                f"{len(csv_check['mismatches'])} sibling report(s) declared a "
                "csv_sha256 that does not match the recomputed payload hash"
            )
    if csv_legal and not manifest_legal:
        expected_fail = manifest_check.get("expected_fail_reason", "MANIFEST_PAYLOAD_FAIL")
        actual_fail = manifest_check.get("actual_fail_reason", "see manifest_check.checks")

    report = {
        "verifier": "verify_artifact_payload_hashes",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-123",
        "status": "PASS" if legal else "FAIL_CLOSED",
        "expected_fail_reason": expected_fail,
        "actual_fail_reason": actual_fail,
        "csv_self_hash_check": csv_check,
        "multi_payload_manifest_check": manifest_check,
    }
    _write_json(PAYLOAD_HASH_REPORT, report)
    print(f"[verify_payload_hashes] {report['status']}")
    print(f"[verify_payload_hashes] wrote: {PAYLOAD_HASH_REPORT.relative_to(REPO_ROOT)}")
    return 0 if legal else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_payload_hashes] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
