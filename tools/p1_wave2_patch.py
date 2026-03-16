"""Wave 2 automated P1 orchestration governance wiring.

Adds 5 P1 emitter imports and bootstrap calls to 15 L3 gap modules.
"""

files = [
    "agentic_core/L3_orchestration/arbitration/arbitrator.py",
    "agentic_core/L3_orchestration/contracts/agent_handoff.py",
    "agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py",
    "agentic_core/L3_orchestration/engines/AgentFactory.py",
    "agentic_core/L3_orchestration/engines/action_router.py",
    "agentic_core/L3_orchestration/engines/autonomous_execution_engine.py",
    "agentic_core/L3_orchestration/engines/coordinator_capability_orchestrator.py",
    "agentic_core/L3_orchestration/engines/decomposition_orchestrator.py",
    "agentic_core/L3_orchestration/engines/nervous_system.py",
    "agentic_core/L3_orchestration/engines/recovery_coordinator_orchestrator.py",
    "agentic_core/L3_orchestration/engines/recursive_orchestrator.py",
    "agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
    "agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
    "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
    "agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
]

NEW_IMPORTS = [
    "_emit_checks_agent_registry",
    "_emit_dispatches_execution_plan",
    "_emit_orchestrates_workflow",
    "_emit_routes_to_agent",
    "_emit_validates_agent_capability",
]

patched = 0
for f in files:
    src = open(f, encoding="utf-8").read()
    mod = f.split("/")[-1].replace(".py", "")
    original = src

    # 1) Add imports into the lifecycle_trace_contract import block
    for imp in NEW_IMPORTS:
        if imp not in src:
            # Insert after _emit_reads_policy_state import line
            lines = src.split("\n")
            for i, line in enumerate(lines):
                if "_emit_reads_policy_state" in line and ("from" in lines[max(0, i - 5):i + 1].__repr__() or "import" in line):
                    if "from" in line or "import" in line or line.strip().startswith("_emit_reads_policy_state,"):
                        lines.insert(i + 1, f"    {imp},")
                        src = "\n".join(lines)
                        break

    # 2) Add bootstrap calls after _emit_reads_policy_state("p1", ...) call
    bootstrap_anchor = f'_emit_reads_policy_state("p1", "{mod}", "L3")'
    if bootstrap_anchor in src and f'_emit_routes_to_agent("p1", "{mod}", "L3")' not in src:
        bootstrap_lines = "\n".join([
            f'_emit_routes_to_agent("p1", "{mod}", "L3")',
            f'_emit_orchestrates_workflow("p1", "{mod}", "L3")',
            f'_emit_dispatches_execution_plan("p1", "{mod}", "L3")',
            f'_emit_validates_agent_capability("p1", "{mod}", "L3")',
            f'_emit_checks_agent_registry("p1", "{mod}", "L3")',
        ])
        src = src.replace(bootstrap_anchor, bootstrap_anchor + "\n" + bootstrap_lines)

    if src != original:
        open(f, "w", encoding="utf-8").write(src)
        patched += 1
        print(f"PATCHED: {mod}")
    else:
        print(f"SKIP: {mod}")

print(f"\nTotal patched: {patched}/15")
