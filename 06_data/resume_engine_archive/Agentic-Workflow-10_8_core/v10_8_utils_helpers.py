"""
V10.8 Consolidated Module: Utils Helpers
Merged from 15 source files
"""

# Consolidated imports
from __future__ import annotations
from dataclasses import dataclass, field
from model_invocation import invoke_model
from typing import Any, Dict
from typing import Any, Dict, Iterable, List
from typing import Any, Dict, List
from typing import Dict, Any
import copy
import time


# ============================================================
# From v10_8_errors_controlflow.py
# ============================================================

Error definitions for control-flow orchestration structures.
"""


class ControlFlowError(Exception):
    """Base error for control-flow orchestration."""


class DAGValidationError(ControlFlowError):
    """Raised when a DAG definition is invalid or cyclic."""


class NodeExecutionError(ControlFlowError):
    """Raised when a DAG node encounters an execution failure."""

# ============================================================
# From v10_8_model_invocation.py
# ============================================================

def invoke_model(prompt: str, route_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic model invocation stub that echoes prompt metadata."""

    completion = prompt[:30]
    model_name = route_metadata.get("model")
    return {
        "completion": completion,
        "model": model_name,
    }

# ============================================================
# From v10_8_node_result.py
# ============================================================

Node result primitives for control-flow orchestration.

This module holds a deterministic result container for DAG nodes,
encapsulating status metadata, payload outputs, and optional error
context. No runtime orchestration logic is included here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class NodeResult:
    """Outcome of a DAG node execution."""

    status: NodeStatus
    payload: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# From v10_8_utils_logger.py
# ============================================================

Utilities — Logger

Responsibilities:
    • Define logging scaffolds shared across agentic layers.
    • Provide structured logging hooks for orchestration, execution, and safety components.
    • Avoid coupling to specific frameworks until implementation phases.

This file is scaffolded for Priority 0; implementation comes later.
"""
from datetime import datetime
from typing import Any, Dict, List


SAFETY_LOG: List[Dict[str, Any]] = []


def log_safety_decision(payload: Dict[str, Any], patch: Dict[str, Any]) -> None:
    """Deterministic stub for logging safety gateway decisions."""

    SAFETY_LOG.append({"payload": payload, "patch": patch, "ts": datetime.utcnow().isoformat()})

# ============================================================
# From v10_8_utils_patch_helpers.py
# ============================================================

Utilities — Patch Helpers

Deterministic utilities for applying nested state patches. The helpers avoid
side effects by working on deep copies and respect "__delete__" directives for
removing keys.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

from utils_types import StatePatch


def _merge_dict(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge dictionaries with deterministic ordering."""

    result = copy.deepcopy(base)
    for key in sorted(patch.keys()):
        value = patch[key]
        if isinstance(value, dict) and value.get("__delete__") is True:
            result.pop(key, None)
            continue

        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def apply_patch(state: Dict[str, Any], patch: StatePatch) -> Dict[str, Any]:
    """Apply a StatePatch to a state dictionary deterministically.

    The function returns a new state without mutating the original input.
    """

    if not isinstance(patch, dict):
        raise TypeError("StatePatch must be a dictionary")

    return _merge_dict(state, patch)

# ============================================================
# From v10_8_utils_types.py
# ============================================================

Utilities — Types

Defines shared type aliases and protocol scaffolds across layers.
These types are intentionally lightweight to avoid entangling the
architecture with concrete implementations during early phases.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Protocol


class PlanObject(Dict[str, Any]):
    """Lightweight plan container used by L1 planners.

    The structure remains intentionally flexible while preserving
    mapping semantics for deterministic patch generation at L2+.
    """


class StatePatch(Dict[str, Any]):
    """Patch structure applied to the mutable orchestration state."""


class Message(Dict[str, Any]):
    """Generic message payload used by memory management."""


@dataclass
class BudgetConfig:
    """Configuration for context budgeting heuristics."""

    max_messages: int = 50
    max_rag_items: int = 20
    max_prompt_tokens: int = 4000
    max_retrieval_tokens: int = 4000
    max_summary_chars: int = 4000
    max_world_items: int = 50


class Phase(str, Enum):
    """Enumerated lifecycle phases for the deterministic state machine."""

    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


class ReasonerProtocol(Protocol):
    """Protocol for L1 planners."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        ...


class ExecutionAgentProtocol(Protocol):
    """Protocol for L2 execution agents."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        ...


# World-model related aliases (lightweight and dependency-free)
WorldModel = Dict[str, Any]
UserProfile = Dict[str, Any]
SessionMetadata = Dict[str, Any]

# ============================================================
# From v10_8_world_model_contracts.py
# ============================================================

World Model Contracts

Defines deterministic schemas for world-model facts and helpers to normalize
incoming data into canonical structures.
"""
from __future__ import annotations

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
# From v10_8_auto_tuner_stub.py
# ============================================================

class PolicyAutoTunerStub:
    def suggest_config(self, state, metrics):
        # deterministic suggestion stub
        return {
            "temperature": 0.3,
            "max_tokens": 500,
            "routing_adjustment": "none",
        }

# ============================================================
# From v10_8_client_strategy.py
# ============================================================

class ModelClient:
    """Abstract client for model execution. Deterministic stub only."""

    def __init__(self, route_metadata: Dict[str, Any] | None = None) -> None:
        self.route_metadata = route_metadata or {}

    def complete(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the deterministic stub with a fully rendered prompt."""

        merged_metadata = {**self.route_metadata, **(config or {})}
        return invoke_model(prompt, merged_metadata)


def build_client_for_route(route: Dict[str, Any]) -> ModelClient:
    # Return a new client bound to route metadata; side-effect free
    return ModelClient(route)


def configure_for_routing(route: Dict[str, Any]) -> Dict[str, Any]:
    selected_model = route.get("selected_model") or route.get("model")
    model_name = selected_model or "stub-model-for-" + route.get("complexity", "default")
    endpoint = route.get("endpoint") or "/v1/" + route.get("complexity", "default")
    return {
        "model": model_name,
        "model_name": model_name,
        "endpoint": endpoint,
        "route": route,
    }


def run_model_for_plan(plan: Dict[str, Any], state: Dict[str, Any]):
    from prompt_utils import build_prompt_from_plan_and_state
    from routing import RoutingCriteria, decide_route
    from routing import get_routing_plan
    from routing import build_client_for_route, configure_for_routing

    rendered = build_prompt_from_plan_and_state(plan, state)
    routing_plan = get_routing_plan(plan)

    safety_metadata = plan.get("safety_metadata", {}) if isinstance(plan, dict) else {}
    latency_seconds = routing_plan.get("latency_target", 0)
    try:
        latency_ms = int(latency_seconds * 1000)
    except Exception:
        latency_ms = 0

    criteria = RoutingCriteria(
        task_type=str(plan.get("mode", "unknown")),
        complexity=str(routing_plan.get("complexity", "low")),
        latency_target_ms=latency_ms,
        cost_ceiling_usd=float(routing_plan.get("cost_ceiling", 0.0)),
        risk_level=str(
            routing_plan.get(
                "risk_level", "strict" if safety_metadata.get("sensitivity") == "high" else "normal"
            )
        ),
    )
    decision = decide_route(criteria)
    routing_dict = {
        "selected_model": decision.model,
        "endpoint": decision.endpoint,
        "rationale": decision.rationale,
    }

    routing_plan.update(routing_dict)
    plan["routing"] = routing_plan

    client = build_client_for_route(routing_dict)
    config = configure_for_routing(routing_dict)
    result = client.complete(rendered["prompt"], config)

    return {
        "prompt": rendered["prompt"],
        "model_output": result,
        "routing": routing_dict,
    }

# ============================================================
# From v10_8_cost_tracker.py
# ============================================================

@dataclass
class CostTracker:
    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        snapshot_spans: List[Dict[str, float]] = []
        for span_name in sorted(self.spans.keys()):
            span = self.spans[span_name]
            start = span.get("start", 0.0) or 0.0
            end = span.get("end", start)
            duration_ms = max((end - start) * 1000.0, 0.0)
            snapshot_spans.append({"name": span_name, "duration_ms": duration_ms})
        return {"spans": snapshot_spans}

# ============================================================
# From v10_8_memory_views.py
# ============================================================

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

# ============================================================
# From v10_8_optimization_hints.py
# ============================================================

def compute_optimization_hint(spans: list) -> Dict[str, Any]:
    """
    Deterministic optimization hint based on span durations.
    """
    planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
    execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

    if float(planning.get("duration_ms", 0)) > float(execution.get("duration_ms", 0)):
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}

# ============================================================
# From v10_8_predictive_cache.py
# ============================================================

class PredictiveCache:
    def __init__(self):
        self.cache = {}

    def get(self, signature: str):
        return self.cache.get(signature)

    def set(self, signature: str, value):
        self.cache[signature] = value

    def snapshot(self):
        return self.cache.copy()

# ============================================================
# From v10_8_state_validation.py
# ============================================================

State Validation Utilities

Provides lightweight validation of orchestration state with warnings for
cross-field inconsistencies.
"""
from __future__ import annotations

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
# From v10_8_evidence_fusion.py
# ============================================================

def fuse_results(list_of_sources: Iterable[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for source in list_of_sources:
        for item in source:
            merged.append(dict(item))

    return sorted(merged, key=lambda r: (r.get("query", ""), r.get("rank", 0)))

