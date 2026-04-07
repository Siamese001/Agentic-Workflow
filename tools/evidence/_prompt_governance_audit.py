"""Prompt governance & injection coverage audit against ADG SQLite."""
# guardian: allow-direct-prompt-compilation -- audit tool uses SQL queries against ADG for prompt governance analysis

import sqlite3
from pathlib import Path


def main():
    db = max(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
    print(f"DB: {db.name}")
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # 1. Prompt governance edge counts
    print("\n=== PROMPT GOVERNANCE EDGES ===")
    prompt_edges = [
        "generates_prompt",
        "consumes_prompt",
        "assembles_into",
        "injects_into",
        "overrides_prompt",
        "prompt_template_used_by",
        "instruction_injection_source",
        "validated_by_llm_gateway",
        "validated_by_safety_plane",
        "applies_guardrail",
        "validated_by_registry",
    ]
    for e in prompt_edges:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (e,))
        c = cur.fetchone()[0]
        if c > 0:
            print(f"  {e}: {c}")

    # 2. High-risk edges without guardrails
    print("\n=== HIGH-RISK OPS (no guardrail in same file) ===")
    high_risk = [
        "accesses_credential",
        "external_http_call",
        "reads_secret",
        "invokes_eval",
        "invokes_importlib",
        "invokes_dynamic",
        "invokes_getattr_dynamic",
    ]
    for e in high_risk:
        cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?", (e,))
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(DISTINCT e1.source_file) FROM edges e1 "
            "WHERE e1.relation_type = ? AND e1.source_file NOT IN ("
            "  SELECT DISTINCT source_file FROM edges WHERE relation_type = 'applies_guardrail'"
            ")",
            (e,),
        )
        gap = cur.fetchone()[0]
        if total > 0:
            print(f"  {e}: {total} files, {gap} WITHOUT guardrail ({100 * gap / total:.0f}% gap)")

    # 3. Prompt slot coverage
    print("\n=== PROMPT SLOT GENERATION (generates_prompt by symbol) ===")
    cur.execute(
        "SELECT symbol, COUNT(*) FROM edges WHERE relation_type = 'generates_prompt' "
        "GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 20",
    )
    for sym, cnt in cur.fetchall():
        print(f"  {sym}: {cnt}")

    # 4. D0 injection fence coverage
    print("\n=== D0 INJECTION FENCE ANALYSIS ===")
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type = 'generates_prompt' AND symbol LIKE '%D0%'",
    )
    d0_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'generates_prompt'")
    total_gen = cur.fetchone()[0]
    print(f"  Files generating prompts: {total_gen}")
    # guardian: allow-direct-prompt-compilation -- CLI output reporting D0 fence audit metrics
    print(f"  Files with D0 fences: {d0_count}")
    if total_gen > 0:
        # guardian: allow-direct-prompt-compilation -- CLI output reporting D0 coverage percentage
        print(f"  D0 coverage: {100 * d0_count / total_gen:.1f}%")

    # 5. Orphan prompt consumers
    print("\n=== PROMPT CONSUMERS WITHOUT GENERATORS ===")
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type = 'consumes_prompt' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges WHERE relation_type = 'generates_prompt'"
        ")",
    )
    orphan = cur.fetchone()[0]
    print(f"  Orphan consumers (consume but dont generate): {orphan}")

    # 6. All injection-related edge types
    print("\n=== ALL INJECTION-RELATED EDGE TYPES ===")
    cur.execute(
        "SELECT relation_type, COUNT(*) FROM edges "
        "WHERE relation_type LIKE '%inject%' OR relation_type LIKE '%injection%' "
        "GROUP BY relation_type ORDER BY COUNT(*) DESC",
    )
    for rt, cnt in cur.fetchall():
        print(f"  {rt}: {cnt}")

    # 7. Agent reasoning classification audit
    print("\n=== AGENT FILES BY REASONING TIER (from agent_registry) ===")
    # Check which agents are in registry
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE 'apps_lic/reasoning/%' OR source_file LIKE 'apps_rg/reasoning/%' "
        "OR source_file LIKE 'apps_shared/reasoning/%' "
        "ORDER BY source_file",
    )
    agent_files = [r[0] for r in cur.fetchall()]
    print(f"  Total agent reasoning files in ADG: {len(agent_files)}")

    # Check which have consumes_prompt or generates_prompt edges
    for af in agent_files:
        cur.execute(
            "SELECT relation_type, COUNT(*) FROM edges "
            "WHERE source_file = ? AND relation_type IN ('generates_prompt', 'consumes_prompt', "
            "'instruction_injection_source', 'prompt_template_used_by') "
            "GROUP BY relation_type",
            (af,),
        )
        edges = cur.fetchall()
        if not edges:
            print(f"  NO PROMPT EDGES: {af}")

    # 8. Relation types containing 'prompt'
    print("\n=== ALL 'PROMPT' RELATION TYPES ===")
    cur.execute(
        "SELECT relation_type, COUNT(*) FROM edges "
        "WHERE relation_type LIKE '%prompt%' "
        "GROUP BY relation_type ORDER BY COUNT(*) DESC",
    )
    for rt, cnt in cur.fetchall():
        print(f"  {rt}: {cnt}")

    # 9. Modules with generates_prompt but NO i0_instructional slot
    print("\n=== MODULES GENERATING PROMPTS WITHOUT I0 INSTRUCTIONAL ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE relation_type = 'generates_prompt' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'generates_prompt' AND symbol LIKE '%I0%'"
        ") ORDER BY source_file",
    )
    no_i0 = cur.fetchall()
    print(f"  Count: {len(no_i0)}")
    for r in no_i0[:20]:
        print(f"    {r[0]}")

    conn.close()


if __name__ == "__main__":
    main()
