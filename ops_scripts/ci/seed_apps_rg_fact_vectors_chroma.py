#!/usr/bin/env python3
"""SEED-RG-FV — Idempotently bootstrap ``fact_vectors`` dense + sparse evidence.

Used by ``run_contract_gates`` immediately before ``check_apps_rg_fact_vectors_readiness``
so fresh CI checkouts satisfy RG-FV-1 without manual operator ingest.

Default behavior (no flags): skip when the dense Chroma collection and sparse SQLite sidecar
are both ready; otherwise build whichever surface is missing.

``--force`` — rebuild dense ``fact_vectors`` and the sparse sidecar.

Bypass: ``APPS_RG_SEED_FACT_VECTORS_BYPASS=1`` (exit 0, no work).

Requires: ``chromadb``, ``sentence-transformers`` (same as the dense builder).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT))


def _chroma_path() -> str:
    return os.environ.get("CHROMA_PERSIST_DIR", str(REPO_ROOT / "data" / "cache" / "chromadb"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild fact_vectors dense collection and sparse sidecar.",
    )
    args = parser.parse_args(argv)

    if os.environ.get("APPS_RG_SEED_FACT_VECTORS_BYPASS", "").lower() in ("1", "true"):
        print("[SEED-RG-FV] APPS_RG_SEED_FACT_VECTORS_BYPASS=1 — skipping")
        return 0

    from tools.apps_rg.bootstrap_fact_vectors import bootstrap

    receipt = bootstrap(chroma_path=Path(_chroma_path()), force=bool(args.force))
    print(
        "[SEED-RG-FV] "
        f"status={receipt.get('status')} "
        f"dense={receipt.get('dense_count_after')} "
        f"sparse_docs={receipt.get('sparse_doc_count_after')}"
    )
    return 0 if receipt.get("status") in {"ready", "skipped_ready"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
