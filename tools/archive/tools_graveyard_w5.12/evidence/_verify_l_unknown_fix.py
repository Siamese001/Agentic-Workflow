import json

import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 1. New L_UNKNOWN count
l_unknown_ids = r.smembers('adg:nodes:by_layer:L_UNKNOWN')
print(f"L_UNKNOWN total: {len(l_unknown_ids)}")

# 2. Full breakdown by identity_kind
full_identity_counts = {}
repo_module_paths = []

for node_id in l_unknown_ids:
    node = r.hgetall(f'adg:node:{node_id}')
    identity_kind = node.get('identity_kind', 'UNKNOWN')
    full_identity_counts[identity_kind] = full_identity_counts.get(identity_kind, 0) + 1
    if identity_kind == 'repo_module':
        repo_module_paths.append(node.get('resolved_path', ''))

print("\nBy identity_kind:")
for k, v in sorted(full_identity_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\nL_UNKNOWN repo_module nodes remaining: {len(repo_module_paths)}")
for p in sorted(repo_module_paths):
    print(f"  {p}")

# 3. Confirm apps_eval/apps_exec/apps_research/apps_rfp now in L_APP
l_app_ids = r.smembers('adg:nodes:by_layer:L_APP')
prefix_counts = {}
for nid in l_app_ids:
    node = r.hgetall(f'adg:node:{nid}')
    rp = node.get('resolved_path', '')
    if rp:
        prefix = rp.split('/')[0]
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
print(f"\nL_APP top-level dirs ({len(l_app_ids)} total nodes):")
for k, v in sorted(prefix_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# 4. Confirm agentic_core/patterns now in L_SHARED
l_shared_patterns = []
l_shared_ids = r.smembers('adg:nodes:by_layer:L_SHARED')
for nid in l_shared_ids:
    node = r.hgetall(f'adg:node:{nid}')
    rp = node.get('resolved_path', '')
    if rp and rp.startswith('agentic_core/patterns'):
        l_shared_patterns.append(rp)
print(f"\nagentic_core/patterns nodes now in L_SHARED: {len(l_shared_patterns)}")
for p in sorted(l_shared_patterns):
    print(f"  {p}")

# 5. New snapshot summary
snapshot = json.loads(r.get('adg:snapshot'))
print("\n=== Updated snapshot by_layer ===")
for layer, count in sorted(snapshot['by_layer'].items()):
    print(f"  {layer}: {count}")
