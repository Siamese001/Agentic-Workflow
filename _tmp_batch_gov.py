"""Batch-wire ALL remaining emitter-based governance edges into missing modules."""
import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

all_mods = set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'"
).fetchall())
conn.close()
print(f"Total modules: {len(all_mods)}")

# Emitters to wire: name -> (emitter_func_name, call_template)
# Signatures from lifecycle_trace_contract.py:
# _emit_checks_agent_registry(root_trace_id, checker, registry_key)
# _emit_validates_agent_capability(root_trace_id, validator, capability)
# _emit_dispatches_execution_plan(root_trace_id, dispatcher, plan_id)
# _emit_agent_executes_agent(root_trace_id, caller, callee)
# _emit_routes_to_agent(root_trace_id, caller, target_agent)
# _emit_verifies_policy(root_trace_id, policy, layer)
# _emit_observes_runtime_state(root_trace_id, state_key, layer)
# _emit_verifies_boundary(root_trace_id, boundary, layer)
# _emit_transcripts_response(root_trace_id, transcript_id, model_id)
# _emit_hard_fails_untranscripted(root_trace_id, reason)
# _emit_gated_by_confidence(root_trace_id, scorer, threshold)

EMITTERS = {
    "_emit_checks_agent_registry": lambda n: f'_emit_checks_agent_registry("p1", "{n}", "agent_registry")',
    "_emit_validates_agent_capability": lambda n: f'_emit_validates_agent_capability("p1", "{n}", "capability")',
    "_emit_dispatches_execution_plan": lambda n: f'_emit_dispatches_execution_plan("p1", "{n}", "exec_plan")',
    "_emit_agent_executes_agent": lambda n: f'_emit_agent_executes_agent("p1", "{n}", "sub_agent")',
    "_emit_routes_to_agent": lambda n: f'_emit_routes_to_agent("p1", "{n}", "target_agent")',
    "_emit_verifies_policy": lambda n: f'_emit_verifies_policy("p1", "{n}", "policy_check")',
    "_emit_observes_runtime_state": lambda n: f'_emit_observes_runtime_state("p1", "{n}", "runtime_state")',
    "_emit_verifies_boundary": lambda n: f'_emit_verifies_boundary("p1", "{n}", "boundary_check")',
    "_emit_transcripts_response": lambda n: f'_emit_transcripts_response("p1", "{n}", "transcript")',
    "_emit_hard_fails_untranscripted": lambda n: f'_emit_hard_fails_untranscripted("p1", "{n}")',
    "_emit_gated_by_confidence": lambda n: f'_emit_gated_by_confidence("p1", "{n}", "confidence_gate")',
}

# For each module, figure out which emitters are missing
changed = []
errors = []

for fpath in sorted(all_mods):
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        continue

    original = content
    mod_name = os.path.splitext(os.path.basename(fpath))[0]

    missing_emitters = []
    for emitter_name, call_fn in EMITTERS.items():
        if emitter_name not in content:
            missing_emitters.append((emitter_name, call_fn))

    if not missing_emitters:
        continue

    # Build imports and calls
    imports_to_add = [e[0] for e in missing_emitters]
    calls_to_add = [e[1](mod_name) for e in missing_emitters]

    # Add imports to existing lifecycle_trace_contract import block
    ltc_pattern = "from agentic_core.runtime.lifecycle_trace_contract import ("
    ltc_idx = content.find(ltc_pattern)

    if ltc_idx >= 0:
        # Find LAST import block
        last_ltc_idx = ltc_idx
        search_from = ltc_idx + 1
        while True:
            next_idx = content.find(ltc_pattern, search_from)
            if next_idx < 0:
                break
            last_ltc_idx = next_idx
            search_from = next_idx + 1

        close_paren = content.find("\n)", last_ltc_idx)
        if close_paren >= 0:
            import_lines = "\n".join(f"    {imp}," for imp in imports_to_add)
            content = content[:close_paren] + "\n" + import_lines + content[close_paren:]
        else:
            # Single-line import — add new block after
            eol = content.find("\n", last_ltc_idx)
            if eol >= 0:
                new_imp = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
                new_imp += ",\n".join(f"    {imp}" for imp in imports_to_add) + ",\n)\n"
                content = content[:eol+1] + new_imp + content[eol+1:]
    else:
        # No existing import — add after last import line
        lines = content.split("\n")
        last_import_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_line = i
            if last_import_line >= 0 and stripped == ")":
                last_import_line = i
        new_imp = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
        new_imp += ",\n".join(f"    {imp}" for imp in imports_to_add) + ",\n)"
        if last_import_line >= 0:
            lines.insert(last_import_line + 1, new_imp)
        else:
            lines.insert(0, new_imp)
        content = "\n".join(lines)

    # Add calls after existing emitter calls
    calls_block = "\n".join(calls_to_add)

    # Find insertion point
    p1_markers = [
        f'_emit_routes_through("p1", "{mod_name}"',
        f'_emit_escalates_to_human("p1", "{mod_name}"',
        f'_emit_reads_policy_state("p1", "{mod_name}"',
        f'_emit_proposal_commits_routing("p1", "{mod_name}"',
        f'_emit_validated_by_safety_plane("p1", "{mod_name}"',
        f'_emit_writes_through("p1", "{mod_name}"',
        f'_emit_pulls_context("p1", "{mod_name}"',
    ]
    p0_markers = [
        f'_emit_snapshots_state("p0", "{mod_name}"',
        f'_emit_applies_guardrail("p0", "{mod_name}"',
        f'emit_determinism_digest("p0", "{mod_name}"',
    ]

    inserted = False
    for marker in p1_markers + p0_markers:
        pos = content.find(marker)
        if pos >= 0:
            eol = content.find("\n", pos)
            if eol >= 0:
                content = content[:eol+1] + calls_block + "\n" + content[eol+1:]
                inserted = True
                break

    if not inserted:
        lines = content.split("\n")
        last_emit_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith("_emit_") or stripped.startswith("emit_")) and not line.startswith(" ") and not line.startswith("\t"):
                last_emit_idx = i
        if last_emit_idx >= 0:
            for j, call in enumerate(calls_to_add):
                lines.insert(last_emit_idx + 1 + j, call)
            content = "\n".join(lines)
            inserted = True

    if not inserted:
        # After imports
        lines = content.split("\n")
        insert_at = 0
        in_import = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                in_import = True
                insert_at = i + 1
            elif in_import and (stripped == "" or stripped == ")"):
                insert_at = i + 1
            elif in_import and stripped:
                break
        for j, call in enumerate(calls_to_add):
            lines.insert(insert_at + j, call)
        content = "\n".join(lines)

    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        changed.append(fpath)

print(f"\n=== Files changed: {len(changed)} ===")
print(f"First 5: {changed[:5]}")
print(f"Last 5: {changed[-5:]}")
