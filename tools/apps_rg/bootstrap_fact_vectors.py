#!/usr/bin/env python3
"""Bootstrap apps_rg C0.2 ``fact_vectors`` dense and sparse evidence.

The dense Chroma collection and sparse SQLite sidecar are gitignored runtime
data, so a fresh checkout needs one idempotent provisioning entrypoint before
the mandatory C0.2 hybrid lane can run.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

COLLECTION = "fact_vectors"
SPARSE_PATH = REPO_ROOT / "data" / "cache" / "sparse" / f"{COLLECTION}.db"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "ci" / "apps_rg_fact_vectors_bootstrap_receipt.json"

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE_VALUES


def _chroma_path(raw: str | None = None) -> Path:
    value = (raw or os.environ.get("CHROMA_PERSIST_DIR", "")).strip()
    if value:
        path = Path(value)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path.resolve()
    return REPO_ROOT / "data" / "cache" / "chromadb"


def dense_count(chroma_path: Path, collection: str = COLLECTION) -> int:
    try:
        import chromadb  # type: ignore[import-not-found]
    except ImportError:
        return 0

    try:
        from chromadb.errors import NotFoundError  # type: ignore[import-not-found]
    except ImportError:
        NotFoundError = KeyError  # older chromadb raised KeyError/ValueError for missing collections

    try:
        client = chromadb.PersistentClient(path=str(chroma_path))
        return int(client.get_collection(collection).count())
    except (KeyError, RuntimeError, ValueError, OSError, NotFoundError):
        return 0


def sparse_doc_count(path: Path | None = None) -> int:
    target = path or SPARSE_PATH
    if not target.is_file():
        return 0
    try:
        with sqlite3.connect(str(target)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM docs").fetchone()
    except sqlite3.Error:
        return 0
    return int(row[0] or 0) if row else 0


def _write_receipt(payload: dict[str, Any], receipt_path: Path = RECEIPT_PATH) -> None:
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _run_dense_build(chroma_path: Path, *, reset: bool) -> int:
    from tools.apps_rg import build_section_fact_vectors

    argv = ["--execute", "--chroma-path", str(chroma_path)]
    if reset:
        argv.append("--reset")
    return int(build_section_fact_vectors.main(argv) or 0)


def _run_sparse_build(chroma_path: Path) -> dict[str, int]:
    os.environ["CHROMA_PERSIST_DIR"] = str(chroma_path)
    from tools.generate.ingestion import build_sparse_index

    return build_sparse_index.build_for_collection(
        COLLECTION,
        dry_run=False,
        chroma_path=chroma_path,
        sparse_dir=SPARSE_PATH.parent,
    )


def bootstrap(
    *,
    chroma_path: Path,
    force: bool = False,
    reset_dense: bool = False,
    receipt_path: Path = RECEIPT_PATH,
) -> dict[str, Any]:
    started = time.time()
    os.environ["CHROMA_PERSIST_DIR"] = str(chroma_path)
    chroma_path.mkdir(parents=True, exist_ok=True)

    dense_before = dense_count(chroma_path)
    sparse_before = sparse_doc_count()
    dense_ready = dense_before > 0
    sparse_ready = sparse_before > 0

    receipt: dict[str, Any] = {
        "collection": COLLECTION,
        "chroma_path": str(chroma_path),
        "sparse_path": str(SPARSE_PATH),
        "dense_count_before": dense_before,
        "sparse_doc_count_before": sparse_before,
        "forced": force,
        "reset_dense": reset_dense,
        "started_at": started,
    }

    if not force and dense_ready and sparse_ready:
        receipt.update(
            {
                "status": "skipped_ready",
                "dense_built": False,
                "sparse_built": False,
                "dense_count_after": dense_before,
                "sparse_doc_count_after": sparse_before,
                "elapsed_seconds": round(time.time() - started, 3),
            }
        )
        _write_receipt(receipt, receipt_path)
        return receipt

    if force or reset_dense or not dense_ready:
        dense_rc = _run_dense_build(chroma_path, reset=force or reset_dense)
        receipt["dense_build_exit_code"] = dense_rc
        if dense_rc != 0:
            receipt.update(
                {
                    "status": "dense_failed",
                    "dense_built": True,
                    "sparse_built": False,
                    "dense_count_after": dense_count(chroma_path),
                    "sparse_doc_count_after": sparse_doc_count(),
                    "elapsed_seconds": round(time.time() - started, 3),
                }
            )
            _write_receipt(receipt, receipt_path)
            return receipt
        receipt["dense_built"] = True
    else:
        receipt["dense_built"] = False

    dense_after = dense_count(chroma_path)
    if dense_after <= 0:
        receipt.update(
            {
                "status": "dense_empty",
                "sparse_built": False,
                "dense_count_after": dense_after,
                "sparse_doc_count_after": sparse_doc_count(),
                "elapsed_seconds": round(time.time() - started, 3),
            }
        )
        _write_receipt(receipt, receipt_path)
        return receipt

    if force or sparse_doc_count() <= 0:
        receipt["sparse_build_stats"] = _run_sparse_build(chroma_path)
        receipt["sparse_built"] = True
    else:
        receipt["sparse_built"] = False

    receipt.update(
        {
            "status": "ready" if dense_count(chroma_path) > 0 and sparse_doc_count() > 0 else "incomplete",
            "dense_count_after": dense_count(chroma_path),
            "sparse_doc_count_after": sparse_doc_count(),
            "elapsed_seconds": round(time.time() - started, 3),
        }
    )
    _write_receipt(receipt, receipt_path)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Rebuild dense collection and sparse sidecar.")
    parser.add_argument("--reset-dense", action="store_true", help="Delete dense collection before rebuilding.")
    parser.add_argument("--chroma-path", default=None, help="Override CHROMA_PERSIST_DIR for this run.")
    parser.add_argument("--receipt", default=str(RECEIPT_PATH), help="JSON provenance receipt path.")
    args = parser.parse_args(argv)

    if _env_true("APPS_RG_FACT_VECTORS_BOOTSTRAP_BYPASS") or _env_true(
        "APPS_RG_SEED_FACT_VECTORS_BYPASS"
    ):
        print("[BOOTSTRAP-RG-FV] bypassed by env")
        return 0

    receipt = bootstrap(
        chroma_path=_chroma_path(args.chroma_path),
        force=bool(args.force),
        reset_dense=bool(args.reset_dense),
        receipt_path=Path(args.receipt),
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("status") in {"ready", "skipped_ready"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
