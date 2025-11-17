"""
L4 — Memory Manager

Provides deterministic handling for episodic (messages) and semantic (summary,
retrieval history) memory buffers. The manager collaborates with the context
budget to enforce lightweight limits.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

from l4_context_budget import ContextBudget
from utils_types import Message


class MemoryManager:
    """Stateful helper for managing contextual buffers."""

    def __init__(self, context_budget: ContextBudget | None = None) -> None:
        self.context_budget = context_budget or ContextBudget()

    def reconcile_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure memory-related keys exist and respect budgeting constraints."""

        normalized = copy.deepcopy(state)
        normalized.setdefault("metadata", {})
        messages: List[Message] = normalized.get("messages", []) or []
        rag_history: List[dict] = normalized.get("rag_history", []) or []
        summary: str = normalized.get("summary", "") or ""
        world: List[dict] = normalized.get("world", []) or []

        canonical_messages: List[Message] = []
        for message in messages:
            if isinstance(message, dict):
                message_copy: Dict[str, Any] = copy.deepcopy(message)
            else:
                message_copy = {"role": "unknown", "content": str(message)}
            message_copy.setdefault("role", "")
            message_copy.setdefault("content", "")
            canonical_messages.append(message_copy)

        messages = canonical_messages

        messages = self.context_budget.prune_messages(messages)
        rag_history = self.context_budget.prune_rag_items(rag_history)
        summary = self.context_budget.prune_summary(summary)
        world = self.context_budget.prune_world(world)

        normalized["messages"] = messages
        normalized["rag_history"] = rag_history
        normalized["summary"] = summary
        normalized["world"] = world
        normalized["metadata"]["context_consistency"] = "unchecked"
        return normalized

    def add_messages(self, state: Dict[str, Any], new_messages: List[Message]) -> Dict[str, Any]:
        """Append episodic messages and prune according to the budget."""

        merged = copy.deepcopy(state)
        merged.setdefault("messages", [])
        merged["messages"].extend(copy.deepcopy(new_messages))
        merged["messages"] = self.context_budget.prune_messages(merged["messages"])
        return merged

    def add_rag_items(self, state: Dict[str, Any], items: List[dict]) -> Dict[str, Any]:
        """Append semantic retrieval entries and prune to the configured limit."""

        merged = copy.deepcopy(state)
        merged.setdefault("rag_history", [])
        merged["rag_history"].extend(copy.deepcopy(items))
        merged["rag_history"] = self.context_budget.prune_rag_items(merged["rag_history"])
        return merged

    def update_summary(self, state: Dict[str, Any], summary: str) -> Dict[str, Any]:
        """Replace the summary while respecting the summary budget."""

        merged = copy.deepcopy(state)
        merged["summary"] = self.context_budget.prune_summary(summary)
        return merged

    def add_world_facts(self, state: Dict[str, Any], facts: List[dict]) -> Dict[str, Any]:
        """Append world facts and prune according to the budget."""

        merged = copy.deepcopy(state)
        merged.setdefault("world", [])
        merged["world"].extend(copy.deepcopy(facts))
        merged["world"] = self.context_budget.prune_world(merged["world"])
        return merged

    def prune_world(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prune world facts in the provided state."""

        merged = copy.deepcopy(state)
        merged["world"] = self.context_budget.prune_world(merged.get("world", []))
        return merged
