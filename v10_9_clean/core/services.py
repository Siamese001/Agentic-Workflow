"""Service layer components for the v10_9_clean runtime.

This module provides the core runtime services (cache, budgets, cost tracking,
metrics, self-correction, precompute, prompt templates, arbitration, and
policy tuning) using the v10_8+ architecture while preserving the v10_7
behavioral surface where practical.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from .exceptions import BudgetExceededError, CacheMiss, ValidationError
from .models import NodeResult, QAOutputModel, StatePatch
from utils_types import BudgetConfig, Message


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cache primitives
# ---------------------------------------------------------------------------


class CacheManager:
    """Hybrid cache supporting exact and semantic strategies.

    This is the v10_7 cache surface, preserved so that existing callers
    and tests continue to work unchanged.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}
        self._semantic_cache: Dict[str, Any] = {}
        self.hits: int = 0
        self.misses: int = 0
        self.semantic_hits: int = 0
        self.semantic_misses: int = 0

    def get(self, key: str) -> Any:
        if key not in self._cache:
            self.misses += 1
            raise CacheMiss(key)
        self.hits += 1
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def get_semantic(self, key: str) -> Any:
        if key not in self._semantic_cache:
            self.semantic_misses += 1
            raise CacheMiss(key)
        self.semantic_hits += 1
        return self._semantic_cache[key]

    def set_semantic(self, key: str, value: Any) -> None:
        self._semantic_cache[key] = value


class PredictiveCache:
    """Simple predictive cache keyed by deterministic signatures."""

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def get(self, signature: str) -> Any:
        return self._cache.get(signature)

    def set(self, signature: str, value: Any) -> None:
        self._cache[signature] = value

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._cache)


class PredictiveCacheManager:
    """Predictive caching facade kept for backwards compatibility.

    In v10_9 this wraps a PredictiveCache instance but keeps the older
    ``prime`` surface so existing code paths remain valid.
    """

    def __init__(self, cache: Optional[PredictiveCache] = None) -> None:
        self._cache = cache or PredictiveCache()

    def prime(self, key: str, value: Any) -> None:
        """Prime the predictive cache with a speculative value."""
        self._cache.set(key, value)

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def snapshot(self) -> Dict[str, Any]:
        return self._cache.snapshot()


class CacheEnvelope:
    """Annotated cache record container."""

    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value
        self.cached_at = time.time()


class PredictiveCacheRecord(CacheEnvelope):
    """Predictive cache payload wrapper."""
    pass


# ---------------------------------------------------------------------------
# Self-correction and validation
# ---------------------------------------------------------------------------


class ResponseValidator:
    """Validates model responses."""

    def __init__(self, rules: Optional[Dict[str, Any]] = None) -> None:
        self.rules = rules or {}

    def validate(self, payload: Dict[str, Any]) -> None:
        if self.rules.get("require_answer") and "answer" not in payload:
            raise ValidationError("Missing answer")


class SelfCorrectionManager:
    """Handles corrective retries for model responses (v10_7 surface)."""

    def __init__(self, validator: Optional[ResponseValidator] = None) -> None:
        self.validator = validator
        self.max_retries = 2
        self.active_retries: Dict[str, int] = {}

    def can_retry(self, workflow_id: str) -> bool:
        return self.active_retries.get(workflow_id, 0) < self.max_retries

    def start_retry(self, workflow_id: str) -> None:
        self.active_retries[workflow_id] = self.active_retries.get(workflow_id, 0) + 1

    def finalize_retry(self, workflow_id: str) -> None:
        self.active_retries.pop(workflow_id, None)

    async def apply(self, result: NodeResult) -> NodeResult:
        """Optionally validate and return the node result unchanged."""
        if self.validator:
            self.validator.validate(getattr(result, "payload", {}))
        await asyncio.sleep(0)  # keep async signature deterministic
        return result


class SelfCorrectionPlan(NodeResult):
    """Alias for a corrective node result."""
    pass


# ---------------------------------------------------------------------------
# Context budgeting (L4-aligned helpers)
# ---------------------------------------------------------------------------


@dataclass
class ContextBudgetConfig:
    """Soft context budgeting configuration for episodic, RAG, and summaries."""

    max_episodic_messages: Optional[int] = 50
    max_rag_documents: Optional[int] = 20
    max_summary_chars: Optional[int] = 12000


class ContextBudget:
    """Applies heuristic limits to contextual elements based on BudgetConfig."""

    def __init__(self, config: BudgetConfig | None = None) -> None:
        self.config = config or BudgetConfig()
        self.pruning_rules = {
            "messages": "preserve order and trim to max_messages",
            "rag_history": "preserve order and trim to max_rag_items",
            "world": "preserve order and trim to max_world_items",
            "summary": "trim to max_summary_chars",
        }

    def prune_messages(self, messages: List[Message]) -> List[Message]:
        if len(messages) <= self.config.max_messages:
            return messages
        return messages[-self.config.max_messages :]

    def prune_rag_items(self, items: List[dict]) -> List[dict]:
        if len(items) <= self.config.max_rag_items:
            return items
        return items[-self.config.max_rag_items :]

    def prune_messages_by_tokens(self, messages: List[Message]) -> List[Message]:
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
        if len(items) <= self.config.max_world_items:
            return items
        return items[-self.config.max_world_items :]

    def prune_summary(self, summary: str) -> str:
        if len(summary) <= self.config.max_summary_chars:
            return summary
        return summary[-self.config.max_summary_chars :]


class ContextBudgetManager:
    """Unified context budget manager.

    Combines the v10_7 hard-token budget surface (allocate/remaining) with
    v10_8+ soft enforcement helpers (episodic memory, RAG documents, summaries)
    and the v10_9 ContextBudget token heuristics.
    """

    def __init__(
        self,
        max_tokens: int = 32000,
        budget_config: BudgetConfig | None = None,
        soft_config: ContextBudgetConfig | None = None,
        delegate: Any | None = None,
    ) -> None:
        self.max_tokens = max_tokens
        self._used_tokens = 0
        self.delegate = delegate
        self.soft_config = soft_config or ContextBudgetConfig()
        self.budget = ContextBudget(budget_config)

    # v10_7-style hard budget -------------------------------------------------

    def allocate(self, tokens: int) -> None:
        if self._used_tokens + tokens > self.max_tokens:
            raise BudgetExceededError("Context budget exceeded")
        self._used_tokens += tokens

    def remaining(self) -> int:
        return max(self.max_tokens - self._used_tokens, 0)

    # v10_8-style soft enforcement -------------------------------------------

    def enforce_all(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Apply delegate enforcement then soft trimming for memory, RAG, and summaries."""
        if not isinstance(state, Mapping):
            return state

        updated_state: Any = state
        if self.delegate is not None:
            delegate_enforce = getattr(self.delegate, "enforce_all", None)
            if callable(delegate_enforce):
                updated_state = delegate_enforce(updated_state)

        updated_state = self._trim_episodic_memory(updated_state)
        updated_state = self._trim_rag_history(updated_state)
        updated_state = self._trim_summary(updated_state)
        return updated_state

    def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        """Delegate pruning if available, otherwise return document unchanged."""
        delegate_prune = getattr(self.delegate, "prune", None)
        if callable(delegate_prune):
            return delegate_prune(document, max_tokens)
        return document

    def _trim_episodic_memory(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_messages = self.soft_config.max_episodic_messages
        if not max_messages:
            return state
        try:
            memory = state.get("memory") or {}
            episodic = memory.get("episodic") or {}
            conversation = episodic.get("conversation")
            if isinstance(conversation, list) and len(conversation) > max_messages:
                trimmed = conversation[-max_messages:]
                logger.info(
                    "Trimming episodic memory from %s to %s entries",
                    len(conversation),
                    len(trimmed),
                )
                episodic = dict(episodic, conversation=trimmed)
                memory = dict(memory, episodic=episodic)
                new_state = dict(state)
                new_state["memory"] = memory
                return new_state
        except Exception as exc:  # pragma: no cover - soft mode resiliency
            logger.warning("Soft budget enforcement failed for episodic memory: %s", exc)
        return state

    def _trim_rag_history(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_docs = self.soft_config.max_rag_documents
        if not max_docs:
            return state
        try:
            rag = state.get("rag") or {}
            documents = rag.get("documents")
            if isinstance(documents, list) and len(documents) > max_docs:
                trimmed_docs = documents[:max_docs]
                logger.info(
                    "Trimming RAG documents from %s to %s",
                    len(documents),
                    len(trimmed_docs),
                )
                rag = dict(rag, documents=trimmed_docs)
                new_state = dict(state)
                new_state["rag"] = rag
                return new_state
        except Exception as exc:  # pragma: no cover
            logger.warning("Soft budget enforcement failed for RAG history: %s", exc)
        return state

    def _trim_summary(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_chars = self.soft_config.max_summary_chars
        if not max_chars:
            return state
        try:
            summary = state.get("summary")
            if isinstance(summary, str) and len(summary) > max_chars:
                logger.info("Trimming summary from %s to %s characters", len(summary), max_chars)
                new_state = dict(state)
                new_state["summary"] = summary[:max_chars]
                return new_state
            prompts = state.get("prompts") or {}
            prompt_summary = prompts.get("summary")
            if isinstance(prompt_summary, str) and len(prompt_summary) > max_chars:
                logger.info(
                    "Trimming prompt summary from %s to %s characters",
                    len(prompt_summary),
                    max_chars,
                )
                prompts = dict(prompts, summary=prompt_summary[:max_chars])
                new_state = dict(state)
                new_state["prompts"] = prompts
                return new_state
        except Exception as exc:  # pragma: no cover
            logger.warning("Soft budget enforcement failed for summary: %s", exc)
        return state


ContextBudgetManagerV10_8 = ContextBudgetManager
ContextBudgetConfigV10_8 = ContextBudgetConfig


# ---------------------------------------------------------------------------
# Cost tracking
# ---------------------------------------------------------------------------


@dataclass
class CostEnvelope:
    """Used to capture cost metadata for arbitration or tuning."""

    amount: float
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class CostTracker:
    """Unified cost tracker.

    - v10_9: span-based performance profiling (start_span/end_span/snapshot)
    - v10_7: aggregated cost accounting (add_cost/log_cost/get_cost_summary)
    """

    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)
    total_cost: float = 0.0
    cost_log: Dict[str, List[float]] = field(default_factory=dict)

    # Span-style timing -------------------------------------------------------

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
        return {"spans": snapshot_spans, "total_cost": self.total_cost}

    # v10_7-style cost accounting --------------------------------------------

    def add_cost(self, amount: float) -> None:
        self.total_cost += amount

    def log_cost(self, workflow_id: str, amount: float) -> None:
        self.cost_log.setdefault(workflow_id, []).append(amount)
        self.add_cost(amount)

    def get_cost_summary(self, workflow_id: str) -> Dict[str, float]:
        entries = self.cost_log.get(workflow_id, [])
        return {
            "workflow_id": workflow_id,
            "total": float(sum(entries)),
            "entries": float(len(entries)),
        }


# ---------------------------------------------------------------------------
# Metrics and precompute
# ---------------------------------------------------------------------------


class MetricsCollector:
    """Collects lightweight runtime metrics."""

    def __init__(self) -> None:
        self.metrics: List[Dict[str, Any]] = []

    def record(
        self,
        name: str,
        value: Any,
        *,
        agent: str | None = None,
        task: str | None = None,
    ) -> None:
        self.metrics.append({"name": name, "value": value, "agent": agent, "task": task})

    def get_average_latency(self, agent_name: str, task_name: str) -> Optional[float]:
        matching = [
            m
            for m in self.metrics
            if m.get("agent") == agent_name
            and m.get("task") == task_name
            and isinstance(m.get("value"), (int, float))
        ]
        if not matching:
            return None
        return sum(m["value"] for m in matching) / len(matching)


class PrecomputeEngine:
    """Executes precomputation hooks for prompts or context."""

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return payload


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------


class PromptTemplateManager:
    """Manages prompt templates with runtime injections."""

    def __init__(self, templates: Optional[Dict[str, str]] = None) -> None:
        self.templates = templates or {
            "default": "Goal: {goal_state}\nFailures: {top_failures}\nContent: {body}",
        }

    def get_template(self, tool_name: str) -> str:
        return self.templates.get(tool_name, self.templates.get("default", ""))

    def render(self, name: str, **kwargs: Any) -> str:
        template = self.get_template(name)
        return template.format(**kwargs)


# ---------------------------------------------------------------------------
# Arbitration and policy tuning
# ---------------------------------------------------------------------------


class ArbitrationEngine:
    """Handles arbitration decisions for multiple candidates."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def choose(self, options: Dict[str, QAOutputModel]) -> Optional[str]:
        if not options:
            return None
        # Stable, deterministic first-key choice
        return next(iter(options))

    def decide(self, stage: str, options: Dict[str, QAOutputModel]) -> Optional[str]:
        choice = self.choose(options)
        self.history.append(
            {"stage": stage, "choice": choice, "options": list(options.keys())}
        )
        return choice


class ArbitrationRecord:
    """Document of an arbitration decision."""

    def __init__(self, chosen: Optional[str], rationale: str = "") -> None:
        self.chosen = chosen
        self.rationale = rationale


class MetricsEnvelope:
    """Simple metrics container for policy tuning."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data


class TuningProfile:
    """Configuration container for policy auto-tuning."""

    def __init__(self, profile: Optional[Dict[str, Any]] = None) -> None:
        self.profile = profile or {}


class PolicyAutoTuner:
    """Adjusts runtime policies based on feedback."""

    def __init__(self, profile: Optional[TuningProfile] = None) -> None:
        self.profile = profile or TuningProfile()

    def tune(self, metrics: MetricsEnvelope) -> None:
        self.profile.profile.update(metrics.data)


class PolicyDecision(StatePatch):
    """Alias for policy-driven state patches."""
    pass


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------


__all__ = [
    # Cache
    "CacheManager",
    "CacheEnvelope",
    "PredictiveCache",
    "PredictiveCacheManager",
    "PredictiveCacheRecord",
    # Self-correction & validation
    "ResponseValidator",
    "SelfCorrectionManager",
    "SelfCorrectionPlan",
    # Budgeting
    "ContextBudget",
    "ContextBudgetConfig",
    "ContextBudgetManager",
    "ContextBudgetConfigV10_8",
    "ContextBudgetManagerV10_8",
    # Cost
    "CostEnvelope",
    "CostTracker",
    # Metrics & precompute
    "MetricsCollector",
    "PrecomputeEngine",
    # Templates
    "PromptTemplateManager",
    # Arbitration & policy
    "ArbitrationEngine",
    "ArbitrationRecord",
    "MetricsEnvelope",
    "PolicyAutoTuner",
    "PolicyDecision",
    "QAOutputModel",
    "TuningProfile",
]
