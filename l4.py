# FILE: l4.py
"""
Unified L4 State Layer (v10_9) — ENTERPRISE REFACTOR

This module implements ALL state-related responsibilities for the v10_9
agentic architecture, with feature parity to and extension of the richer
state handling in earlier versions (v10_7 / v10_8), but rewritten
cleanly with no legacy dependencies.

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
        - store checkpoints/episodic traces (metadata only)

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

    if state.get("safety_result") is not None and "arbitration" not in state:
        warnings.append("safety_result present without arbitration metadata")

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
        • Stores simple checkpoint/episodic metadata for higher-level
          persistence systems (no actual IO here).
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
            # Optional enterprise fields
            "checkpoints": [],
            "episodic": [],
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._state)

    def _update_phase(self, new_phase: WorkflowPhase) -> None:
        if new_phase == self._phase:
            return
        self._phase = new_phase
        self._phase_history.append(new_phase.value)
        self._state["phase"] = new_phase.value
        self._state["phase_metadata"] = {
            "phase": new_phase.value,
            "history": list(self._phase_history),
        }

    def _merge_value(self, existing: Any, value: Any) -> Any:
        """
        Shallow merge semantics used by apply_patch:

            • If both existing and value are dicts, update in place.
            • If both are lists, concatenate.
            • Else, value replaces existing.
        """
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
        """
        Apply a StatePatch, reconcile memory, enforce phase metadata,
        and attach validation information.

        Patch semantics:
            • If both existing state[key] and patch.value are dicts,
              we perform a shallow deep-merge (existing updated in place).
            • If both are lists, we append.
            • Else we replace the top-level key with patch.value.
        """
        updated = copy.deepcopy(self._state)
        key = patch.key
        value = patch.value

        if key in updated:
            updated[key] = self._merge_value(updated[key], value)
        else:
            updated[key] = value

        # Update phase if patch explicitly sets it
        if key == "phase":
            try:
                new_phase = WorkflowPhase(str(value))
                self._update_phase(new_phase)
                # sync into updated map as well
                updated["phase"] = new_phase.value
                updated["phase_metadata"] = {
                    "phase": new_phase.value,
                    "history": list(self._phase_history),
                }
            except Exception:
                # ignore invalid phase values
                pass

        # Reconcile via memory manager
        updated = self.memory.reconcile(updated)

        # Validate and attach validation metadata
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation

        # Commit to internal state
        self._state = updated
        return self.state

    # -------------------------------------------------------------------------
    # Convenience helpers for checkpoints and episodic metadata
    # -------------------------------------------------------------------------

    def record_checkpoint(self, checkpoint_id: str, notes: str = "") -> Dict[str, Any]:
        """
        Record a simple checkpoint metadata object into state["checkpoints"].

        This does not perform any IO or persistence. A higher-level
        checkpointing system is responsible for actually storing/restoring
        full state blobs associated with checkpoint_id.
        """
        cp = {
            "id": str(checkpoint_id),
            "phase": self._phase.value,
            "notes": str(notes),
        }
        updated = copy.deepcopy(self._state)
        checkpoints = list(updated.get("checkpoints") or [])
        checkpoints.append(cp)
        updated["checkpoints"] = checkpoints
        updated = self.memory.reconcile(updated)
        validation = validate_state(updated)
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validation
        self._state = updated
        return self.state

    def append_episodic_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Append an episodic event into state["episodic"].

        Events are arbitrary, but strongly encouraged to be small
        metadata blobs (e.g., {"source": "qa", "type": "failure"}).
        """
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
