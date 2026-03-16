"""Batch-wire _emit_escalates_to_human and _emit_routes_through into ALL missing modules."""
import sqlite3, glob, os, re

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

# Get all modules with 'calls' edges
all_mods = set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'"
).fetchall())

conn.close()
print(f"Total modules with calls: {len(all_mods)}")

# Find modules truly missing each emitter
def find_truly_missing(modules, emitter_name):
    missing = []
    for mod in modules:
        try:
            with open(mod, "r", encoding="utf-8") as f:
                content = f.read()
            if emitter_name not in content:
                missing.append(mod)
        except (FileNotFoundError, UnicodeDecodeError):
            pass
    return missing

eth_missing = find_truly_missing(all_mods, "_emit_escalates_to_human")
rt_missing = find_truly_missing(all_mods, "_emit_routes_through")
print(f"Missing _emit_escalates_to_human in source: {len(eth_missing)}")
print(f"Missing _emit_routes_through in source: {len(rt_missing)}")

# Union of both sets for wiring
all_to_wire = set(eth_missing) | set(rt_missing)
print(f"Total unique modules to wire: {len(all_to_wire)}")

changed = []
errors = []

for fpath in sorted(all_to_wire):
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        errors.append((fpath, str(e)))
        continue

    original = content
    mod_name = os.path.splitext(os.path.basename(fpath))[0]
    needs_eth = "_emit_escalates_to_human" not in content
    needs_rt = "_emit_routes_through" not in content

    if not needs_eth and not needs_rt:
        continue

    # Build list of imports to add
    imports_to_add = []
    if needs_eth:
        imports_to_add.append("_emit_escalates_to_human")
    if needs_rt:
        imports_to_add.append("_emit_routes_through")

    # Build list of emitter calls to add
    calls_to_add = []
    if needs_eth:
        calls_to_add.append(f'_emit_escalates_to_human("p1", "{mod_name}", "human_escalation")')
    if needs_rt:
        calls_to_add.append(f'_emit_routes_through("p1", "{mod_name}", "route_through")')

    # Strategy 1: Add to existing lifecycle_trace_contract import block
    ltc_pattern = "from agentic_core.runtime.lifecycle_trace_contract import ("
    ltc_idx = content.find(ltc_pattern)

    if ltc_idx >= 0:
        # Find the LAST import block from lifecycle_trace_contract (some files have multiple)
        last_ltc_idx = ltc_idx
        search_from = ltc_idx + 1
        while True:
            next_idx = content.find(ltc_pattern, search_from)
            if next_idx < 0:
                break
            last_ltc_idx = next_idx
            search_from = next_idx + 1

        # Find closing paren of last import block
        close_paren = content.find("\n)", last_ltc_idx)
        if close_paren >= 0:
            import_lines = "\n".join(f"    {imp}," for imp in imports_to_add)
            content = content[:close_paren] + "\n" + import_lines + content[close_paren:]
        else:
            # Fallback: single-line import, add new import after
            eol = content.find("\n", last_ltc_idx)
            if eol >= 0:
                new_import = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
                new_import += ",\n".join(f"    {imp}" for imp in imports_to_add)
                new_import += ",\n)\n"
                content = content[:eol+1] + new_import + content[eol+1:]
    else:
        # No existing import block — add one after the last import line
        lines = content.split("\n")
        last_import_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_line = i
            # Also count continuation lines of multi-line imports
            if last_import_line >= 0 and stripped == ")":
                last_import_line = i

        if last_import_line >= 0:
            new_import = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
            new_import += ",\n".join(f"    {imp}" for imp in imports_to_add)
            new_import += ",\n)"
            lines.insert(last_import_line + 1, new_import)
            content = "\n".join(lines)
        else:
            # No imports at all — add at top after docstring
            new_import = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
            new_import += ",\n".join(f"    {imp}" for imp in imports_to_add)
            new_import += ",\n)\n"
            # Find end of module docstring if any
            if content.startswith('"""') or content.startswith("'''"):
                quote = content[:3]
                end_doc = content.find(quote, 3)
                if end_doc >= 0:
                    insert_pos = content.find("\n", end_doc) + 1
                    content = content[:insert_pos] + "\n" + new_import + content[insert_pos:]
                else:
                    content = new_import + "\n" + content
            else:
                content = new_import + "\n" + content

    # Add emitter calls — find best insertion point
    calls_block = "\n".join(calls_to_add)

    # Try to find existing module-level emitter calls to place nearby
    # Look for common P1 markers
    p1_markers = [
        f'_emit_reads_policy_state("p1", "{mod_name}"',
        f'_emit_proposal_commits_routing("p1", "{mod_name}"',
        f'_emit_validated_by_safety_plane("p1", "{mod_name}"',
        f'_emit_writes_through("p1", "{mod_name}"',
        f'_emit_pulls_context("p1", "{mod_name}"',
        f'_emit_dispatches_healing_run("p1", "{mod_name}"',
    ]
    # P0 markers as fallback
    p0_markers = [
        f'_emit_snapshots_state("p0", "{mod_name}"',
        f'_emit_applies_guardrail("p0", "{mod_name}"',
        f'emit_determinism_digest("p0", "{mod_name}"',
        f'emit_replay_key("p0", "{mod_name}"',
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
        # Find last module-level _emit_ or emit_ call
        lines = content.split("\n")
        last_emit_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith("_emit_") or stripped.startswith("emit_")) and not line.startswith(" ") and not line.startswith("\t"):
                last_emit_idx = i

        if last_emit_idx >= 0:
            for call in reversed(calls_to_add):
                lines.insert(last_emit_idx + 1, call)
            content = "\n".join(lines)
            inserted = True

    if not inserted:
        # Last resort: add after imports (find first non-import, non-blank line)
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
if errors:
    print(f"Errors: {len(errors)}")
    for fp, err in errors[:5]:
        print(f"  {fp}: {err}")

# Show first and last few
if changed:
    for f in changed[:5]:
        print(f"  {f}")
    if len(changed) > 10:
        print(f"  ... ({len(changed) - 10} more) ...")
    for f in changed[-5:]:
        print(f"  {f}")
