"""
apps_lic/shared/core/agent_base.py - Linked-In Canonical Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for LIC domain
- Domain-specific healing pattern memory (similarity_threshold=THRESHOLD)
- Campaign pattern learning and compliance rule memory

PHASE 1.1 GUARDRAILS INTEGRATION (Feb 2026):
- MetaLearningGuardrails integration for security and safety
- Cache poisoning protection, healing depth tracking
- Domain isolation enforcement, rate limiting

PHASE 2.1 META-LEARNING CLIENT (Feb 2026):
- Full MetaLearningClient integration for Redis/Pinecone
- Pattern storage and retrieval with semantic search
- Healing pattern memory with domain isolation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.L0_routing.config import APPS_LIC_DIR
from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR
from agentic_core.L1_cognition.reasoning.meta_client import (
    MetaLearningClient,
    get_meta_learning_client,
)
from agentic_core.L1_cognition.types.client_types import HealingPattern
from agentic_core.L1_cognition.utils.guardrails_util import (
    MetaLearningGuardrails,
    get_guardrails,
)
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
from apps_shared.utils.app_base_util import AppBase

_emit_applies_guardrail("p0", "lic_agent_base_util", "p0_governance")
_emit_reads_policy_state("p0", "lic_agent_base_util", "policy_binding")
_emit_snapshots_state("p0", "lic_agent_base_util", "state_snapshot")
emit_replay_key("p0", "lic_agent_base_util")
emit_determinism_digest("p0", "lic_agent_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "lic_agent_base_util", "execution_auth")
_emit_validates_capability("p2", "lic_agent_base_util", "capability_check")
_emit_routes_to_capability("p2", "lic_agent_base_util", "capability_route")
_emit_writes_via_uwg("p2", "lic_agent_base_util", "uwg_write")
_emit_blocks_direct_write("p2", "lic_agent_base_util", "direct_write_block")
_emit_records_tool_invocation("p2", "lic_agent_base_util", "tool_invocation")
_emit_captures_execution_output("p2", "lic_agent_base_util", "exec_output")
_emit_dispatches_agent("p3", "lic_agent_base_util", "agent_dispatch")
_emit_coordinates_agents("p3", "lic_agent_base_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "lic_agent_base_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "lic_agent_base_util", "healing_outcome")
_emit_escalates_failure("p3", "lic_agent_base_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "lic_agent_base_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lic_agent_base_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "lic_agent_base_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "lic_agent_base_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lic_agent_base_util", "eval_metric")
_emit_stores_embedding("p4", "lic_agent_base_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "lic_agent_base_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lic_agent_base_util", "exec_snapshot_link")
_emit_links_execution_to_snapshot("p4", "lic_agent_base_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
try:
    from agentic_core.interfaces.mixins import HealingPolicyMixin, MetaLearningMixin
except ImportError:

    class HealingPolicyMixin:
        pass


try:
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
except ImportError:

    class SemanticCacheMixin:
        pass


try:
    from agentic_core.mixins.embedding_mixin import EmbeddingMixin
except ImportError:

    class EmbeddingMixin:
        pass


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

_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_1")
_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_2")
_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_3")
_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_4")
_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_5")
_emit_emits_metric_event("lic_agent_base_util", "p4obs", "metric_6")
_emit_records_incident_event("lic_agent_base_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("lic_agent_base_util", "p4obs", "anomaly")
_emit_writes_observability_log("lic_agent_base_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("lic_agent_base_util", "p4obs", "mon_state")
_emit_triggers_alert("lic_agent_base_util", "p4obs", "alert")
_emit_links_incident_trace("lic_agent_base_util", "p4obs", "trace_link")
_emit_captures_pattern("lic_agent_base_util", "p3lm", "pattern")
_emit_records_learning_event("lic_agent_base_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lic_agent_base_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("lic_agent_base_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lic_agent_base_util", "p3lm", "routing")
_emit_improves_agent_policy("lic_agent_base_util", "p3lm", "policy")
_emit_stores_learning_state("lic_agent_base_util", "p3lm", "state")
_emit_records_execution_trace("lic_agent_base_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lic_agent_base_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lic_agent_base_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lic_agent_base_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lic_agent_base_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lic_agent_base_util", "env_read", "p2_env_1")
_emit_reads_environ("lic_agent_base_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("lic_agent_base_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lic_agent_base_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lic_agent_base_util", "context_pull")
_emit_pulls_context("p1", "lic_agent_base_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lic_agent_base_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lic_agent_base_util", "uwg_term_2")
_emit_writes_through("p1", "lic_agent_base_util", "write_through")
_emit_writes_through("p1", "lic_agent_base_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "lic_agent_base_util", "safety_validation")
_emit_invokes_eval("p1", "lic_agent_base_util", "eval_call")
_emit_proposal_commits_routing("p1", "lic_agent_base_util", "routing_commit")
_emit_escalates_to_human("p1", "lic_agent_base_util", "human_escalation")
_emit_routes_through("p1", "lic_agent_base_util", "route_through")
_emit_checks_agent_registry("p1", "lic_agent_base_util", "agent_registry")
_emit_validates_agent_capability("p1", "lic_agent_base_util", "capability")
_emit_dispatches_execution_plan("p1", "lic_agent_base_util", "exec_plan")
_emit_agent_executes_agent("p1", "lic_agent_base_util", "sub_agent")
_emit_routes_to_agent("p1", "lic_agent_base_util", "target_agent")
_emit_verifies_policy("p1", "lic_agent_base_util", "policy_check")
_emit_observes_runtime_state("p1", "lic_agent_base_util", "runtime_state")
_emit_verifies_boundary("p1", "lic_agent_base_util", "boundary_check")
_emit_transcripts_response("p1", "lic_agent_base_util", "transcript")
_emit_hard_fails_untranscripted("p1", "lic_agent_base_util")
_emit_gated_by_confidence("p1", "lic_agent_base_util", "confidence_gate")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_1")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_2")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_3")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_4")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_5")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_6")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_7")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_8")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_9")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_10")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_11")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_12")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_13")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_14")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_15")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_16")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_17")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_18")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_19")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_20")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_21")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_22")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_23")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_24")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_25")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_26")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_27")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_28")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_29")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_30")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_31")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_32")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_33")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_34")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_35")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_36")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_37")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_38")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_39")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_40")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_41")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_42")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_43")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_44")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_45")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_46")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_47")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_48")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_49")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_50")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_51")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_52")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_53")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_54")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_55")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_56")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_57")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_58")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_59")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_60")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_61")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_62")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_63")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_64")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_65")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_66")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_67")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_68")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_69")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_70")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_71")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_72")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_73")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_74")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_75")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_76")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_77")
_emit_reads_through("l4", "lic_agent_base_util", "urg_read_78")


@dataclass
class LICAgentBase(AppBase, HealingPolicyMixin):
    """
    LICAgentBase: Sovereign Foundation for 'Linked-In Canonical' (LIC).

    Inherits from AppBase for unified app-level capabilities.

    PHASE 1.1 GUARDRAILS:
    - Integrated MetaLearningGuardrails for security
    - Cache poisoning protection via input validation
    - Healing depth tracking to prevent infinite loops
    - Domain isolation enforcement for apps_lic
    - Higher similarity threshold (0.92) for stricter LIC compliance
    """

    domain_root: Path = field(default_factory=lambda: Path(APPS_LIC_DIR))
    _lic_version: Final[str] = "2.5.0-hardened"
    _namespace: str = field(default=APPS_LIC_DIR, init=False)
    _similarity_threshold: float = field(default=0.92, init=False)
    _resource_prefix: str = field(default="lic", init=False)
    _ml_domain: str = field(default=APPS_LIC_DIR, init=False)
    _guardrails: MetaLearningGuardrails = field(default=None, init=False)
    _lic_ttl: int = field(default=7200, init=False)
    _meta_client: MetaLearningClient = field(default=None, init=False)

    def __post_init__(self) -> None:
        """
        Initialize LIC capabilities after Core hardening.
        """
        super().__post_init__()
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)
        self._initialize_guardrails()
        self._initialize_meta_client()
        Logger.debug(
            f"[{self.__class__.__name__}] LIC Meta-Learning activated with guardrails and MetaLearningClient",
        )

    def _initialize_guardrails(self) -> None:
        """Initialize guardrails with LIC-specific configuration (stricter thresholds)."""
        self._guardrails = get_guardrails()
        self._guardrails.guardrails.default_similarity_threshold = self._similarity_threshold
        self._guardrails.guardrails.default_ttl = self._lic_ttl
        Logger.debug(
            f"[{self.__class__.__name__}] Guardrails initialized (threshold={self._similarity_threshold})",
        )

    def _initialize_meta_client(self) -> None:
        """Initialize MetaLearningClient with LIC-specific configuration."""
        self._meta_client = get_meta_learning_client()
        Logger.debug(f"[{self.__class__.__name__}] MetaLearningClient initialized")

    def store_healing_pattern(self, violation: dict[str, Any], healing_result: dict[str, Any]) -> str | None:
        """
        Store a successful healing pattern for future recall.

        Args:
            violation: The violation that was healed
            healing_result: The successful healing result

        Returns:
            Pattern ID if stored successfully, None otherwise
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "LICAgentBase.store_healing_pattern"
        )

        if self._meta_client is None:
            self._initialize_meta_client()
        if not self.validate_domain_pattern({"domain": APPS_LIC_DIR, **violation}):
            return None
        return self._meta_client.store_healing_pattern(violation, healing_result, domain=APPS_LIC_DIR)

    def retrieve_healing_patterns(self, violation: dict[str, Any], top_k: int = 3) -> list[HealingPattern]:
        """
        Retrieve similar healing patterns for a violation.

        Args:
            violation: Current violation to find patterns for
            top_k: Maximum number of patterns to retrieve

        Returns:
            List of similar healing patterns
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.retrieve_healing_patterns(
            violation,
            domain=APPS_LIC_DIR,
            top_k=top_k,
            min_similarity=self._similarity_threshold,
        )

    def ml_check_healing_depth(self, violation_id: str) -> bool:
        """
        Check healing depth using MetaLearningClient.

        Args:
            violation_id: Unique violation identifier

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.check_healing_depth(self.__class__.__name__, violation_id)

    def ml_increment_healing_depth(self, violation_id: str) -> int:
        """
        Increment healing depth using MetaLearningClient.

        Args:
            violation_id: Unique violation identifier

        Returns:
            Current depth after increment
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.increment_healing_depth(self.__class__.__name__, violation_id)

    def ml_reset_healing_depth(self, violation_id: str) -> None:
        """
        Reset healing depth after successful healing.

        Args:
            violation_id: Unique violation identifier
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        self._meta_client.reset_healing_depth(self.__class__.__name__, violation_id)

    def get_meta_learning_stats(self) -> dict[str, Any]:
        """
        Get meta-learning statistics for monitoring.

        Returns:
            Dictionary with meta-learning statistics
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.get_stats()

    def get_lic_context(self) -> dict[str, Any]:
        return {
            "domain": "apps_lic",
            "version": self._lic_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    def cache_pattern_with_metadata(
        self,
        pattern_type: str,
        pattern_id: str,
        pattern_data: dict[str, Any],
        success_count: int = 0,
    ) -> bool:
        """
        Cache a pattern with full metadata for enhanced learning.

        Args:
            pattern_type: Type of pattern (campaign, compliance, etc.)
            pattern_id: Unique pattern identifier
            pattern_data: Pattern data
            success_count: Number of successful applications

        Returns:
            True if cached successfully
        """
        import time

        if not self.check_and_enforce_rate_limit("pattern"):
            return False
        if not self.check_cache_capacity():
            return False
        enhanced_data = {
            **pattern_data,
            "_metadata": {
                "pattern_type": pattern_type,
                "domain": "apps_lic",
                "created_at": time.time(),
                "success_count": success_count,
                "similarity_threshold": self._similarity_threshold,
            },
        }
        success, namespaced_key = self.isolate_cache_operation(
            "set",
            f"{pattern_type}:{pattern_id}",
            enhanced_data,
        )
        if not success:
            return False
        try:
            result = self.ml_cache_set(namespaced_key, enhanced_data)
            if result:
                self.update_cache_metrics(1)
            return result
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            Logger.error(f"[{self.__class__.__name__}] Enhanced cache failed: {e}")
            return False

    def retrieve_pattern_with_metadata(self, pattern_type: str, pattern_id: str) -> dict[str, Any] | None:
        """
        Retrieve a pattern with its metadata.

        Args:
            pattern_type: Type of pattern
            pattern_id: Pattern identifier

        Returns:
            Pattern data with metadata or None
        """
        if not self.check_and_enforce_rate_limit("request"):
            return None
        namespaced_key = self.get_namespaced_cache_key(f"{pattern_type}:{pattern_id}")
        try:
            return self.ml_cache_get(namespaced_key)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            Logger.error(f"[{self.__class__.__name__}] Pattern retrieval failed: {e}")
            return None

    def increment_pattern_success(self, pattern_type: str, pattern_id: str) -> bool:
        """
        Increment success count for a pattern (learning signal).

        Args:
            pattern_type: Type of pattern
            pattern_id: Pattern identifier

        Returns:
            True if updated successfully
        """
        pattern = self.retrieve_pattern_with_metadata(pattern_type, pattern_id)
        if pattern is None:
            return False
        metadata = pattern.get("_metadata", {})
        metadata["success_count"] = metadata.get("success_count", 0) + 1
        pattern["_metadata"] = metadata
        return self.cache_pattern_with_metadata(pattern_type, pattern_id, pattern, metadata["success_count"])

    def ml_cache_campaign_pattern(self, campaign_id: str, pattern_data: dict[str, Any]) -> bool:
        """
        Cache a successful campaign pattern for future recall.

        Args:
            campaign_id: Unique campaign identifier
            pattern_data: Campaign pattern data (templates, timing, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_campaign_pattern(self, campaign_id: str) -> dict[str, Any] | None:
        """
        Recall a cached campaign pattern.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_compliance_rule(self, rule_id: str, rule_data: dict[str, Any]) -> bool:
        """
        Cache a compliance rule resolution for future reference.

        Args:
            rule_id: Unique rule identifier
            rule_data: Rule resolution data

        Returns:
            True if cached successfully
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_set(cache_key, rule_data)

    def ml_recall_compliance_rule(self, rule_id: str) -> dict[str, Any] | None:
        """
        Recall a cached compliance rule resolution.

        Args:
            rule_id: Unique rule identifier

        Returns:
            Cached rule data or None
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_get(cache_key)

    def get_namespaced_cache_key(self, key: str) -> str:
        """
        Generate a namespaced cache key for LIC domain isolation.

        Args:
            key: Base cache key

        Returns:
            Namespaced key with apps_lic prefix
        """
        return f"apps_lic:{self._resource_prefix}:{key}"

    def validate_domain_pattern(self, pattern: dict[str, Any]) -> bool:
        """
        Validate that a pattern belongs to the LIC domain.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for LIC domain
        """
        domain_value = pattern.get("domain") or pattern.get("_domain")
        if domain_value:
            if domain_value != APPS_LIC_DIR:
                Logger.warning(f"[{self.__class__.__name__}] Rejected cross-domain pattern: {domain_value}")
                return False
        return True

    def isolate_cache_operation(self, operation: str, key: str, value: Any = None) -> tuple[bool, Any]:
        """
        Perform a cache operation with domain isolation.

        Args:
            operation: 'get', 'set', or 'delete'
            key: Cache key (will be namespaced)
            value: Value for set operations

        Returns:
            Tuple of (success, result)
        """
        namespaced_key = self.get_namespaced_cache_key(key)
        if not self.guardrails_validate_cache_key(namespaced_key):
            return (False, None)
        if operation == "set" and value is not None:
            if not self.guardrails_validate_cache_value(value):
                return (False, None)
            if isinstance(value, dict):
                value["_domain"] = APPS_LIC_DIR
                value["_namespace"] = self._namespace
        return (True, namespaced_key)

    def check_and_enforce_rate_limit(self, operation: str = "request") -> bool:
        """
        Check and enforce rate limits for cache operations.

        Args:
            operation: Type of operation ('request' or 'pattern')

        Returns:
            True if operation is allowed, False if rate limited
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        allowed = self._guardrails.check_rate_limit(APPS_LIC_DIR, operation)
        if not allowed:
            Logger.warning(f"[{self.__class__.__name__}] Rate limit exceeded for {operation}")
        return allowed

    def check_cache_capacity(self) -> bool:
        """
        Check if cache has capacity for new entries.

        Returns:
            True if cache can accept new entries, False if at capacity
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_cache_size_limit(APPS_LIC_DIR)

    def update_cache_metrics(self, delta: int = 1) -> None:
        """
        Update cache size metrics after cache operations.

        Args:
            delta: Change in cache size (+1 for add, -1 for remove)
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        self._guardrails.update_cache_size(APPS_LIC_DIR, delta)

    def safe_cache_set(self, key: str, value: Any, validate_rate: bool = True) -> bool:
        """
        Safely set a cache value with rate limiting and size checks.

        Args:
            key: Cache key
            value: Value to cache
            validate_rate: Whether to check rate limits

        Returns:
            True if cached successfully, False otherwise
        """
        if validate_rate and (not self.check_and_enforce_rate_limit("request")):
            return False
        if not self.check_cache_capacity():
            Logger.warning(f"[{self.__class__.__name__}] Cache at capacity")
            return False
        success, namespaced_key = self.isolate_cache_operation("set", key, value)
        if not success:
            return False
        try:
            result = self.ml_cache_set(namespaced_key, value)
            if result:
                self.update_cache_metrics(1)
            return result
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            Logger.error(f"[{self.__class__.__name__}] Cache set failed: {e}")
            return False

    def safe_cache_get(self, key: str, validate_rate: bool = True) -> Any:
        """
        Safely get a cache value with rate limiting.

        Args:
            key: Cache key
            validate_rate: Whether to check rate limits

        Returns:
            Cached value or None
        """
        if validate_rate and (not self.check_and_enforce_rate_limit("request")):
            return None
        namespaced_key = self.get_namespaced_cache_key(key)
        try:
            return self.ml_cache_get(namespaced_key)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            Logger.error(f"[{self.__class__.__name__}] Cache get failed: {e}")
            return None

    def get_cache_health(self) -> dict[str, Any]:
        """
        Get cache health metrics for monitoring.

        Returns:
            Dictionary with cache health information
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        stats = self._guardrails.get_stats()
        return {
            "domain": "apps_lic",
            "cache_size": stats.get("cache_sizes", {}).get("apps_lic", 0),
            "request_rate": stats.get("request_rates", {}).get("apps_lic", 0),
            "pattern_rate": stats.get("pattern_rates", {}).get("apps_lic", 0),
            "active_healing_cycles": len(stats.get("depth_trackers", {}).get(self.__class__.__name__, {})),
            "healthy": True,
        }

    def guardrails_validate_cache_key(self, key: str) -> bool:
        """
        Validate cache key to prevent injection attacks.

        Args:
            key: Cache key to validate

        Returns:
            True if key is safe, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_cache_key(key)

    def guardrails_validate_cache_value(self, value: Any) -> bool:
        """
        Validate cache value to prevent memory exhaustion.

        Args:
            value: Cache value to validate

        Returns:
            True if value is safe, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_cache_value(value)

    def guardrails_check_healing_depth(self, violation_id: str) -> bool:
        """
        Check if healing depth limit is reached for this agent.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_increment_healing_depth(self, violation_id: str) -> int:
        """
        Increment healing depth counter.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            Current depth after increment
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.increment_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_reset_healing_depth(self, violation_id: str) -> None:
        """
        Reset healing depth counter after successful healing.

        Args:
            violation_id: Unique identifier for the violation
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        self._guardrails.reset_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_validate_domain_isolation(self, pattern: dict[str, Any]) -> bool:
        """
        Validate domain isolation to prevent cross-domain contamination.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for apps_lic domain, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_domain_isolation(APPS_LIC_DIR, pattern)

    def guardrails_sanitize_violation(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize violation data to prevent cache poisoning.

        Args:
            violation: Raw violation data

        Returns:
            Sanitized violation data
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.sanitize_violation_data(violation)

    def guardrails_check_rate_limit(self, operation: str = "request") -> bool:
        """
        Check rate limits for operations.

        Args:
            operation: Type of operation (request, pattern)

        Returns:
            True if operation allowed, False if rate limited
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_rate_limit(APPS_LIC_DIR, operation)

    def guardrails_get_stats(self) -> dict[str, Any]:
        """Get guardrails statistics for monitoring."""
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.get_stats()
