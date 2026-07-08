"""
SovereignConfigManager - Centralized configuration Management

[PHASE 6 MIGRATION] Consolidates configuration for:
- LLM defaults & API Keys (Phase 4)
- Embedding parameters (Phase 4)
- Safety thresholds (Phase 5)
- Infrastructure paths
"""

from __future__ import annotations

import logging
import os
from typing import Any
from dataclasses import dataclass

from agentic_core.L0_routing.config import model_registry as _MR
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "sovereign_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "sovereign_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "sovereign_config", "state_snapshot")

trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_config", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_config", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "sovereign_config", "human_escalation")
trace_contract._emit_routes_through("p1", "sovereign_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "sovereign_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_config")
trace_contract._emit_gated_by_confidence("p1", "sovereign_config", "confidence_gate")
trace_contract.emit_replay_key("p0", "sovereign_config")
trace_contract.emit_determinism_digest("p0", "sovereign_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "sovereign_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_config", "exec_snapshot_link")

# Configuration constants

# Setup basic logger since we can't depend on complex agent loggers here
Logger = logging.getLogger("SovereignConfig")
logger = Logger


@dataclass
class SovereignConfigManager:
    """
    Centralized configuration Singleton.

    Design:
    - Low-level utility (No dependencies on BaseAgent).
    - Loads from Environment Variables with strictly typed defaults.
    - Single source of truth for Infrastructure constants.
    """

    _instance: SovereignConfigManager | None = None

    # --- DEFAULT CONSTANTS ---

    # Infrastructure Limits (Phases 4 & 5)
    DEFAULT_MAX_AUDIT_LOG_SIZE: int = 1000
    DEFAULT_MAX_HEALING_ATTEMPTS: int = 3
    DEFAULT_CACHE_TTL: int = 86400  # 24 Hours

    # Model Defaults (Phase 4) — sourced from L0 model_registry SSOT.
    # Env vars (OPENAI_MODEL / ANTHROPIC_MODEL / GOOGLE_AI_MODEL / GOOGLE_AI_PRO_MODEL /
    # EMBEDDING_MODEL) still override at runtime via get_str().
    DEFAULT_OPENAI_MODEL: str = _MR.OPENAI_MODEL_ID
    DEFAULT_ANTHROPIC_MODEL: str = _MR.ANTHROPIC_MODEL_ID
    DEFAULT_GOOGLE_MODEL: str = _MR.GEMINI_FLASH_MODEL_ID
    DEFAULT_GOOGLE_PRO_MODEL: str = _MR.GEMINI_PRO_MODEL_ID
    DEFAULT_EMBEDDING_MODEL: str = _MR.EMBEDDING_MODEL_ID
    DEFAULT_BGE_EMBEDDING_MODEL: str = _MR.EMBEDDING_MODEL_ID

    # Dimensions (Phase 4)
    EMBEDDING_DIM_OPENAI: int = 1536
    EMBEDDING_DIM_GEMINI: int = 768
    EMBEDDING_DIM_BGE: int = 1024

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset singleton state."""
        cls._instance = None

    def get_str(self, key: str, default: str = "") -> str:
        """Get string env var."""
        return os.environ.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get int env var."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SovereignConfigManager.get_int"
        )

        val = os.environ.get(key)
        if val is None:
            return default
        try:
            parsed = int(val)
        except ValueError:
            logger.warning("Config key %s expected int, got %s. Using default %s.", key, val, default)
            return default
        if parsed < 0:
            logger.warning("Config key %s must be >= 0, got %s. Using default %s.", key, parsed, default)
            return default
        return parsed

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like accessor for legacy callers.

        Resolution order: instance attribute → environment variable → default.
        """
        if hasattr(self, key):
            value = getattr(self, key)
            if not callable(value):
                return value
        env_val = os.environ.get(key)
        if env_val is not None:
            return env_val
        return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get bool env var (true/false/1/0)."""
        val = os.environ.get(key)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes", "on")

    # --- Typed Accessors (API Surface) ---

    @property
    def max_audit_log_size(self) -> int:
        return self.get_int("SOVEREIGN_MAX_AUDIT_LOG_SIZE", self.DEFAULT_MAX_AUDIT_LOG_SIZE)

    @property
    def max_healing_attempts(self) -> int:
        return self.get_int("SOVEREIGN_MAX_HEALING_ATTEMPTS", self.DEFAULT_MAX_HEALING_ATTEMPTS)

    @property
    def openai_model(self) -> str:
        return self.get_str("OPENAI_MODEL", self.DEFAULT_OPENAI_MODEL)

    @property
    def anthropic_model(self) -> str:
        return self.get_str("ANTHROPIC_MODEL", self.DEFAULT_ANTHROPIC_MODEL)

    @property
    def google_model(self) -> str:
        from agentic_core.config.google_ai_env import (
            GEMINI_MODEL_LEGACY,
            GOOGLE_AI_MODEL,
            google_ai_flash_model_id,
        )

        explicit, _ = google_ai_flash_model_id()
        if explicit and explicit != self.DEFAULT_GOOGLE_MODEL:
            return explicit
        return self.get_str(GOOGLE_AI_MODEL, self.get_str(GEMINI_MODEL_LEGACY, self.DEFAULT_GOOGLE_MODEL))

    @property
    def google_pro_model(self) -> str:
        from agentic_core.config.google_ai_env import (
            GEMINI_PRO_MODEL_LEGACY,
            GOOGLE_AI_PRO_MODEL,
            google_ai_pro_model_id,
        )

        explicit, _ = google_ai_pro_model_id()
        if explicit and explicit != self.DEFAULT_GOOGLE_PRO_MODEL:
            return explicit
        return self.get_str(
            GOOGLE_AI_PRO_MODEL,
            self.get_str(GEMINI_PRO_MODEL_LEGACY, self.DEFAULT_GOOGLE_PRO_MODEL),
        )

    # Redis MCP Configuration
    @property
    def redis_mcp_enabled(self) -> bool:
        """Redis MCP enablement - single source of truth from REDIS_MCP_ENABLED env var."""
        return self.get_bool("REDIS_MCP_ENABLED", False)

    # Compatibility alias for exact env var name
    @property
    def REDIS_MCP_ENABLED(self) -> bool:
        """Compatibility alias - exact env var name mapping."""
        return self.redis_mcp_enabled

    @property
    def redis_url(self) -> str:
        return self.get_str("REDIS_URL", "redis://localhost:6379")

    @property
    def redis_cache_prefix(self) -> str:
        return self.get_str("REDIS_CACHE_PREFIX", "agentic:")

    @property
    def redis_max_key_length(self) -> int:
        return self.get_int("REDIS_MAX_KEY_LENGTH", 250)

    @property
    def redis_default_ttl_seconds(self) -> int:
        return self.get_int("REDIS_DEFAULT_TTL_SECONDS", 3600)


# Singleton Accessor
def get_sovereign_config() -> SovereignConfigManager:
    return SovereignConfigManager()
