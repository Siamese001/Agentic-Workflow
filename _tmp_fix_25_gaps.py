"""Fix 25 gap files: add governance emitter calls at ACTUAL module level."""
import ast, sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
conn = sqlite3.connect(db)

# Get the 25 gap files (missing escalates_to_human in ADG)
gap_mods = [r[0] for r in conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='escalates_to_human'
    )
    ORDER BY e1.source_file
""").fetchall()]
conn.close()

print(f"Gap files: {len(gap_mods)}")

GOV_CALLS = [
    '_emit_escalates_to_human("p1", "{mod}", "human_escalation")',
    '_emit_routes_through("p1", "{mod}", "route_through")',
    '_emit_checks_agent_registry("p1", "{mod}", "agent_registry")',
    '_emit_validates_agent_capability("p1", "{mod}", "capability")',
    '_emit_dispatches_execution_plan("p1", "{mod}", "exec_plan")',
    '_emit_agent_executes_agent("p1", "{mod}", "sub_agent")',
    '_emit_routes_to_agent("p1", "{mod}", "target_agent")',
    '_emit_verifies_policy("p1", "{mod}", "policy_check")',
    '_emit_observes_runtime_state("p1", "{mod}", "runtime_state")',
    '_emit_verifies_boundary("p1", "{mod}", "boundary_check")',
    '_emit_transcripts_response("p1", "{mod}", "transcript")',
    '_emit_hard_fails_untranscripted("p1", "{mod}")',
    '_emit_gated_by_confidence("p1", "{mod}", "confidence_gate")',
]

GOV_IMPORTS = [
    "_emit_escalates_to_human",
    "_emit_routes_through",
    "_emit_checks_agent_registry",
    "_emit_validates_agent_capability",
    "_emit_dispatches_execution_plan",
    "_emit_agent_executes_agent",
    "_emit_routes_to_agent",
    "_emit_verifies_policy",
    "_emit_observes_runtime_state",
    "_emit_verifies_boundary",
    "_emit_transcripts_response",
    "_emit_hard_fails_untranscripted",
    "_emit_gated_by_confidence",
]

fixed = 0
for fpath in gap_mods:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        print(f"  SKIP: {fpath}")
        continue

    mod_name = os.path.splitext(os.path.basename(fpath))[0]

    # Parse AST to find the last MODULE-LEVEL _emit_ call
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"  SYNTAX ERROR: {fpath}")
        continue

    last_emit_line = -1
    for node in ast.iter_child_nodes(tree):  # Only top-level nodes
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            if name and (name.startswith("_emit_") or name.startswith("emit_")):
                last_emit_line = node.lineno

    if last_emit_line < 0:
        # No module-level emit calls found — find last module-level import
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_emit_line = node.end_lineno or node.lineno

    if last_emit_line < 0:
        print(f"  NO INSERTION POINT: {fpath}")
        continue

    # Build the calls block
    calls = [c.format(mod=mod_name) for c in GOV_CALLS]
    calls_block = "\n".join(calls) + "\n"

    # Insert after last_emit_line
    lines = content.split("\n")
    # Check if governance calls already exist at module level (avoid duplicates)
    has_gov_at_module = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "_emit_checks_agent_registry":
                has_gov_at_module = True
                break

    if has_gov_at_module:
        print(f"  ALREADY HAS GOV AT MODULE LEVEL: {fpath}")
        continue

    # Also ensure imports exist in the first import block
    first_ltc_block_end = -1
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "agentic_core.runtime.lifecycle_trace_contract":
            first_ltc_block_end = (node.end_lineno or node.lineno) - 1  # 0-indexed
            break

    if first_ltc_block_end >= 0:
        # Check if governance imports are already there
        block_text = "\n".join(lines[node.lineno - 1:first_ltc_block_end + 1])
        missing_imports = [gi for gi in GOV_IMPORTS if gi not in block_text]
        if missing_imports:
            # Insert before closing )
            import_lines = [f"    {gi}," for gi in missing_imports]
            for j, il in enumerate(import_lines):
                lines.insert(first_ltc_block_end + j, il)
            # Adjust last_emit_line
            last_emit_line += len(import_lines)

    # Insert calls after last_emit_line
    for j, call in enumerate(calls):
        lines.insert(last_emit_line + j, call)

    new_content = "\n".join(lines)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)
    fixed += 1
    print(f"  Fixed: {fpath} (insert after line {last_emit_line})")

print(f"\nTotal fixed: {fixed}")
