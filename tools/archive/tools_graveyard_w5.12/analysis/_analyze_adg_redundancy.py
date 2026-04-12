"""Analyze ADG file redundancy and size reduction opportunities."""

from pathlib import Path

REPO = Path(r"c:\Git\Agentic-Workflow")
ADG = REPO / "artifacts" / "adg"
TS = "0427"


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
