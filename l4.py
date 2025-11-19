# FILE: l4.py
"""
Unified L4 State Layer (v10_9) — PURE STATE / MEMORY MANAGEMENT

This module implements ALL state-related responsibilities for the v10_9
agentic architecture, with zero cross-layer violations:

    • Context-budget-aware memory management.
    • World-model normalization (facts, origins, categories).
    • State validation helpers (type + structural checks).
    • State views (conversational, retrieval, prompt-context).
    • Global StateAdapter:
        - apply patches (StatePatch)
        - reconcile memory
        - maintain phase & phase history
        - attach validation metadata
        - store checkpoints & episodic traces (metadata only)
        - store meta-blocks (telemetry, self_correction, multi_agent, etc.)

Layer constraints (Agentic Guardrails):

    • NO cognition (L1) — no planning logic.
    • NO execution (L2) — no tool/LLM calls.
    • NO orchestration (L3) — no DAG/phase logic.
    • NO safety/policy decisions (L5) — no SafetyEngine/PolicyEngine logic.
    • NO provider/tool imports — Anthropic/Gemini/OpenAI/etc. are not visible here.

All state updates in the runtime MUST go through StateAdapter.apply_patch()
or its helpers. This ensures deterministic, validated, budgeted state
evolution aligned with the Agentic Ecosystem Scorecard.
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

    This is a pure function; it does not touch StateAdapter or phases.
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

    This config is used ONLY by ContextBudget and MemoryManager. It does
    not perform any tokenization or external calls.
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

    This class is layer-pure: it does not know about phases, plans,
    tools, or providers. It operates on generic lists/dicts/strings.
    """

    def __init__(self, config: Optional[BudgetConfig] = None) -> None:
        self.config = config or BudgetConfig()

    # ---- hard limits on list sizes -----------------------------------------

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
        """
        Approximate token budget for retrieval: use evidence lengths as
        a simple proxy; drop from the front until under the limit.
        """
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

    It must NOT:
        • know about L1/L2/L3 logic
        • call tools, providers, or safety engines

    It receives a state dict, returns a reconciled copy; actual writes
    are performed by StateAdapter.
    """

    def __init__(self, budget: Optional[ContextBudget] = None) -> None:
        self.budget = budget or ContextBudget()

    def reconcile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a reconciled copy of the state with:

            • canonicalized messages / rag_history / world
            • summaries trimmed to budget
            • approximate token budgets applied
            • metadata["context_consistency"] left as "unchecked"
              (StateAdapter attaches validation metadata later)
        """
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

        # Mark context consistency as unchecked; validate_state will refine.
        s["metadata"]["context_consistency"] = "unchecked"
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
    # Extended but optional keys: checked only if present
    # (we do not treat absence as a hard error)
}


def validate_state(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Check for missing fields, type mismatches, and structural warnings.

    This function is **pure**: it does not mutate the state, it only
    inspects it and returns warnings/errors for StateAdapter to attach
    under metadata["validation"].
    """
    missing: List[str] = []
    mismatch: List[str] = []
    warnings: List[str] = []

    for field_name, t in _EXPECTED_TYPES.items():
        if field_name not in state:
            missing.append(field_name)
            continue
        if not isinstance(state[field_name], t):
            mismatch.append(field_name)

    # Example structural warnings
    if state.get("draft_result") is not None and len(state.get("messages", [])) == 0:
        warnings.append("draft_result present but messages are empty")

    if state.get("qa_result") is not None and "plan" not in state:
        warnings.append("qa_result present without plan stored in state")

    if state.get("rag_result") is not None and not state.get("rag_history"):
        warnings.append("rag_result present but rag_history is empty")

    if state.get("safety_result") is not None and "arbitration" not in state:
        warnings.append("safety_result present without arbitration metadata")

    if state.get("self_correction") is not None and "telemetry" not in state:
        warnings.append("self_correction present but telemetry is missing")

    if state.get("multi_agent") is not None and "qa_result" not in state:
        warnings.append("multi_agent block present without qa_result")

    return {"missing": missing, "type_mismatch": mismatch, "warnings": warnings}


# ============================================================================
# 4. STATE VIEWS (FOR L2/L3/L5/PROMPT LAYER)
# ============================================================================


def get_conversational_view(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a view containing only conversationally relevant fields.

    Typically used by L1/L2/L5 and the prompt layer to build input
    context for reasoning/execution.
    """
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": str(state.get("summary") or ""),
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a view containing only retrieval-relevant fields.
    """
    return {
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a view suitable for prompt construction, including
    conversational and retrieval context.
    """
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

        • Owns an internal canonical state dict.
        • Applies key-scoped patches via StatePatch.
        • Delegates to MemoryManager for reconciliation.
        • Attaches validation metadata.
        • Tracks phase and phase history as plain strings.
        • Stores simple checkpoint/episodic metadata for higher-level
          persistence systems (no actual IO here).
        • Stores additional meta blocks (telemetry, self_correction,
          multi_agent, arbitration, etc.) without interpreting them.

    This is the **only** component allowed to mutate runtime state.
    All other layers must read state via `state_adapter.state` and
    write via StatePatch + apply_patch.
    """

    memory: MemoryManager = field(default_factory=MemoryManager)
    _phase: WorkflowPhase = field(default=WorkflowPhase.INIT, init=False)
    _phase_history: List[str] = field(default_factory=lambda: [WorkflowPhase.INIT.value], init=False)
    _state: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """
        Initialize the internal state with a canonical skeleton.

        Keys:
            messages        — list of message dicts
            rag_history     — list of retrieval history entries
            world           — list of normalized world facts
            summary         — overall textual summary
            session         — misc session metadata
            metadata        — validation/context metadata
            phase           — current workflow phase
            phase_metadata  — phase + history
            checkpoints     — list of checkpoint metadata
            episodic        — list of small episodic events
        """
        self._state = {
            "messages": [],
            "rag_history": [],
            "world": [],
            "summary": "",
            "session": {},
            "metadata": {},
            "phase": self._phase.value,
            "phase_metadata": {"phase": self._phase.value, "history": list(self._phase_history)},
            # Optional enterprise/meta fields
            "checkpoints": [],
            "episodic": [],
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def state(self) -> Dict[str, Any]:
        """
        Return a deep copy of the internal state.

        Callers must never mutate the returned dict in-place expecting
        changes to persist; all mutations must go through apply_patch().
        """
        return copy.deepcopy(self._state)

    def _update_phase(self, new_phase: WorkflowPhase) -> None:
        """
        Internal helper to update phase & phase history in the state.
        """
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

        This keeps L4 logic simple and predictable, while delegating
        any deeper structures to callers.
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
              we perform a shallow merge (existing updated in place).
            • If both are lists, we append.
            • Else we replace the top-level key with patch.value.

        This method is the central choke-point for all state writes.
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
        metadata blobs, e.g.:

            {"source": "qa", "type": "failure", "severity": "high"}

        This method is convenience only, wrapping apply_patch semantics.
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
