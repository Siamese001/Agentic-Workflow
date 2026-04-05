"""
L4 Versioned Config SSOT — Phase 2

Authoritative versioned configs for policy, routing, model, and budget.
Each config exposes version, canonical_bytes(), and config_hash (sha256).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class PolicyConfig:
    """Tool allowlist, file scope, and budget policy."""

    version: str = "1.0.0"
    tool_allowlist: tuple[str, ...] = (
        "file_read",
        "file_write",
        "ast_parse",
        "llm_call",
        "redis_get",
        "redis_set",
        "pinecone_query",
        "pinecone_upsert",
    )
    file_scope_whitelist: tuple[str, ...] = ("/tmp", "/workspace", AGENTIC_CORE_DIR)
    token_budget: int = 1000000

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PolicyConfig.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PolicyConfig.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "PolicyConfig.canonical_bytes")

        doc = {
            "version": self.version,
            "tool_allowlist": sorted(self.tool_allowlist),
            "file_scope_whitelist": sorted(self.file_scope_whitelist),
            "token_budget": self.token_budget,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @property
    def config_hash(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass
class RoutingConfig:
    """Mode routing thresholds and escalation parameters."""

    version: str = "1.0.0"
    depth_breaker: int = 10
    escalation_threshold: float = 0.85
    fallback_mode: str = "safe"
    anomaly_routing_threshold: float = 0.75
    escalation_window_ticks: int = 10
    escalation_severity_threshold: float = 0.75
    escalation_violation_code_denylist: tuple[str, ...] = ()
    escalation_mode: str = "normal"

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RoutingConfig.canonical_bytes")

        doc = {
            "version": self.version,
            "anomaly_routing_threshold": self.anomaly_routing_threshold,
            "depth_breaker": self.depth_breaker,
            "escalation_mode": self.escalation_mode,
            "escalation_severity_threshold": self.escalation_severity_threshold,
            "escalation_threshold": self.escalation_threshold,
            "escalation_violation_code_denylist": sorted(self.escalation_violation_code_denylist),
            "escalation_window_ticks": self.escalation_window_ticks,
            "fallback_mode": self.fallback_mode,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @property
    def config_hash(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass
class ModelConfig:
    """Model name/version used by cognition and embedding."""

    version: str = "1.0.0"
    cognition_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ModelConfig.canonical_bytes")

        doc = {
            "version": self.version,
            "cognition_model": self.cognition_model,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @property
    def config_hash(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass
class BudgetConfig:
    """Token budget ceilings, retry ceilings, max_k."""

    version: str = "1.0.0"
    token_budget: int = 1000000
    max_k: int = 10
    max_retries: int = 3
    backoff_base_seconds: float = 1.0

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "BudgetConfig.canonical_bytes")

        doc = {
            "version": self.version,
            "token_budget": self.token_budget,
            "max_k": self.max_k,
            "max_retries": self.max_retries,
            "backoff_base_seconds": self.backoff_base_seconds,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @property
    def config_hash(self) -> str:
        return _sha256(self.canonical_bytes())


@dataclass
class L4ActiveConfigs:
    """
    L4 SSOT registry of active versioned configs.

    This is the single authoritative source consulted by L2.0 validation.
    """

    policy: PolicyConfig = field(default_factory=PolicyConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)

    def hashes(self) -> dict[str, str]:
        return {
            "policy_hash": self.policy.config_hash,
            "routing_hash": self.routing.config_hash,
            "model_hash": self.model.config_hash,
            "budget_hash": self.budget.config_hash,
        }


@dataclass
class MLCacheConfig:
    """Versioned ML cache policy: TTL, max entries, eviction mode."""

    version: str = "1.0.0"
    default_ttl_seconds: int = 3600
    max_entries: int = 1000
    eviction_mode: str = "lru"

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "MLCacheConfig.canonical_bytes")

        doc = {
            "version": self.version,
            "default_ttl_seconds": self.default_ttl_seconds,
            "eviction_mode": self.eviction_mode,
            "max_entries": self.max_entries,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @property
    def config_hash(self) -> str:
        return _sha256(self.canonical_bytes())


_ACTIVE_CONFIGS = L4ActiveConfigs()
_ML_CACHE_CONFIG = MLCacheConfig()


def get_active_configs() -> L4ActiveConfigs:
    """Return the module-level L4 SSOT active config registry."""
    return _ACTIVE_CONFIGS


def get_ml_cache_config() -> MLCacheConfig:
    """Return the module-level ML cache config singleton."""
    return _ML_CACHE_CONFIG
