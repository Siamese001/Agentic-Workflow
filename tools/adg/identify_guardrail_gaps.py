"""Identify files with high-risk operations but no guardrail coverage."""

# guardian: allow-direct-prompt-compilation -- audit script uses print for CLI output

import sqlite3
from pathlib import Path


def identify_guardrail_gaps():
    adg_dir = Path(__file__).resolve().parents[2] / "artifacts" / "adg"
    sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        print("No ADG SQLite files found")
        return

    latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    print(f"Querying: {latest_sqlite.name}\n")

    conn = sqlite3.connect(latest_sqlite)
    cur = conn.cursor()

    # High-risk edge types that should have guardrails
    high_risk_edges = [
        "accesses_credential",
        "external_http_call",
        "reads_secret",
        "invokes_dynamic",
        "invokes_eval",
        "invokes_importlib",
    ]

    print("=== High-Risk Operations Without Guardrails ===\n")

    for edge_type in high_risk_edges:
        # Get files with this edge type
        cur.execute(f"""
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = '{edge_type}'
        """)
        files_with_risk = {row[0] for row in cur.fetchall()}

        # Get files with guardrails
        cur.execute("""
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        """)
        files_with_guardrails = {row[0] for row in cur.fetchall()}

        # Find gap
        gap_files = files_with_risk - files_with_guardrails

        if gap_files:
            print(f"\n{edge_type}: {len(gap_files)} files without guardrails")
            for f in sorted(gap_files)[:10]:  # Show first 10
                # Get count of this edge type in file
                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM edges
                    WHERE relation_type = '{edge_type}' AND source_file = ?
                """,
                    (f,),
                )
                count = cur.fetchone()[0]
                print(f"  {f} ({count} sites)")
            if len(gap_files) > 10:
                print(f"  ... and {len(gap_files) - 10} more files")

    # Check AgentDispatchRegistry usage without guardrails
    print("\n\n=== AgentDispatchRegistry.dispatch() Without Guardrails ===\n")
    cur.execute("""
        SELECT source_file, COUNT(*) as cnt
        FROM edges
        WHERE symbol LIKE '%AgentDispatchRegistry%dispatch%'
        AND source_file NOT IN (
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        )
        GROUP BY source_file
        ORDER BY cnt DESC
        LIMIT 20
    """)

    dispatch_gaps = cur.fetchall()
    if dispatch_gaps:
        print(f"Found {len(dispatch_gaps)} files using dispatch without guardrails:\n")
        for file_path, count in dispatch_gaps:
            print(f"{file_path}: {count} dispatch calls")
    else:
        print("All dispatch calls have guardrail coverage ✓")

    # Check LLM client usage without guardrails
    print("\n\n=== LLM Client Usage Without Guardrails ===\n")
    cur.execute("""
        SELECT source_file, symbol, COUNT(*) as cnt
        FROM edges
        WHERE (
            symbol LIKE '%openai%' OR
            symbol LIKE '%anthropic%' OR
            symbol LIKE '%gemini%' OR
            symbol LIKE '%LLM%' OR
            symbol LIKE '%llm%'
        )
        AND relation_type = 'calls'
        AND source_file NOT IN (
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        )
        AND source_file NOT LIKE 'tests/%'
        GROUP BY source_file, symbol
        ORDER BY cnt DESC
        LIMIT 20
    """)

    llm_gaps = cur.fetchall()
    if llm_gaps:
        print(f"Found {len(llm_gaps)} LLM usage patterns without guardrails:\n")
        for file_path, symbol, count in llm_gaps:
            print(f"{file_path}: {symbol} ({count} calls)")

    # Prompt Governance Gaps
    print("\n\n=== Prompt Governance Gaps ===\n")

    # D0 injection fence coverage
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type = 'generates_prompt' AND symbol LIKE '%D0%'"
    )
    d0_files = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'generates_prompt'")
    total_prompt_files = cur.fetchone()[0]
    if total_prompt_files > 0:
        d0_pct = 100 * d0_files / total_prompt_files
        print(f"D0 injection fence coverage: {d0_files}/{total_prompt_files} files ({d0_pct:.1f}%)")
        if d0_pct < 100:
            cur.execute(
                "SELECT DISTINCT source_file FROM edges "
                "WHERE relation_type = 'generates_prompt' "
                "AND source_file NOT IN ("
                "  SELECT DISTINCT source_file FROM edges "
                "  WHERE relation_type = 'generates_prompt' AND symbol LIKE '%D0%'"
                ") AND source_file NOT LIKE 'tests/%'"
            )
            for (f,) in cur.fetchall():
                print(f"  MISSING D0: {f}")

    # Agent reasoning files without prompt governance edges
    cur.execute(
        "SELECT DISTINCT source_file FROM edges "
        "WHERE (source_file LIKE 'apps_%/reasoning/%' OR source_file LIKE 'apps_shared/reasoning/%') "
        "AND source_file NOT LIKE '%__init__%' "
        "AND source_file NOT IN ("
        "  SELECT DISTINCT source_file FROM edges "
        "  WHERE relation_type IN ('generates_prompt', 'consumes_prompt', "
        "    'instruction_injection_source', 'prompt_template_used_by')"
        ") ORDER BY source_file"
    )
    agents_no_prompt = [r[0] for r in cur.fetchall()]
    print(f"\nAgent reasoning files WITHOUT prompt governance edges: {len(agents_no_prompt)}")
    for f in agents_no_prompt[:15]:
        print(f"  {f}")
    if len(agents_no_prompt) > 15:
        print(f"  ... and {len(agents_no_prompt) - 15} more")

    # Instruction injection source coverage
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'instruction_injection_source'")
    inj_count = cur.fetchone()[0]
    print(f"\nInstruction injection sources tracked: {inj_count}")
    if inj_count < 5:
        print("  WARNING: Very low injection source tracking — scanner may need wider symbol coverage")

    # Summary
    print("\n\n=== Wave 4 Target Summary ===\n")

    total_high_risk = 0
    for edge_type in high_risk_edges:
        cur.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type = '{edge_type}'")
        count = cur.fetchone()[0]
        total_high_risk += count
        print(f"{edge_type}: {count} edges")

    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'applies_guardrail'")
    current_guardrails = cur.fetchone()[0]

    print(f"\nTotal high-risk edges: {total_high_risk}")
    print(f"Current guardrail coverage: {current_guardrails} edges")
    print(f"Coverage ratio: {100 * current_guardrails / max(total_high_risk, 1):.1f}%")

    conn.close()


if __name__ == "__main__":
    identify_guardrail_gaps()
