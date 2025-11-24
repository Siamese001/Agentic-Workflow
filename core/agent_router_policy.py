from __future__ import annotations

"""Defines simple routing rules that pick which specialist agents handle planning, drafting, review, and safety so each resume step is done by the right expertise."""

from typing import List

from profiles.agent_profile import AgentCard
from core.agent_registry import AgentRegistry


def choose_agents_for_task(task_type: str, registry: AgentRegistry) -> List[AgentCard]:
    """Chooses agents for a given task type so planning, retrieval, drafting, QA, and safety work are handled by specialists, leading to clearer, more relevant, and safer resumes."""

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
