# FILE: v10_9_clean/l4.py
"""
Unified L4 State Layer (v10_9)

This file consolidates ALL L4 responsibilities:

    • StateMachine
    • StateAdapter (global)
    • MemoryManager
    • ContextBudget
    • World-model normalization
    • State validation helpers
    • State views (conversational, retrieval, etc.)
    • Domain-specific state adapters:
        - attach_rag_result
        - attach_bullet_result
        - attach_draft_result
        - attach_qa_result
        - attach_safety_result
        - attach_strategy_result

Pure state management:
    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO safety logic (L5)
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List
from dataclasses import dataclass, field

from constants import WorkflowPhase
from exceptions import ValidationError


# ============================================================================
# STATE MACHINE
# ============================================================================

class StateMachine:
    """
    Finite-state machine for orchestrator phase control.
    """

    _TRANSITIONS = {
        WorkflowPhase.INIT.value: {WorkflowPhase.PLANNING, WorkflowPhase.FAILED},
        WorkflowPhase.PLANNING.value: {WorkflowPhase.EXECUTING, WorkflowPhase.FAILED},
        WorkflowPhase.EXECUTING.value: {WorkflowPhase.REVIEWING, WorkflowPhase.FAILED},
        WorkflowPhase.REVIEWING.value: {
            WorkflowPhase.COMPLETE,
            WorkflowPhase.PLANNING,
            WorkflowPhase.FAILED,
        },
        WorkflowPhase.COMPLETE.value: set(),
        WorkflowPhase.FAILED.value: set(),
    }

    def __init__(self, initial: WorkflowPhase = WorkflowPhase.INIT) -> None:
        self.phase = initial
        self.history = [initial.value]

    def can_transition(self, target: WorkflowPhase) -> bool:
        return target in self._TRANSITIONS[self.phase.value]

    def transition(self, target: WorkflowPhase) -> WorkflowPhase:
        if not self.can_transition(target):
            raise ValueError(f"Illegal transition {self.phase} → {target}")
        self.phase = target
        self.history.append(target.value)
        return target


# ============================================================================
# WORLD-MODEL NORMALIZATION
# ============================================================================

_ALLOWED_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_ORIGINS = {"retrieval", "user", "system"}

def _coerce_category(v: Any) -> str:
    return v if isinstance(v, str) and v in _ALLOWED_CATEGORIES else "entity"

def _coerce_origin(v: Any) -> str:
    return v if isinstance(v, str) and v in _ALLOWED_ORIGINS else "system"

def _coerce_content(v: Any) -> str:
    if isinstance(v, str):
        return v
    return "" if v is None else str(v)

def normalize_world_facts(items: List[dict]) -> List[Dict[str, Any]]:
    out = []
    for item in items or []:
        if isinstance(item, dict):
            d = dict(item)
        else:
            d = {"content": _coerce_content(item)}
        d["category"] = _coerce_category(d.get("category"))
        d["origin"] = _coerce_origin(d.get("origin"))
        d["content"] = _coerce_content(d.get("content"))
        out.append(d)
    return out


# ============================================================================
# CONTEXT BUDGET
# ============================================================================

@dataclass
class BudgetConfig:
    max_messages: int = 30
    max_rag_items: int = 20
    max_world_items: int = 30
    max_summary_chars: int = 2000
    max_prompt_tokens: int = 5000
    max_retrieval_tokens: int = 5000


class ContextBudget:
    def __init__(self, config: BudgetConfig | None = None) -> None:
        self.config = config or BudgetConfig()

    def prune_messages(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return msgs[-self.config.max_messages:] if len(msgs) > self.config.max_messages else msgs

    def prune_rag_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return items[-self.config.max_rag_items:] if len(items) > self.config.max_rag_items else items

    def prune_world(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return items[-self.config.max_world_items:] if len(items) > self.config.max_world_items else items

    def prune_summary(self, s: str) -> str:
        return s[-self.config.max_summary_chars:] if len(s) > self.config.max_summary_chars else s

    def prune_messages_by_tokens(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # approximate token count (split)
        token_counts = [len(str(m.get("content", "")).split()) for m in msgs]
        total = sum(token_counts)
        limit = self.config.max_prompt_tokens
        if total <= limit:
            return msgs
        i = 0
        while i < len(msgs) and total > limit:
            total -= token_counts[i]
            i += 1
        return msgs[i:]

    def prune_rag_items_by_tokens(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        token_counts = [len(str(x.get("evidence", "")).split()) for x in items]
        total = sum(token_counts)
        limit = self.config.max_retrieval_tokens
        if total <= limit:
            return items
        i = 0
        while i < len(items) and total > limit:
            total -= token_counts[i]
            i += 1
        return items[i:]


# ============================================================================
# MEMORY MANAGER
# ============================================================================

class MemoryManager:
    """Handles message/rag/world/summary pruning + normalization."""

    def __init__(self, budget: ContextBudget | None = None) -> None:
        self.budget = budget or ContextBudget()

    def reconcile_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        s = copy.deepcopy(state)
        s.setdefault("metadata", {})

        msgs = s.get("messages") or []
        rag_hist = s.get("rag_history") or []
        summary = s.get("summary", "") or ""
        world = s.get("world") or []

        canon_msgs = []
        for m in msgs:
            if isinstance(m, dict):
                mm = copy.deepcopy(m)
            else:
                mm = {"role": "unknown", "content": str(m)}
            mm["role"] = str(mm.get("role", ""))
            mm["content"] = str(mm.get("content", ""))
            canon_msgs.append(mm)

        # normalize RAG
        canon_rag = []
        for item in rag_hist:
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

        msgs = self.budget.prune_messages(canon_msgs)
        rag_hist = self.budget.prune_rag_items(canon_rag)
        summary = self.budget.prune_summary(summary)
        world = self.budget.prune_world(normalize_world_facts(world))

        msgs = self.budget.prune_messages_by_tokens(msgs)
        rag_hist = self.budget.prune_rag_items_by_tokens(rag_hist)

        s["messages"] = msgs
        s["rag_history"] = rag_hist
        s["summary"] = summary
        s["world"] = world
        s["metadata"]["context_consistency"] = "unchecked"
        return s


# ============================================================================
# STATE VALIDATION
# ============================================================================

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

def validate_state(state: Dict[str, Any]) -> Dict[str, List[str]]:
    missing, mismatch, warn = [], [], []

    for field, t in _EXPECTED_TYPES.items():
        if field not in state:
            missing.append(field)
            continue
        if not isinstance(state[field], t):
            mismatch.append(field)

    if state.get("draft") is not None and len(state.get("messages", [])) == 0:
        warn.append("draft present but messages empty")

    if state.get("qa_result") is not None and "plan" not in state:
        warn.append("qa_result present without plan")

    return {"missing": missing, "type_mismatch": mismatch, "warnings": warn}


# ============================================================================
# STATE VIEWS
# ============================================================================

def get_conversational_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": state.get("summary", "") or "",
    }

def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }

def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": state.get("summary", "") or "",
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


# ============================================================================
# GLOBAL STATE ADAPTER
# ============================================================================

class StateAdapter:
    """
    Unified L4 state manager:
        • apply patches
        • enforce phase via StateMachine
        • reconcile memory
        • validate state
        • produce canonical snapshots
    """

    def __init__(self, memory_manager: MemoryManager | None = None, machine: StateMachine | None = None):
        self.memory = memory_manager or MemoryManager()
        self.machine = machine or StateMachine()
        self._state = {
            "messages": [],
            "rag_history": [],
            "summary": "",
            "world": [],
            "session": {},
            "metadata": {},
            "phase": self.machine.phase.value,
            "phase_metadata": {"phase": self.machine.phase.value},
        }

    @property
    def state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._state)

    def apply_patch(self, key: str, value: Any) -> Dict[str, Any]:
        updated = copy.deepcopy(self._state)
        updated[key] = value

        updated = self.memory.reconcile_state(updated)

        phase_value = updated.get("phase")
        phase = WorkflowPhase(phase_value)
        if self.machine.phase != phase:
            self.machine.transition(phase)

        updated["phase"] = self.machine.phase.value
        updated["phase_metadata"] = {"phase": self.machine.phase.value}
        updated["metadata"]["validation"] = validate_state(updated)

        self._state = updated
        return self.state

    def advance_phase(self, phase: WorkflowPhase) -> WorkflowPhase:
        newp = self.machine.transition(phase)
        self._state["phase"] = newp.value
        return newp


# ============================================================================
# DOMAIN-SPECIFIC STATE ADAPTERS
# ============================================================================

def attach_rag_result(state: Dict[str, Any], rag_payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    docs = rag_payload.get("documents") or []
    s.setdefault("rag_history", []).extend(docs)
    s["rag"] = {
        "results": docs,
        "last_run": {
            "queries": rag_payload.get("queries", []),
            "filters": rag_payload.get("filters", {}),
            "ranking": rag_payload.get("ranking", {}),
        },
    }
    return s


def attach_bullet_result(state: Dict[str, Any], bullet_payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    bullets = bullet_payload.get("bullets") or []
    s.setdefault("bullet_history", []).append(bullets)
    s["bullets"] = {
        "items": bullets,
        "target_sections": bullet_payload.get("target_sections", []),
        "guidelines": bullet_payload.get("guidelines", []),
        "validation_checks": bullet_payload.get("validation_checks", []),
    }
    return s


def attach_draft_result(state: Dict[str, Any], draft_payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    draft = draft_payload.get("draft") or []
    s.setdefault("draft_history", []).append(draft)
    s["draft"] = {
        "sections": draft_payload.get("sections", []),
        "tone": draft_payload.get("tone", ""),
        "audience": draft_payload.get("audience", ""),
        "hints": draft_payload.get("hints", []),
        "content": draft,
    }
    return s


def attach_qa_result(state: Dict[str, Any], qa_payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    report = qa_payload.get("qa_report") or {}
    s.setdefault("qa_history", []).append(report)
    s["qa"] = {
        "report": report,
        "issues": report.get("issues", []),
        "confidence": report.get("confidence", 0.0),
        "passed": report.get("passed", False),
    }
    return s


def attach_safety_result(state: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    report = payload.get("safety_report") or {}
    sanitized = payload.get("sanitized_content", "")
    s.setdefault("safety_history", []).append(report)
    s["safety"] = {
        "report": report,
        "issues": report.get("issues", []),
        "passed": report.get("passed", False),
        "audience": report.get("audience", ""),
        "sensitivity": report.get("sensitivity", ""),
        "sanitized_content": sanitized,
    }
    return s


def attach_strategy_result(state: Dict[str, Any], strat_payload: Dict[str, Any]) -> Dict[str, Any]:
    s = copy.deepcopy(state)
    s.setdefault("strategy_history", []).append(strat_payload)
    s["strategy"] = {
        "objective": strat_payload.get("objective"),
        "constraints": strat_payload.get("constraints", []),
        "dependencies": strat_payload.get("dependencies", []),
        "deliverables": strat_payload.get("deliverables", []),
        "outline": strat_payload.get("outline", []),
        "next_actions": strat_payload.get("next_actions", []),
    }
    return s
