import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Check the static_scanner for what it imports re: layer assignment
scanner_ids = r.smembers("adg:nodes:by_file:agentic_core/adg/extraction/static_scanner.py")
print("=== static_scanner.py fan-out imports ===")
for nid in scanner_ids:
    node = r.hgetall(f"adg:node:{nid}")
    if node.get("entity_type") == "module":
        imports = r.smembers(f"adg:edge:{nid}:imports")
        print(f"  Module imports {len(imports)} targets:")
        for tid in imports:
            tnode = r.hgetall(f"adg:node:{tid}")
            print(f"    -> {tnode.get('adg_name', tid)} [{tnode.get('identity_kind')}]")

# Check structure_blueprint files - the SSOT for path rules
print("\n=== structure_blueprint files ===")
cursor = 0
bp_keys = []
while True:
    cursor, keys = r.scan(
        cursor, match="adg:nodes:by_file:agentic_core/L5_safety/config/structure_blueprint/*", count=200
    )
    bp_keys.extend(keys)
    if cursor == 0:
        break
for k in sorted(bp_keys):
    print(f"  {k.replace('adg:nodes:by_file:', '')}")

# Check L0_routing config - often has path prefix rules
print("\n=== L0_routing config files ===")
cursor = 0
l0_keys = []
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:agentic_core/L0_routing/config/*", count=200)
    l0_keys.extend(keys)
    if cursor == 0:
        break
for k in sorted(l0_keys):
    print(f"  {k.replace('adg:nodes:by_file:', '')}")

# Check adg extraction files
print("\n=== agentic_core/adg/extraction files ===")
cursor = 0
ex_keys = []
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:agentic_core/adg/extraction/*", count=200)
    ex_keys.extend(keys)
    if cursor == 0:
        break
for k in sorted(ex_keys):
    print(f"  {k.replace('adg:nodes:by_file:', '')}")

# Check agentic_core/adg/config files
print("\n=== agentic_core/adg/config files ===")
cursor = 0
adg_cfg_keys = []
while True:
    cursor, keys = r.scan(cursor, match="adg:nodes:by_file:agentic_core/adg/config/*", count=200)
    adg_cfg_keys.extend(keys)
    if cursor == 0:
        break
for k in sorted(adg_cfg_keys):
    print(f"  {k.replace('adg:nodes:by_file:', '')}")
