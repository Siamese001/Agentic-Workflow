#!/usr/bin/env python3
"""Drop the corrupt/redundant ``repo_adg_graph`` ChromaDB collection (W5.2).

Decision:
    The ``repo_adg_graph`` collection was populated by
    ``tools/ingestion/ingest_adg.py`` as a semantic index over ADG nodes.
    Its responsibilities are now fully covered by two other sources:

        1. ``symbols`` collection (canonical store, 78,591 rows) — semantic
           search over every ADG symbol name + docstring.
        2. ``adg_sqlite`` MCP server — the authoritative live ADG query
           surface.

    A Chroma copy of the graph drifts the moment ``tools/generate_full_adg.py``
    is re-run. Plus the current legacy-store copy is corrupt: ``count()``
    raises a compactor backfill error. Cleanest resolution is to drop it
    from both stores and remove the ``adg`` stage from the pipeline.

Usage::

    python tools/retrieval/drop_repo_adg_graph.py          # dry-run
    python tools/retrieval/drop_repo_adg_graph.py --apply  # actually delete

W5.2 of ``docs/archive/windsurf/legacy-tree/plans/chromadb-bge-retrieval-hardening-e9aa09.md``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import chromadb

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir, legacy_persist_dir

COLLECTION = "repo_adg_graph"


def _drop_one(store: Path, apply: bool) -> None:
    if not store.exists():
        print(f"  SKIP  {store} (directory missing)")
        return
    try:
        client = chromadb.PersistentClient(path=str(store))
    except (OSError, RuntimeError) as exc:
        print(f"  FAIL  {store} cannot open: {exc}")
        return
    names = {c.name for c in client.list_collections()}
    if COLLECTION not in names:
        print(f"  SKIP  {store} (no '{COLLECTION}' collection)")
        return
    if not apply:
        print(f"  DRY   {store} would DELETE '{COLLECTION}'")
        return
    try:
        client.delete_collection(COLLECTION)
        print(f"  OK    {store} deleted '{COLLECTION}'")
    except Exception as exc:  # guardian: allow-broad-exception -- Chroma raises opaque rust errors
        print(f"  FAIL  {store} delete raised {type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually delete (default is dry-run).")
    args = parser.parse_args()

    print(f"Drop '{COLLECTION}' (mode={'APPLY' if args.apply else 'DRY'})")
    _drop_one(canonical_persist_dir(), args.apply)
    _drop_one(legacy_persist_dir(), args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
