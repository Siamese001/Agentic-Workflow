import sqlite3
import sys
from pathlib import Path

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from tools.adg.shared_modules.path_resolver import latest_sqlite
from tqdm import tqdm


def open_db() -> sqlite3.Connection:
    db_path = latest_sqlite()
    if db_path is None:
        raise FileNotFoundError("No ADG SQLite file found. Run: python tools/generate_full_adg.py")
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def main() -> None:
    with open_db() as db:
        cur = db.cursor()

        absence_check = [
            ("rlhf", "RLHF"),
            ("reward_model", "Reward Modeling"),
            ("fine_tun", "Fine-Tuning"),
            ("dpo", "Direct Preference Optimization"),
            ("ppo", "Proximal Policy Optimization"),
            ("constitution", "Constitutional AI"),
            ("alignment", "Alignment"),
            ("preference", "Preference Data"),
            ("harmless", "Harmlessness"),
            ("helpful", "Helpfulness"),
            ("honest", "Honesty"),
            ("feedback", "Human Feedback"),
            ("annotation", "Annotation/Labeling"),
            ("evaluator", "Model Evaluator"),
            ("critic", "Critic/Discriminator"),
            ("safety_filter", "Safety Filter"),
            ("toxicity", "Toxicity Detection"),
            ("red_team", "Red-Teaming"),
            ("grounding", "Grounding/Factuality"),
            ("hallucin", "Hallucination Detection"),
            ("calibrat", "Calibration"),
            ("uncertainty", "Uncertainty Estimation"),
            ("refusal", "Refusal Policy"),
            ("guardrail", "Guardrails"),
            ("moderation", "Content Moderation"),
            ("jailbreak", "Jailbreak Prevention"),
            ("prompt_inject", "Prompt Injection Defense"),
        ]

        absent_list = []
        present_list = []
        for kw, label in tqdm(absence_check, desc="Processing", unit="item"):
            cur.execute(
                "SELECT COUNT(*) FROM nodes WHERE layer NOT IN ('L_TEST','L_UNKNOWN','')"
                " AND (LOWER(adg_name) LIKE ? OR LOWER(resolved_path) LIKE ?)",
                (f"%{kw}%", f"%{kw}%"),
            )
            cnt = cur.fetchone()[0]
            if cnt == 0:
                absent_list.append(label)
            else:
                present_list.append((label, cnt))

        print("ABSENT:")
        for a in absent_list:
            print(f"  - {a}")
        print("PRESENT:")
        for p, cnt in present_list:
            print(f"  + ({cnt:3d})  {p}")

        # L1 cognition modules
        print("\n=== L1 MODULES ===")
        cur.execute(
            "SELECT adg_name, resolved_path FROM nodes WHERE layer='L1' AND entity_type='module' ORDER BY adg_name",
        )
        rows = cur.fetchall()
        for n in rows:
            name = n["adg_name"].replace("ADG::Module::", "")
            print(f"  {name}")

        # L2 LLM modules
        print("\n=== L2 LLM MODULES ===")
        cur.execute(
            "SELECT adg_name, resolved_path FROM nodes WHERE layer='L2' AND entity_type='module' "
            "AND (LOWER(adg_name) LIKE '%llm%' OR LOWER(adg_name) LIKE '%vllm%') ORDER BY adg_name",
        )
        for n in cur.fetchall():
            print(f"  {n['adg_name'].replace('ADG::Module::', '')} | {n['resolved_path']}")

        # L5 alignment modules
        print("\n=== L5 ALIGN/LLM/HEAL MODULES ===")
        cur.execute(
            "SELECT adg_name, resolved_path FROM nodes WHERE layer='L5' AND entity_type='module' "
            "AND (LOWER(adg_name) LIKE '%align%' OR LOWER(adg_name) LIKE '%llm%' "
            "OR LOWER(adg_name) LIKE '%heal%' OR LOWER(adg_name) LIKE '%guard%') ORDER BY adg_name",
        )
        for n in cur.fetchall():
            print(f"  {n['adg_name'].replace('ADG::Module::', '')} | {n['resolved_path']}")

        # L_SL modules with preference/embed/feedback
        print("\n=== L_SL PREFERENCE/EMBED/FEEDBACK MODULES ===")
        cur.execute(
            "SELECT adg_name, resolved_path FROM nodes WHERE layer='L_SL' AND entity_type='module' "
            "AND (LOWER(adg_name) LIKE '%preference%' OR LOWER(adg_name) LIKE '%reward%' "
            "OR LOWER(adg_name) LIKE '%feedback%' OR LOWER(adg_name) LIKE '%embed%' "
            "OR LOWER(adg_name) LIKE '%openai%' OR LOWER(adg_name) LIKE '%arbitrat%' "
            "OR LOWER(adg_name) LIKE '%confidence%') ORDER BY adg_name",
        )
        for n in cur.fetchall():
            print(f"  {n['adg_name'].replace('ADG::Module::', '')} | {n['resolved_path']}")

        # Dead LLM seams prod only
        print("\n=== PROD DEAD LLM SEAMS ===")
        cur.execute("""
            SELECT e.symbol, n.adg_name, n.layer, n.resolved_path
            FROM edges e JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'dead_imports'
            AND n.layer NOT IN ('L_TEST','L_UNKNOWN','')
            AND (LOWER(e.symbol) LIKE '%llm%' OR LOWER(e.symbol) LIKE '%vllm%'
                 OR LOWER(e.symbol) LIKE '%openai%' OR LOWER(e.symbol) LIKE '%embed%')
            ORDER BY n.layer
        """)
        for d in cur.fetchall():
            print(f"  [{d['layer']}] dead '{d['symbol']}' in {d['resolved_path']}")

        print("\nDONE")


if __name__ == "__main__":
    main()
