"""Wave 3b: Fix the 13 skipped modules with non-standard patterns."""

files = [
    ("agentic_core/mixins/adaptive_execution_mixin.py", "L3"),
    ("apps_shared/scripts/app_remediation_dispatcher.py", "apps"),
    ("apps_shared/spine/vigilance_dispatcher_adapter.py", "apps"),
    ("tests/adg/test_adg_g17_g22_completeness_accuracy.py", "test"),
    ("tests/adg/test_adg_gap_remediation_p0_p4.py", "test"),
    ("tests/governance/test_plumbing_rigorous.py", "test"),
    ("tests/integration/test_creative_cross_context.py", "test"),
    ("tests/unit/agentic_core/L2_execution/enforcement/test_static_dispatch_registry.py", "test"),
    ("tests/unit/agentic_core/L3_orchestration/test_orchestration_handshake.py", "test"),
    ("tests/unit/test_spine_adapter_wiring.py", "test"),
    ("tests/unit/test_vigilance_dispatcher.py", "test"),
    ("tests/unit_min_deps/test_handshake_state_machine.py", "test"),
    ("tests/unit_min_deps/test_llm_workflow_creative.py", "test"),
]

NEW_IMPORTS = [
    "_emit_checks_agent_registry",
    "_emit_dispatches_execution_plan",
    "_emit_orchestrates_workflow",
    "_emit_routes_to_agent",
    "_emit_validates_agent_capability",
]

patched = 0

for f, layer in files:
    src = open(f, encoding="utf-8").read()
    mod = f.split("/")[-1].replace(".py", "")
    original = src
    lines = src.split("\n")

    # Step 1: Add missing imports into the lifecycle_trace_contract import block
    for imp in NEW_IMPORTS:
        if imp in src:
            continue
        # Find any existing _emit_ import line inside the ltc block
        newlines = src.split("\n")
        inserted = False
        for i, line in enumerate(newlines):
            stripped = line.strip()
            # Look for any _emit_ import line ending with comma
            if stripped.startswith("_emit_") and stripped.endswith(",") and i > 0:
                # Check we're inside the ltc import block by looking back
                for j in range(max(0, i - 15), i):
                    if "lifecycle_trace_contract" in newlines[j]:
                        newlines.insert(i + 1, f"    {imp},")
                        src = "\n".join(newlines)
                        inserted = True
                        break
                if inserted:
                    break
            # Also handle inline import patterns like `    _emit_reads_policy_state,  # noqa`
            if "_emit_reads_policy_state" in stripped and stripped.endswith(",") and not stripped.startswith("#"):
                for j in range(max(0, i - 15), i):
                    if "lifecycle_trace_contract" in newlines[j]:
                        newlines.insert(i + 1, f"    {imp},")
                        src = "\n".join(newlines)
                        inserted = True
                        break
                if inserted:
                    break

    # Step 2: Add bootstrap calls
    if f"_emit_routes_to_agent" not in src or f'_emit_routes_to_agent("p1", "{mod}"' not in src:
        bootstrap = "\n".join([
            f'_emit_routes_to_agent("p1", "{mod}", "{layer}")',
            f'_emit_orchestrates_workflow("p1", "{mod}", "{layer}")',
            f'_emit_dispatches_execution_plan("p1", "{mod}", "{layer}")',
            f'_emit_validates_agent_capability("p1", "{mod}", "{layer}")',
            f'_emit_checks_agent_registry("p1", "{mod}", "{layer}")',
        ])

        # Find anchor: _emit_reads_policy_state call (not import)
        newlines = src.split("\n")
        inserted = False
        for i, line in enumerate(newlines):
            stripped = line.strip()
            if stripped.startswith(f'_emit_reads_policy_state("p1"') and f'"{mod}"' in stripped:
                newlines.insert(i + 1, bootstrap)
                src = "\n".join(newlines)
                inserted = True
                break

        if not inserted:
            # Try broader anchor: any _emit_reads_policy_state bootstrap call
            for i, line in enumerate(newlines):
                stripped = line.strip()
                if stripped.startswith("_emit_reads_policy_state(") and "import" not in stripped and not stripped.startswith("#"):
                    newlines.insert(i + 1, bootstrap)
                    src = "\n".join(newlines)
                    inserted = True
                    break

        if not inserted:
            # Last resort: find end of imports and add there
            newlines = src.split("\n")
            for i, line in enumerate(newlines):
                if "lifecycle_trace_contract" in line and "from" in line:
                    # Find the closing paren
                    for j in range(i, min(i + 30, len(newlines))):
                        if newlines[j].strip() == ")":
                            newlines.insert(j + 1, "\n" + bootstrap)
                            src = "\n".join(newlines)
                            inserted = True
                            break
                    break

    if src != original:
        open(f, "w", encoding="utf-8").write(src)
        patched += 1
        print(f"PATCHED: {mod}")
    else:
        print(f"SKIP: {mod}")

print(f"\nTotal patched: {patched}/13")
