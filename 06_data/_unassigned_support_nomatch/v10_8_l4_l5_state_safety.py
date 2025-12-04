"""
V10.8 Consolidated Module: L4 L5 State Safety
Merged from 13 source files
"""

# Consolidated imports
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE
from l4_memory import MemoryManager
from l5_policy import (
from typing import Any, Dict
from typing import Any, Dict, List
from typing import Any, Dict, List, Optional, Set
from utils_patch_helpers import apply_patch
from utils_types import Message
from utils_types import Phase, StatePatch
from utils_types import StatePatch
import copy
import re


# ============================================================
# From v10_8_l4_memory.py
# ============================================================

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

# ============================================================
# From v10_8_l4_state.py
# ============================================================

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

# ============================================================
# From v10_8_l4_context_budget.py
# ============================================================

L4 — Context Budget Manager

Tracks and enforces lightweight budgeting constraints for context elements such
as messages, retrieved artifacts, and running summaries.
"""
from __future__ import annotations

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

# ============================================================
# From v10_8_l4_memory_manager.py
# ============================================================

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

# ============================================================
# From v10_8_l4_state_adapter.py
# ============================================================

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

# ============================================================
# From v10_8_l4_state_machine.py
# ============================================================

L4 — State Machine

Provides deterministic transitions between orchestration phases.
"""
from __future__ import annotations

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

# ============================================================
# From v10_8_l5_safety.py
# ============================================================

    PolicyEngine,
    SafetyMode,
    evaluate_routing_permissions,
    permissions as tool_permissions,
)
from prompt_system import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from utils_logger import SAFETY_LOG, log_safety_decision
from utils_types import StatePatch

EMAIL_TOKEN = "@"
PHONE_REGEX = re.compile(r"\d{3}-\d{3}-\d{4}")
BIAS_KEYWORDS = ["gender", "race", "ethnicity"]


def detect_pii(text: str) -> Dict[str, object]:
    """Deterministic PII detection based on simple patterns."""

    instances: List[str] = []
    if EMAIL_TOKEN in text:
        instances.append("email-like")
    phone_matches = PHONE_REGEX.findall(text)
    if phone_matches:
        instances.extend(phone_matches)

    return {"pii_found": bool(instances), "instances": instances}


def detect_bias(text: str) -> Dict[str, object]:
    """Deterministic bias detection using keyword scanning."""

    categories = [keyword for keyword in BIAS_KEYWORDS if keyword in text.lower()]
    return {"bias_found": bool(categories), "categories": categories}


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    def __init__(self) -> None:
        self.patterns: List[str] = DEFAULT_INJECTION_PATTERNS
        self.instructional_types: List[str] = INSTRUCTIONAL_INJECTION_ALL
        self.pattern_taxonomy: Dict[str, str] = {
            "override_system": "SYSTEM_OVERRIDE",
            "ignore_previous_instructions": "IGNORING_SYSTEM",
            "disable_safety": "DISABLE_SAFETY_PROTOCOLS",
            "run_arbitrary_code": "ARBITRARY_CODE_EXECUTION",
        }

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        matched_patterns: List[str] = []
        regex_matches: List[str] = []
        lower_content = content.lower()
        for pattern in self.patterns:
            normalized_pattern = pattern.replace("_", " ")
            if pattern in lower_content or normalized_pattern in lower_content:
                matches.append(pattern)
                matched_patterns.append(pattern)
            boundary_pattern = rf"\b{re.escape(normalized_pattern)}\b"
            if re.search(boundary_pattern, lower_content):
                regex_matches.append(pattern)

        taxonomy_tags = [self.pattern_taxonomy.get(pattern, "UNKNOWN_INJECTION") for pattern in matched_patterns]

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                    "matched_patterns": matched_patterns,
                    "instructional_types": self.instructional_types,
                    "regex_matches": regex_matches,
                    "taxonomy_tags": taxonomy_tags,
                }
            }
        )
        return patch


class ConstitutionalEngine:
    """Evaluate content against deterministic constitutional rules."""

    DEFAULT_RULES: List[Dict[str, str]] = [
        {"id": "no_harm", "pattern": "harm", "description": "Avoid promoting harm."},
        {"id": "no_malware", "pattern": "malware", "description": "Avoid malicious software."},
        {"id": "no_privacy", "pattern": "private data", "description": "Avoid collecting private data."},
        {
            "id": "restricted_biomed",
            "pattern": "restricted_biomed",
            "description": "Avoid restricted biomedical guidance.",
        },
        {
            "id": "political_advocacy",
            "pattern": "political_advocacy",
            "description": "Avoid political advocacy.",
        },
        {
            "id": "cybersecurity_unsafe",
            "pattern": "cybersecurity_unsafe",
            "description": "Avoid unsafe cybersecurity guidance.",
        },
    ]

    def __init__(self, rules: List[Dict[str, str]] | None = None) -> None:
        self.rules = rules or list(self.DEFAULT_RULES)

    def evaluate(self, content: str) -> StatePatch:
        """Return a StatePatch capturing any matched constitutional rules."""

        violations: List[Dict[str, str]] = []
        for rule in self.rules:
            if rule["pattern"].lower() in content.lower():
                violations.append(
                    {
                        "rule": rule["id"],
                        "description": rule["description"],
                        "matched": rule["pattern"],
                    }
                )

        patch: StatePatch = StatePatch(
            {
                "constitutional_evaluation": {
                    "violations": violations,
                    "compliant": len(violations) == 0,
                    "pii": detect_pii(content),
                    "bias": detect_bias(content),
                }
            }
        )
        return patch


class SafetyGateway:
    """Deterministic gateway that wraps safety evaluations into a patch."""

    def __init__(
        self,
        constitutional_engine: ConstitutionalEngine | None = None,
        policy_engine: PolicyEngine | None = None,
        injection_detector: InjectionDetector | None = None,
        safety_mode: SafetyMode = SafetyMode.BALANCED,
    ) -> None:
        self.constitutional_engine = constitutional_engine or ConstitutionalEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.injection_detector = injection_detector or InjectionDetector()
        self.safety_mode = safety_mode

    def evaluate(self, payload: Dict[str, Any]) -> StatePatch:
        """Perform safety checks on the provided payload and return a StatePatch."""

        content = str(payload.get("content", ""))
        intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
        routing_permissions = evaluate_routing_permissions(payload)

        constitutional_patch = self.constitutional_engine.evaluate(content)
        policy_patch = self.policy_engine.evaluate(intent)
        injection_patch = self.injection_detector.scan(content)

        constitutional_eval = constitutional_patch.get("constitutional_evaluation", {})
        policy_eval = policy_patch.get("policy_evaluation", {})
        injection_eval = injection_patch.get("injection_scan", {})

        violations = constitutional_eval.get("violations")
        is_injection = injection_eval.get("is_injection")
        policy_allowed = policy_eval.get("allowed")

        blocked = False
        if self.safety_mode == SafetyMode.STRICT:
            blocked = bool(violations) or bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.BALANCED:
            blocked = bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.PERMISSIVE:
            blocked = bool(is_injection)

        patch: StatePatch = StatePatch(
            {
                "safety_gateway": {
                    "constitutional": constitutional_patch.get("constitutional_evaluation", {}),
                    "policy": policy_patch.get("policy_evaluation", {}),
                    "injection": injection_patch.get("injection_scan", {}),
                    "tool_permissions": tool_permissions,
                    "routing_permissions": routing_permissions,
                    "taxonomy": {
                        "primitive_injection_patterns": DEFAULT_INJECTION_PATTERNS,
                        "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
                    },
                },
                "content_safety": {
                    "pii": constitutional_patch.get("constitutional_evaluation", {}).get("pii", {}),
                    "bias": constitutional_patch.get("constitutional_evaluation", {}).get("bias", {}),
                },
                "injection_safety": {
                    "prompt_shield": DEFAULT_SAFETY_OUTPUT_PROFILE.prompt_shield,
                    "data_instruction_separation": DEFAULT_SAFETY_OUTPUT_PROFILE.data_instruction_separation,
                    "constitutional_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.constitutional_guardrails_enabled,
                    "delegation_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.delegation_guardrails_enabled,
                    "adversarial_mode_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.adversarial_mode_enabled,
                },
                "status": "blocked" if blocked else "allowed",
                "mode": self.safety_mode.value,
            }
        )
        log_safety_decision(payload, patch)
        return patch

# ============================================================
# From v10_8_l5_policy.py
# ============================================================

class SafetyMode(str, Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def mode_defaults(mode: SafetyMode) -> Dict[str, bool]:
    if mode == SafetyMode.STRICT:
        return {"block_on_any": True}
    if mode == SafetyMode.BALANCED:
        return {"block_on_injection_or_policy": True}
    if mode == SafetyMode.PERMISSIVE:
        return {"block_on_injection_only": True}
    return {}


@dataclass
class SafetyRule:
    id: str
    description: str
    enabled: bool
    severity: str
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyRule:
    action: str
    allowed: bool
    reason: Optional[str]


@dataclass
class InjectionPattern:
    pattern: str
    enabled: bool
    tags: List[str] = field(default_factory=list)


@dataclass
class SafetyConfig:
    policy_rules: List[PolicyRule]
    injection_patterns: List[InjectionPattern]
    pii_enabled: bool
    bias_enabled: bool


DEFAULT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "override system",
    "disable safety",
    "run arbitrary code",
]

DEFAULT_POLICY_DENY_LIST = [
    "exfiltrate_data",
    "execute_code",
    "publish_unreviewed",
]


def load_default_safety_config() -> SafetyConfig:
    injection_patterns = [
        InjectionPattern(pattern=pattern, enabled=True, tags=["default", "injection"])
        for pattern in DEFAULT_INJECTION_PATTERNS
    ]
    policy_rules = [
        PolicyRule(action=action, allowed=False, reason="action blocked by policy")
        for action in DEFAULT_POLICY_DENY_LIST
    ]

    return SafetyConfig(
        policy_rules=policy_rules,
        injection_patterns=injection_patterns,
        pii_enabled=True,
        bias_enabled=True,
    )


permissions = {
    "drafting": {"allowed": True},
    "rag": {"allowed": True},
    "bullet": {"allowed": True},
    "qa": {"allowed": True},
}


PERMITTED_MODELS: Set[str] = {"gpt-4o", "gpt-4o-mini"}
PERMITTED_ENDPOINTS: Set[str] = {"default", "fast"}


def evaluate_routing_permissions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return metadata describing routing allowance for the payload."""

    model = str(payload.get("model", "")).strip()
    endpoint = str(payload.get("endpoint", "")).strip()

    return {
        "model": model or None,
        "endpoint": endpoint or None,
        "model_allowed": bool(model) and model in PERMITTED_MODELS,
        "endpoint_allowed": bool(endpoint) and endpoint in PERMITTED_ENDPOINTS,
    }


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()

    def evaluate(self, intent: Dict[str, str] | None = None) -> StatePatch:
        """Return a StatePatch describing policy allowances for the given intent."""

        intent = intent or {}
        action = intent.get("action", "unspecified")
        rule = next(
            (policy_rule for policy_rule in self._config.policy_rules if policy_rule.action == action),
            PolicyRule(action=action, allowed=True, reason=None),
        )
        allowed = rule.allowed

        patch: StatePatch = StatePatch(
            {
                "policy_evaluation": {
                    "action": action,
                    "allowed": allowed,
                    "denied_reason": rule.reason if not allowed else None,
                    "denied_actions": [policy_rule.action for policy_rule in self._config.policy_rules if not policy_rule.allowed],
                }
            }
        )
        return patch

# ============================================================
# From v10_8_l5_constitutional_engine.py
# ============================================================

L5 — Constitutional Engine

Responsibilities:
    • Apply high-level constitutional rules to evaluate agent behavior.
    • Provide interpretations and guidance to the safety gateway for enforcement.
    • Maintain rule sets independent from orchestration or execution logic.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Dict, List

from utils_types import StatePatch
from l5_safety import detect_bias, detect_pii


class ConstitutionalEngine:
    """Evaluate content against deterministic constitutional rules."""

    DEFAULT_RULES: List[Dict[str, str]] = [
        {"id": "no_harm", "pattern": "harm", "description": "Avoid promoting harm."},
        {"id": "no_malware", "pattern": "malware", "description": "Avoid malicious software."},
        {"id": "no_privacy", "pattern": "private data", "description": "Avoid collecting private data."},
        {
            "id": "restricted_biomed",
            "pattern": "restricted_biomed",
            "description": "Avoid restricted biomedical guidance.",
        },
        {
            "id": "political_advocacy",
            "pattern": "political_advocacy",
            "description": "Avoid political advocacy.",
        },
        {
            "id": "cybersecurity_unsafe",
            "pattern": "cybersecurity_unsafe",
            "description": "Avoid unsafe cybersecurity guidance.",
        },
    ]

    def __init__(self, rules: List[Dict[str, str]] | None = None) -> None:
        self.rules = rules or list(self.DEFAULT_RULES)

    def evaluate(self, content: str) -> StatePatch:
        """Return a StatePatch capturing any matched constitutional rules."""

        violations: List[Dict[str, str]] = []
        for rule in self.rules:
            if rule["pattern"].lower() in content.lower():
                violations.append({
                    "rule": rule["id"],
                    "description": rule["description"],
                    "matched": rule["pattern"],
                })

        patch: StatePatch = StatePatch(
            {
                "constitutional_evaluation": {
                    "violations": violations,
                    "compliant": len(violations) == 0,
                    "pii": detect_pii(content),
                    "bias": detect_bias(content),
                }
            }
        )
        return patch

# ============================================================
# From v10_8_l5_content_safety.py
# ============================================================

L5 — Content Safety

Deterministic stub evaluators for PII and bias detection.
"""
from __future__ import annotations

import re
from typing import Dict, List


EMAIL_TOKEN = "@"
PHONE_REGEX = re.compile(r"\d{3}-\d{3}-\d{4}")
BIAS_KEYWORDS = ["gender", "race", "ethnicity"]


def detect_pii(text: str) -> Dict[str, object]:
    """Deterministic PII detection based on simple patterns."""

    instances: List[str] = []
    if EMAIL_TOKEN in text:
        instances.append("email-like")
    phone_matches = PHONE_REGEX.findall(text)
    if phone_matches:
        instances.extend(phone_matches)

    return {"pii_found": bool(instances), "instances": instances}


def detect_bias(text: str) -> Dict[str, object]:
    """Deterministic bias detection using keyword scanning."""

    categories = [keyword for keyword in BIAS_KEYWORDS if keyword in text.lower()]
    return {"bias_found": bool(categories), "categories": categories}

# ============================================================
# From v10_8_l5_injection_detector.py
# ============================================================

L5 — Injection Detector

Responsibilities:
    • Detect prompt injection or malicious input patterns before execution.
    • Provide signals to the safety gateway and policy engine for enforcement.
    • Operate independently from orchestration flow while integrating with monitoring.

Produces StatePatch outputs only.
"""
from __future__ import annotations

import re
from typing import Dict, List

from prompt_system import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from l5_policy import InjectionPattern, SafetyConfig, load_default_safety_config
from utils_types import StatePatch


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()
        self.patterns: List[str] = DEFAULT_INJECTION_PATTERNS
        self.instructional_types: List[str] = INSTRUCTIONAL_INJECTION_ALL
        self.pattern_taxonomy: Dict[str, str] = {
            "override_system": "SYSTEM_OVERRIDE",
            "ignore_previous_instructions": "IGNORING_SYSTEM",
            "disable_safety": "DISABLE_SAFETY_PROTOCOLS",
            "run_arbitrary_code": "ARBITRARY_CODE_EXECUTION",
        }

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        matched_patterns: List[str] = []
        regex_matches: List[str] = []
        lower_content = content.lower()
        for pattern in self.patterns:
            normalized_pattern = pattern.replace("_", " ")
            if pattern in lower_content or normalized_pattern in lower_content:
                matches.append(pattern)
                matched_patterns.append(pattern)
            boundary_pattern = rf"\b{re.escape(normalized_pattern)}\b"
            if re.search(boundary_pattern, lower_content):
                regex_matches.append(pattern)

        taxonomy_tags = [self.pattern_taxonomy.get(pattern, "UNKNOWN_INJECTION") for pattern in matched_patterns]

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                    "matched_patterns": matched_patterns,
                    "instructional_types": self.instructional_types,
                    "regex_matches": regex_matches,
                    "taxonomy_tags": taxonomy_tags,
                }
            }
        )
        return patch

# ============================================================
# From v10_8_l5_policy_engine.py
# ============================================================

L5 — Policy Engine

Responsibilities:
    • Enforce organizational policies and guardrails on agent activities.
    • Translate policy decisions into actionable constraints for orchestration and execution layers.
    • Provide auditable policy evaluations for compliance and safety reviews.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Dict, List

from l5_policy import PolicyRule, SafetyConfig, load_default_safety_config
from utils_types import StatePatch


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()

    def evaluate(self, intent: Dict[str, str] | None = None) -> StatePatch:
        """Return a StatePatch describing policy allowances for the given intent."""

        intent = intent or {}
        action = intent.get("action", "unspecified")
        rule = next(
            (policy_rule for policy_rule in self._config.policy_rules if policy_rule.action == action),
            PolicyRule(action=action, allowed=True, reason=None),
        )
        allowed = rule.allowed

        patch: StatePatch = StatePatch(
            {
                "policy_evaluation": {
                    "action": action,
                    "allowed": allowed,
                    "denied_reason": rule.reason if not allowed else None,
                    "denied_actions": [policy_rule.action for policy_rule in self._config.policy_rules if not policy_rule.allowed],
                }
            }
        )
        return patch

# ============================================================
# From v10_8_l5_safety_gateway.py
# ============================================================

L5 — Safety Gateway

Responsibilities:
    • Serve as the primary enforcement point for safety and policy checks.
    • Evaluate intents and outputs from lower layers before execution or release.
    • Route escalations to constitutional and policy engines without duplicating their logic.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Any, Dict

from injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE
from l5_safety import ConstitutionalEngine
from l5_safety import InjectionDetector
from l5_policy import PolicyEngine
from prompt_system import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from l5_policy import evaluate_routing_permissions
from l5_policy import SafetyMode
from l5_policy import permissions as tool_permissions
from l5_safety import log_safety_decision
from utils_types import StatePatch


class SafetyGateway:
    """Deterministic gateway that wraps safety evaluations into a patch."""

    def __init__(
        self,
        constitutional_engine: ConstitutionalEngine | None = None,
        policy_engine: PolicyEngine | None = None,
        injection_detector: InjectionDetector | None = None,
        safety_mode: SafetyMode = SafetyMode.BALANCED,
    ) -> None:
        self.constitutional_engine = constitutional_engine or ConstitutionalEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.injection_detector = injection_detector or InjectionDetector()
        self.safety_mode = safety_mode

    def evaluate(self, payload: Dict[str, Any]) -> StatePatch:
        """Perform safety checks on the provided payload and return a StatePatch."""

        content = str(payload.get("content", ""))
        intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
        routing_permissions = evaluate_routing_permissions(payload)

        constitutional_patch = self.constitutional_engine.evaluate(content)
        policy_patch = self.policy_engine.evaluate(intent)
        injection_patch = self.injection_detector.scan(content)

        constitutional_eval = constitutional_patch.get("constitutional_evaluation", {})
        policy_eval = policy_patch.get("policy_evaluation", {})
        injection_eval = injection_patch.get("injection_scan", {})

        violations = constitutional_eval.get("violations")
        is_injection = injection_eval.get("is_injection")
        policy_allowed = policy_eval.get("allowed")

        blocked = False
        if self.safety_mode == SafetyMode.STRICT:
            blocked = bool(violations) or bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.BALANCED:
            blocked = bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.PERMISSIVE:
            blocked = bool(is_injection)

        patch: StatePatch = StatePatch(
            {
                "safety_gateway": {
                    "constitutional": constitutional_patch.get("constitutional_evaluation", {}),
                    "policy": policy_patch.get("policy_evaluation", {}),
                    "injection": injection_patch.get("injection_scan", {}),
                    "tool_permissions": tool_permissions,
                    "routing_permissions": routing_permissions,
                    "taxonomy": {
                        "primitive_injection_patterns": DEFAULT_INJECTION_PATTERNS,
                        "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
                    },
                },
                "content_safety": {
                    "pii": constitutional_patch.get("constitutional_evaluation", {}).get("pii", {}),
                    "bias": constitutional_patch.get("constitutional_evaluation", {}).get("bias", {}),
                },
                "injection_safety": {
                    "prompt_shield": DEFAULT_SAFETY_OUTPUT_PROFILE.prompt_shield,
                    "data_instruction_separation": DEFAULT_SAFETY_OUTPUT_PROFILE.data_instruction_separation,
                    "constitutional_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.constitutional_guardrails_enabled,
                    "delegation_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.delegation_guardrails_enabled,
                    "adversarial_mode_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.adversarial_mode_enabled,
                },
                "status": "blocked" if blocked else "allowed",
                "mode": self.safety_mode.value,
            }
        )
        log_safety_decision(payload, patch)
        return patch
