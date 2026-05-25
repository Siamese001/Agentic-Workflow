"""J0.1 — Generate `requirements_source.json` from the canonical CSV.

This is the canonical declarative universe consumed by
scripts/compile_requirement_signoff.py. ONE object per RTC-REQ,
fields per operator spec.

Output: certification/requirements_source.json (sorted, deterministic).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_CSV = Path(
    r"C:\Users\amita\Downloads\runtime_certification_requirements_100_percent_hardened.csv"
)
from cert_paths import REQS_PATH as OUT_JSON

# Per-claim_type required controls. Matches tools/cert/required_evidence_matrix.yaml
# but expressed in absolute control names the compiler understands.
PER_CLAIM_TYPE_REQUIRED_CONTROLS = {
    "MATRIX_GOVERNANCE":            ["ci_gate"],
    "STATIC_ENFORCEMENT":           ["ci_gate", "layer_boundary"],
    "STATIC_CONTRACT":              ["required_artifacts", "artifact_payload_hash"],
    "COMPONENT_RUNTIME":            ["runtime_evidence", "evidence_manifest_hash"],
    "INTEGRATED_RUNTIME":           ["runtime_evidence", "otel_trace", "source_root_binding", "artifact_payload_hash"],
    "NO_BYPASS_RUNTIME":            ["no_bypass", "runtime_evidence"],
    "COMPOSITION_RUNTIME":          ["runtime_evidence", "positive_evidence"],
    "OBSERVABILITY_RUNTIME":        ["otel_trace"],
    "REPLAY_RUNTIME":               ["replay_receipt"],
    "PRODUCTION_DEPENDENCY_RUNTIME": ["runtime_evidence", "certifier_signature"],
}

# Reqs that are "final 100% rows" — must wait for all dependencies to be SIGNED_OFF
# before they can sign off themselves. Detected by requirement_group="100 Percent Standard"
# or req_id in the explicit list below.
FINAL_HUNDRED_PERCENT_GROUPS = {"100 Percent Standard"}


def _split_csv_field(s: str) -> list[str]:
    """Split a multi-value CSV cell. Empty cells return []."""
    if not s:
        return []
    return [tok.strip() for tok in s.replace(";", "\n").split("\n") if tok.strip()]


def main() -> int:
    if not SRC_CSV.exists():
        print(f"FATAL: source CSV not found at {SRC_CSV}", file=sys.stderr)
        return 2
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(SRC_CSV, encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        rows = list(rdr)

    requirements = []
    for r in rows:
        ct = (r.get("claim_type") or "").strip()
        required_controls = list(PER_CLAIM_TYPE_REQUIRED_CONTROLS.get(ct, []))
        # Universal controls every row needs:
        universal = ["verifier_pass", "verifier_exit_zero", "last_verified_timestamp"]
        # Negative-control universe — only the actual negative-control rows.
        # Heuristic: title contains "negative" AND claim_type is NO_BYPASS or REPLAY.
        title_lower = (r.get("requirement_title", "") or "").lower()
        is_negative_row = ("negative" in title_lower
                           and ct in ("NO_BYPASS_RUNTIME", "REPLAY_RUNTIME"))
        if is_negative_row:
            required_controls.append("negative_controls")
            required_controls.append("expected_fail_reason")
        # Merkle leaf only for the gate+merkle row.
        if r["req_id"].strip() == "RTC-REQ-031":
            required_controls.append("merkle_leaf")
        # UWG write path only for explicit UWG / cache rows.
        if ("uwg" in title_lower or "durable write" in title_lower
                or r["req_id"].strip() in ("RTC-REQ-064", "RTC-REQ-070", "RTC-REQ-071", "RTC-REQ-072")):
            required_controls.append("uwg_write_path")

        is_final_hundred = (r.get("requirement_group", "").strip() in FINAL_HUNDRED_PERCENT_GROUPS)

        entry = {
            "req_id": r["req_id"].strip(),
            "title": (r.get("requirement_title") or "").strip(),
            "priority": (r.get("priority") or "").strip(),
            "requirement_group": (r.get("requirement_group") or "").strip(),
            "owner_layer": (r.get("owner_layer") or "").strip(),
            "owner_component": (r.get("owner_component") or "").strip(),
            "claim_type": ct,
            "required_proof_depth": (r.get("required_proof_depth") or "").strip(),
            "acceptance_rule": (r.get("acceptance_rule") or "").strip(),
            "required_controls": universal + required_controls,
            "required_artifacts": _split_csv_field(r.get("required_artifacts", "")),
            "required_ci_gate": (r.get("required_ci_gate") or "").strip(),
            "fail_closed_if_missing": (r.get("fail_closed_if_missing", "true").strip().lower() != "false"),
            "is_final_hundred_percent_row": is_final_hundred,
            "depends_on_req_ids": _split_csv_field(r.get("depends_on_req_ids", "")),
        }
        requirements.append(entry)

    requirements.sort(key=lambda x: x["req_id"])

    payload = {
        "schema_version": "1.0",
        "purpose": (
            "Canonical requirement universe for runtime certification. SSOT "
            "consumed by scripts/compile_requirement_signoff.py. Derived from "
            "runtime_certification_requirements_100_percent_hardened.csv."
        ),
        "generator": "tools/cert/generate_requirements_source.py",
        "requirement_count": len(requirements),
        "claim_type_required_controls": PER_CLAIM_TYPE_REQUIRED_CONTROLS,
        "final_hundred_percent_groups": sorted(FINAL_HUNDRED_PERCENT_GROUPS),
        "requirements": requirements,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[generate_requirements_source] wrote {len(requirements)} reqs to {OUT_JSON.relative_to(REPO_ROOT)}")
    by_ct: dict[str, int] = {}
    for r in requirements:
        by_ct[r["claim_type"]] = by_ct.get(r["claim_type"], 0) + 1
    for ct, n in sorted(by_ct.items()):
        print(f"  {ct:<30} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
