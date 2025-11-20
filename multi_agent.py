# FILE: 10_10/multi_agent.py
"""
Deprecated Multi-Agent Layer (v10_10)
=====================================

In earlier architectures (v10_7, v10_8, early v10_9):
-----------------------------------------------------
This module hosted:
    • Multi-agent “councils”
    • Emergent-agent routing
    • AgentGraph topologies
    • Meta-agent arbitration
    • Multi-step group reasoning

In v10_10:
-----------
ALL cognitive behavior has been refactored into SINGLE-PURPOSE L2 agents:

    cognitive_agents.py
        • StrategyLLMAgent
        • DraftingGuild
        • SemanticQAAgent
        • ConstitutionalSafetyAgent

ALL orchestration has been refactored into:

    l3.py
        • DAG
        • Correction surfaces + retry loop

ALL safety gating has been refactored into:

    l5.py
        • deterministic SafetyPolicy

Therefore:
-----------
There is *no longer* any valid use case for this module.

It remains ONLY as a compatibility stub so older branches
or legacy scripts importing `multi_agent` will not crash.

DO NOT place any agent logic, planning, routing, or orchestration here.
"""


# This file intentionally exports nothing.
__all__: list[str] = []


def __getattr__(name: str):
    """
    Catch all legacy attribute accesses (for safety).
    Provide a clear error message at runtime.
    """
    raise AttributeError(
        f"'multi_agent' is deprecated in v10_10. "
        f"All cognitive agents are now in `cognitive_agents.py` and "
        f"all orchestration is in `l3.py`. Accessing '{name}' is invalid."
    )
