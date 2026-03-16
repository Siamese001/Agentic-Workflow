"""Wire _emit_escalates_to_human into 9 modules that truly lack it."""

TARGETS = [
    ("agentic_core/L4_persistence/lifecycle/lifecycle_policy_applier.py", "lifecycle_policy_applier"),
    ("agentic_core/L4_persistence/lifecycle/state_lifecycle.py", "state_lifecycle"),
    ("agentic_core/adg/adapters/memory_mcp_adapter.py", "memory_mcp_adapter"),
    ("agentic_core/adg/analysis/dep_inversion.py", "dep_inversion"),
    ("agentic_core/adg/analysis/diff.py", "diff"),
    ("agentic_core/adg/analysis/healer_validator_graph.py", "healer_validator_graph"),
    ("agentic_core/adg/analysis/hotspot_index.py", "hotspot_index"),
    ("agentic_core/adg/analysis/impact.py", "impact"),
    ("agentic_core/adg/analysis/layer_authority.py", "layer_authority"),
]

changed = []

for fpath, mod_name in TARGETS:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    if "_emit_escalates_to_human" in content:
        print(f"SKIP: {fpath} already has escalates_to_human")
        continue

    # Strategy: find an existing lifecycle_trace_contract import block and add the import,
    # then add the emitter call near other module-level emitter calls.

    # 1. Add import
    # Find a lifecycle_trace_contract import block
    ltc = "from agentic_core.runtime.lifecycle_trace_contract import ("
    idx = content.find(ltc)
    if idx >= 0:
        # Find the closing paren of this import block
        close = content.find("\n)", idx)
        if close >= 0:
            # Insert _emit_escalates_to_human before the closing paren
            content = content[:close] + "\n    _emit_escalates_to_human," + content[close:]
        else:
            print(f"WARN: no closing paren for import in {fpath}")
            continue
    else:
        # No import block - check for single-line import
        ltc_single = "from agentic_core.runtime.lifecycle_trace_contract import "
        idx_s = content.find(ltc_single)
        if idx_s >= 0:
            # Find the end of this line
            eol = content.find("\n", idx_s)
            # Add a new import after it
            content = content[:eol+1] + "from agentic_core.runtime.lifecycle_trace_contract import _emit_escalates_to_human\n" + content[eol+1:]
        else:
            # No lifecycle_trace_contract import at all - add one after the last import
            # Find the last import line
            lines = content.split("\n")
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, "from agentic_core.runtime.lifecycle_trace_contract import _emit_escalates_to_human")
            content = "\n".join(lines)

    # 2. Add emitter call
    # Find existing module-level emitter calls to place ours nearby
    # Look for patterns like _emit_*("p1", ... or _emit_*("p0", ...
    # Place after the last such call at module level, or after imports if none

    # Try to find _emit_snapshots_state or _emit_applies_guardrail or similar P0/P1 markers
    markers = [
        f'_emit_snapshots_state("p0", "{mod_name}"',
        f'_emit_reads_policy_state("p1", "{mod_name}"',
        f'_emit_applies_guardrail("p0", "{mod_name}"',
        f'emit_determinism_digest("p0", "{mod_name}"',
        f'emit_replay_key("p0", "{mod_name}"',
        f'_emit_proposal_commits_routing("p1", "{mod_name}"',
    ]

    inserted = False
    for marker in markers:
        pos = content.find(marker)
        if pos >= 0:
            # Find end of this line
            eol = content.find("\n", pos)
            if eol >= 0:
                call = f'_emit_escalates_to_human("p1", "{mod_name}", "human_escalation")'
                content = content[:eol+1] + call + "\n" + content[eol+1:]
                inserted = True
                break

    if not inserted:
        # Fallback: add after last module-level emitter call
        # Find last _emit_ at module level (not indented)
        lines = content.split("\n")
        last_emit_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("_emit_") or line.startswith("emit_"):
                last_emit_idx = i
        if last_emit_idx > 0:
            call = f'_emit_escalates_to_human("p1", "{mod_name}", "human_escalation")'
            lines.insert(last_emit_idx + 1, call)
            content = "\n".join(lines)
            inserted = True

    if not inserted:
        print(f"WARN: could not find insertion point for emitter call in {fpath}")
        continue

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    changed.append(fpath)
    print(f"✓ {fpath}")

print(f"\n=== Files changed: {len(changed)} ===")
for f in changed:
    print(f"  {f}")
