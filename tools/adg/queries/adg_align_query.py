# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
import sys
from pathlib import Path
from typing import Iterable

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from tools.adg.shared_modules.path_resolver import latest_sqlite


def open_db() -> sqlite3.Connection:
    db_path = latest_sqlite()
    if db_path is None:
        raise FileNotFoundError("No ADG SQLite file found. Run: python tools/generate/generate_full_adg.py")
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def build_like_clause(columns: tuple[str, ...], keywords: Iterable[str]) -> tuple[str, list[str]]:
    clauses: list[str] = []
    params: list[str] = []
    for kw in keywords:
        pattern = f"%{kw.lower()}%"
        for column in columns:
            clauses.append(f"LOWER({column}) LIKE ?")
            params.append(pattern)
    return " OR ".join(clauses), params


def main() -> None:
    with open_db() as db:
        cur = db.cursor()

        # Show tables + schema
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print("TABLES:", tables)

        cur.execute("PRAGMA table_info(nodes)")
        print("NODE COLS:", [c[1] for c in cur.fetchall()])

        cur.execute("PRAGMA table_info(edges)")
        print("EDGE COLS:", [c[1] for c in cur.fetchall()])

        # --- 1. Search nodes for LLM/alignment-related terms ---
        keywords = [
            "rlhf",
            "fine_tun",
            "finetuning",
            "finetune",
            "alignment",
            "reward",
            "supervised",
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
            "policy",
            "proximal",
            "constitution",
            "helpfulness",
            "harmless",
            "honest",
            "dpo",
            "ppo",
        ]

        where_clause, where_params = build_like_clause(("adg_name", "resolved_path"), keywords)
        cur.execute(
            f"SELECT id, adg_name, layer, entity_type, resolved_path FROM nodes WHERE {where_clause}",
            where_params,
        )
        align_nodes = cur.fetchall()
        print(f"\n=== ALIGNMENT-RELATED NODES ({len(align_nodes)}) ===")
        for n in align_nodes:
            print(f"  [{n['layer']}] {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

        # --- 2. Check test coverage for those nodes ---
        if align_nodes:
            ids = [str(n["id"]) for n in align_nodes]
            placeholders = ",".join("?" * len(ids))
            cur.execute(
                f"SELECT DISTINCT src_id, dst_id FROM edges WHERE relation_type='covers' AND dst_id IN ({placeholders})",
                ids,
            )
            covered = {str(r["dst_id"]) for r in cur.fetchall()}
            uncovered = [n for n in align_nodes if str(n["id"]) not in covered]
            print(f"\n=== UNCOVERED ALIGNMENT NODES ({len(uncovered)}/{len(align_nodes)}) ===")
            for n in uncovered:
                print(f"  [{n['layer']}] {n['adg_name']} | {n['resolved_path']}")

        # --- 3. Broader architectural scan: L1_cognition engines that invoke LLM APIs ---
        cur.execute("""
            SELECT n.id, n.adg_name, n.layer, n.entity_type, n.resolved_path
            FROM nodes n
            WHERE n.layer IN ('L1', 'L2', 'L3', 'L_APP')
            AND (
                LOWER(n.adg_name) LIKE '%prompt%'
                OR LOWER(n.adg_name) LIKE '%completion%'
                OR LOWER(n.adg_name) LIKE '%chat%'
                OR LOWER(n.adg_name) LIKE '%model%'
                OR LOWER(n.adg_name) LIKE '%inference%'
                OR LOWER(n.adg_name) LIKE '%generate%'
                OR LOWER(n.adg_name) LIKE '%embed%'
            )
            ORDER BY n.layer, n.adg_name
            LIMIT 80
        """)
        llm_adjacent = cur.fetchall()
        print(f"\n=== LLM-ADJACENT NODES BY LAYER ({len(llm_adjacent)}) ===")
        for n in llm_adjacent:
            print(f"  [{n['layer']}] {n['adg_name']} | {n['entity_type']} | {n['resolved_path']}")

        # --- 4. Check dead_imports signal for alignment-adjacent paths ---
        cur.execute("""
            SELECT e.src_id, e.symbol, n.adg_name, n.layer, n.resolved_path
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'dead_imports'
            AND (
                LOWER(e.symbol) LIKE '%openai%'
                OR LOWER(e.symbol) LIKE '%anthropic%'
                OR LOWER(e.symbol) LIKE '%reward%'
                OR LOWER(e.symbol) LIKE '%alignment%'
                OR LOWER(e.symbol) LIKE '%llm%'
                OR LOWER(e.symbol) LIKE '%fine_tun%'
            )
            LIMIT 40
        """)
        dead = cur.fetchall()
        print(f"\n=== DEAD IMPORTS w/ ALIGNMENT SYMBOLS ({len(dead)}) ===")
        for d in dead:
            print(f"  [{d['layer']}] {d['adg_name']} dead-imports '{d['symbol']}' | {d['resolved_path']}")

        # --- 5. Layer distribution of all nodes to see where alignment fits ---
        cur.execute(
            "SELECT layer, COUNT(*) as cnt FROM nodes WHERE layer NOT LIKE 'L_TEST%' GROUP BY layer ORDER BY cnt DESC",
        )
        dist = cur.fetchall()
        print("\n=== PROD LAYER DISTRIBUTION ===")
        for row in dist:
            print(f"  {row['layer']}: {row['cnt']}")

        print("\nDONE")


if __name__ == "__main__":
    main()
