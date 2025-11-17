"""
L4 — State Adapter

Bridges orchestration code with deterministic state management. It applies
state patches, coordinates memory handling, and surfaces the current phase via
an embedded finite state machine.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

from l4_memory import MemoryManager
from l4_state import StateMachine
from l4_state import validate
from utils_patch_helpers import apply_patch
from utils_types import Phase, StatePatch


class StateAdapter:
    """Facade for deterministic state operations."""

    def __init__(self, memory_manager: MemoryManager | None = None, state_machine: StateMachine | None = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()
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
"""Layer 4 state management module consolidating state logic."""



from __future__ import annotations
import copy
from typing import Any, Dict

from l4_memory import MemoryManager
from utils_patch_helpers import apply_patch
from utils_types import Phase, StatePatch


class StateAdapter:
    """Facade for deterministic state operations."""

    def __init__(self, memory_manager: MemoryManager | None = None, state_machine: StateMachine | None = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()
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
"""
L4 — State Machine

Provides deterministic transitions between orchestration phases.
"""

from typing import Dict, List

from utils_types import Phase


class StateMachine:
    """Finite state machine enforcing legal transitions."""

    _TRANSITIONS = {
        Phase.INIT: {Phase.PLANNING, Phase.FAILED},
        Phase.PLANNING: {Phase.EXECUTING, Phase.FAILED},
        Phase.EXECUTING: {Phase.REVIEWING, Phase.FAILED},
        Phase.REVIEWING: {Phase.COMPLETE, Phase.PLANNING, Phase.FAILED},
        Phase.COMPLETE: set(),
        Phase.FAILED: set(),
    }

    def __init__(self, initial: Phase = Phase.INIT) -> None:
        self.phase = initial
        self._history: List[Phase] = [initial]

    def can_transition(self, target: Phase) -> bool:
        """Return True if the transition is legal."""

        return target in self._TRANSITIONS[self.phase]

    def transition(self, target: Phase) -> Phase:
        """Move to the target phase if legal, otherwise raise."""

        if not self.can_transition(target):
            raise ValueError(f"Illegal transition from {self.phase} to {target}")
        self.phase = target
        self._history.append(target)
        return self.phase

    def serialize(self) -> Dict[str, str]:
        """Return a serializable representation of the current phase."""

        return {"phase": self.phase.value}

    def on_enter_phase(self, phase: Phase) -> Dict[str, str]:
        return {"phase": phase.value}

    def history(self) -> List[str]:
        return [p.value for p in self._history]
"""
State Validation Utilities

Provides lightweight validation of orchestration state with warnings for
cross-field inconsistencies.
"""

from typing import Any, Dict, List


_EXPECTED_TYPES = {
    "messages": list,
    "rag_history": list,
    "summary": str,
    "world": list,
    "session": dict,
    "metadata": dict,
    "phase": str,
    "phase_metadata": dict,
}


def validate(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate the orchestration state for required keys and consistency."""

    missing: List[str] = []
    type_mismatch: List[str] = []
    cross_field_warnings: List[str] = []

    for field, expected_type in _EXPECTED_TYPES.items():
        if field not in state:
            missing.append(field)
            continue
        if not isinstance(state[field], expected_type):
            type_mismatch.append(field)

    if state.get("draft") is not None and len(state.get("messages", [])) == 0:
        cross_field_warnings.append("draft present but messages are empty")

    if state.get("qa_report") is not None and "plan" not in state:
        cross_field_warnings.append("qa_report present without plan")

    return {
        "missing": missing,
        "type_mismatch": type_mismatch,
        "cross_field_warnings": cross_field_warnings,
    }
"""
L4 — Memory Manager

Provides deterministic handling for episodic (messages) and semantic (summary,
retrieval history) memory buffers. The manager collaborates with the context
budget to enforce lightweight limits.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

from l4_memory import ContextBudget
from utils_types import Message
from l4_memory import normalize_world_facts


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
from __future__ import annotations

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
