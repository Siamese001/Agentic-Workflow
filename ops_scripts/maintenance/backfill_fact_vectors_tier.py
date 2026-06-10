"""Backfill ``tier`` metadata for the apps_rg ``fact_vectors`` collection.

W1 of plan c0-grounded-fact-writeback-spine-4f8e2a introduces two tiers:
``seed`` for bootstrap/canonical rows and ``learned`` for promoted rows.
Existing live rows are inferred from the W1 plan rule:
rows with ``write_back_operation`` => learned; otherwise seed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_COLLECTION = "fact_vectors"
DEFAULT_RECEIPT = REPO_ROOT / "artifacts" / "apps_rg" / "fact_vectors_tier_backfill_receipt.json"
VALID_TIERS = frozenset({"seed", "learned"})


def infer_fact_vector_tier(metadata: dict[str, Any]) -> str:
    """Infer the W1 tier for a pre-v2.1 row."""
    if str(metadata.get("write_back_operation") or "").strip():
        return "learned"
    return "seed"


def _current_tier(metadata: dict[str, Any]) -> str:
    tier = str(metadata.get("tier") or "").strip()
    return tier if tier in VALID_TIERS else ""


def _iter_collection_rows(
    collection: Any,
    *,
    page_size: int = 1000,
    limit: int | None = None,
) -> Iterable[tuple[str, dict[str, Any]]]:
    total = int(collection.count())
    if limit is not None and limit >= 0:
        total = min(total, limit)
    offset = 0
    while offset < total:
        batch_limit = min(page_size, total - offset)
        batch = collection.get(
            include=["metadatas"],
            limit=batch_limit,
            offset=offset,
        )
        ids = list(batch.get("ids") or [])
        metadatas = list(batch.get("metadatas") or [])
        if not ids:
            break
        for idx, row_id in enumerate(ids):
            metadata = metadatas[idx] if idx < len(metadatas) and isinstance(metadatas[idx], dict) else {}
            yield str(row_id), dict(metadata)
        offset += len(ids)


def _count_untagged(collection: Any, *, page_size: int, limit: int | None) -> int:
    return sum(
        1
        for _row_id, metadata in _iter_collection_rows(collection, page_size=page_size, limit=limit)
        if not _current_tier(metadata)
    )


def backfill_collection_tier(
    collection: Any,
    *,
    execute: bool,
    page_size: int = 1000,
    limit: int | None = None,
) -> dict[str, Any]:
    """Backfill missing/invalid ``tier`` metadata on a Chroma-like collection."""
    rows = list(_iter_collection_rows(collection, page_size=page_size, limit=limit))
    tier_counts_before: Counter[str] = Counter()
    inferred_counts: Counter[str] = Counter()
    update_ids: list[str] = []
    update_metadatas: list[dict[str, Any]] = []
    samples: list[dict[str, str]] = []

    for row_id, metadata in rows:
        tier = _current_tier(metadata)
        if tier:
            tier_counts_before[tier] += 1
            continue
        inferred = infer_fact_vector_tier(metadata)
        inferred_counts[inferred] += 1
        updated = dict(metadata)
        updated["tier"] = inferred
        update_ids.append(row_id)
        update_metadatas.append(updated)
        if len(samples) < 25:
            samples.append({"id": row_id, "inferred_tier": inferred})

    if execute and update_ids:
        collection.update(ids=update_ids, metadatas=update_metadatas)

    untagged_before = len(update_ids)
    untagged_after = (
        _count_untagged(collection, page_size=page_size, limit=limit)
        if execute
        else untagged_before
    )
    return {
        "schema_version": "fact_vectors_tier_backfill_v1",
        "status": "PASS" if execute else "DRY_RUN",
        "execute": bool(execute),
        "total_rows_scanned": len(rows),
        "tagged_before": len(rows) - untagged_before,
        "untagged_before": untagged_before,
        "tier_counts_before": dict(sorted(tier_counts_before.items())),
        "inferred_counts": dict(sorted(inferred_counts.items())),
        "updated_count": len(update_ids) if execute else 0,
        "untagged_after": untagged_after,
        "samples": samples,
    }


def _load_collection(chroma_path: str, collection_name: str) -> Any:
    from agentic_core.L4_state.utils.client.chroma_client import (
        chromadb_module as chromadb,
    )

    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_collection(collection_name)


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Inspect rows and write a receipt without updating.")
    mode.add_argument("--execute", action="store_true", help="Update missing/invalid tier metadata.")
    parser.add_argument(
        "--chroma-path",
        default=os.environ.get("CHROMA_PERSIST_DIR", "")
        or str(REPO_ROOT / "data" / "cache" / "chromadb"),
    )
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument("--receipt-path", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    execute = bool(args.execute)
    receipt_path = Path(args.receipt_path)
    receipt: dict[str, Any]
    try:
        collection = _load_collection(str(args.chroma_path), str(args.collection))
        receipt = backfill_collection_tier(
            collection,
            execute=execute,
            page_size=max(1, int(args.page_size)),
            limit=args.limit,
        )
        receipt.update(
            {
                "collection": str(args.collection),
                "chroma_path": str(args.chroma_path),
                "receipt_path": str(receipt_path),
            }
        )
    except Exception as exc:  # guardian: allow-broad-exception -- operator backfill must emit a failure receipt instead of losing diagnostics.
        receipt = {
            "schema_version": "fact_vectors_tier_backfill_v1",
            "status": "FAIL",
            "execute": execute,
            "collection": str(args.collection),
            "chroma_path": str(args.chroma_path),
            "receipt_path": str(receipt_path),
            "reason": f"{type(exc).__name__}:{exc}",
            "untagged_after": None,
        }
    _write_receipt(receipt_path, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("status") in {"PASS", "DRY_RUN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "VALID_TIERS",
    "backfill_collection_tier",
    "infer_fact_vector_tier",
    "main",
]
