"""Wave Gap Finder — identifies modules with denominator edges but missing numerator edges.

Usage:
    python tools/wave_gap_finder.py --metric reads_through/reads_from --scope "apps_*" --limit 15
    python tools/wave_gap_finder.py --metric writes_through/writes_to --scope "tools/*" --limit 12
    python tools/wave_gap_finder.py --metric records_execution_trace/calls --scope "agentic_core/*" --limit 10
    python tools/wave_gap_finder.py --metric validated_by_safety_plane/applies_guardrail --limit 15
    python tools/wave_gap_finder.py --metric pulls_context/records_execution_trace --limit 15
    python tools/wave_gap_finder.py --metric emits_determinism_digest/records_execution_trace --limit 15
    python tools/wave_gap_finder.py --metric emits_metric_event/records_execution_trace --limit 15

Optional filters:
    --symbol-hint "json,yaml,toml,env,settings"   # only modules whose reads_from symbol matches hints
    --exclude-tests                                 # skip test modules
"""
import argparse
import glob
import json
import os
import sqlite3


def find_latest_db():
    adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
    files = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))
    return files[-1] if files else None


def find_gap_modules(db_path, numerator_type, denominator_type, scope_pattern, limit,
                     symbol_hints=None, exclude_tests=False):
    conn = sqlite3.connect(db_path)

    # Build scope filter
    scope_clauses = []
    if scope_pattern:
        for pat in scope_pattern.split(","):
            pat = pat.strip().replace("*", "%")
            scope_clauses.append(f"source_file LIKE '{pat}'")
    scope_sql = f"AND ({' OR '.join(scope_clauses)})" if scope_clauses else ""

    test_sql = "AND source_file NOT LIKE 'tests/%'" if exclude_tests else ""

    # Find modules with denominator edges
    denom_modules = conn.execute(f"""
        SELECT DISTINCT source_file FROM edges
        WHERE relation_type = ?
        {scope_sql} {test_sql}
    """, (denominator_type,)).fetchall()
    denom_set = {r[0] for r in denom_modules}

    # Find modules with numerator edges
    numer_modules = conn.execute(f"""
        SELECT DISTINCT source_file FROM edges
        WHERE relation_type = ?
        {scope_sql} {test_sql}
    """, (numerator_type,)).fetchall()
    numer_set = {r[0] for r in numer_modules}

    # Gap = has denominator but no numerator
    gap_modules = sorted(denom_set - numer_set)

    # If symbol hints, filter to modules whose denominator symbol matches
    if symbol_hints:
        hints = [h.strip().lower() for h in symbol_hints.split(",")]
        filtered = []
        for mod in gap_modules:
            symbols = conn.execute(
                "SELECT symbol FROM edges WHERE relation_type = ? AND source_file = ?",
                (denominator_type, mod)
            ).fetchall()
            sym_text = " ".join(s[0].lower() for s in symbols if s[0])
            if any(h in sym_text for h in hints):
                filtered.append(mod)
        gap_modules = filtered

    # Get denominator edge count per gap module for prioritization
    results = []
    for mod in gap_modules:
        count = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type = ? AND source_file = ?",
            (denominator_type, mod)
        ).fetchone()[0]
        symbols = conn.execute(
            "SELECT DISTINCT symbol FROM edges WHERE relation_type = ? AND source_file = ?",
            (denominator_type, mod)
        ).fetchall()
        sym_list = [s[0] for s in symbols if s[0]]
        results.append((mod, count, sym_list))

    # Sort by denominator count descending (highest-density first)
    results.sort(key=lambda x: -x[1])

    conn.close()
    return results[:limit], len(denom_set), len(numer_set), len(gap_modules)


def main():
    parser = argparse.ArgumentParser(description="Wave Gap Finder")
    parser.add_argument("--metric", required=True, help="numerator/denominator e.g. reads_through/reads_from")
    parser.add_argument("--scope", default=None, help="Source file pattern e.g. apps_*,apps_shared/*")
    parser.add_argument("--limit", type=int, default=15, help="Max modules to return")
    parser.add_argument("--symbol-hint", default=None, help="Comma-sep symbol substrings to filter by")
    parser.add_argument("--exclude-tests", action="store_true", help="Exclude test modules")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    parts = args.metric.split("/")
    if len(parts) != 2:
        print("ERROR: --metric must be numerator/denominator e.g. reads_through/reads_from")
        return

    numerator_type, denominator_type = parts
    db_path = find_latest_db()
    if not db_path:
        print("ERROR: No ADG SQLite found")
        return

    print(f"DB: {db_path}")
    print(f"Metric: {numerator_type} / {denominator_type}")
    print(f"Scope: {args.scope or 'all'}")
    print()

    results, denom_total, numer_total, gap_total = find_gap_modules(
        db_path, numerator_type, denominator_type,
        args.scope, args.limit, args.symbol_hint, args.exclude_tests
    )

    print(f"Modules with {denominator_type}: {denom_total}")
    print(f"Modules with {numerator_type}: {numer_total}")
    print(f"Gap modules (has denom, no numer): {gap_total}")
    print(f"Showing top {len(results)} by density:")
    print()

    if args.json:
        out = []
        for mod, count, syms in results:
            out.append({"module": mod, "denom_edges": count, "symbols": syms[:5]})
        print(json.dumps(out, indent=2))
    else:
        for i, (mod, count, syms) in enumerate(results, 1):
            sym_preview = ", ".join(syms[:3])
            if len(syms) > 3:
                sym_preview += f" (+{len(syms)-3} more)"
            print(f"  {i:>3}. {mod}")
            print(f"       {denominator_type} edges: {count}  symbols: {sym_preview}")


if __name__ == "__main__":
    main()
