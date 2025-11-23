from __future__ import annotations

from typing import List

from profiles.agent_profile import AgentCard
from core.agent_registry import AgentRegistry


def choose_agents_for_task(task_type: str, registry: AgentRegistry) -> List[AgentCard]:
    """Return a list of AgentCard objects appropriate for the given task.

    Simple policy:
      - For strategy tasks → prefer agent_type == "planner"
      - For retrieval/RAG tasks → prefer "researcher"
      - For drafting → "drafter"
      - For QA → "qa"
      - For safety → "safety"
    Fallback: return all agents if no specific type matches.
    """

    mapping = {
        "strategy": "planner",
        "planning": "planner",
        "retrieval": "researcher",
        "rag": "researcher",
        "drafting": "drafter",
        "qa": "qa",
        "safety": "safety",
    }
    desired_type = mapping.get(task_type)
    if desired_type is None:
        return list(registry.agents.values())
    candidates = registry.find_agents_by_type(desired_type)
    return candidates or list(registry.agents.values())
