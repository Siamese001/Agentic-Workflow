#!/usr/bin/env python3
"""ADG ↔ ChromaDB coverage report.

Compares the set of ADG Symbol nodes (functions, classes, methods) against
the set of chunks stored in the canonical ChromaDB ``repo_code_chunks``
collection and reports coverage by layer.

Output: ``docs/reports/plans/chromadb_coverage_report.md``.

W3.3 of the ChromaDB/BGE retrieval-hardening plan
(``.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md``).
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import chromadb

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str
from agentic_core.L4_state.utils.chunk_metadata import infer_layer

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = REPO_ROOT / "docs" / "reports" / "plans" / "chromadb_coverage_report.md"
ADG_DIR = REPO_ROOT / "artifacts" / "adg"


def latest_adg() -> Path | None:
    cands = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def adg_symbols_by_layer(adg_path: Path) -> dict[str, int]:
    """Count ADG Symbol nodes per inferred layer."""
    counts: dict[str, int] = defaultdict(int)
    uri = f"file:{adg_path.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=10.0) as conn:
        cur = conn.execute(
            "SELECT resolved_path FROM nodes "
            "WHERE adg_name LIKE 'ADG::Symbol::%' AND resolved_path LIKE '%.py' "
            "  AND resolved_path NOT LIKE 'tests/%' "
            "  AND resolved_path NOT LIKE '%/tests/%' "
            "  AND resolved_path NOT LIKE '%/test_%'"
        )
        for (path,) in cur:
            counts[infer_layer(path)] += 1
    return dict(counts)


def chroma_chunks_by_layer(
    store_path: str,
    collection_name: str,
) -> tuple[int, dict[str, int]]:
    """Count ChromaDB chunks per layer in a collection. Returns (total, by_layer)."""
    client = chromadb.PersistentClient(path=store_path)
    names = {c.name for c in client.list_collections()}
    if collection_name not in names:
        return 0, {}
    col = client.get_collection(collection_name)
    total = col.count()
    if total == 0:
        return 0, {}

    # Paginate through all metadatas — ChromaDB .get() default cap is 10.
    by_layer: dict[str, int] = defaultdict(int)
    page = 10_000
    offset = 0
    while offset < total:
        res = col.get(limit=page, offset=offset, include=["metadatas"])
        metas = res.get("metadatas") or []
        if not metas:
            break
        for m in metas:
            layer = (m or {}).get("layer") or "L_UNKNOWN"
            by_layer[layer] += 1
        offset += len(metas)
    return total, dict(by_layer)


def render(
    adg_total: int,
    adg_by_layer: dict[str, int],
    chroma_total: int,
    chroma_by_layer: dict[str, int],
    adg_path: Path,
    collection_name: str,
) -> str:
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# ChromaDB Coverage Report",
        "",
        f"**Generated:** {ts}",
        f"**ADG snapshot:** `{adg_path.name}`",
        f"**Collection:** `{collection_name}` @ canonical store",
        "",
        "## Totals",
        "",
        f"| Source | Count |",
        f"|---|---:|",
        f"| ADG Symbol nodes (non-test `.py`) | {adg_total} |",
        f"| ChromaDB chunks | {chroma_total} |",
        f"| Ratio (chunks / symbols) | {chroma_total / adg_total:.2%} |" if adg_total else "| Ratio | n/a |",
        "",
        "## By Layer",
        "",
        "| Layer | ADG Symbols | ChromaDB Chunks | Coverage |",
        "|---|---:|---:|---:|",
    ]
    all_layers = sorted(set(adg_by_layer) | set(chroma_by_layer))
    for layer in all_layers:
        a = adg_by_layer.get(layer, 0)
        c = chroma_by_layer.get(layer, 0)
        cov = f"{c / a:.1%}" if a else ("n/a" if c == 0 else "∞")
        lines.append(f"| `{layer}` | {a} | {c} | {cov} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `Coverage > 100%` means ChromaDB has multiple chunks per ADG symbol "
            "(expected — every function/class/method yields one chunk; additional "
            "``*`` module-level symbols show as 1:1 in ADG but 0 chunks here).",
            "- `Coverage == n/a` means ADG has no symbols for that layer — ChromaDB "
            "chunks labelled `L_UNKNOWN` belong here.",
            "- `Coverage < 50%` on a populated layer indicates an ingest gap. "
            "Run `python -m tools.ingestion.pipeline --only code_<root>` for the "
            "affected root.",
            "",
            "## Next",
            "",
            "Per plan `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md`: "
            "run full pipeline to converge chunk count with ADG symbols, then re-run "
            "this report. Target: ≥ 90% layer coverage on every populated layer.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", default="repo_code_chunks")
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    adg_path = latest_adg()
    if adg_path is None:
        print("ERROR: no ADG snapshot under artifacts/adg/; run tools/generate_full_adg.py first.")
        return 1

    print(f"ADG snapshot: {adg_path.name}")
    adg_by_layer = adg_symbols_by_layer(adg_path)
    adg_total = sum(adg_by_layer.values())

    store = canonical_persist_dir_str()
    print(f"ChromaDB store: {store}")
    chroma_total, chroma_by_layer = chroma_chunks_by_layer(store, args.collection)

    report = render(
        adg_total=adg_total,
        adg_by_layer=adg_by_layer,
        chroma_total=chroma_total,
        chroma_by_layer=chroma_by_layer,
        adg_path=adg_path,
        collection_name=args.collection,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"Wrote coverage report: {args.out}")
    print()
    print(f"ADG symbols: {adg_total}  ChromaDB chunks: {chroma_total}")
    for layer in sorted(set(adg_by_layer) | set(chroma_by_layer)):
        a = adg_by_layer.get(layer, 0)
        c = chroma_by_layer.get(layer, 0)
        print(f"  {layer:<20}  adg={a:>6}  chroma={c:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
