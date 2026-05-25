"""Diff G_REACH orphan sets between canonical ADG and shadow proof snapshot."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import networkx as nx
from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
    connect_snapshot,
    latest_snapshot,
)

PROD = ("L1", "L2", "L3", "L4", "L5", "L_APP", "L_PG")


def orphans(conn) -> set[str]:
    g = nx.DiGraph()
    for node_id, layer, et, path, _ in conn.execute(
        "SELECT id, layer, entity_type, resolved_path, adg_name FROM nodes"
    ):
        g.add_node(node_id, layer=layer or "", path=path or "", et=et or "")
    for src, tgt in conn.execute("SELECT src_id, dst_id FROM edges WHERE relation_type='imports'"):
        if src in g and tgt in g:
            g.add_edge(src, tgt)
    l0 = [n for n, d in g.nodes(data=True) if d["layer"] == "L0" and d["et"] == "module"]
    reach = set(l0)
    for s in l0:
        reach.update(nx.descendants(g, s))
    out: set[str] = set()
    for n, d in g.nodes(data=True):
        if d["et"] != "module" or d["layer"] not in PROD:
            continue
        if n not in reach:
            out.add(d["path"])
    return out


def main() -> int:
    shadow = ROOT / "artifacts/adg/shadow_reach_proof.sqlite"
    if not shadow.exists():
        print(f"missing shadow: {shadow}", file=sys.stderr)
        return 1
    canon = connect_snapshot(latest_snapshot())
    sh = connect_snapshot(shadow)
    try:
        a, b = orphans(canon), orphans(sh)
    finally:
        canon.close()
        sh.close()
    print(f"canonical={len(a)} shadow={len(b)} delta={len(a) - len(b)}")
    fixed_pg = sorted(x for x in a - b if "prompt_governance" in x or x.startswith("agentic_core/knowledge/"))
    print(f"fixed_l_pg={len(fixed_pg)}")
    for x in fixed_pg[:40]:
        print(f"  {x}")
    if len(fixed_pg) > 40:
        print(f"  ... +{len(fixed_pg) - 40} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
