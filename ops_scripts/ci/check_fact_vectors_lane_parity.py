"""CHECK-RG-FV-PARITY - fact_vectors dense/sparse row-count parity gate.

Verifies the dense Chroma ``fact_vectors`` collection and sparse SQLite sidecar
carry the same document count. Advisory by default; fail-closed via
APPS_RG_FACT_VECTORS_PARITY_FAIL_CLOSED=1.

Bypass: APPS_RG_FACT_VECTORS_PARITY_BYPASS=1.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BYPASS_ENV = "APPS_RG_FACT_VECTORS_PARITY_BYPASS"
FAIL_CLOSED_ENV = "APPS_RG_FACT_VECTORS_PARITY_FAIL_CLOSED"
DEFAULT_COLLECTION = "fact_vectors"
DEFAULT_CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
DEFAULT_SPARSE_DIR = REPO_ROOT / "data" / "cache" / "sparse"
REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "fact_vectors_lane_parity_gate.json"


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _dense_count(chroma_path: Path, collection_name: str) -> tuple[int | None, str]:
    try:
        from agentic_core.L4_state.utils.client.chroma_client import (
            chromadb_module as chromadb,
        )
    except ImportError as exc:
        return None, f"chromadb_adapter_import_failed:{exc}"

    try:
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_collection(collection_name)
        return int(collection.count()), "ok"
    except Exception as exc:  # guardian: allow-broad-except -- gate reports advisory diagnostics.
        return None, f"{type(exc).__name__}:{exc}"


def _sparse_count(sparse_db: Path) -> tuple[int | None, str]:
    if not sparse_db.is_file():
        return None, f"missing_sparse_sidecar:{sparse_db}"
    try:
        with sqlite3.connect(str(sparse_db)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM docs").fetchone()
        return int(row[0] or 0) if row else 0, "ok"
    except sqlite3.Error as exc:
        return None, f"sqlite_error:{exc}"


def evaluate_parity(
    *,
    dense_count: int | None,
    dense_detail: str,
    sparse_count: int | None,
    sparse_detail: str,
) -> tuple[bool, str]:
    if dense_count is None:
        return False, dense_detail
    if sparse_count is None:
        return False, sparse_detail
    if dense_count != sparse_count:
        return False, f"dense_count={dense_count} sparse_count={sparse_count}"
    return True, f"dense_count=sparse_count={dense_count}"


def build_report(
    *,
    chroma_path: Path,
    sparse_db: Path,
    collection_name: str,
) -> dict[str, Any]:
    dense, dense_detail = _dense_count(chroma_path, collection_name)
    sparse, sparse_detail = _sparse_count(sparse_db)
    ok, detail = evaluate_parity(
        dense_count=dense,
        dense_detail=dense_detail,
        sparse_count=sparse,
        sparse_detail=sparse_detail,
    )
    return {
        "gate": "CHECK-RG-FV-PARITY",
        "collection": collection_name,
        "chroma_path": str(chroma_path),
        "sparse_db": str(sparse_db),
        "dense_count": dense,
        "dense_detail": dense_detail,
        "sparse_count": sparse,
        "sparse_detail": sparse_detail,
        "ok": ok,
        "detail": detail,
    }


def _write_report(report: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"  Report: {REPORT_PATH}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chroma-path",
        type=Path,
        default=Path(os.environ.get("CHROMA_PERSIST_DIR", str(DEFAULT_CHROMA_PATH))),
    )
    parser.add_argument(
        "--sparse-dir",
        type=Path,
        default=Path(os.environ.get("APPS_RG_FACT_VECTORS_SPARSE_DIR", str(DEFAULT_SPARSE_DIR))),
    )
    parser.add_argument("--collection", default=os.environ.get("APPS_RG_FACT_VECTORS_COLLECTION", DEFAULT_COLLECTION))
    parser.add_argument("--strict", action="store_true", help=f"Exit non-zero on mismatch (or set {FAIL_CLOSED_ENV}=1)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if _env_truthy(BYPASS_ENV):
        print(f"{BYPASS_ENV}=1 - skipping CHECK-RG-FV-PARITY")
        return 0

    strict = bool(args.strict or _env_truthy(FAIL_CLOSED_ENV))
    collection_name = str(args.collection or DEFAULT_COLLECTION)
    sparse_db = Path(args.sparse_dir) / f"{collection_name}.db"
    print("[CHECK-RG-FV-PARITY] apps_rg fact_vectors dense/sparse parity")
    report = build_report(
        chroma_path=Path(args.chroma_path),
        sparse_db=sparse_db,
        collection_name=collection_name,
    )
    report["advisory"] = not strict
    _write_report(report)
    if report["ok"]:
        print(f"  OK: {report['detail']}")
        return 0
    print(f"  ERROR: {report['detail']}")
    if strict:
        print(f"{FAIL_CLOSED_ENV}=1 or --strict - exiting non-zero")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
