"""Wave Read Gap Finder — finds modules with actual file/db read calls but no reads_through edge.

Distinguishes type_annotation reads_from (imports) from actual I/O reads.
Looks for calls to open(), json.load, yaml.load, sqlite3.connect, redis, Path.read_text, etc.
"""
import argparse
import glob
import os
import sqlite3

IO_READ_SYMBOLS = {
    "open", "read", "read_text", "read_bytes", "read_file",
    "json.load", "json.loads", "yaml.safe_load", "yaml.load",
    "toml.load", "toml.loads", "tomllib.load",
    "configparser", "ConfigParser",
    "sqlite3.connect", "connect",
    "Path.read_text", "Path.read_bytes",
    "load", "loads", "read_csv", "read_json",
    "getenv", "environ",
}

IO_READ_TAILS = {
    "open", "read", "read_text", "read_bytes", "read_file",
    "safe_load", "load", "loads", "read_csv", "read_json",
    "connect", "getenv", "get", "read_all",
    "ConfigParser", "read_config", "load_config",
    "load_yaml", "load_json", "load_toml",
    "read_artifact", "read_sqlite", "read_redis", "read_vector",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=None)
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--exclude-tests", action="store_true")
    parser.add_argument("--storage-type", default=None,
                        help="config,sqlite,redis,vector,artifact,report")
    args = parser.parse_args()

    adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
    db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
    print(f"DB: {db}")
    conn = sqlite3.connect(db)

    # Scope filter
    scope_sql = ""
    if args.scope:
        clauses = []
        for pat in args.scope.split(","):
            clauses.append(f"e.source_file LIKE '{pat.strip().replace('*', '%')}'")
        scope_sql = f"AND ({' OR '.join(clauses)})"

    test_sql = "AND e.source_file NOT LIKE 'tests/%'" if args.exclude_tests else ""

    # Storage type symbol hints
    storage_hints = {
        "config": ["json", "yaml", "toml", "config", "env", "settings", "ini", "cfg"],
        "sqlite": ["sqlite", "connect", "cursor", "execute", "fetchall"],
        "redis": ["redis", "Redis", "cache", "hget", "get_redis"],
        "vector": ["vector", "faiss", "embedding", "retriev", "query_similarity"],
        "artifact": ["artifact", "archive", "bundle", "package", "report"],
        "report": ["markdown", "csv", "log", "report", "evidence"],
    }
    hint_list = None
    if args.storage_type:
        hint_list = storage_hints.get(args.storage_type, [])

    # Find modules with reads_through already
    has_reads_through = set()
    rows = conn.execute(f"""
        SELECT DISTINCT e.source_file FROM edges e
        WHERE e.relation_type = 'reads_through'
        {scope_sql} {test_sql}
    """).fetchall()
    has_reads_through = {r[0] for r in rows}

    # Find modules with actual I/O-like calls (not just type imports)
    # Look in 'calls' edges for I/O read symbols
    like_clauses = " OR ".join(f"e.symbol LIKE '%{t}%'" for t in IO_READ_TAILS)
    rows = conn.execute(f"""
        SELECT e.source_file, e.symbol, COUNT(*) as cnt
        FROM edges e
        WHERE e.relation_type = 'calls'
        AND ({like_clauses})
        {scope_sql} {test_sql}
        GROUP BY e.source_file, e.symbol
        ORDER BY e.source_file
    """).fetchall()

    # Aggregate by module
    module_reads = {}
    for sf, sym, cnt in rows:
        if sf in has_reads_through:
            continue
        tail = sym.split(".")[-1] if sym else ""
        if tail in IO_READ_TAILS or any(t in sym.lower() for t in ["open", "read", "load", "connect"]):
            if sf not in module_reads:
                module_reads[sf] = {"count": 0, "symbols": []}
            module_reads[sf]["count"] += cnt
            module_reads[sf]["symbols"].append(f"{tail}({cnt})")

    # Apply storage type filter
    if hint_list:
        filtered = {}
        for mod, info in module_reads.items():
            sym_text = " ".join(info["symbols"]).lower()
            if any(h in sym_text for h in hint_list):
                filtered[mod] = info
        module_reads = filtered

    # Also check reads_from edges exist (denominator must exist)
    final = []
    for mod in sorted(module_reads, key=lambda m: -module_reads[m]["count"]):
        has_denom = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND source_file=?",
            (mod,)
        ).fetchone()[0]
        if has_denom > 0:
            info = module_reads[mod]
            final.append((mod, info["count"], info["symbols"][:5], has_denom))

    print(f"Scope: {args.scope or 'all'}")
    print(f"Storage type: {args.storage_type or 'all'}")
    print(f"Modules with reads_through: {len(has_reads_through)}")
    print(f"Gap modules with I/O reads + reads_from denom: {len(final)}")
    print(f"Showing top {min(args.limit, len(final))}:")
    print()

    for i, (mod, call_cnt, syms, denom_cnt) in enumerate(final[:args.limit], 1):
        sym_str = ", ".join(syms)
        print(f"  {i:>3}. {mod}")
        print(f"       IO calls: {call_cnt}  reads_from: {denom_cnt}  symbols: {sym_str}")

    conn.close()


if __name__ == "__main__":
    main()
