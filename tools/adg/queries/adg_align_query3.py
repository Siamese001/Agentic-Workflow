import sqlite3
import sys
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.adg.shared_modules.path_resolver import latest_sqlite

DB = latest_sqlite()
if DB is None:
    raise FileNotFoundError("No ADG SQLite file found. Run: python tools/generate_full_adg.py")
DB = str(DB)
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# --- Concept absence check ---
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
    "harmless": "Harmlessness constraint",
    "helpful": "Helpfulness constraint",
    "honest": "Honesty constraint",
    "feedback": "Human Feedback",
    "annotation": "Annotation/Labeling",
    "evaluator": "Model Evaluator",
    "critic": "Critic/Discriminator",
    "safety_filter": "Safety Filter",
    "toxicity": "Toxicity Detection",
    "bias_detect": "Bias Detection",
    "red_team": "Red-Teaming",
    "grounding": "Grounding/Factuality",
    "hallucin": "Hallucination Detection",
    "calibrat": "Calibration",
    "uncertainty": "Uncertainty Estimation",
    "refusal": "Refusal Policy",
    "guardrail": "Guardrails",
    "moderation": "Content Moderation",
    "jailbreak": "Jailbreak Prevention",
    "prompt_inject": "Prompt Injection Defense",
}

print("=== CONCEPT ABSENCE CHECK (PROD nodes only) ===")
for kw, label in absence_check.items():
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE layer NOT IN ('L_TEST','L_UNKNOWN','') "
        f"AND (LOWER(adg_name) LIKE '%{kw}%' OR LOWER(resolved_path) LIKE '%{kw}%')",
    )
    cnt = cur.fetchone()[0]
    status = "PRESENT" if cnt > 0 else "ABSENT "
    print(f"  {status} ({cnt:3d}) {label}")

# --- Prod alignment nodes full list ---
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
    "openai",
    "anthropic",
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
]
like_clauses = " OR ".join(
    f"LOWER(adg_name) LIKE '%{kw}%' OR LOWER(resolved_path) LIKE '%{kw}%'" for kw in keywords
)
cur.execute(f"""
    SELECT id, adg_name, layer, entity_type, resolved_path
    FROM nodes
    WHERE layer NOT IN ('L_TEST', 'L_UNKNOWN', '')
    AND ({like_clauses})
    AND entity_type IN ('module','symbol')
    ORDER BY layer, adg_name
""")
align_nodes = cur.fetchall()

ids = [str(n["id"]) for n in align_nodes]
placeholders = ",".join(["?"] * len(ids))
cur.execute(
    f"SELECT DISTINCT dst_id FROM edges WHERE relation_type='covers' AND dst_id IN ({placeholders})",
    ids,
)
covered_ids = {str(r["dst_id"]) for r in cur.fetchall()}
uncovered = [n for n in align_nodes if str(n["id"]) not in covered_ids]

print(f"\n=== PROD LLM/ALIGNMENT NODES: {len(align_nodes)} total, {len(uncovered)} uncovered ===")
print("\n-- BY LAYER BREAKDOWN --")
from collections import Counter

layer_counts = Counter(n["layer"] for n in align_nodes)
layer_uncov = Counter(n["layer"] for n in uncovered)
for layer, cnt in sorted(layer_counts.items()):
    print(f"  {layer}: {cnt} total, {layer_uncov.get(layer, 0)} uncovered")

print("\n-- UNCOVERED MODULES (not symbols) --")
for n in uncovered:
    if "module" in n["entity_type"].lower() or "Module" in n["adg_name"]:
        print(f"  [{n['layer']}] {n['adg_name']} | {n['resolved_path']}")

# --- What layers HAVE alignment/LLM infra? ---
print("\n=== L1 (COGNITION) LLM NODES ===")
cur.execute("""
    SELECT id, adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer='L1'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%' OR LOWER(resolved_path) LIKE '%llm%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

print("\n=== L2 (EXECUTION) LLM NODES ===")
cur.execute("""
    SELECT id, adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer='L2'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%' OR LOWER(resolved_path) LIKE '%llm%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

print("\n=== L5 (SAFETY) LLM NODES ===")
cur.execute("""
    SELECT id, adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer='L5'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%' OR LOWER(resolved_path) LIKE '%llm%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

print("\n=== L_SL (SYSTEM LEARNING) ALIGNMENT-ADJACENT ===")
cur.execute("""
    SELECT id, adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer='L_SL'
    AND (
        LOWER(adg_name) LIKE '%preference%'
        OR LOWER(adg_name) LIKE '%reward%'
        OR LOWER(adg_name) LIKE '%embed%'
        OR LOWER(adg_name) LIKE '%openai%'
        OR LOWER(adg_name) LIKE '%feedback%'
    )
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- Dead import seam breaks ---
print("\n=== PROD DEAD IMPORTS (LLM-related) ===")
cur.execute("""
    SELECT e.symbol, n.adg_name, n.layer, n.resolved_path
    FROM edges e
    JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type = 'dead_imports'
    AND n.layer NOT IN ('L_TEST', 'L_UNKNOWN', '')
    AND (
        LOWER(e.symbol) LIKE '%llm%'
        OR LOWER(e.symbol) LIKE '%vllm%'
        OR LOWER(e.symbol) LIKE '%openai%'
        OR LOWER(e.symbol) LIKE '%embed%'
        OR LOWER(e.symbol) LIKE '%sovereign%'
    )
    ORDER BY n.layer, n.adg_name
""")
for d in cur.fetchall():
    print(f"  [{d['layer']}] {d['adg_name']} -> dead: '{d['symbol']}' | {d['resolved_path']}")

db.close()
print("\nDONE")
