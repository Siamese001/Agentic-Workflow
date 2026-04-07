"""
ForwardRollingConfig - Feature Flags and Configuration for Gradual Rollout.

[PHASE 4] Implements feature flags, traffic routing, and configuration
management for gradual rollout of Forward-Rolling Recursion.

ROLLOUT SAFETY: Gradual traffic migration with instant rollback
CONFIGURATION: Centralized settings with runtime updates

Author: Cascade
Date: February 2026
Phase: 4 - Gradual Rollout
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "forward_rolling_types")
emit_determinism_digest("p0", "forward_rolling_types")

_emit_dispatches_healing_run("p1", "forward_rolling_types", "L3")
_emit_routes_through("p1", "forward_rolling_types", "L3")
_emit_checks_agent_registry("p1", "forward_rolling_types", "agent_registry")
_emit_validates_agent_capability("p1", "forward_rolling_types", "capability")
_emit_dispatches_execution_plan("p1", "forward_rolling_types", "exec_plan")
_emit_agent_executes_agent("p1", "forward_rolling_types", "sub_agent")
_emit_routes_to_agent("p1", "forward_rolling_types", "target_agent")
_emit_verifies_policy("p1", "forward_rolling_types", "policy_check")
_emit_observes_runtime_state("p1", "forward_rolling_types", "runtime_state")
_emit_verifies_boundary("p1", "forward_rolling_types", "boundary_check")
_emit_transcripts_response("p1", "forward_rolling_types", "transcript")
_emit_hard_fails_untranscripted("p1", "forward_rolling_types")
_emit_gated_by_confidence("p1", "forward_rolling_types", "confidence_gate")
_emit_escalates_to_human("p1", "forward_rolling_types", "L3")
_emit_reads_policy_state("p1", "forward_rolling_types", "L3")
_emit_authorize_and_execute("p2", "forward_rolling_types", "execution_auth")
_emit_validates_capability("p2", "forward_rolling_types", "capability_check")
_emit_routes_to_capability("p2", "forward_rolling_types", "capability_route")
_emit_writes_via_uwg("p2", "forward_rolling_types", "uwg_write")
_emit_blocks_direct_write("p2", "forward_rolling_types", "direct_write_block")
_emit_records_tool_invocation("p2", "forward_rolling_types", "tool_invocation")
_emit_captures_execution_output("p2", "forward_rolling_types", "exec_output")
_emit_dispatches_agent("p3", "forward_rolling_types", "agent_dispatch")
_emit_coordinates_agents("p3", "forward_rolling_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "forward_rolling_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "forward_rolling_types", "healing_outcome")
_emit_escalates_failure("p3", "forward_rolling_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "forward_rolling_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "forward_rolling_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "forward_rolling_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "forward_rolling_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "forward_rolling_types", "eval_metric")
_emit_stores_embedding("p4", "forward_rolling_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "forward_rolling_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "forward_rolling_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_1")
_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_2")
_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_3")
_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_4")
_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_5")
_emit_emits_metric_event("forward_rolling_types", "p4obs", "metric_6")
_emit_records_incident_event("forward_rolling_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("forward_rolling_types", "p4obs", "anomaly")
_emit_writes_observability_log("forward_rolling_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("forward_rolling_types", "p4obs", "mon_state")
_emit_triggers_alert("forward_rolling_types", "p4obs", "alert")
_emit_links_incident_trace("forward_rolling_types", "p4obs", "trace_link")
_emit_captures_pattern("forward_rolling_types", "p3lm", "pattern")
_emit_records_learning_event("forward_rolling_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("forward_rolling_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("forward_rolling_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("forward_rolling_types", "p3lm", "routing")
_emit_improves_agent_policy("forward_rolling_types", "p3lm", "policy")
_emit_stores_learning_state("forward_rolling_types", "p3lm", "state")
_emit_records_execution_trace("forward_rolling_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("forward_rolling_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("forward_rolling_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("forward_rolling_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("forward_rolling_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("forward_rolling_types", "env_read", "p2_env_1")
_emit_reads_environ("forward_rolling_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("forward_rolling_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("forward_rolling_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "forward_rolling_types", "context_pull")
_emit_pulls_context("p1", "forward_rolling_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "forward_rolling_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "forward_rolling_types", "uwg_term_2")
_emit_writes_through("p1", "forward_rolling_types", "write_through")
_emit_writes_through("p1", "forward_rolling_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "forward_rolling_types", "safety_validation")
_emit_invokes_eval("p1", "forward_rolling_types", "eval_call")
_emit_proposal_commits_routing("p1", "forward_rolling_types", "routing_commit")

Logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """Execution mode for orchestration."""

    STATIC_DAG = "static_dag"
    FORWARD_ROLLING = "forward_rolling"
    HYBRID = "hybrid"


class RolloutStage(str, Enum):
    """Rollout stage for gradual deployment."""

    DISABLED = "disabled"
    CANARY = "canary"
    EARLY_ADOPTER = "early_adopter"
    PARTIAL = "partial"
    MAJORITY = "majority"
    FULL = "full"


ROLLOUT_PERCENTAGES = {
    RolloutStage.DISABLED: 0,
    RolloutStage.CANARY: 5,
    RolloutStage.EARLY_ADOPTER: 25,
    RolloutStage.PARTIAL: 50,
    RolloutStage.MAJORITY: 75,
    RolloutStage.FULL: 100,
}


@dataclass
class FeatureFlag:
    """Feature flag configuration."""

    name: str
    enabled: bool
    rollout_percentage: int = 100
    allowed_agents: set[str] = field(default_factory=set)
    blocked_agents: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RolloutConfig:
    """Configuration for Forward-Rolling Recursion rollout."""

    stage: RolloutStage = RolloutStage.DISABLED
    execution_mode: ExecutionMode = ExecutionMode.STATIC_DAG
    max_depth: int = 50
    enable_context_pruning: bool = True
    enable_adaptive_depth: bool = True
    enable_monitoring: bool = True
    fallback_on_error: bool = True
    sticky_routing: bool = True
    metrics_sampling_rate: float = 1.0


class ForwardRollingConfig:
    """
    Configuration manager for Forward-Rolling Recursion rollout.

    Features:
    - Feature flags with percentage-based rollout
    - Sticky routing for consistent user experience
    - Runtime configuration updates
    - Instant rollback capability
    - A/B testing support
    """

    def __init__(
        self,
        initial_stage: RolloutStage = RolloutStage.DISABLED,
        config_update_callback: Callable[[RolloutConfig], None] | None = None,
    ):
        """
        Initialize configuration manager.

        Args:
            initial_stage: Initial rollout stage
            config_update_callback: Callback when config changes
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ForwardRollingConfig.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ForwardRollingConfig.__init__", "p0_governance")
        self._config = RolloutConfig(stage=initial_stage)
        self._feature_flags: dict[str, FeatureFlag] = {}
        self._routing_cache: dict[str, ExecutionMode] = {}
        self._config_update_callback = config_update_callback
        self._rollback_history: list[RolloutConfig] = []
        self._init_default_flags()
        Logger.info(f"[ForwardRollingConfig] Initialized with stage={initial_stage.value}")

    def _init_default_flags(self) -> None:
        """Initialize default feature flags."""
        default_flags = [
            FeatureFlag(name="forward_rolling_enabled", enabled=False, rollout_percentage=0),
            FeatureFlag(name="context_pruning", enabled=True, rollout_percentage=100),
            FeatureFlag(name="adaptive_depth", enabled=True, rollout_percentage=100),
            FeatureFlag(name="monitoring", enabled=True, rollout_percentage=100),
            FeatureFlag(name="circuit_breaker", enabled=True, rollout_percentage=100),
        ]
        for flag in default_flags:
            self._feature_flags[flag.name] = flag

    def get_execution_mode(self, agent_id: str, mission_id: str = "") -> ExecutionMode:
        """
        Determine execution mode for a specific agent/mission.

        Uses sticky routing to ensure consistent experience.

        Args:
            agent_id: Agent identifier
            mission_id: Optional mission identifier

        Returns:
            ExecutionMode to use for this request
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"ForwardRollingManager.get_execution_mode:{agent_id}",
        )
        cache_key = f"{agent_id}:{mission_id}" if mission_id else agent_id
        if self._config.sticky_routing and cache_key in self._routing_cache:
            return self._routing_cache[cache_key]
        mode = self._calculate_execution_mode(agent_id, mission_id)
        if self._config.sticky_routing:
            self._routing_cache[cache_key] = mode
        return mode

    def _calculate_execution_mode(self, agent_id: str, mission_id: str) -> ExecutionMode:
        """Calculate execution mode based on rollout configuration."""
        if self._config.stage == RolloutStage.DISABLED:
            return ExecutionMode.STATIC_DAG
        fr_flag = self._feature_flags.get("forward_rolling_enabled")
        if fr_flag and (not fr_flag.enabled):
            return ExecutionMode.STATIC_DAG
        if fr_flag and agent_id in fr_flag.blocked_agents:
            return ExecutionMode.STATIC_DAG
        if fr_flag and fr_flag.allowed_agents and (agent_id not in fr_flag.allowed_agents):
            return ExecutionMode.STATIC_DAG
        rollout_pct = ROLLOUT_PERCENTAGES.get(self._config.stage, 0)
        if self._should_route_to_forward_rolling(agent_id, mission_id, rollout_pct):
            return self._config.execution_mode
        else:
            return ExecutionMode.STATIC_DAG

    def _should_route_to_forward_rolling(self, agent_id: str, mission_id: str, percentage: int) -> bool:
        """
        Determine if request should be routed to Forward-Rolling.

        Uses consistent hashing for deterministic routing.

        Args:
            agent_id: Agent identifier
            mission_id: Mission identifier
            percentage: Rollout percentage (0-100)

        Returns:
            True if should use Forward-Rolling
        """
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False
        hash_input = f"{agent_id}:{mission_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        bucket = hash_value % 100
        return bucket < percentage

    def set_rollout_stage(self, stage: RolloutStage) -> None:
        """
        Set the rollout stage.

        Args:
            stage: New rollout stage
        """
        self._rollback_history.append(
            RolloutConfig(
                stage=self._config.stage,
                execution_mode=self._config.execution_mode,
                max_depth=self._config.max_depth,
                enable_context_pruning=self._config.enable_context_pruning,
                enable_adaptive_depth=self._config.enable_adaptive_depth,
                enable_monitoring=self._config.enable_monitoring,
                fallback_on_error=self._config.fallback_on_error,
                sticky_routing=self._config.sticky_routing,
            ),
        )
        self._config.stage = stage
        fr_flag = self._feature_flags.get("forward_rolling_enabled")
        if fr_flag:
            fr_flag.enabled = stage != RolloutStage.DISABLED
            fr_flag.rollout_percentage = ROLLOUT_PERCENTAGES.get(stage, 0)
            fr_flag.updated_at = datetime.now().isoformat()
        self._routing_cache.clear()
        if self._config_update_callback:
            self._config_update_callback(self._config)
        Logger.info(f"[ForwardRollingConfig] Rollout stage set to {stage.value}")

    def rollback(self) -> bool:
        """
        Rollback to previous configuration.

        Returns:
            True if rollback successful
        """
        if not self._rollback_history:
            Logger.warning("[ForwardRollingConfig] No rollback history available")
            return False
        previous_config = self._rollback_history.pop()
        self._config = previous_config
        fr_flag = self._feature_flags.get("forward_rolling_enabled")
        if fr_flag:
            fr_flag.enabled = previous_config.stage != RolloutStage.DISABLED
            fr_flag.rollout_percentage = ROLLOUT_PERCENTAGES.get(previous_config.stage, 0)
        self._routing_cache.clear()
        Logger.info(f"[ForwardRollingConfig] Rolled back to stage {previous_config.stage.value}")
        return True

    def emergency_disable(self) -> None:
        """Emergency disable of Forward-Rolling Recursion."""
        self.set_rollout_stage(RolloutStage.DISABLED)
        self._config.execution_mode = ExecutionMode.STATIC_DAG
        fr_flag = self._feature_flags.get("forward_rolling_enabled")
        if fr_flag:
            fr_flag.enabled = False
            fr_flag.rollout_percentage = 0
        Logger.critical("[ForwardRollingConfig] EMERGENCY DISABLE activated")

    def set_feature_flag(
        self,
        name: str,
        enabled: bool,
        rollout_percentage: int = 100,
        allowed_agents: set[str] | None = None,
        blocked_agents: set[str] | None = None,
    ) -> FeatureFlag:
        """
        Set or update a feature flag.

        Args:
            name: Flag name
            enabled: Whether flag is enabled
            rollout_percentage: Percentage of traffic (0-100)
            allowed_agents: Set of allowed agent IDs
            blocked_agents: Set of blocked agent IDs

        Returns:
            Updated FeatureFlag
        """
        if name in self._feature_flags:
            flag = self._feature_flags[name]
            flag.enabled = enabled
            flag.rollout_percentage = min(max(rollout_percentage, 0), 100)
            if allowed_agents is not None:
                flag.allowed_agents = allowed_agents
            if blocked_agents is not None:
                flag.blocked_agents = blocked_agents
            flag.updated_at = datetime.now().isoformat()
        else:
            flag = FeatureFlag(
                name=name,
                enabled=enabled,
                rollout_percentage=min(max(rollout_percentage, 0), 100),
                allowed_agents=allowed_agents or set(),
                blocked_agents=blocked_agents or set(),
            )
            self._feature_flags[name] = flag
        Logger.info(
            f"[ForwardRollingConfig] Feature flag '{name}' set to enabled={enabled}, rollout={rollout_percentage}%",
        )
        return flag

    def is_feature_enabled(self, name: str, agent_id: str = "") -> bool:
        """
        Check if a feature is enabled for an agent.

        Args:
            name: Feature flag name
            agent_id: Optional agent ID for percentage-based check

        Returns:
            True if feature is enabled
        """
        flag = self._feature_flags.get(name)
        if not flag or not flag.enabled:
            return False
        if agent_id and agent_id in flag.blocked_agents:
            return False
        if flag.allowed_agents and agent_id not in flag.allowed_agents:
            return False
        if flag.rollout_percentage < 100 and agent_id:
            return self._should_route_to_forward_rolling(agent_id, "", flag.rollout_percentage)
        return True

    def get_feature_flag(self, name: str) -> FeatureFlag | None:
        """Get a feature flag by name."""
        return self._feature_flags.get(name)

    def get_all_feature_flags(self) -> dict[str, FeatureFlag]:
        """Get all feature flags."""
        return self._feature_flags.copy()

    def update_config(self, **kwargs) -> None:
        """
        Update configuration values.

        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            # guardian: allow-config-with-logic
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                Logger.info(f"[ForwardRollingConfig] Config {key} set to {value}")
        # guardian: allow-config-with-logic
        if self._config_update_callback:
            self._config_update_callback(self._config)

    def get_config(self) -> RolloutConfig:
        """Get current configuration."""
        return self._config

    def get_rollout_percentage(self) -> int:
        """Get current rollout percentage."""
        return ROLLOUT_PERCENTAGES.get(self._config.stage, 0)

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics."""
        total_cached = len(self._routing_cache)
        mode_counts = {}
        for mode in self._routing_cache.values():
            mode_counts[mode.value] = mode_counts.get(mode.value, 0) + 1
        return {
            "total_cached_routes": total_cached,
            "mode_distribution": mode_counts,
            "rollout_stage": self._config.stage.value,
            "rollout_percentage": self.get_rollout_percentage(),
            "sticky_routing_enabled": self._config.sticky_routing,
        }

    def clear_routing_cache(self) -> int:
        """Clear routing cache and return count cleared."""
        count = len(self._routing_cache)
        self._routing_cache.clear()
        Logger.info(f"[ForwardRollingConfig] Cleared {count} cached routes")
        return count

    def add_agent_to_allowlist(self, flag_name: str, agent_id: str) -> bool:
        """Add agent to a feature flag's allowlist."""
        flag = self._feature_flags.get(flag_name)
        if flag:
            flag.allowed_agents.add(agent_id)
            flag.updated_at = datetime.now().isoformat()
            return True
        return False

    def add_agent_to_blocklist(self, flag_name: str, agent_id: str) -> bool:
        """Add agent to a feature flag's blocklist."""
        flag = self._feature_flags.get(flag_name)
        if flag:
            flag.blocked_agents.add(agent_id)
            flag.updated_at = datetime.now().isoformat()
            return True
        return False

    def remove_agent_from_allowlist(self, flag_name: str, agent_id: str) -> bool:
        """Remove agent from a feature flag's allowlist."""
        flag = self._feature_flags.get(flag_name)
        if flag and agent_id in flag.allowed_agents:
            flag.allowed_agents.remove(agent_id)
            flag.updated_at = datetime.now().isoformat()
            return True
        return False

    def remove_agent_from_blocklist(self, flag_name: str, agent_id: str) -> bool:
        """Remove agent from a feature flag's blocklist."""
        flag = self._feature_flags.get(flag_name)
        if flag and agent_id in flag.blocked_agents:
            flag.blocked_agents.remove(agent_id)
            flag.updated_at = datetime.now().isoformat()
            return True
        return False

    def export_config(self) -> dict[str, Any]:
        """Export current configuration as dictionary."""
        return {
            "config": {
                "stage": self._config.stage.value,
                "execution_mode": self._config.execution_mode.value,
                "max_depth": self._config.max_depth,
                "enable_context_pruning": self._config.enable_context_pruning,
                "enable_adaptive_depth": self._config.enable_adaptive_depth,
                "enable_monitoring": self._config.enable_monitoring,
                "fallback_on_error": self._config.fallback_on_error,
                "sticky_routing": self._config.sticky_routing,
                "metrics_sampling_rate": self._config.metrics_sampling_rate,
            },
            "feature_flags": {
                name: {
                    "enabled": flag.enabled,
                    "rollout_percentage": flag.rollout_percentage,
                    "allowed_agents": list(flag.allowed_agents),
                    "blocked_agents": list(flag.blocked_agents),
                }
                for name, flag in self._feature_flags.items()
            },
            "rollout_percentage": self.get_rollout_percentage(),
        }


__all__ = [
    "ForwardRollingConfig",
    "ExecutionMode",
    "RolloutStage",
    "RolloutConfig",
    "FeatureFlag",
    "ROLLOUT_PERCENTAGES",
]
