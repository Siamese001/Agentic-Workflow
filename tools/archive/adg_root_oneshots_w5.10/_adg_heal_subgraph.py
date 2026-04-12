"""
Query the refreshed ADG file_graph for healing/routing subgraph.
Uses the compact edge format: s=src_id, d=dst_id, r=relation, k=kind, f=file, ln=line
"""

import glob
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = str(REPO_ROOT / "artifacts" / "adg")
fg_path = sorted(glob.glob(Path(ADG_DIR) / "adg_file_graph_*.json"))[-1]
print(f"Loading: {Path(fg_path).name}")
with open(fg_path, encoding="utf-8") as f:
    fg = json.load(f)
nodes = fg["nodes"]
edges = fg["edges"]
id_to_node = {int(k): v for k, v in nodes.items()}
print(f"Nodes: {len(nodes)}  Edges: {len(edges)}")
HEAL_PATTERNS = [
    "healing_tier_router",
    "healing_tier_dispatcher",
    "healing_tier_config",
    "healing_tier_types",
    "healing_provider_adapters",
    "healing_event_emitter",
    "qwen_vllm_inference",
    "qwen_circuit_breaker",
    "qwen_gpu_validator",
    "qwen_health",
    "qwen_determinism",
    "qwen_meta_learning",
    "tiering_allowlist",
    "remediation_dispatcher",
    "execute_ssot",
    "vllm_routing_predicates",
    "bmg_embedding_similarity",
    "hardened_gemini_executor",
    "SovereignLLMGateway",
    "HardenedGeminiExecutor",
]

heal_ids = {int(k) for k, v in nodes.items() if matches(v)}
print(f"\nHealing/routing nodes matched: {len(heal_ids)}")
sorted_nodes = sorted(
    [(nid, id_to_node[nid]) for nid in heal_ids if id_to_node[nid].get("t") == "module"],
    key=lambda x: (x[1].get("l", ""), x[1].get("n", "")),
)
print(f"\n=== HEALING/ROUTING MODULE NODES ({len(sorted_nodes)}) ===")
for nid, nd in sorted_nodes:
    print(f"  [{nd.get('l', '?')}] {nd.get('p') or nd.get('n', '?')}  crit={nd.get('c', '?')}")
print("\n=== INTRA-SUBGRAPH EDGES ===")
intra = [e for e in edges if e["s"] in heal_ids and e["d"] in heal_ids]
intra.sort(key=lambda e: (id_to_node.get(e["s"], {}).get("n", ""), e.get("r", "")))
for e in intra:
    sn = id_to_node.get(e["s"], {}).get("p") or id_to_node.get(e["s"], {}).get("n", "?")
    dn = id_to_node.get(e["d"], {}).get("p") or id_to_node.get(e["d"], {}).get("n", "?")
    sym = e.get("sym", "")
    print(f"  {sn}  --[{e.get('r', '?')}]-->  {dn}" + (f"  sym={sym}" if sym else ""))
print("\n=== EXTERNAL CALLERS OF DISPATCHER/ROUTER ===")
dispatcher_ids = {
    int(k)
    for k, v in nodes.items()
    if "healing_tier_dispatcher" in (v.get("n") or "").lower()
    or "healing_tier_router" in (v.get("n") or "").lower()
}
for e in edges:
    if e["d"] in dispatcher_ids and e["s"] not in heal_ids:
        sn = id_to_node.get(e["s"], {}).get("p") or id_to_node.get(e["s"], {}).get("n", "?")
        dn = id_to_node.get(e["d"], {}).get("p") or id_to_node.get(e["d"], {}).get("n", "?")
        print(f"  {sn}  --[{e.get('r', '?')}]-->  {dn}")
print("\n=== execute_ssot -> L2 healing imports ===")
ssot_ids = {int(k) for k, v in nodes.items() if "execute_ssot" in (v.get("n") or "").lower()}
l2_heal_ids = {
    int(k)
    for k, v in nodes.items()
    if "L2_execution/healers" in (v.get("n") or "") or "L2_execution/healers" in (v.get("p") or "")
}
for e in edges:
    if e["s"] in ssot_ids and e["d"] in l2_heal_ids:
        sn = id_to_node.get(e["s"], {}).get("p") or id_to_node.get(e["s"], {}).get("n", "?")
        dn = id_to_node.get(e["d"], {}).get("n", "?")
        print(f"  {sn}  --[{e.get('r', '?')}]-->  {dn}")
print("\n=== VIOLATIONS IN HEALING SUBGRAPH ===")
viols = [
    e
    for e in edges
    if e.get("k", "") in ("GV_violates", "violation") and (e["s"] in heal_ids or e["d"] in heal_ids)
]
for e in viols:
    sn = id_to_node.get(e["s"], {}).get("p") or id_to_node.get(e["s"], {}).get("n", "?")
    dn = id_to_node.get(e["d"], {}).get("p") or id_to_node.get(e["d"], {}).get("n", "?")
    print(f"  {sn}  --[{e.get('r', '?')}]-->  {dn}  (file={e.get('f', '?')} ln={e.get('ln', '?')})")
print("\n=== SUBGRAPH EDGE SUMMARY (by relation) ===")
all_heal_edges = [e for e in edges if e["s"] in heal_ids or e["d"] in heal_ids]
by_rel = defaultdict(int)
for e in all_heal_edges:
    by_rel[e.get("r", "?")] += 1
for rel, cnt in sorted(by_rel.items(), key=lambda x: -x[1]):
    print(f"  {rel}: {cnt}")
