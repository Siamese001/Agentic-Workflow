"""Prompt governance detail audit — which files generate which prompt slots."""

import sqlite3
from pathlib import Path


def main():
    db = max(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    print("=== FILES GENERATING PROMPTS (by slot) ===")
    cur.execute(
        "SELECT source_file, symbol, COUNT(*) FROM edges "
        "WHERE relation_type = 'generates_prompt' "
        "GROUP BY source_file, symbol ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]} | {r[1]} | count={r[2]}")

    print("\n=== FILES WITH instruction_injection_source ===")
    cur.execute(
        "SELECT source_file, symbol, COUNT(*) FROM edges "
        "WHERE relation_type = 'instruction_injection_source' "
        "GROUP BY source_file, symbol",
    )
    for r in cur.fetchall():
        print(f"  {r[0]} | {r[1]} | count={r[2]}")

    print("\n=== CONSUMES_PROMPT FILES ===")
    cur.execute(
        "SELECT source_file, symbol, COUNT(*) FROM edges "
        "WHERE relation_type = 'consumes_prompt' "
        "GROUP BY source_file, symbol",
    )
    for r in cur.fetchall():
        print(f"  {r[0]} | {r[1]} | count={r[2]}")

    print("\n=== PROMPT_TEMPLATE_USED_BY FILES ===")
    cur.execute(
        "SELECT source_file, symbol, COUNT(*) FROM edges "
        "WHERE relation_type = 'prompt_template_used_by' "
        "GROUP BY source_file, symbol ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]} | {r[1]} | count={r[2]}")

    print("\n=== ASSEMBLY STAGE PROMPT COVERAGE ===")
    # Check which agent reasoning files have ANY prompt-related edge
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE 'apps_%/reasoning/%' "
        "AND source_file NOT LIKE '%__init__%' "
        "ORDER BY source_file",
    )
    all_agents = [r[0] for r in cur.fetchall()]

    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE 'apps_%/reasoning/%' "
        "AND relation_type IN ('generates_prompt', 'consumes_prompt', "
        "'instruction_injection_source', 'prompt_template_used_by') ",
    )
    agents_with_prompt = {r[0] for r in cur.fetchall()}

    agents_without = [a for a in all_agents if a not in agents_with_prompt]
    print(f"  Total agent reasoning files: {len(all_agents)}")
    print(f"  With prompt governance edges: {len(agents_with_prompt)}")
    print(f"  WITHOUT any prompt edges: {len(agents_without)}")

    # Check if these are shims or real agents
    print("\n=== AGENT FILES WITHOUT PROMPT EDGES (edge counts) ===")
    for af in agents_without[:30]:
        cur.execute("SELECT COUNT(*) FROM edges WHERE source_file = ?", (af,))
        total_edges = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM edges WHERE source_file = ? AND relation_type = 'calls'", (af,))
        call_edges = cur.fetchone()[0]
        print(f"  {af}: {total_edges} total edges, {call_edges} calls")

    conn.close()


if __name__ == "__main__":
    main()
