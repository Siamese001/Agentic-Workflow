"""Inspect actual node structure in the ADG file_graph."""

import glob
import json
import os

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
fg_path = sorted(glob.glob(os.path.join(ADG_DIR, "adg_file_graph_*.json")))[-1]
print(f"Loading: {os.path.basename(fg_path)}")

with open(fg_path, encoding="utf-8") as f:
    fg = json.load(f)

nodes = fg["nodes"]
edges = fg["edges"]
print(f"Nodes: {len(nodes)}  Edges: {len(edges)}")

# Show first 5 nodes - actual structure
print("\n=== FIRST 5 NODES (raw) ===")
for i, (k, v) in enumerate(list(nodes.items())[:5]):
    print(f"  key={k!r}  val={v!r}")

# Show first 3 edges
print("\n=== FIRST 3 EDGES (raw) ===")
for e in edges[:3]:
    print(f"  {e}")

# Try to find a healing node by iterating values
print("\n=== SEARCHING FOR 'heal' IN NODE VALUES ===")
count = 0
for k, v in nodes.items():
    v_str = str(v).lower()
    if "heal" in v_str or "qwen" in v_str or "execute_ssot" in v_str:
        print(f"  key={k!r}  val={v!r}")
        count += 1
        if count >= 20:
            break
if count == 0:
    print("  (none found - nodes may be numeric IDs only)")
    # Check what keys look like in a node value
    first_v = list(nodes.values())[0]
    print(f"  First node value type: {type(first_v).__name__}  val={first_v!r}")
