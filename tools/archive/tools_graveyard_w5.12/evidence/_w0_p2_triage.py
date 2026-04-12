"""W0: P2 HIGH-severity antipattern triage.

Queries the ADG SQLite for exact counts of the four HIGH-severity antipattern
edge_kinds, broken down by source_file layer prefix. Exports a CSV inventory
to artifacts/adg_analysis/p2_high_severity_inventory.csv.

Usage:
    python tools/evidence/_w0_p2_triage.py
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

HIGH_SEVERITY_KINDS = (
    "silent_exception_swallow",
    "broad_exception_catch",
    "log_and_swallow",
    "return_none_swallow",
)

LAYER_PREFIXES = {
    "agentic_core/L0": "L0",
    "agentic_core/L1": "L1",
    "agentic_core/L2": "L2",
    "agentic_core/L3": "L3",
    "agentic_core/L4": "L4",
    "agentic_core/L5": "L5",
    "agentic_core/L6": "L6",
    "apps_": "L_APP",
    "system_learning/": "L_SL",
    "ops_scripts/": "L_OPS",
    "tools/": "L_TOOLS",
    "tests/": "L_TEST",
    "infrastructure/": "L_INFRA",
}


def classify_layer(source_file: str) -> str:
    for prefix, layer in LAYER_PREFIXES.items():
        if source_file.startswith(prefix):
            return layer
    return "L_UNKNOWN"


def main() -> None:
    adg_dir = Path("artifacts/adg")
    dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not dbs:
        print("ERROR: No ADG SQLite found in artifacts/adg/")
        raise SystemExit(1)
    db = dbs[-1]
    print(f"Using: {db}")

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    placeholders = ",".join("?" * len(HIGH_SEVERITY_KINDS))
    cur.execute(
        f"""
        SELECT e.edge_kind, e.source_file, e.line_no
        FROM edges e
        WHERE e.relation_type = 'antipattern'
          AND e.edge_kind IN ({placeholders})
        ORDER BY e.edge_kind, e.source_file, e.line_no
        """,
        HIGH_SEVERITY_KINDS,
    )
    rows = cur.fetchall()
    conn.close()

    print(f"\nTotal HIGH-severity antipattern rows: {len(rows)}")

    # Per-category summary
    by_kind: dict[str, int] = {}
    for edge_kind, _, _ in rows:
        by_kind[edge_kind] = by_kind.get(edge_kind, 0) + 1

    print("\n=== Per-category counts ===")
    for kind in HIGH_SEVERITY_KINDS:
        print(f"  {kind}: {by_kind.get(kind, 0)}")

    # Per-layer summary
    by_layer: dict[str, int] = {}
    for _, source_file, _ in rows:
        layer = classify_layer(source_file or "")
        by_layer[layer] = by_layer.get(layer, 0) + 1

    print("\n=== Per-layer counts ===")
    for layer, count in sorted(by_layer.items(), key=lambda x: -x[1]):
        print(f"  {layer}: {count}")

    # Per-category × per-layer matrix
    matrix: dict[tuple[str, str], int] = {}
    for edge_kind, source_file, _ in rows:
        layer = classify_layer(source_file or "")
        key = (edge_kind, layer)
        matrix[key] = matrix.get(key, 0) + 1

    print("\n=== Category × Layer matrix ===")
    layers_seen = sorted({k[1] for k in matrix})
    header = f"{'kind':<35}" + "".join(f"{l:<12}" for l in layers_seen)
    print(f"  {header}")
    for kind in HIGH_SEVERITY_KINDS:
        row_str = f"  {kind:<35}" + "".join(f"{matrix.get((kind, l), 0):<12}" for l in layers_seen)
        print(row_str)

    # Top-20 files by count
    by_file: dict[str, int] = {}
    for _, source_file, _ in rows:
        by_file[source_file or "(unknown)"] = by_file.get(source_file or "(unknown)", 0) + 1

    print("\n=== Top 20 files by antipattern density ===")
    for fpath, cnt in sorted(by_file.items(), key=lambda x: -x[1])[:20]:
        layer = classify_layer(fpath)
        print(f"  {cnt:>5}  [{layer}]  {fpath}")

    # Export CSV
    out_dir = Path("artifacts/adg_analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "p2_high_severity_inventory.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["edge_kind", "source_file", "line_no", "layer"])
        for edge_kind, source_file, line_no in rows:
            writer.writerow([edge_kind, source_file or "", line_no or "", classify_layer(source_file or "")])

    print(f"\nCSV exported: {out_path}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
