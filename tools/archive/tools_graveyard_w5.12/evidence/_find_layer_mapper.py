import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Search for nodes whose adg_name or resolved_path contains "layer_map" or "layer_assign"
# We'll scan adg:nodes:by_file keys to find relevant files
print("=== Searching for layer mapper files via Redis ===")

# Check known candidate patterns
candidates = [
    "adg:nodes:by_file:agentic_core/adg/extraction/static_scanner.py",
    "adg:nodes:by_file:tools/adg/adg_redis_ingest.py",
]

# Scan for keys matching layer_map patterns
cursor = 0
layer_map_keys = []
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:*layer*", count=200)
    layer_map_keys.extend(keys)
    if cursor == 0:
        break

print(f"Keys matching '*layer*' in file paths: {len(layer_map_keys)}")
for k in sorted(layer_map_keys):
    print(f"  {k}")

# Also scan for assign/classify/mapper
cursor = 0
classify_keys = []
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:*classif*", count=200)
    classify_keys.extend(keys)
    if cursor == 0:
        break

cursor = 0
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:*assign*", count=200)
    classify_keys.extend(keys)
    if cursor == 0:
        break

cursor = 0
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:*mapper*", count=200)
    classify_keys.extend(keys)
    if cursor == 0:
        break

print(f"\nKeys matching classif/assign/mapper in file paths: {len(classify_keys)}")
for k in sorted(classify_keys):
    print(f"  {k}")

# Look for the static_scanner node to find what it imports/uses
scanner_key = "adg:nodes:by_file:agentic_core/adg/extraction/static_scanner.py"
scanner_ids = r.smembers(scanner_key)
print(f"\n=== static_scanner.py nodes: {len(scanner_ids)} ===")
for nid in list(scanner_ids)[:5]:
    node = r.hgetall(f"adg:node:{nid}")
    print(
        f"  {node.get('adg_name')} [{node.get('entity_type')}|{node.get('identity_kind')}] layer={node.get('layer')}"
    )
    # Get fan-out (imports)
    imports = r.smembers(f"adg:edge:{nid}:imports")
    print(f"    imports {len(imports)} targets")
