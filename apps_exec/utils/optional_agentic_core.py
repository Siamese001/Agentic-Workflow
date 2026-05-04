from __future__ import annotations

import enum
import logging
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def _noop(*args: Any, **kwargs: Any) -> None:
    return None


class _LayerSegment(str, enum.Enum):
    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"
    L5_POLICY = "L5_POLICY"
    L6_OBSERVABILITY = "L6_OBSERVABILITY"


class _LifecycleModule(types.ModuleType):
    LayerSegment = _LayerSegment

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_emit_") or name.startswith("emit_"):
            return _noop
        raise AttributeError(name)


class _SemanticCacheMixin:
    pass


class _EmbeddingMixin:
    pass


@dataclass
class _ADGProfile:
    behavioral_score: float = 0.5
    antipattern_signals: set[str] = field(default_factory=set)


class _ADGBehavioralIndex:
    @classmethod
    def from_latest(cls, _repo_root: Path) -> "_ADGBehavioralIndex | None":
        return None

    def profile_for(self, _path: Path) -> _ADGProfile | None:
        return None


@dataclass
class _PreRunReport:
    summary: str = "agentic_core unavailable; ADG bootstrap skipped"
    layer_violation_count: int = 0
    scope_widening_events: list[str] = field(default_factory=list)
    route_mode: str = "ALLOW"


@dataclass
class _AppsQwenRequest:
    prompt: str = ""
    max_tokens: int = 0
    temperature: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class _AppsQwenGateway:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    async def infer(self, _request: Any) -> dict[str, Any]:
        raise RuntimeError("agentic_core Qwen gateway unavailable in standalone apps_exec package")


class _AppsQwenTelemetry:
    @staticmethod
    def start_session(_app_name: str) -> str:
        return "standalone-session"


@dataclass
class _VllmGatewayAdapterRequest:
    prompt: str = ""
    max_tokens: int = 0
    temperature: float = 0.0


@dataclass
class _LocalFirstDisposition:
    route: str = "DISABLED"
    reason: str = "agentic_core unavailable"

    def model_dump(self) -> dict[str, Any]:
        return {"route": self.route, "reason": self.reason}


class _RoutingPredicatesModule(types.ModuleType):
    def should_route_to_local_vllm(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def resolve_local_first_disposition(self, *args: Any, **kwargs: Any) -> _LocalFirstDisposition:
        return _LocalFirstDisposition()


def _install_module(name: str, module: types.ModuleType) -> None:
    sys.modules.setdefault(name, module)


def install_optional_agentic_core_stubs() -> None:
    try:
        import agentic_core.runtime.contracts.lifecycle_trace_contract  # noqa: F401

        return
    except ImportError:
        _log.debug("agentic_core not available; installing standalone stubs")

    agentic_core = types.ModuleType("agentic_core")
    runtime = types.ModuleType("agentic_core.runtime")
    contracts = types.ModuleType("agentic_core.runtime.contracts")
    lifecycle = _LifecycleModule("agentic_core.runtime.contracts.lifecycle_trace_contract")

    mixins = types.ModuleType("agentic_core.mixins")
    semantic_cache = types.ModuleType("agentic_core.mixins.semantic_cache_mixin")
    semantic_cache.SemanticCacheMixin = _SemanticCacheMixin
    embedding = types.ModuleType("agentic_core.mixins.embedding_mixin")
    embedding.EmbeddingMixin = _EmbeddingMixin

    l3 = types.ModuleType("agentic_core.L3_orchestration")
    inference = types.ModuleType("agentic_core.L3_orchestration.inference")
    qwen = types.ModuleType("agentic_core.L3_orchestration.inference.qwen_vllm")
    qwen.AppsQwenGateway = _AppsQwenGateway
    qwen.AppsQwenRequest = _AppsQwenRequest
    qwen.apps_qwen_telemetry = _AppsQwenTelemetry()

    adg = types.ModuleType("agentic_core.adg")
    adg_app = types.ModuleType("agentic_core.adg.applications")
    execute_ssot = types.ModuleType("agentic_core.adg.applications.execute_ssot_integration")
    execute_ssot.build_pre_run_report = lambda *args, **kwargs: _PreRunReport()
    adg_runtime = types.ModuleType("agentic_core.adg.runtime")
    behavioral_index = types.ModuleType("agentic_core.adg.runtime.behavioral_index")
    behavioral_index.ADGBehavioralIndex = _ADGBehavioralIndex

    l2 = types.ModuleType("agentic_core.L2_execution")
    l2_types = types.ModuleType("agentic_core.L2_execution.types")
    vllm_types = types.ModuleType("agentic_core.L2_execution.types.vllm_gateway_adapter_types")
    vllm_types.VllmGatewayAdapterRequest = _VllmGatewayAdapterRequest
    local_first = types.ModuleType("agentic_core.L2_execution.types.local_first_disposition")
    local_first.LocalFirstDisposition = _LocalFirstDisposition

    l4 = types.ModuleType("agentic_core.L4_state")
    l4_config = types.ModuleType("agentic_core.L4_state.config")
    routing_predicates = _RoutingPredicatesModule("agentic_core.L4_state.config.vllm_routing_predicates")

    _install_module("agentic_core", agentic_core)
    _install_module("agentic_core.runtime", runtime)
    _install_module("agentic_core.runtime.contracts", contracts)
    _install_module("agentic_core.runtime.contracts.lifecycle_trace_contract", lifecycle)
    _install_module("agentic_core.mixins", mixins)
    _install_module("agentic_core.mixins.semantic_cache_mixin", semantic_cache)
    _install_module("agentic_core.mixins.embedding_mixin", embedding)
    _install_module("agentic_core.L3_orchestration", l3)
    _install_module("agentic_core.L3_orchestration.inference", inference)
    _install_module("agentic_core.L3_orchestration.inference.qwen_vllm", qwen)
    _install_module("agentic_core.adg", adg)
    _install_module("agentic_core.adg.applications", adg_app)
    _install_module("agentic_core.adg.applications.execute_ssot_integration", execute_ssot)
    _install_module("agentic_core.adg.runtime", adg_runtime)
    _install_module("agentic_core.adg.runtime.behavioral_index", behavioral_index)
    _install_module("agentic_core.L2_execution", l2)
    _install_module("agentic_core.L2_execution.types", l2_types)
    _install_module("agentic_core.L2_execution.types.vllm_gateway_adapter_types", vllm_types)
    _install_module("agentic_core.L2_execution.types.local_first_disposition", local_first)
    _install_module("agentic_core.L4_state", l4)
    _install_module("agentic_core.L4_state.config", l4_config)
    _install_module("agentic_core.L4_state.config.vllm_routing_predicates", routing_predicates)


# -----------------------------
# Optional apps_shared stubs
# -----------------------------


@dataclass
class _SharedRepoSignalSnapshot:
    captured_at: str = ""
    adg: dict[str, Any] = field(default_factory=dict)
    tests: dict[str, Any] = field(default_factory=dict)
    ci: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, str] = field(default_factory=dict)
    baseline: str = "standalone"


class _RepoSignalAdapter:
    def __init__(self, _repo_root: Path) -> None:
        self.repo_root = _repo_root

    def collect(self) -> _SharedRepoSignalSnapshot:
        return _SharedRepoSignalSnapshot()


@dataclass
class _GovernedAppRunRecord:
    run_id: str
    query: str
    l1_sub_queries: tuple[str, ...] = ()
    l1_fallback: bool = False
    l0_intent: str = "exec_brief"
    l0_target: str = "exec_brief_assembly"
    l0_confidence: float = 0.0
    l0_fallback: bool = True
    c0_raw_count: int = 0
    c0_shaped_count: int = 0
    c0_collection: str = ""
    disposition: str = "DEGRADED"
    gate_disposition: str = "ALLOW"
    grounded: bool = False
    citation_count: int = 0
    support_coverage: float = 0.0
    l6_ingested: bool = False
    l2_executed: bool = False
    error: str = ""


class _GovernedAppRunner:
    def __init__(self, collection: str = "") -> None:
        self.collection = collection

    def run_governed_core(
        self, query: str, run_id: str, inject_chunks: list[Any] | None = None
    ) -> _GovernedAppRunRecord:
        return _GovernedAppRunRecord(run_id=run_id, query=query, c0_collection=self.collection)


class _BaseSpineAdapter:
    def __init__(
        self, cid_registry: Any, orchestrator: Any, *, prefix: str, max_reentry_attempts: int = 3
    ) -> None:
        self.cid_registry = cid_registry
        self.orchestrator = orchestrator
        self.prefix = prefix
        self.max_reentry_attempts = max_reentry_attempts

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        return {"cid": f"{self.prefix}standalone", "intent_input": intent_input}


def install_optional_apps_shared_stubs() -> None:
    try:
        import apps_shared.data_adapters  # noqa: F401

        return
    except ImportError:
        _log.debug("apps_shared not available; installing standalone stubs")

    apps_shared = types.ModuleType("apps_shared")
    data_adapters = types.ModuleType("apps_shared.data_adapters")
    data_adapters.RepoSignalAdapter = _RepoSignalAdapter
    data_adapters.RepoSignalSnapshot = _SharedRepoSignalSnapshot

    integrations = types.ModuleType("apps_shared.integrations")
    governed_runner = types.ModuleType("apps_shared.integrations.governed_app_runner")
    governed_runner.GovernedAppRunRecord = _GovernedAppRunRecord
    governed_runner.GovernedAppRunner = _GovernedAppRunner

    spine = types.ModuleType("apps_shared.spine")
    base_spine = types.ModuleType("apps_shared.spine.base_spine_adapter")
    base_spine.BaseSpineAdapter = _BaseSpineAdapter

    _install_module("apps_shared", apps_shared)
    _install_module("apps_shared.data_adapters", data_adapters)
    _install_module("apps_shared.integrations", integrations)
    _install_module("apps_shared.integrations.governed_app_runner", governed_runner)
    _install_module("apps_shared.spine", spine)
    _install_module("apps_shared.spine.base_spine_adapter", base_spine)
