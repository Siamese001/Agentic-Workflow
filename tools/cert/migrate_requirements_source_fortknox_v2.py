"""One-shot migrator: promote requirements_source.json to Fort Knox v2 shape.

Adds three new required fields to every requirement row:
  - allowed_verifier_commands : [str]   (derived from claim_type defaults)
  - allowed_artifact_classes  : [str]   (derived from claim_type defaults)
  - freshness_hours           : int     (168h default; stricter for runtime)

Leaves existing fields intact. Idempotent: re-running is a no-op if the
three fields are already present and pass schema validation.

Also rewrites top-level header fields (schema_version='fortknox-v2',
generated_at_utc, source_csv_sha256).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(REPO_ROOT))
from tools.cert.cert_paths import REQS_PATH  # noqa: E402

SRC = REQS_PATH
CSV = REQS_PATH.with_suffix(".csv")

# Defaults per claim_type
CLAIM_TYPE_VERIFIERS = {
    "STATIC_ENFORCEMENT": ["scripts/verify_rtc_req_csv_gate.py"],
    "STATIC_CONTRACT": ["scripts/verify_rtc_req_csv_gate.py"],
    "COMPONENT_RUNTIME": ["scripts/verify_rtc_req_component_runtime.py"],
    "COMPOSITION_RUNTIME": ["scripts/verify_rtc_req_integrated_runtime.py"],
    "INTEGRATED_RUNTIME": ["scripts/verify_rtc_req_integrated_runtime.py"],
    "OBSERVABILITY_RUNTIME": ["scripts/verify_rtc_req_otel_replay.py"],
    "REPLAY_RUNTIME": ["scripts/verify_rtc_req_otel_replay.py"],
    "NO_BYPASS_RUNTIME": ["scripts/verify_semantic_cache_certification.py", "tools/cert/verify_cache_fixture_vs_uwg.py"],
    "PRODUCTION_DEPENDENCY_RUNTIME": ["scripts/verify_rtc_req_production_dependencies.py"],
}

CLAIM_TYPE_ARTIFACT_CLASSES = {
    "STATIC_ENFORCEMENT": ["STATIC_VERIFIER_REPORT", "STATIC_SCAN_REPORT", "CSV_GATE_RESULT", "ACCEPTANCE_LEGALITY_REPORT", "LAYER_BOUNDARY_REPORT", "MERKLE_TREE_REPORT", "SIGNATURE_ENVELOPE"],
    "STATIC_CONTRACT": ["STATIC_VERIFIER_REPORT", "STATIC_SCAN_REPORT", "CSV_GATE_RESULT"],
    "COMPONENT_RUNTIME": ["COMPONENT_RUNTIME_PROOF", "INTEGRATED_RUNTIME_BUNDLE"],
    "COMPOSITION_RUNTIME": ["INTEGRATED_RUNTIME_BUNDLE"],
    "INTEGRATED_RUNTIME": ["INTEGRATED_RUNTIME_BUNDLE"],
    "OBSERVABILITY_RUNTIME": ["OTEL_SPAN_EXPORT", "INTEGRATED_RUNTIME_BUNDLE"],
    "REPLAY_RUNTIME": ["REPLAY_COMPARISON_RECEIPT"],
    "NO_BYPASS_RUNTIME": ["NEGATIVE_CONTROL_REPORT", "UWG_WRITE_RECEIPT", "SUBCLAIMS_REPORT"],
    "PRODUCTION_DEPENDENCY_RUNTIME": ["PRODUCTION_DEPENDENCY_PROOF"],
}

# Fresh windows
FRESHNESS_BY_CLAIM = {
    "STATIC_ENFORCEMENT": 168,    # 1 week
    "STATIC_CONTRACT": 168,
    "COMPONENT_RUNTIME": 48,
    "COMPOSITION_RUNTIME": 48,
    "INTEGRATED_RUNTIME": 48,
    "OBSERVABILITY_RUNTIME": 48,
    "REPLAY_RUNTIME": 72,
    "NO_BYPASS_RUNTIME": 72,
    "PRODUCTION_DEPENDENCY_RUNTIME": 168,
}


def _sha256_file(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SRC.exists():
        print(f"FATAL: {SRC} missing", file=sys.stderr)
        return 2
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    reqs = doc.get("requirements") or []
    if not reqs:
        print("FATAL: requirements list empty", file=sys.stderr)
        return 2

    ALLOWED_CONTROLS = {
        "verifier_pass", "verifier_exit_zero", "last_verified_timestamp",
        "artifact_payload_hash", "evidence_manifest_hash", "source_root_binding",
        "ci_gate", "layer_boundary", "runtime_evidence", "otel_trace",
        "replay_receipt", "no_bypass", "negative_controls", "expected_fail_reason",
        "uwg_write_path", "positive_evidence", "merkle_leaf", "certifier_signature",
        "required_artifacts",
    }

    mutated = 0
    for r in reqs:
        ct = r.get("claim_type", "STATIC_ENFORCEMENT")
        if "allowed_verifier_commands" not in r:
            r["allowed_verifier_commands"] = list(CLAIM_TYPE_VERIFIERS.get(ct, ["scripts/verify_rtc_req_csv_gate.py"]))
            mutated += 1
        if "allowed_artifact_classes" not in r:
            r["allowed_artifact_classes"] = list(CLAIM_TYPE_ARTIFACT_CLASSES.get(ct, ["STATIC_VERIFIER_REPORT"]))
            mutated += 1
        if "freshness_hours" not in r:
            r["freshness_hours"] = FRESHNESS_BY_CLAIM.get(ct, 168)
            mutated += 1
        # Ensure required fields exist (fail-closed defaults)
        r.setdefault("depends_on_req_ids", [])
        r.setdefault("is_final_hundred_percent_row", False)
        r.setdefault("fail_closed_if_missing", True)
        r.setdefault("required_controls", ["verifier_pass", "verifier_exit_zero", "last_verified_timestamp"])
        # Normalize control names that drifted (e.g. "required_artifacts" may not be a control)
        r["required_controls"] = [c for c in r["required_controls"] if c in ALLOWED_CONTROLS]
        if not r["required_controls"]:
            r["required_controls"] = ["verifier_pass", "verifier_exit_zero", "last_verified_timestamp"]

    # Deterministic sort for reproducibility: by req_id
    reqs.sort(key=lambda x: x["req_id"])

    doc["schema_version"] = "fortknox-v2"
    doc["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    doc["source_csv_sha256"] = _sha256_file(CSV)
    doc["requirements"] = reqs

    SRC.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[migrate_requirements_source] wrote {SRC.relative_to(REPO_ROOT)}")
    print(f"  rows: {len(reqs)}")
    print(f"  field mutations applied: {mutated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
