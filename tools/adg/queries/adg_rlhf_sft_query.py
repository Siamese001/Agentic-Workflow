"""
Focused Redis hot-cache query: RLHF and SFT gaps only.
"""
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get_nodes_for_file(filepath):
    members = r.smembers(f'adg:nodes:by_file:{filepath}')
    nodes = []
    for nid in members:
        data = r.hgetall(f'adg:node:{nid.decode()}')
        if data:
            nodes.append({k.decode(): v.decode() for k, v in data.items()})
    return nodes

def node_has_covers(node_id):
    return bool(r.smembers(f'adg:edge:in:{node_id}:covers'))

def get_edge_targets(node_id, rel):
    return [m.decode() for m in r.smembers(f'adg:edge:{node_id}:{rel}')]

def node_name(nid):
    data = r.hgetall(f'adg:node:{nid}')
    if data:
        return data.get(b'adg_name', b'?').decode().replace('ADG::Module::','').replace('ADG::Symbol::','')
    return f'<{nid}>'

# Files of interest: RLHF and SFT ecosystem
TARGET_FILES = [
    # RLHF
    'system_learning/engines/rlhf_optimizer.py',
    'system_learning/engines/rlhf_optimizer_impl.py',
    # Reward model
    'system_learning/engines/governance_reward_model.py',
    # DPO
    'agentic_core/L6_observability/engines/dpo_pair_generator.py',
    'agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py',
    'agentic_core/L6_observability/types/dpo_types.py',
    'agentic_core/utils/workflow_engines/dpo_batch_builder.py',
    # Preference
    'system_learning/engines/path_d_preference_embedder.py',
    # Optimization
    'system_learning/engines/optimization_proposal_engine.py',
    # Pipeline
    'system_learning/pipelines/pipeline_factory.py',
]

print("=" * 70)
print("RLHF / SFT / DPO / REWARD MODEL — REDIS HOT CACHE QUERY")
print("=" * 70)

all_prod_nodes = []

for filepath in TARGET_FILES:
    nodes = get_nodes_for_file(filepath)
    print(f"\n[FILE] {filepath}  ({len(nodes)} nodes)")
    for n in nodes:
        nid = n.get('id', '?')
        name = n.get('adg_name', '?').replace('ADG::Module::','').replace('ADG::Symbol::','')
        layer = n.get('layer', '?')
        etype = n.get('entity_type', '?')
        covered = node_has_covers(nid)

        # Get all outbound edge types for this node
        edge_keys = r.keys(f'adg:edge:{nid}:*')
        edge_types = [k.decode().split(':')[-1] for k in edge_keys]

        # Get inbound covers
        covers_in = [m.decode() for m in r.smembers(f'adg:edge:in:{nid}:covers')]

        print(f"  [{layer}] {name} | {etype}")
        print(f"    covered: {covered} | covers_in: {len(covers_in)}")
        if edge_types:
            print(f"    outbound edges: {sorted(set(edge_types))}")

        if layer not in ('L_TEST', 'L_UNKNOWN', ''):
            all_prod_nodes.append((nid, name, layer, filepath, covered, edge_types))

# --- Summary of what RLHF pipeline edges exist ---
print("\n\n" + "=" * 70)
print("RLHF-SPECIFIC EDGE TYPES IN SNAPSHOT")
print("=" * 70)

# From the snapshot we know: builds_dpo_batch=43, produces_preference_pair=13
# Let's find which prod nodes have these
for rel in ['builds_dpo_batch', 'produces_preference_pair']:
    keys = r.keys(f'adg:edge:*:{rel}')
    print(f"\n[{rel}] ({len(keys)} source nodes total)")
    for k in keys:
        parts = k.decode().split(':')
        src_id = parts[2]
        data = r.hgetall(f'adg:node:{src_id}')
        if not data:
            continue
        layer = data.get(b'layer', b'?').decode()
        name = data.get(b'adg_name', b'?').decode().replace('ADG::Module::','')
        if layer in ('L_TEST', 'L_UNKNOWN', ''):
            continue
        dst_ids = [m.decode() for m in r.smembers(k)]
        dst_names = [node_name(d) for d in dst_ids[:4]]
        covered = node_has_covers(src_id)
        print(f"  [{layer}] {name} | covered={covered}")
        print(f"    -> {dst_names}")

# --- Check: does any RLHF/SFT loop wire back to the LLM gateway? ---
print("\n\n" + "=" * 70)
print("RLHF FEEDBACK LOOP CONNECTIVITY CHECK")
print("=" * 70)

# Find if rlhf_optimizer or dpo_batch_builder are imported by anything
for filepath in ['system_learning/engines/rlhf_optimizer.py',
                 'system_learning/engines/rlhf_optimizer_impl.py',
                 'agentic_core/utils/workflow_engines/dpo_batch_builder.py',
                 'system_learning/engines/governance_reward_model.py']:
    nodes = get_nodes_for_file(filepath)
    for n in nodes:
        nid = n.get('id')
        name = n.get('adg_name','?').replace('ADG::Module::','')
        layer = n.get('layer','?')
        if layer in ('L_TEST','L_UNKNOWN',''):
            continue
        # Who imports this node?
        importers = [m.decode() for m in r.smembers(f'adg:edge:in:{nid}:imports')]
        importer_names = []
        for imp in importers[:6]:
            d = r.hgetall(f'adg:node:{imp}')
            if d:
                importer_names.append(
                    f"[{d.get(b'layer',b'?').decode()}] {d.get(b'adg_name',b'?').decode().replace('ADG::Module::','')}",
                )
        print(f"\n{name} ({layer})")
        print(f"  imported by ({len(importers)} total): {importer_names if importer_names else 'NOBODY'}")

        # What does it import?
        imports_out = [m.decode() for m in r.smembers(f'adg:edge:{nid}:imports')]
        import_names = []
        for imp in imports_out[:6]:
            d = r.hgetall(f'adg:node:{imp}')
            if d:
                lyr = d.get(b'layer', b'?').decode()
                nm = d.get(b'adg_name', b'?').decode().replace('ADG::Module::','')
                if lyr not in ('L_UNKNOWN',):
                    import_names.append(f"[{lyr}] {nm}")
        print(f"  imports: {import_names if import_names else '(none resolved)'}")

# --- What does governance_reward_model expose? ---
print("\n\n" + "=" * 70)
print("GOVERNANCE REWARD MODEL DETAILS")
print("=" * 70)
nodes = get_nodes_for_file('system_learning/engines/governance_reward_model.py')
for n in nodes:
    nid = n.get('id')
    name = n.get('adg_name','?')
    layer = n.get('layer','?')
    etype = n.get('entity_type','?')
    print(f"  [{layer}] {name} | {etype}")
    edge_keys = r.keys(f'adg:edge:{nid}:*')
    for ek in edge_keys:
        rel = ek.decode().split(':')[-1]
        targets = [node_name(m.decode()) for m in r.smembers(ek)]
        print(f"    -{rel}: {targets[:4]}")

print("\nDONE")
