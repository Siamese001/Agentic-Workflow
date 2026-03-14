"""
Query Redis hot cache directly for LLM alignment gap analysis.
Uses adg:node:* HASH keys and adg:edge:* SET keys exclusively.
"""
import redis
from collections import defaultdict, Counter

r = redis.Redis(host='localhost', port=6379, db=0)

# --- 1. Concept keyword scan over all nodes via Redis SCAN ---
alignment_kws = [
    'rlhf', 'fine_tun', 'finetuning', 'finetune', 'reward',
    'sft', 'llm', 'vllm', 'openai', 'anthropic', 'reinforcement',
    'preference', 'proximal', 'constitution', 'dpo', 'ppo',
    'sovereign_llm', 'heal_llm', 'llm_gateway', 'llm_replay',
    'llm_seam', 'backpressure', 'serving_profile', 'token_budget',
    'network_egress', 'embedder', 'alignment',
]

matches = []
cursor = 0
scanned = 0
while True:
    cursor, keys = r.scan(cursor, match='adg:node:*', count=1000)
    scanned += len(keys)
    pipe = r.pipeline(transaction=False)
    for k in keys:
        pipe.hgetall(k)
    results = pipe.execute()
    for data in results:
        if not data:
            continue
        layer = data.get(b'layer', b'').decode()
        if layer in ('L_TEST', 'L_UNKNOWN', ''):
            continue
        name = data.get(b'adg_name', b'').decode().lower()
        path = data.get(b'resolved_path', b'').decode().lower()
        for kw in alignment_kws:
            if kw in name or kw in path:
                matches.append({
                    'id': data.get(b'id', b'').decode(),
                    'name': data.get(b'adg_name', b'').decode(),
                    'layer': layer,
                    'entity_type': data.get(b'entity_type', b'').decode(),
                    'path': data.get(b'resolved_path', b'').decode(),
                    'matched_kw': kw,
                })
                break
    if cursor == 0:
        break

print(f"Scanned {scanned} node keys, found {len(matches)} prod alignment/LLM matches")

# --- 2. Coverage check: which matched nodes have 'covers' edges pointing to them? ---
# adg:edge:in:<dst_id>:covers is a SET of src_ids (tests that cover this node)
covered_ids = set()
uncovered = []
pipe = r.pipeline(transaction=False)
for m in matches:
    pipe.scard(f"adg:edge:in:{m['id']}:covers")
results = pipe.execute()
for m, cnt in zip(matches, results):
    if cnt and cnt > 0:
        covered_ids.add(m['id'])
    else:
        uncovered.append(m)

print(f"Covered: {len(covered_ids)}, Uncovered: {len(uncovered)}")

# --- 3. Layer breakdown ---
layer_total = Counter(m['layer'] for m in matches)
layer_uncov = Counter(m['layer'] for m in uncovered)
print("\n=== LAYER BREAKDOWN ===")
for layer in sorted(layer_total):
    print(f"  {layer}: {layer_total[layer]} total, {layer_uncov.get(layer,0)} uncovered")

# --- 4. Concept-level presence check via Redis ---
concept_checks = [
    ('rlhf',           'RLHF'),
    ('reward_model',   'Reward Modeling'),
    ('fine_tun',       'Fine-Tuning / SFT'),
    ('dpo',            'DPO'),
    ('ppo',            'PPO'),
    ('constitution',   'Constitutional AI'),
    ('alignment',      'Alignment'),
    ('preference',     'Preference Data'),
    ('harmless',       'Harmlessness'),
    ('helpful',        'Helpfulness'),
    ('honest',         'Honesty'),
    ('feedback',       'Human Feedback'),
    ('annotation',     'Annotation/Labeling'),
    ('evaluator',      'Model Evaluator'),
    ('critic',         'Critic/Discriminator'),
    ('safety_filter',  'Safety Filter'),
    ('toxicity',       'Toxicity Detection'),
    ('red_team',       'Red-Teaming'),
    ('grounding',      'Grounding/Factuality'),
    ('hallucin',       'Hallucination Detection'),
    ('calibrat',       'Calibration'),
    ('uncertainty',    'Uncertainty Estimation'),
    ('refusal',        'Refusal Policy'),
    ('guardrail',      'Guardrails'),
    ('moderation',     'Content Moderation'),
    ('jailbreak',      'Jailbreak Prevention'),
    ('prompt_inject',  'Prompt Injection Defense'),
]

# Count from already-scanned matches (prod only)
concept_counts = defaultdict(int)
# Re-scan all prod nodes for concept keywords (some may not match alignment_kws above)
cursor = 0
all_prod_names = []
while True:
    cursor, keys = r.scan(cursor, match='adg:node:*', count=1000)
    pipe = r.pipeline(transaction=False)
    for k in keys:
        pipe.hgetall(k)
    results = pipe.execute()
    for data in results:
        if not data:
            continue
        layer = data.get(b'layer', b'').decode()
        if layer in ('L_TEST', 'L_UNKNOWN', ''):
            continue
        name = data.get(b'adg_name', b'').decode().lower()
        path = data.get(b'resolved_path', b'').decode().lower()
        all_prod_names.append((name, path))
    if cursor == 0:
        break

print(f"\nTotal prod nodes scanned for concept check: {len(all_prod_names)}")
print("\n=== CONCEPT PRESENCE (PROD only, Redis hot cache) ===")
absent = []
present = []
for kw, label in concept_checks:
    cnt = sum(1 for n, p in all_prod_names if kw in n or kw in p)
    if cnt == 0:
        absent.append(label)
    else:
        present.append((label, cnt))

print("ABSENT:")
for a in absent:
    print(f"  - {a}")
print("PRESENT:")
for p, cnt in present:
    print(f"  + ({cnt:3d})  {p}")

# --- 5. Key LLM infrastructure nodes (modules only) ---
print("\n=== KEY LLM INFRA MODULES BY LAYER ===")
llm_infra_kws = ['llm', 'vllm', 'sovereign_llm', 'llm_gateway', 'llm_replay',
                 'llm_seam', 'backpressure', 'serving_profile', 'token_budget',
                 'network_egress', 'openai', 'embedder']
for m in sorted(matches, key=lambda x: (x['layer'], x['name'])):
    if m['entity_type'] == 'module':
        for kw in llm_infra_kws:
            if kw in m['name'].lower() or kw in m['path'].lower():
                cov = 'COV' if m['id'] in covered_ids else 'UNCOV'
                print(f"  [{m['layer']}] [{cov}] {m['name']} | {m['path']}")
                break

# --- 6. Dead imports for LLM-related paths from adg:violations ---
print("\n=== ADG VIOLATIONS (from adg:violations LIST) ===")
vcount = r.llen('adg:violations')
print(f"  Total violations in list: {vcount}")
if vcount > 0:
    import json
    samples = r.lrange('adg:violations', 0, 19)
    llm_viols = []
    for v in samples:
        try:
            vd = json.loads(v.decode())
            sym = str(vd).lower()
            if any(k in sym for k in ['llm', 'vllm', 'openai', 'embed', 'sovereign']):
                llm_viols.append(vd)
        except Exception:
            pass
    print(f"  LLM-related in first 20: {len(llm_viols)}")
    for v in llm_viols:
        print(f"    {v}")

# --- 7. Drift state ---
print("\n=== ADG DRIFT STATE (from Redis) ===")
score = r.get('adg:drift:score')
print(f"  Composite drift score: {score.decode() if score else 'NOT SET (TTL expired?)'}")

uncov_count = r.llen('adg:drift:uncovered')
orphan_count = r.llen('adg:drift:orphan_tests')
print(f"  Uncovered prod modules: {uncov_count}")
print(f"  Orphan tests: {orphan_count}")

# Check if any of our alignment matches are in the uncovered drift list
if uncov_count > 0:
    all_uncov = [x.decode() for x in r.lrange('adg:drift:uncovered', 0, -1)]
    align_uncov_drift = [u for u in all_uncov if any(k in u.lower() for k in ['llm', 'vllm', 'align', 'prefer', 'embed', 'openai', 'guardrail'])]
    print(f"  Alignment-related in drift uncovered list: {len(align_uncov_drift)}")
    for u in align_uncov_drift[:20]:
        print(f"    {u}")

print("\nDONE")
