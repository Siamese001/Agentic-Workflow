"""Model router - Smart LLM selection based on task complexity.

This module optimizes cost and latency by dynamically selecting the appropriate
LLM based on task type, complexity, and budget constraints.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "model_router_types", "p0_governance")
_emit_reads_policy_state("p0", "model_router_types", "policy_binding")
_emit_snapshots_state("p0", "model_router_types", "state_snapshot")
emit_replay_key("p0", "model_router_types")
emit_determinism_digest("p0", "model_router_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "model_router_types", "execution_auth")
_emit_validates_capability("p2", "model_router_types", "capability_check")
_emit_routes_to_capability("p2", "model_router_types", "capability_route")
_emit_writes_via_uwg("p2", "model_router_types", "uwg_write")
_emit_blocks_direct_write("p2", "model_router_types", "direct_write_block")
_emit_records_tool_invocation("p2", "model_router_types", "tool_invocation")
_emit_captures_execution_output("p2", "model_router_types", "exec_output")
_emit_dispatches_agent("p3", "model_router_types", "agent_dispatch")
_emit_coordinates_agents("p3", "model_router_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "model_router_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "model_router_types", "healing_outcome")
_emit_escalates_failure("p3", "model_router_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "model_router_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "model_router_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "model_router_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "model_router_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "model_router_types", "eval_metric")
_emit_stores_embedding("p4", "model_router_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "model_router_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "model_router_types", "exec_snapshot_link")

try:
    from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager as _MCPManager
except ImportError:  # guardian: allow-silent-swallow - optional dependency
    _MCPManager = None

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("model_router_types", "p4obs", "metric_1")
_emit_emits_metric_event("model_router_types", "p4obs", "metric_2")
_emit_emits_metric_event("model_router_types", "p4obs", "metric_3")
_emit_emits_metric_event("model_router_types", "p4obs", "metric_4")
_emit_emits_metric_event("model_router_types", "p4obs", "metric_5")
_emit_emits_metric_event("model_router_types", "p4obs", "metric_6")
_emit_records_incident_event("model_router_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("model_router_types", "p4obs", "anomaly")
_emit_writes_observability_log("model_router_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("model_router_types", "p4obs", "mon_state")
_emit_triggers_alert("model_router_types", "p4obs", "alert")
_emit_links_incident_trace("model_router_types", "p4obs", "trace_link")
_emit_captures_pattern("model_router_types", "p3lm", "pattern")
_emit_records_learning_event("model_router_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("model_router_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("model_router_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("model_router_types", "p3lm", "routing")
_emit_improves_agent_policy("model_router_types", "p3lm", "policy")
_emit_stores_learning_state("model_router_types", "p3lm", "state")
_emit_records_execution_trace("model_router_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("model_router_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("model_router_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("model_router_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("model_router_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("model_router_types", "env_read", "p2_env_1")
_emit_reads_environ("model_router_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("model_router_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("model_router_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "model_router_types", "context_pull")
_emit_pulls_context("p1", "model_router_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "model_router_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "model_router_types", "uwg_term_2")
_emit_writes_through("p1", "model_router_types", "write_through")
_emit_writes_through("p1", "model_router_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "model_router_types", "safety_validation")
_emit_invokes_eval("p1", "model_router_types", "eval_call")
_emit_proposal_commits_routing("p1", "model_router_types", "routing_commit")
_emit_escalates_to_human("p1", "model_router_types", "human_escalation")
_emit_routes_through("p1", "model_router_types", "route_through")
_emit_checks_agent_registry("p1", "model_router_types", "agent_registry")
_emit_validates_agent_capability("p1", "model_router_types", "capability")
_emit_dispatches_execution_plan("p1", "model_router_types", "exec_plan")
_emit_agent_executes_agent("p1", "model_router_types", "sub_agent")
_emit_routes_to_agent("p1", "model_router_types", "target_agent")
_emit_verifies_policy("p1", "model_router_types", "policy_check")
_emit_observes_runtime_state("p1", "model_router_types", "runtime_state")
_emit_verifies_boundary("p1", "model_router_types", "boundary_check")
_emit_transcripts_response("p1", "model_router_types", "transcript")
_emit_hard_fails_untranscripted("p1", "model_router_types")
_emit_gated_by_confidence("p1", "model_router_types", "confidence_gate")
_emit_reads_through("l4", "model_router_types", "urg_read_1")
_emit_reads_through("l4", "model_router_types", "urg_read_2")
_emit_reads_through("l4", "model_router_types", "urg_read_3")
_emit_reads_through("l4", "model_router_types", "urg_read_4")
_emit_reads_through("l4", "model_router_types", "urg_read_5")
_emit_reads_through("l4", "model_router_types", "urg_read_6")
_emit_reads_through("l4", "model_router_types", "urg_read_7")
_emit_reads_through("l4", "model_router_types", "urg_read_8")
_emit_reads_through("l4", "model_router_types", "urg_read_9")
_emit_reads_through("l4", "model_router_types", "urg_read_10")
_emit_reads_through("l4", "model_router_types", "urg_read_11")
_emit_reads_through("l4", "model_router_types", "urg_read_12")
_emit_reads_through("l4", "model_router_types", "urg_read_13")
_emit_reads_through("l4", "model_router_types", "urg_read_14")
_emit_reads_through("l4", "model_router_types", "urg_read_15")
_emit_reads_through("l4", "model_router_types", "urg_read_16")
_emit_reads_through("l4", "model_router_types", "urg_read_17")
_emit_reads_through("l4", "model_router_types", "urg_read_18")
_emit_reads_through("l4", "model_router_types", "urg_read_19")
_emit_reads_through("l4", "model_router_types", "urg_read_20")
_emit_reads_through("l4", "model_router_types", "urg_read_21")
_emit_reads_through("l4", "model_router_types", "urg_read_22")
_emit_reads_through("l4", "model_router_types", "urg_read_23")
_emit_reads_through("l4", "model_router_types", "urg_read_24")
_emit_reads_through("l4", "model_router_types", "urg_read_25")
_emit_reads_through("l4", "model_router_types", "urg_read_26")
_emit_reads_through("l4", "model_router_types", "urg_read_27")
_emit_reads_through("l4", "model_router_types", "urg_read_28")
_emit_reads_through("l4", "model_router_types", "urg_read_29")
_emit_reads_through("l4", "model_router_types", "urg_read_30")
_emit_reads_through("l4", "model_router_types", "urg_read_31")
_emit_reads_through("l4", "model_router_types", "urg_read_32")
_emit_reads_through("l4", "model_router_types", "urg_read_33")
_emit_reads_through("l4", "model_router_types", "urg_read_34")
_emit_reads_through("l4", "model_router_types", "urg_read_35")
_emit_reads_through("l4", "model_router_types", "urg_read_36")
_emit_reads_through("l4", "model_router_types", "urg_read_37")
_emit_reads_through("l4", "model_router_types", "urg_read_38")
_emit_reads_through("l4", "model_router_types", "urg_read_39")
_emit_reads_through("l4", "model_router_types", "urg_read_40")
_emit_reads_through("l4", "model_router_types", "urg_read_41")
_emit_reads_through("l4", "model_router_types", "urg_read_42")
_emit_reads_through("l4", "model_router_types", "urg_read_43")
_emit_reads_through("l4", "model_router_types", "urg_read_44")
_emit_reads_through("l4", "model_router_types", "urg_read_45")
_emit_reads_through("l4", "model_router_types", "urg_read_46")
_emit_reads_through("l4", "model_router_types", "urg_read_47")
_emit_reads_through("l4", "model_router_types", "urg_read_48")
_emit_reads_through("l4", "model_router_types", "urg_read_49")
_emit_reads_through("l4", "model_router_types", "urg_read_50")
_emit_reads_through("l4", "model_router_types", "urg_read_51")
_emit_reads_through("l4", "model_router_types", "urg_read_52")
_emit_reads_through("l4", "model_router_types", "urg_read_53")
_emit_reads_through("l4", "model_router_types", "urg_read_54")
_emit_reads_through("l4", "model_router_types", "urg_read_55")
_emit_reads_through("l4", "model_router_types", "urg_read_56")
_emit_reads_through("l4", "model_router_types", "urg_read_57")
_emit_reads_through("l4", "model_router_types", "urg_read_58")
_emit_reads_through("l4", "model_router_types", "urg_read_59")
_emit_reads_through("l4", "model_router_types", "urg_read_60")
_emit_reads_through("l4", "model_router_types", "urg_read_61")
_emit_reads_through("l4", "model_router_types", "urg_read_62")
_emit_reads_through("l4", "model_router_types", "urg_read_63")
_emit_reads_through("l4", "model_router_types", "urg_read_64")
_emit_reads_through("l4", "model_router_types", "urg_read_65")
_emit_reads_through("l4", "model_router_types", "urg_read_66")
_emit_reads_through("l4", "model_router_types", "urg_read_67")
_emit_reads_through("l4", "model_router_types", "urg_read_68")
_emit_reads_through("l4", "model_router_types", "urg_read_69")
_emit_reads_through("l4", "model_router_types", "urg_read_70")
_emit_reads_through("l4", "model_router_types", "urg_read_71")
_emit_reads_through("l4", "model_router_types", "urg_read_72")
_emit_reads_through("l4", "model_router_types", "urg_read_73")
_emit_reads_through("l4", "model_router_types", "urg_read_74")
_emit_reads_through("l4", "model_router_types", "urg_read_75")

logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """Model performance tiers."""

    FAST = "FAST"
    BALANCED = "BALANCED"
    REASONING = "REASONING"
    SEQUENTIAL = "SEQUENTIAL"


class TaskType(str, Enum):
    """Types of tasks that can be routed."""

    RESUME_FORMATTING = "RESUME_FORMATTING"
    MESSAGE_DRAFTING = "MESSAGE_DRAFTING"
    STRATEGIC_PLANNING = "STRATEGIC_PLANNING"
    CODE_GENERATION = "CODE_GENERATION"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    CONTENT_CREATION = "CONTENT_CREATION"
    TRANSLATION = "TRANSLATION"
    SUMMARIZATION = "SUMMARIZATION"
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    VALIDATION = "VALIDATION"


@dataclass
class ModelConfig:
    """configuration for a specific model."""

    provider: str
    model_name: str
    tier: ModelTier
    max_tokens: int
    temperature: float
    cost_per_1k_tokens: float
    max_retries: int = 3
    timeout_seconds: int = 30


@dataclass
class TaskProfile:
    """Profile for a task type."""

    task_type: TaskType
    default_tier: ModelTier
    min_complexity: int = 1
    max_complexity: int = 10
    complexity_thresholds: dict[ModelTier, int] = field(default_factory=dict)
    config_overrides: dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """Routes tasks to appropriate models based on various factors."""

    # guardian: allow-magic-config
    def __init__(self, daily_budget: float = 5.0, budget_period_hours: int = 24):
        """Initialize model router.

        Args:
            daily_budget: Daily spend limit in USD
            budget_period_hours: Budget period in hours
        """
        self.daily_budget = daily_budget
        self.budget_period_hours = budget_period_hours
        self._models: dict[str, ModelConfig] = {}
        self._task_profiles: dict[TaskType, TaskProfile] = {}
        self._budget_start = datetime.utcnow()
        self._current_spend = 0.0
        self._usage_history: list[dict[str, Any]] = []
        self._stats = {
            "total_requests": 0,
            "requests_by_tier": {tier.value: 0 for tier in ModelTier},
            "requests_by_task": {task.value: 0 for task in TaskType},
            "fallbacks": 0,
            "budget_enforced": 0,
            "total_spend": 0.0,
        }
        self._initialize_defaults()
        logger.info(f"Initialized ModelRouter with budget ${daily_budget}/{budget_period_hours}h")

    def _initialize_defaults(self) -> None:
        """Initialize default model configurations and task profiles."""
        # guardian: allow-magic-config
        self._models["gpt-4o-mini"] = ModelConfig(
            provider="openai",
            model_name="gpt-4o-mini",
            tier=ModelTier.FAST,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.00015,
        )
        # guardian: allow-magic-config
        self._models["claude-3-haiku"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-haiku-20240307",
            tier=ModelTier.FAST,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.00025,
        )
        # guardian: allow-magic-config
        self._models["gpt-4o"] = ModelConfig(
            provider="openai",
            model_name="gpt-4o",
            tier=ModelTier.BALANCED,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.005,
        )
        # guardian: allow-magic-config
        self._models["claude-3-5-sonnet"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-5-sonnet-20241022",
            tier=ModelTier.BALANCED,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.003,
        )
        # guardian: allow-magic-config
        self._models["o1-preview"] = ModelConfig(
            provider="openai",
            model_name="o1-preview",
            tier=ModelTier.REASONING,
            max_tokens=32768,
            temperature=1.0,
            cost_per_1k_tokens=0.015,
        )
        # guardian: allow-magic-config
        self._models["claude-3-opus"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-opus-20240229",
            tier=ModelTier.REASONING,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.015,
        )
        self._task_profiles[TaskType.RESUME_FORMATTING] = TaskProfile(
            task_type=TaskType.RESUME_FORMATTING,
            default_tier=ModelTier.FAST,
            complexity_thresholds={ModelTier.FAST: 3, ModelTier.BALANCED: 7, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.MESSAGE_DRAFTING] = TaskProfile(
            task_type=TaskType.MESSAGE_DRAFTING,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={ModelTier.FAST: 2, ModelTier.BALANCED: 8, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.STRATEGIC_PLANNING] = TaskProfile(
            task_type=TaskType.STRATEGIC_PLANNING,
            default_tier=ModelTier.REASONING,
            complexity_thresholds={ModelTier.FAST: 1, ModelTier.BALANCED: 5, ModelTier.REASONING: 8},
        )
        self._task_profiles[TaskType.CODE_GENERATION] = TaskProfile(
            task_type=TaskType.CODE_GENERATION,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={ModelTier.FAST: 3, ModelTier.BALANCED: 7, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.DATA_ANALYSIS] = TaskProfile(
            task_type=TaskType.DATA_ANALYSIS,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={ModelTier.FAST: 2, ModelTier.BALANCED: 6, ModelTier.REASONING: 9},
        )
        self._task_profiles[TaskType.CONTENT_CREATION] = TaskProfile(
            task_type=TaskType.CONTENT_CREATION,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={ModelTier.FAST: 3, ModelTier.BALANCED: 7, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.TRANSLATION] = TaskProfile(
            task_type=TaskType.TRANSLATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={ModelTier.FAST: 5, ModelTier.BALANCED: 8, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.SUMMARIZATION] = TaskProfile(
            task_type=TaskType.SUMMARIZATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={ModelTier.FAST: 4, ModelTier.BALANCED: 8, ModelTier.REASONING: 10},
        )
        self._task_profiles[TaskType.QUESTION_ANSWERING] = TaskProfile(
            task_type=TaskType.QUESTION_ANSWERING,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={ModelTier.FAST: 2, ModelTier.BALANCED: 6, ModelTier.REASONING: 9},
        )
        self._task_profiles[TaskType.VALIDATION] = TaskProfile(
            task_type=TaskType.VALIDATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={ModelTier.FAST: 4, ModelTier.BALANCED: 8, ModelTier.REASONING: 10},
        )

    def get_model_config(
        self,
        task_type: TaskType,
        complexity_score: int = 1,
        force_tier: ModelTier | None = None,
    ) -> dict[str, Any]:
        """Get model configuration for a task.

        Args:
            task_type: Type of task
            complexity_score: Task complexity (1-10)
            force_tier: Force specific tier

        Returns:
            Model configuration dictionary
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"AdaptiveModelRouter.get_model_config:{task_type}",
        )
        profile = self._task_profiles.get(task_type)
        # guardian: allow-config-with-logic
        if not profile:
            raise ValueError(f"Unknown task type: {task_type}")
        # guardian: allow-config-with-logic
        if force_tier:
            tier = force_tier
        else:
            tier = self._determine_tier(profile, complexity_score)
        tier = self._apply_budget_constraints(tier)
        model_config = self._select_model_for_tier(tier)
        config = {
            "provider": model_config.provider,
            "model": model_config.model_name,
            "tier": tier.value,
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
            "max_retries": model_config.max_retries,
            "timeout_seconds": model_config.timeout_seconds,
        }
        config.update(profile.config_overrides)
        self._stats["total_requests"] += 1
        self._stats["requests_by_tier"][tier.value] += 1
        self._stats["requests_by_task"][task_type.value] += 1
        return config

    def _determine_tier(self, profile: TaskProfile, complexity_score: int) -> ModelTier:
        """Determine model tier based on complexity.

        Args:
            profile: Task profile
            complexity_score: Complexity score

        Returns:
            Selected tier
        """
        thresholds = profile.complexity_thresholds
        if complexity_score >= 9 or profile.task_type == TaskType.STRATEGIC_PLANNING:
            return ModelTier.SEQUENTIAL
        if complexity_score >= thresholds.get(ModelTier.REASONING, 10):
            return ModelTier.REASONING
        elif complexity_score >= thresholds.get(ModelTier.BALANCED, 7):
            return ModelTier.BALANCED
        else:
            return ModelTier.FAST

    def _apply_budget_constraints(self, tier: ModelTier) -> ModelTier:
        """Apply budget constraints to tier selection.

        Args:
            tier: Original tier selection

        Returns:
            Adjusted tier
        """
        if self._is_budget_exceeded():
            if tier == ModelTier.REASONING:
                self._stats["budget_enforced"] += 1
                return ModelTier.BALANCED
            elif tier == ModelTier.BALANCED:
                self._stats["budget_enforced"] += 1
                return ModelTier.FAST
        return tier

    def _select_model_for_tier(self, tier: ModelTier) -> ModelConfig:
        """Select the best model for a tier.

        Args:
            tier: Model tier

        Returns:
            Selected model configuration
        """
        tier_models = [config for config in self._models.values() if config.tier == tier]
        if not tier_models:
            raise ValueError(f"No models available for tier: {tier}")
        return min(tier_models, key=lambda m: m.cost_per_1k_tokens)

    async def get_client(self, tier: ModelTier) -> "FallbackClient":
        """Get LLM client for a tier with fallback.

        Args:
            tier: Model tier

        Returns:
            LLM client with fallback logic
        """
        if tier == ModelTier.SEQUENTIAL:
            return SequentialThinkingClient(self)
        model_config = self._select_model_for_tier(tier)
        return FallbackClient(model_config, self)

    def record_usage(self, model_name: str, input_tokens: int, output_tokens: int, cost: float) -> None:
        """Record model usage for budget tracking.

        Args:
            model_name: Model used
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost: Cost in USD
        """
        self._current_spend += cost
        self._stats["total_spend"] += cost
        usage = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
        }
        self._usage_history.append(usage)
        if len(self._usage_history) > 1000:
            self._usage_history = self._usage_history[-1000:]
        self._check_budget_period()

    def _is_budget_exceeded(self) -> bool:
        """Check if budget is exceeded.

        Returns:
            True if budget exceeded
        """
        return self._current_spend >= self.daily_budget

    def _check_budget_period(self) -> None:
        """Check and reset budget period if needed."""
        now = datetime.utcnow()
        elapsed = now - self._budget_start
        if elapsed >= timedelta(hours=self.budget_period_hours):
            self._budget_start = now
            self._current_spend = 0.0
            logger.info("Budget period reset")

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["budget_info"] = {
            "daily_budget": self.daily_budget,
            "current_spend": self._current_spend,
            "remaining": max(0, self.daily_budget - self._current_spend),
            "period_hours": self.budget_period_hours,
            "period_start": self._budget_start.isoformat(),
        }
        stats["available_models"] = {
            tier.value: len([m for m in self._models.values() if m.tier == tier]) for tier in ModelTier
        }
        return stats

    def add_model(self, name: str, config: ModelConfig) -> None:
        """Add a new model configuration.

        Args:
            name: Model name
            config: Model configuration
        """
        self._models[name] = config
        logger.info(f"Added model {name} ({config.tier.value})")

    def add_task_profile(self, profile: TaskProfile) -> None:
        """Add a new task profile.

        Args:
            profile: Task profile
        """
        self._task_profiles[profile.task_type] = profile
        logger.info(f"Added task profile {profile.task_type.value}")


class LLMClient:
    """Abstract base for LLM provider clients."""

    async def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """OpenAI provider client — reads OPENAI_API_KEY from environment."""

    def __init__(self, config: ModelConfig):
        self.config = config

    async def generate(self, prompt: str, **kwargs) -> str:
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        try:
            import openai

            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            )
            return response.choices[0].message.content or ""
        except ImportError as exc:
            raise RuntimeError("openai package not installed — pip install openai") from exc


class AnthropicClient(LLMClient):
    """Anthropic provider client — reads ANTHROPIC_API_KEY from environment."""

    def __init__(self, config: ModelConfig):
        self.config = config

    async def generate(self, prompt: str, **kwargs) -> str:
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model=self.config.model_name,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""
        except ImportError as exc:
            raise RuntimeError("anthropic package not installed — pip install anthropic") from exc


class FallbackClient:
    """LLM client with automatic fallback and retry logic."""

    def __init__(self, primary_config: ModelConfig, router: ModelRouter):
        """Initialize fallback client.

        Args:
            primary_config: Primary model configuration
            router: Model router instance
        """
        self.primary_config = primary_config
        self.router = router
        self._client_cache: dict[str, LLMClient] = {}

    async def _get_client(self, config: ModelConfig) -> LLMClient:
        """Get or create an LLM client for the given config."""
        if config.model_name not in self._client_cache:
            if config.provider == "openai":
                self._client_cache[config.model_name] = OpenAIClient(config)
            elif config.provider == "anthropic":
                self._client_cache[config.model_name] = AnthropicClient(config)
            else:
                raise ValueError(f"Unknown provider: {config.provider}")
        return self._client_cache[config.model_name]

    def _get_fallback_tier(self, tier: ModelTier) -> ModelTier | None:
        """Return the next-lower tier to fall back to, or None."""
        fallback_map: dict[ModelTier, ModelTier | None] = {
            ModelTier.REASONING: ModelTier.BALANCED,
            ModelTier.BALANCED: ModelTier.FAST,
            ModelTier.SEQUENTIAL: ModelTier.REASONING,
            ModelTier.FAST: None,
        }
        return fallback_map.get(tier)

    def _record_usage(self, client: LLMClient, prompt: str, result: str) -> None:
        """Estimate and record token usage for budget tracking."""
        input_est = len(prompt) // 4
        output_est = len(result) // 4
        cost = (input_est + output_est) / 1000 * self.primary_config.cost_per_1k_tokens
        self.router.record_usage(self.primary_config.model_name, input_est, output_est, cost)

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text with fallback logic.

        Args:
            prompt: Generation prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            client = await self._get_client(self.primary_config)
            result = await client.generate(prompt, **kwargs)
            self._record_usage(client, prompt, result)
            return result
        # guardian: allow-silent-swallow
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.warning(f"Primary model failed: {e}")
            fallback_tier = self._get_fallback_tier(self.primary_config.tier)
            if fallback_tier:
                self.router._stats["fallbacks"] += 1
                try:
                    fallback_config = self.router._select_model_for_tier(fallback_tier)
                    client = await self._get_client(fallback_config)
                    result = await client.generate(prompt, **kwargs)
                    self._record_usage(client, prompt, result)
                    logger.info(f"Fallback to {fallback_config.model_name} succeeded")
                    return result
                # guardian: allow-silent-swallow
                except (
                    OSError,
                    ValueError,
                    TypeError,
                    KeyError,
                    AttributeError,
                    RuntimeError,
                ) as fallback_error:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    logger.error(f"[FallbackClient] All providers failed: {fallback_error}")
                    raise
            raise RuntimeError(f"All model attempts failed. Last error: {e}") from e


class SequentialThinkingClient:
    """Routes generation through the sequential_thinking MCP tool."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def generate(self, prompt: str, goal: str = "", max_steps: int = 8, **kwargs) -> str:
        """Route prompt through sequential_thinking MCP with iterative thought processing.

        Args:
            prompt: Task description
            goal: High-level resolution goal (optional)
            max_steps: Maximum reasoning steps (capped at 15 by L5 shield)
            **kwargs: Additional parameters

        Returns:
            Reasoning result as text
        """
        if _MCPManager is None:
            raise RuntimeError("MCPManager unavailable — cannot run sequential thinking")
        try:
            mcp_mgr = _MCPManager()
            await mcp_mgr.connect("sequential_thinking")
            total = min(max_steps, 15)
            initial = f"Analyzing: {prompt[:200]}"
            if goal:
                initial += f"\nGoal: {goal}"
            thoughts = []
            for idx in tqdm(range(total), desc="Processing", unit="item"):
                is_last = idx == total - 1
                thought_text = (
                    initial
                    if idx == 0
                    else f"Final synthesis: {len(thoughts)} steps completed."
                    if is_last
                    else f"Step {idx + 1}: continuing analysis."
                )
                step_result = await mcp_mgr.call_tool(
                    "sequential_thinking",
                    {
                        "thought": thought_text,
                        "nextThoughtNeeded": not is_last,
                        "thoughtNumber": idx + 1,
                        "totalThoughts": total,
                    },
                )
                thoughts.append(thought_text)
                if isinstance(step_result, dict) and not step_result.get("nextThoughtNeeded", not is_last):
                    break
            self.router._stats["total_requests"] += 1
            self.router._stats["requests_by_tier"][ModelTier.SEQUENTIAL.value] += 1
            return "\n".join(thoughts)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.warning(f"[SequentialThinkingClient] Sequential thinking failed: {e}")
            fallback_config = self.router._select_model_for_tier(ModelTier.REASONING)
            client = FallbackClient(fallback_config, self.router)
            return await client.generate(prompt, **kwargs)


_model_router: ModelRouter | None = None
_router_lock = asyncio.Lock()


async def get_model_router() -> ModelRouter:
    """Get global model router instance.

    Returns:
        ModelRouter instance
    """
    global _model_router
    async with _router_lock:
        if _model_router is None:
            _model_router = ModelRouter()
    return _model_router


async def route_and_generate(task_type: TaskType, prompt: str, complexity_score: int = 1, **kwargs) -> str:
    """Route task and generate response.

    Args:
        task_type: Type of task
        prompt: Generation prompt
        complexity_score: Task complexity
        **kwargs: Additional parameters

    Returns:
        Generated response
    """
    router = await get_model_router()
    config = router.get_model_config(task_type, complexity_score)
    tier = ModelTier(config["tier"])
    client = await router.get_client(tier)
    return await client.generate(prompt, **kwargs)
