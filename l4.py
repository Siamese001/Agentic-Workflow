# FILE: l4.py
"""
Unified L4 State Layer (v10_9) — FULL AGENTIC IMPLEMENTATION

This module implements ALL state-related responsibilities for the v10_9
agentic architecture, with feature parity (conceptually) to the richer
state handling in earlier versions, but rewritten cleanly with no legacy
dependencies.

Responsibilities:
    • Phase-aware StateMachine wrapper
    • Context-budget aware MemoryManager
    • World-model normalization (facts, origins, categories)
    • State validation helpers (type + structural checks)
    • State views (conversational, retrieval, prompt-context)
    • Global StateAdapter
        - apply patches
        - reconcile memory
        - enforce phase coherence
        - maintain validation metadata
    • Domain-specific adapters:
        - attach_rag_result
        - attach_bullet_result
        - attach_draft_result
        - attach_qa_result
        - attach_safety_result
        - attach_strategy_result

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

from runtime_utils import Constants

WorkflowPhase = Constants.WorkflowPhase


# ============================================================================
# 1. PHASE-LEVEL STATE MACHINE
# ============================================================================

class StatePhaseMachine:
    """
    Finite-state machine for orchestrator phase control, mirroring
    the allowed transitions defined at the orchestration layer.

        init       → planning, failed
        planning   → executing, failed
        executing  → reviewing, failed
        reviewing  → complete, planning, failed
        complete   → (terminal)
        failed     → (terminal)
    """

    _TRANSITIONS = {
        WorkflowPhase.INIT:      {WorkflowPhase.PLANNING, WorkflowPhase.FAILED},
        WorkflowPhase.PLANNING:  {WorkflowPhase.EXECUTING, WorkflowPhase.FAILED},
        WorkflowPhase.EXECUTING: {WorkflowPhase.REVIEWING, WorkflowPhase.FAILED},
        WorkflowPhase.REVIEWING: {WorkflowPhase.COMPLETE, WorkflowPhase.PLANNING, WorkflowPhase.FAILED},
        WorkflowPhase.COMPLETE:  set(),
        WorkflowPhase.FAILED:    set(),
    }

    def __init__(self, initial: WorkflowPhase = WorkflowPhase.INIT) -> None:
        self.phase: WorkflowPhase = initial
        self.history: List[str] = [initial]

    def can_transition(self, target: WorkflowPhase) -> bool:
        return target in self._TRANSITIONS[self.phase]

    def transition(self, target: WorkflowPhase) -> WorkflowPhase:
        if not self.can_transition(target):
            raise ValueError(f"Illegal transition {self.phase} → {target}")
        self.phase = target
        self.history.append(target)
        return target


# ============================================================================
# 2. WORLD-MODEL NORMALIZATION
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
# 3. CONTEXT BUDGET & MEMORY MANAGEMENT
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

        canon_msgs: List[Dict[str, Any]] = []
        for m in messages:
            if isinstance(m, dict):
                mm = copy.deepcopy(m)
            else:
                mm = {"role": "unknown", "content": str(m)}
            mm["role"] = str(mm.get("role", ""))
            mm["content"] = str(mm.get("content", ""))
            canon_msgs.append(mm)

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

        canon_world = normalize_world_facts(world)

        # Apply simple budgets
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

        s["metadata"]["context_consistency"] = "unchecked"  # placeholder; updated by validation
        return s


# ============================================================================
# 4. STATE VALIDATION
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
    if state.get("draft") is not None and not state.get("messages"):
        warnings.append("draft present but messages are empty")

    if state.get("qa_result") is not None and "plan" not in state:
        warnings.append("qa_result present but no L1 plan stored")

    if state.get("rag_result") is not None and not state.get("rag_history"):
        warnings.append("rag_result present but rag_history is empty")

    return {"missing": missing, "type_mismatch": mismatch, "warnings": warnings}


# ============================================================================
# 5. STATE VIEWS (FOR L2/L3/L5)
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
# 6. GLOBAL STATE ADAPTER
# ============================================================================

class StateAdapter:
    """
    Unified L4 state manager:

        • Owns an internal canonical state dict
        • Applies key-scoped patches
        • Delegates to MemoryManager for reconciliation
        • Enforces phase transitions via StatePhaseMachine
        • Attaches validation metadata
    """

    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        machine: Optional[StatePhaseMachine] = None,
    ) -> None:
        self.memory = memory_manager or MemoryManager()
        self.machine = machine or StatePhaseMachine()

        self._state: Dict[str, Any] = {
            "messages": [],
            "rag_history": [],
            "world": [],
            "summary": "",
            "session": {},
            "metadata": {},
            "phase": self.machine.phase.value,
            "phase_metadata": {"phase": self.machine.phase.value},
        }

    @property
    def state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._state)

    def _coerce_mapping(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, MutableMapping):
            return dict(value)
        return {}

    def apply_patch(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Apply a patch to a top-level key of the state, then reconcile memory
        and update phase/validation metadata.

        Returns a (deep-copied) snapshot of the updated state.
        """
        updated = copy.deepcopy(self._state)
        updated[key] = value

        # Reconcile context budgets & canonicalization
        updated = self.memory.reconcile(updated)

        # Enforce phase coherence (if phase changed externally)
        phase_value = updated.get("phase", self.machine.phase.value)
        phase_obj = WorkflowPhase(phase_value)
        if phase_obj != self.machine.phase:
            self.machine.transition(phase_obj)
        updated["phase"] = self.machine.phase.value
        updated["phase_metadata"] = {
            "phase": self.machine.phase.value,
            "history": list(self.machine.history),
        }

        # Attach validation metadata
        updated["metadata"]["validation"] = validate_state(updated)

        self._state = updated
        return self.state

    def advance_phase(self, phase: WorkflowPhase) -> WorkflowPhase:
        """
        Force a phase transition on the machine and reflect it in state.
        """
        new_phase = self.machine.transition(phase)
        self._state["phase"] = new_phase.value
        self._state["phase_metadata"] = {
            "phase": new_phase.value,
            "history": list(self.machine.history),
        }
        return new_phase


# ============================================================================
# 7. DOMAIN-SPECIFIC STATE ATTACHERS (for L3 Orchestrator)
# ============================================================================

def attach_rag_result(state: Dict[str, Any], rag_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate RAG execution result into state:
        • Extend rag_history
        • Update rag bucket with results + last_run metadata
    """
    s = copy.deepcopy(state)
    docs = rag_payload.get("documents") or []
    s.setdefault("rag_history", []).extend(docs)
    s["rag_result"] = {
        "documents": docs,
        "queries": rag_payload.get("queries", []),
        "ranking_strategy": rag_payload.get("ranking_strategy", "hybrid"),
        "hyde_used": rag_payload.get("hyde_used", False),
    }
    return s


def attach_bullet_result(state: Dict[str, Any], bullet_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate bullet execution result:
        • Append to bullet_history
        • Store bullet_result bucket
    """
    s = copy.deepcopy(state)
    bullets = bullet_payload.get("bullets") or []
    s.setdefault("bullet_history", []).append(bullets)
    s["bullet_result"] = {
        "bullets": bullets,
        "guidelines": bullet_payload.get("guidelines", []),
        "metrics_focus": bullet_payload.get("metrics_focus", []),
    }
    return s


def attach_draft_result(state: Dict[str, Any], draft_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate draft execution result:
        • Append to draft_history
        • Store draft_result bucket
    """
    s = copy.deepcopy(state)
    draft = draft_payload.get("draft") or []
    s.setdefault("draft_history", []).append(draft)
    s["draft_result"] = {
        "sections": draft_payload.get("sections", []),
        "tone": draft_payload.get("tone", ""),
        "draft": draft,
        "hints": draft_payload.get("hints", []),
    }
    # Optionally reflect a summary snippet
    if draft and not s.get("summary"):
        s["summary"] = str(draft[0])[:400]
    return s


def attach_qa_result(state: Dict[str, Any], qa_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate QA execution result:
        • Append qa_report to qa_history
        • Store qa_result bucket
    """
    s = copy.deepcopy(state)
    report = (qa_payload.get("qa_report") or {}).copy()
    s.setdefault("qa_history", []).append(report)
    s["qa_result"] = {
        "report": report,
        "issues": report.get("issues", []),
        "passed": report.get("passed", False),
        "confidence": report.get("confidence", 0.0),
    }
    return s


def attach_safety_result(state: Dict[str, Any], safety_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate Safety execution result:
        • Append safety_report to safety_history
        • Store safety_result bucket
    """
    s = copy.deepcopy(state)
    report = (safety_payload.get("safety_report") or {}).copy()
    sanitized = safety_payload.get("sanitized_content", "")
    s.setdefault("safety_history", []).append(report)
    s["safety_result"] = {
        "report": report,
        "issues": report.get("issues", []),
        "passed": report.get("passed", False),
        "toxicity": report.get("toxicity", 0.0),
        "sanitized_content": sanitized,
    }
    return s


def attach_strategy_result(state: Dict[str, Any], strat_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate Strategy execution result:
        • Append to strategy_history
        • Store strategy_result bucket
    """
    s = copy.deepcopy(state)
    branches = strat_payload.get("strategy_branches") or []
    selected = strat_payload.get("selected_strategy") or (branches[0] if branches else {})
    s.setdefault("strategy_history", []).append(selected)
    s["strategy_result"] = {
        "branches": branches,
        "selected_strategy": selected,
    }
    return s
