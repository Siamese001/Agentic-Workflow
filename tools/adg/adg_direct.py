"""
ADG Direct Query Tool — MCP-FREE backup for adg_redis MCP server.

When the ADG Redis MCP is flaky/unavailable, use this script directly via run_command.
It queries Redis (preferred) then falls back to SQLite.

Usage:
    python tools/adg/adg_direct.py status
    python tools/adg/adg_direct.py meta
    python tools/adg/adg_direct.py node <node_id>
    python tools/adg/adg_direct.py nodes_by_layer <layer> [limit]
    python tools/adg/adg_direct.py nodes_by_file <relative_path>
    python tools/adg/adg_direct.py edge_fanout <src_id> <relation_type> [limit]
    python tools/adg/adg_direct.py edge_fanin <tgt_id> <relation_type> [limit]
    python tools/adg/adg_direct.py violations [limit]
    python tools/adg/adg_direct.py sql "<SQL>"
    python tools/adg/adg_direct.py edge_counts [top_n]
    python tools/adg/adg_direct.py layer_counts
    python tools/adg/adg_direct.py find_node <name_fragment>
    python tools/adg/adg_direct.py module_context <node_id>

Examples:
    python tools/adg/adg_direct.py status
    python tools/adg/adg_direct.py edge_counts 20
    python tools/adg/adg_direct.py find_node "adg_backed_registry"
    python tools/adg/adg_direct.py sql "SELECT relation_type, COUNT(*) c FROM edges GROUP BY relation_type ORDER BY c DESC LIMIT 20"
"""
from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
from tools.adg.shared_modules.path_resolver import get_adg_dir

_REDIS_URL = os.environ.get("ADG_REDIS_URL", "redis://localhost:6379/0")
_ADG_DIR = get_adg_dir()


# ---------------------------------------------------------------------------
# Redis layer (optional — graceful fallback if unavailable)
# ---------------------------------------------------------------------------
def _get_redis():
    try:
        import redis as _r
        client = _r.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return client
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# SQLite layer — always available
# ---------------------------------------------------------------------------
def _latest_sqlite() -> Path | None:
    files = sorted(_ADG_DIR.glob("adg_indexed_*.sqlite"))
    return files[-1] if files else None


def _sqlite_con() -> sqlite3.Connection | None:
    p = _latest_sqlite()
    if p and p.exists():
        con = sqlite3.connect(str(p))
        con.row_factory = sqlite3.Row
        return con
    return None


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def _pp(obj: Any) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(args: list[str]) -> None:
    _header("ADG STATUS")
    r = _get_redis()

    # --- Redis path ---
    if r:
        raw = r.get("adg:status")
        if raw:
            status = json.loads(raw)
            ingested_at = float(status.get("ingested_at", 0))
            sqlite_path = Path(status.get("sqlite_path", ""))
            disk_mtime = sqlite_path.stat().st_mtime if sqlite_path.exists() else None
            is_fresh = (ingested_at >= disk_mtime) if disk_mtime is not None else False
            age = round(time.time() - ingested_at, 1)
            print(f"SOURCE     : Redis (direct)")
            print(f"TIMESTAMP  : {status.get('timestamp', 'unknown')}")
            print(f"NODES      : {int(status.get('node_count', 0)):,}")
            print(f"EDGES      : {int(status.get('edge_count', 0)):,}")
            print(f"IS_FRESH   : {is_fresh}")
            print(f"AGE        : {age}s")
            print(f"DIGEST     : {status.get('digest', 'n/a')}")
            print(f"COHERENT   : {status.get('projection_coherent', 'unknown')}")
            print(f"VERDICT    : {'HOT [OK]' if is_fresh else 'STALE — run: python tools/adg/adg_redis_ingest.py --force'}")
            return
        else:
            print("Redis: adg:status key missing — falling back to SQLite")
    else:
        print("Redis: UNAVAILABLE — using SQLite fallback")

    # --- SQLite fallback ---
    p = _latest_sqlite()
    if not p:
        print("ERROR: No SQLite file found in", _ADG_DIR)
        return
    con = sqlite3.connect(str(p))
    nodes = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    con.close()
    mtime = time.strftime("%Y%m%d_%H%M", time.localtime(p.stat().st_mtime))
    print(f"SOURCE     : SQLite (fallback)")
    print(f"FILE       : {p.name}")
    print(f"MTIME      : {mtime}")
    print(f"NODES      : {nodes:,}")
    print(f"EDGES      : {edges:,}")


def cmd_meta(args: list[str]) -> None:
    _header("ADG META")
    r = _get_redis()
    if r:
        meta = r.hgetall("adg:meta")
        if meta:
            print("SOURCE: Redis (direct)")
            _pp(meta)
            return
        print("Redis: adg:meta missing — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    p = _latest_sqlite()
    if not p:
        print("ERROR: No SQLite file")
        return
    con = sqlite3.connect(str(p))
    nodes = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    con.close()
    print("SOURCE: SQLite (fallback)")
    _pp({"file": str(p), "nodes": nodes, "edges": edges, "mtime": p.stat().st_mtime})


def cmd_node(args: list[str]) -> None:
    if not args:
        print("Usage: node <node_id>")
        return
    node_id = args[0]
    _header(f"NODE {node_id}")

    r = _get_redis()
    if r:
        data = r.hgetall(f"adg:node:{node_id}")
        if data:
            print("SOURCE: Redis")
            _pp(data)
            return
        print(f"Redis: adg:node:{node_id} not found — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        print("ERROR: No SQLite")
        return
    row = con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    if row:
        print("SOURCE: SQLite")
        _pp(dict(row))
    else:
        # Try by adg_name
        rows = con.execute("SELECT * FROM nodes WHERE adg_name LIKE ?", (f"%{node_id}%",)).fetchall()
        print(f"Not found by id. adg_name matches: {len(rows)}")
        for r2 in rows[:10]:
            _pp(dict(r2))
    con.close()


def cmd_nodes_by_layer(args: list[str]) -> None:
    if not args:
        print("Usage: nodes_by_layer <layer> [limit]")
        return
    layer = args[0]
    limit = int(args[1]) if len(args) > 1 else 20
    _header(f"NODES BY LAYER: {layer} (limit={limit})")

    r = _get_redis()
    if r:
        members = r.smembers(f"adg:nodes:by_layer:{layer}")
        if members:
            items = list(members)[:limit]
            print(f"SOURCE: Redis | Total in layer: {len(members)} | Showing: {len(items)}")
            for m in items:
                print(f"  {m}")
            return
        print(f"Redis: adg:nodes:by_layer:{layer} empty — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        return
    rows = con.execute(
        "SELECT id, adg_name, entity_type FROM nodes WHERE layer=? LIMIT ?", (layer, limit)
    ).fetchall()
    total = con.execute("SELECT COUNT(*) FROM nodes WHERE layer=?", (layer,)).fetchone()[0]
    print(f"SOURCE: SQLite | Total in layer: {total:,} | Showing: {len(rows)}")
    for row in rows:
        print(f"  [{row[0]}] {row[1]} ({row[2]})")
    con.close()


def cmd_nodes_by_file(args: list[str]) -> None:
    if not args:
        print("Usage: nodes_by_file <relative_path>")
        return
    path = args[0]
    _header(f"NODES BY FILE: {path}")

    r = _get_redis()
    if r:
        members = r.smembers(f"adg:nodes:by_file:{path}")
        if members:
            print(f"SOURCE: Redis | {len(members)} nodes")
            for m in list(members)[:50]:
                print(f"  {m}")
            return
        print(f"Redis: adg:nodes:by_file:{path} not found — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        return
    rows = con.execute(
        "SELECT id, adg_name, entity_type FROM nodes WHERE resolved_path LIKE ?", (f"%{path}%",)
    ).fetchall()
    print(f"SOURCE: SQLite | {len(rows)} nodes")
    for row in rows[:50]:
        print(f"  [{row[0]}] {row[1]} ({row[2]})")
    con.close()


def cmd_edge_fanout(args: list[str]) -> None:
    if len(args) < 2:
        print("Usage: edge_fanout <src_id> <relation_type> [limit]")
        return
    src_id, rel = args[0], args[1]
    limit = int(args[2]) if len(args) > 2 else 30
    _header(f"EDGE FANOUT: {src_id} --[{rel}]--> ?")

    r = _get_redis()
    if r:
        members = r.smembers(f"adg:edge:{src_id}:{rel}")
        if members:
            print(f"SOURCE: Redis | {len(members)} edge_ids")
            shown = list(members)[:limit]
            for eid in shown:
                detail = r.hgetall(f"adg:edge_detail:{eid}")
                if detail:
                    print(f"  -> {detail.get('dst_id', '?')} [{detail.get('symbol', '')}] @ {detail.get('source_file', '')}:{detail.get('line_no', '')}")
                else:
                    print(f"  edge_id={eid}")
            return
        print(f"Redis: empty — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        return
    rows = con.execute(
        "SELECT dst_id, symbol, source_file, line_no FROM edges WHERE src_id=? AND relation_type=? LIMIT ?",
        (src_id, rel, limit),
    ).fetchall()
    total = con.execute(
        "SELECT COUNT(*) FROM edges WHERE src_id=? AND relation_type=?", (src_id, rel)
    ).fetchone()[0]
    print(f"SOURCE: SQLite | Total: {total} | Showing: {len(rows)}")
    for row in rows:
        print(f"  -> {row[0]} [{row[1]}] @ {row[2]}:{row[3]}")
    con.close()


def cmd_edge_fanin(args: list[str]) -> None:
    if len(args) < 2:
        print("Usage: edge_fanin <tgt_id> <relation_type> [limit]")
        return
    tgt_id, rel = args[0], args[1]
    limit = int(args[2]) if len(args) > 2 else 30
    _header(f"EDGE FANIN: ? --[{rel}]--> {tgt_id}")

    r = _get_redis()
    if r:
        members = r.smembers(f"adg:edge:in:{tgt_id}:{rel}")
        if members:
            print(f"SOURCE: Redis | {len(members)} edge_ids")
            shown = list(members)[:limit]
            for eid in shown:
                detail = r.hgetall(f"adg:edge_detail:{eid}")
                if detail:
                    print(f"  <- {detail.get('src_id', '?')} [{detail.get('symbol', '')}] @ {detail.get('source_file', '')}:{detail.get('line_no', '')}")
                else:
                    print(f"  edge_id={eid}")
            return
        print(f"Redis: empty — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        return
    rows = con.execute(
        "SELECT src_id, symbol, source_file, line_no FROM edges WHERE dst_id=? AND relation_type=? LIMIT ?",
        (tgt_id, rel, limit),
    ).fetchall()
    total = con.execute(
        "SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type=?", (tgt_id, rel)
    ).fetchone()[0]
    print(f"SOURCE: SQLite | Total: {total} | Showing: {len(rows)}")
    for row in rows:
        print(f"  <- {row[0]} [{row[1]}] @ {row[2]}:{row[3]}")
    con.close()


def cmd_violations(args: list[str]) -> None:
    limit = int(args[0]) if args else 20
    _header(f"VIOLATIONS (limit={limit})")

    r = _get_redis()
    if r:
        vids = r.lrange("adg:violations", 0, limit - 1)
        total = r.llen("adg:violations")
        if vids:
            print(f"SOURCE: Redis | Total: {total} | Showing: {len(vids)}")
            for vid in vids:
                v = r.hgetall(f"adg:violation:{vid}")
                if v:
                    print(f"  [{v.get('category', '?')}] {v.get('file_path', '?')}:{v.get('line_number', '?')} — {v.get('evidence', '')[:80]}")
                else:
                    print(f"  violation_id={vid}")
            return
        if total == 0:
            print("SOURCE: Redis | 0 violations")
            return
        print("Redis: violation detail missing — fallback to SQLite")
    else:
        print("Redis: UNAVAILABLE")

    con = _sqlite_con()
    if not con:
        return
    try:
        rows = con.execute(
            "SELECT source_file, relation_type, symbol FROM edges WHERE relation_type='violates' LIMIT ?", (limit,)
        ).fetchall()
        print(f"SOURCE: SQLite (approximation via violates edges) | Showing: {len(rows)}")
        for row in rows:
            print(f"  {row[0]} [{row[1]}] {row[2]}")
    except Exception as e:
        print(f"SQLite fallback error: {e}")
    con.close()


def cmd_sql(args: list[str]) -> None:
    if not args:
        print("Usage: sql <SQL query>")
        return
    query = " ".join(args)
    _header(f"SQL QUERY")
    print(f"  {query}\n")

    con = _sqlite_con()
    if not con:
        print("ERROR: No SQLite file found")
        return
    try:
        rows = con.execute(query).fetchall()
        if not rows:
            print("(no results)")
        else:
            # Print header from column names
            col_names = [d[0] for d in con.execute(query).description]
            print("  " + " | ".join(col_names))
            print("  " + "-" * 60)
            for row in rows:
                print("  " + " | ".join(str(v) for v in row))
            print(f"\n  ({len(rows)} rows)")
    except Exception as e:
        print(f"ERROR: {e}")
    con.close()


def cmd_edge_counts(args: list[str]) -> None:
    top_n = int(args[0]) if args else 30
    _header(f"EDGE COUNTS BY RELATION TYPE (top {top_n})")

    con = _sqlite_con()
    if not con:
        print("ERROR: No SQLite file")
        return
    rows = con.execute(
        f"SELECT relation_type, COUNT(*) as c FROM edges GROUP BY relation_type ORDER BY c DESC LIMIT {top_n}"
    ).fetchall()
    total = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    print(f"Total edges: {total:,}\n")
    for row in rows:
        bar = "#" * min(50, row[1] * 50 // max(rows[0][1], 1))
        print(f"  {row[0]:<45} {row[1]:>8,}  {bar}")
    con.close()


def cmd_layer_counts(args: list[str]) -> None:
    _header("NODE COUNTS BY LAYER")
    con = _sqlite_con()
    if not con:
        print("ERROR: No SQLite file")
        return
    rows = con.execute(
        "SELECT layer, COUNT(*) as c FROM nodes GROUP BY layer ORDER BY layer"
    ).fetchall()
    total = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    print(f"Total nodes: {total:,}\n")
    for row in rows:
        print(f"  {(row[0] or 'None'):<12} {row[1]:>8,}")
    con.close()


def cmd_find_node(args: list[str]) -> None:
    if not args:
        print("Usage: find_node <name_fragment>")
        return
    fragment = args[0]
    _header(f"FIND NODE: '{fragment}'")

    con = _sqlite_con()
    if not con:
        return
    rows = con.execute(
        "SELECT id, adg_name, layer, entity_type, resolved_path FROM nodes WHERE adg_name LIKE ? LIMIT 30",
        (f"%{fragment}%",),
    ).fetchall()
    print(f"Matches: {len(rows)}")
    for row in rows:
        print(f"  id={row[0]} layer={row[2]} type={row[3]}")
        print(f"    {row[1]}")
        if row[4]:
            print(f"    path: {row[4]}")
    con.close()


def cmd_module_context(args: list[str]) -> None:
    if not args:
        print("Usage: module_context <node_id>")
        return
    node_id = args[0]
    _header(f"MODULE CONTEXT: {node_id}")

    r = _get_redis()
    if r:
        data = r.hgetall(f"adg:module_context:{node_id}")
        if data:
            print("SOURCE: Redis (precomputed)")
            _pp(data)
            return
        print("Redis: no precomputed context — using SQLite")

    con = _sqlite_con()
    if not con:
        return

    node = con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    if node:
        print("NODE:", dict(node))
    else:
        print(f"Node {node_id} not found")

    out_counts = con.execute(
        "SELECT relation_type, COUNT(*) c FROM edges WHERE src_id=? GROUP BY relation_type ORDER BY c DESC",
        (node_id,),
    ).fetchall()
    print("\nOUTGOING by relation:")
    for row in out_counts:
        print(f"  {row[0]}: {row[1]}")

    in_counts = con.execute(
        "SELECT relation_type, COUNT(*) c FROM edges WHERE dst_id=? GROUP BY relation_type ORDER BY c DESC",
        (node_id,),
    ).fetchall()
    print("\nINCOMING by relation:")
    for row in in_counts:
        print(f"  {row[0]}: {row[1]}")
    con.close()


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
_COMMANDS = {
    "status": cmd_status,
    "meta": cmd_meta,
    "node": cmd_node,
    "nodes_by_layer": cmd_nodes_by_layer,
    "nodes_by_file": cmd_nodes_by_file,
    "edge_fanout": cmd_edge_fanout,
    "edge_fanin": cmd_edge_fanin,
    "violations": cmd_violations,
    "sql": cmd_sql,
    "edge_counts": cmd_edge_counts,
    "layer_counts": cmd_layer_counts,
    "find_node": cmd_find_node,
    "module_context": cmd_module_context,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        print("\nAvailable commands:", ", ".join(sorted(_COMMANDS)))
        return

    cmd_name = sys.argv[1]
    cmd_args = sys.argv[2:]

    fn = _COMMANDS.get(cmd_name)
    if not fn:
        print(f"Unknown command: '{cmd_name}'")
        print("Available:", ", ".join(sorted(_COMMANDS)))
        sys.exit(1)

    fn(cmd_args)


if __name__ == "__main__":
    main()
