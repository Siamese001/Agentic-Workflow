import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Find all files that contain symbols related to layer assignment
# Search for nodes with 'assign_layer', 'get_layer', 'path_to_layer', '_layer_for' etc in adg_name
print("=== Searching for layer assignment symbols ===")
cursor = 0
hits = []
while True:
    cursor, keys = r.scan(cursor, match='adg:node:*', count=500)
    for k in keys:
        node = r.hgetall(k)
        name = node.get('adg_name', '')
        if any(term in name.lower() for term in ['assign_layer', 'get_layer', 'path_to_layer', '_layer_for', 'resolve_layer', 'infer_layer', 'classify_layer', 'layer_for_path', 'layer_map']):
            hits.append((name, node.get('resolved_path', ''), node.get('entity_type', ''), node.get('layer', '')))
    if cursor == 0:
        break

print(f"Found {len(hits)} matching symbols:")
for name, rp, et, layer in sorted(hits, key=lambda x: x[1]):
    print(f"  [{et}|{layer}] {name} -> {rp}")
