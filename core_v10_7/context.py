"""Workflow context, states, and helpers for v10.7."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from chromadb.utils import embedding_functions
from mcp import get_tool

try:  # pragma: no cover - optional runtime deps
    from redis import Redis as RedisType
    from chromadb import Client as ChromaClientType
except ImportError:  # pragma: no cover - fallback types
    RedisType = Any
    ChromaClientType = Any

from .clients import AnthropicAsyncClient, GeminiAsyncClient, OpenAIAsyncClient
from .config import ConfigV10_7
from .constants import canonical_model_name
from .exceptions import MCPClientInitializationError
from .mcp import MCPClientSpec, MCPClientStub, instantiate_mcp_client, parse_mcp_client_specs
from .models import (
    ConstitutionalReviewResult,
    GeneratedPrompts,
    HILAmbiguityReport,
    StrategyPlan,
)
from .services import (
    ArbitrationEngine,
    AdvancedMetaLearner,
    AutonomyEngine,
    CacheManager,
    CollaborationEngine,
    ContextBudgetManager,
    CostTracker,
    EpisodicMemory,
    FeedbackEntry,
    FeedbackLogReader,
    MetricsCollector,
    PolicyAutoTuner,
    PromptTemplateManager,
    PredictiveCacheManager,
    ProposedRulesLoader,
    ResponseValidator,
    SelfCorrectionManager,
    SemanticValidator,
    PrecomputeEngine,
    TuningProfile,
    WorldModelStore,
)

logger = logging.getLogger("core_v10_7")

redis_module = get_tool("redis")
chromadb_module = get_tool("chromadb")


def _resolve_path(path_like: str) -> Path:
    path_obj = Path(str(path_like)).expanduser()
    try:
        return path_obj.resolve()
    except Exception:
        return path_obj


def _path_is_durable(path_like: str, storage_config: Any) -> bool:
    if not storage_config or not path_like:
        return False

    durable_root = getattr(storage_config, "durable_root", None)
    if not durable_root:
        return False

    try:
        target_path = _resolve_path(path_like)
        durable_path = _resolve_path(durable_root)
    except Exception:
        return False

    try:
        target_path.relative_to(durable_path)
        return True
    except ValueError:
        return False


def _detect_meta_learning_persistence(config: ConfigV10_7) -> str:
    try:
        meta_cfg = config.meta_loop_config
    except AttributeError:
        return "UNKNOWN"

    if not getattr(meta_cfg, "enable_meta_learning", False):
        return "NONE"

    storage_cfg = getattr(config, "storage_config", None)
    backend = (getattr(storage_cfg, "logs_backend", "fs") or "fs").strip().upper()
    if backend == "DRIVE":
        return "DRIVE"

    durability_checks = [
        getattr(meta_cfg, "feedback_log_path", ""),
        getattr(meta_cfg, "preference_log_path", ""),
        getattr(meta_cfg, "proposed_rules_path", ""),
        getattr(meta_cfg, "generated_tools_path", ""),
    ]
    if any(_path_is_durable(path, storage_cfg) for path in durability_checks):
        return "LOCAL"
    return "NONE"


def _describe_redis_mode(redis_client: Any) -> str:
    if isinstance(redis_client, MCPClientStub):
        return "STUB"

    ping_fn = getattr(redis_client, "ping", None)
    if callable(ping_fn):
        try:
            ping_fn()
            return "REAL"
        except Exception as exc:  # pragma: no cover - network dependency
            logger.warning("Redis ping failed; continuing with degraded cache: %s", exc)
            return "UNREACHABLE"
    return "UNKNOWN"


def _describe_chroma_mode(config: ConfigV10_7, storage_config: Any) -> str:
    try:
        chroma_cfg = config.chromadb_config
    except AttributeError:
        return "UNKNOWN"

    if getattr(chroma_cfg, "use_http_client", False):
        return "REMOTE_HTTP"

    persistent_path = getattr(chroma_cfg, "persistent_path", "")
    if persistent_path and _path_is_durable(persistent_path, storage_config):
        return "PERSISTENT"
    return "EPHEMERAL"


def _log_runtime_capabilities(
    config: ConfigV10_7,
    redis_mode: str,
    chroma_mode: str,
    meta_mode: str,
) -> None:
    storage_cfg = getattr(config, "storage_config", None)
    logs_backend = (getattr(storage_cfg, "logs_backend", "fs") or "fs").upper()
    vector_backend = (getattr(storage_cfg, "vector_backend", "local") or "local").upper()
    durable_root = getattr(storage_cfg, "durable_root", "n/a") if storage_cfg else "n/a"
    ephemeral_root = getattr(storage_cfg, "ephemeral_root", "n/a") if storage_cfg else "n/a"

    logger.info(
        "Runtime storage capabilities | Meta-learning=%s | Redis=%s | Chroma=%s | Logs backend=%s | Vector backend=%s",
        meta_mode,
        redis_mode,
        chroma_mode,
        logs_backend,
        vector_backend,
    )
    logger.info(
        "Storage roots | durable=%s | ephemeral=%s",
        durable_root,
        ephemeral_root,
    )


def _mcp_get(config_obj: Any, key: str, default: Any) -> Any:
    """
    Helper to read MCP config fields from either a dict-like structure
    or an attribute-based config object. This makes context robust to
    both styles of ConfigV10_7.mcp_config.
    """
    # Dict-like
    if isinstance(config_obj, dict):
        return config_obj.get(key, default)
    # Object-like (dataclass / simple namespace)
    return getattr(config_obj, key, default)


class WorkflowContext:
    """
    v10.7: True Dependency Injection container.
    """

    def __init__(
        self,
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
        embedding_function: embedding_functions.EmbeddingFunction,
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
        redis_required = bool(getattr(config.redis_config, "required", True))
        if redis_required:
            try:
                redis_client.ping()
            except Exception as e:
                raise RuntimeError(
                    f"Redis is required but not running: {e}"
                ) from e
            logger.warning(
                "Redis mode: REQUIRED — workflow will fail if Redis is not running."
            )
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
        self.arbitration_engine = arbitration_engine
        self.predictive_cache_manager = predictive_cache_manager
        self.precompute_engine = precompute_engine
        self.self_correction_manager = self_correction_manager
        self.tuning_profile = tuning_profile
        self.policy_auto_tuner = policy_auto_tuner
        self.world_model_store = world_model_store
        self.episodic_memory = episodic_memory
        self.autonomy_engine = autonomy_engine
        self.collaboration_engine = collaboration_engine
        self.advanced_meta_learner = advanced_meta_learner

        # This is injected *after* __init__ to break circular dependency
        self.context_budget_manager: ContextBudgetManager = None  # type: ignore

        self._model_clients: Dict[str, Any] = {}

        # MCP integration state
        self.mcp_clients: Dict[str, Any] = {}
        self._mcp_initialized: bool = False
        self._mcp_client_specs: List[MCPClientSpec] = []
        self._mcp_fallback_mode: str = "error"
        self._mcp_fallback_parameters: Dict[str, Any] = {}
        self._mcp_errors: Dict[str, str] = {}
        self._mcp_enabled: bool = False
        self.wrap_mcp_nodes: bool = False

        self._load_mcp_config()

        logger.info("WorkflowContext initialized with v10.7 injected dependencies")

    def get_model_client(self, provider: str, model_name: str):
        canonical_name = canonical_model_name(model_name)
        key = f"{provider}:{canonical_name}"
        if key not in self._model_clients:
            base_args = {
                "config": self.config,
                "model_name": canonical_name,
                "cache_manager": self.cache_manager,
                "cost_tracker": self.cost_tracker,
                "metrics_collector": self.metrics_collector,
                "workflow_id": self.workflow_id,
                "agent_name": "",
            }
            if provider == "anthropic":
                self._model_clients[key] = AnthropicAsyncClient(**base_args)
            elif provider == "google":
                self._model_clients[key] = GeminiAsyncClient(**base_args)
            elif provider == "openai":
                self._model_clients[key] = OpenAIAsyncClient(**base_args)
            else:
                raise ValueError(f"Unknown provider: {provider}")

        client = self._model_clients[key]
        client.workflow_id = self.workflow_id
        client.model_name = canonical_name
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
            # No MCP config present at all
            return

        enabled = bool(_mcp_get(mcp_config, "enabled", False))
        self._mcp_enabled = enabled
        self.wrap_mcp_nodes = bool(_mcp_get(mcp_config, "wrap_nodes_by_default", False))

        if not enabled:
            return

        fallback_mode = str(_mcp_get(mcp_config, "fallback_mode", "error") or "error").lower()
        if fallback_mode not in {"error", "stub"}:
            logger.warning("Unknown MCP fallback mode '%s'; defaulting to 'error'.", fallback_mode)
            fallback_mode = "error"
        self._mcp_fallback_mode = fallback_mode

        fallback_parameters = _mcp_get(mcp_config, "fallback_parameters", {})
        if fallback_parameters is None:
            fallback_parameters = {}
        if not isinstance(fallback_parameters, dict):
            logger.warning("MCP fallback parameters must be a mapping; ignoring invalid value.")
            fallback_parameters = {}
        self._mcp_fallback_parameters = fallback_parameters

        raw_clients = _mcp_get(mcp_config, "clients", [])
        try:
            self._mcp_client_specs = parse_mcp_client_specs(raw_clients)
        except Exception as exc:
            raise MCPClientInitializationError(f"Invalid MCP configuration: {exc}") from exc

    def is_mcp_enabled(self) -> bool:
        return self._mcp_enabled

    def ensure_mcp_clients(self) -> Dict[str, Any]:
        """Initialise MCP clients if required and return the registry."""

        if self._mcp_initialized:
            return self.mcp_clients

        if not self._mcp_enabled:
            self.mcp_clients = {}
            self._mcp_initialized = True
            return self.mcp_clients

        clients: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        for spec in self._mcp_client_specs:
            try:
                clients[spec.name] = instantiate_mcp_client(spec)
            except Exception as exc:
                errors[spec.name] = str(exc)
                if spec.optional:
                    logger.warning(
                        "MCP client '%s' failed to initialise (%s). Using stub fallback.",
                        spec.name,
                        exc,
                    )
                    clients[spec.name] = MCPClientStub(
                        spec.name,
                        {"error": str(exc), **spec.parameters, **self._mcp_fallback_parameters},
                    )
                elif self._mcp_fallback_mode == "stub":
                    logger.error(
                        "Required MCP client '%s' failed during initialisation and cannot fall back to a stub.",
                        spec.name,
                    )
                    raise MCPClientInitializationError(
                        f"Failed to initialize MCP client '{spec.name}': {exc}"
                    ) from exc
                else:
                    raise MCPClientInitializationError(
                        f"Failed to initialize MCP client '{spec.name}': {exc}"
                    ) from exc

        self.mcp_clients = clients
        self._mcp_errors = errors
        self._mcp_initialized = True
        return self.mcp_clients

    def get_mcp_client(self, name: str, default: Optional[Any] = None) -> Any:
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
    db: Optional[int] = None,
    allow_memory_fallback: bool = False,
):
    """
    DESTRUCTIVE OVERWRITE — v10.7 Colab / Local Runtime Patch

    Purpose:
    LangGraph 1.x removed the 'langgraph.checkpoint' module that v10.7 relied on.
    RedisSaver and SqliteSaver no longer exist under those import paths, so attempting
    to initialize them raises ModuleNotFoundError and halts the workflow.

    For Colab, local laptops, or any environment without a persistent checkpointer,
    checkpointing is unnecessary — single-run DAG execution works perfectly in-memory.

    This replacement function disables all checkpointing and forces LangGraph to run
    purely in-memory by returning None. All upstream graph.compile() logic accepts
    checkpointer=None and proceeds normally.

    Compatible with:
      • LangGraph 1.x
      • Colab with pip-installed langgraph
      • Any env lacking Redis or Sqlite checkpoint modules
    """

    # Force in-memory execution — do NOT attempt Redis or Sqlite.
    return None


def create_workflow_context(config: ConfigV10_7, db: int = 0) -> WorkflowContext:
    """
    v10.7 REFACTOR: Centralized Composition Root.
    """
    logger.info(f"Creating WorkflowContext with {config.schema_version}...")

    storage_config = getattr(config, "storage_config", None)

    # 1. Initialize Clients (Redis, ChromaDB, Embedding)
    redis_ctor = getattr(redis_module, "Redis", None)
    if callable(redis_ctor):
        redis_client = redis_ctor(
            host=config.redis_config.host,
            port=config.redis_config.port,
            db=db or config.redis_config.db,
        )
    else:  # pragma: no cover - defensive stub fallback
        redis_client = MCPClientStub(
            "redis",
            {
                "host": config.redis_config.host,
                "port": config.redis_config.port,
                "db": db or config.redis_config.db,
            },
        )

    if config.chromadb_config.use_http_client:
        http_ctor = getattr(chromadb_module, "HttpClient", None)
        if callable(http_ctor):
            chromadb_client = http_ctor(
                host=config.chromadb_config.host,
                port=config.chromadb_config.port,
            )
        else:  # pragma: no cover - defensive stub fallback
            client_ctor = getattr(chromadb_module, "Client", None)
            chromadb_client = client_ctor() if callable(client_ctor) else MCPClientStub("chromadb")
    else:
        persistent_ctor = getattr(chromadb_module, "PersistentClient", None)
        if callable(persistent_ctor):
            chromadb_client = persistent_ctor(path=config.chromadb_config.persistent_path)
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
    self_correction_manager = SelfCorrectionManager(config=config)
    world_model_store = WorldModelStore(config=config, redis_client=redis_client)
    episodic_memory = EpisodicMemory(config=config, redis_client=redis_client)
    feedback_reader = FeedbackLogReader(
        config.meta_loop_config.feedback_log_path,
        self_correction_manager=self_correction_manager,
    )
    cache_manager = CacheManager(
        config=config,
        redis_client=redis_client,
        chromadb_client=chromadb_client,
        embedding_function=embedding_function,
    )
    cost_tracker = CostTracker()
    rules_loader = ProposedRulesLoader(config.meta_loop_config.proposed_rules_path)
    prompt_manager = PromptTemplateManager(feedback_reader=feedback_reader)
    response_validator = ResponseValidator()
    metrics_collector = MetricsCollector(self_correction_manager=self_correction_manager)
    tuning_profile = TuningProfile()
    policy_auto_tuner = PolicyAutoTuner(config, metrics_collector)
    predictive_cache_manager = PredictiveCacheManager(
        config=config,
        cache_manager=cache_manager,
        metrics=metrics_collector,
    )
    precompute_engine = PrecomputeEngine(context=None)  # placeholder
    semantic_validator = SemanticValidator(metrics_collector=metrics_collector)
    arbitration_engine = ArbitrationEngine(config=config, metrics=metrics_collector)
    metrics_collector.predictive_cache_manager = predictive_cache_manager

    autonomy_engine = AutonomyEngine(
        config=config,
        metrics=metrics_collector,
        episodic_memory=None,  # Placeholder for PR9 wiring
    )

    collaboration_engine = CollaborationEngine(
        config=config,
        episodic_memory=None,
    )

    advanced_meta_learner = AdvancedMetaLearner(
        config=config,
        metrics=metrics_collector,
        episodic_memory=None,
    )

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
        embedding_function=embedding_function,
        arbitration_engine=arbitration_engine,
        predictive_cache_manager=predictive_cache_manager,
        precompute_engine=precompute_engine,
        self_correction_manager=self_correction_manager,
        tuning_profile=tuning_profile,
        policy_auto_tuner=policy_auto_tuner,
        world_model_store=world_model_store,
        episodic_memory=episodic_memory,
        autonomy_engine=autonomy_engine,
        collaboration_engine=collaboration_engine,
        advanced_meta_learner=advanced_meta_learner,
    )

    # 4. v10.7 (Fix #14): Resolve circular dependency for ContextBudgetManager
    context_budget_manager = ContextBudgetManager(
        config=config,
        model_client_getter=context.get_model_client,  # Pass the method
        self_correction_manager=self_correction_manager,
        workflow_id_getter=lambda: context.workflow_id,
    )
    # 5. Inject the final service
    context.context_budget_manager = context_budget_manager

    # Wire the precompute engine now that context exists
    precompute_engine.context = context

    redis_mode = _describe_redis_mode(redis_client)
    chroma_mode = _describe_chroma_mode(config, storage_config)
    meta_mode = _detect_meta_learning_persistence(config)
    _log_runtime_capabilities(config, redis_mode, chroma_mode, meta_mode)

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


def detect_bias(context: WorkflowContext, text: str, workflow_id: str = "") -> Dict[str, Any]:
    """Centralized bias detection service shared by agents and tools."""

    logger.debug("Running centralized bias detection service.")

    base_patterns = ["he/she", "his/her", "male/female", "young", "old"]
    rules = context.rules_loader.get_constitution_rules()

    bias_patterns: List[str] = base_patterns.copy()
    for rule in rules:
        if isinstance(rule, dict) and "bias_patterns" in rule:
            patterns = rule.get("bias_patterns")
            if isinstance(patterns, list):
                bias_patterns.extend(str(p) for p in patterns)

    normalized_text = text.lower()
    detected_patterns = sorted({p for p in bias_patterns if p.lower() in normalized_text})
    bias_detected = len(detected_patterns) > 0

    result = {
        "bias_detected": bias_detected,
        "patterns": detected_patterns,
        "bias_score": (len(detected_patterns) / len(bias_patterns)) if bias_patterns else 0.0,
        "dynamic_rules_applied": len(rules),
    }

    return result


# ============================================================================
# STATE MODELS (v10.7: Fix #10 - A2A Comms)
# ============================================================================

@dataclass
class ResumeContext:
    master_resume: Dict[str, Any] = field(default_factory=dict)
    sanitized_resume: Dict[str, Any] = field(default_factory=dict)
    experience_bullets: List[Dict] = field(default_factory=list)


@dataclass
class JobContext:
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""
    parsed_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyContext:
    strategy_plan: Optional[StrategyPlan] = None
    tot_branches: List[Dict] = field(default_factory=list)


@dataclass
class PromptContext:
    prompts: Optional[GeneratedPrompts] = None


@dataclass
class BulletContext:
    generated_bullets: List[Dict] = field(default_factory=list)
    critiqued_bullets: List[Dict] = field(default_factory=list)


@dataclass
class DraftContext:
    sections: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAContext:
    validation_results: Dict[str, Any] = field(default_factory=dict)
    qa_passed: bool = False
    constitutional_review: Optional[ConstitutionalReviewResult] = None  # v10.7 (Fix #30)


@dataclass
class ArtifactContext:
    artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataContext:
    workflow_id: str = ""
    timestamp: str = ""
    cost: float = 0.0
    retries: Dict[str, int] = field(
        default_factory=lambda: {"bullet_retries": 0, "qa_retries": 0}
    )
    complexity: str = "unknown"


@dataclass
class SafetyContext:
    pii_detected: bool = False
    bias_detected: bool = False
    safety_notes: List[str] = field(default_factory=list)
    injection_detected: bool = False


@dataclass
class FeedbackContext:
    recent_feedback: List[FeedbackEntry] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    selected_agents: Dict[str, str] = field(default_factory=dict)


@dataclass
class HILContext:
    ambiguity_detected: bool = False
    ambiguity_report: Optional[HILAmbiguityReport] = None
    next_step: str = ""
    payload: Optional[str] = None


# v10.7 (Fix #10): Agent-to-Agent Communication State
@dataclass
class A2AMessage:
    sender: str
    recipient: str  # Can be "ALL"
    message_type: str  # e.g., "ERROR", "METRIC", "UI_EVENT"
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class A2AContext:
    messages: List[A2AMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized: List[A2AMessage] = []
        for raw in self.messages:
            if isinstance(raw, A2AMessage):
                normalized.append(raw)
            elif isinstance(raw, dict):
                try:
                    normalized.append(A2AMessage(**raw))
                except TypeError:
                    continue
        self.messages = normalized

    def append(
        self,
        *,
        sender: str,
        message_type: str,
        payload: Dict[str, Any],
        recipient: str = "ALL",
        timestamp: Optional[str] = None,
    ) -> None:
        message = A2AMessage(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=dict(payload or {}),
            timestamp=timestamp or datetime.now().isoformat(),
        )
        self.messages.append(message)


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
    a2a: A2AContext = field(default_factory=A2AContext)  # v10.7 (Fix #10)

    def to_dict(self) -> Dict[str, Any]:
        """v10.7: Custom serializer to handle nested Pydantic models."""
        data = asdict(self)

        # Manually serialize nested Pydantic models to dicts
        if self.strategy.strategy_plan:
            data["strategy"]["strategy_plan"] = self.strategy.strategy_plan.model_dump()
        if self.prompts.prompts:
            data["prompts"]["prompts"] = self.prompts.prompts.model_dump()
        if self.hil.ambiguity_report:
            data["hil"]["ambiguity_report"] = self.hil.ambiguity_report.model_dump()
        if self.qa.constitutional_review:  # v10.7 (Fix #30)
            data["qa"]["constitutional_review"] = self.qa.constitutional_review.model_dump()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MainGraphState":
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
        state.a2a = A2AContext(**data.get("a2a", {}))  # v10.7 (Fix #10)

        # Deserialize QA
        qa_data = data.get("qa", {})
        qa_review_data = qa_data.get("constitutional_review")
        state.qa = QAContext(
            validation_results=qa_data.get("validation_results", {}),
            qa_passed=qa_data.get("qa_passed", False),
            constitutional_review=ConstitutionalReviewResult.model_validate(qa_review_data)
            if qa_review_data and isinstance(qa_review_data, dict)
            else None,
        )

        # Deserialize Strategy
        strategy_data = data.get("strategy", {})
        strategy_plan_data = strategy_data.get("strategy_plan")
        state.strategy = StrategyContext(
            strategy_plan=StrategyPlan.model_validate(strategy_plan_data)
            if strategy_plan_data and isinstance(strategy_plan_data, dict)
            else None,
            tot_branches=strategy_data.get("tot_branches", []),
        )

        # Deserialize Prompts
        prompts_data = data.get("prompts", {})
        prompts_model_data = prompts_data.get("prompts")
        state.prompts = PromptContext(
            prompts=GeneratedPrompts.model_validate(prompts_model_data)
            if prompts_model_data and isinstance(prompts_model_data, dict)
            else None
        )

        # Deserialize HIL
        hil_data = data.get("hil", {})
        hil_report_data = hil_data.get("ambiguity_report")
        state.hil = HILContext(
            ambiguity_detected=hil_data.get("ambiguity_detected", False),
            ambiguity_report=HILAmbiguityReport.model_validate(hil_report_data)
            if hil_report_data and isinstance(hil_report_data, dict)
            else None,
            next_step=hil_data.get("next_step", ""),
            payload=hil_data.get("payload"),
        )
        return state


@dataclass
class MetaGraphState:
    """v10.7: Meta-learning graph state."""

    raw_logs: Dict[str, str] = field(default_factory=dict)
    log_summary: Dict[str, Any] = field(default_factory=dict)
    patterns: List[Dict] = field(default_factory=list)
    hypotheses: List[Dict] = field(default_factory=list)
    proposal: Dict[str, Any] = field(default_factory=dict)
    critique: Dict[str, Any] = field(default_factory=dict)
    replan_count: int = 0
    workflow_id: str = ""
    generated_tool_code: Optional[str] = None


__all__ = [
    "WorkflowContext",
    "get_checkpointer",
    "create_workflow_context",
    "cleanup_workflow_chroma_collection",
    "detect_bias",
    "ResumeContext",
    "JobContext",
    "StrategyContext",
    "PromptContext",
    "BulletContext",
    "DraftContext",
    "QAContext",
    "ArtifactContext",
    "MetadataContext",
    "SafetyContext",
    "FeedbackContext",
    "HILContext",
    "A2AMessage",
    "A2AContext",
    "MainGraphState",
    "MetaGraphState",
]
