"""
Focused: RLHF optimizer + SFT node details from Redis hot cache.
"""

import redis

r = redis.Redis(host="localhost", port=6379, db=0)


def get_nodes_for_file(filepath):
    members = r.smembers(f"adg:nodes:by_file:{filepath}")
    nodes = []
    for nid in members:
        data = r.hgetall(f"adg:node:{nid.decode()}")
        if data:
            nodes.append({k.decode(): v.decode() for k, v in data.items()})
    return nodes


def node_has_covers(node_id):
    return bool(r.smembers(f"adg:edge:in:{node_id}:covers"))


RLHF_FILES = [
    "system_learning/engines/rlhf_optimizer.py",
    "system_learning/engines/rlhf_optimizer_impl.py",
    "system_learning/engines/governance_reward_model.py",
]

print("=== RLHF OPTIMIZER + REWARD MODEL NODE DETAILS ===")
for fp in RLHF_FILES:
    nodes = get_nodes_for_file(fp)
    print(f"\n[{fp}]  ({len(nodes)} nodes)")
    for n in nodes:
        nid = n.get("id", "?")
        layer = n.get("layer", "?")
        etype = n.get("entity_type", "?")
        name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
        covered = node_has_covers(nid)
        # outbound edges
        edge_keys = r.keys(f"adg:edge:{nid}:*")
        rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
        # importers
        importers_raw = r.smembers(f"adg:edge:in:{nid}:imports")
        importer_layers = []
        for imp in importers_raw:
            d = r.hgetall(f"adg:node:{imp.decode()}")
            if d:
                lyr = d.get(b"layer", b"?").decode()
                nm = (
                    d.get(b"adg_name", b"?")
                    .decode()
                    .replace("ADG::Module::", "")
                    .replace("ADG::Symbol::", "")
                )
                importer_layers.append(f"[{lyr}] {nm}")
        print(f"  [{layer}] {name} | {etype} | covered={covered}")
        if rels:
            print(f"    edges: {rels}")
        if importer_layers:
            print(f"    imported_by: {importer_layers}")

# Check meta_learning_pipeline.py — is RLHFOptimizer wired there?
print("\n=== meta_learning_pipeline.py details ===")
nodes = get_nodes_for_file("system_learning/pipelines/meta_learning_pipeline.py")
for n in nodes:
    nid = n.get("id", "?")
    layer = n.get("layer", "?")
    etype = n.get("entity_type", "?")
    name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
    covered = node_has_covers(nid)
    edge_keys = r.keys(f"adg:edge:{nid}:*")
    rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
    # What does it import?
    imports_out = r.smembers(f"adg:edge:{nid}:imports")
    import_names = []
    for imp in imports_out:
        d = r.hgetall(f"adg:node:{imp.decode()}")
        if d:
            lyr = d.get(b"layer", b"?").decode()
            nm = d.get(b"adg_name", b"?").decode().replace("ADG::Module::", "").replace("ADG::Symbol::", "")
            if "UNKNOWN" not in lyr:
                import_names.append(f"[{lyr}] {nm}")
    print(f"  [{layer}] {name} | {etype} | covered={covered}")
    if rels:
        print(f"    edges: {rels}")
    if import_names:
        print(f"    imports: {import_names}")

# Check meta_learning_bus.py — uses GovernanceRewardModel
print("\n=== meta_learning_bus.py details ===")
nodes = get_nodes_for_file("system_learning/engines/meta_learning_bus.py")
for n in nodes:
    nid = n.get("id", "?")
    layer = n.get("layer", "?")
    etype = n.get("entity_type", "?")
    name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
    covered = node_has_covers(nid)
    edge_keys = r.keys(f"adg:edge:{nid}:*")
    rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
    imports_out = r.smembers(f"adg:edge:{nid}:imports")
    import_names = []
    for imp in imports_out:
        d = r.hgetall(f"adg:node:{imp.decode()}")
        if d:
            lyr = d.get(b"layer", b"?").decode()
            nm = d.get(b"adg_name", b"?").decode().replace("ADG::Module::", "").replace("ADG::Symbol::", "")
            if "UNKNOWN" not in lyr:
                import_names.append(f"[{lyr}] {nm}")
    print(f"  [{layer}] {name} | {etype} | covered={covered}")
    if rels:
        print(f"    edges: {rels}")
    if import_names:
        print(f"    imports (non-unknown): {import_names[:10]}")

# What is SFT-absent? Scan for any sft/finetune/train* files
print("\n=== SFT / fine-tune / trainer scan (Redis file index) ===")
for pattern in [
    "*sft*",
    "*fine_tun*",
    "*finetune*",
    "*trainer*",
    "*training*",
    "*feedback_collect*",
    "*human_feedback*",
    "*annotation*",
]:
    keys = r.keys(f"adg:nodes:by_file:{pattern}")
    if keys:
        for k in keys:
            print(f"  FOUND: {k.decode()}")
    else:
        print(f"  ABSENT: {pattern}")

print("\nDONE")
