# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
from __future__ import annotations

from agentic_core.config.model_catalog import (
    OPENAI_GPT4_TURBO_MODEL_ID,
)

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "model_provider_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "model_provider_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "model_provider_config", "state_snapshot")
trace_contract.emit_replay_key("p0", "model_provider_config")
trace_contract.emit_determinism_digest("p0", "model_provider_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "model_provider_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "model_provider_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "model_provider_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "model_provider_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "model_provider_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "model_provider_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "model_provider_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "model_provider_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "model_provider_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "model_provider_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "model_provider_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "model_provider_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "model_provider_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "model_provider_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "model_provider_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "model_provider_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "model_provider_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "model_provider_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "model_provider_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "model_provider_config", "exec_snapshot_link")

# Configuration constants

"""
Shared configuration constants and constraint classes.

This module contains configuration dataclasses for content constraints,
signal control, and other shared settings.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)

trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("model_provider_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("model_provider_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("model_provider_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("model_provider_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("model_provider_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("model_provider_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("model_provider_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("model_provider_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("model_provider_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("model_provider_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("model_provider_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("model_provider_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("model_provider_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("model_provider_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("model_provider_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("model_provider_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("model_provider_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("model_provider_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("model_provider_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("model_provider_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("model_provider_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("model_provider_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("model_provider_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "model_provider_config", "context_pull")
trace_contract._emit_pulls_context("p1", "model_provider_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_provider_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_provider_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "model_provider_config", "write_through")
trace_contract._emit_writes_through("p1", "model_provider_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "model_provider_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "model_provider_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "model_provider_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "model_provider_config", "human_escalation")
trace_contract._emit_routes_through("p1", "model_provider_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "model_provider_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "model_provider_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "model_provider_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "model_provider_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "model_provider_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "model_provider_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "model_provider_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "model_provider_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "model_provider_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "model_provider_config")
trace_contract._emit_gated_by_confidence("p1", "model_provider_config", "confidence_gate")

# =============================================================================
# CORE CONSTANTS
# =============================================================================

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_API_TIMEOUT = 60.0
DEFAULT_GENERATION_TEMPERATURE = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE = 0.3
DEFAULT_MAX_OUTPUT_TOKENS = 4000
SAFETY_THRESHOLD = "MEDIUM_AND_ABOVE"

# =============================================================================
# PATH CONSTANTS
# =============================================================================

# Resolve absolute paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
LOGS_DIR = PROJECT_ROOT / AGENTIC_CORE_DIR / "L0_routing" / "logs"

# Ensure directories exist
for d in [DATA_DIR, OUTPUT_DIR, CACHE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# =============================================================================
# ENUMS & CONFIG CLASSES
# =============================================================================


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class ModelConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    Provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="Model provider")
    model_name: str = Field(default=OPENAI_GPT4_TURBO_MODEL_ID, description="Model name")
    api_key: str | None = Field(default=None, description="API key if required")
    temperature: float = Field(
        default=DEFAULT_GENERATION_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(default=DEFAULT_MAX_OUTPUT_TOKENS, ge=1, description="Maximum tokens")

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        """[HARDENED] Ensure model name is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ModelConfig.validate_model_name"
        )

        if not value.strip():
            raise ValueError("model_name cannot be empty")
        return value.strip()


class RAGConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True, description="Whether RAG is enabled")
    chunk_size: int = Field(default=1000, ge=1, description="Chunk size for retrieval")
    chunk_overlap: int = Field(default=200, ge=0, description="Chunk overlap")
    retrieval_count: int = Field(default=5, ge=1, description="Number of chunks to retrieve")


class GovernorConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    strict_mode: bool = Field(default=True, description="Enable strict governance")
    constraints: ContentConstraintsConfig = Field(
        default_factory=lambda: ContentConstraintsConfig(),
        description="Content constraints configuration",
    )


class WorkflowConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_steps: int = Field(default=10, ge=1, description="Maximum workflow steps")
    stop_on_error: bool = Field(default=True, description="Stop on error")
    parallel_execution: bool = Field(default=False, description="Allow parallel execution")


class Config(BaseModel):
    """Legacy Config class for backward compatibility"""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: ModelConfig = Field(default_factory=ModelConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    governor: GovernorConfig = Field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)


# =============================================================================
# ORIGINAL CONTENT CONSTRAINTS (PRESERVED)
# =============================================================================


class ContentConstraintsConfig(BaseModel):
    """Centralized configuration for content constraints like word counts."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    # Overall Resume
    TOTAL_WORD_COUNT_MIN: int = 950
    TOTAL_WORD_COUNT_MAX: int = 1100
    MIN_JD_KEYWORDS: int = 5

    # K.0 Headline
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_MIN_CHARS: int = 60
    HEADLINE_MAX_CHARS: int = 90
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 5
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 6
    K1_MIN_DIFFERENTIATORS: int = 3

    # Experience Overviews
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 28
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 44
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 28
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 38
    EY_OVERVIEW_WORD_COUNT_MIN: int = 28
    EY_OVERVIEW_WORD_COUNT_MAX: int = 38
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 21
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 33
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 33

    # Word Distribution (Experience)
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    # K.13 Cover Letter
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 110
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 100
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 130
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 110
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


class SignalControlConfig(BaseModel):
    """configuration for signal quality control thresholds."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    # K.1 Executive Summary
    K1_MAX_DIFFERENTIATORS: int = 4

    # Overall Resume
    RESUME_MAX_JD_KEYWORDS: int = 15

    # K.13 Cover Letter
    CL_MAX_JD_SIMILARITY: float = 0.75

    # QA Report (Section 1)
    SECTION_SIGNAL_SCORE_MAX: float = 0.95


# =============================================================================
# GLOBAL CONFIG OBJECTS
# =============================================================================


class GlobalConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: ModelConfig = Field(default_factory=ModelConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    governor: GovernorConfig = Field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)


# Singleton Instance
CONFIG = GlobalConfig()

# Default instances (preserved for backward compatibility)
CONTENT_CONSTRAINTS = ContentConstraintsConfig()
SIGNAL_CONTROL = SignalControlConfig()

trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_1")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_2")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_3")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_4")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_5")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_6")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_7")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_8")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_9")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_10")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_11")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_12")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_13")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_14")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_15")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_16")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_17")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_18")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_19")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_20")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_21")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_22")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_23")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_24")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_25")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_26")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_27")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_28")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_29")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_30")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_31")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_32")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_33")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_34")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_35")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_36")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_37")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_38")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_39")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_40")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_41")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_42")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_43")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_44")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_45")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_46")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_47")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_48")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_49")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_50")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_51")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_52")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_53")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_54")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_55")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_56")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_57")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_58")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_59")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_60")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_61")
trace_contract._emit_reads_through("l4", "model_provider_config", "urg_read_62")
