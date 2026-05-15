"""CHECK-RG-FACT-VECTORS — apps_rg fact_vectors Chroma gate (sibling to CHECK-RG-CHROMA).

Verifies the C0 dense lane collection ``fact_vectors`` exists at the canonical persist
path, uses BGE-M3-sized embeddings (1024), and carries required metadata keys on a sample.

``run_contract_gates`` runs ``ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py`` immediately
before this gate so fresh CI checkouts can satisfy RG-FV-1 when chromadb + sentence-transformers
are available. Bypass seed: ``APPS_RG_SEED_FACT_VECTORS_BYPASS=1``.

Advisory by default; fail-closed via APPS_RG_FACT_VECTORS_FAIL_CLOSED=1.
Bypass: APPS_RG_FACT_VECTORS_BYPASS=1.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

BYPASS = os.environ.get("APPS_RG_FACT_VECTORS_BYPASS", "").lower() in ("1", "true")
FAIL_CLOSED = os.environ.get("APPS_RG_FACT_VECTORS_FAIL_CLOSED", "").lower() in ("1", "true")

CHROMA_PATH = os.environ.get("CHROMA_PERSIST_DIR", str(REPO_ROOT / "data/cache/chromadb"))

REQUIRED_METADATA_KEYS = (
    "app",
    "source_class",
    "source_document_id",
    "source_version_hash",
    "embedding_model_id",
    "embedding_dim",
)

REPORT_PATH = REPO_ROOT / "artifacts/ci/apps_rg_fact_vectors_readiness_gate.json"
EXPECTED_DIM = 1024


def _check(checks: list[dict], check_id: str, ok: bool, detail: str) -> None:
    level = "OK" if ok else "ERROR"
    checks.append({"check": check_id, "level": level, "detail": detail})
    print(f"  {'✅' if ok else '❌'} {check_id}: {detail}")


def main() -> int:
    if BYPASS:
        print("APPS_RG_FACT_VECTORS_BYPASS=1 — skipping CHECK-RG-FACT-VECTORS")
        return 0

    print("[CHECK-RG-FACT-VECTORS] apps_rg fact_vectors readiness gate")
    checks: list[dict] = []

    try:
        import chromadb  # type: ignore
    except ImportError:
        _check(checks, "RG-FV-1", False, "chromadb not importable — install chromadb")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
    except Exception as exc:
        _check(checks, "RG-FV-1", False, f"Cannot open ChromaDB at {CHROMA_PATH}: {exc}")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    try:
        col = client.get_collection("fact_vectors")
        total = col.count()
        _check(checks, "RG-FV-1", total > 0, f"fact_vectors count={total}")
    except Exception as exc:
        _check(checks, "RG-FV-1", False, f"fact_vectors collection: {exc}")
        _write_report(checks, 1)
        return 0 if not FAIL_CLOSED else 1

    try:
        peek = col.get(include=["embeddings", "metadatas"], limit=1)
        embs = peek.get("embeddings")
        dim_ok = False
        if embs is not None and len(embs) > 0 and embs[0] is not None:
            dim_ok = len(embs[0]) == EXPECTED_DIM
        _check(
            checks,
            "RG-FV-2",
            dim_ok,
            f"embedding dimension == {EXPECTED_DIM}" if dim_ok else "missing or wrong embedding dim",
        )
    except Exception as exc:
        _check(checks, "RG-FV-2", False, f"embedding peek failed: {exc}")

    try:
        sample = col.get(where={"app": "apps_rg"}, limit=3, include=["metadatas"])
        metas = sample.get("metadatas") or []
        missing_all: set[str] = set()
        for meta in metas:
            missing = [k for k in REQUIRED_METADATA_KEYS if k not in meta]
            missing_all.update(missing)
        _check(
            checks,
            "RG-FV-3",
            len(missing_all) == 0 and bool(metas),
            "all required metadata keys on sample" if not missing_all else f"missing: {sorted(missing_all)}",
        )
    except Exception as exc:
        _check(checks, "RG-FV-3", False, f"metadata sample error: {exc}")

    try:
        from agentic_core.runtime.contracts.final_evidence_contract import (
            SUPPORT_STATUS_PASSING_VALUES as FEC_PASS,
        )
        from apps_rg.runtime.bindings.c0_binding import SUPPORT_STATUS_PASSING_VALUES as BINDING_PASS

        ok = BINDING_PASS == FEC_PASS and "UNKNOWN" not in BINDING_PASS
        _check(
            checks,
            "RG-FV-4",
            ok,
            f"c0_binding re-exports contract PASS set: {sorted(BINDING_PASS)}",
        )
    except Exception as exc:
        _check(checks, "RG-FV-4", False, f"SUPPORT_STATUS_PASSING_VALUES import: {exc}")

    errors = [c for c in checks if c["level"] == "ERROR"]
    _write_report(checks, len(errors))

    print(f"\nCHECK-RG-FACT-VECTORS: {len(checks) - len(errors)} OK, {len(errors)} ERROR")
    if errors and FAIL_CLOSED:
        print("APPS_RG_FACT_VECTORS_FAIL_CLOSED=1 — exiting non-zero")
        return 1
    return 0


def _write_report(checks: list[dict], error_count: int) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "gate": "CHECK-RG-FACT-VECTORS",
        "chroma_path": CHROMA_PATH,
        "checks": checks,
        "error_count": error_count,
        "advisory": not FAIL_CLOSED,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"  Report: {REPORT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
