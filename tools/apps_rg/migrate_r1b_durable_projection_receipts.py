#!/usr/bin/env python3
"""Conservatively annotate existing R1B durable projection bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

UNKNOWN = "MIGRATION_UNKNOWN"


def _migrate_bundle(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    original = dict(payload)
    for key in (
        "source_commit_receipt_ref",
        "policy_hash",
        "blueprint_hash",
        "replay_key",
        "audit_append_receipt_ref",
        "content_hash",
        "chain_hash",
    ):
        payload.setdefault(key, payload.get("uwg_commit_receipt_id") if key == "source_commit_receipt_ref" else UNKNOWN)
    payload["migration_status"] = "MIGRATED_UNCERTAIN"
    payload["migration_cache_admissible_without_valid_receipt_chain"] = False
    payload["pre_migration_payload"] = original
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "path": str(path),
        "source_commit_receipt_ref": payload.get("source_commit_receipt_ref"),
        "migration_status": payload["migration_status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default="artifacts/apps_rg/r1b_semantic_cache",
        help="R1B projection root",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    intents = Path(args.root) / "durable" / "uwg_admitted" / "intents"
    rows: list[dict[str, Any]] = []
    for path in sorted(intents.glob("*.json")) if intents.is_dir() else []:
        if args.dry_run:
            rows.append({"path": str(path), "dry_run": True})
        else:
            rows.append(_migrate_bundle(path))
    print(json.dumps({"bundles_seen": len(rows), "rows": rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
