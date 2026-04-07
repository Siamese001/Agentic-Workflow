"""Focused wiring gap analysis — top actionable gaps only."""

# guardian: allow-direct-prompt-compilation -- audit script uses print for CLI output

import sqlite3
from pathlib import Path


def main():
    db = max(
        Path("artifacts/adg").glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime,
    )
    print(f"DB: {db.name}\n")
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # 1. SovereignPromptRenderer imported but never used
    print("=== IMPORTS SovereignPromptRenderer BUT NEVER CALLS render() ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE relation_type = 'imports' AND symbol LIKE '%SovereignPromptRenderer%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'calls' AND symbol LIKE '%render%'"
        ") AND source_file NOT LIKE 'tests/%' "
        "ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 2. AgentDispatchRegistry imported but never used
    print("\n=== IMPORTS AgentDispatchRegistry BUT NEVER DISPATCHES ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE relation_type = 'imports' AND symbol LIKE '%AgentDispatchRegistry%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'calls' AND symbol LIKE '%dispatch%'"
        ") AND source_file NOT LIKE 'tests/%' "
        "ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 3. Template files not referenced
    print("\n=== TEMPLATE FILES ON DISK NEVER REFERENCED IN CODE ===")
    template_dir = Path("agentic_core/prompt_governance/templates")
    disk_templates = set()
    if template_dir.exists():
        disk_templates = {f.name for f in template_dir.glob("*.jinja")}
    cur.execute("SELECT DISTINCT symbol FROM edges WHERE symbol LIKE '%.jinja%'")
    referenced = set()
    for r in cur.fetchall():
        name = r[0].split("/")[-1] if "/" in r[0] else r[0]
        referenced.add(name)
    unreferenced = disk_templates - referenced
    for t in sorted(unreferenced):
        print(f"  {t}")
    print(f"  Total: {len(unreferenced)} unreferenced / {len(disk_templates)} on disk")

    # 4. High-risk ops without guardrails
    print("\n=== HIGH-RISK OPS WITHOUT GUARDRAILS ===")
    high_risk = [
        "invokes_dynamic",
        "accesses_credential",
        "external_http_call",
        "invokes_importlib",
        "invokes_subprocess",
    ]
    for edge_type in high_risk:
        cur.execute(
            "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?",
            (edge_type,),
        )
        total = cur.fetchone()[0]
        if total > 0:
            cur.execute(
                "SELECT COUNT(DISTINCT source_file) FROM edges "
                "WHERE relation_type = ? AND source_file NOT IN ("
                "  SELECT DISTINCT source_file FROM edges "
                "  WHERE relation_type = 'applies_guardrail'"
                ")",
                (edge_type,),
            )
            gap = cur.fetchone()[0]
            pct = 100 * gap // max(total, 1)
            print(f"  {edge_type}: {total} files, {gap} WITHOUT guardrail ({pct}% gap)")

    # 5. Agent reasoning files that have NO prompt governance edges at all
    print("\n=== AGENT FILES WITHOUT ANY PROMPT GOVERNANCE (agentic_core only) ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE 'agentic_core/%reasoning/%Agent%' "
        "AND source_file NOT LIKE 'tests/%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type IN ('generates_prompt', 'consumes_prompt', "
        "    'instruction_injection_source', 'renders_template')"
        ") ORDER BY source_file",
    )
    agents_no_prompt = [r[0] for r in cur.fetchall()]
    for a in agents_no_prompt:
        print(f"  {a}")
    print(f"  Total: {len(agents_no_prompt)} agents without prompt edges")

    # 6. Count agents WITH vs WITHOUT prompt edges
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE source_file LIKE 'agentic_core/%reasoning/%Agent%' "
        "AND source_file NOT LIKE 'tests/%'",
    )
    total_agents = cur.fetchone()[0]
    print(f"\n  Summary: {total_agents - len(agents_no_prompt)}/{total_agents} agents have prompt edges")

    # 7. Orchestration summary
    print("\n=== ORCHESTRATION WIRING SUMMARY ===")
    orch_types = [
        "routes_to_agent",
        "orchestrates_workflow",
        "dispatches_execution_plan",
        "validates_agent_capability",
        "checks_agent_registry",
    ]
    for rt in orch_types:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (rt,))
        cnt = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?",
            (rt,),
        )
        files = cur.fetchone()[0]
        print(f"  {rt}: {cnt} edges across {files} files")

    # 8. Agent classes imported but never instantiated or called
    print("\n=== CORE AGENT CLASSES IMPORTED BUT NEVER CALLED (top 15) ===")
    cur.execute(
        "SELECT e1.source_file, e1.symbol, COUNT(*) as cnt FROM edges e1 "
        "WHERE e1.relation_type = 'imports' "
        "AND e1.symbol LIKE '%Agent' "
        "AND e1.source_file LIKE 'agentic_core/%' "
        "AND e1.source_file NOT LIKE 'tests/%' "
        "AND NOT EXISTS ("
        "  SELECT 1 FROM edges e2 "
        "  WHERE e2.source_file = e1.source_file "
        "  AND e2.relation_type IN ('calls', 'instantiates') "
        "  AND e2.symbol LIKE '%' || REPLACE(e1.symbol, '.', '%') || '%'"
        ") GROUP BY e1.source_file, e1.symbol "
        "ORDER BY cnt DESC LIMIT 15",
    )
    for src, sym, cnt in cur.fetchall():
        print(f"  {src} imports {sym}")

    # 9. Prompt governance edge coverage by category
    print("\n=== PROMPT GOVERNANCE EDGE COUNTS ===")
    prompt_edges = [
        "generates_prompt",
        "consumes_prompt",
        "renders_template",
        "instruction_injection_source",
        "d0_injection_fence",
    ]
    for pe in prompt_edges:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (pe,))
        cnt = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?",
            (pe,),
        )
        files = cur.fetchone()[0]
        if cnt > 0:
            print(f"  {pe}: {cnt} edges across {files} files")
        else:
            print(f"  {pe}: MISSING (0 edges)")

    conn.close()


if __name__ == "__main__":
    main()
