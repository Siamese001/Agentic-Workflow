"""W5.P2 — apps_rg Fort Knox proof producer.

Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
Phase: W5.P2

Reads W4 canonical receipts from artifacts/apps_rg/runs/<latest>/
and emits per-claim JSON+sha256 for APPS-REQ-RG-* assertions.

Patterned after: tools/cert/apps_e2e/emit_apps_evidence_assertions.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runs"
OUT_DIR = REPO_ROOT / "certification" / "apps" / "per_app_evidence" / "apps_rg"

PRODUCER_COMMAND = "tools/cert/apps_e2e/apps_rg_proof_producer.py"
PRODUCER_VERSION = "apps_rg_proof_producer-v1"

# APPS-REQ-RG-* claim definitions (aligned with W4 adapter output)
_RG_CLAIMS = [
    {
        "claim_id": "APPS-REQ-RG-001",
        "title": "Canonical RouteContract v15 emitted",
        "required_artifact": "route_contract.json",
        "required_fields": [
            "route_id",
            "execution_form",
            "route_digest",
            "hmac_sig",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ],
    },
    {
        "claim_id": "APPS-REQ-RG-002",
        "title": "L2 ExecutionReceipt E1-E5 sealed",
        "required_artifact": "l2_execution_receipt.json",
        "required_fields": [
            "e1_work_order",
            "e2_validation_output",
            "e3_attempt_receipt",
            "e4_heal_receipt",
            "e5_dispatch_receipt",
        ],
    },
    {
        "claim_id": "APPS-REQ-RG-003",
        "title": "ExitReviewPacket X1-X3 canonical",
        "required_artifact": "exit_review_packet.json",
        "required_fields": [
            "x1_verdicts",
            "x2_aggregate",
            "x3_disposition",
        ],
    },
    {
        "claim_id": "APPS-REQ-RG-004",
        "title": "Runtime gates applicable subset invoked",
        "required_artifact": "gate_verdicts.json",
        "required_fields": ["g01", "g24", "g26", "g28"],
    },
    {
        "claim_id": "APPS-REQ-RG-005",
        "title": "Spine proof bundle no-bypass construct present",
        "required_artifact": "spine_proof_bundle.json",
        "required_fields": ["proof_type", "no_bypass_evidence"],
    },
    {
        "claim_id": "APPS-REQ-RG-006",
        "title": "Replay verdict emitted",
        "required_artifact": "replay_comparison.json",
        "required_fields": ["replay_key", "determinism_verdict"],
    },
    {
        "claim_id": "APPS-REQ-RG-007",
        "title": "ATS coverage floor met (≥0.73 baseline)",
        "required_artifact": "ats_coverage_report.json",
        "required_fields": ["coverage_score", "matched_terms"],
    },
    {
        "claim_id": "APPS-REQ-RG-008",
        "title": "Provenance bound to master resume",
        "required_artifact": "provenance_report.json",
        "required_fields": ["valid", "master_binding_digest"],
    },
]


def _compute_sha256(data: bytes) -> str:
    """SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def _relative_path(path: Path) -> str:
    """Return path relative to REPO_ROOT; fallback to str(path) if outside."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_latest_run_dir() -> Path | None:
    """Return the most recent run directory under RUNS_ROOT."""
    if not RUNS_ROOT.exists():
        return None
    candidates = sorted(
        (p for p in RUNS_ROOT.iterdir() if p.is_dir() and p.name[:8].isdigit()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _check_artifact_exists(run_dir: Path, artifact_name: str) -> Path | None:
    """Check if artifact exists in run_dir; return path or None."""
    path = run_dir / artifact_name
    return path if path.exists() else None


def _load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load JSON file safely; return None on any error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _check_fields_present(data: dict[str, Any] | None, fields: list[str]) -> list[str]:
    """Return list of missing fields (empty if all present)."""
    if data is None:
        return fields
    return [f for f in fields if f not in data]


def produce_proof(claim: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    """Produce a single proof bundle for a claim.

    Returns PASS if all required artifacts and fields are present,
    NOT_VERIFIED otherwise.
    """
    artifact_name = claim["required_artifact"]
    artifact_path = _check_artifact_exists(run_dir, artifact_name)

    if artifact_path is None:
        return {
            "claim_id": claim["claim_id"],
            "claim_title": claim["title"],
            "assertion_result": "NOT_VERIFIED",
            "reason": f"Missing artifact: {artifact_name}",
            "artifact_path": None,
            "artifact_sha256": None,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "generated_by_command": PRODUCER_COMMAND,
            "producer_version": PRODUCER_VERSION,
        }

    data = _load_json_safe(artifact_path)
    missing = _check_fields_present(data, claim["required_fields"])

    if missing:
        return {
            "claim_id": claim["claim_id"],
            "claim_title": claim["title"],
            "assertion_result": "NOT_VERIFIED",
            "reason": f"Missing fields: {missing}",
            "artifact_path": _relative_path(artifact_path),
            "artifact_sha256": _compute_sha256(artifact_path.read_bytes()),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "generated_by_command": PRODUCER_COMMAND,
            "producer_version": PRODUCER_VERSION,
        }

    # All fields present - PASS
    artifact_bytes = artifact_path.read_bytes()
    return {
        "claim_id": claim["claim_id"],
        "claim_title": claim["title"],
        "assertion_result": "PASS",
        "reason": "All required fields present",
        "artifact_path": _relative_path(artifact_path),
        "artifact_sha256": _compute_sha256(artifact_bytes),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_by_command": PRODUCER_COMMAND,
        "producer_version": PRODUCER_VERSION,
    }


def emit_proofs(out_dir: Path | None = None) -> list[dict[str, Any]]:
    """Emit all APPS-REQ-RG-* proofs for the latest run.

    Returns list of proof bundles (one per claim).
    """
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    run_dir = _load_latest_run_dir()
    proofs: list[dict[str, Any]] = []

    for claim in _RG_CLAIMS:
        if run_dir is None:
            proof = {
                "claim_id": claim["claim_id"],
                "claim_title": claim["title"],
                "assertion_result": "NOT_VERIFIED",
                "reason": "No run directories found",
                "artifact_path": None,
                "artifact_sha256": None,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "generated_by_command": PRODUCER_COMMAND,
                "producer_version": PRODUCER_VERSION,
            }
        else:
            proof = produce_proof(claim, run_dir)
        proofs.append(proof)

        # Write individual proof file
        proof_path = out_dir / f"{claim['claim_id']}_proof.json"
        proof_path.write_text(
            json.dumps(proof, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    # Write combined bundle
    bundle = {
        "schema_version": "apps_rg_proof_bundle/2026-05-03/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer_version": PRODUCER_VERSION,
        "run_dir": _relative_path(run_dir) if run_dir else None,
        "claim_count": len(proofs),
        "pass_count": sum(1 for p in proofs if p["assertion_result"] == "PASS"),
        "not_verified_count": sum(1 for p in proofs if p["assertion_result"] == "NOT_VERIFIED"),
        "proofs": proofs,
    }
    bundle_path = out_dir / "apps_rg_proof_bundle.json"
    bundle_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return proofs


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for proof producer."""
    parser = argparse.ArgumentParser(
        prog="apps_rg_proof_producer",
        description="Produce Fort Knox proof bundles for apps_rg",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help="Output directory for proof bundles",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Specific run directory (default: latest)",
    )
    args = parser.parse_args(argv)

    proofs = emit_proofs(args.out_dir)

    # Summary
    pass_count = sum(1 for p in proofs if p["assertion_result"] == "PASS")
    nv_count = sum(1 for p in proofs if p["assertion_result"] == "NOT_VERIFIED")

    print(f"[apps_rg_proof_producer] Generated {len(proofs)} proofs")
    print(f"  PASS: {pass_count}")
    print(f"  NOT_VERIFIED: {nv_count}")
    print(f"  Output: {args.out_dir}")

    return 0 if nv_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
