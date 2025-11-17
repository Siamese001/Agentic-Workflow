"""Layer 4 memory management module consolidating memory components."""



from __future__ import annotations
import copy
from typing import Any, Dict, List

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
            message_copy["role"] = str(message_copy.get("role", ""))
            message_copy["content"] = str(message_copy.get("content", ""))
            canonical_messages.append(message_copy)

        messages = canonical_messages

        rag_canonical: List[dict] = []
        for item in rag_history:
            if isinstance(item, dict):
                item_copy: Dict[str, Any] = copy.deepcopy(item)
            else:
                item_copy = {"query": str(item), "evidence": []}
            item_copy["query"] = str(item_copy.get("query", ""))
            evidence = item_copy.get("evidence", [])
            if not isinstance(evidence, list):
                evidence = [evidence]
            item_copy["evidence"] = evidence
            rag_canonical.append(item_copy)

        messages = self.context_budget.prune_messages(messages)
        rag_history = self.context_budget.prune_rag_items(rag_canonical)
        summary = self.context_budget.prune_summary(summary)
        world = self.context_budget.prune_world(normalize_world_facts(world))

        messages = self.context_budget.prune_messages_by_tokens(messages)
        rag_history = self.context_budget.prune_rag_items_by_tokens(rag_history)

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
"""
L4 — Context Budget Manager

Tracks and enforces lightweight budgeting constraints for context elements such
as messages, retrieved artifacts, and running summaries.
"""

from typing import List

from utils_types import BudgetConfig, Message


class ContextBudget:
    """Applies heuristic limits to contextual elements."""

    def __init__(self, config: BudgetConfig | None = None) -> None:
        self.config = config or BudgetConfig()
        self.pruning_rules = {
            "messages": "preserve order and trim to max_messages",
            "rag_history": "preserve order and trim to max_rag_items",
            "world": "preserve order and trim to max_world_items",
            "summary": "trim to max_summary_chars",
        }

    def prune_messages(self, messages: List[Message]) -> List[Message]:
        """Trim messages to the configured maximum count while preserving order."""

        if len(messages) <= self.config.max_messages:
            return messages
        return messages[-self.config.max_messages :]

    def prune_rag_items(self, items: List[dict]) -> List[dict]:
        """Trim retrieval items to the configured limit."""

        if len(items) <= self.config.max_rag_items:
            return items
        return items[-self.config.max_rag_items :]

    def prune_messages_by_tokens(self, messages: List[Message]) -> List[Message]:
        """Trim messages by approximate token budget while preserving order."""

        token_counts = [len(str(message.get("content", "")).split()) for message in messages]
        total_tokens = sum(token_counts)

        if total_tokens <= self.config.max_prompt_tokens:
            return messages

        start_index = 0
        while start_index < len(messages) and total_tokens > self.config.max_prompt_tokens:
            total_tokens -= token_counts[start_index]
            start_index += 1

        return messages[start_index:]

    def prune_rag_items_by_tokens(self, items: List[dict]) -> List[dict]:
        """Trim retrieval items by approximate token budget while preserving order."""

        token_counts = [len(str(item.get("evidence", "")).split()) for item in items]
        total_tokens = sum(token_counts)

        if total_tokens <= self.config.max_retrieval_tokens:
            return items

        start_index = 0
        while start_index < len(items) and total_tokens > self.config.max_retrieval_tokens:
            total_tokens -= token_counts[start_index]
            start_index += 1

        return items[start_index:]

    def prune_world(self, items: List[dict]) -> List[dict]:
        """Trim world-model facts to the configured limit."""

        if len(items) <= self.config.max_world_items:
            return items
        return items[-self.config.max_world_items :]

    def prune_summary(self, summary: str) -> str:
        """Constrain the summary to a maximum character budget."""

        if len(summary) <= self.config.max_summary_chars:
            return summary
        return summary[-self.config.max_summary_chars :]

from typing import Any, Dict
import copy


def get_conversational_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages", []) or []),
        "summary": state.get("summary", "") or "",
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }


def get_evidence_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }


def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages", []) or []),
        "summary": state.get("summary", "") or "",
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }
"""
World Model Contracts

Defines deterministic schemas for world-model facts and helpers to normalize
incoming data into canonical structures.
"""

from typing import Any, Dict, List

_ALLOWED_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_ORIGINS = {"retrieval", "user", "system"}


def _coerce_category(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_CATEGORIES:
        return value
    return "entity"


def _coerce_origin(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_ORIGINS:
        return value
    return "system"


def _coerce_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    return "" if value is None else str(value)


def normalize_world_facts(facts: List[dict]) -> List[Dict[str, Any]]:
    """Normalize a list of world facts into the deterministic schema."""

    normalized: List[Dict[str, Any]] = []
    for fact in facts or []:
        if isinstance(fact, dict):
            fact_copy: Dict[str, Any] = dict(fact)
        else:
            fact_copy = {"content": _coerce_content(fact)}

        fact_copy["category"] = _coerce_category(fact_copy.get("category"))
        fact_copy["origin"] = _coerce_origin(fact_copy.get("origin"))
        fact_copy["content"] = _coerce_content(fact_copy.get("content"))
        normalized.append(fact_copy)

    return normalized
