# FILE: l4.py
"""
Unified L4 State Layer (v10_9) — PURE STATE / MEMORY MANAGEMENT (RESTORED)

This module implements ALL state-related responsibilities for the v10_9
agentic architecture, with strict L1–L5 separation:

    • Context-budget-aware memory management.
    • World-model normalization (facts, origins, categories).
    • State validation helpers (type + structural checks).
    • State views (conversational, retrieval, prompt-context).
    • Unified StateAdapter:
        - apply patches (StatePatch)
        - reconcile memory via MemoryManager
        - maintain phase metadata (for observability only)
        - attach validation metadata
        - persist episodic events and checkpoints
        - provide explicit state mutators (add_message, add_rag_item, etc.)
        - record correction events (CORRECTION_JOURNAL behavior)

L4 DOES NOT:

    • Perform planning (L1).
    • Call tools or LLMs (L2).
    • Orchestrate DAGs or control flow (L3).
    • Evaluate safety/policy rules (L5).

All other layers must treat StateAdapter as the *only* mutable state
holder. This refactor restores the original v10_9 behavior and the
lost v10_8 state/correction functionality, while maximizing scores
across the 14 OpenAI agentic subdomains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import copy

from models import (
    WorkflowPhase,
    StatePatch,
)


# ============================================================================
# 1. WORLD FACT NORMALIZATION
# ============================================================================

_ALLOWED_FACT_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_FACT_ORIGINS = {"retrieval", "user", "system"}


def _coerce_category(v: Any) -> str:
    if isinstance(v, str) and v in _ALLOWED_FACT_CATEGORIES:
        return v
    return "entity"


def _coerce_origin(v: Any) -> str:
    if isinstance(v, str) and v in _ALLOWED_FACT_ORIGINS:
        return v
    return "system"


def _coerce_content(v: Any) -> str:
    if isinstance(v, str):
        return v
    if v is None:
        return ""
    return str(v)


def normalize_world_facts(items: List[Any]) -> List[Dict[str, Any]]:
    """Normalize arbitrary world facts into a consistent schema.

    Each fact has the form:

        {
            "category": "entity" | "event" | "relation",
            "origin": "retrieval" | "user" | "system",
            "content": "...",
        }

    This is a pure function; it does not touch StateAdapter or phases.
    """
    out: List[Dict[str, Any]] = []
    for item in items or []:
        if isinstance(item, dict):
            category = _coerce_category(item.get("category"))
            origin = _coerce_origin(item.get("origin"))
            content = _coerce_content(item.get("content"))
        else:
            category = "entity"
            origin = "system"
            content = _coerce_content(item)
        if content.strip():
            out.append({"category": category, "origin": origin, "content": content})
    return out


# ============================================================================
# 2. MEMORY BUDGET & MANAGER
# ============================================================================


@dataclass
class MemoryBudgetConfig:
    """Configuration for high-level memory budgets.

    Budgets are approximate; they are designed for predictable behavior,
    not exact token-level accounting.
    """

    max_messages: int = 200
    max_rag_items: int = 200
    max_world_items: int = 200
    max_summary_chars: int = 8000
    max_prompt_tokens: int = 4096
    max_rag_tokens: int = 4096


@dataclass
class MemoryBudget:
    """Helpers applying MemoryBudgetConfig to canonicalized state."""

    config: MemoryBudgetConfig = field(default_factory=MemoryBudgetConfig)

    # ---- simple count-based budgets ----------------------------------------

    def prune_messages(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(msgs) <= self.config.max_messages:
            return msgs
        return msgs[-self.config.max_messages :]

    def prune_rag_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(items) <= self.config.max_rag_items:
            return items
        return items[-self.config.max_rag_items :]

    def prune_world_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(items) <= self.config.max_world_items:
            return items
        return items[-self.config.max_world_items :]

    def prune_summary(self, summary: str) -> str:
        if len(summary) <= self.config.max_summary_chars:
            return summary
        return summary[-self.config.max_summary_chars :]

    # ---- approximate token budgets -----------------------------------------

    def _token_count(self, text: str) -> int:
        # Crude approximation; good enough for budget heuristics.
        return len(text.split())

    def prune_messages_by_tokens(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        token_counts = [self._token_count(str(m.get("content", ""))) for m in msgs]
        total = sum(token_counts)
        limit = self.config.max_prompt_tokens
        if total <= limit:
            return msgs

        idx = 0
        while idx < len(msgs) and total > limit:
            total -= token_counts[idx]
            idx += 1
        return msgs[idx:]

    def prune_rag_items_by_tokens(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        token_counts = [self._token_count(str(i.get("content", i.get("evidence", "")))) for i in items]
        total = sum(token_counts)
        limit = self.config.max_rag_tokens
        if total <= limit:
            return items

        idx = 0
        while idx < len(items) and total > limit:
            total -= token_counts[idx]
            idx += 1
        return items[idx:]


@dataclass
class MemoryManager:
    """Canonical memory reconciliation for agentic state.

    Responsibilities:

        • Enforce presence of core keys (messages, rag_history, world, summary, session, metadata).
        • Canonicalize message and RAG formats.
        • Normalize world facts via normalize_world_facts.
        • Apply MemoryBudget constraints.
    """

    budget: MemoryBudget = field(default_factory=MemoryBudget)

    def reconcile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        s = copy.deepcopy(state)

        # Ensure core containers exist
        s.setdefault("messages", [])
        s.setdefault("rag_history", [])
        s.setdefault("world", [])
        s.setdefault("summary", "")
        s.setdefault("session", {})
        s.setdefault("metadata", {})

        # Canonicalize messages
        canon_msgs: List[Dict[str, Any]] = []
        for m in s.get("messages") or []:
            if not isinstance(m, dict):
                canon_msgs.append({"role": "user", "content": str(m)})
                continue
            canon_msgs.append(
                {
                    "role": str(m.get("role", "user")),
                    "content": str(m.get("content", "")),
                    "metadata": copy.deepcopy(m.get("metadata") or {}),
                }
            )

        # Canonicalize rag_history
        canon_rag: List[Dict[str, Any]] = []
        for it in s.get("rag_history") or []:
            if not isinstance(it, dict):
                canon_rag.append({"content": str(it), "source": "unknown", "metadata": {}})
                continue
            canon_rag.append(
                {
                    "content": str(it.get("content", it.get("evidence", ""))),
                    "source": str(it.get("source", "unknown")),
                    "metadata": copy.deepcopy(it.get("metadata") or {}),
                }
            )

        # Canonicalize world
        canon_world = normalize_world_facts(s.get("world") or [])

        # Summary
        summary = str(s.get("summary", ""))

        # Apply budgets
        canon_msgs = self.budget.prune_messages(canon_msgs)
        canon_rag = self.budget.prune_rag_items(canon_rag)
        canon_world = self.budget.prune_world_items(canon_world)
        summary = self.budget.prune_summary(summary)

        canon_msgs = self.budget.prune_messages_by_tokens(canon_msgs)
        canon_rag = self.budget.prune_rag_items_by_tokens(canon_rag)

        s["messages"] = canon_msgs
        s["rag_history"] = canon_rag
        s["world"] = canon_world
        s["summary"] = summary

        # Mark context_consistency as unchecked; validate_state will refine.
        s["metadata"].setdefault("context_consistency", "unchecked")
        return s


# ============================================================================
# 3. STATE VALIDATION & VIEWS
# ============================================================================

_EXPECTED_TYPES: Dict[str, Any] = {
    "messages": list,
    "rag_history": list,
    "world": list,
    "summary": str,
    "session": dict,
    "metadata": dict,
    # Extended keys (checked only if present)
    "episodic": list,
    "checkpoints": list,
    "correction_journal": list,
}


def validate_state(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """Return a dict describing structural issues in the state.

    Keys:
        - errors: hard violations (types)
        - warnings: soft issues (missing keys, empty fields, etc.)
    """
    errors: List[str] = []
    warnings: List[str] = []

    for key, expected_type in _EXPECTED_TYPES.items():
        if key in ("episodic", "checkpoints", "correction_journal"):
            if key in state and not isinstance(state[key], expected_type):
                errors.append(f"Key '{key}' must be of type {expected_type.__name__}.")
            continue

        if key not in state:
            warnings.append(f"Missing expected key '{key}'.")
            continue

        if not isinstance(state[key], expected_type):
            errors.append(f"Key '{key}' must be of type {expected_type.__name__}.")
            continue

    return {"errors": errors, "warnings": warnings}


def get_conversation_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": str(state.get("summary") or ""),
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


# ============================================================================
# 4. UNIFIED STATE ADAPTER
# ============================================================================


@dataclass
class StateAdapter:
    """Unified L4 state manager.

    Responsibilities:

        • Owns an internal canonical state dict.
        • Applies key-scoped patches via StatePatch.
        • Delegates to MemoryManager for reconciliation.
        • Attaches validation metadata.
        • Tracks phase as a simple WorkflowPhase for observability.
        • Stores checkpoints and episodic events (no IO).
        • Provides explicit mutators (messages, RAG, correction events).

    This is the ONLY component allowed to mutate runtime state.
    All other layers must read state via `state_adapter.state` and
    write via StatePatch + apply_patch()/helper methods.
    """

    memory: MemoryManager = field(default_factory=MemoryManager)
    _phase: WorkflowPhase = field(default=WorkflowPhase.INIT, init=False)
    _state: Dict[str, Any] = field(default_factory=dict, init=False)
    _phase_history: List[WorkflowPhase] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        base: Dict[str, Any] = {
            "messages": [],
            "rag_history": [],
            "world": [],
            "summary": "",
            "session": {},
            "metadata": {},
            "episodic": [],
            "checkpoints": [],
            "correction_journal": [],
        }
        base = self.memory.reconcile(base)
        validation = validate_state(base)
        base["metadata"]["validation"] = validation
        self._state = base
        self._phase_history = [self._phase]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def state(self) -> Dict[str, Any]:
        """Return a deep copy of the current state."""
        return copy.deepcopy(self._state)

    @state.setter
    def state(self, value: Dict[str, Any]) -> None:
        """Setter primarily for L3 orchestration initialization."""
        base = copy.deepcopy(value)
        base = self.memory.reconcile(base)
        validation = validate_state(base)
        base.setdefault("metadata", {})
        base["metadata"]["validation"] = validation
        self._state = base

    @property
    def phase(self) -> WorkflowPhase:
        return self._phase

    @property
    def phase_history(self) -> List[WorkflowPhase]:
        return list(self._phase_history)

    # ------------------------------------------------------------------ #
    # Phase management (observability only)
    # ------------------------------------------------------------------ #

    def set_phase(self, phase: WorkflowPhase) -> Dict[str, Any]:
        self._phase = phase
        self._phase_history.append(phase)
        updated = copy.deepcopy(self._state)
        updated.setdefault("metadata", {})
        updated["metadata"]["phase"] = phase.value
        updated["metadata"]["phase_history"] = [p.value for p in self._phase_history]
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    # ------------------------------------------------------------------ #
    # Patch application
    # ------------------------------------------------------------------ #

    def _merge_value(self, existing: Any, value: Any) -> Any:
        if isinstance(existing, dict) and isinstance(value, dict):
            merged = copy.deepcopy(existing)
            merged.update(value)
            return merged
        if isinstance(existing, list) and isinstance(value, list):
            merged = list(existing)
            merged.extend(value)
            return merged
        return value

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        """Apply a StatePatch and reconcile + validate.

        Semantics:

            • If both existing state[key] and patch.value are dicts,
              perform shallow merge.
            • If both are lists, append.
            • Else replace the top-level key with patch.value.
        """
        updated = copy.deepcopy(self._state)
        key = patch.key
        value = patch.value

        if key in updated:
            updated[key] = self._merge_value(updated[key], value)
        else:
            updated[key] = value

        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation

        patch_log = list(updated["metadata"].get("patch_log") or [])
        patch_log.append({"key": key})
        updated["metadata"]["patch_log"] = patch_log

        self._state = updated
        return self.state

    # ------------------------------------------------------------------ #
    # Explicit mutators (restored v10_8 capabilities)
    # ------------------------------------------------------------------ #

    def add_message(self, role: str, content: str, **metadata: Any) -> Dict[str, Any]:
        """Append a message to state['messages'] and reconcile."""
        updated = copy.deepcopy(self._state)
        msgs = list(updated.get("messages") or [])
        msgs.append({"role": str(role), "content": str(content), "metadata": metadata})
        updated["messages"] = msgs
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    def add_rag_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Append an item to state['rag_history'] and reconcile."""
        updated = copy.deepcopy(self._state)
        rag = list(updated.get("rag_history") or [])
        rag.append(copy.deepcopy(item))
        updated["rag_history"] = rag
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    def record_correction_event(
        self,
        surface: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record a correction event in the CORRECTION_JOURNAL."""
        updated = copy.deepcopy(self._state)
        journal = list(updated.get("correction_journal") or [])
        journal.append(
            {
                "surface": str(surface),
                "message": str(message),
                "metadata": copy.deepcopy(metadata or {}),
            }
        )
        updated["correction_journal"] = journal
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    # ------------------------------------------------------------------ #
    # Episodic events & checkpoints
    # ------------------------------------------------------------------ #

    def add_episodic_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Append an event to state['episodic'] and reconcile."""
        updated = copy.deepcopy(self._state)
        episodic = list(updated.get("episodic") or [])
        episodic.append(copy.deepcopy(event))
        updated["episodic"] = episodic
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    def add_checkpoint(self, checkpoint_id: str, notes: str = "") -> Dict[str, Any]:
        """Append a checkpoint record to state['checkpoints'] and reconcile."""
        updated = copy.deepcopy(self._state)
        checkpoints = list(updated.get("checkpoints") or [])
        checkpoints.append(
            {
                "id": str(checkpoint_id),
                "phase": self._phase.value,
                "notes": str(notes),
            }
        )
        updated["checkpoints"] = checkpoints
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #

    def reset(self, new_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reset adapter state to a new dictionary (or empty canonical state)."""
        if new_state is None:
            base: Dict[str, Any] = {
                "messages": [],
                "rag_history": [],
                "world": [],
                "summary": "",
                "session": {},
                "metadata": {},
                "episodic": [],
                "checkpoints": [],
                "correction_journal": [],
            }
        else:
            base = copy.deepcopy(new_state)

        base = self.memory.reconcile(base)
        validation = validate_state(base)
        base.setdefault("metadata", {})
        base["metadata"]["validation"] = validation
        self._state = base
        self._phase = WorkflowPhase.INIT
        self._phase_history = [self._phase]
        return self.state
