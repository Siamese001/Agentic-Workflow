#!/usr/bin/env python3
"""REQ-00B §5 — UWG commit receipt carries parent-pack linkage fields."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Fields required by integrated-runtime certification bundles and parent §5 narrative.
REQUIRED_PAYLOAD_KEYS = frozenset(
    {
        "commit_receipt_id",
        "request_id",
        "run_id",
        "commit_status",
        "committed_by_surface",
        "uwg_validation_receipt_ref",
        "write_lock_receipt_ref",
        "audit_append_receipt_ref",
        "deterministic_digest",
    }
)


def _check_bundle(path: Path) -> list[str]:
    errors: list[str] = []
    receipt_path = path / "uwg_commit_receipt.json"
    if not receipt_path.is_file():
        return [f"missing {receipt_path.relative_to(ROOT)}"]
    env = json.loads(receipt_path.read_text(encoding="utf-8"))
    payload = env.get("payload") or env
    missing = sorted(REQUIRED_PAYLOAD_KEYS - set(payload.keys()))
    if missing:
        errors.append(f"{receipt_path.name} missing keys: {missing}")
    if payload.get("committed_by_surface") != "UWG":
        errors.append(f"{receipt_path.name} committed_by_surface must be UWG")
    return errors


def main() -> int:
    bundles = [
        ROOT / "certification/agentic_core/integrated_runtime/uwg_commit_latest",
    ]
    all_errors: list[str] = []
    for bundle in bundles:
        all_errors.extend(_check_bundle(bundle))
    if all_errors:
        for err in all_errors:
            print(f"[verify_uwg_receipt_parent_fields] {err}", file=sys.stderr)
        return 1
    print("[verify_uwg_receipt_parent_fields] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
