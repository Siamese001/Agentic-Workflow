
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 1. Check if ADG is hot
meta = r.hgetall('adg:meta')
print("=== ADG Meta ===")
for k, v in sorted(meta.items()):
    print(f"  {k}: {v}")

# 2. Get L_UNKNOWN node IDs
l_unknown_ids = r.smembers('adg:nodes:by_layer:L_UNKNOWN')
print("\n=== L_UNKNOWN Node Count ===")
print(f"Total L_UNKNOWN nodes: {len(l_unknown_ids)}")

# 3. Sample 50 L_UNKNOWN nodes and categorize
print("\n=== Sampling 50 L_UNKNOWN nodes ===")
sample_ids = list(l_unknown_ids)[:50]
identity_kind_counts = {}
entity_type_counts = {}
resolved_path_prefixes = {}

for node_id in sample_ids:
    node = r.hgetall(f'adg:node:{node_id}')
    identity_kind = node.get('identity_kind', 'UNKNOWN')
    entity_type = node.get('entity_type', 'UNKNOWN')
    resolved_path = node.get('resolved_path', '')

    identity_kind_counts[identity_kind] = identity_kind_counts.get(identity_kind, 0) + 1
    entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1

    if resolved_path:
        prefix = resolved_path.split('/')[0] if '/' in resolved_path else resolved_path
        resolved_path_prefixes[prefix] = resolved_path_prefixes.get(prefix, 0) + 1

    # Print first 10 samples
    if len([k for k in identity_kind_counts.values()]) <= 10:
        print(f"  [{entity_type}|{identity_kind}] {node.get('adg_name', 'N/A')} -> {resolved_path or '(null)'}")

print("\n=== Sample breakdown (50 nodes) ===")
print("By identity_kind:")
for k, v in sorted(identity_kind_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print("\nBy entity_type:")
for k, v in sorted(entity_type_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print("\nBy resolved_path prefix:")
for k, v in sorted(resolved_path_prefixes.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# 4. Full scan to get accurate identity_kind distribution
print(f"\n=== Full L_UNKNOWN scan (all {len(l_unknown_ids)} nodes) ===")
full_identity_counts = {}
full_entity_counts = {}
full_path_prefixes = {}
repo_module_paths = []

for node_id in l_unknown_ids:
    node = r.hgetall(f'adg:node:{node_id}')
    identity_kind = node.get('identity_kind', 'UNKNOWN')
    entity_type = node.get('entity_type', 'UNKNOWN')
    resolved_path = node.get('resolved_path', '')

    full_identity_counts[identity_kind] = full_identity_counts.get(identity_kind, 0) + 1
    full_entity_counts[entity_type] = full_entity_counts.get(entity_type, 0) + 1

    if resolved_path:
        prefix = resolved_path.split('/')[0] if '/' in resolved_path else resolved_path
        full_path_prefixes[prefix] = full_path_prefixes.get(prefix, 0) + 1

    if identity_kind == 'repo_module':
        repo_module_paths.append(resolved_path)

print("By identity_kind:")
for k, v in sorted(full_identity_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print("\nBy entity_type:")
for k, v in sorted(full_entity_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print("\nBy resolved_path prefix (top 20):")
for k, v in sorted(full_path_prefixes.items(), key=lambda x: -x[1])[:20]:
    print(f"  {k}: {v}")

print(f"\n=== L_UNKNOWN repo_module paths ({len(repo_module_paths)} total) ===")
for path in sorted(repo_module_paths)[:50]:
    print(f"  {path}")
if len(repo_module_paths) > 50:
    print(f"  ... and {len(repo_module_paths) - 50} more")
