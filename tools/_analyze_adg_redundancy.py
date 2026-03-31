"""Analyze ADG file redundancy and size reduction opportunities."""

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO = Path(r"c:\Git\Agentic-Workflow")
ADG = REPO / "artifacts" / "adg"
TS = "0427"


def load_json(name):
    p = ADG / f"{name}_03132026_{TS}.json"
    with open(p) as f:
        return json.load(f), p.stat().st_size


def analyze_sqlite():
    db = ADG / f"adg_indexed_03132026_{TS}.sqlite"
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"\n[SQLITE] Tables: {tables}")
    table_info = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM [{t}]")
        count = cur.fetchone()[0]
        cur.execute(f"SELECT * FROM [{t}] LIMIT 1")
        cols = [d[0] for d in cur.description] if cur.description else []
        table_info[t] = {"rows": count, "cols": cols}
        print(f"  {t}: {count:,} rows, cols={cols}")
    conn.close()
    return table_info


def analyze_symbol_graph():
    data, size = load_json("adg_symbol_graph")
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])
    # node key distribution
    all_keys = defaultdict(int)
    key_vals = defaultdict(set)
    for n in nodes.values():
        for k, v in n.items():
            all_keys[k] += 1
            if isinstance(v, str) and len(v) < 50:
                key_vals[k].add(v)
    print(f"\n[SYMBOL_GRAPH] Size: {size / 1e6:.2f} MB")
    print(f"  Nodes: {len(nodes):,}, Edges: {len(edges):,}")
    print("  Node keys (field -> count, unique values sample):")
    for k, cnt in sorted(all_keys.items()):
        uvals = sorted(key_vals[k])[:10] if key_vals[k] else ["(non-str or long)"]
        print(f"    '{k}': present in {cnt:,} nodes | unique vals: {uvals}")
    return set(all_keys.keys()), len(nodes), len(edges)


def analyze_file_graph():
    data, size = load_json("adg_file_graph")
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])
    all_keys = defaultdict(int)
    key_vals = defaultdict(set)
    for n in nodes.values():
        for k, v in n.items():
            all_keys[k] += 1
            if isinstance(v, str) and len(v) < 50:
                key_vals[k].add(v)
    print(f"\n[FILE_GRAPH] Size: {size / 1e6:.2f} MB")
    print(f"  Nodes: {len(nodes):,}, Edges: {len(edges):,}")
    print("  Node keys:")
    for k, cnt in sorted(all_keys.items()):
        uvals = sorted(key_vals[k])[:5] if key_vals[k] else ["(non-str or long)"]
        print(f"    '{k}': {cnt:,} nodes | sample: {uvals}")
    return set(all_keys.keys()), len(nodes), len(edges)


def analyze_governance_graph():
    data, size = load_json("adg_governance_graph")
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])
    all_keys = defaultdict(int)
    key_vals = defaultdict(set)
    for n in nodes.values():
        for k, v in n.items():
            all_keys[k] += 1
            if isinstance(v, str) and len(v) < 50:
                key_vals[k].add(v)
    print(f"\n[GOVERNANCE_GRAPH] Size: {size / 1e6:.2f} MB")
    print(f"  Nodes: {len(nodes):,}, Edges: {len(edges):,}")
    print("  Node keys:")
    for k, cnt in sorted(all_keys.items()):
        uvals = sorted(key_vals[k])[:5] if key_vals[k] else ["(non-str or long)"]
        print(f"    '{k}': {cnt:,} nodes | sample: {uvals}")
    return set(all_keys.keys()), len(nodes), len(edges)


def analyze_graphsnap():
    data, size = load_json("adg_graphsnap")
    print(f"\n[GRAPHSNAP] Size: {size / 1e6:.2f} MB")
    print(f"  Top-level keys: {list(data.keys())}")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"  '{k}': dict with {len(v)} keys")
        elif isinstance(v, list):
            print(f"  '{k}': list with {len(v)} items")
        else:
            print(f"  '{k}': {type(v).__name__} = {str(v)[:80]}")
    return data


def analyze_snapshot():
    data, size = load_json("adg_snapshot")
    print(f"\n[SNAPSHOT] Size: {size / 1e6:.4f} MB")
    print(f"  Top-level keys: {list(data.keys())}")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"  '{k}': dict with {len(v)} keys -> {list(v.keys())[:8]}")
        elif isinstance(v, list):
            print(f"  '{k}': list with {len(v)} items")
        else:
            print(f"  '{k}': {str(v)[:120]}")


def compare_node_sets():
    """Check if file_graph and symbol_graph share the same node IDs."""
    sym, _ = load_json("adg_symbol_graph")
    fil, _ = load_json("adg_file_graph")
    gov, _ = load_json("adg_governance_graph")

    sym_ids = set(sym.get("nodes", {}).keys())
    fil_ids = set(fil.get("nodes", {}).keys())
    gov_ids = set(gov.get("nodes", {}).keys())

    print("\n[NODE_OVERLAP]")
    print(f"  symbol_graph nodes:     {len(sym_ids):,}")
    print(f"  file_graph nodes:       {len(fil_ids):,}")
    print(f"  governance_graph nodes: {len(gov_ids):,}")
    print(f"  sym ∩ fil:  {len(sym_ids & fil_ids):,}")
    print(f"  sym ∩ gov:  {len(sym_ids & gov_ids):,}")
    print(f"  fil ∩ gov:  {len(fil_ids & gov_ids):,}")
    print(f"  sym only:   {len(sym_ids - fil_ids - gov_ids):,}")
    print(f"  fil only:   {len(fil_ids - sym_ids - gov_ids):,}")
    print(f"  gov only:   {len(gov_ids - sym_ids - fil_ids):,}")

    # Compare node field content for overlapping nodes
    overlap = list(sym_ids & fil_ids)[:3]
    print("\n  Sample overlapping nodes (sym vs fil):")
    for nid in overlap:
        sn = sym["nodes"][nid]
        fn = fil["nodes"][nid]
        print(f"    ID={nid}")
        print(f"      sym: {sn}")
        print(f"      fil: {fn}")

    # Check edge overlap
    sym_edges = {(e.get("s"), e.get("t"), e.get("r")) for e in sym.get("edges", [])}
    fil_edges = {(e.get("s"), e.get("t"), e.get("r")) for e in fil.get("edges", [])}
    gov_edges = {(e.get("s"), e.get("t"), e.get("r")) for e in gov.get("edges", [])}

    print("\n[EDGE_OVERLAP]")
    print(f"  symbol_graph edges:     {len(sym_edges):,}")
    print(f"  file_graph edges:       {len(fil_edges):,}")
    print(f"  governance_graph edges: {len(gov_edges):,}")
    print(f"  sym ∩ fil: {len(sym_edges & fil_edges):,}")
    print(f"  sym ∩ gov: {len(sym_edges & gov_edges):,}")
    print(f"  fil ∩ gov: {len(fil_edges & gov_edges):,}")


def sqlite_vs_json():
    """Check if sqlite tables mirror JSON file data."""
    db = ADG / f"adg_indexed_03132026_{TS}.sqlite"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Sample nodes from sqlite
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]

    # Load symbol graph for comparison
    sym, _ = load_json("adg_symbol_graph")
    sym_nodes = sym.get("nodes", {})
    sym_paths = {v.get("p") for v in sym_nodes.values() if v.get("p")}

    print("\n[SQLITE vs JSON COMPARISON]")
    for t in tables:
        try:
            cur.execute(f"SELECT * FROM [{t}] LIMIT 5")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            # Check if path column exists
            path_col = next((c for c in cols if c.lower() in ("path", "p", "file_path", "module_path")), None)
            if path_col:
                pidx = cols.index(path_col)
                sqlite_paths = {r[pidx] for r in rows if r[pidx]}
                overlap = sqlite_paths & sym_paths
                print(
                    f"  Table '{t}': path col='{path_col}', sample paths overlap with symbol_graph: {len(overlap)}/{len(sqlite_paths)}"
                )
            else:
                print(f"  Table '{t}': no path col found | cols={cols}")
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"  Table '{t}': ERROR {e}")
    conn.close()


def size_summary():
    print(f"\n{'=' * 80}")
    print("SIZE SUMMARY")
    print(f"{'=' * 80}")
    files = {
        "adg_symbol_graph": f"adg_symbol_graph_03132026_{TS}.json",
        "adg_file_graph": f"adg_file_graph_03132026_{TS}.json",
        "adg_governance_graph": f"adg_governance_graph_03132026_{TS}.json",
        "adg_graphsnap": f"adg_graphsnap_03132026_{TS}.json",
        "adg_snapshot": f"adg_snapshot_03132026_{TS}.json",
        "adg_indexed (sqlite)": f"adg_indexed_03132026_{TS}.sqlite",
    }
    total = 0
    for label, fname in files.items():
        p = ADG / fname
        sz = p.stat().st_size
        total += sz
        print(f"  {label:<30} {sz / 1e6:8.2f} MB")
    print(f"  {'TOTAL':<30} {total / 1e6:8.2f} MB")


if __name__ == "__main__":
    print("ADG File Redundancy Analysis")
    print("=" * 80)
    size_summary()
    sym_keys, sym_nodes, sym_edges = analyze_symbol_graph()
    fil_keys, fil_nodes, fil_edges = analyze_file_graph()
    gov_keys, gov_nodes, gov_edges = analyze_governance_graph()
    analyze_graphsnap()
    analyze_snapshot()
    analyze_sqlite()
    compare_node_sets()
    sqlite_vs_json()
    print("\n" + "=" * 80)
    print("FIELD KEY COMPARISON ACROSS GRAPHS")
    print("=" * 80)
    print(f"  symbol_graph fields: {sorted(sym_keys)}")
    print(f"  file_graph fields:   {sorted(fil_keys)}")
    print(f"  governance fields:   {sorted(gov_keys)}")
    print(f"  sym ∩ fil:  {sorted(sym_keys & fil_keys)}")
    print(f"  sym - fil:  {sorted(sym_keys - fil_keys)}")
    print(f"  fil - sym:  {sorted(fil_keys - sym_keys)}")
