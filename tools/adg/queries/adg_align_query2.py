import sqlite3
import sys
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.adg.shared_modules.path_resolver import latest_sqlite

DB = str(latest_sqlite())
if not DB or DB == "None":
    raise FileNotFoundError("No ADG SQLite file found. Run: python tools/generate_full_adg.py")
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# --- 1. Alignment-keyword node search (PROD only, exclude L_TEST/L_UNKNOWN) ---
keywords = [
    "rlhf",
    "fine_tun",
    "finetuning",
    "finetune",
    "alignment",
    "reward",
    "sft",
    "llm",
    "language_model",
    "transformer",
    "openai",
    "anthropic",
    "claude",
    "gpt",
    "reinforcement",
    "preference",
    "proximal",
    "constitution",
    "helpfulness",
    "harmless",
    "honest",
    "dpo",
    "ppo",
    "vllm",
    "sovereign_llm",
    "heal_llm",
    "llm_gateway",
    "llm_replay",
    "llm_seam",
    "backpressure",
    "serving_profile",
    "token_budget",
    "network_egress",
    "embedder",
    "embed",
]

like_clauses = " OR ".join(
    f"LOWER(adg_name) LIKE '%{kw}%' OR LOWER(resolved_path) LIKE '%{kw}%'" for kw in keywords
)
cur.execute(f"""
    SELECT id, adg_name, layer, entity_type, resolved_path
    FROM nodes
    WHERE layer NOT IN ('L_TEST', 'L_UNKNOWN', '')
    AND ({like_clauses})
    ORDER BY layer, adg_name
""")
align_nodes = cur.fetchall()
print(f"=== PROD ALIGNMENT/LLM NODES ({len(align_nodes)}) ===")
for n in align_nodes:
    print(f"  [{n['layer']}] {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- 2. Test coverage for those nodes ---
if align_nodes:
    ids = [str(n["id"]) for n in align_nodes]
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(
        f"SELECT DISTINCT dst_id FROM edges WHERE relation_type='covers' AND dst_id IN ({placeholders})", ids
    )
    covered_ids = {str(r["dst_id"]) for r in cur.fetchall()}
    uncovered = [n for n in align_nodes if str(n["id"]) not in covered_ids]
    print(f"\n=== UNCOVERED PROD ALIGNMENT NODES ({len(uncovered)}/{len(align_nodes)}) ===")
    for n in uncovered:
        print(f"  [{n['layer']}] {n['adg_name']} | {n['resolved_path']}")

# --- 3. What RLHF/SFT/alignment concepts are completely ABSENT as node names? ---
print("\n=== CONCEPT ABSENCE CHECK (nodes with ZERO matches) ===")
absence_check = {
    "rlhf": "RLHF",
    "reward_model": "Reward Modeling",
    "fine_tun": "Fine-Tuning",
    "sft": "Supervised Fine-Tuning (SFT)",
    "dpo": "Direct Preference Optimization (DPO)",
    "ppo": "Proximal Policy Optimization (PPO)",
    "constitution": "Constitutional AI",
    "alignment": "Alignment",
    "preference": "Preference Data/Sampling",
    "harmless": "Harmlessness",
    "helpful": "Helpfulness",
    "honest": "Honesty",
    "feedback": "Human Feedback",
    "annotation": "Annotation/Labeling",
    "evaluator": "Model Evaluator",
    "critic": "Critic/Discriminator",
    "safety_filter": "Safety Filter",
    "toxicity": "Toxicity Detection",
    "bias": "Bias Detection",
    "red_team": "Red-Teaming",
}
for kw, label in absence_check.items():
    cur.execute(
        f"SELECT COUNT(*) FROM nodes WHERE layer NOT IN ('L_TEST','L_UNKNOWN','') AND (LOWER(adg_name) LIKE '%{kw}%' OR LOWER(resolved_path) LIKE '%{kw}%')"
    )
    cnt = cur.fetchone()[0]
    status = "PRESENT" if cnt > 0 else "ABSENT"
    print(f"  {status:8s} ({cnt:3d}) {label}")

# --- 4. Existing LLM infrastructure (vLLM, gateway, embedder, etc.) ---
cur.execute("""
    SELECT id, adg_name, layer, entity_type, resolved_path
    FROM nodes
    WHERE layer NOT IN ('L_TEST', 'L_UNKNOWN', '')
    AND (
        LOWER(adg_name) LIKE '%vllm%'
        OR LOWER(adg_name) LIKE '%sovereign_llm%'
        OR LOWER(adg_name) LIKE '%llm_gateway%'
        OR LOWER(adg_name) LIKE '%llm_replay%'
        OR LOWER(adg_name) LIKE '%llm_seam%'
        OR LOWER(adg_name) LIKE '%backpressure%'
        OR LOWER(adg_name) LIKE '%serving_profile%'
        OR LOWER(adg_name) LIKE '%token_budget%'
        OR LOWER(adg_name) LIKE '%network_egress%'
        OR LOWER(adg_name) LIKE '%embedder%'
        OR LOWER(adg_name) LIKE '%openai%'
    )
    ORDER BY layer, adg_name
""")
infra = cur.fetchall()
print(f"\n=== EXISTING LLM INFRASTRUCTURE NODES ({len(infra)}) ===")
for n in infra:
    print(f"  [{n['layer']}] {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- 5. Dead imports referencing LLM infra (stale/broken seams) ---
cur.execute("""
    SELECT e.src_id, e.symbol, n.adg_name, n.layer, n.resolved_path
    FROM edges e
    JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type = 'dead_imports'
    AND n.layer NOT IN ('L_TEST', 'L_UNKNOWN', '')
    AND (
        LOWER(e.symbol) LIKE '%llm%'
        OR LOWER(e.symbol) LIKE '%vllm%'
        OR LOWER(e.symbol) LIKE '%openai%'
        OR LOWER(e.symbol) LIKE '%anthropic%'
        OR LOWER(e.symbol) LIKE '%reward%'
        OR LOWER(e.symbol) LIKE '%embed%'
    )
    ORDER BY n.layer, n.adg_name
""")
dead = cur.fetchall()
print(f"\n=== PROD DEAD IMPORTS (LLM-related, {len(dead)}) ===")
for d in dead:
    print(f"  [{d['layer']}] {d['adg_name']} dead '{d['symbol']}' | {d['resolved_path']}")

# --- 6. Layer-level import fan-out for LLM infra (who depends on these?) ---
cur.execute("""
    SELECT n_src.layer as src_layer, n_dst.layer as dst_layer, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n_src ON e.src_id = n_src.id
    JOIN nodes n_dst ON e.dst_id = n_dst.id
    WHERE e.relation_type = 'imports'
    AND (
        LOWER(n_dst.adg_name) LIKE '%llm%'
        OR LOWER(n_dst.adg_name) LIKE '%vllm%'
        OR LOWER(n_dst.adg_name) LIKE '%openai%'
    )
    AND n_src.layer NOT IN ('L_TEST','L_UNKNOWN','')
    GROUP BY n_src.layer, n_dst.layer
    ORDER BY cnt DESC
""")
fanout = cur.fetchall()
print(f"\n=== LLM IMPORT FAN-OUT BY LAYER ({len(fanout)} combos) ===")
for f in fanout:
    print(f"  {f['src_layer']} -> {f['dst_layer']}: {f['cnt']} imports")

db.close()
print("\nDONE")
