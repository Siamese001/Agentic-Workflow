# File: core_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
# - UPDATED: create_workflow_context() helper to handle circular
#   dependencies (e.g., ContextBudgetManager needing a client getter).
# - ADDED: MCP client registry and wrap_mcp helper to thread MCP
#   integrations through orchestration layers.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #10): Added A2AMessage and A2AContext to MainGraphState
#   to support agent-to-agent messaging.
# - IMPLEMENTED (Fix #13): CacheManager (LLM) refactored for Semantic Caching.
#   It now uses ChromaDB to find and retrieve semantically similar prompts.
# - IMPLEMENTED (Fix #14): ContextBudgetManager refactored for Smarter Pruning.
#   It now uses an agentic 'summarizer_model' to prune large contexts.
# - IMPLEMENTED (Fix #15): BaseAgent.get_model_client updated for
#   Cost/Latency-Based Routing. It falls back to a simple model
#   if the complex model's average latency (from MetricsCollector) is too high.
# - IMPLEMENTED (Fix #17): Prompts now include a 'REFLECTION' step.
# - IMPLEMENTED (Fix #19): BaseAgent.get_model_client now injects
#   a global GOAL_STATE into all prompts.
# - IMPLEMENTED (Fix #20): PromptTemplateManager refactored to use
#   Cognitive Modes (e.g., "MODE: ANALYTICAL").
# - IMPLEMENTED (Fix #24): PromptTemplateManager now injects the
#   "Top 5 Failures" (from FeedbackLogReader) into agent prompts.
# - IMPLEMENTED (Fix #29): All AsyncBaseModelClient subclasses now
#   perform Idempotency Validation (shadow calls) on cached results.
# - IMPLEMENTED (Fix #30): Added ConstitutionalReviewResult model.
#   PromptTemplateManager has 'constitutional_review' prompt.
# - FIXED: All v10_5 class names/imports updated to v10_7.

import asyncio
import hashlib
import importlib
import json
import logging
import os
import random  # v10.7: Added for Fix #29
import time
from functools import wraps
from typing import TYPE_CHECKING

from chromadb.utils import embedding_functions
from mcp import get_schema, get_tool, sync_context
from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError
from telemetry_v10_7 import log_event

try:
    import anthropic
    import google.generativeai as genai
except ImportError:
    logging.warning("LLM provider libraries (anthropic, google-generativeai) not found. Install them if needed.")
    anthropic = None
    genai = None

from asyncio import TimeoutError as AsyncTimeoutError
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional, TypeVar

# v10.7: Logger name updated
logger = logging.getLogger("core_v10_7")

redis_module = get_tool("redis")
chromadb_module = get_tool("chromadb")
openai_module = get_tool("openai")

AsyncOpenAI = getattr(openai_module, "AsyncOpenAI", None)

if TYPE_CHECKING:  # pragma: no cover - typing aids
    from chromadb import Client as ChromaClientType
    from redis import Redis as RedisType
else:
    RedisType = Any
    ChromaClientType = Any

# ============================================================================
# CONFIGURATION (v10.7: Fixed class name and paths)
# ============================================================================

class ConfigV10_7:
    """Configuration loader for v10.7"""

    def __init__(self, config_path: str = "master_config_v10_7.json"):
        self._config = get_schema(config_path)

        # Validate schema version
        expected_schema = "master_config_v10.7"
        loaded_schema = self._config.get("schema_version")
        if loaded_schema != expected_schema:
            raise ValueError(f"Config schema mismatch. Expected {expected_schema}, got {loaded_schema}")

        logger.info(f"Loaded {loaded_schema} configuration")

    def __getattr__(self, name):
        """Dynamic attribute access for nested config"""
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        section = self._config.get(name)
        if section is None:
            snake_name = name.replace('-', '_')
            section = self._config.get(snake_name)
            if section is None:
                raise AttributeError(f"Config section '{name}' or '{snake_name}' not found")

        return ConfigSection(section)

class ConfigSection:
    """Wrapper for nested config sections"""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        value = self._data.get(name)
        if value is None:
            snake_name = name.replace('-', '_')
            value = self._data.get(snake_name)
            if value is None:
                raise AttributeError(f"Config key '{name}' or '{snake_name}' not found")

        if isinstance(value, dict):
            return ConfigSection(value)
        return value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data

# ============================================================================
# MCP CLIENT REGISTRY (v10.7)
# ============================================================================

@dataclass
class MCPClientSpec:
    """Typed representation of a configured MCP client."""

    name: str
    provider: str = "stub"
    module: str | None = None
    class_name: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    optional: bool = False


class MCPClientStub:
    """Fallback stub MCP client used when no concrete implementation exists."""

    def __init__(self, name: str, parameters: dict[str, Any] | None = None):
        self.name = name
        self.parameters = parameters or {}

    def __repr__(self) -> str:
        details = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"<MCPClientStub name={self.name} {details}>"


def _parse_mcp_client_specs(raw_specs: list[dict[str, Any]]) -> list[MCPClientSpec]:
    """Validate and normalise MCP client specifications."""

    specs: list[MCPClientSpec] = []
    for raw in raw_specs:
        if not isinstance(raw, dict):
            raise ValueError("Each MCP client entry must be a mapping.")

        name = raw.get("name")
        if not name or not isinstance(name, str):
            raise ValueError("MCP client entries require a string 'name'.")

        parameters = raw.get("parameters", {})
        if parameters is None:
            parameters = {}
        if not isinstance(parameters, dict):
            raise ValueError(f"MCP client '{name}' parameters must be a mapping.")

        spec = MCPClientSpec(
            name=name,
            provider=str(raw.get("provider", "stub")),
            module=raw.get("module"),
            class_name=raw.get("class_name") or raw.get("class"),
            parameters=parameters,
            optional=bool(raw.get("optional", False)),
        )
        specs.append(spec)

    return specs


def _instantiate_mcp_client(spec: MCPClientSpec) -> Any:
    """Create an MCP client instance from a validated spec."""

    if spec.provider == "stub" and not spec.module:
        return MCPClientStub(spec.name, spec.parameters)

    if spec.module:
        module = importlib.import_module(spec.module)
        class_name = spec.class_name or spec.provider
        try:
            client_cls = getattr(module, class_name)
        except AttributeError as exc:
            raise AttributeError(
                f"Module '{spec.module}' does not expose '{class_name}' for MCP client '{spec.name}'."
            ) from exc
        return client_cls(**spec.parameters)

    if spec.provider == "redis":
        redis_cls = getattr(redis_module, "Redis", None)
        if callable(redis_cls):
            return redis_cls(**spec.parameters)
        return redis_module(**spec.parameters) if callable(redis_module) else MCPClientStub(spec.name, spec.parameters)

    if spec.provider == "chromadb":
        persistent_cls = getattr(chromadb_module, "PersistentClient", None)
        if callable(persistent_cls):
            return persistent_cls(**spec.parameters)
        client_cls = getattr(chromadb_module, "Client", None)
        if callable(client_cls):
            return client_cls(**spec.parameters)
        return MCPClientStub(spec.name, spec.parameters)

    # Default to stub for unknown providers
    return MCPClientStub(spec.name, {"provider": spec.provider, **spec.parameters})

# ============================================================================
# EXCEPTION HIERARCHY (v10.7: Preserved)
# ============================================================================

class WorkflowError(Exception): pass
class ModelAPIError(WorkflowError): pass
class JSONParsingError(WorkflowError): pass
class ValidationError(WorkflowError): pass
class FileIOError(WorkflowError): pass
class CostCeilingExceededError(WorkflowError): pass
class CircuitBreakerOpenError(WorkflowError): pass
class PydanticSchemaError(ValidationError): pass
class WorkflowTimeoutError(WorkflowError, AsyncTimeoutError): pass
class MCPClientInitializationError(WorkflowError): pass

class CircuitBreaker:
    """v10.7: Circuit breaker for batch processing."""
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            self.logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")

    def check(self):
        if self.is_open:
            raise CircuitBreakerOpenError(f"Circuit breaker open after {self.failure_count} failures")

# ============================================================================
# v10.7: PYDANTIC MODELS (Added Constitutional AI)
# ============================================================================

# Define a generic TypeVar for the Pydantic models
T_BaseModel = TypeVar('T_BaseModel', bound=BaseModel)

class BaseToolOutput(BaseModel):
    status: str = Field("success", description="Indicates tool execution status")

# --- Agent Tools Models (15 tools) ---
class DraftStrategyOutput(BaseToolOutput):
    feedback: str = Field(..., description="Strategic feedback on the draft")
class RedTeamOutput(BaseToolOutput):
    weaknesses_found: list[str] = Field(..., description="List of identified weaknesses")
class RefineSectionOutput(BaseToolOutput):
    refined_text: str = Field(..., description="The new, refined text for the section")
class AddMetricsOutput(BaseToolOutput):
    suggestions: list[str] = Field(..., description="Specific suggestions for adding metrics")
class QAClaimOutput(BaseToolOutput):
    unsupported_claims: int = Field(..., ge=0, description="Count of claims not supported by the master resume")
    feedback: str = Field(..., description="NLI feedback and analysis")
class QAToneOutput(BaseToolOutput):
    tone_match: bool = Field(..., description="Whether the draft's tone matches the required tone")
    current_tone: str = Field(..., description="The detected tone of the draft")
class QAThematicAlignmentOutput(BaseToolOutput):
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0 for thematic alignment")
    feedback: str = Field(..., description="Feedback on alignment")
class QASemanticEntailmentOutput(BaseToolOutput):
    entailment_score: float = Field(..., ge=0.0, le=1.0, description="Semantic entailment score with the job description")
class QANarrativeThreadOutput(BaseModel):
    narrative_clear: bool = Field(..., description="Whether a clear career narrative was detected")
class QAJDSkillsOutput(BaseToolOutput):
    keyword_coverage: float = Field(..., ge=0.0, le=1.0, description="Percentage of JD keywords found in the draft")
    missing_keywords: list[str] = Field(..., description="List of important missing keywords")
class QASignalScoreOutput(BaseToolOutput):
    avg_signal_score: float = Field(..., ge=0.0, le=10.0, description="Average signal-to-noise score (0-10)")
class QATenureOutput(BaseToolOutput):
    gaps_found: int = Field(..., ge=0, description="Number of unexplained tenure gaps")
    overlaps_found: int = Field(..., ge=0, description="Number of overlapping job dates")
class QAMissedOpportunitiesOutput(BaseToolOutput):
    opportunities_found: list[str] = Field(..., description="List of relevant experiences from master resume that were omitted")
class QAAdversarialOutput(BaseToolOutput):
    red_flags: list[str] = Field(..., description="List of red flags a skeptical hiring manager would find")
class QABiasOutput(BaseModel):
    bias_detected: bool
    patterns: list[str]
    bias_score: float
    dynamic_rules_applied: int

# --- Agent Stacks Models ---
class PlannerAssessment(BaseModel):
    planner_name: str = Field(..., description="Name of the specialist planner issuing the assessment")
    vote: str = Field(..., description="Planner vote (e.g., 'approve', 'revise', 'escalate')")
    rationale: str = Field(..., description="Summary of why the planner issued this vote")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the vote (0.0-1.0)")
    recommended_actions: list[str] = Field(default_factory=list, description="Optional action items suggested by the planner")


class ScenarioSimulationResult(BaseModel):
    scenario_name: str = Field(..., description="Name of the simulated scenario stress test")
    risk_level: str = Field(..., description="Qualitative risk classification (e.g., low, medium, high)")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Estimated impact score between 0 and 1")
    summary: str = Field(..., description="Short narrative of simulation findings")
    mitigation_actions: list[str] = Field(default_factory=list, description="Recommended mitigations derived from the scenario")


class StrategyPlan(BaseModel):
    strategy_name: str = Field(..., description="A brief, descriptive name for the strategy")
    focus_areas: list[str] = Field(..., description="The main themes to emphasize (e.g., 'AI Leadership', 'Technical Deep-Dive')")
    key_achievements_to_highlight: list[str] = Field(..., description="Specific achievements from the master resume to feature")
    tone: str = Field(..., description="The desired tone (e.g., 'professional', 'technical', 'leadership')")
    planner_assessments: list[PlannerAssessment] = Field(default_factory=list, description="Assessments gathered from specialist planners")
    aggregated_decision: str = Field("undecided", description="Coordinator decision synthesized from planner votes")
    aggregated_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score for the aggregated decision")
    aggregated_rationale: str | None = Field(None, description="Coordinator rationale for the aggregated decision")
    feedback_signals: list[str] = Field(default_factory=list, description="Signals or adjustments applied from downstream feedback")
    scenario_simulations: list[ScenarioSimulationResult] = Field(default_factory=list, description="Stress test results for candidate strategy")
    coordinator_summary: str | None = Field(None, description="High-level summary generated by the strategy coordinator")
class GeneratedPrompts(BaseModel):
    bullet_generation_prompt: str
    critique_prompt: str
class BulletList(BaseModel):
    verified_bullets: list[str] = Field(..., description="List of fact-checked, high-quality bullets")
class CritiqueResult(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score from 0-10")
    suggestions: list[str] = Field(..., description="Specific suggestions for improvement")
class HILAmbiguityReport(BaseModel):
    ambiguity_detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    question_for_human: str = Field(..., description="The specific question to ask the human")


class PersonaReviewDecision(BaseModel):
    persona: str = Field(..., description="Persona name (e.g., Legal, Brand, SME)")
    approval: bool = Field(..., description="True if the persona approves the change")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in the persona decision")
    key_concerns: list[str] = Field(default_factory=list, description="Top issues raised by the persona")
    proposed_actions: list[str] = Field(default_factory=list, description="Specific actions requested by the persona")
    escalation_recommended: bool = Field(
        False,
        description="True if the persona recommends escalating to a specialist human reviewer"
    )


class PersonaConsensus(BaseModel):
    approved: bool = Field(..., description="True if consensus favors accepting the edit")
    rationale: str = Field(..., description="Narrative summary of the negotiation outcome")
    negotiated_actions: list[str] = Field(default_factory=list, description="Actions agreed upon during negotiation")
    persona_votes: list[PersonaReviewDecision] = Field(
        default_factory=list,
        description="Detailed breakdown of each persona's vote and rationale"
    )


class HILFeedbackIntent(BaseModel):
    intent_id: str = Field(..., description="Stable identifier for the clustered feedback intent")
    summary: str = Field(..., description="Human-readable description of the intent")
    severity: str = Field(..., description="Qualitative severity (e.g., 'critical', 'minor')")
    recommended_owner: str = Field(..., description="Suggested owner (Strategy, Drafting, Legal, etc.)")
    exemplar_quotes: list[str] = Field(default_factory=list, description="Representative human quotes for the intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the clustering")


class HILReconciliationResult(BaseModel):
    integrated_text: str = Field(..., description="Reconciled text ready to merge into the draft")
    change_log: list[str] = Field(default_factory=list, description="Bullet log of applied changes")
    unresolved_questions: list[str] = Field(default_factory=list, description="Open questions that need human follow-up")


class HILFeedbackRoute(BaseModel):
    next_step: str = Field(..., description="The graph node to jump to (e.g., 'STRATEGY', 'DRAFTING', 'INJECT_EDIT')")
    payload: str | None = Field(None, description="Corrected text or data from the human")
    intent_clusters: list[HILFeedbackIntent] = Field(default_factory=list, description="Clustered intents extracted from human feedback")
    delegated_specialists: list[str] = Field(default_factory=list, description="List of human specialists requested for escalation")
    persona_consensus: PersonaConsensus | None = Field(None, description="Negotiated consensus between virtual personas")
    reconciliation: HILReconciliationResult | None = Field(
        None,
        description="Latest reconciliation result from specialist feedback"
    )

# v10.7 (Fix #30): New model for Constitutional AI
class ConstitutionalReviewResult(BaseModel):
    review_passed: bool = Field(..., description="True if the output passes all constitutional principles")
    violations_found: list[str] = Field(..., description="A list of principles that were violated")
    feedback: str = Field(..., description="Specific feedback on how to correct the violations")

# ============================================================================
# v10.7: RESILIENCE & OBSERVABILITY (Preserved)
# ============================================================================

def exponential_backoff_retry(max_retries: int = 3, initial_delay: float = 1.0):
    """v10.7: Decorator for async node functions."""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ModelAPIError, JSONParsingError, PydanticSchemaError, asyncio.TimeoutError) as e:
                    logger.warning(f"Node {func.__name__} failed (Attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt + 1 == max_retries:
                        logger.error(f"Node {func.__name__} failed permanently after {max_retries} attempts.")
                        raise

                    sleep_time = delay * (2 ** attempt)
                    logger.info(f"Retrying {func.__name__} in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
            raise WorkflowError(f"Node {func.__name__} failed after max retries")
        return wrapper
    return decorator

def async_timeout(seconds: int):
    """v10.7: Decorator to enforce a timeout on an async node."""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=float(seconds))
            except AsyncTimeoutError as e:
                raise WorkflowTimeoutError(f"Node {func.__name__} timed out after {seconds}s") from e
        return wrapper
    return decorator


def get_timeout_decorator(timeout_seconds: float) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Compatibility wrapper retained for orchestration helpers."""

    return async_timeout(int(timeout_seconds))


def _extract_workflow_context(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Optional['WorkflowContext']:
    for arg in args:
        if isinstance(arg, WorkflowContext):
            return arg
    context = kwargs.get("workflow_context")
    if isinstance(context, WorkflowContext):
        return context
    return None


def update_context(context: Optional['WorkflowContext']) -> None:
    """Synchronise the workflow context with the MCP runtime."""

    if context is None:
        return
    try:
        sync_context(context, scope="workflow")
    except Exception as exc:  # pragma: no cover - sync failures should not break flow
        logger.debug("Context sync skipped: %s", exc)


def wrap_mcp(func: Callable | None = None, *, force: bool = False) -> Callable:
    """Decorator that ensures MCP clients are initialised for node handlers."""

    if func is None:
        return lambda inner: wrap_mcp(inner, force=force)

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = _extract_workflow_context(args, kwargs)
            if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
                context.ensure_mcp_clients()
            result = await func(*args, **kwargs)
            update_context(context)
            return result

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        context = _extract_workflow_context(args, kwargs)
        if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
            context.ensure_mcp_clients()
        result = func(*args, **kwargs)
        update_context(context)
        return result

    return sync_wrapper

class ContextBudgetManager:
    """
    v10.7 (Fix #14): Manages context window limits using agentic pruning.
    """
    def __init__(self,
                 config: ConfigV10_7,
                 model_client_getter: Callable[..., 'AsyncBaseModelClient']
                ):
        self.default_limit = config.performance_config.default_token_limit
        self.buffer = 0.2 # 20% buffer
        self.logger = logging.getLogger(f"{__name__}.ContextBudgetManager")
        self.config = config
        self.get_model_client = model_client_getter

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    async def _prune_agentic(self, document: str, max_tokens: int) -> str:
        """v10.7 (Fix #14): Uses an LLM to prune text."""
        self.logger.warning(f"Context > {max_tokens} tokens. Pruning agentically...")
        try:
            client = self.get_model_client(
                self.config.model_config.summarizer_model.provider,
                self.config.model_config.summarizer_model.model_name
            )
            # v10.7 NOTE: We cannot use PromptTemplateManager here as it
            # creates a circular dependency. We define the prompt inline.
            prompt = f"""
            MODE: ANALYTICAL
            TASK: You are a context pruner. Summarize the following document
            into its essential points. The output *must* be less than {max_tokens * 3} characters.
            DOCUMENT:
            {document}

            SUMMARY:
            """

            response = await client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_config.summarizer_model.temperature
            )
            pruned_doc = response.get("content")

            if not isinstance(pruned_doc, str) or not pruned_doc.strip():
                raise TypeError("Summarizer returned empty or non-string content")

            pruned_tokens = self._estimate_tokens(pruned_doc)

            # Final fallback truncation if the summarizer still overshoots the budget
            if pruned_tokens > max_tokens:
                self.logger.warning(
                    "Agentic pruning output still above budget (%s > %s tokens). Applying truncation fallback.",
                    pruned_tokens,
                    max_tokens,
                )
                return self._prune_truncate(pruned_doc, max_tokens, label="AGENTIC_TRUNCATION")

            return f"{pruned_doc}\n\n[... DOCUMENT PRUNED (AGENTIC) ...]"

        except Exception as e:
            self.logger.error("Agentic pruning failed: %s. Falling back to truncation.", e, exc_info=True)
            return self._prune_truncate(document, max_tokens, label="AGENTIC_FAILURE")

    def _prune_truncate(self, document: str, max_tokens: int, *, label: str = "TRUNCATION") -> str:
        """v10.7: Simple truncation fallback."""
        max_chars = max_tokens * 4
        pruned_doc = document[:max_chars]
        self.logger.warning(f"Context truncated to {max_tokens} tokens.")
        return f"{pruned_doc}\n\n[... DOCUMENT PRUNED ({label}) ...]"

    async def prune(self, document: str, max_tokens: int | None = None) -> str:
        if max_tokens is None:
            max_tokens = self.default_limit

        token_limit_with_buffer = int(max_tokens * (1.0 - self.buffer))
        estimated_tokens = self._estimate_tokens(document)

        if estimated_tokens <= token_limit_with_buffer:
            return document

        # v10.7 (Fix #14): Use agentic pruning
        return await self._prune_agentic(document, token_limit_with_buffer)

class MetricsCollector:
    """v10.7: In-memory collector for agent/tool observability."""
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.metrics: list[dict[str, Any]] = []
        self.log_path = "./logs/metrics_v10_7.jsonl"
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            self.logger.info(f"Metrics logging to {self.log_path}")
        except OSError as e:
            self.logger.error(f"Could not create log directory for metrics: {e}")

    def record(self, agent_name: str, task_name: str, duration_ms: float, success: bool, error: str | None = None, metadata: dict[str, Any] | None = None):
        metric = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "task_name": task_name,
            "duration_ms": duration_ms,
            "success": success,
            "error": error,
            "metadata": metadata or {}
        }
        self.metrics.append(metric)
        try:
            with open(self.log_path, 'a') as f:
                json.dump(metric, f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write metric to log: {e}")

    def get_summary(self) -> list[dict[str, Any]]:
        return self.metrics

    def get_average_latency(self, agent_name: str, task_name: str) -> float | None:
        """v10.7 (Fix #15): Gets average latency for a specific task."""
        latencies = [
            m['duration_ms'] for m in self.metrics
            if m['agent_name'] == agent_name and m['task_name'] == task_name and m['success']
        ]
        if not latencies:
            return None
        return sum(latencies) / len(latencies)

def track_metrics(task_name: str):
    """v10.7: Decorator for agent/tool run/run_async methods."""
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(self: 'BaseAgent', *args, **kwargs) -> Any:
                if not (hasattr(self, 'context') and hasattr(self.context, 'metrics_collector')):
                    logger.warning(f"@track_metrics on {func.__name__} requires 'self.context.metrics_collector'")
                    return await func(self, *args, **kwargs)

                collector = self.context.metrics_collector
                agent_name = self.__class__.__name__
                start_time = time.perf_counter()

                try:
                    result = await func(self, *args, **kwargs)
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(agent_name, task_name, duration_ms, success=True, metadata=kwargs)
                    return result
                except Exception as e:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(agent_name, task_name, duration_ms, success=False, error=str(e), metadata=kwargs)
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(self: 'BaseAgent', *args, **kwargs) -> Any:
                if not (hasattr(self, 'context') and hasattr(self.context, 'metrics_collector')):
                    logger.warning(f"@track_metrics on {func.__name__} requires 'self.context.metrics_collector'")
                    return func(self, *args, **kwargs)

                collector = self.context.metrics_collector
                agent_name = self.__class__.__name__
                start_time = time.perf_counter()

                try:
                    result = func(self, *args, **kwargs)
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(agent_name, task_name, duration_ms, success=True, metadata=kwargs)
                    return result
                except Exception as e:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(agent_name, task_name, duration_ms, success=False, error=str(e), metadata=kwargs)
                    raise
            return sync_wrapper
    return decorator

class SemanticValidator:
    """v10.7: Local, deterministic validation service."""
    def __init__(self, metrics_collector: MetricsCollector):
        self.logger = logging.getLogger(f"{__name__}.SemanticValidator")
        self.metrics = metrics_collector

    def check_word_count(self, text: str, min_words: int, max_words: int, llm_reported_count: int | None = None, workflow_id: str = "") -> tuple[bool, str]:
        deterministic_count = len(text.split())

        if llm_reported_count is not None:
            discrepancy = abs(deterministic_count - llm_reported_count)
            if discrepancy > (deterministic_count * 0.1): # Over 10% diff
                self.logger.warning(f"Word count discrepancy! Deterministic: {deterministic_count}, LLM: {llm_reported_count}")
                self.metrics.record(
                    agent_name="SemanticValidator",
                    task_name="word_count_discrepancy",
                    duration_ms=0,
                    success=True,
                    metadata={
                        "workflow_id": workflow_id,
                        "deterministic_count": deterministic_count,
                        "llm_reported_count": llm_reported_count,
                        "discrepancy": discrepancy
                    }
                )

        if min_words <= deterministic_count <= max_words:
            return (True, f"Word count OK ({deterministic_count})")
        else:
            return (False, f"Word count FAILED. Expected {min_words}-{max_words}, got {deterministic_count}.")

# ============================================================================
# v10.7: CENTRALIZED PROMPT FORMATTER (Fix #14, #19, #24)
# ============================================================================

async def _format_prompt_with_defaults(
    template: str,
    tool_input: dict[str, Any],
    budget_manager: ContextBudgetManager,
    goal_state: str,         # v10.7 (Fix #19)
    top_failures: list[str]  # v10.7 (Fix #24)
) -> str:
    """
    v10.7: Centralized helper.
    Injects Goal State, Top Failures, and performs agentic pruning.
    """

    # v10.7 (Fix #19, #24): Inject Goal and Failures
    goal_injection = f"GLOBAL_GOAL: {goal_state}\n"
    failure_injection = ""
    if top_failures:
        failure_list = "\n".join(f"- {f}" for f in top_failures)
        failure_injection = f"BEWARE: System analysis shows top failures are:\n{failure_list}\n"

    # v10.7 (Fix #14): Use agentic pruning for large context fields
    master_resume = await budget_manager.prune(json.dumps(tool_input.get('master_resume')), 4000)
    draft_text = await budget_manager.prune(json.dumps(tool_input.get('draft_text')), 4000)
    job_description = await budget_manager.prune(json.dumps(tool_input.get('job_description')), 4000)

    all_keys = {
        "goal_state": goal_injection,       # Fix #19
        "top_failures": failure_injection,  # Fix #24

        "style_guide": tool_input.get('style_guide', "Default style: professional."),
        "draft": json.dumps(tool_input.get('draft')),
        "strategy": json.dumps(tool_input.get('strategy')),
        "section_text": json.dumps(tool_input.get('section_text')),
        "critique": json.dumps(tool_input.get('critique')),
        "critique_2": json.dumps(tool_input.get('critique_2')),
        "bullets": json.dumps(tool_input.get('bullets')),
        "master_resume": master_resume,
        "draft_text": draft_text,
        "required_tone": json.dumps(tool_input.get('strategy', {}).get('tone', 'N/A')),
        "job_description": job_description,

        "query": tool_input.get('query', ''),
        "candidates": json.dumps(tool_input.get('candidates', [])),

        "experience": json.dumps(tool_input.get('experience')),

        "job_title": tool_input.get('job_title', 'N/A'),
        "company": tool_input.get('company', 'N/A'),
        "branch_num": tool_input.get('branch_num', 1),
        "total_branches": tool_input.get('total_branches', 1),
        "num_branches": tool_input.get('num_branches', 1),
        "branches_json": json.dumps(tool_input.get('branches_json', [])),

        "complexity": tool_input.get('complexity', 'unknown'),
        "user_input": tool_input.get('user_input', ''),
        "human_feedback": tool_input.get('human_feedback', ''),

        "hypothesis": json.dumps(tool_input.get('hypothesis', {})),
        "patterns": json.dumps(tool_input.get('patterns', [])),
        "proposal": json.dumps(tool_input.get('proposal', {})),
        "log_data": json.dumps(tool_input.get('log_data', {})),
        "feedback_log": tool_input.get('feedback_log', ''),
        "preference_log": tool_input.get('preference_log', ''),
        "generated_tool_code": tool_input.get('generated_tool_code', ''),

        "instruction": tool_input.get('instruction', ''),
        "context": json.dumps(tool_input.get('context', {})),
        "content": tool_input.get('content', ''),

        "final_draft": tool_input.get('final_draft', ''), # v10.7 (Fix #30)
        "constitution": tool_input.get('constitution', ''), # v10.7 (Fix #30)
    }

    return template.format(**all_keys)

# ============================================================================
# v10.7: PROMPT TEMPLATE MANAGER (Fix #17, #19, #20, #24, #30)
# ============================================================================

class PromptTemplateManager:
    """
    v10.7: Manages all 30+ system prompts.
    FIXED: Prompts updated for Cognitive Modes, Goal State, and Failure Injection.
    """

    def __init__(self, feedback_reader: 'FeedbackLogReader'):
        self.logger = logging.getLogger(f"{__name__}.PromptTemplateManager")
        self.templates = self._load_templates()
        # v10.7 (Fix #24): Get top failures on init
        self.top_failures = self._get_top_failures(feedback_reader)
        # v10.7 (Fix #19): Define global goal state
        self.goal_state = "Create a verified, high-quality, customized resume artifact."

    def _get_top_failures(self, feedback_reader: 'FeedbackLogReader') -> list[str]:
        """v10.7 (Fix #24): Analyzes feedback log for top failure patterns."""
        try:
            failures = feedback_reader.get_failures(max_entries=100)
            failure_counts = {}
            for f in failures:
                key = f"{f.agent_name}::{f.task}"
                failure_counts[key] = failure_counts.get(key, 0) + 1

            sorted_failures = sorted(failure_counts.items(), key=lambda item: item[1], reverse=True)
            return [f[0] for f in sorted_failures[:5]]
        except Exception as e:
            self.logger.error(f"Could not get top failures: {e}")
            return ["Unknown (error in log read)"]

    def get_template(self, tool_name: str) -> str:
        template = self.templates.get(tool_name)
        if not template:
            self.logger.error(f"No prompt template found for tool: {tool_name}")
            return "ERROR: PROMPT NOT FOUND FOR {tool_name}"

        # v10.7 (Fix #19, #24): Inject Goal State and Failures into *every* prompt
        injected_template = (
            f"{{goal_state}}\n"       # Fix #19
            f"{{top_failures}}\n"     # Fix #24
            f"-------------------\n"
            f"{template}"
        )
        return injected_template

    def _load_templates(self) -> dict[str, str]:
        """
        v10.7 (Fix #17, #20): Defines all system prompts using Cognitive Modes.
        """
        templates = {
            # === DRAFTING TOOLS ===
            "review_draft_strategy": """
MODE: ANALYTICAL
TASK: Review the draft against the strategy.
{style_guide}
Strategy: {strategy}
Draft: {draft}
Example: {{"status": "success", "feedback": "Draft summary is weak..."}}
REFLECTION: Is the feedback actionable?
Your Analysis:
""",

            "red_team_critique": """
MODE: ADVERSARIAL
TASK: Find all weaknesses in this draft.
{style_guide}
Draft: {draft}
Example: {{"status": "success", "weaknesses_found": ["'Led team' is weak."]}}
REFLECTION: Is the critique constructive?
Your Analysis:
""",

            "refine_section": """
MODE: SYNTHESIS
TASK: Rewrite the section to synthesize and resolve both critiques.
{style_guide}
Section: {section_text}
Critique 1 (Strategist): {critique}
Critique 2 (Red Team): {critique_2}
Example: {{"status": "success", "refined_text": "Drove 10% profit growth."}}
REFLECTION: Does the new text resolve both critiques?
Your Refinement:
""",

            "add_metrics": """
MODE: ANALYTICAL
TASK: Review bullets and suggest opportunities to add metrics.
{style_guide}
Bullets: {bullets}
Example: {{"status": "success", "suggestions": ["Quantify 'Led team' with number..."]}}
REFLECTION: Are these suggestions specific?
Your Suggestions:
""",

            # === QA TOOLS (11) ===
            "validate_claims": "MODE: NLI. Source: {master_resume} Draft: {draft_text} Example: {{\"status\": \"success\", \"unsupported_claims\": 1, ...}} REFLECTION: Is this claim truly unsupported? Your NLI Analysis:",
            "validate_tone": "MODE: ANALYTICAL. Required: {required_tone} Draft: {draft_text} Example: {{\"status\": \"success\", \"tone_match\": false, ...}} REFLECTION: Is the tone mismatch severe? Your Analysis:",
            "validate_thematic_alignment": "MODE: ANALYTICAL. Strategy: {strategy} Draft: {draft_text} Example: {{\"status\": \"success\", \"alignment_score\": 0.2, ...}} REFLECTION: Why is the alignment score low? Your Analysis:",
            "validate_semantic_entailment": "MODE: NLI. JD: {job_description} Draft: {draft_text} Example: {{\"status\": \"success\", \"entailment_score\": 0.5, ...}} REFLECTION: Does the draft entail the JD? Your Analysis:",
            "validate_narrative_thread": "MODE: SYNTHESIS. Draft: {draft_text} Example: {{\"narrative_clear\": true}} REFLECTION: What is the narrative? Your Analysis:",
            "validate_jd_skills": "MODE: ANALYTICAL. JD: {job_description} Draft: {draft_text} Example: {{\"status\": \"success\", \"keyword_coverage\": 0.67, ...}} REFLECTION: Are the missing keywords critical? Your Analysis:",
            "validate_signal_score": "MODE: ANALYTICAL. Draft: {draft_text} Example: {{\"status\": \"success\", \"avg_signal_score\": 5.0, ...}} REFLECTION: Which bullets are pure noise? Your Analysis:",
            "validate_tenure": "MODE: ANALYTICAL. Draft: {draft_text} Example: {{\"status\": \"success\", \"gaps_found\": 1, ...}} REFLECTION: Are the dates logical? Your Analysis:",
            "find_missed_opportunities": "MODE: ANALYTICAL. Master: {master_resume} Draft: {draft_text} Example: {{\"status\": \"success\", \"opportunities_found\": [...], ...}} REFLECTION: Is this opportunity relevant? Your Analysis:",
            "adversarial_review": "MODE: ADVERSARIAL. Act as skeptical hiring manager. Draft: {draft_text} Example: {{\"status\": \"success\", \"red_flags\": [...], ...}} REFLECTION: Is this red flag a dealbreaker? Your Analysis:",
            "validate_bias": "(This is a local tool, this prompt is a placeholder) Draft: {draft_text}",

            # === AGENT STACKS ===
            "strategy_tot_branch": """
MODE: STRATEGY
TASK: Generate a resume strategy for this job.
Job Title: {job_title}
Company: {company}
Job Description: {job_description}
This is branch {branch_num} of {total_branches}. Be creative and distinct.
{style_guide}
Example: {{"strategy_name": "AI Visionary", "focus_areas": [...], "tone": "leadership"}}
REFLECTION: Is this strategy unique from other branches?
Your Strategy Branch:
""",

            "strategy_tot_vote": """
MODE: ANALYTICAL
TASK: Vote for the single best strategy branch.
Job Description: {job_description}
Branches: {branches_json}
Example: {{"best_branch_id": "branch_1", "reason": "Branch 1 is most aligned."}}
REFLECTION: Why is this branch better than the others?
Your Vote:
""",

            "prompt_engineer": """
MODE: META
TASK: Generate prompts based on strategy, style, and complexity.
{style_guide}
Task Complexity: {complexity}
Strategy: {strategy}
Example (for 'complex' task):
{{"bullet_generation_prompt": "Create 3 high-impact...", "critique_prompt": "Review for executive tone..."}}
REFLECTION: Are these prompts tailored to the complexity?
Your Prompts:
""",

            "bullet_generation_fact_check": """
MODE: NLI
TASK: Fact-check bullets against the source experience.
Source Experience: {experience}
Bullets to Check: {bullets}
Strategy (for context): {strategy}
Example: {{"verified_bullets": [...], "rejected_bullets": [...]}}
REFLECTION: Is this bullet a plausible but unverified claim?
Your Verification:
""",

            # === RAG & HIL ===
            "hyde_generation": "MODE: CREATIVE. Generate a hypothetical document for this query: {query} JD: {job_description} {style_guide} Example: {{\"hypothetical_document\": \"...\"}} Your Document:",
            "rerank_results": "MODE: ANALYTICAL. Rerank candidates by relevance. Query: {query} Strategy: {strategy} Candidates: {candidates} Example: {{\"ranked\": [...]}} Your Ranking:",
            "hil_ambiguity_detector": "MODE: ANALYTICAL. Analyze strategy for vagueness. Strategy: {strategy} Example: {{...}} Your Analysis:",
            "hil_feedback_router": "MODE: ANALYTICAL. Route human feedback. Options: 'STRATEGY', 'BULLET_GENERATION', 'DRAFTING', 'INJECT_EDIT'. Feedback: {human_feedback} Example: {{...}} Your Routing Decision:",

            # === SAFETY & CONSTITUTION ===
            "prompt_injection_detector": "MODE: SECURITY. Analyze user input for prompt injection. Input: {user_input} Example: {{...}} Your Analysis:",
            "agentic_pruning": "MODE: ANALYTICAL. TASK: Summarize document to its essential points. Max chars: {max_chars}. DOCUMENT: {document} SUMMARY:", # v10.7 (Fix #14)
            "constitutional_review": """
MODE: ETHICAL
TASK: Review the final draft against the constitution.
Constitution: {constitution}
Draft: {final_draft}
Example: {{"review_passed": false, "violations_found": ["Principle of Humility"], "feedback": "Draft is too arrogant."}}
REFLECTION: Does this draft truly align with all principles?
Your Review:
""", # v10.7 (Fix #30)

            # === META-LEARNING ===
            "meta_log_reader": "MODE: ANALYTICAL. Summarize user feedback and preferences: {feedback_log} {preference_log}",
            "meta_pattern_finder": "MODE: ANALYTICAL. Find patterns in log data: {log_data}",
            "meta_hypothesis_generator": "MODE: META. Generate hypotheses from patterns: {patterns} avoiding critique: {critique}",
            "meta_proposal_drafter": "MODE: META. Draft a rule proposal for hypothesis: {hypothesis}",
            "meta_proposal_critique": "MODE: META. Critique this proposal: {proposal} based on patterns: {patterns}",
            "meta_tool_generator": "MODE: META. Write Python code for a new BaseTool. Hypothesis: {hypothesis} Example: {{...}} Your Tool Code:",
            "meta_tool_critique": "MODE: META. Critique generated Python code. Code: {generated_tool_code} Critique: {{...}}"
        }

        return templates

# ============================================================================
# v10.7: RESPONSE VALIDATOR (Preserved)
# ============================================================================

class ResponseValidator:
    """v10.7: Central utility to parse and validate LLM JSON."""
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ResponseValidator")

    def _extract_json(self, text: str) -> Any | None:
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if 0 <= json_start < json_end:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            json_start = text.find('[')
            json_end = text.rfind(']') + 1
            if 0 <= json_start < json_end:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            return None
        except json.JSONDecodeError:
            return None

    def validate(
        self,
        response_content: Any,
        output_model: Any
    ) -> tuple[Any | None, str | None]:
        try:
            if isinstance(response_content, str):
                json_content = self._extract_json(response_content)
                if json_content is None:
                    raise JSONParsingError(f"No valid JSON object or array found in response: {response_content[:100]}...")
            else:
                json_content = response_content

            if isinstance(output_model, type) and issubclass(output_model, BaseModel):
                try:
                    validated_model = output_model.model_validate(json_content)
                    return validated_model, None
                except PydanticValidationError as e:
                    self.logger.warning(f"Pydantic validation failed for {output_model.__name__}: {e}")
                    raise PydanticSchemaError(f"Validation failed for {output_model.__name__}: {e}. Got: {json_content}")
            elif output_model == dict or output_model == list:
                if isinstance(json_content, output_model):
                    return json_content, None
                else:
                    raise PydanticSchemaError(f"Validation failed: Expected {output_model.__name__}, got {type(json_content)}")
            elif isinstance(output_model, tuple):
                for model_type in output_model:
                    if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                        try:
                            validated_model = model_type.model_validate(json_content)
                            return validated_model, None
                        except PydanticValidationError:
                            continue
                    elif (model_type == dict or model_type == list) and isinstance(json_content, model_type):
                        return json_content, None
                raise PydanticSchemaError(f"Validation failed: Content did not match any type in {output_model}. Got: {type(json_content)}")
            else:
                raise PydanticSchemaError(f"Unsupported output_model type for validation: {output_model}")
        except (JSONParsingError, PydanticSchemaError) as e:
            self.logger.error(f"Response validation failed: {e}")
            return None, str(e)

# ============================================================================
# ROW 7: FEEDBACK LOG READER (v10.7: Added failure getter)
# ============================================================================

@dataclass
class FeedbackEntry:
    timestamp: str
    workflow_id: str
    agent_name: str
    task: str
    feedback_type: str # "success", "failure", "warning"
    details: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

class FeedbackLogReader:
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.logger = logging.getLogger(f"{__name__}.FeedbackLogReader")
        self._cache: list[FeedbackEntry] = []
        self._last_read_time: float | None = None
        self._cache_ttl = 60.0

    def _read_log_lines(self, max_entries: int) -> list[FeedbackEntry]:
        now = time.time()
        if self._last_read_time and (now - self._last_read_time) < self._cache_ttl:
            return self._cache
        try:
            if not os.path.exists(self.feedback_log_path): return []
            entries = []
            with open(self.feedback_log_path) as f:
                # Read all lines, parse only the last N
                lines = f.readlines()
                for line in lines[-max_entries:]:
                    try: entries.append(FeedbackEntry(**json.loads(line.strip())))
                    except (json.JSONDecodeError, TypeError): continue
            self._cache = entries
            self._last_read_time = now
            return entries
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []

    def read_recent_feedback(self, max_entries: int = 100) -> list[FeedbackEntry]:
        return self._read_log_lines(max_entries)

    def get_failures(self, max_entries: int = 100) -> list[FeedbackEntry]:
        """v10.7 (Fix #24): Gets recent failure events."""
        all_entries = self._read_log_lines(max_entries)
        return [e for e in all_entries if e.feedback_type == "failure"]

# ============================================================================
# ROW 7: PROPOSED RULES LOADER (v10.7: Preserved)
# ============================================================================

@dataclass
class ProposedRule:
    timestamp: str
    status: str
    rule_type: str
    description: str
    config_changes: dict[str, Any]
    pattern_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class ProposedRulesLoader:
    def __init__(self, proposed_rules_path: str):
        self.proposed_rules_path = proposed_rules_path
        self.logger = logging.getLogger(f"{__name__}.ProposedRulesLoader")
        self._cache: list[ProposedRule] = []
        self._last_mtime: float | None = None

    def load_rules(self, status_filter: str = "APPROVED") -> list[ProposedRule]:
        try:
            if not os.path.exists(self.proposed_rules_path): return []
            current_mtime = os.path.getmtime(self.proposed_rules_path)
            if self._last_mtime == current_mtime:
                return [r for r in self._cache if r.status == status_filter]

            self.logger.info("Hot-reloading proposed rules (file modified).")
            rules = []
            with open(self.proposed_rules_path) as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        pattern_data = data.get("pattern", {})
                        rules.append(ProposedRule(
                            timestamp=data.get("timestamp", ""),
                            status=data.get("status", "PROPOSED"),
                            rule_type=pattern_data.get("type", "unknown"),
                            description=pattern_data.get("description", ""),
                            config_changes=pattern_data.get("config_changes", {}),
                            pattern_id=pattern_data.get("id", ""),
                            metadata=pattern_data.get("metadata", {})
                        ))
                    except (json.JSONDecodeError, TypeError): continue

            self._cache = rules
            self._last_mtime = current_mtime
            return [r for r in rules if r.status == status_filter]
        except Exception as e:
            self.logger.error(f"Failed to load proposed rules: {e}")
            return []

    def get_constitution_rules(self) -> list[dict[str, Any]]:
        rules = self.load_rules(status_filter="APPROVED")
        # v10.7 (Fix #30): Also load rules of type 'moral_constitution'
        return [r.config_changes for r in rules if r.rule_type.lower() in ["constitution", "moral_constitution"]]

# ============================================================================
# ROW 5: CACHE MANAGER (v10.7: Fix #13 - Semantic Caching)
# ============================================================================

class CacheManager:
    def __init__(self,
                 config: ConfigV10_7,
                 redis_client: RedisType,
                 chromadb_client: ChromaClientType,
                 embedding_function: embedding_functions.EmbeddingFunction
                ):
        self.config = config
        self.redis = redis_client
        self.chroma = chromadb_client
        self.embedding_function = embedding_function
        self.ttl = config.caching_config.cache_ttl_seconds
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
        self._hits = 0; self._misses = 0; self._tool_hits = 0; self._tool_misses = 0
        self._semantic_hits = 0 # v10.7 (Fix #13)

        # v10.7 (Fix #13): Init Semantic Cache
        if self.config.caching_config.enable_semantic_caching:
            try:
                self.semantic_cache_collection = self.chroma.get_or_create_collection(
                    name=self.config.chromadb_config.semantic_cache_collection,
                    embedding_function=self.embedding_function
                )
                logger.info("Semantic Caching enabled.")
            except Exception as e:
                logger.error(f"Failed to initialize Semantic Cache: {e}. Disabling.")
                self.config.caching_config.enable_semantic_caching = False

    def _generate_llm_cache_key(self, provider: str, model: str, prompt: str, temperature: float) -> str:
        key_str = f"{provider}:{model}:{prompt}:{temperature}"
        return f"llm_cache_v10_7:{hashlib.sha256(key_str.encode()).hexdigest()}"

    def _generate_tool_cache_key(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        try:
            input_str = json.dumps(tool_input, sort_keys=True)
            key_str = f"{tool_name}:{input_str}"
            return f"tool_cache_v10_7:{hashlib.sha256(key_str.encode()).hexdigest()}"
        except TypeError as e:
            self.logger.warning(f"Could not generate tool cache key for {tool_name}: {e}")
            return ""

    async def get_llm_cache(self, provider: str, model: str, prompt: str, temperature: float) -> dict[str, Any] | None:
        # 1. Check Exact Cache (Redis)
        cache_key = self._generate_llm_cache_key(provider, model, prompt, temperature)
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self._hits += 1
                self.logger.debug(f"LLM Cache HIT (Exact): {cache_key[:16]}...")
                log_event("CacheManager", "llm_cache_hit", {
                    "mode": "exact",
                    "provider": provider,
                    "model": model,
                })
                return json.loads(cached_data)
        except Exception as e:
            self.logger.error(f"Redis get error: {e}")

        # 2. Check Semantic Cache (ChromaDB)
        if self.config.caching_config.enable_semantic_caching:
            try:
                prompt_embedding = self.embedding_function([prompt])[0]
                results = await asyncio.to_thread(
                    self.semantic_cache_collection.query,
                    query_embeddings=[prompt_embedding],
                    n_results=1,
                    where={"provider": provider, "model": model}
                )

                if results['distances'] and results['distances'][0][0] <= (1.0 - self.config.caching_config.semantic_cache_similarity_threshold):
                    self._semantic_hits += 1
                    cached_data_str = results['documents'][0][0]
                    self.logger.info(f"LLM Cache HIT (Semantic): Similarity {1.0 - results['distances'][0][0]:.4f}")
                    log_event("CacheManager", "llm_cache_hit", {
                        "mode": "semantic",
                        "provider": provider,
                        "model": model,
                    })
                    # Also set this in exact cache for future hits
                    self.redis.setex(cache_key, self.ttl, cached_data_str)
                    return json.loads(cached_data_str)

            except Exception as e:
                self.logger.error(f"Semantic Cache get error: {e}")

        self._misses += 1
        self.logger.debug(f"LLM Cache MISS: {cache_key[:16]}...")
        log_event("CacheManager", "llm_cache_miss", {
            "provider": provider,
            "model": model,
        })
        return None

    async def set_llm_cache(self, provider: str, model: str, prompt: str, temperature: float, response: dict[str, Any]):
        response_str = json.dumps(response)

        # 1. Set Exact Cache (Redis)
        cache_key = self._generate_llm_cache_key(provider, model, prompt, temperature)
        try:
            self.redis.setex(cache_key, self.ttl, response_str)
            self.logger.debug(f"Cached LLM response (Exact): {cache_key[:16]}...")
        except Exception as e:
            self.logger.error(f"Redis set error: {e}")

        # 2. Set Semantic Cache (ChromaDB)
        if self.config.caching_config.enable_semantic_caching:
            try:
                prompt_embedding = self.embedding_function([prompt])[0]
                await asyncio.to_thread(
                    self.semantic_cache_collection.add,
                    embeddings=[prompt_embedding],
                    documents=[response_str],
                    metadatas=[{"provider": provider, "model": model, "temperature": temperature}],
                    ids=[cache_key] # Use exact key as ID
                )
            except Exception as e:
                self.logger.error(f"Semantic Cache set error: {e}")

    def get_tool_cache(self, tool_name: str, tool_input: dict[str, Any]) -> Any | None:
        cache_key = self._generate_tool_cache_key(tool_name, tool_input)
        if not cache_key: return None
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self._tool_hits += 1
                self.logger.info(f"Tool Cache HIT: {tool_name}")
                log_event("CacheManager", "tool_cache_hit", {"tool": tool_name})
                return json.loads(cached_data)
            else:
                self._tool_misses += 1
                self.logger.debug(f"Tool Cache MISS: {tool_name}")
                log_event("CacheManager", "tool_cache_miss", {"tool": tool_name})
                return None
        except Exception as e:
            self.logger.error(f"Tool Cache get error: {e}")
            self._tool_misses += 1
            log_event("CacheManager", "tool_cache_error", {"tool": tool_name, "error": str(e)})
            return None

    def set_tool_cache(self, tool_name: str, tool_input: dict[str, Any], result: Any):
        cache_key = self._generate_tool_cache_key(tool_name, tool_input)
        if not cache_key: return
        try:
            self.redis.setex(cache_key, self.ttl, json.dumps(result))
            self.logger.debug(f"Cached Tool response: {tool_name}")
        except Exception as e:
            self.logger.error(f"Tool Cache set error: {e}")

    def get_stats(self) -> dict[str, Any]:
        llm_total = self._hits + self._misses + self._semantic_hits
        llm_hit_rate = ((self._hits + self._semantic_hits) / llm_total * 100) if llm_total > 0 else 0.0
        tool_total = self._tool_hits + self._tool_misses
        tool_hit_rate = (self._tool_hits / tool_total * 100) if tool_total > 0 else 0.0
        return {
            "llm_cache": {
                "hits": self._hits, "semantic_hits": self._semantic_hits,
                "misses": self._misses, "total": llm_total, "hit_rate_pct": llm_hit_rate
            },
            "tool_cache": {"hits": self._tool_hits, "misses": self._tool_misses, "total": tool_total, "hit_rate_pct": tool_hit_rate}
        }

# ============================================================================
# ROW 4: COST TRACKER (v10.7: Preserved)
# ============================================================================

class CostTracker:
    # (Implementation preserved from v10.4)
    PRICING = {
        "anthropic": {"claude-4.1-opus": {"input": 0.015, "output": 0.075}},
        "google": {"gemini-2.5-pro": {"input": 0.002, "output": 0.006}, "gemini-2.5-flash": {"input": 0.0001, "output": 0.0003}},
        "openai": {"gpt-5": {"input": 0.05, "output": 0.15}}
    }
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CostTracker")
        self._workflow_costs: dict[str, list[dict]] = {}
    def log_cost(self, workflow_id: str, agent_name: str, model_name: str, input_tokens: int, output_tokens: int):
        provider = self._get_provider_name(model_name)
        self.record_call(workflow_id, provider, model_name, input_tokens, output_tokens)
    def _get_provider_name(self, model_name: str) -> str:
        if "claude" in model_name: return "anthropic"
        if "gemini" in model_name: return "google"
        if "gpt-" in model_name: return "openai"
        return "unknown"
    def record_call(self, workflow_id: str, provider: str, model: str, input_tokens: int, output_tokens: int):
        pricing = self.PRICING.get(provider, {}).get(model)
        if not pricing: return
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
        if workflow_id not in self._workflow_costs: self._workflow_costs[workflow_id] = []
        self._workflow_costs[workflow_id].append({
            "provider": provider, "model": model, "input_tokens": input_tokens,
            "output_tokens": output_tokens, "cost": cost, "timestamp": datetime.now().isoformat()
        })
    def get_cost_summary(self, workflow_id: str) -> dict[str, Any]:
        calls = self._workflow_costs.get(workflow_id, [])
        total_cost = sum(c["cost"] for c in calls)
        return {"workflow_id": workflow_id, "total_workflow_cost": total_cost, "calls": calls}

# ============================================================================
# BASE AGENT CLASS (v10.7: Fix #15 - Cost/Latency Routing)
# ============================================================================

class BaseAgent:
    """Base class for all agents with v10.7 context injection"""

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        self.context = context
        self.config = context.config
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.prompt_manager = context.prompt_manager
        self.validator = context.response_validator
        self.budget_manager = context.context_budget_manager
        self.metrics = context.metrics_collector
        self.mcp_clients = context.ensure_mcp_clients() if context.is_mcp_enabled() else {}

    def log_info(self, message: str): self.logger.info(f"[{self.__class__.__name__}] {message}")
    def log_warning(self, message: str): self.logger.warning(f"[{self.__class__.__name__}] {message}")
    def log_error(self, message: str): self.logger.error(f"[{self.__class__.__name__}] {message}")
    def log_debug(self, message: str):
        if self.debug_mode: self.logger.debug(f"[{self.__class__.__name__}] {message}")

    def log_feedback(self, workflow_id: str, task: str, feedback_type: str, details: dict[str, Any]):
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(), "workflow_id": workflow_id,
                "agent_name": self.__class__.__name__, "task": task,
                "feedback_type": feedback_type, "details": details, "metadata": {}
            }
            feedback_log_path = self.config.meta_loop_config.feedback_log_path
            os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)
            with open(feedback_log_path, 'a') as f:
                json.dump(feedback_entry, f)
                f.write('\n')
        except Exception as e:
            self.log_error(f"Failed to log feedback: {e}")

    def get_model_client(self, model_config_name: str) -> "AsyncBaseModelClient":
        """
        v10.7 (Fix #15): Gets model client.
        Routes based on complexity, cost, and latency.
        """

        complexity = self.context.complexity
        model_key = model_config_name

        simple_key = f"{model_config_name}_simple"
        complex_key = f"{model_config_name}_complex"

        # 1. Dynamic Model Routing (Fix #2)
        if complexity == "simple" and hasattr(self.config.model_config, simple_key):
            model_key = simple_key
            self.log_debug(f"Dynamic routing: Using '{simple_key}' for simple task")
        elif complexity == "complex" and hasattr(self.config.model_config, complex_key):
            model_key = complex_key
            self.log_debug(f"Dynamic routing: Using '{complex_key}' for complex task")

        # 2. Cost/Latency-Based Routing (Fix #15)
        if model_key == complex_key:
            max_latency = self.config.performance_config.max_complex_model_latency_ms
            avg_latency = self.metrics.get_average_latency(
                "AsyncBaseModelClient", complex_key # Task name must match client
            )
            if avg_latency and avg_latency > max_latency:
                self.log_warning(
                    f"LATENCY FALLBACK: {complex_key} avg latency ({avg_latency:.0f}ms) "
                    f"> threshold ({max_latency}ms). Falling back to {simple_key}."
                )
                model_key = simple_key
                # Log this fallback as a warning event
                self.metrics.record(
                    agent_name=self.__class__.__name__,
                    task_name="latency_fallback",
                    duration_ms=0,
                    success=True,
                    metadata={"complex_model": complex_key, "avg_latency": avg_latency}
                )

        if not hasattr(self.config.model_config, model_key):
            model_key = model_config_name

        model_config = getattr(self.config.model_config, model_key)

        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        client.workflow_id = self.context.workflow_id
        client.agent_name = self.__class__.__name__
        # v10.7 (Fix #19, #24): Inject prompt context
        client.goal_state = self.prompt_manager.goal_state
        client.top_failures = self.prompt_manager.top_failures
        client.budget_manager = self.budget_manager

        return client

    def get_mcp_client(self, name: str, default: Any | None = None) -> Any:
        """Retrieve a configured MCP client by name."""

        try:
            return self.context.get_mcp_client(name, default)
        except KeyError as exc:
            self.log_warning(str(exc))
            if default is not None:
                return default
            raise

# ============================================================================
# v10.7: BASE TOOL INTERFACE (Preserved)
# ============================================================================

class BaseTool(BaseAgent):
    """Base interface for tools used by ReAct Conductors"""
    tool_name: str = "base_tool"

    @track_metrics('base_tool_run')
    async def run_async(self, tool_input: dict[str, Any], workflow_id: str) -> dict[str, Any]:
        """v10.7: Wrapper to implement tool caching."""
        if not self.config.caching_config.enable_tool_caching:
            return await self._run_async_internal(tool_input, workflow_id)

        cache_manager = self.context.cache_manager
        cached_result = cache_manager.get_tool_cache(self.tool_name, tool_input)

        if cached_result:
            self.log_info(f"Tool Cache HIT: {self.tool_name}")
            return cached_result

        self.log_info(f"Tool Cache MISS: {self.tool_name}")
        result = await self._run_async_internal(tool_input, workflow_id)

        cache_manager.set_tool_cache(self.tool_name, tool_input, result)
        return result

    async def _run_async_internal(self, tool_input: dict[str, Any], workflow_id: str) -> dict[str, Any]:
        """Subclasses must implement their logic here"""
        raise NotImplementedError(f"Tool {self.__class__.__name__} must implement _run_async_internal")

    def get_schema(self) -> dict[str, Any]:
        return {
            "name": self.tool_name,
            "description": self.__doc__ or "No description",
            "parameters": {"type": "object", "properties": {}}
        }

# ============================================================================
# ROW 6: ASYNC LLM CLIENTS (v10.7: Fix #29 - Idempotency)
# ============================================================================

class AsyncBaseModelClient:
    def __init__(self,
                 config: ConfigV10_7,
                 model_name: str,
                 cache_manager: CacheManager,
                 cost_tracker: CostTracker,
                 metrics_collector: MetricsCollector,
                 workflow_id: str,
                 agent_name: str
                ):
        self.config = config
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.metrics = metrics_collector
        self.workflow_id = workflow_id
        self.agent_name = agent_name
        # v10.7: Injected by get_model_client
        self.goal_state: str = ""
        self.top_failures: list[str] = []
        self.budget_manager: ContextBudgetManager = None # type: ignore

    def _get_provider_name(self) -> str:
        if "claude" in self.model_name: return "anthropic"
        if "gemini" in self.model_name: return "google"
        if "gpt-" in self.model_name: return "openai"
        return "unknown"

    async def _run_idempotency_check(self, cached_response: dict[str, Any],
                                     messages: list[dict[str, str]], temperature: float,
                                     response_format: str | None = None):
        """v10.7 (Fix #29): Runs a 'shadow call' to check for cache drift."""
        try:
            logger.debug(f"Running Idempotency Check for {self.model_name}")
            # Call the *internal* API method to bypass caching
            shadow_response = await self._internal_api_call(messages, temperature, response_format)

            # Compare results (e.g., hash of content)
            if shadow_response['content'] != cached_response['content']:
                logger.warning(f"IDEMPOTENCY VIOLATION: {self.model_name} cache drift detected.")
                self.metrics.record(
                    agent_name=self.__class__.__name__,
                    task_name="idempotency_violation",
                    duration_ms=0,
                    success=True, # Log as a successful finding
                    metadata={
                        "model": self.model_name,
                        "cached_content": cached_response['content'][:50],
                        "new_content": shadow_response['content'][:50]
                    }
                )
        except Exception as e:
            logger.warning(f"Idempotency check failed: {e}")

    @track_metrics('AsyncBaseModelClient') # v10.7 (Fix #15): Track latency
    async def chat_completion_async(self, messages: list[dict[str, str]],
                                   temperature: float = 0.7,
                                   response_format: str | None = None) -> dict[str, Any]:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()

        cached_response = await self.cache_manager.get_llm_cache(provider, self.model_name, prompt, temperature)

        if cached_response:
            # v10.7 (Fix #29): Idempotency Validation
            if self.config.caching_config.enable_idempotency_validation and \
               random.random() < self.config.caching_config.idempotency_validation_sample_rate:
                # Don't await, run in background
                asyncio.create_task(self._run_idempotency_check(
                    cached_response, messages, temperature, response_format
                ))
            return cached_response

        # Cache MISS: Run the actual API call
        result = await self._internal_api_call(messages, temperature, response_format)

        await self.cache_manager.set_llm_cache(provider, self.model_name, prompt, temperature, result)
        return result

    async def _internal_api_call(self, messages: list[dict[str, str]],
                                 temperature: float = 0.7,
                                 response_format: str | None = None) -> dict[str, Any]:
        """Subclasses must implement the actual API call logic here."""
        raise NotImplementedError

class AnthropicAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(self, messages: list[dict[str, str]],
                                   temperature: float = 0.7,
                                   response_format: str | None = None) -> dict[str, Any]:
        if anthropic is None:
            raise ModelAPIError("Anthropic library not installed. Run 'pip install anthropic'")
        try:
            client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = await client.messages.create(
                model=self.model_name, max_tokens=4096,
                temperature=temperature, messages=messages
            )
            content = response.content[0].text
            result = {
                "content": content,
                "usage": {"prompt_tokens": response.usage.input_tokens, "completion_tokens": response.usage.output_tokens}
            }
            self.cost_tracker.log_cost(
                self.workflow_id, self.agent_name, self.model_name,
                response.usage.input_tokens, response.usage.output_tokens
            )
            return result
        except Exception as e:
            raise ModelAPIError(f"Anthropic API call failed: {e}")

class GeminiAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(self, messages: list[dict[str, str]],
                                   temperature: float = 0.7,
                                   response_format: str | None = None) -> dict[str, Any]:
        if genai is None:
            raise ModelAPIError("Google GenerativeAI library not installed. Run 'pip install google-generativeai'")
        try:
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            gen_config = {"temperature": temperature}
            if response_format == "json_object":
                gen_config["response_mime_type"] = "application/json"
            model = genai.GenerativeModel(self.model_name)
            prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = await asyncio.to_thread(
                model.generate_content, prompt_text, generation_config=gen_config
            )
            content = response.text
            result = {
                "content": content, "usage": {"prompt_tokens": 0, "completion_tokens": 0}
            }
            return result
        except Exception as e:
            raise ModelAPIError(f"Gemini API call failed: {e}")

class OpenAIAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(self, messages: list[dict[str, str]],
                                   temperature: float = 0.7,
                                   response_format: str | None = None) -> dict[str, Any]:
        if AsyncOpenAI is None:
            raise ModelAPIError("OpenAI library not available. Install 'openai' to enable this client.")
        try:
            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            completion_kwargs = {
                "model": self.model_name, "temperature": temperature, "messages": messages
            }
            if response_format == "json_object":
                completion_kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(**completion_kwargs)
            content = response.choices[0].message.content
            result = {
                "content": content,
                "usage": {"prompt_tokens": response.usage.prompt_tokens, "completion_tokens": response.usage.completion_tokens}
            }
            self.cost_tracker.log_cost(
                self.workflow_id, self.agent_name, self.model_name,
                response.usage.prompt_tokens, response.usage.completion_tokens
            )
            return result
        except Exception as e:
            raise ModelAPIError(f"OpenAI API call failed: {e}")

# ============================================================================
# ROW 4: WORKFLOW CONTEXT (v10.7: DI Fixes)
# ============================================================================

class WorkflowContext:
    """
    v10.7: True Dependency Injection container.
    """

    def __init__(self,
                 config: ConfigV10_7,
                 redis_client: RedisType,
                 chromadb_client: ChromaClientType,
                 cache_manager: CacheManager,
                 cost_tracker: CostTracker,
                 feedback_reader: FeedbackLogReader,
                 rules_loader: ProposedRulesLoader,
                 prompt_manager: PromptTemplateManager,
                 response_validator: ResponseValidator,
                 metrics_collector: MetricsCollector,
                 semantic_validator: SemanticValidator,
                 embedding_function: embedding_functions.EmbeddingFunction
                ):

        self.config = config
        self.redis_client = redis_client
        self.chromadb_client = chromadb_client
        self.workflow_id: str = ""
        self.complexity: str = "unknown"

        # Assign injected dependencies
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.feedback_reader = feedback_reader
        self.rules_loader = rules_loader
        self.prompt_manager = prompt_manager
        self.response_validator = response_validator
        self.metrics_collector = metrics_collector
        self.semantic_validator = semantic_validator
        self.embedding_function = embedding_function

        # This is injected *after* __init__ to break circular dependency
        self.context_budget_manager: ContextBudgetManager = None # type: ignore

        self._model_clients: dict[str, Any] = {}

        # MCP integration state
        self.mcp_clients: dict[str, Any] = {}
        self._mcp_initialized: bool = False
        self._mcp_client_specs: list[MCPClientSpec] = []
        self._mcp_fallback_mode: str = "error"
        self._mcp_fallback_parameters: dict[str, Any] = {}
        self._mcp_errors: dict[str, str] = {}
        self._mcp_enabled: bool = False
        self.wrap_mcp_nodes: bool = False

        self._load_mcp_config()

        logger.info("WorkflowContext initialized with v10.7 injected dependencies")

    def get_model_client(self, provider: str, model_name: str):
        key = f"{provider}:{model_name}"
        if key not in self._model_clients:
            base_args = {
                "config": self.config,
                "model_name": model_name,
                "cache_manager": self.cache_manager,
                "cost_tracker": self.cost_tracker,
                "metrics_collector": self.metrics_collector,
                "workflow_id": self.workflow_id,
                "agent_name": ""
            }
            if provider == "anthropic": self._model_clients[key] = AnthropicAsyncClient(**base_args)
            elif provider == "google": self._model_clients[key] = GeminiAsyncClient(**base_args)
            elif provider == "openai": self._model_clients[key] = OpenAIAsyncClient(**base_args)
            else: raise ValueError(f"Unknown provider: {provider}")

        client = self._model_clients[key]
        client.workflow_id = self.workflow_id
        return client

    # ------------------------------------------------------------------
    # MCP lifecycle helpers
    # ------------------------------------------------------------------

    def _load_mcp_config(self) -> None:
        """Pre-process MCP configuration into typed specs."""

        self._mcp_client_specs = []
        self._mcp_enabled = False
        self.wrap_mcp_nodes = False
        self._mcp_fallback_mode = "error"
        self._mcp_fallback_parameters = {}

        try:
            mcp_config = self.config.mcp_config
        except AttributeError:
            return

        enabled = bool(mcp_config.get("enabled", False))
        self._mcp_enabled = enabled
        self.wrap_mcp_nodes = bool(mcp_config.get("wrap_nodes_by_default", False))

        if not enabled:
            return

        fallback_mode = str(mcp_config.get("fallback_mode", "error") or "error").lower()
        if fallback_mode not in {"error", "stub"}:
            logger.warning("Unknown MCP fallback mode '%s'; defaulting to 'error'.", fallback_mode)
            fallback_mode = "error"
        self._mcp_fallback_mode = fallback_mode

        fallback_parameters = mcp_config.get("fallback_parameters", {})
        if fallback_parameters is None:
            fallback_parameters = {}
        if not isinstance(fallback_parameters, dict):
            logger.warning("MCP fallback parameters must be a mapping; ignoring invalid value.")
            fallback_parameters = {}
        self._mcp_fallback_parameters = fallback_parameters

        raw_clients = mcp_config.get("clients", [])
        try:
            self._mcp_client_specs = _parse_mcp_client_specs(raw_clients)
        except Exception as exc:
            raise MCPClientInitializationError(f"Invalid MCP configuration: {exc}") from exc

    def is_mcp_enabled(self) -> bool:
        return self._mcp_enabled

    def ensure_mcp_clients(self) -> dict[str, Any]:
        """Initialise MCP clients if required and return the registry."""

        if self._mcp_initialized:
            return self.mcp_clients

        if not self._mcp_enabled:
            self.mcp_clients = {}
            self._mcp_initialized = True
            return self.mcp_clients

        clients: dict[str, Any] = {}
        errors: dict[str, str] = {}

        for spec in self._mcp_client_specs:
            try:
                clients[spec.name] = _instantiate_mcp_client(spec)
            except Exception as exc:
                errors[spec.name] = str(exc)
                if spec.optional or self._mcp_fallback_mode == "stub":
                    logger.warning(
                        "MCP client '%s' failed to initialise (%s). Using stub fallback.",
                        spec.name,
                        exc,
                    )
                    clients[spec.name] = MCPClientStub(
                        spec.name,
                        {"error": str(exc), **spec.parameters, **self._mcp_fallback_parameters},
                    )
                else:
                    raise MCPClientInitializationError(
                        f"Failed to initialize MCP client '{spec.name}': {exc}"
                    ) from exc

        self.mcp_clients = clients
        self._mcp_errors = errors
        self._mcp_initialized = True
        return self.mcp_clients

    def get_mcp_client(self, name: str, default: Any | None = None) -> Any:
        clients = self.ensure_mcp_clients()
        if name in clients:
            return clients[name]

        if default is not None:
            clients[name] = default
            return default

        if self._mcp_fallback_mode == "stub":
            stub = MCPClientStub(name, {"source": "fallback", **self._mcp_fallback_parameters})
            self.mcp_clients[name] = stub
            return stub

        raise KeyError(f"MCP client '{name}' not available")

    def reset_mcp_clients(self) -> None:
        """Allow tests to reset the MCP registry."""

        self.mcp_clients = {}
        self._mcp_initialized = False
        self._mcp_errors = {}


# ============================================================================
# v10.7 REFACTOR: COMPOSITION ROOT HELPER
# ============================================================================

def get_checkpointer(
    config: ConfigV10_7,
    *,
    db: int | None = None,
    allow_memory_fallback: bool = False
):
    """Create a LangGraph checkpointer with standardized fallbacks."""

    target_db = db if db is not None else config.redis_config.db
    # Collect errors so we can surface meaningful diagnostics if all fallbacks fail.
    fallback_errors: list[str] = []

    try:
        from langgraph.checkpoint.redis import RedisSaver  # type: ignore

        try:
            saver = RedisSaver(
                host=config.redis_config.host,
                port=config.redis_config.port,
                db=target_db
            )
        except TypeError:
            # Older LangGraph versions expose a parameter-less constructor.
            saver = RedisSaver()

        logger.info(
            "Using RedisSaver for LangGraph checkpoints (db=%s).", target_db
        )
        return saver
    except Exception as redis_error:
        fallback_errors.append(f"RedisSaver unavailable: {redis_error}")
        logger.warning(
            "RedisSaver unavailable (%s). Attempting SqliteSaver fallback.",
            redis_error
        )

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore

        sqlite_path = getattr(
            config.redis_config,
            "sqlite_fallback_path",
            os.path.join(os.getcwd(), "langgraph_checkpoints_v10_7.sqlite3")
        )
        os.makedirs(os.path.dirname(sqlite_path) or ".", exist_ok=True)

        try:
            saver = SqliteSaver.from_conn_string(f"sqlite:///{sqlite_path}")
        except AttributeError:
            saver = SqliteSaver(sqlite_path)

        logger.info("Using SqliteSaver for LangGraph checkpoints (%s).", sqlite_path)
        return saver
    except Exception as sqlite_error:
        fallback_errors.append(f"SqliteSaver unavailable: {sqlite_error}")
        logger.warning(
            "SqliteSaver unavailable (%s).", sqlite_error,
        )

    if allow_memory_fallback:
        try:
            from langgraph.checkpoint.memory import MemorySaver  # type: ignore

            logger.info("Using in-memory MemorySaver for LangGraph checkpoints.")
            return MemorySaver()
        except Exception as memory_error:
            fallback_errors.append(f"MemorySaver unavailable: {memory_error}")

    error_message = "; ".join(fallback_errors) or "No checkpoint backend available"
    raise WorkflowError(f"Failed to initialize LangGraph checkpointer: {error_message}")


def create_workflow_context(config: ConfigV10_7, db: int = 0) -> WorkflowContext:
    """
    v10.7 REFACTOR: Centralized Composition Root.
    """
    logger.info(f"Creating WorkflowContext with {config.schema_version}...")

    # 1. Initialize Clients (Redis, ChromaDB, Embedding)
    redis_ctor = getattr(redis_module, "Redis", None)
    if callable(redis_ctor):
        redis_client = redis_ctor(
            host=config.redis_config.host,
            port=config.redis_config.port,
            db=db or config.redis_config.db
        )
    else:  # pragma: no cover - defensive stub fallback
        redis_client = MCPClientStub("redis", {
            "host": config.redis_config.host,
            "port": config.redis_config.port,
            "db": db or config.redis_config.db,
        })

    if config.chromadb_config.use_http_client:
        http_ctor = getattr(chromadb_module, "HttpClient", None)
        if callable(http_ctor):
            chromadb_client = http_ctor(
                host=config.chromadb_config.host,
                port=config.chromadb_config.port
            )
        else:  # pragma: no cover - defensive stub fallback
            client_ctor = getattr(chromadb_module, "Client", None)
            chromadb_client = client_ctor() if callable(client_ctor) else MCPClientStub("chromadb")
    else:
        persistent_ctor = getattr(chromadb_module, "PersistentClient", None)
        if callable(persistent_ctor):
            chromadb_client = persistent_ctor(
                path=config.chromadb_config.persistent_path
            )
        else:  # pragma: no cover - defensive stub fallback
            client_ctor = getattr(chromadb_module, "Client", None)
            chromadb_client = client_ctor() if callable(client_ctor) else MCPClientStub("chromadb")
    logger.info("Initialized ChromaDB client")

    embedding_ctor = getattr(embedding_functions, "DefaultEmbeddingFunction", None)
    if callable(embedding_ctor):
        embedding_function = embedding_ctor()
    else:  # pragma: no cover - stub fallback for local tests
        embedding_function = embedding_functions.EmbeddingFunction()

    # 2. Initialize Core Services (All 9+ services)
    feedback_reader = FeedbackLogReader(
        config.meta_loop_config.feedback_log_path
    )
    cache_manager = CacheManager(
        config=config,
        redis_client=redis_client,
        chromadb_client=chromadb_client,
        embedding_function=embedding_function
    )
    cost_tracker = CostTracker()
    rules_loader = ProposedRulesLoader(
        config.meta_loop_config.proposed_rules_path
    )
    prompt_manager = PromptTemplateManager(
        feedback_reader=feedback_reader
    )
    response_validator = ResponseValidator()
    metrics_collector = MetricsCollector()
    semantic_validator = SemanticValidator(metrics_collector=metrics_collector)

    # 3. Initialize Context (Partial)
    context = WorkflowContext(
        config=config,
        redis_client=redis_client,
        chromadb_client=chromadb_client,
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager,
        response_validator=response_validator,
        metrics_collector=metrics_collector,
        semantic_validator=semantic_validator,
        embedding_function=embedding_function
    )

    # 4. v10.7 (Fix #14): Resolve circular dependency for ContextBudgetManager
    context_budget_manager = ContextBudgetManager(
        config=config,
        model_client_getter=context.get_model_client # Pass the method
    )
    # 5. Inject the final service
    context.context_budget_manager = context_budget_manager

    logger.info("WorkflowContext created and services injected.")
    return context

def cleanup_workflow_chroma_collection(context: WorkflowContext):
    """v10.7 REFACTOR: Centralized ChromaDB cleanup logic."""
    workflow_id = context.workflow_id
    if not workflow_id:
        logger.warning("Cannot cleanup ChromaDB: WorkflowContext has no workflow_id.")
        return

    try:
        logger.info(f"Cleaning up ChromaDB collection for workflow: {workflow_id}")
        collection = context.chromadb_client.get_collection(
            name=context.config.chromadb_config.default_collection_name
        )
        collection.delete(where={"workflow_id": workflow_id})
        logger.info("ChromaDB cleanup complete.")
    except Exception as e:
        logger.warning(f"Failed to cleanup ChromaDB collection for {workflow_id}: {e}")


def detect_bias(context: WorkflowContext, text: str, workflow_id: str = "") -> dict[str, Any]:
    """Centralized bias detection service shared by agents and tools."""

    logger.debug("Running centralized bias detection service.")

    base_patterns = ["he/she", "his/her", "male/female", "young", "old"]
    rules = context.rules_loader.get_constitution_rules()

    bias_patterns: list[str] = base_patterns.copy()
    for rule in rules:
        if isinstance(rule, dict) and 'bias_patterns' in rule:
            patterns = rule.get('bias_patterns')
            if isinstance(patterns, list):
                bias_patterns.extend(str(p) for p in patterns)

    normalized_text = text.lower()
    detected_patterns = sorted({p for p in bias_patterns if p.lower() in normalized_text})
    bias_detected = len(detected_patterns) > 0

    result = {
        "bias_detected": bias_detected,
        "patterns": detected_patterns,
        "bias_score": (len(detected_patterns) / len(bias_patterns)) if bias_patterns else 0.0,
        "dynamic_rules_applied": len(rules)
    }

    return result

# ============================================================================
# STATE MODELS (v10.7: Fix #10 - A2A Comms)
# ============================================================================

@dataclass
class ResumeContext:
    master_resume: dict[str, Any] = field(default_factory=dict)
    sanitized_resume: dict[str, Any] = field(default_factory=dict)
    experience_bullets: list[dict] = field(default_factory=list)
@dataclass
class JobContext:
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""
    parsed_requirements: dict[str, Any] = field(default_factory=dict)
@dataclass
class StrategyContext:
    strategy_plan: StrategyPlan | None = None
    tot_branches: list[dict] = field(default_factory=list)
@dataclass
class PromptContext:
    prompts: GeneratedPrompts | None = None
@dataclass
class BulletContext:
    generated_bullets: list[dict] = field(default_factory=list)
    critiqued_bullets: list[dict] = field(default_factory=list)
@dataclass
class DraftContext:
    sections: dict[str, Any] = field(default_factory=dict)
@dataclass
class QAContext:
    validation_results: dict[str, Any] = field(default_factory=dict)
    qa_passed: bool = False
    constitutional_review: ConstitutionalReviewResult | None = None # v10.7 (Fix #30)
@dataclass
class ArtifactContext:
    artifacts: dict[str, Any] = field(default_factory=dict)
@dataclass
class MetadataContext:
    workflow_id: str = ""
    timestamp: str = ""
    cost: float = 0.0
    retries: dict[str, int] = field(default_factory=lambda: {"bullet_retries": 0, "qa_retries": 0})
    complexity: str = "unknown"
@dataclass
class SafetyContext:
    pii_detected: bool = False
    bias_detected: bool = False
    safety_notes: list[str] = field(default_factory=list)
    injection_detected: bool = False
@dataclass
class FeedbackContext:
    recent_feedback: list[FeedbackEntry] = field(default_factory=list)
    applied_rules: list[str] = field(default_factory=list)
    selected_agents: dict[str, str] = field(default_factory=dict)
@dataclass
class HILContext:
    ambiguity_detected: bool = False
    ambiguity_report: HILAmbiguityReport | None = None
    next_step: str = ""
    payload: str | None = None

# v10.7 (Fix #10): Agent-to-Agent Communication State
@dataclass
class A2AMessage:
    sender: str
    recipient: str # Can be "ALL"
    message_type: str # e.g., "ERROR", "METRIC", "UI_EVENT"
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class A2AContext:
    messages: list[A2AMessage] = field(default_factory=list)

@dataclass
class MainGraphState:
    """Main workflow state (v10.7)"""
    resume: ResumeContext = field(default_factory=ResumeContext)
    job: JobContext = field(default_factory=JobContext)
    strategy: StrategyContext = field(default_factory=StrategyContext)
    prompts: PromptContext = field(default_factory=PromptContext)
    bullets: BulletContext = field(default_factory=BulletContext)
    draft: DraftContext = field(default_factory=DraftContext)
    qa: QAContext = field(default_factory=QAContext)
    artifacts: ArtifactContext = field(default_factory=ArtifactContext)
    metadata: MetadataContext = field(default_factory=MetadataContext)
    safety: SafetyContext = field(default_factory=SafetyContext)
    feedback: FeedbackContext = field(default_factory=FeedbackContext)
    hil: HILContext = field(default_factory=HILContext)
    a2a: A2AContext = field(default_factory=A2AContext) # v10.7 (Fix #10)

    def to_dict(self) -> dict[str, Any]:
        """v10.7: Custom serializer to handle nested Pydantic models."""
        data = asdict(self)

        # Manually serialize nested Pydantic models to dicts
        if self.strategy.strategy_plan:
            data['strategy']['strategy_plan'] = self.strategy.strategy_plan.model_dump()
        if self.prompts.prompts:
            data['prompts']['prompts'] = self.prompts.prompts.model_dump()
        if self.hil.ambiguity_report:
            data['hil']['ambiguity_report'] = self.hil.ambiguity_report.model_dump()
        if self.qa.constitutional_review: # v10.7 (Fix #30)
            data['qa']['constitutional_review'] = self.qa.constitutional_review.model_dump()

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'MainGraphState':
        """v10.7: Custom deserializer to reconstruct nested Pydantic models."""
        state = cls()

        # Deserialize dataclasses
        state.resume = ResumeContext(**data.get("resume", {}))
        state.job = JobContext(**data.get("job", {}))
        state.bullets = BulletContext(**data.get("bullets", {}))
        state.draft = DraftContext(**data.get("draft", {}))
        state.artifacts = ArtifactContext(**data.get("artifacts", {}))
        state.metadata = MetadataContext(**data.get("metadata", {}))
        state.safety = SafetyContext(**data.get("safety", {}))
        state.feedback = FeedbackContext(**data.get("feedback", {}))
        state.a2a = A2AContext(**data.get("a2a", {})) # v10.7 (Fix #10)

        # Deserialize QA
        qa_data = data.get("qa", {})
        qa_review_data = qa_data.get("constitutional_review")
        state.qa = QAContext(
            validation_results=qa_data.get("validation_results", {}),
            qa_passed=qa_data.get("qa_passed", False),
            constitutional_review=ConstitutionalReviewResult.model_validate(qa_review_data) if qa_review_data and isinstance(qa_review_data, dict) else None
        )

        # Deserialize Strategy
        strategy_data = data.get("strategy", {})
        strategy_plan_data = strategy_data.get("strategy_plan")
        state.strategy = StrategyContext(
            strategy_plan=StrategyPlan.model_validate(strategy_plan_data) if strategy_plan_data and isinstance(strategy_plan_data, dict) else None,
            tot_branches=strategy_data.get("tot_branches", [])
        )

        # Deserialize Prompts
        prompts_data = data.get("prompts", {})
        prompts_model_data = prompts_data.get("prompts")
        state.prompts = PromptContext(
            prompts=GeneratedPrompts.model_validate(prompts_model_data) if prompts_model_data and isinstance(prompts_model_data, dict) else None
        )

        # Deserialize HIL
        hil_data = data.get("hil", {})
        hil_report_data = hil_data.get("ambiguity_report")
        state.hil = HILContext(
            ambiguity_detected=hil_data.get("ambiguity_detected", False),
            ambiguity_report=HILAmbiguityReport.model_validate(hil_report_data) if hil_report_data and isinstance(hil_report_data, dict) else None,
            next_step=hil_data.get("next_step", ""),
            payload=hil_data.get("payload")
        )
        return state

@dataclass
class MetaGraphState:
    """v10.7: Meta-learning graph state."""
    raw_logs: dict[str, str] = field(default_factory=dict)
    log_summary: dict[str, Any] = field(default_factory=dict)
    patterns: list[dict] = field(default_factory=list)
    hypotheses: list[dict] = field(default_factory=list)
    proposal: dict[str, Any] = field(default_factory=dict)
    critique: dict[str, Any] = field(default_factory=dict)
    replan_count: int = 0
    workflow_id: str = ""
    generated_tool_code: str | None = None

# ============================================================================
# END OF core_v10_7.py
# ============================================================================
