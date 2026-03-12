"""Peek at governance graph edge structure and identify coverage gaps."""

import json
from pathlib import Path

gov_files = sorted(Path("artifacts/adg").glob("adg_governance_graph_*.json"))
with open(gov_files[-1]) as f:
    gov = json.load(f)

edges = gov.get("edges", [])
print(f"Total governance edges: {len(edges)}")
if edges:
    print("Sample edge keys:", list(edges[0].keys()))
    print("Sample edge[0]:", edges[0])
    print("Sample edge[1]:", edges[1] if len(edges) > 1 else "N/A")

# Count by rel key
rels = {}
for e in edges:
    for k in ["rel", "relation", "type", "kind", "relation_type", "edge_type"]:
        if k in e:
            rels[e[k]] = rels.get(e[k], 0) + 1
            break

print()
print("Relation types found:", rels)

# Also check snapshot for gap planes
snap_files = sorted(Path("artifacts/adg").glob("adg_snapshot_*.json"))
with open(snap_files[-1]) as f:
    snap = json.load(f)
print()
print("Snapshot keys:", list(snap.keys()))
if "gap_planes" in snap:
    print("Gap planes:", snap["gap_planes"])
if "planes" in snap:
    print("Planes:", snap["planes"])
for k, v in snap.items():
    print(f"  {k}: {str(v)[:80]}")
