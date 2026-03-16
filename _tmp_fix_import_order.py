"""Fix import ordering: ensure governance emitter imports appear BEFORE their calls.

Strategy:
1. For each file, find ALL governance emitter calls
2. Find the FIRST lifecycle_trace_contract import block
3. Add any missing governance emitters to that FIRST block
4. Remove any duplicate second import block that batch_gov.py created
"""
import os, re

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

def find_all_py(root):
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
        for f in filenames:
            if f.endswith('.py') and not f.startswith('_tmp_'):
                result.append(os.path.join(dirpath, f).replace('\\', '/'))
    return result

LTC_OPEN = "from agentic_core.runtime.lifecycle_trace_contract import ("

all_files = find_all_py(".")
print(f"Scanning {len(all_files)} files...")

fixed = 0
removed_dup_blocks = 0

for fpath in all_files:
    if "lifecycle_trace_contract.py" in fpath:
        continue
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        continue

    content = "".join(lines)

    # Check if any governance emitter is called in this file
    has_gov_call = any(em + "(" in content for em in GOV_EMITTERS)
    if not has_gov_call:
        continue

    # Find ALL lifecycle_trace_contract import blocks (start_line, end_line)
    blocks = []
    i = 0
    while i < len(lines):
        if LTC_OPEN in lines[i]:
            start = i
            j = i + 1
            while j < len(lines):
                if lines[j].strip() == ")" or lines[j].strip().startswith(")"):
                    blocks.append((start, j))
                    break
                j += 1
            i = j + 1 if j < len(lines) else i + 1
        else:
            i += 1

    if not blocks:
        continue

    # Collect all imported names from ALL blocks
    first_block = blocks[0]
    first_block_imports = set()
    for line_idx in range(first_block[0], first_block[1] + 1):
        stripped = lines[line_idx].strip().rstrip(',').rstrip()
        # Remove comments
        if '#' in stripped:
            stripped = stripped[:stripped.index('#')].strip().rstrip(',').strip()
        if stripped.startswith("_emit_") or stripped.startswith("emit_") or stripped.startswith("LayerSegment"):
            first_block_imports.add(stripped)

    # Find which governance emitters are called but missing from FIRST block
    needed_in_first = []
    for em in GOV_EMITTERS:
        if em + "(" in content and em not in first_block_imports:
            needed_in_first.append(em)

    if not needed_in_first and len(blocks) <= 1:
        continue

    modified = False

    # Step 1: Add missing imports to FIRST block (before its closing paren)
    if needed_in_first:
        insert_at = first_block[1]
        new_import_lines = [f"    {em},\n" for em in needed_in_first]
        for j, nl in enumerate(new_import_lines):
            lines.insert(insert_at + j, nl)
        modified = True
        # Adjust all subsequent block indices
        offset = len(new_import_lines)
        blocks = [(s + (offset if s > first_block[0] else 0), e + (offset if e >= first_block[1] else 0)) for s, e in blocks]

    # Step 2: Remove duplicate blocks (blocks[1:]) that were created by batch_gov.py
    # Only remove if all their imports are now in the first block
    if len(blocks) > 1:
        # Re-read what's now in the first block
        first_end = blocks[0][1] + (len(needed_in_first) if needed_in_first else 0)
        first_content = "".join(lines[blocks[0][0]:first_end + 1])

        for block_start, block_end in reversed(blocks[1:]):
            # Check if this block's imports are all in the first block
            block_imports = []
            all_covered = True
            for line_idx in range(block_start + 1, block_end):
                stripped = lines[line_idx].strip().rstrip(',').strip()
                if '#' in stripped:
                    stripped = stripped[:stripped.index('#')].strip().rstrip(',').strip()
                if stripped and stripped != "(" and stripped != ")":
                    block_imports.append(stripped)
                    if stripped not in first_content:
                        all_covered = False

            if all_covered and block_imports:
                # Safe to remove this duplicate block
                del lines[block_start:block_end + 1]
                removed_dup_blocks += 1
                modified = True

    if modified:
        with open(fpath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        fixed += 1

print(f"\nFixed {fixed} files, removed {removed_dup_blocks} duplicate import blocks")

# Verify key import chain files
print("\n--- Import chain verification ---")
chain_files = [
    "agentic_core/L0_routing/seams/layer_emission_seam.py",
    "agentic_core/L0_routing/capacity/capacity_aware_router.py",
    "agentic_core/L0_routing/capacity/capacity_snapshot.py",
    "agentic_core/L0_routing/artifacts/deterministic_routing_gateway.py",
    "agentic_core/L0_routing/types/routing_artifact_types.py",
]
for cf in chain_files:
    try:
        with open(cf) as f:
            c = f.read()
        broken = []
        for em in GOV_EMITTERS:
            if em + "(" in c:
                idx = c.find(em + "(")
                if em not in c[:idx]:
                    broken.append(em)
        status = "OK" if not broken else f"BROKEN: {broken[:3]}"
        print(f"  {cf}: {status}")
    except FileNotFoundError:
        print(f"  {cf}: NOT FOUND")
