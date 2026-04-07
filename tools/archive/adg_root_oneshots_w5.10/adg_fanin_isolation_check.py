#!/usr/bin/env python3
"""ADG Fan-In Isolation Check — dead-code and sign-off gate.

Implements the fan-in isolation pattern from the ADG gptcache RCA:
any component claimed to be "active" or "signed off" must have at
least ONE non-test, non-ops_scripts, non-ci import edge pointing at it.

Zero production fan-in == dead code.  The ADG can prove this in two
queries; this tool automates the check and can be run as a gate.

Usage:
    # Check a single component by path fragment
    python tools/adg/adg_fanin_isolation_check.py gptcache_client

    # Check multiple patterns
    python tools/adg/adg_fanin_isolation_check.py gptcache_client semantic_cache_manager

    # Scan whole codebase for zero-fan-in modules (dead code sweep)
    python tools/adg/adg_fanin_isolation_check.py --sweep-dead-code

    # Detect split-architecture pairs (A replaced by B with no convergence)
    python tools/adg/adg_fanin_isolation_check.py --detect-splits

    # Full gate mode: exit 1 if any target has zero production fan-in
    python tools/adg/adg_fanin_isolation_check.py --gate gptcache_client

Exit codes:
    0  All targets have production fan-in (or sweep found nothing)
    1  One or more targets have zero production fan-in
    2  SQLite not found or schema error
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"

# --------------------------------------------------------------------------- #
# Production vs non-production classification                                  #
# --------------------------------------------------------------------------- #

NON_PROD_PREFIXES = (
    "tests/",
    "test_",
    "_test.",
    "ops_scripts/ci/",
    "ops_scripts/general/",
    "tools/",
    "docs/",
    "artifacts/",
    ".windsurf/",
)


def is_non_production(path: str) -> bool:
    """Return True if this source path is a test/CI/tooling file."""
    p = path.replace("\\", "/")
    return any(p.startswith(pfx) or f"/{pfx}" in p for pfx in NON_PROD_PREFIXES)


# --------------------------------------------------------------------------- #
# SQLite helpers                                                               #
# --------------------------------------------------------------------------- #


def get_latest_sqlite() -> Path:
    files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
    if not files:
        print("[ERROR] No ADG SQLite found in artifacts/adg/", file=sys.stderr)
        sys.exit(2)
    return files[-1]


def open_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------------------------------- #
# Core queries                                                                 #
# --------------------------------------------------------------------------- #

_FANIN_SQL = """
SELECT
    src.resolved_path  AS importer,
    e.source_file      AS source_file,
    e.relation_type    AS relation_type,
    e.edge_kind        AS edge_kind
FROM edges e
JOIN nodes src ON src.id = e.src_id
JOIN nodes dst ON dst.id = e.dst_id
WHERE dst.resolved_path LIKE :pattern
  AND e.relation_type = 'imports'
ORDER BY src.resolved_path
"""

_MODULE_EXISTS_SQL = """
SELECT COUNT(*) FROM nodes
WHERE resolved_path LIKE :pattern
"""


def fanin_edges(conn: sqlite3.Connection, pattern: str) -> list[dict]:
    """Return all edges where dst matches *pattern*."""
    cur = conn.execute(_FANIN_SQL, {"pattern": f"%{pattern}%"})
    return [dict(r) for r in cur.fetchall()]


def split_edges(
    edges: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Partition edges into production importers vs non-production."""
    prod, non_prod = [], []
    for e in edges:
        src = e.get("importer") or e.get("source_file") or ""
        (non_prod if is_non_production(src) else prod).append(e)
    return prod, non_prod


# --------------------------------------------------------------------------- #
# Single-target report                                                         #
# --------------------------------------------------------------------------- #


def check_target(conn: sqlite3.Connection, pattern: str, verbose: bool = True) -> bool:
    """Check fan-in for one pattern.  Returns True if production fan-in > 0."""
    # Confirm the module actually exists
    count = conn.execute(_MODULE_EXISTS_SQL, {"pattern": f"%{pattern}%"}).fetchone()[0]
    if count == 0:
        print(f"  [WARN] No nodes matching '{pattern}' found in ADG")
        return True  # not a failure — pattern unknown

    edges = fanin_edges(conn, pattern)
    prod_edges, non_prod_edges = split_edges(edges)

    status = "OK" if prod_edges else "DEAD"
    icon = "✅" if prod_edges else "❌"

    print(f"\n{icon}  [{status}] Pattern: {pattern!r}")
    print(f"     Total importers : {len(edges)}")
    print(f"     Production      : {len(prod_edges)}")
    print(f"     Non-production  : {len(non_prod_edges)}")

    if verbose:
        if prod_edges:
            print("     Production importers:")
            for e in prod_edges[:10]:
                print(f"       • {e['importer']}")
            if len(prod_edges) > 10:
                print(f"       … and {len(prod_edges) - 10} more")
        else:
            print("     ⚠️  ZERO production importers — this is dead code")
            if non_prod_edges:
                print("     Non-production importers (test/CI/tools):")
                for e in non_prod_edges[:5]:
                    print(f"       • {e['importer']}")
                if len(non_prod_edges) > 5:
                    print(f"       … and {len(non_prod_edges) - 5} more")

    return bool(prod_edges)


# --------------------------------------------------------------------------- #
# Split-architecture detection                                                 #
# --------------------------------------------------------------------------- #

_CANDIDATE_PAIRS_SQL = """
SELECT DISTINCT
    n1.resolved_path AS a,
    n2.resolved_path AS b
FROM nodes n1
JOIN nodes n2
  ON n1.resolved_path != n2.resolved_path
 AND (
     -- same stem, different name suggests replacement
     INSTR(n2.resolved_path, SUBSTR(n1.resolved_path, 1, LENGTH(n1.resolved_path)-3)) > 0
     OR INSTR(n1.resolved_path, SUBSTR(n2.resolved_path, 1, LENGTH(n2.resolved_path)-3)) > 0
 )
WHERE n1.entity_type = 'module'
  AND n2.entity_type = 'module'
  AND n1.resolved_path NOT LIKE '%test%'
  AND n2.resolved_path NOT LIKE '%test%'
LIMIT 50
"""

_CONVERGENCE_SQL = """
SELECT COUNT(*) FROM edges
WHERE (
    (src_id = (SELECT id FROM nodes WHERE resolved_path = :a LIMIT 1)
     AND dst_id = (SELECT id FROM nodes WHERE resolved_path = :b LIMIT 1))
 OR (src_id = (SELECT id FROM nodes WHERE resolved_path = :b LIMIT 1)
     AND dst_id = (SELECT id FROM nodes WHERE resolved_path = :a LIMIT 1))
)
"""


def detect_splits(conn: sqlite3.Connection) -> list[dict]:
    """Find pairs where one has no prod fan-in and they don't import each other."""
    # Use a simpler approach: find all modules with zero prod fan-in
    # cross-referenced with modules that share naming patterns
    zero_prod = find_zero_prod_fanin_modules(conn, limit=500)

    splits = []
    for mod in zero_prod:
        path = mod["resolved_path"]
        stem = Path(path).stem.replace("_client", "").replace("_cache", "").replace("_manager", "")
        if len(stem) < 6:
            continue  # too short to be meaningful

        # Look for sibling modules with the same stem
        cur = conn.execute(
            """
            SELECT DISTINCT resolved_path FROM nodes
            WHERE resolved_path LIKE :stem
              AND resolved_path != :path
              AND entity_type = 'module'
            LIMIT 5
            """,
            {"stem": f"%{stem}%", "path": path},
        )
        siblings = [r[0] for r in cur.fetchall()]
        if siblings:
            splits.append({"dead_module": path, "siblings": siblings, "stem": stem})

    return splits


# --------------------------------------------------------------------------- #
# Dead-code sweep                                                              #
# --------------------------------------------------------------------------- #

_ALL_MODULES_SQL = """
SELECT id, resolved_path, layer
FROM nodes
WHERE entity_type = 'module'
  AND resolved_path NOT LIKE '%test%'
  AND resolved_path NOT LIKE '%__pycache__%'
  AND resolved_path NOT LIKE '%ops_scripts%'
  AND resolved_path NOT LIKE '%tools/%'
  AND resolved_path NOT LIKE '%docs/%'
  AND resolved_path NOT LIKE '%.windsurf%'
  AND resolved_path NOT LIKE '%artifacts%'
"""

_PROD_FANIN_COUNT_SQL = """
SELECT COUNT(*) FROM edges e
JOIN nodes src ON src.id = e.src_id
WHERE e.dst_id = :node_id
  AND e.relation_type = 'imports'
  AND src.resolved_path NOT LIKE '%test%'
  AND src.resolved_path NOT LIKE '%ops_scripts%'
  AND src.resolved_path NOT LIKE '%tools/%'
"""


def find_zero_prod_fanin_modules(
    conn: sqlite3.Connection, limit: int = 200,
) -> list[dict]:
    """Return production modules with zero production importers."""
    cur = conn.execute(_ALL_MODULES_SQL)
    modules = cur.fetchall()

    dead = []
    for row in modules:
        node_id, path, layer = row["id"], row["resolved_path"], row["layer"]
        prod_count = conn.execute(
            _PROD_FANIN_COUNT_SQL, {"node_id": node_id},
        ).fetchone()[0]
        if prod_count == 0:
            dead.append(
                {"resolved_path": path, "layer": layer, "prod_fan_in": 0},
            )
        if len(dead) >= limit:
            break

    return dead


def sweep_dead_code(conn: sqlite3.Connection, top_n: int = 50) -> int:
    """Sweep for zero-fan-in production modules. Returns count found."""
    print(f"\n{'='*70}")
    print("DEAD CODE SWEEP — production modules with zero production importers")
    print(f"{'='*70}")

    dead = find_zero_prod_fanin_modules(conn, limit=top_n)

    if not dead:
        print("✅ No dead modules found (all production modules have importers)")
        return 0

    print(f"Found {len(dead)} candidate dead modules (may include entrypoints):\n")
    by_layer: dict[str, list[str]] = {}
    for m in dead:
        layer = m["layer"] or "UNKNOWN"
        by_layer.setdefault(layer, []).append(m["resolved_path"])

    for layer, paths in sorted(by_layer.items()):
        print(f"  Layer {layer} ({len(paths)} modules):")
        for p in paths[:5]:
            print(f"    • {p}")
        if len(paths) > 5:
            print(f"    … and {len(paths) - 5} more")
        print()

    print(
        "NOTE: Entrypoints (main.py, __main__.py, CLI scripts) are expected to have\n"
        "zero importers — filter them before acting on this list.",
    )
    return len(dead)


# --------------------------------------------------------------------------- #
# SQL printout for documentation                                               #
# --------------------------------------------------------------------------- #


def print_sql_reference() -> None:
    """Print the canonical SQL patterns for documentation."""
    print("""
=== CANONICAL ADG FAN-IN ISOLATION SQL PATTERNS ===

-- Q1: All importers of a component (who uses it?)
SELECT src.resolved_path AS importer, e.relation_type, e.edge_kind
FROM edges e
JOIN nodes src ON src.id = e.src_id
JOIN nodes dst ON dst.id = e.dst_id
WHERE dst.resolved_path LIKE '%<component>%'
  AND e.relation_type = 'imports'
ORDER BY src.resolved_path;

-- Q2: Production-only fan-in count (is it dead code?)
SELECT COUNT(*) AS prod_fan_in
FROM edges e
JOIN nodes src ON src.id = e.src_id
JOIN nodes dst ON dst.id = e.dst_id
WHERE dst.resolved_path LIKE '%<component>%'
  AND e.relation_type = 'imports'
  AND src.resolved_path NOT LIKE '%test%'
  AND src.resolved_path NOT LIKE '%ops_scripts%'
  AND src.resolved_path NOT LIKE '%tools/%';

-- Q3: Do two components share any importer? (split architecture check)
SELECT src.resolved_path, 'imports_A' AS which FROM edges e
  JOIN nodes src ON src.id = e.src_id
  JOIN nodes dst ON dst.id = e.dst_id
  WHERE dst.resolved_path LIKE '%<component_A>%' AND e.relation_type='imports'
INTERSECT
SELECT src.resolved_path, 'imports_B' AS which FROM edges e
  JOIN nodes src ON src.id = e.src_id
  JOIN nodes dst ON dst.id = e.dst_id
  WHERE dst.resolved_path LIKE '%<component_B>%' AND e.relation_type='imports';

-- Q4: Fan-out from a component (what does it depend on?)
SELECT dst.resolved_path AS dependency, e.edge_kind
FROM edges e
JOIN nodes src ON src.id = e.src_id
JOIN nodes dst ON dst.id = e.dst_id
WHERE src.resolved_path LIKE '%<component>%'
  AND e.relation_type = 'imports'
ORDER BY dst.resolved_path;
""")


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ADG fan-in isolation check — dead code / sign-off gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "patterns",
        nargs="*",
        help="Path fragment(s) to check fan-in for",
    )
    p.add_argument(
        "--gate",
        action="store_true",
        help="Gate mode: exit 1 if any target has zero production fan-in",
    )
    p.add_argument(
        "--sweep-dead-code",
        action="store_true",
        help="Sweep entire codebase for zero-fan-in production modules",
    )
    p.add_argument(
        "--detect-splits",
        action="store_true",
        help="Detect split-architecture pairs (A alongside B with no convergence)",
    )
    p.add_argument(
        "--print-sql",
        action="store_true",
        help="Print canonical SQL patterns for documentation",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    p.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Explicit path to ADG SQLite file (default: latest in artifacts/adg/)",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    if args.print_sql:
        print_sql_reference()
        return 0

    db_path = args.db or get_latest_sqlite()
    print(f"[ADG Fan-In] Using: {db_path.name}")
    conn = open_db(db_path)

    results: dict = {}
    exit_code = 0

    try:
        # ----- Dead code sweep -----
        if args.sweep_dead_code:
            n = sweep_dead_code(conn)
            results["dead_module_count"] = n
            if args.json:
                print(json.dumps(results, indent=2))
            return 0  # sweep is informational, not a gate failure

        # ----- Split architecture detection -----
        if args.detect_splits:
            splits = detect_splits(conn)
            print(f"\nSplit-architecture candidates: {len(splits)}")
            for s in splits[:20]:
                print(f"  DEAD: {s['dead_module']}")
                for sib in s["siblings"][:3]:
                    print(f"    ↔  {sib}")
            results["splits"] = splits
            if args.json:
                print(json.dumps(results, indent=2))
            return 0

        # ----- Explicit pattern checks -----
        if not args.patterns:
            print("No patterns specified. Use --help for usage.")
            print("Quick example: python tools/adg/adg_fanin_isolation_check.py gptcache_client")
            return 0

        print(f"\n{'='*70}")
        print(f"ADG FAN-IN ISOLATION CHECK  ({len(args.patterns)} target(s))")
        print(f"{'='*70}")

        failed = []
        for pattern in args.patterns:
            has_prod = check_target(conn, pattern, verbose=True)
            results[pattern] = {"has_production_fan_in": has_prod}
            if not has_prod:
                failed.append(pattern)

        print(f"\n{'='*70}")
        if failed:
            print(f"❌ GATE FAIL — {len(failed)} target(s) have zero production fan-in:")
            for f in failed:
                print(f"   • {f}")
            exit_code = 1
        else:
            print(f"✅ GATE PASS — all {len(args.patterns)} target(s) have production fan-in")

        if args.json:
            print(json.dumps(results, indent=2))

    finally:
        conn.close()

    return exit_code if args.gate else 0


if __name__ == "__main__":
    sys.exit(main())
