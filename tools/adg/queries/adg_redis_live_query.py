"""
Direct Redis hot-cache query for LLM alignment gap analysis.
Queries HASH nodes via Python redis-py (MCP can only GET strings).
Focuses on edge types surfaced in the snapshot graph_plane_counts.
"""
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Target edge types most relevant to LLM alignment
ALIGNMENT_EDGE_TYPES = [
    'builds_dpo_batch',
    'produces_preference_pair',
    'validated_by_llm_gateway',
    'scores_groundedness',
    'gated_by_confidence',
    'escalates_to_human',
    'applies_guardrail',
    'dispatches_healing_run',
    'orchestrates_healing',
    'generates_prompt',
    'consumes_prompt',
    'instruction_injection_source',
    'reenters_safety',
    'validated_by_safety_plane',
    'hard_fails_untranscripted',
]

# Collect all src node IDs for each alignment edge type
print("=== ALIGNMENT EDGE SOURCE NODES (from Redis hot cache) ===\n")

node_ids_to_fetch = set()
edge_src_map = {}  # edge_type -> list of src node ids

cursor = 0
# Scan for adg:edge:*:<relation_type> keys
for edge_type in ALIGNMENT_EDGE_TYPES:
    pattern = f'adg:edge:*:{edge_type}'
    cur = 0
    src_ids = []
    while True:
        cur, keys = r.scan(cur, match=pattern, count=1000)
        for key in keys:
            # key format: adg:edge:<src_id>:<relation_type>
            parts = key.decode().split(':')
            if len(parts) >= 4:
                src_id = parts[2]
                src_ids.append(src_id)
                node_ids_to_fetch.add(src_id)
                # Also get dst node ids
                members = r.smembers(key)
                for m in members:
                    node_ids_to_fetch.add(m.decode())
        if cur == 0:
            break
    edge_src_map[edge_type] = src_ids

# Fetch all relevant node hashes
print(f"Fetching {len(node_ids_to_fetch)} unique nodes...")
node_cache = {}
for nid in node_ids_to_fetch:
    data = r.hgetall(f'adg:node:{nid}')
    if data:
        node_cache[nid] = {k.decode(): v.decode() for k, v in data.items()}

# Print results per edge type
for edge_type in ALIGNMENT_EDGE_TYPES:
    src_ids = edge_src_map.get(edge_type, [])
    if not src_ids:
        print(f"[{edge_type}] NO SOURCES FOUND")
        continue
    print(f"\n[{edge_type}] ({len(src_ids)} sources)")
    seen = set()
    for sid in src_ids:
        if sid in seen:
            continue
        seen.add(sid)
        node = node_cache.get(sid, {})
        name = node.get('adg_name', f'<id:{sid}>')
        layer = node.get('layer', '?')
        path = node.get('resolved_path', '')
        # Get destination nodes
        dst_ids = r.smembers(f'adg:edge:{sid}:{edge_type}')
        dst_names = []
        for did in list(dst_ids)[:3]:
            dn = node_cache.get(did.decode(), {})
            dst_names.append(dn.get('adg_name', f'<id:{did.decode()}>').replace('ADG::Module::','').replace('ADG::Symbol::',''))
        dst_str = ' -> ' + ', '.join(dst_names) if dst_names else ''
        print(f"  [{layer}] {name.replace('ADG::Module::','').replace('ADG::Symbol::','')} | {path}{dst_str}")

# --- Check coverage for alignment-critical prod modules ---
print("\n\n=== COVERAGE CHECK: ALIGNMENT-CRITICAL PROD MODULES ===")

# Find nodes with alignment edge types and check if they have 'covers' fan-in
alignment_prod_nodes = {}
for edge_type in ['builds_dpo_batch', 'produces_preference_pair', 'scores_groundedness',
                   'validated_by_llm_gateway', 'applies_guardrail', 'gated_by_confidence']:
    for sid in edge_src_map.get(edge_type, []):
        node = node_cache.get(sid, {})
        layer = node.get('layer', '')
        if layer and 'TEST' not in layer and 'UNKNOWN' not in layer:
            alignment_prod_nodes[sid] = (node, edge_type)

covered = 0
uncovered_list = []
for nid, (node, edge_type) in alignment_prod_nodes.items():
    # Check fan-in covers edges
    covers_in = r.smembers(f'adg:edge:in:{nid}:covers')
    if covers_in:
        covered += 1
    else:
        uncovered_list.append((node.get('adg_name','?'), node.get('layer','?'), node.get('resolved_path','?'), edge_type))

print(f"Alignment-critical prod nodes: {len(alignment_prod_nodes)} total, {covered} covered, {len(uncovered_list)} UNCOVERED")
print("\nUNCOVERED:")
for name, layer, path, etype in uncovered_list:
    print(f"  [{layer}] {name.replace('ADG::Module::','')} (via {etype}) | {path}")

# --- Concept gap: which alignment edge types have ZERO prod sources? ---
print("\n\n=== ALIGNMENT EDGE TYPES WITH ZERO PROD SOURCES ===")
for edge_type in ALIGNMENT_EDGE_TYPES:
    prod_srcs = [sid for sid in edge_src_map.get(edge_type,[])
                 if node_cache.get(sid,{}).get('layer','') not in ('','L_TEST','L_UNKNOWN')]
    if not prod_srcs:
        print(f"  ABSENT (prod): {edge_type}")
    else:
        print(f"  PRESENT ({len(prod_srcs)} prod nodes): {edge_type}")

print("\nDONE")
