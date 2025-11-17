"""
L4 — State Adapter (v10_9_clean)

Deterministic state management bridge between orchestration and storage.
Keeps 10_7 semantics (messages, rag_history, summary, world) and uses the
10_8+ budgeting architecture (ContextBudget + MemoryManager + FSM).
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

from utils_patch_helpers import apply_patch
from utils_types import Phase, StatePatch, Message

from ..core.services import ContextBudget
from ..core.world_model_contracts import normalize_world_facts
from .l4_state_machine import StateMachine
from .state_validation import validate


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

        # Canonicalize messages
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

        # Canonicalize RAG history
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

        # Apply structural budgets
        messages = self.context_budget.prune_messages(messages)
        rag_history = self.context_budget.prune_rag_items(rag_canonical)
        summary = self.context_budget.prune_summary(summary)
        world = self.context_budget.prune_world(normalize_world_facts(world))

        # Apply token-based budgets
        messages = self.context_budget.prune_messages_by_tokens(messages)
        rag_history = self.context_budget.prune_rag_items_by_tokens(rag_history)

        normalized["messages"] = messages
        normalized["rag_history"] = rag_history
        normalized["summary"] = summary
        normalized["world"] = world
        normalized["metadata"]["context_consistency"] = "unchecked"
        return normalized

    def add_messages(self, state: Dict[str, Any], new_messages: List[Message]) -> Dict[str, Any]:
        merged = copy.deepcopy(state)
        merged.setdefault("messages", [])
        merged["messages"].extend(copy.deepcopy(new_messages))
        merged["messages"] = self.context_budget.prune_messages(merged["messages"])
        return merged

    def add_rag_items(self, state: Dict[str, Any], items: List[dict]) -> Dict[str, Any]:
        merged = copy.deepcopy(state)
        merged.setdefault("rag_history", [])
        merged["rag_history"].extend(copy.deepcopy(items))
        merged["rag_history"] = self.context_budget.prune_rag_items(merged["rag_history"])
        return merged

    def update_summary(self, state: Dict[str, Any], summary: str) -> Dict[str, Any]:
        merged = copy.deepcopy(state)
        merged["summary"] = self.context_budget.prune_summary(summary)
        return merged

    def add_world_facts(self, state: Dict[str, Any], facts: List[dict]) -> Dict[str, Any]:
        merged = copy.deepcopy(state)
        merged.setdefault("world", [])
        merged["world"].extend(copy.deepcopy(facts))
        merged["world"] = self.context_budget.prune_world(merged["world"])
        return merged

    def prune_world(self, state: Dict[str, Any]) -> Dict[str, Any]:
        merged = copy.deepcopy(state)
        merged["world"] = self.context_budget.prune_world(merged.get("world", []))
        return merged


class StateAdapter:
    """Facade for deterministic state operations."""

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        state_machine: StateMachine | None = None,
        context_budget: ContextBudget | None = None,
    ) -> None:
        self.context_budget = context_budget or ContextBudget()
        self.memory_manager = memory_manager or MemoryManager(self.context_budget)
        self.state_machine = state_machine or StateMachine()

        self._state: Dict[str, Any] = {
            "messages": [],
            "rag_history": [],
            "summary": "",
            "world": [],
            "session": {},
            "metadata": {},
            "phase": self.state_machine.phase.value,
            "phase_metadata": {"phase": self.state_machine.phase.value},
        }

    @property
    def state(self) -> Dict[str, Any]:
        """Return a deep copy of the current state."""
        return copy.deepcopy(self._state)

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        """Apply a patch, reconcile memory budgets, and update cached state."""

        updated = apply_patch(self._state, patch)
        updated = self.memory_manager.reconcile_state(updated)

        # Sync FSM if the patch contains a phase directive
        phase_value = updated.get("phase")
        if phase_value is not None:
            phase = Phase(phase_value)
            if self.state_machine.phase != phase:
                self.state_machine.transition(phase)

        updated["phase"] = self.state_machine.phase.value
        metadata = self.state_machine.on_enter_phase(self.state_machine.phase)
        updated["phase_metadata"] = metadata
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validate(updated)

        self._state = updated
        return self.state

    def advance_phase(self, target: Phase) -> Phase:
        """Transition the FSM and mirror the phase into state."""
        new_phase = self.state_machine.transition(target)
        self._state["phase"] = new_phase.value
        return new_phase


__all__ = ["StateAdapter", "MemoryManager"]
