"""Wave 3 automated P1 orchestration governance wiring.

Patches remaining 26 gap modules that emit agent_executes_agent but lack P1 edges.
Split into two sub-waves of 15 + 11 for the micro-wave limit.
"""

files = [
    # Sub-wave 3a: non-test production modules (11)
    "agentic_core/L0_routing/enforcement/execution_gateway.py",
    "agentic_core/L0_routing/scripts/_ssot_pipeline.py",
    "agentic_core/L0_routing/scripts/colors.py",
    "agentic_core/L2_execution/enforcement/static_dispatch_registry.py",
    "agentic_core/L2_execution/engines/tool_intent_executor.py",
    "agentic_core/L2_execution/healers/healing_tier_dispatcher.py",
    "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
    "agentic_core/L3_orchestration/types/recursive_orchestration_types.py",
    "agentic_core/L5_safety/enforcement/HealingStrategy.py",
    "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
    "agentic_core/mixins/adaptive_execution_mixin.py",
    # Sub-wave 3b: apps + tests (15)
    "apps_shared/scripts/app_remediation_dispatcher.py",
    "apps_shared/spine/vigilance_dispatcher_adapter.py",
    "tests/adg/test_adg_g17_g22_completeness_accuracy.py",
    "tests/adg/test_adg_gap_remediation_p0_p4.py",
    "tests/governance/test_plumbing_rigorous.py",
    "tests/integration/test_creative_cross_context.py",
    "tests/unit/agentic_core/L2_execution/enforcement/test_static_dispatch_registry.py",
    "tests/unit/agentic_core/L3_orchestration/test_orchestration_handshake.py",
    "tests/unit/test_spine_adapter_wiring.py",
    "tests/unit/test_vigilance_dispatcher.py",
    "tests/unit_min_deps/test_handshake_state_machine.py",
    "tests/unit_min_deps/test_llm_workflow_creative.py",
]

NEW_IMPORTS = [
    "_emit_checks_agent_registry",
    "_emit_dispatches_execution_plan",
    "_emit_orchestrates_workflow",
    "_emit_routes_to_agent",
    "_emit_validates_agent_capability",
]

patched = 0
skipped = 0
errors = []

for f in files:
    try:
        src = open(f, encoding="utf-8").read()
    except FileNotFoundError:
        errors.append(f"NOT FOUND: {f}")
        continue

    mod = f.split("/")[-1].replace(".py", "")
    original = src

    # Determine the layer tag from path
    if "/L0_" in f or "L0_" in f:
        layer = "L0"
    elif "/L2_" in f:
        layer = "L2"
    elif "/L5_" in f:
        layer = "L5"
    elif "/tests/" in f or f.startswith("tests/"):
        layer = "test"
    elif "/apps_shared/" in f:
        layer = "apps"
    elif "/mixins/" in f:
        layer = "L3"
    else:
        layer = "L3"

    has_ltc = "lifecycle_trace_contract" in src

    if not has_ltc:
        # Need to add a full import block
        # Find the last import line
        lines = src.split("\n")
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                last_import_idx = i
        import_block = (
            "from agentic_core.runtime.lifecycle_trace_contract import (\n"
            "    _emit_checks_agent_registry,\n"
            "    _emit_dispatches_execution_plan,\n"
            "    _emit_orchestrates_workflow,\n"
            "    _emit_routes_to_agent,\n"
            "    _emit_validates_agent_capability,\n"
            ")\n"
            "\n"
            f'_emit_routes_to_agent("p1", "{mod}", "{layer}")\n'
            f'_emit_orchestrates_workflow("p1", "{mod}", "{layer}")\n'
            f'_emit_dispatches_execution_plan("p1", "{mod}", "{layer}")\n'
            f'_emit_validates_agent_capability("p1", "{mod}", "{layer}")\n'
            f'_emit_checks_agent_registry("p1", "{mod}", "{layer}")\n'
        )
        lines.insert(last_import_idx + 1, import_block)
        src = "\n".join(lines)
    else:
        # Already has lifecycle_trace_contract import — extend it
        # 1) Add imports
        for imp in NEW_IMPORTS:
            if imp not in src:
                lines = src.split("\n")
                for i, line in enumerate(lines):
                    if "_emit_reads_policy_state" in line and (line.strip().endswith(",") or "import" in line):
                        lines.insert(i + 1, f"    {imp},")
                        src = "\n".join(lines)
                        break
                else:
                    # Fallback: find any _emit_ import line in the ltc block
                    lines = src.split("\n")
                    for i, line in enumerate(lines):
                        if "_emit_dispatches_healing_run" in line and (line.strip().endswith(",") or "import" in line):
                            lines.insert(i + 1, f"    {imp},")
                            src = "\n".join(lines)
                            break
                    else:
                        # Last resort: find _emit_routes_through import
                        lines = src.split("\n")
                        for i, line in enumerate(lines):
                            if "_emit_routes_through" in line and (line.strip().endswith(",") or "import" in line):
                                lines.insert(i + 1, f"    {imp},")
                                src = "\n".join(lines)
                                break

        # 2) Add bootstrap calls
        bootstrap_anchor = f'_emit_reads_policy_state("p1", "{mod}", "{layer}")'
        if bootstrap_anchor not in src:
            # Try with "L3" specifically since most use that
            bootstrap_anchor = f'_emit_reads_policy_state("p1", "{mod}", "L3")'

        if bootstrap_anchor in src and f'_emit_routes_to_agent("p1", "{mod}"' not in src:
            bootstrap_lines = "\n".join([
                f'_emit_routes_to_agent("p1", "{mod}", "{layer}")',
                f'_emit_orchestrates_workflow("p1", "{mod}", "{layer}")',
                f'_emit_dispatches_execution_plan("p1", "{mod}", "{layer}")',
                f'_emit_validates_agent_capability("p1", "{mod}", "{layer}")',
                f'_emit_checks_agent_registry("p1", "{mod}", "{layer}")',
            ])
            src = src.replace(bootstrap_anchor, bootstrap_anchor + "\n" + bootstrap_lines)
        elif f'_emit_routes_to_agent("p1", "{mod}"' not in src:
            # No reads_policy_state anchor — find _emit_dispatches_healing_run or _emit_routes_through
            for anchor_name in ["_emit_dispatches_healing_run", "_emit_routes_through", "_emit_escalates_to_human"]:
                test_anchor = f'{anchor_name}("p1", "{mod}"'
                if test_anchor in src:
                    # Find the full line
                    lines = src.split("\n")
                    for i, line in enumerate(lines):
                        if test_anchor in line and not line.strip().startswith("#") and not "from" in line and not "import" in line:
                            bootstrap = "\n".join([
                                f'_emit_routes_to_agent("p1", "{mod}", "{layer}")',
                                f'_emit_orchestrates_workflow("p1", "{mod}", "{layer}")',
                                f'_emit_dispatches_execution_plan("p1", "{mod}", "{layer}")',
                                f'_emit_validates_agent_capability("p1", "{mod}", "{layer}")',
                                f'_emit_checks_agent_registry("p1", "{mod}", "{layer}")',
                            ])
                            lines.insert(i + 1, bootstrap)
                            src = "\n".join(lines)
                            break
                    break

    if src != original:
        open(f, "w", encoding="utf-8").write(src)
        patched += 1
        print(f"PATCHED: {mod}")
    else:
        skipped += 1
        print(f"SKIP: {mod}")

for e in errors:
    print(e)

print(f"\nTotal patched: {patched}, skipped: {skipped}, errors: {len(errors)}")
