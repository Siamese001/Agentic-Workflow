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

# --- Concept absence check ONLY ---
absence_check = {
    "rlhf": "RLHF",
    "reward_model": "Reward Modeling",
    "fine_tun": "Fine-Tuning",
    " sft ": "Supervised Fine-Tuning (SFT)",
    "dpo": "Direct Preference Optimization (DPO)",
    "ppo": "Proximal Policy Optimization (PPO)",
    "constitution": "Constitutional AI",
    "alignment": "Alignment (generic)",
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
absent = []
present = []
for kw, label in absence_check.items():
    kw_clean = kw.strip()
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE layer NOT IN ('L_TEST','L_UNKNOWN','') "
        f"AND (LOWER(adg_name) LIKE '%{kw_clean}%' OR LOWER(resolved_path) LIKE '%{kw_clean}%')"
    )
    cnt = cur.fetchone()[0]
    if cnt == 0:
        absent.append(label)
        print(f"  ABSENT   ({cnt:3d}) {label}")
    else:
        present.append((label, cnt))
        print(f"  PRESENT  ({cnt:3d}) {label}")

print(f"\nSUMMARY: {len(absent)} absent, {len(present)} present out of {len(absence_check)} concepts")
print("\nABSENT concepts:")
for a in absent:
    print(f"  - {a}")

# --- L1 cognition nodes with LLM ---
print("\n=== L1 (COGNITION) ALL NODES ===")
cur.execute("SELECT adg_name, entity_type, resolved_path FROM nodes WHERE layer='L1' ORDER BY adg_name")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- L5 safety nodes with LLM/alignment terms ---
print("\n=== L5 (SAFETY) LLM/ALIGNMENT NODES ===")
cur.execute("""
    SELECT adg_name, entity_type, resolved_path FROM nodes
    WHERE layer='L5'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%align%'
         OR LOWER(adg_name) LIKE '%heal%' OR LOWER(adg_name) LIKE '%seam%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- L_SL preference/reward/feedback ---
print("\n=== L_SL (SYSTEM LEARNING) PREFERENCE/REWARD/FEEDBACK NODES ===")
cur.execute("""
    SELECT adg_name, entity_type, resolved_path FROM nodes
    WHERE layer='L_SL'
    AND (LOWER(adg_name) LIKE '%preference%' OR LOWER(adg_name) LIKE '%reward%'
         OR LOWER(adg_name) LIKE '%feedback%' OR LOWER(adg_name) LIKE '%embed%'
         OR LOWER(adg_name) LIKE '%openai%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- L2 LLM-related modules specifically ---
print("\n=== L2 (EXECUTION) LLM/VLLM MODULES ===")
cur.execute("""
    SELECT adg_name, entity_type, resolved_path FROM nodes
    WHERE layer='L2' AND entity_type='module'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- DDDAlignmentAgent specifically ---
print("\n=== DDDAlignmentAgent (interesting name!) ===")
cur.execute("SELECT * FROM nodes WHERE adg_name LIKE '%DDDAlignment%' OR adg_name LIKE '%Alignment%'")
for n in cur.fetchall():
    print(
        f"  [{dict(n)['layer']}] {dict(n)['adg_name']} | {dict(n)['entity_type']} | {dict(n)['resolved_path']}"
    )

db.close()
print("\nDONE")
