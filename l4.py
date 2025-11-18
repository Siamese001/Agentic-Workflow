# FILE: l4.py
"""
Unified L4 State Layer (v10_9) — FULL AGENTIC IMPLEMENTATION (REFINED)

This module implements ALL state-related responsibilities for the v10_9
agentic architecture, with feature parity to the richer state handling
in earlier versions, but rewritten cleanly with no legacy dependencies.

Responsibilities:
    • Context-budget aware MemoryManager
    • World-model normalization (facts, origins, categories)
    • State validation helpers (type + structural checks)
    • State views (conversational, retrieval, prompt-context)
    • Global StateAdapter:
        - apply patches (StatePatch)
        - reconcile memory
        - maintain phase & phase history
        - attach validation metadata

Pure state management:
    • NO cognition (L1)
    • NO execution (L2)
    • NO orchestration logic (L3)
    • NO safety/policy decisions (L5)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, MutableMapping, Optional

from models import StatePatch, WorkflowPhase


# ============================================================================
# 1. WORLD-MODEL NORMALIZATION
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
    """
    Normalize arbitrary world facts into a consistent schema:

        {"category": "entity|event|relation",
         "origin": "retrieval|user|system",
         "content": "text"}
    """
    out: List[Dict[str, Any]] = []
    for item in items or []:
        if isinstance(item, dict):
            d = dict(item)
        else:
            d = {"content": item}
        d["category"] = _coerce_category(d.get("category"))
        d["origin"] = _coerce_origin(d.get("origin"))
        d["content"] = _coerce_content(d.get("content"))
        out.append(d)
    return out


# ============================================================================
# 2. CONTEXT BUDGET & MEMORY MANAGEMENT
# ============================================================================


@dataclass
class BudgetConfig:
    """
    Soft context-budget configuration.
    These limits are deliberately conservative and can be tuned.
    """

    max_messages: int = 40
    max_rag_items: int = 50
    max_world_items: int = 50
    max_summary_chars: int = 4000
    max_prompt_tokens: int = 8000
    max_retrieval_tokens: int = 8000


class ContextBudget:
    """
    Purely deterministic, soft context budget. There is no tokenization
    dependency; we approximate tokens via whitespace splits.
    """

    def __init__(self, config: Optional[BudgetConfig] = None) -> None:
        self.config = config or BudgetConfig()

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

    def prune_messages_by_tokens(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Approximate token budget for prompts: compute simple token counts,
        then drop from the front until we're under the limit.
        """
        token_counts = [len(str(m.get("content", "")).split()) for m in msgs]
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
        token_counts = [len(str(it.get("evidence", "")).split()) for it in items]
        total = sum(token_counts)
        limit = self.config.max_retrieval_tokens
        if total <= limit:
            return items

        idx = 0
        while idx < len(items) and total > limit:
            total -= token_counts[idx]
            idx += 1
        return items[idx:]


class MemoryManager:
    """
    Centralized memory & state reconciler.

    Responsibilities:
        • canonicalize messages (role, content)
        • canonicalize RAG history
        • canonicalize world facts
        • enforce context budgets (messages, rag, world, summary)
        • annotate state with context-consistency metadata
    """

    def __init__(self, budget: Optional[ContextBudget] = None) -> None:
        self.budget = budget or ContextBudget()

    def reconcile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        s = copy.deepcopy(state)
        s.setdefault("metadata", {})

        messages = s.get("messages") or []
        rag_history = s.get("rag_history") or []
        world = s.get("world") or []
        summary = s.get("summary", "") or ""

        # Canonicalize messages
        canon_msgs: List[Dict[str, Any]] = []
        for m in messages:
            if isinstance(m, dict):
                mm = copy.deepcopy(m)
            else:
                mm = {"role": "unknown", "content": str(m)}
            mm["role"] = str(mm.get("role", ""))
            mm["content"] = str(mm.get("content", ""))
            canon_msgs.append(mm)

        # Canonicalize RAG history
        canon_rag: List[Dict[str, Any]] = []
        for item in rag_history:
            if isinstance(item, dict):
                it = copy.deepcopy(item)
            else:
                it = {"query": str(item), "evidence": []}
            it["query"] = str(it.get("query", ""))
            ev = it.get("evidence", [])
            if not isinstance(ev, list):
                ev = [ev]
            it["evidence"] = ev
            canon_rag.append(it)

        # Canonicalize world
        canon_world = normalize_world_facts(world)

        # Apply simple budgets
        canon_msgs = self.budget.prune_messages(canon_msgs)
        canon_rag = self.budget.prune_rag_items(canon_rag)
        canon_world = self.budget.prune_world_items(canon_world)
        summary = self.budget.prune_summary(summary)

        # Apply token-based budgets
        canon_msgs = self.budget.prune_messages_by_tokens(canon_msgs)
        canon_rag = self.budget.prune_rag_items_by_tokens(canon_rag)

        s["messages"] = canon_msgs
        s["rag_history"] = canon_rag
        s["world"] = canon_world
        s["summary"] = summary

        s["metadata"]["context_consistency"] = "unchecked"  # updated by validation
        return s


# ============================================================================
# 3. STATE VALIDATION
# ============================================================================

_EXPECTED_TYPES: Dict[str, Any] = {
    "messages": list,
    "rag_history": list,
    "world": list,
    "summary": str,
    "session": dict,
    "metadata": dict,
    "phase": str,
    "phase_metadata": dict,
}


def validate_state(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Check for missing fields, type mismatches, and structural warnings.
    """
    missing: List[str] = []
    mismatch: List[str] = []
    warnings: List[str] = []

    for field, t in _EXPECTED_TYPES.items():
        if field not in state:
            missing.append(field)
            continue
        if not isinstance(state[field], t):
            mismatch.append(field)

    # Example structural warnings
    if state.get("draft_result") is not None and len(state.get("messages", [])) == 0:
        warnings.append("draft_result present but messages are empty")

    if state.get("qa_result") is not None and "plan" not in state:
        warnings.append("qa_result present without plan stored in state")

    if state.get("rag_result") is not None and not state.get("rag_history"):
        warnings.append("rag_result present but rag_history is empty")

    return {"missing": missing, "type_mismatch": mismatch, "warnings": warnings}


# ============================================================================
# 4. STATE VIEWS (FOR L2/L3/L5)
# ============================================================================


def get_conversational_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": str(state.get("summary") or ""),
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": str(state.get("summary") or ""),
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


# ============================================================================
# 5. GLOBAL STATE ADAPTER
# ============================================================================


@dataclass
class StateAdapter:
    """
    Unified L4 state manager:

        • Owns an internal canonical state dict
        • Applies key-scoped patches via StatePatch
        • Delegates to MemoryManager for reconciliation
        • Attaches validation metadata
        • Tracks phase and phase history as plain strings
    """

    memory: MemoryManager = field(default_factory=MemoryManager)
    _phase: WorkflowPhase = field(default=WorkflowPhase.INIT, init=False)
    _phase_history: List[str] = field(default_factory=lambda: [WorkflowPhase.INIT.value], init=False)
    _state: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self._state = {
            "messages": [],
            "rag_history": [],
            "world": [],
            "summary": "",
            "session": {},
            "metadata": {},
            "phase": self._phase.value,
            "phase_metadata": {"phase": self._phase.value, "history": list(self._phase_history)},
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._state)

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        """
        Apply a StatePatch, reconcile memory, enforce phase metadata,
        and attach validation information.

        Patch semantics:
            • If both existing state[key] and patch.value are dicts,
              we perform a shallow deep-merge (existing updated in place).
            • Else we replace the top-level key with patch.value.
        """
        updated = copy.deepcopy(self._state)
        key = patch.key
        value = patch.value

        if isinstance(value, dict) and isinstance(updated.get(key), dict):
            # shallow deep-merge
            merged = copy.deepcopy(updated.get(key))
            merged.update(value)
            updated[key] = merged
        else:
            updated[key] = value

        # Reconcile via memory manager
        updated = self.memory.reconcile(updated)

        # Keep phase and phase_metadata consistent
        phase_value = updated.get("phase", self._phase.value)
        try:
            phase_enum = WorkflowPhase(phase_value)
        except ValueError:
            # fallback to previous phase if invalid
            phase_enum = self._phase

        if phase_enum != self._phase:
            self._phase = phase_enum
            self._phase_history.append(phase_enum.value)

        updated["phase"] = self._phase.value
        updated["phase_metadata"] = {
            "phase": self._phase.value,
            "history": list(self._phase_history),
        }

        # Attach validation metadata
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validate_state(updated)

        self._state = updated
        return self.state

    def advance_phase(self, phase: WorkflowPhase) -> WorkflowPhase:
        """
        Advance phase and reflect it in state; does not perform any
        orchestration logic — only updates metadata.
        """
        if not isinstance(phase, WorkflowPhase):
            raise ValueError(f"Invalid phase: {phase}")
        self._phase = phase
        self._phase_history.append(phase.value)
        self._state["phase"] = self._phase.value
        self._state["phase_metadata"] = {
            "phase": self._phase.value,
            "history": list(self._phase_history),
        }
        # Also re-validate after phase change
        self._state.setdefault("metadata", {})
        self._state["metadata"]["validation"] = validate_state(self._state)
        return self._phase
