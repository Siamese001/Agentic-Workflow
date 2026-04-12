"""ADG Incremental Update Engine.

Usage:
    python tools/adg_incremental_update.py file1.py file2.py ...

Given a list of patched modules:
1. Compute impacted closure (patched + import neighbors + export neighbors)
2. Rescan ONLY impacted modules (reuse scan cache for unchanged)
3. Update SQLite: delete old edges for impacted files, insert new ones
4. Recompute and print metrics

This avoids a full 6,290-module rescan when only 10-15 files changed.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash
from agentic_core.adg.extraction.static_scanner import Edge, _scan_file

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _latest_sqlite() -> Path:
    """Find the most recent ADG SQLite file."""
    import glob

    candidates = sorted(
        glob.glob(str(ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite")),
        key=os.path.getmtime,
    )
    if not candidates:
        raise FileNotFoundError("No ADG SQLite found in artifacts/adg/")
    return Path(candidates[-1])


# ---------------------------------------------------------------------------
# Step 1 — Impacted closure
# ---------------------------------------------------------------------------


def _compute_impacted_closure(
    patched_files: list[str],
    conn: sqlite3.Connection,
) -> set[str]:
    """Compute impacted closure: patched + import neighbors + export neighbors.

    Schema: edges(src_id, dst_id, relation_type, source_file, ...)
            nodes(id, adg_name, resolved_path, ...)
    """
    impacted = set(patched_files)

    for pf in patched_files:
        # Inbound import neighbors: other modules whose imports resolve to
        # a symbol inside the patched file (dst node resolved_path = pf).
        rows = conn.execute(
            """SELECT DISTINCT e.source_file
               FROM edges e
               JOIN nodes n ON e.dst_id = n.id
               WHERE e.relation_type = 'imports'
                 AND n.resolved_path = ?""",
            (pf,),
        ).fetchall()
        for (sf,) in rows:
            if sf:
                impacted.add(sf)

        # Outbound import neighbors: modules that the patched file imports.
        rows = conn.execute(
            """SELECT DISTINCT n.resolved_path
               FROM edges e
               JOIN nodes n ON e.dst_id = n.id
               WHERE e.relation_type = 'imports'
                 AND e.source_file = ?""",
            (pf,),
        ).fetchall()
        for (rp,) in rows:
            if rp:
                impacted.add(rp)

    return impacted


# ---------------------------------------------------------------------------
# Step 2 — Rescan impacted files
# ---------------------------------------------------------------------------


def _rescan_impacted(
    impacted_files: set[str],
    repo_root: Path,
    cache: ScanCache,
    include_tests: bool = True,
) -> list[Edge]:
    """Rescan only impacted files.  Updates the cache in-place."""
    all_edges: list[Edge] = []
    scanned = 0

    for rel in sorted(impacted_files):
        filepath = repo_root / rel
        if not filepath.exists():
            continue

        file_edges, had_error = _scan_file(filepath, repo_root, include_tests)
        if not had_error:
            fhash = file_hash(filepath)
            cache.put(rel, fhash, file_edges)
            scanned += 1
        all_edges.extend(file_edges)

    print(f"[INCR] Rescanned {scanned} files, produced {len(all_edges)} edges")
    return all_edges


# ---------------------------------------------------------------------------
# Step 3 — Update SQLite (delete-then-insert for impacted files)
# ---------------------------------------------------------------------------


def _resolve_node_id(conn: sqlite3.Connection, adg_name: str, cache: dict[str, int]) -> int:
    """Lookup or create a node by its adg_name.  Uses a session cache."""
    if adg_name in cache:
        return cache[adg_name]
    row = conn.execute(
        "SELECT id FROM nodes WHERE adg_name = ?",
        (adg_name,),
    ).fetchone()
    if row:
        cache[adg_name] = row[0]
        return row[0]
    # Create new node
    cur = conn.execute(
        "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
        "VALUES (?, 'symbol', '', 'inferred', 'MEDIUM', '')",
        (adg_name,),
    )
    nid = cur.lastrowid
    cache[adg_name] = nid
    return nid


def _update_sqlite(
    db_path: Path,
    impacted_files: set[str],
    new_edges: list[Edge],
) -> tuple[int, int]:
    """Delete old edges for impacted files, insert new ones.

    Returns (deleted, inserted).
    """
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Delete existing edges for impacted files
    placeholders = ",".join("?" for _ in impacted_files)
    deleted = conn.execute(
        f"DELETE FROM edges WHERE source_file IN ({placeholders})",
        list(impacted_files),
    ).rowcount

    # Build a node-ID cache for fast lookups
    node_cache: dict[str, int] = {}

    inserted = 0
    for e in new_edges:
        src_id = _resolve_node_id(conn, e.from_name, node_cache)
        dst_id = _resolve_node_id(conn, e.to_name, node_cache)
        conn.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (src_id, dst_id, e.relation_type, e.edge_kind, e.source_file, e.line_no, e.symbol),
        )
        inserted += 1

    conn.commit()
    conn.close()
    return deleted, inserted


# ---------------------------------------------------------------------------
# Step 4 — Metrics
# ---------------------------------------------------------------------------


def _compute_metrics(db_path: Path) -> dict:
    """Run the verification SQL pack and compute ratios."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("""
        SELECT relation_type, COUNT(*)
        FROM edges
        WHERE relation_type IN (
          'calls','records_execution_trace','pulls_context','emits_determinism_digest',
          'writes_to','writes_through','applies_guardrail','validated_by_safety_plane',
          'emits_metric_event','dispatches_healing_run','agent_executes_agent'
        )
        GROUP BY relation_type
        ORDER BY relation_type
    """).fetchall()
    counts = {rt: cnt for rt, cnt in rows}
    conn.close()

    ratios = {}
    metrics = [
        ("L0_trace_coverage", "records_execution_trace", "calls", 0.70),
        ("L1_context_binding", "pulls_context", "records_execution_trace", 0.70),
        ("L2_determinism_proof", "emits_determinism_digest", "calls", 0.55),
        ("L4_memory_authority", "writes_through", "writes_to", 0.90),
        ("L5_safety_governance", "validated_by_safety_plane", "applies_guardrail", 1.00),
        ("L6_observability", "emits_metric_event", "calls", 0.55),
    ]
    for label, num, den, target in metrics:
        n = counts.get(num, 0)
        d = counts.get(den, 0)
        ratio = n / d if d else 0
        gap = max(0, int(target * d - n))
        ratios[label] = {
            "numerator": n,
            "denominator": d,
            "ratio": round(ratio, 4),
            "target": target,
            "gap": gap,
            "pass": ratio >= target,
        }
    return {"counts": counts, "ratios": ratios}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="ADG Incremental Update Engine")
    parser.add_argument("files", nargs="+", help="Patched module paths (repo-relative)")
    parser.add_argument("--db", help="SQLite path (default: latest)", default=None)
    args = parser.parse_args()

    patched = [f.replace("\\", "/") for f in args.files]
    db_path = Path(args.db) if args.db else _latest_sqlite()
    cache_path = ROOT / "artifacts" / "adg" / "scan_result_cache.json"

    print(f"[INCR] SQLite: {db_path.name}")
    print(f"[INCR] Patched files: {len(patched)}")

    t0 = time.time()

    # 1. Compute impacted closure
    conn = sqlite3.connect(str(db_path))
    impacted = _compute_impacted_closure(patched, conn)
    conn.close()
    print(f"[INCR] Impacted closure: {len(impacted)} modules (from {len(patched)} patched)")

    # 2. Load cache + rescan impacted
    cache = ScanCache.load(cache_path) if cache_path.exists() else ScanCache()
    print(f"[INCR] Cache loaded: {cache.size} entries")
    new_edges = _rescan_impacted(impacted, ROOT, cache, include_tests=True)

    # 3. Update SQLite
    deleted, inserted = _update_sqlite(db_path, impacted, new_edges)
    print(f"[INCR] SQLite: deleted={deleted} inserted={inserted} delta={inserted - deleted:+d}")

    # 4. Save updated cache
    cache.save(cache_path)

    # 5. Compute metrics
    metrics = _compute_metrics(db_path)

    elapsed = time.time() - t0
    print(f"[INCR] Completed in {elapsed:.1f}s")

    # Report
    BASELINE = {
        "agent_executes_agent": 3136,
        "applies_guardrail": 3136,
        "calls": 252355,
        "dispatches_healing_run": 4235,
        "emits_determinism_digest": 3077,
        "emits_metric_event": 18033,
        "pulls_context": 5980,
        "records_execution_trace": 21562,
        "validated_by_safety_plane": 3056,
        "writes_through": 6070,
        "writes_to": 18228,
    }
    print("\n=== POST-WAVE COUNTS ===")
    for rt, cnt in sorted(metrics["counts"].items()):
        base = BASELINE.get(rt, 0)
        delta = cnt - base
        sign = "+" if delta >= 0 else ""
        print(f"  {rt:35s} {cnt:>8d}  (baseline {base:>8d}, delta {sign}{delta})")

    print("\n=== POST-WAVE RATIOS ===")
    for label, info in metrics["ratios"].items():
        status = "PASS" if info["pass"] else f"gap={info['gap']}"
        print(
            f"  {label:25s} {info['numerator']:>8d}/{info['denominator']:<8d} "
            f"= {info['ratio']:.4f}  target={info['target']}  {status}",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
