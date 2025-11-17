"""Service layer components for the v10_7 runtime."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from .exceptions import BudgetExceededError, CacheMiss, ValidationError
from .models import NodeResult, QAOutputModel, StatePatch


class CacheManager:
    """Hybrid cache supporting exact and semantic strategies."""

    def __init__(self):
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


class PredictiveCacheManager:
    """Predictive caching placeholder for speculative retrieval."""

    def prime(self, key: str, value: Any) -> None:
        return None


class SelfCorrectionManager:
    """Handles corrective retries for model responses."""

    def __init__(self, validator: Optional["ResponseValidator"] = None):
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
        if self.validator:
            self.validator.validate(result.payload)
        return result


class ContextBudgetManager:
    """Legacy budget manager tracking token usage."""

    def __init__(self, max_tokens: int = 32000):
        self.max_tokens = max_tokens
        self._used_tokens = 0

    def allocate(self, tokens: int) -> None:
        if self._used_tokens + tokens > self.max_tokens:
            raise BudgetExceededError("Context budget exceeded")
        self._used_tokens += tokens

    def remaining(self) -> int:
        return max(self.max_tokens - self._used_tokens, 0)


class MetricsCollector:
    """Collects lightweight runtime metrics."""

    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []

    def record(self, name: str, value: Any, *, agent: str | None = None, task: str | None = None) -> None:
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


class PromptTemplateManager:
    """Manages prompt templates with runtime injections."""

    def __init__(self, templates: Optional[Dict[str, str]] = None):
        self.templates = templates or {
            "default": "Goal: {goal_state}\nFailures: {top_failures}\nContent: {body}",
        }

    def get_template(self, tool_name: str) -> str:
        return self.templates.get(tool_name, self.templates.get("default", ""))

    def render(self, name: str, **kwargs: Any) -> str:
        template = self.get_template(name)
        return template.format(**kwargs)


class ResponseValidator:
    """Validates model responses."""

    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or {}

    def validate(self, payload: Dict[str, Any]) -> None:
        if self.rules.get("require_answer") and "answer" not in payload:
            raise ValidationError("Missing answer")


class CostTracker:
    """Tracks cost estimates for model invocations."""

    def __init__(self):
        self.cost = 0.0
        self.cost_log: Dict[str, List[float]] = {}

    def add_cost(self, amount: float) -> None:
        self.cost += amount

    def log_cost(self, workflow_id: str, amount: float) -> None:
        self.cost_log.setdefault(workflow_id, []).append(amount)
        self.add_cost(amount)

    def get_cost_summary(self, workflow_id: str) -> Dict[str, float]:
        entries = self.cost_log.get(workflow_id, [])
        return {
            "workflow_id": workflow_id,
            "total": sum(entries),
            "entries": len(entries),
        }


class ArbitrationEngine:
    """Handles arbitration decisions for multiple candidates."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def choose(self, options: Dict[str, QAOutputModel]) -> Optional[str]:
        if not options:
            return None
        return next(iter(options))

    def decide(self, stage: str, options: Dict[str, QAOutputModel]) -> Optional[str]:
        choice = self.choose(options)
        self.history.append({"stage": stage, "choice": choice, "options": list(options.keys())})
        return choice


class MetricsEnvelope:
    """Simple metrics container for tuning."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class TuningProfile:
    """Configuration container for policy auto-tuning."""

    def __init__(self, profile: Optional[Dict[str, Any]] = None):
        self.profile = profile or {}


class PolicyAutoTuner:
    """Adjusts runtime policies based on feedback."""

    def __init__(self, profile: Optional[TuningProfile] = None):
        self.profile = profile or TuningProfile()

    def tune(self, metrics: MetricsEnvelope) -> None:
        self.profile.profile.update(metrics.data)


class CostEnvelope:
    """Used to capture cost metadata for arbitration or tuning."""

    def __init__(self, amount: float, timestamp: Optional[float] = None):
        self.amount = amount
        self.timestamp = timestamp or time.time()


class CacheEnvelope:
    """Annotated cache record container."""

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.cached_at = time.time()


class ArbitrationRecord:
    """Document of an arbitration decision."""

    def __init__(self, chosen: Optional[str], rationale: str = ""):
        self.chosen = chosen
        self.rationale = rationale


class PredictiveCacheRecord(CacheEnvelope):
    """Predictive cache payload wrapper."""

    pass


class PolicyDecision(VQA := StatePatch):
    """Alias for policy-driven state patches."""


class SelfCorrectionPlan(NodeResult):
    """Alias for a corrective node result."""


__all__ = [
    "ArbitrationEngine",
    "ArbitrationRecord",
    "CacheEnvelope",
    "CacheManager",
    "ContextBudgetManager",
    "CostEnvelope",
    "CostTracker",
    "MetricsCollector",
    "MetricsEnvelope",
    "PolicyAutoTuner",
    "PolicyDecision",
    "PredictiveCacheManager",
    "PredictiveCacheRecord",
    "PrecomputeEngine",
    "PromptTemplateManager",
    "QAOutputModel",
    "ResponseValidator",
    "SelfCorrectionManager",
    "SelfCorrectionPlan",
    "TuningProfile",
]
"""Soft context budget enforcement for v10_8 with delegate support."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContextBudgetConfig:
    """Configuration for soft context budgeting."""

    max_episodic_messages: Optional[int] = 50
    max_rag_documents: Optional[int] = 20
    max_summary_chars: Optional[int] = 12000


class ContextBudgetManager:
    """Soft-mode budget manager that wraps a delegate if provided."""

    def __init__(self, config: Optional[ContextBudgetConfig] = None, delegate: Any = None):
        self.config = config or ContextBudgetConfig()
        self.delegate = delegate

    def enforce_all(self, state: Any) -> Any:
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
        max_messages = self.config.max_episodic_messages
        if not max_messages:
            return state
        try:
            memory = state.get("memory") or {}
            episodic = memory.get("episodic") or {}
            conversation = episodic.get("conversation")
            if isinstance(conversation, list) and len(conversation) > max_messages:
                trimmed = conversation[-max_messages:]
                logger.info(
                    "Trimming episodic memory from %s to %s entries", len(conversation), len(trimmed)
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
        max_docs = self.config.max_rag_documents
        if not max_docs:
            return state
        try:
            rag = state.get("rag") or {}
            documents = rag.get("documents")
            if isinstance(documents, list) and len(documents) > max_docs:
                trimmed_docs = documents[:max_docs]
                logger.info("Trimming RAG documents from %s to %s", len(documents), len(trimmed_docs))
                rag = dict(rag, documents=trimmed_docs)
                new_state = dict(state)
                new_state["rag"] = rag
                return new_state
        except Exception as exc:  # pragma: no cover
            logger.warning("Soft budget enforcement failed for RAG history: %s", exc)
        return state

    def _trim_summary(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_chars = self.config.max_summary_chars
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
                    "Trimming prompt summary from %s to %s characters", len(prompt_summary), max_chars
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
"""
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
class PredictiveCache:
    def __init__(self):
        self.cache = {}

    def get(self, signature: str):
        return self.cache.get(signature)

    def set(self, signature: str, value):
        self.cache[signature] = value

    def snapshot(self):
        return self.cache.copy()
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


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
