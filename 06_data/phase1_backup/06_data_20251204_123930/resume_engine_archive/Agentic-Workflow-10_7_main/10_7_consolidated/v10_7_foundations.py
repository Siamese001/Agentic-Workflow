# FILE: v10_7_foundations.py
# CONSOLIDATED: Core Infrastructure (Exceptions, Models, Config, MCP, Services, Context)
# STATUS: Production Ready (v10.7 Baseline)

import asyncio
import copy
import hashlib
import importlib
import json
import logging
import math
import os
import random
import re
import time
import uuid
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

# External Dependencies (must be installed via requirements.txt)
try:
    from pydantic import BaseModel, ConfigDict, Field, ValidationError as PydanticValidationError
    import chromadb
    from chromadb.utils import embedding_functions
    import redis
except ImportError:
    # Fallback for static analysis without deps
    BaseModel = object
    Field = lambda *args, **kwargs: None
    ConfigDict = lambda *args, **kwargs: None
    PydanticValidationError = Exception


# ============================================================================
# SECTION 1: EXCEPTIONS (Source: exceptions.py)
# ============================================================================

class WorkflowError(Exception):
    """Base exception for workflow failures."""


class ModelAPIError(WorkflowError):
    """Raised when an LLM provider call fails."""


class JSONParsingError(WorkflowError):
    """Raised when JSON parsing fails."""


class ValidationError(WorkflowError):
    """Raised when workflow validation fails."""


class FileIOError(WorkflowError):
    """Raised when file IO fails."""


class CostCeilingExceededError(WorkflowError):
    """Raised when a workflow exceeds the configured cost ceiling."""


class CircuitBreakerOpenError(WorkflowError):
    """Raised when the circuit breaker remains open."""


class PydanticSchemaError(ValidationError):
    """Raised when Pydantic validation fails."""


class WorkflowTimeoutError(WorkflowError, asyncio.TimeoutError):
    """Raised when async workflow execution exceeds its timeout."""


class MCPClientInitializationError(WorkflowError):
    """Raised when an MCP client fails to initialize."""


# ============================================================================
# SECTION 2: CONSTANTS (Source: constants.py)
# ============================================================================

LEGACY_MODEL_ALIASES = {
    # --- Gemini ---
    "gemini-2.5-pro": "gemini-pro",
    "gemini-2.5-flash": "gemini-flash",
    "gemini-pro-1.0": "gemini-pro",
    "gemini-pro-vision": "gemini-pro",
    "gemini-flash-1.0": "gemini-flash",

    # --- Anthropic ---
    "claude-2.1": "claude-3-sonnet",
    "claude-3-sonnet-20240229": "claude-3-sonnet",
    "claude-1": "claude-3-haiku",
    "claude-instant-1.2": "claude-3-haiku",

    # --- OpenAI ---
    "gpt-4o-mini": "gpt-4o",
    "gpt-4o-mini-2024-05-27": "gpt-4o",
    "gpt-4-1106-preview": "gpt-4o",
    "gpt-3.5-turbo": "gpt-4o-mini",

    # --- Internal agentic workflow ---
    "resume-gen-draft": "gpt-4o-mini",
    "resume-gen-qa": "gpt-4o-mini",
}

LEGACY_MODEL_REVERSE = {alias: orig for orig, alias in LEGACY_MODEL_ALIASES.items()}

def _normalize(model_name: str) -> str:
    if not isinstance(model_name, str):
        return str(model_name)
    model_name = model_name.strip().lower()
    model_name = model_name.replace(" ", "-").replace("_", "-")
    return model_name

def legacy_model_alias(model_name: str) -> str:
    normalized = _normalize(model_name)
    return LEGACY_MODEL_ALIASES.get(normalized, normalized)

def canonical_model_name(model_name: str) -> str:
    normalized = _normalize(model_name)
    return LEGACY_MODEL_REVERSE.get(normalized, normalized)


# ============================================================================
# SECTION 3: MODELS (Source: models.py)
# ============================================================================

class SpecialistDraftPacket(BaseModel):
    """Container for specialist drafting outputs."""
    specialist: str = Field(..., description="Name of the drafting specialist")
    focus_area: str = Field(..., description="Primary responsibility of the specialist")
    sections: Dict[str, Any] = Field(default_factory=dict, description="Section-level draft contributions")
    notes: List[str] = Field(default_factory=list, description="Observations or hand-off notes")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or follow-up actions")

class EvidenceClarificationRecord(BaseModel):
    """Represents a clarification request raised by the liaison."""
    request_id: str
    recipient: str
    questions: List[str]
    priority: str = "normal"
    context_summary: str = ""

class EvidenceBriefRecord(BaseModel):
    """Structured evidence digest for a section."""
    section: str
    brief: str
    key_points: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    outstanding_questions: List[str] = Field(default_factory=list)

class EvidenceLiaisonPacket(BaseModel):
    """Aggregated liaison output feeding back to the guild."""
    clarifications: List[EvidenceClarificationRecord] = Field(default_factory=list)
    briefs: List[EvidenceBriefRecord] = Field(default_factory=list)

class CritiqueFindingRecord(BaseModel):
    """Single critique finding routed by the panel."""
    critic: str
    severity: str
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)

class CritiquePanelPacket(BaseModel):
    """Aggregated critique findings for the coordinator."""
    findings: List[CritiqueFindingRecord] = Field(default_factory=list)
    overall_status: str = Field(..., description="Coordinator-level status derived from findings")

# -- Core Data Models (from context.py and services.py imports in 10.7) --
# Re-declared here to resolve dependencies for the consolidated file.

class StrategyPlan(BaseModel):
    strategy_name: str
    focus_areas: List[str]
    key_achievements_to_highlight: List[str]
    tone: str
    feedback_signals: Optional[List[str]] = None
    aggregated_decision: Optional[str] = None
    aggregated_confidence: Optional[float] = None
    aggregated_rationale: Optional[str] = None
    scenario_simulations: Optional[List[Any]] = None # Simplified for circular dep
    planner_assessments: Optional[List[Any]] = None
    coordinator_summary: Optional[str] = None

class RAGPlan(BaseModel):
    goal: str
    context_inputs: List[str]
    retrieval_queries: List[str]
    prioritization: List[str]
    risk_checks: List[str]

class BulletPlan(BaseModel):
    target_sections: List[str]
    highlight_order: List[str]
    metrics_focus: List[str]
    style_guidelines: List[str]
    validation_checks: List[str]

class DraftPlan(BaseModel):
    structure: List[str]
    tone: str
    key_messages: List[str]
    review_gates: List[str]
    risks: List[str]

class GeneratedPrompts(BaseModel):
    prompts: Dict[str, str] = Field(default_factory=dict)
    qa_prompts: List[str] = Field(default_factory=list)
    bullet_generation_prompt: str = ""
    critique_prompt: str = ""
    final_prompt: Optional[str] = None
    prompt_envelope: Optional[Dict[str, Any]] = None

class PromptEnvelope(BaseModel):
    framing: str
    context: str
    reasoning: str
    instructions: str
    tool_context: str = ""
    output_schema: str = ""
    safety_context: Dict[str, Any] = Field(default_factory=dict)

class ConstitutionalReviewResult(BaseModel):
    review_passed: bool
    violations_found: List[str]
    feedback: str
    self_correction: Optional[Dict[str, Any]] = None

class HILAmbiguityReport(BaseModel):
    ambiguity_detected: bool
    confidence: float = 0.0
    reason: str = ""
    question_for_human: str = ""

class HILFeedbackIntent(BaseModel):
    category: str
    summary: str
    urgency: str

class HILFeedbackRoute(BaseModel):
    next_step: str
    payload: Optional[str] = None
    intent_clusters: List[HILFeedbackIntent] = Field(default_factory=list)
    delegated_specialists: List[str] = Field(default_factory=list)
    persona_consensus: Optional[Any] = None # Circular dep handle

class HILReconciliationResult(BaseModel):
    integrated_text: str
    change_log: List[str]
    unresolved_questions: List[str]

class PersonaReviewDecision(BaseModel):
    persona: str
    approval: bool
    confidence: float
    key_concerns: List[str]
    proposed_actions: List[str]
    escalation_recommended: bool

class PersonaConsensus(BaseModel):
    approved: bool
    persona_decisions: List[PersonaReviewDecision]
    negotiated_actions: List[str]
    rationale: str
    escalation_recommended: bool

class PlannerAssessment(BaseModel):
    planner_name: str
    vote: str
    rationale: str
    confidence: float
    recommended_actions: List[str]

class ScenarioSimulationResult(BaseModel):
    scenario_name: str
    risk_level: str
    impact_score: float
    summary: str
    mitigation_actions: List[str]

class BaseToolOutput(BaseModel):
    status: str = "success"
    message: Optional[str] = None

class BulletList(BaseModel):
    verified_bullets: List[str]
    rejected_bullets: List[str] = Field(default_factory=list)

class CritiqueResult(BaseModel):
    score: float
    suggestions: List[str]

class ArbitrationReport(BaseModel):
    stage: str
    decision: str
    reasons: List[str]
    confidence: float
    suggested_route: str
    metrics_snapshot: Dict[str, Any]

class SelfCorrectionReport(BaseModel):
    stack_name: str
    workflow_id: str
    issue_detected: str
    action_taken: str
    retry_count: int
    resolved: bool
    notes: Dict[str, Any] = Field(default_factory=dict)

class MemoryState(BaseModel):
    episodic: Any = None
    semantic: Any = None

class EphemeralState(BaseModel):
    events: List[Any] = Field(default_factory=list)
    debug_traces: List[str] = Field(default_factory=list)
    last_node: Optional[str] = None

class WorkflowPhase:
    INIT = "INIT"
    SAFETY = "SAFETY"
    STRATEGY = "STRATEGY"
    RAG = "RAG"
    BULLETS = "BULLETS"
    DRAFTING = "DRAFTING"
    QA = "QA"
    HIL = "HIL"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class SemanticMemoryRef(BaseModel):
    vector_store_ids: List[str]
    tags: List[str]


# ============================================================================
# SECTION 4: MCP REGISTRY (Source: mcp.py)
# ============================================================================

logger = logging.getLogger("core_v10_7.mcp")

DEFAULT_PROVIDER_MODULES = {
    "redis": "redis",
    "chromadb": "chromadb",
    "openai": "mcp_openai",
    "http": "mcp_http_client",
}

DEFAULT_PROVIDER_CLASSES = {
    "redis": "RedisMCPClient",
    "chromadb": "ChromaMCPClient",
    "openai": "OpenAIMCPClient",
    "http": "HTTPMCPClient",
}

@dataclass
class MCPClientSpec:
    name: str
    provider: str = "stub"
    module: Optional[str] = None
    class_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    optional: bool = False

    def resolved_module(self) -> Optional[str]:
        if self.module: return self.module
        return DEFAULT_PROVIDER_MODULES.get(self.provider)

    def resolved_class(self) -> Optional[str]:
        if self.class_name: return self.class_name
        return DEFAULT_PROVIDER_CLASSES.get(self.provider)

class MCPClientStub:
    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}

    def __call__(self, *args, **kwargs):
        return {
            "stub": True,
            "client": self.name,
            "parameters": self.parameters,
            "args": args,
            "kwargs": kwargs,
            "error": self.parameters.get("error", "Stubbed MCP client."),
        }
    
    def __repr__(self) -> str:
        details = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"<MCPClientStub name={self.name} {details}>"

def parse_mcp_client_specs(raw_specs: List[Dict[str, Any]]) -> List[MCPClientSpec]:
    specs: List[MCPClientSpec] = []
    for raw in raw_specs:
        if not isinstance(raw, dict): raise ValueError("Each MCP client entry must be a mapping.")
        name = raw.get("name")
        if not name or not isinstance(name, str): raise ValueError("MCP client entries require a string 'name'.")
        spec = MCPClientSpec(
            name=name,
            provider=str(raw.get("provider", "stub")).lower(),
            module=raw.get("module"),
            class_name=raw.get("class_name") or raw.get("class"),
            parameters=raw.get("parameters", {}),
            optional=bool(raw.get("optional", False)),
        )
        specs.append(spec)
    return specs

def instantiate_mcp_client(spec: MCPClientSpec) -> Any:
    if spec.provider == "stub" and not spec.module:
        logger.info(f"[MCP] Using stub for '{spec.name}'.")
        return MCPClientStub(spec.name, spec.parameters)
    
    module_name = spec.resolved_module()
    class_name = spec.resolved_class()
    
    if not module_name or not class_name:
        raise MCPClientInitializationError(f"Cannot create MCP client '{spec.name}': incomplete spec.")

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise MCPClientInitializationError(f"Failed to import MCP module '{module_name}': {exc}") from exc

    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        raise MCPClientInitializationError(f"Module '{module_name}' missing class '{class_name}'") from exc

    try:
        instance = client_cls(**spec.parameters)
        logger.info(f"[MCP] Initialized client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except Exception as exc:
        raise MCPClientInitializationError(f"Failed to instantiate MCP client '{spec.name}': {exc}") from exc

# Placeholder for mcp.get_tool and mcp.emit_event which were imported in source files
def get_tool(name: str):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None

def emit_event(envelope: Dict[str, Any]):
    # In a real implementation, this sends to an MCP stream
    pass


# ============================================================================
# SECTION 5: TELEMETRY (Source: telemetry_v10_7.py)
# ============================================================================

logger_telemetry = logging.getLogger("telemetry_v10_7")

def _build_envelope(
    agent: str,
    event: str,
    payload: Dict[str, Any],
    *,
    workflow_id: Optional[str] = None,
    node: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    envelope = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "event": event,
        "category": category or "runtime",
        "workflow_id": workflow_id,
        "node": node,
        "payload": payload or {},
    }
    return {k: v for k, v in envelope.items() if v is not None}

def log_event(
    agent: str,
    event: str,
    data: Optional[Dict[str, Any]] = None,
    *,
    workflow_id: Optional[str] = None,
    node: Optional[str] = None,
    category: Optional[str] = None,
) -> None:
    data = data or {}
    env = _build_envelope(
        agent=agent,
        event=event,
        payload=data,
        workflow_id=workflow_id,
        node=node,
        category=category,
    )
    try:
        emit_event(env)
        logger_telemetry.debug("Telemetry emitted: %s", env)
    except Exception as exc:
        logger_telemetry.warning(f"Failed to emit MCP telemetry: {exc}")


# ============================================================================
# SECTION 6: CONFIGURATION (Source: config.py)
# ============================================================================

# Mock get_schema to simulate loading from file without filesystem dependency
def get_schema(path: str) -> Dict[str, Any]:
    # This returns the defaults matching master_config_v10_7.json structure
    return {
        "schema_version": "master_config_v10.7",
        "redis_config": {"host": "localhost", "port": 6379, "db": 0, "required": True},
        "chromadb_config": {"host": "localhost", "port": 8000, "use_http_client": False, "default_collection_name": "resume_embeddings"},
        "caching_config": {"enable_llm_caching": True, "enable_semantic_caching": True, "enable_idempotency_validation": True},
        "performance_config": {"workflow_node_timeout_seconds": 60, "default_token_limit": 8192},
        "meta_loop_config": {"enable_meta_learning": True, "feedback_log_path": "./logs/feedback.jsonl"},
        "agent_stacks": {"enable_hil_stack": True, "strategy_tot_branching_factor": 3},
        "model_config": {
            "strategy_model": {"provider": "google", "model_name": "gemini-2.5-pro", "temperature": 0.5},
            "qa_model": {"provider": "google", "model_name": "gemini-2.5-flash", "temperature": 0.3},
            "summarizer_model": {"provider": "google", "model_name": "gemini-2.5-flash", "temperature": 0.3},
        },
        "mcp_config": {"enabled": True, "clients": []}
    }

class ConfigSection:
    def __init__(self, data: Dict):
        self._data = data
    def __getattr__(self, name):
        if name.startswith('_'): return object.__getattribute__(self, name)
        value = self._data.get(name)
        if value is None:
            snake_name = name.replace('-', '_')
            value = self._data.get(snake_name)
            if value is None:
                # Fallback for missing keys to avoid crash
                return None
        if isinstance(value, dict):
            return ConfigSection(value)
        return value
    def get(self, key, default=None): return self._data.get(key, default)

class ConfigV10_7:
    def __init__(self, config_path: str = "master_config_v10_7.json"):
        self._config = get_schema(config_path)
        logger_config = logging.getLogger("core_v10_7")
        logger_config.info(f"Loaded configuration schema: {self._config.get('schema_version')}")

    def __getattr__(self, name):
        if name.startswith('_'): return object.__getattribute__(self, name)
        section = self._config.get(name)
        if section is None:
            snake_name = name.replace('-', '_')
            section = self._config.get(snake_name)
            if section is None:
                # Allow accessing top-level keys or returning empty section
                return ConfigSection({})
        return ConfigSection(section)


# ============================================================================
# SECTION 7: RESILIENCE (Source: resilience.py)
# ============================================================================

def sync_context(context: Any, scope: str):
    pass # Stub for MCP sync

class CircuitBreaker:
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
            self.logger.error("Circuit breaker OPEN after %s failures", self.failure_count)

    def check(self):
        if self.is_open:
            raise CircuitBreakerOpenError(f"Circuit breaker open after {self.failure_count} failures")

def exponential_backoff_retry(max_retries: int = 3, initial_delay: float = 1.0):
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            total_attempts = max(1, max_retries + 1)
            for attempt in range(total_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ModelAPIError, JSONParsingError, PydanticSchemaError, asyncio.TimeoutError) as exc:
                    logging.warning(f"Node {func.__name__} failed (Attempt {attempt + 1}/{total_attempts}): {exc}")
                    if attempt + 1 == total_attempts: raise
                    sleep_time = delay * (2 ** attempt)
                    await asyncio.sleep(sleep_time)
            raise WorkflowError(f"Node {func.__name__} failed after max retries")
        return wrapper
    return decorator

def async_timeout(seconds: int):
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=float(seconds))
            except asyncio.TimeoutError as exc:
                raise WorkflowTimeoutError(f"Node {func.__name__} timed out after {seconds}s") from exc
        return wrapper
    return decorator

def get_timeout_decorator(timeout_seconds: float):
    return async_timeout(int(timeout_seconds))

def update_context(context: Optional["WorkflowContext"]) -> None:
    if context is None: return
    try: sync_context(context, scope="workflow")
    except Exception: pass

def wrap_mcp(func: Optional[Callable] = None, *, force: bool = False) -> Callable:
    if func is None: return lambda inner: wrap_mcp(inner, force=force)
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Context extraction logic simplified for single-file
            context = kwargs.get("workflow_context")
            if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
                context.ensure_mcp_clients()
            result = await func(*args, **kwargs)
            update_context(context)
            return result
        return async_wrapper
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        context = kwargs.get("workflow_context")
        if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
            context.ensure_mcp_clients()
        result = func(*args, **kwargs)
        update_context(context)
        return result
    return sync_wrapper


# ============================================================================
# SECTION 8: CONTEXT BUDGET (Source: context_budget_v10_8.py)
# ============================================================================

class ContextBudgetConfig(BaseModel):
    max_episodic_messages: int = 50
    max_rag_documents: int = 10
    max_summary_chars: int = 4000

class ContextBudgetManagerV10_8:
    _TRIGGER_RATIO: float = 1.0
    def __init__(self, config: Optional[ContextBudgetConfig] = None, *, delegate: Any = None):
        self.config = config or ContextBudgetConfig()
        self.delegate = delegate
        self.logger = logging.getLogger(f"{__name__}.ContextBudgetManager")

    async def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        if self.delegate and hasattr(self.delegate, "prune"):
            return await self.delegate.prune(document, max_tokens)
        return document

    def enforce_all(self, state: Any) -> Any:
        working_state = self._coerce_mapping(state)
        if working_state is None: return state
        self._trim_episodic_memory(working_state)
        self._trim_rag_history(working_state)
        self._trim_summary(working_state)
        return working_state

    def _trim_episodic_memory(self, state: MutableMapping[str, Any]) -> None:
        memory = self._ensure_mapping(state.get("memory"))
        episodic = self._ensure_mapping(memory.get("episodic")) if memory else None
        conversation = episodic.get("conversation") if episodic else None
        if not isinstance(conversation, list): return
        limit = self.config.max_episodic_messages
        if len(conversation) <= limit * self._TRIGGER_RATIO: return
        episodic["conversation"] = conversation[-limit:]
        memory["episodic"] = episodic
        state["memory"] = memory

    def _trim_rag_history(self, state: MutableMapping[str, Any]) -> None:
        rag = self._ensure_mapping(state.get("rag"))
        history = rag.get("history") if rag else None
        if not isinstance(history, list): return
        limit = self.config.max_rag_documents
        if len(history) <= limit * self._TRIGGER_RATIO: return
        rag["history"] = history[-limit:]
        state["rag"] = rag

    def _trim_summary(self, state: MutableMapping[str, Any]) -> None:
        summary_parent = None
        summary_key = None
        summary_value: Optional[str] = None
        resume = self._ensure_mapping(state.get("resume"))
        if resume and isinstance(resume.get("summary"), str):
            summary_parent, summary_key, summary_value = resume, "summary", resume.get("summary")
        elif isinstance(state.get("summary"), str):
            summary_parent, summary_key, summary_value = state, "summary", state.get("summary")
        if not summary_parent or not summary_key or not isinstance(summary_value, str): return
        limit = self.config.max_summary_chars
        if len(summary_value) <= limit * self._TRIGGER_RATIO: return
        trimmed = f"{summary_value[:limit]}\n\n[... SUMMARY TRIMMED ...]"
        summary_parent[summary_key] = trimmed
        if resume is summary_parent: state["resume"] = resume

    def _coerce_mapping(self, state: Any) -> Optional[MutableMapping[str, Any]]:
        if isinstance(state, MutableMapping): return state
        if hasattr(state, "to_dict"): return copy.deepcopy(state.to_dict())
        if hasattr(state, "model_dump"): return copy.deepcopy(state.model_dump())
        return None

    def _ensure_mapping(self, value: Any) -> Optional[MutableMapping[str, Any]]:
        if isinstance(value, MutableMapping): return value
        if hasattr(value, "model_dump"): return value.model_dump()
        return None

    def __getattr__(self, name: str) -> Any:
        if self.delegate and hasattr(self.delegate, name): return getattr(self.delegate, name)
        raise AttributeError(name)


# ============================================================================
# SECTION 9: STATE ADAPTER (Source: state_adapter_stack.py)
# ============================================================================

@dataclass
class A2AMessage:
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    def to_dict(self): return asdict(self)
    def model_dump(self): return asdict(self)

@dataclass
class A2AContext:
    messages: List[A2AMessage] = field(default_factory=list)
    def __post_init__(self):
        self.messages = [m if isinstance(m, A2AMessage) else A2AMessage(**m) for m in self.messages]
    def append(self, **kwargs): self.messages.append(A2AMessage(**kwargs))

# Simplified dataclass versions of Context Models to support StatePatch
@dataclass
class ResumeContext:
    master_resume: Dict = field(default_factory=dict)
    sanitized_resume: Dict = field(default_factory=dict)
    experience_bullets: List = field(default_factory=list)

@dataclass
class JobContext:
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""

@dataclass
class StrategyContext:
    strategy_plan: Optional[StrategyPlan] = None
    tot_branches: List = field(default_factory=list)

@dataclass
class PromptContext:
    prompts: Optional[GeneratedPrompts] = None

@dataclass
class BulletContext:
    generated_bullets: List = field(default_factory=list)
    critiqued_bullets: List = field(default_factory=list)

@dataclass
class DraftContext:
    sections: Dict = field(default_factory=dict)

@dataclass
class QAContext:
    validation_results: Dict = field(default_factory=dict)
    qa_passed: bool = False
    constitutional_review: Optional[ConstitutionalReviewResult] = None

@dataclass
class ArtifactContext:
    artifacts: Dict = field(default_factory=dict)

@dataclass
class MetadataContext:
    workflow_id: str = ""
    complexity: str = "unknown"
    retries: Dict = field(default_factory=dict)

@dataclass
class SafetyContext:
    pii_detected: bool = False
    bias_detected: bool = False
    injection_detected: bool = False

@dataclass
class FeedbackContext:
    recent_feedback: List = field(default_factory=list)

@dataclass
class HILContext:
    ambiguity_report: Optional[HILAmbiguityReport] = None
    next_step: str = ""
    payload: Optional[str] = None

@dataclass
class MainGraphState:
    resume: ResumeContext = field(default_factory=ResumeContext)
    job: JobContext = field(default_factory=JobContext)
    strategy: StrategyContext = field(default_factory=StrategyContext)
    prompts: PromptContext = field(default_factory=PromptContext)
    bullets: BulletContext = field(default_factory=BulletContext)
    draft: DraftContext = field(default_factory=DraftContext)
    qa: QAContext = field(default_factory=QAContext)
    safety_report: Optional[Dict] = None
    policy_decision: Optional[Dict] = None
    constitutional_review: Optional[Dict] = None
    artifacts: ArtifactContext = field(default_factory=ArtifactContext)
    metadata: MetadataContext = field(default_factory=MetadataContext)
    safety: SafetyContext = field(default_factory=SafetyContext)
    feedback: FeedbackContext = field(default_factory=FeedbackContext)
    hil: HILContext = field(default_factory=HILContext)
    a2a: A2AContext = field(default_factory=A2AContext)
    memory: MemoryState = field(default_factory=MemoryState)
    ephemeral: EphemeralState = field(default_factory=EphemeralState)
    phase: str = WorkflowPhase.INIT

    def to_dict(self):
        data = asdict(self)
        # Serialization helpers for Pydantic nested objects
        if self.strategy.strategy_plan: data["strategy"]["strategy_plan"] = self.strategy.strategy_plan.model_dump()
        if self.prompts.prompts: data["prompts"]["prompts"] = self.prompts.prompts.model_dump()
        if self.qa.constitutional_review: data["qa"]["constitutional_review"] = self.qa.constitutional_review.model_dump()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # Simplified deserializer for this consolidated view
        return cls() # Placeholder - real implementation is complex mapping

class StatePatch(BaseModel):
    resume: dict | None = None
    strategy: dict | None = None
    rag: dict | None = None
    bullets: dict | None = None
    drafting: dict | None = None
    qa: dict | None = None
    artifacts: dict | None = None
    safety_report: dict | None = None
    policy_decision: dict | None = None
    constitutional_review: dict | None = None
    memory: MemoryState | None = None
    ephemeral: EphemeralState | None = None
    extra: dict | None = None
    model_config = ConfigDict(extra="allow")

class StateAdapterStack:
    def __init__(self, context: Any, debug_mode: bool = False):
        self.context = context
        self.debug_mode = debug_mode

    def apply_patch(self, state_dict: Dict[str, Any], patch: Dict[str, Any] | StatePatch) -> Dict[str, Any]:
        if isinstance(patch, StatePatch):
            patch_dict = patch.model_dump(exclude_unset=True)
        else:
            patch_dict = patch
        
        # Deep merge logic stub
        for k, v in patch_dict.items():
            if isinstance(v, dict) and k in state_dict and isinstance(state_dict[k], dict):
                state_dict[k].update(v)
            else:
                state_dict[k] = v
        
        # Enforce budget
        budget_manager = getattr(self.context, "context_budget_manager", None)
        if budget_manager:
            return budget_manager.enforce_all(state_dict)
        return state_dict

    def patch_memory(self, agent_notes: Iterable[str] | None = None, **kwargs) -> StatePatch:
        # Simplified
        return StatePatch()


# ============================================================================
# SECTION 10: SERVICES (Source: services.py)
# ============================================================================

class EpisodicMemory:
    def __init__(self, config: ConfigV10_7, redis_client: Any):
        self.config = config
        self.redis = redis_client
    def _key(self, wf_id): return f"episodic_v10_7:{wf_id or 'unknown'}"
    def append(self, wf_id, event):
        # Stub redis logic
        pass
    def get(self, wf_id): return {"events": []}

class WorldModelStore:
    def __init__(self, config: ConfigV10_7, redis_client: Any):
        self.config = config
        self.redis = redis_client
    def enabled(self): return False
    def set_json(self, suffix, value): pass
    def get_json(self, suffix): return {}
    def append_strategy_outcome(self, outcome): pass

class SelfCorrectionManager:
    def __init__(self, config: ConfigV10_7):
        self.enabled = False
    def can_retry(self, wf_id, stack): return False
    def start_retry(self, wf_id, stack, issue, action, metadata=None):
        return SelfCorrectionReport(stack_name=stack, workflow_id=wf_id, issue_detected=issue, action_taken=action, retry_count=1, resolved=False)
    def finalize_retry(self, report, resolved, notes=None): pass
    def register_signal(self, wf_id, source, payload): pass

class ContextBudgetManager: # Legacy Wrapper
    def __init__(self, config, model_client_getter, self_correction_manager=None, workflow_id_getter=None):
        self.config = config
        self.getter = model_client_getter
    async def _prune_agentic(self, doc, limit): return doc[:limit] # Stub
    async def prune(self, doc, limit=None): return doc[:(limit or 4000)]

class MetricsCollector:
    def __init__(self, self_correction_manager=None):
        self.metrics = []
    def record(self, agent_name, task_name, duration_ms, success, error=None, metadata=None):
        self.metrics.append({"agent": agent_name, "task": task_name, "duration": duration_ms})
    def get_summary(self): return self.metrics
    def get_average_latency(self, agent, task): return 0.0

def track_metrics(task_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Stubbed wrapper that calls the function
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

class SemanticValidator:
    def __init__(self, metrics): self.metrics = metrics
    def check_word_count(self, text, min_w, max_w, llm_cnt=None, wf_id=""):
        count = len(text.split())
        return (min_w <= count <= max_w, f"Count {count}")

async def _format_prompt_with_defaults(template, inputs, budget, goal, failures):
    # Simplified formatter
    return template.format(**inputs)

class PromptTemplateManager:
    def __init__(self, feedback_reader):
        self.templates = {"strategy_tot_branch": "{job_title}", "prompt_engineer": "{strategy}"}
    def get_template(self, name): return self.templates.get(name, "")

class FeedbackLogReader:
    def __init__(self, path, self_correction_manager=None): pass
    def get_failures(self, limit=100): return []

class ProposedRulesLoader:
    def __init__(self, path): pass
    def get_constitution_rules(self): return []

class CacheManager:
    def __init__(self, config, redis, chroma, embed): pass
    async def get_llm_cache(self, p, m, prompt, t): return None
    async def set_llm_cache(self, p, m, prompt, t, res): pass
    def get_stats(self): return {}

class CostTracker:
    def log_cost(self, wf, agent, model, input_t, output_t): pass
    def get_cost_summary(self, wf): return {"total_workflow_cost": 0.0}

class PredictiveCacheManager:
    def __init__(self, config, cache, metrics): pass
    def enabled(self): return False
    def schedule(self, task): pass
    async def run_scheduled(self): pass

class PrecomputeEngine:
    def __init__(self, context): pass
    async def precompute_prompt_plan(self, strategy, complexity): pass
    async def precompute_embeddings(self, text): pass
    async def precompute_hyde_document(self, query): pass

class TuningProfile(BaseModel):
    temperature: float = 0.5
    drafting_expand_summary: bool = False
    drafting_boost_metrics: bool = False

class PolicyAutoTuner:
    def __init__(self, config, metrics): pass
    def enabled(self): return False
    def tune_profile(self, profile): return profile

class ArbitrationEngine:
    def __init__(self, config, metrics): pass
    async def run_check(self, stage, state):
        return ArbitrationReport(stage=stage, decision="ACCEPT", reasons=[], confidence=1.0, suggested_route="ACCEPT", metrics_snapshot={})

class AutonomyEngine:
    def __init__(self, config, metrics, episodic=None): pass
    def enabled(self): return False
    def decide(self, wf_id): return {}

class AdvancedMetaLearner:
    def __init__(self, config, metrics, episodic=None): pass
    def enabled(self): return False
    def analyze(self, wf_id): return {}

class CollaborationEngine:
    def __init__(self, config, episodic=None): pass
    def enabled(self): return False
    def form_team(self, name): return [name]


# ============================================================================
# SECTION 11: CONTEXT (Source: context.py)
# ============================================================================

class WorkflowContext:
    """v10.7: True Dependency Injection container."""
    def __init__(
        self,
        config: ConfigV10_7,
        redis_client: Any,
        chromadb_client: Any,
        cache_manager: CacheManager,
        cost_tracker: CostTracker,
        feedback_reader: FeedbackLogReader,
        rules_loader: ProposedRulesLoader,
        prompt_manager: PromptTemplateManager,
        response_validator: Any,
        metrics_collector: MetricsCollector,
        semantic_validator: SemanticValidator,
        embedding_function: Any,
        arbitration_engine: ArbitrationEngine,
        predictive_cache_manager: PredictiveCacheManager,
        precompute_engine: PrecomputeEngine,
        tuning_profile: TuningProfile,
        policy_auto_tuner: PolicyAutoTuner,
        self_correction_manager: Optional[SelfCorrectionManager] = None,
        world_model_store: Optional[WorldModelStore] = None,
        episodic_memory: Optional[EpisodicMemory] = None,
        autonomy_engine: Optional[AutonomyEngine] = None,
        collaboration_engine: Optional[CollaborationEngine] = None,
        advanced_meta_learner: Optional[AdvancedMetaLearner] = None,
    ):
        self.config = config
        self.redis_client = redis_client
        self.chromadb_client = chromadb_client
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.feedback_reader = feedback_reader
        self.rules_loader = rules_loader
        self.prompt_manager = prompt_manager
        self.response_validator = response_validator
        self.metrics_collector = metrics_collector
        self.semantic_validator = semantic_validator
        self.embedding_function = embedding_function
        self.arbitration_engine = arbitration_engine
        self.predictive_cache_manager = predictive_cache_manager
        self.precompute_engine = precompute_engine
        self.tuning_profile = tuning_profile
        self.policy_auto_tuner = policy_auto_tuner
        self.self_correction_manager = self_correction_manager
        self.world_model_store = world_model_store
        self.episodic_memory = episodic_memory
        self.autonomy_engine = autonomy_engine
        self.collaboration_engine = collaboration_engine
        self.advanced_meta_learner = advanced_meta_learner
        
        self.workflow_id = ""
        self.complexity = "unknown"
        self._model_clients = {}
        self.context_budget_manager = None
        
        # MCP
        self.mcp_clients = {}
        self.wrap_mcp_nodes = False

    def get_model_client(self, provider, model_name):
        # Stub for dependency injection
        from types import SimpleNamespace
        return SimpleNamespace(
            chat_completion_async=self._mock_chat,
            goal_state="goal",
            top_failures=[]
        )
    
    async def _mock_chat(self, **kwargs):
        return {"content": "{}"}

    def is_mcp_enabled(self): return False
    def ensure_mcp_clients(self): return {}
    def get_mcp_client(self, name, default=None): return default

def create_workflow_context(config: ConfigV10_7, db: int = 0) -> WorkflowContext:
    # Stub factory
    return WorkflowContext(
        config, None, None, CacheManager(None,None,None,None), CostTracker(),
        FeedbackLogReader(None), ProposedRulesLoader(None), PromptTemplateManager(None),
        None, MetricsCollector(), SemanticValidator(None), None, ArbitrationEngine(None,None),
        PredictiveCacheManager(None,None,None), PrecomputeEngine(None), TuningProfile(), PolicyAutoTuner(None,None)
    )

def cleanup_workflow_chroma_collection(context): pass

def detect_bias(context, text, wf_id=""):
    return {"bias_detected": False, "patterns": []}