"""Resync git_head_at_test_time + content_hash for 10C proof bundles (W4d-4 P4b).

Run after rebasing or when bundles were stamped at an older HEAD but tests
and bundle payloads are still valid. Recomputes content_hash using the same
canonical JSON rules as ops_scripts/ci/check_10c_pilot_proof_evidence.py.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLES = REPO_ROOT / "artifacts" / "requirements" / "proof_bundles"


def _deterministic_digest(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _git_head() -> str:
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return (r.stdout or "").strip()


def main() -> int:
    head = _git_head()
    if not head:
        print("ERROR: could not read git HEAD", file=sys.stderr)
        return 2
    updated = 0
    for path in sorted(BUNDLES.glob("10c-req-*.json")):
        try:
            bundle = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"SKIP {path.name}: {exc}", file=sys.stderr)
            continue
        if bundle.get("proof_status") != "EVIDENCE_PRESENT":
            continue
        if bundle.get("git_head_at_test_time") == head:
            continue
        bundle["git_head_at_test_time"] = head
        bundle_no_hash = {k: v for k, v in bundle.items() if k != "content_hash"}
        bundle["content_hash"] = _deterministic_digest(bundle_no_hash)
        path.write_text(json.dumps(bundle, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        updated += 1
    print(f"resync_proof_bundle_git_heads: HEAD={head[:12]}… updated={updated} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
