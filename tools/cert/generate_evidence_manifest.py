"""J0.3 — Generate `evidence_manifest.jsonl`.

One JSON object per line. Each object describes ONE artifact:
  - path
  - sha256
  - exists
  - size_bytes
  - mtime_utc
  - linked_req_ids   (which RTC-REQ this artifact attests)
  - verifier_command  (how it was produced, if known)
  - verifier_exit_code (last known)
  - verifier_version
  - fresh_within_hours (declared SLA)

The compiler reads this manifest to verify artifact existence, hash,
linkage, and freshness for each requirement's required_controls.

Linkage map below is the SSOT for which artifacts attest which reqs.
Adding a new artifact -> append entry. Adding a new req -> add it to
linked_req_ids of the relevant artifacts.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from cert_paths import EVIDENCE_MANIFEST_PATH as OUT_PATH

# Linkage map: artifact_relpath -> {linked_req_ids, verifier_command, ...}
LINKAGE: dict[str, dict] = {
    # Matrix governance / static enforcement
    "artifacts/certification/rtc_req_csv_gate_result.json": {
        "linked_req_ids": [
            "RTC-REQ-001", "RTC-REQ-002", "RTC-REQ-003", "RTC-REQ-004",
            "RTC-REQ-005", "RTC-REQ-006", "RTC-REQ-030", "RTC-REQ-033",
            "RTC-REQ-110", "RTC-REQ-111", "RTC-REQ-127",
        ],
        "verifier_command": "scripts/verify_rtc_req_csv_gate.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/rtc_req_csv_merkle_root.json": {
        "linked_req_ids": ["RTC-REQ-031"],
        "verifier_command": "scripts/verify_all_requirements_merkle_root.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/rtc_req_csv_merkle_leaves.json": {
        "linked_req_ids": ["RTC-REQ-031"],
        "verifier_command": "scripts/verify_all_requirements_merkle_root.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/downgraded_rows_report.json": {
        "linked_req_ids": ["RTC-REQ-034"],
        "verifier_command": "scripts/verify_runtime_certification_acceptance.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # Integrated runtime R1B
    "artifacts/certification/rtc_req_integrated_runtime_report.json": {
        "linked_req_ids": [
            "RTC-REQ-010", "RTC-REQ-011", "RTC-REQ-012", "RTC-REQ-013",
            "RTC-REQ-014", "RTC-REQ-015", "RTC-REQ-072", "RTC-REQ-092",
            "RTC-REQ-095", "RTC-REQ-101", "RTC-REQ-114", "RTC-REQ-120",
            "RTC-REQ-065",
        ],
        "verifier_command": "scripts/verify_rtc_req_integrated_runtime.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/integrated_runtime/latest/runtime_exhaust_bundle.json": {
        "linked_req_ids": [
            "RTC-REQ-010", "RTC-REQ-011", "RTC-REQ-012", "RTC-REQ-013",
            "RTC-REQ-014", "RTC-REQ-015", "RTC-REQ-055", "RTC-REQ-065",
            "RTC-REQ-072", "RTC-REQ-092", "RTC-REQ-095", "RTC-REQ-120",
        ],
        "verifier_command": "scripts/verify_rtc_req_integrated_runtime.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/r1b_terminal_exit_proof.json": {
        "linked_req_ids": ["RTC-REQ-055", "RTC-REQ-096"],
        "verifier_command": "scripts/verify_rtc_req_integrated_runtime.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # OTEL + Replay
    "artifacts/certification/rtc_req_otel_replay_report.json": {
        "linked_req_ids": ["RTC-REQ-021", "RTC-REQ-023", "RTC-REQ-024", "RTC-REQ-114"],
        "verifier_command": "scripts/verify_rtc_req_otel_replay.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/integrated_runtime/replay/replay_pair_receipt.json": {
        "linked_req_ids": ["RTC-REQ-023", "RTC-REQ-114"],
        "verifier_command": "scripts/verify_rtc_req_otel_replay.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/integrated_runtime/replay/replay_mutation_negative_receipt.json": {
        "linked_req_ids": ["RTC-REQ-024"],
        "verifier_command": "scripts/verify_rtc_req_otel_replay.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # Semantic cache
    "artifacts/certification/semantic_cache_subclaims.json": {
        "linked_req_ids": [
            "RTC-REQ-040", "RTC-REQ-047", "RTC-REQ-048", "RTC-REQ-049",
            "RTC-REQ-050", "RTC-REQ-051", "RTC-REQ-052", "RTC-REQ-053",
            "RTC-REQ-054", "RTC-REQ-061", "RTC-REQ-062", "RTC-REQ-064",
        ],
        "verifier_command": "scripts/verify_semantic_cache_certification.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/semantic_cache_negative_controls.json": {
        "linked_req_ids": [
            "RTC-REQ-047", "RTC-REQ-048", "RTC-REQ-049", "RTC-REQ-050",
            "RTC-REQ-051", "RTC-REQ-052", "RTC-REQ-053", "RTC-REQ-054",
        ],
        "verifier_command": "scripts/verify_semantic_cache_certification.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/semantic_cache_certification_report.json": {
        "linked_req_ids": ["RTC-REQ-100"],
        "verifier_command": "scripts/verify_semantic_cache_certification.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # Cache state safety
    "artifacts/certification/cache_fixture_vs_uwg_proof.json": {
        "linked_req_ids": [
            "RTC-REQ-060", "RTC-REQ-061", "RTC-REQ-062", "RTC-REQ-063",
            "RTC-REQ-064", "RTC-REQ-066", "RTC-REQ-070", "RTC-REQ-071",
            "RTC-REQ-073",
        ],
        "verifier_command": "tools/cert/verify_cache_fixture_vs_uwg.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/l4_cache_state_schema_proof.json": {
        "linked_req_ids": ["RTC-REQ-060", "RTC-REQ-066", "RTC-REQ-067", "RTC-REQ-073"],
        "verifier_command": "tools/cert/verify_l4_cache_state_schema.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # Control surface + payload hash + source divergence
    "artifacts/certification/control_surface_separation_report.json": {
        "linked_req_ids": [
            "RTC-REQ-032", "RTC-REQ-070", "RTC-REQ-071", "RTC-REQ-097", "RTC-REQ-123",
        ],
        "verifier_command": "scripts/verify_control_surface_separation.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/artifact_payload_hash_report.json": {
        "linked_req_ids": ["RTC-REQ-123", "RTC-REQ-124"],
        "verifier_command": "scripts/verify_artifact_payload_hashes.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/source_divergence_report.json": {
        "linked_req_ids": ["RTC-REQ-032", "RTC-REQ-091", "RTC-REQ-093", "RTC-REQ-094"],
        "verifier_command": "scripts/verify_source_divergence.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    "artifacts/certification/acceptance_legality_report.json": {
        "linked_req_ids": [
            "RTC-REQ-082", "RTC-REQ-121", "RTC-REQ-122",
        ],
        "verifier_command": "scripts/verify_runtime_certification_acceptance.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
    # Reporting language discipline
    "artifacts/certification/w0_language_discipline_report.json": {
        "linked_req_ids": ["RTC-REQ-102", "RTC-REQ-103"],
        "verifier_command": "scripts/verify_w0_language_discipline.py",
        "verifier_version": "v1.0",
        "fresh_within_hours": 168,
    },
}


def _utc_iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat(timespec="seconds")


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _last_exit_code(verifier_command: str) -> int | None:
    """Re-run the verifier and capture exit code (best-effort, fail-soft).

    Timeout = 600s (10min) to accommodate slow verifiers like
    verify_all_requirements_merkle_root.py and tier_gate_hardening.
    """
    try:
        r = subprocess.run([sys.executable, verifier_command], cwd=REPO_ROOT,
                           capture_output=True, timeout=600)
        return r.returncode
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def main() -> int:
    import argparse
    ap_args = argparse.ArgumentParser()
    ap_args.add_argument("--run-verifiers", action="store_true",
                         help="Re-run each verifier to capture current exit code (slower)")
    args = ap_args.parse_args()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = []
    # Cache one exit code per unique verifier_command to avoid re-running it
    # for every artifact that shares the same verifier.
    exit_cache: dict[str, int | None] = {}
    for relpath, meta in sorted(LINKAGE.items()):
        ap = REPO_ROOT / relpath
        exists = ap.exists()
        cmd = meta.get("verifier_command")
        exit_code = None
        if args.run_verifiers and cmd:
            if cmd in exit_cache:
                exit_code = exit_cache[cmd]
            else:
                exit_code = _last_exit_code(cmd)
                exit_cache[cmd] = exit_code
        rec = {
            "schema_version": "1.0",
            "path": relpath,
            "exists": exists,
            "sha256": _file_sha256(ap) if exists else "",
            "size_bytes": ap.stat().st_size if exists else 0,
            "mtime_utc": _utc_iso(ap.stat().st_mtime) if exists else None,
            "linked_req_ids": meta["linked_req_ids"],
            "verifier_command": cmd,
            "verifier_version": meta.get("verifier_version"),
            "verifier_exit_code": exit_code,
            "fresh_within_hours": meta.get("fresh_within_hours"),
            "manifest_recorded_at_utc": _utc_now_iso(),
        }
        records.append(rec)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    n_exists = sum(1 for r in records if r["exists"])
    print(f"[generate_evidence_manifest] wrote {len(records)} records to {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  artifacts present: {n_exists}/{len(records)}")
    print(f"  artifacts missing: {len(records) - n_exists}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
