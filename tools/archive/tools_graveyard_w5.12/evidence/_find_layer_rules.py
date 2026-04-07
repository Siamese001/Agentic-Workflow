import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Get all nodes for the classification.py file
cls_ids = r.smembers('adg:nodes:by_file:agentic_core/L5_safety/config/structure_blueprint/classification.py')
print(f"=== classification.py nodes ({len(cls_ids)}) ===")
for nid in cls_ids:
    node = r.hgetall(f'adg:node:{nid}')
    print(f"  {node.get('adg_name')} [{node.get('entity_type')}|{node.get('identity_kind')}] layer={node.get('layer')}")

# Get all nodes for layer_authority.py
la_ids = r.smembers('adg:nodes:by_file:agentic_core/adg/analysis/layer_authority.py')
print(f"\n=== layer_authority.py nodes ({len(la_ids)}) ===")
for nid in la_ids:
    node = r.hgetall(f'adg:node:{nid}')
    print(f"  {node.get('adg_name')} [{node.get('entity_type')}|{node.get('identity_kind')}] layer={node.get('layer')}")

# Also check the static_scanner for path->layer assignment logic
scanner_ids = r.smembers('adg:nodes:by_file:agentic_core/adg/extraction/static_scanner.py')
print("\n=== static_scanner.py symbols that mention 'layer' ===")
for nid in scanner_ids:
    node = r.hgetall(f'adg:node:{nid}')
    name = node.get('adg_name', '')
    if 'layer' in name.lower() or 'Layer' in name:
        print(f"  {name} [{node.get('entity_type')}|{node.get('identity_kind')}]")

# Check for L_APP layer assignment - which files are in L_APP?
l_app_ids = r.smembers('adg:nodes:by_layer:L_APP')
print(f"\n=== L_APP top-level dirs (from {len(l_app_ids)} nodes) ===")
prefix_counts = {}
for nid in l_app_ids:
    node = r.hgetall(f'adg:node:{nid}')
    rp = node.get('resolved_path', '')
    if rp:
        prefix = rp.split('/')[0]
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
for k, v in sorted(prefix_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
