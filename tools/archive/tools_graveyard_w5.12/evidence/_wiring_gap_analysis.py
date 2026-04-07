"""Analyze ADG for wiring gaps: present-but-not-wired functionality."""

import sqlite3
from pathlib import Path


def main():
    db = max(
        Path("artifacts/adg").glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime,
    )
    print(f"DB: {db.name}")
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Schema discovery
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Tables: {tables}")
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [(r[1], r[2]) for r in cur.fetchall()]
        print(f"  {t}: {cols}")

    # Edge type summary
    print("\n=== EDGE TYPE COUNTS (top 30) ===")
    cur.execute(
        "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC LIMIT 30",
    )
    for rt, cnt in cur.fetchall():
        print(f"  {rt}: {cnt}")

    # 1. Agent reasoning files with NO prompt governance edges
    print("\n=== AGENT REASONING FILES WITHOUT PROMPT EDGES ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE '%reasoning/%Agent%' "
        "AND source_file NOT LIKE 'tests/%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type IN ('generates_prompt', 'consumes_prompt', "
        "    'instruction_injection_source', 'renders_template')"
        ") ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 2. Modules importing SovereignPromptRenderer but never calling render
    print("\n=== IMPORTS SovereignPromptRenderer BUT NEVER CALLS render() ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE relation_type = 'imports' AND symbol LIKE '%SovereignPromptRenderer%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'calls' AND symbol LIKE '%render%'"
        ") ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 3. Modules importing AgentDispatchRegistry but never dispatching
    print("\n=== IMPORTS AgentDispatchRegistry BUT NEVER DISPATCHES ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE relation_type = 'imports' AND symbol LIKE '%AgentDispatchRegistry%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'calls' AND symbol LIKE '%dispatch%'"
        ") ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 4. Agent files NOT in checks_agent_registry edges
    print("\n=== AGENT FILES NOT REGISTERED (no checks_agent_registry) ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE source_file LIKE '%reasoning/%Agent%' "
        "AND source_file NOT LIKE 'tests/%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type = 'checks_agent_registry'"
        ") ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    # 5. Template files on disk vs referenced in code
    print("\n=== TEMPLATE FILES NEVER REFERENCED IN CODE ===")
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

    # 6. Lifecycle trace contract gaps
    print("\n=== MODULES WITH calls BUT NO records_execution_trace ===")
    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'calls'")
    total_callers = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'records_execution_trace'",
    )
    traced = cur.fetchone()[0]
    print(f"  Total modules with calls: {total_callers}")
    print(f"  Modules with execution trace: {traced}")
    print(f"  Gap: {total_callers - traced}")

    # 7. Guardrail coverage gaps
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
            print(
                f"  {edge_type}: {total} files, {gap} WITHOUT guardrail ({100 * gap // max(total, 1)}% gap)",
            )

    # 8. Orchestration wiring gaps
    print("\n=== ORCHESTRATION EDGES SUMMARY ===")
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

    # 9. Dead imports (import edge but symbol never used in calls)
    print("\n=== IMPORT-BUT-NEVER-CALL PATTERNS (Agent classes) ===")
    cur.execute(
        "SELECT e1.source_file, e1.symbol FROM edges e1 "
        "WHERE e1.relation_type = 'imports' "
        "AND e1.symbol LIKE '%Agent' "
        "AND e1.source_file NOT LIKE 'tests/%' "
        "AND NOT EXISTS ("
        "  SELECT 1 FROM edges e2 "
        "  WHERE e2.source_file = e1.source_file "
        "  AND e2.relation_type = 'calls' "
        "  AND e2.symbol LIKE '%' || e1.symbol || '%'"
        ") ORDER BY e1.source_file",
    )
    for src, sym in cur.fetchall():
        print(f"  {src} imports {sym} but never calls it")

    # 10. Modules with standard_heal decorator but missing heal() method pattern
    print("\n=== FILES USING @standard_heal DECORATOR ===")
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE symbol LIKE '%standard_heal%' "
        "AND source_file NOT LIKE 'tests/%' "
        "ORDER BY source_file",
    )
    for r in cur.fetchall():
        print(f"  {r[0]}")

    conn.close()


if __name__ == "__main__":
    main()
