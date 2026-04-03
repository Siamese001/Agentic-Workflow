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

absence_check = {
    "rlhf": "RLHF",
    "reward_model": "Reward Modeling",
    "fine_tun": "Fine-Tuning",
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

absent = []
present = []
for kw, label in absence_check.items():
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE layer NOT IN ('L_TEST','L_UNKNOWN','') "
        "AND (LOWER(adg_name) LIKE ? OR LOWER(resolved_path) LIKE ?)",
        (f"%{kw}%", f"%{kw}%"),
    )
    cnt = cur.fetchone()[0]
    if cnt == 0:
        absent.append(label)
    else:
        present.append((label, cnt))

print("=== CONCEPT ABSENCE CHECK ===")
print("ABSENT:")
for a in absent:
    print(f"  - {a}")
print("PRESENT:")
for p, cnt in present:
    print(f"  + ({cnt}) {p}")

# --- L1 cognition layer ALL modules ---
print("\n=== L1 COGNITION MODULES ===")
cur.execute(
    "SELECT adg_name, resolved_path FROM nodes WHERE layer='L1' AND entity_type='module' ORDER BY adg_name"
)
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- L5 safety MODULES ---
print("\n=== L5 SAFETY MODULES (LLM/align) ===")
cur.execute("""
    SELECT adg_name, resolved_path FROM nodes
    WHERE layer='L5' AND entity_type='module'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%align%'
         OR LOWER(adg_name) LIKE '%heal%' OR LOWER(adg_name) LIKE '%seam%'
         OR LOWER(adg_name) LIKE '%guard%' OR LOWER(adg_name) LIKE '%sovereign%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- L_SL MODULES with preference/embed/feedback ---
print("\n=== L_SL MODULES (preference/reward/embed/feedback) ===")
cur.execute("""
    SELECT adg_name, resolved_path FROM nodes
    WHERE layer='L_SL' AND entity_type='module'
    AND (LOWER(adg_name) LIKE '%preference%' OR LOWER(adg_name) LIKE '%reward%'
         OR LOWER(adg_name) LIKE '%feedback%' OR LOWER(adg_name) LIKE '%embed%'
         OR LOWER(adg_name) LIKE '%openai%' OR LOWER(adg_name) LIKE '%arbitrat%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- L2 LLM/vLLM MODULES ---
print("\n=== L2 EXECUTION LLM/vLLM MODULES ===")
cur.execute("""
    SELECT adg_name, resolved_path FROM nodes
    WHERE layer='L2' AND entity_type='module'
    AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- DDDAlignmentAgent details ---
print("\n=== DDDAlignmentAgent details ===")
cur.execute("""
    SELECT layer, adg_name, entity_type, resolved_path FROM nodes
    WHERE adg_name LIKE '%DDDAlign%' OR adg_name LIKE '%ddd_align%'
    ORDER BY layer, adg_name
""")
for n in cur.fetchall():
    print(f"  [{n['layer']}] {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

# --- alignment-adjacent L0 routing modules ---
print("\n=== L0 ROUTING ALIGNMENT-ADJACENT MODULES ===")
cur.execute("""
    SELECT adg_name, resolved_path FROM nodes
    WHERE layer='L0' AND entity_type='module'
    AND (LOWER(adg_name) LIKE '%align%' OR LOWER(adg_name) LIKE '%policy%'
         OR LOWER(adg_name) LIKE '%sovereign%')
    ORDER BY adg_name
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

# --- L_PG prompt governance modules ---
print("\n=== L_PG PROMPT GOVERNANCE MODULES ===")
cur.execute("""
    SELECT adg_name, resolved_path FROM nodes
    WHERE layer='L_PG' AND entity_type='module'
    ORDER BY adg_name LIMIT 30
""")
for n in cur.fetchall():
    print(f"  {n['adg_name']} | {n['resolved_path']}")

db.close()
print("\nDONE")
