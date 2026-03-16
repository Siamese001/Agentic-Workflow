"""Comprehensive fix: add missing governance emitter imports to ALL files."""
import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
conn = sqlite3.connect(db)
all_mods = sorted(set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'"
).fetchall()))
conn.close()

GOV_EMITTERS = [
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
    "_emit_escalates_to_human",
    "_emit_routes_through",
]

fixed = 0
for fpath in all_mods:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (FileNotFoundError, UnicodeDecodeError):
        continue

    content = "".join(lines)

    # Find which governance emitters are called but not imported
    missing = []
    for em in GOV_EMITTERS:
        call_str = em + "("
        if call_str not in content:
            continue
        # Check if there's an import for this emitter
        # Look for the emitter name in lines that are part of import statements
        found_import = False
        in_import_block = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("from ") and "import" in stripped:
                if "(" in stripped and ")" not in stripped:
                    in_import_block = True
                if em in stripped:
                    found_import = True
                    break
            elif in_import_block:
                if em in stripped:
                    found_import = True
                    break
                if ")" in stripped:
                    in_import_block = False
            # Also check single-line: from ... import em
            if stripped.startswith("from ") and em in stripped and "import" in stripped:
                found_import = True
                break
        if not found_import:
            missing.append(em)

    if not missing:
        continue

    # Find the LAST "from agentic_core.runtime.lifecycle_trace_contract import (" block
    ltc_open = "from agentic_core.runtime.lifecycle_trace_contract import ("
    last_block_start = -1
    last_block_end = -1  # line index of closing ")"

    i = 0
    while i < len(lines):
        if ltc_open in lines[i]:
            block_start = i
            # Find closing )
            j = i + 1
            while j < len(lines):
                if lines[j].strip().startswith(")"):
                    last_block_start = block_start
                    last_block_end = j
                    break
                j += 1
            i = j + 1
        else:
            i += 1

    if last_block_start >= 0 and last_block_end >= 0:
        # Insert missing imports before the closing )
        new_import_lines = [f"    {em},\n" for em in missing]
        for idx, new_line in enumerate(new_import_lines):
            lines.insert(last_block_end + idx, new_line)
    else:
        # No multi-line import block — find last import line and add new block
        last_imp = -1
        in_block = False
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("import ") or s.startswith("from "):
                in_block = "(" in s and ")" not in s
                last_imp = i
            elif in_block and s.startswith(")"):
                last_imp = i
                in_block = False

        new_block = "from agentic_core.runtime.lifecycle_trace_contract import (\n"
        for em in missing:
            new_block += f"    {em},\n"
        new_block += ")\n"

        if last_imp >= 0:
            lines.insert(last_imp + 1, new_block)
        else:
            lines.insert(0, new_block)

    with open(fpath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    fixed += 1

print(f"Fixed {fixed} files")

# Verify a sample
test_files = [
    "agentic_core/L0_routing/seams/layer_emission_seam.py",
    "agentic_core/L0_routing/capacity/capacity_aware_router.py",
    "agentic_core/L2_execution/adaptation/adaptation_orchestrator.py",
]
for tf in test_files:
    try:
        with open(tf) as f:
            c = f.read()
        missing_count = sum(1 for em in GOV_EMITTERS if em + "(" in c and em + "," not in c.split(em + "(")[0])
        # Better check: look for em in import section
        ok = True
        for em in GOV_EMITTERS:
            if em + "(" in c:
                idx = c.find(em + "(")
                before = c[:idx]
                if em not in before:
                    ok = False
                    break
        print(f"  {tf}: imports_ok={ok}")
    except FileNotFoundError:
        pass
