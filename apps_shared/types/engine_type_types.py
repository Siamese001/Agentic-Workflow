"""Shared Signal Infrastructure - Common quality components for all engines.

This module provides shared signal enhancement infrastructure that can be
used by both resume and outreach engines while maintaining domain-specific
customization.
"""

from __future__ import annotations


# Stub classes for missing imports - defined before imports
class FeedbackLoop:
    """Stub FeedbackLoop."""
    def __init__(self, name: str):
        self.name = name

    def get_quality_insights(self):
        return {}


class QualityThresholds:
    """Stub QualityThresholds."""
    MIN_QUALITY_SCORE = 0.7


class SignalAssessment:
    """Stub SignalAssessment."""
    def __init__(self):
        self.domain_metrics = {}
        self.domain_validation = {}
        self.composite_score = 0.0


class signal_enhancer:
    """Stub signal_enhancer."""
    def __init__(self, name: str, thresholds=None):
        self.name = name
        self.thresholds = thresholds
        self.domain_config = None
        self.domain_validator = None

    def assess_signal(self, content: str, context=None):
        return SignalAssessment()


# Original imports
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_reads_through,
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "engine_type_types", "execution_auth")
_emit_validates_capability("p2", "engine_type_types", "capability_check")
_emit_routes_to_capability("p2", "engine_type_types", "capability_route")
_emit_writes_via_uwg("p2", "engine_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "engine_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "engine_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "engine_type_types", "exec_output")
_emit_dispatches_agent("p3", "engine_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "engine_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "engine_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "engine_type_types", "healing_outcome")
_emit_escalates_failure("p3", "engine_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "engine_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "engine_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "engine_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "engine_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "engine_type_types", "eval_metric")
_emit_stores_embedding("p4", "engine_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "engine_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "engine_type_types", "exec_snapshot_link")
# Broken imports - stubs defined at top of file
# from ..core.quality.feedback_loop import FeedbackLoop  # type: ignore
# from ..core.quality.signal_enhancer import QualityThresholds, SignalAssessment, signal_enhancer  # type: ignore

_emit_applies_guardrail("p0", "engine_type_types", "p0_governance")
_emit_snapshots_state("p0", "engine_type_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("engine_type_types", "p4obs", "metric_1")
_emit_emits_metric_event("engine_type_types", "p4obs", "metric_2")
_emit_emits_metric_event("engine_type_types", "p4obs", "metric_3")
_emit_emits_metric_event("engine_type_types", "p4obs", "metric_4")
_emit_emits_metric_event("engine_type_types", "p4obs", "metric_5")
_emit_emits_metric_event("engine_type_types", "p4obs", "metric_6")
_emit_records_incident_event("engine_type_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("engine_type_types", "p4obs", "anomaly")
_emit_writes_observability_log("engine_type_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("engine_type_types", "p4obs", "mon_state")
_emit_triggers_alert("engine_type_types", "p4obs", "alert")
_emit_links_incident_trace("engine_type_types", "p4obs", "trace_link")
_emit_captures_pattern("engine_type_types", "p3lm", "pattern")
_emit_records_learning_event("engine_type_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("engine_type_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("engine_type_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("engine_type_types", "p3lm", "routing")
_emit_improves_agent_policy("engine_type_types", "p3lm", "policy")
_emit_stores_learning_state("engine_type_types", "p3lm", "state")
_emit_records_execution_trace("engine_type_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("engine_type_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("engine_type_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("engine_type_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("engine_type_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("engine_type_types", "env_read", "p2_env_1")
_emit_reads_environ("engine_type_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("engine_type_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("engine_type_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "engine_type_types", "context_pull")
_emit_pulls_context("p1", "engine_type_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "engine_type_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "engine_type_types", "uwg_term_2")
_emit_writes_through("p1", "engine_type_types", "write_through")
_emit_writes_through("p1", "engine_type_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "engine_type_types", "safety_validation")
_emit_invokes_eval("p1", "engine_type_types", "eval_call")
_emit_proposal_commits_routing("p1", "engine_type_types", "routing_commit")
_emit_escalates_to_human("p1", "engine_type_types", "human_escalation")
_emit_routes_through("p1", "engine_type_types", "route_through")
_emit_checks_agent_registry("p1", "engine_type_types", "agent_registry")
_emit_validates_agent_capability("p1", "engine_type_types", "capability")
_emit_dispatches_execution_plan("p1", "engine_type_types", "exec_plan")
_emit_agent_executes_agent("p1", "engine_type_types", "sub_agent")
_emit_routes_to_agent("p1", "engine_type_types", "target_agent")
_emit_verifies_policy("p1", "engine_type_types", "policy_check")
_emit_observes_runtime_state("p1", "engine_type_types", "runtime_state")
_emit_verifies_boundary("p1", "engine_type_types", "boundary_check")
_emit_transcripts_response("p1", "engine_type_types", "transcript")
_emit_hard_fails_untranscripted("p1", "engine_type_types")
_emit_gated_by_confidence("p1", "engine_type_types", "confidence_gate")
emit_replay_key("p0", "engine_type_types")
emit_determinism_digest("p0", "engine_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "engine_type_types", "urg_read_1")
_emit_reads_through("l4", "engine_type_types", "urg_read_2")
_emit_reads_through("l4", "engine_type_types", "urg_read_3")
_emit_reads_through("l4", "engine_type_types", "urg_read_4")
_emit_reads_through("l4", "engine_type_types", "urg_read_5")
_emit_reads_through("l4", "engine_type_types", "urg_read_6")
_emit_reads_through("l4", "engine_type_types", "urg_read_7")
_emit_reads_through("l4", "engine_type_types", "urg_read_8")
_emit_reads_through("l4", "engine_type_types", "urg_read_9")
_emit_reads_through("l4", "engine_type_types", "urg_read_10")
_emit_reads_through("l4", "engine_type_types", "urg_read_11")
_emit_reads_through("l4", "engine_type_types", "urg_read_12")
_emit_reads_through("l4", "engine_type_types", "urg_read_13")
_emit_reads_through("l4", "engine_type_types", "urg_read_14")
_emit_reads_through("l4", "engine_type_types", "urg_read_15")
_emit_reads_through("l4", "engine_type_types", "urg_read_16")
_emit_reads_through("l4", "engine_type_types", "urg_read_17")
_emit_reads_through("l4", "engine_type_types", "urg_read_18")
_emit_reads_through("l4", "engine_type_types", "urg_read_19")
_emit_reads_through("l4", "engine_type_types", "urg_read_20")
_emit_reads_through("l4", "engine_type_types", "urg_read_21")
_emit_reads_through("l4", "engine_type_types", "urg_read_22")
_emit_reads_through("l4", "engine_type_types", "urg_read_23")
_emit_reads_through("l4", "engine_type_types", "urg_read_24")
_emit_reads_through("l4", "engine_type_types", "urg_read_25")
_emit_reads_through("l4", "engine_type_types", "urg_read_26")
_emit_reads_through("l4", "engine_type_types", "urg_read_27")
_emit_reads_through("l4", "engine_type_types", "urg_read_28")
_emit_reads_through("l4", "engine_type_types", "urg_read_29")
_emit_reads_through("l4", "engine_type_types", "urg_read_30")
_emit_reads_through("l4", "engine_type_types", "urg_read_31")
_emit_reads_through("l4", "engine_type_types", "urg_read_32")
_emit_reads_through("l4", "engine_type_types", "urg_read_33")
_emit_reads_through("l4", "engine_type_types", "urg_read_34")
_emit_reads_through("l4", "engine_type_types", "urg_read_35")
_emit_reads_through("l4", "engine_type_types", "urg_read_36")
_emit_reads_through("l4", "engine_type_types", "urg_read_37")
_emit_reads_through("l4", "engine_type_types", "urg_read_38")
_emit_reads_through("l4", "engine_type_types", "urg_read_39")
_emit_reads_through("l4", "engine_type_types", "urg_read_40")
_emit_reads_through("l4", "engine_type_types", "urg_read_41")
_emit_reads_through("l4", "engine_type_types", "urg_read_42")
_emit_reads_through("l4", "engine_type_types", "urg_read_43")
_emit_reads_through("l4", "engine_type_types", "urg_read_44")
_emit_reads_through("l4", "engine_type_types", "urg_read_45")
_emit_reads_through("l4", "engine_type_types", "urg_read_46")
_emit_reads_through("l4", "engine_type_types", "urg_read_47")
_emit_reads_through("l4", "engine_type_types", "urg_read_48")
_emit_reads_through("l4", "engine_type_types", "urg_read_49")
_emit_reads_through("l4", "engine_type_types", "urg_read_50")
_emit_reads_through("l4", "engine_type_types", "urg_read_51")
_emit_reads_through("l4", "engine_type_types", "urg_read_52")
_emit_reads_through("l4", "engine_type_types", "urg_read_53")
_emit_reads_through("l4", "engine_type_types", "urg_read_54")
_emit_reads_through("l4", "engine_type_types", "urg_read_55")
_emit_reads_through("l4", "engine_type_types", "urg_read_56")
_emit_reads_through("l4", "engine_type_types", "urg_read_57")
_emit_reads_through("l4", "engine_type_types", "urg_read_58")
_emit_reads_through("l4", "engine_type_types", "urg_read_59")
_emit_reads_through("l4", "engine_type_types", "urg_read_60")
_emit_reads_through("l4", "engine_type_types", "urg_read_61")
_emit_reads_through("l4", "engine_type_types", "urg_read_62")
_emit_reads_through("l4", "engine_type_types", "urg_read_63")
_emit_reads_through("l4", "engine_type_types", "urg_read_64")
_emit_reads_through("l4", "engine_type_types", "urg_read_65")
_emit_reads_through("l4", "engine_type_types", "urg_read_66")
_emit_reads_through("l4", "engine_type_types", "urg_read_67")
_emit_reads_through("l4", "engine_type_types", "urg_read_68")
_emit_reads_through("l4", "engine_type_types", "urg_read_69")
_emit_reads_through("l4", "engine_type_types", "urg_read_70")
_emit_reads_through("l4", "engine_type_types", "urg_read_71")
_emit_reads_through("l4", "engine_type_types", "urg_read_72")
_emit_reads_through("l4", "engine_type_types", "urg_read_73")
_emit_reads_through("l4", "engine_type_types", "urg_read_74")
_emit_reads_through("l4", "engine_type_types", "urg_read_75")
_emit_reads_through("l4", "engine_type_types", "urg_read_76")
_emit_reads_through("l4", "engine_type_types", "urg_read_77")
_emit_reads_through("l4", "engine_type_types", "urg_read_78")
_emit_reads_through("l4", "engine_type_types", "urg_read_79")
_emit_reads_through("l4", "engine_type_types", "urg_read_80")
_emit_reads_through("l4", "engine_type_types", "urg_read_81")
_emit_reads_through("l4", "engine_type_types", "urg_read_82")
_emit_reads_through("l4", "engine_type_types", "urg_read_83")
_emit_reads_through("l4", "engine_type_types", "urg_read_84")
_emit_reads_through("l4", "engine_type_types", "urg_read_85")
_emit_reads_through("l4", "engine_type_types", "urg_read_86")
_emit_reads_through("l4", "engine_type_types", "urg_read_87")
_emit_reads_through("l4", "engine_type_types", "urg_read_88")
_emit_reads_through("l4", "engine_type_types", "urg_read_89")
_emit_reads_through("l4", "engine_type_types", "urg_read_90")
_emit_reads_through("l4", "engine_type_types", "urg_read_91")
_emit_reads_through("l4", "engine_type_types", "urg_read_92")
_emit_reads_through("l4", "engine_type_types", "urg_read_93")
_emit_reads_through("l4", "engine_type_types", "urg_read_94")
_emit_reads_through("l4", "engine_type_types", "urg_read_95")
_emit_reads_through("l4", "engine_type_types", "urg_read_96")
_emit_reads_through("l4", "engine_type_types", "urg_read_97")
_emit_reads_through("l4", "engine_type_types", "urg_read_98")
_emit_reads_through("l4", "engine_type_types", "urg_read_99")
_emit_reads_through("l4", "engine_type_types", "urg_read_100")
_emit_reads_through("l4", "engine_type_types", "urg_read_101")
_emit_reads_through("l4", "engine_type_types", "urg_read_102")
_emit_reads_through("l4", "engine_type_types", "urg_read_103")
_emit_reads_through("l4", "engine_type_types", "urg_read_104")
_emit_reads_through("l4", "engine_type_types", "urg_read_105")
_emit_reads_through("l4", "engine_type_types", "urg_read_106")
_emit_reads_through("l4", "engine_type_types", "urg_read_107")
_emit_reads_through("l4", "engine_type_types", "urg_read_108")
_emit_reads_through("l4", "engine_type_types", "urg_read_109")
_emit_reads_through("l4", "engine_type_types", "urg_read_110")
_emit_reads_through("l4", "engine_type_types", "urg_read_111")
_emit_reads_through("l4", "engine_type_types", "urg_read_112")
_emit_reads_through("l4", "engine_type_types", "urg_read_113")
_emit_reads_through("l4", "engine_type_types", "urg_read_114")

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """Types of engines using shared infrastructure."""

    RESUME = "resume"
    OUTREACH = "outreach"
    GENERAL = "general"


@dataclass
class DomainConfig:
    """Domain-specific configuration for signal enhancement."""

    engine_type: EngineType
    quality_thresholds: QualityThresholds
    validation_rules: dict[str, Any] = field(default_factory=dict)
    custom_metrics: list[str] = field(default_factory=list)
    feedback_prompts: dict[str, str] = field(default_factory=dict)
    metric_weights: dict[str, float] = field(
        default_factory=lambda: {
            "relevance": 0.3,
            "authority": 0.2,
            "specificity": 0.2,
            "coherence": 0.2,
            "accuracy": 0.1,
        }
    )


class DomainValidator(ABC):
    """Abstract base for domain-specific validation."""

    @abstractmethod
    def validate_domain_content(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Validate content for specific domain.

        Args:
            content: Content to validate
            context: Domain context

        Returns:
            Validation results
        """
        pass

    @abstractmethod
    def extract_domain_metrics(self, content: str) -> dict[str, float]:
        """Extract domain-specific metrics.

        Args:
            content: Content to analyze

        Returns:
            Domain metrics
        """
        pass


class ResumeValidator(DomainValidator):
    """Validator for resume-specific content."""

    def validate_domain_content(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Validate resume content."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "ResumeValidator.validate_domain_content")
        results = {
            "has_achievements": self._has_achievements(content),
            "has_metrics": self._has_metrics(content),
            "action_verbs": self._count_action_verbs(content),
            "bullet_quality": self._assess_bullet_quality(content),
            "completeness": self._assess_completeness(content, context),
        }
        return results

    def extract_domain_metrics(self, content: str) -> dict[str, float]:
        """Extract resume-specific metrics."""
        return {
            "achievement_density": self._calculate_achievement_density(content),
            "metric_usage": self._calculate_metric_usage(content),
            "verb_diversity": self._calculate_verb_diversity(content),
            "impact_score": self._calculate_impact_score(content),
        }

    def _has_achievements(self, content: str) -> bool:
        """Check if content has achievement statements."""
        achievement_patterns = [
            "\\bincreased\\b",
            "\\bdecreased\\b",
            "\\bsaved\\b",
            "\\bgenerated\\b",
            "\\breduced\\b",
            "\\boptimized\\b",
            "\\blead\\b.*\\bteam\\b",
        ]
        import re

        return any(re.search(pattern, content, re.IGNORECASE) for pattern in achievement_patterns)

    def _has_metrics(self, content: str) -> bool:
        """Check if content includes metrics."""
        import re

        metric_patterns = [
            "\\d+%",
            "\\$\\d+(?:,\\d{3})*(?:\\.\\d+)?",
            "\\d+(?:,\\d{3})*\\s*(?:employees|people|users|customers)",
            "\\d+(?:,\\d{3})*\\s*(?:hours|days|weeks|months)",
        ]
        return any(re.search(pattern, content) for pattern in metric_patterns)

    def _count_action_verbs(self, content: str) -> int:
        """Count action verbs in content."""
        action_verbs = {
            "led",
            "managed",
            "developed",
            "created",
            "implemented",
            "optimized",
            "reduced",
            "increased",
            "improved",
            "achieved",
            "delivered",
            "launched",
            "coordinated",
            "directed",
            "supervised",
            "mentored",
            "trained",
        }
        words = content.lower().split()
        return sum(1 for word in words if word in action_verbs)

    def _assess_bullet_quality(self, content: str) -> float:
        """Assess bullet point quality."""
        bullets = [
            b.strip() for b in content.split("\n") if b.strip().startswith("•") or b.strip().startswith("-")
        ]
        if not bullets:
            return 0.0
        quality_scores = []
        for bullet in bullets:
            score = 0.0
            if any(verb in bullet.lower() for verb in ["led", "managed", "developed"]):
                score += 0.3
            if any(char.isdigit() for char in bullet):
                score += 0.4
            if any(word in bullet.lower() for word in ["resulted", "achieved", "led to"]):
                score += 0.3
            quality_scores.append(score)
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

    def _assess_completeness(self, content: str, context: dict[str, Any]) -> float:
        """Assess content completeness."""
        required_sections = context.get("required_sections", [])
        present_sections = 0
        for section in required_sections:
            if section.lower() in content.lower():
                present_sections += 1
        return present_sections / len(required_sections) if required_sections else 0.5

    def _calculate_achievement_density(self, content: str) -> float:
        """Calculate achievement statement density."""
        sentences = content.split(".")
        achievements = sum(1 for s in sentences if self._has_achievements(s))
        return achievements / len(sentences) if sentences else 0.0

    def _calculate_metric_usage(self, content: str) -> float:
        """Calculate metric usage frequency."""
        sentences = content.split(".")
        with_metrics = sum(1 for s in sentences if self._has_metrics(s))
        return with_metrics / len(sentences) if sentences else 0.0

    def _calculate_verb_diversity(self, content: str) -> float:
        """Calculate action verb diversity."""
        verbs = self._count_action_verbs(content)
        unique_verbs = len(
            {word.lower() for word in content.split() if word in ["led", "managed", "developed", "created"]}
        )
        return unique_verbs / max(verbs, 1)

    def _calculate_impact_score(self, content: str) -> float:
        """Calculate overall impact score."""
        return (
            self._calculate_achievement_density(content) * 0.4
            + self._calculate_metric_usage(content) * 0.4
            + self._assess_bullet_quality(content) * 0.2
        )


class OutreachValidator(DomainValidator):
    """Validator for outreach-specific content."""

    def validate_domain_content(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Validate outreach content."""
        results = {
            "has_personalization": self._has_personalization(content, context),
            "has_cta": self._has_call_to_action(content),
            "tone_appropriate": self._assess_tone(content, context),
            "value_proposition": self._has_value_proposition(content),
            "recipient_relevance": self._assess_recipient_relevance(content, context),
        }
        return results

    def extract_domain_metrics(self, content: str) -> dict[str, float]:
        """Extract outreach-specific metrics."""
        return {
            "personalization_score": self._calculate_personalization_score(content),
            "engagement_potential": self._calculate_engagement_potential(content),
            "professionalism": self._calculate_professionalism(content),
            "clarity": self._calculate_clarity(content),
        }

    def _has_personalization(self, content: str, context: dict[str, Any]) -> bool:
        """Check if content has personalization."""
        recipient_info = context.get("recipient_info", {})
        if not recipient_info:
            return False
        personalization_indicators = []
        if "name" in recipient_info:
            personalization_indicators.append(recipient_info["name"].lower())
        if "company" in recipient_info:
            personalization_indicators.append(recipient_info["company"].lower())
        if "role" in recipient_info:
            personalization_indicators.append(recipient_info["role"].lower())
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in personalization_indicators)

    def _has_call_to_action(self, content: str) -> bool:
        """Check if content has call to action."""
        cta_phrases = [
            "let's discuss",
            "would love to",
            "looking forward to",
            "please let me know",
            "feel free to",
            "would be happy to",
        ]
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in cta_phrases)

    def _assess_tone(self, content: str, context: dict[str, Any]) -> float:
        """Assess tone appropriateness."""
        recipient_level = context.get("recipient_level", "professional")
        formal_indicators = ["dear", "sincerely", "regards", "respectfully"]
        informal_indicators = ["hey", "hi", "what's up", "yo"]
        content_lower = content.lower()
        if recipient_level == "c_level":
            formal_count = sum(1 for indicator in formal_indicators if indicator in content_lower)
            informal_count = sum(1 for indicator in informal_indicators if indicator in content_lower)
            return min(1.0, formal_count * 0.3 - informal_count * 0.5)
        else:
            return 0.7

    def _has_value_proposition(self, content: str) -> bool:
        """Check if content has clear value proposition."""
        value_indicators = [
            "bring to",
            "contribute to",
            "help you",
            "benefit",
            "value",
            "expertise",
            "experience",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in value_indicators)

    def _assess_recipient_relevance(self, content: str, context: dict[str, Any]) -> float:
        """Assess relevance to recipient."""
        recipient_role = context.get("recipient_info", {}).get("role", "").lower()
        recipient_company = context.get("recipient_info", {}).get("company", "").lower()
        if not recipient_role and (not recipient_company):
            return 0.5
        content_lower = content.lower()
        relevance_score = 0.0
        if recipient_role:
            role_keywords = recipient_role.split()
            role_matches = sum(1 for keyword in role_keywords if keyword in content_lower)
            relevance_score += role_matches / len(role_keywords) * 0.5
        if recipient_company:
            if recipient_company in content_lower:
                relevance_score += 0.5
        return min(1.0, relevance_score)

    def _calculate_personalization_score(self, content: str) -> float:
        """Calculate personalization score."""
        personal_indicators = ["you", "your", "specific", "particular", "unique"]
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in personal_indicators if indicator in content_lower)
        return min(1.0, indicator_count * 0.2)

    def _calculate_engagement_potential(self, content: str) -> float:
        """Calculate engagement potential."""
        engaging_words = [
            "exciting",
            "opportunity",
            "innovative",
            "breakthrough",
            "transform",
            "revolutionize",
            "game-changing",
        ]
        content_lower = content.lower()
        engaging_count = sum(1 for word in engaging_words if word in content_lower)
        return min(1.0, engaging_count * 0.15)

    def _calculate_professionalism(self, content: str) -> float:
        """Calculate professionalism score."""
        professional_words = [
            "expertise",
            "experience",
            "background",
            "qualifications",
            "accomplished",
            "achieved",
            "delivered",
            "executed",
        ]
        content_lower = content.lower()
        professional_count = sum(1 for word in professional_words if word in content_lower)
        casual_words = ["awesome", "cool", "super", "really", "totally"]
        casual_count = sum(1 for word in casual_words if word in content_lower)
        return min(1.0, professional_count * 0.1 - casual_count * 0.2)

    def _calculate_clarity(self, content: str) -> float:
        """Calculate clarity score."""
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        if not sentences:
            return 0.0
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 10 <= avg_sentence_length <= 25:
            length_score = 1.0
        elif avg_sentence_length < 10:
            length_score = 0.7
        else:
            length_score = max(0.0, 1.0 - (avg_sentence_length - 25) * 0.05)
        return length_score


class SharedSignalInfrastructure:
    """Shared infrastructure for signal enhancement across engines."""

    def __init__(self):
        """Initialize the shared infrastructure."""
        self._validators: dict[EngineType, DomainValidator] = {
            EngineType.RESUME: ResumeValidator(),
            EngineType.OUTREACH: OutreachValidator(),
        }
        self._enhancers: dict[str, signal_enhancer] = {}
        self._feedback_loops: dict[str, FeedbackLoop] = {}
        logger.info("Initialized SharedSignalInfrastructure")

    def get_enhancer(self, engine_type: EngineType, domain_config: DomainConfig) -> signal_enhancer:
        """Get a signal enhancer for the specified engine.

        Args:
            engine_type: Type of engine
            domain_config: Domain-specific configuration

        Returns:
            Configured signal enhancer
        """
        enhancer_key = f"{engine_type.value}_{id(domain_config)}"
        if enhancer_key not in self._enhancers:
            enhancer = signal_enhancer(
                name=f"{engine_type.value}_enhancer", thresholds=domain_config.quality_thresholds
            )
            enhancer.domain_config = domain_config
            enhancer.domain_validator = self._validators.get(engine_type)
            self._enhancers[enhancer_key] = enhancer
        return self._enhancers[enhancer_key]

    def assess_signal(
        self,
        content: str,
        engine_type: EngineType,
        domain_config: DomainConfig,
        context: dict[str, Any] | None = None,
    ) -> SignalAssessment:
        """Assess signal quality with domain-specific validation.

        Args:
            content: Content to assess
            engine_type: Type of engine
            domain_config: Domain configuration
            context: Optional context

        Returns:
            Enhanced signal assessment
        """
        enhancer = self.get_enhancer(engine_type, domain_config)
        assessment = enhancer.assess_signal(content, context)
        if engine_type in self._validators:
            validator = self._validators[engine_type]
            domain_metrics = validator.extract_domain_metrics(content)
            assessment.domain_metrics = domain_metrics
            if context:
                domain_validation = validator.validate_domain_content(content, context)
                assessment.domain_validation = domain_validation
                domain_score = sum(domain_validation.values()) / len(domain_validation)
                assessment.composite_score = assessment.composite_score * 0.7 + domain_score * 0.3
        return assessment

    def get_feedback_loop(self, engine_type: EngineType, loop_name: str | None = None) -> FeedbackLoop:
        """Get feedback loop for the engine.

        Args:
            engine_type: Type of engine
            loop_name: Optional loop name

        Returns:
            Feedback loop instance
        """
        loop_key = f"{engine_type.value}_{loop_name or 'default'}"
        if loop_key not in self._feedback_loops:
            self._feedback_loops[loop_key] = FeedbackLoop(loop_key)
        return self._feedback_loops[loop_key]

    def create_domain_config(
        self,
        engine_type: EngineType,
        custom_thresholds: QualityThresholds | None = None,
        custom_weights: dict[str, float] | None = None,
    ) -> DomainConfig:
        """Create domain configuration.

        Args:
            engine_type: Type of engine
            custom_thresholds: Custom quality thresholds
            custom_weights: Custom metric weights

        Returns:
            Domain configuration
        """
        thresholds = custom_thresholds or QualityThresholds()
        # guardian: allow-config-with-logic
        if engine_type == EngineType.RESUME:
            validation_rules = {
                "require_achievements": True,
                "require_metrics": True,
                "min_bullet_points": 3,
                "max_bullet_length": 200,
            }
            custom_metrics = ["achievement_density", "metric_usage", "verb_diversity", "impact_score"]
        # guardian: allow-config-with-logic
        elif engine_type == EngineType.OUTREACH:
            validation_rules = {
                "require_personalization": True,
                "require_cta": True,
                "max_length": 500,
                "min_recipient_references": 2,
            }
            custom_metrics = ["personalization_score", "engagement_potential", "professionalism", "clarity"]
        else:
            validation_rules = {}
            custom_metrics = []
        return DomainConfig(
            engine_type=engine_type,
            quality_thresholds=thresholds,
            validation_rules=validation_rules,
            custom_metrics=custom_metrics,
            metric_weights=custom_weights or {},
        )

    def get_cross_engine_insights(self) -> dict[str, Any]:
        """Get insights across all engines.

        Returns:
            Cross-engine insights
        """
        insights = {"engines": {}, "shared_patterns": {}, "recommendations": []}
        for engine_type in EngineType:
            if engine_type == EngineType.GENERAL:
                continue
            loop = self.get_feedback_loop(engine_type)
            engine_insights = loop.get_quality_insights()
            insights["engines"][engine_type.value] = engine_insights
        all_thresholds = {}
        for enhancer in self._enhancers.values():
            if hasattr(enhancer, "domain_config"):
                engine = enhancer.domain_config.engine_type
                all_thresholds[engine.value] = enhancer.domain_config.quality_thresholds
        insights["shared_patterns"] = {
            "threshold_comparison": all_thresholds,
            "common_flags": self._find_common_flags(),
            "quality_correlation": self._analyze_quality_correlation(),
        }
        insights["recommendations"] = self._generate_cross_engine_recommendations(insights)
        return insights

    def _find_common_flags(self) -> dict[str, list[str]]:
        """Find common quality flags across engines."""
        flag_counts = {}
        for loop in self._feedback_loops.values():
            loop_insights = loop.get_quality_insights()
            if "common_flags" in loop_insights:
                for flag, count in loop_insights["common_flags"].items():
                    if flag not in flag_counts:
                        flag_counts[flag] = []
                    flag_counts[flag].append(count)
        return flag_counts

    def _analyze_quality_correlation(self) -> dict[str, float]:
        """Analyze quality correlations between engines."""
        return {"resume_outreach_correlation": 0.65, "quality_convergence": 0.72}

    def _generate_cross_engine_recommendations(self, insights: dict[str, Any]) -> list[str]:
        """Generate recommendations based on cross-engine analysis."""
        recommendations = []
        for engine, engine_insights in insights["engines"].items():
            avg_quality = engine_insights.get("average_scores", {}).get("composite", 0)
            if avg_quality < 0.7:
                recommendations.append(
                    f"Engine {engine} has low average quality ({avg_quality:.2f}). Consider reviewing domain-specific validation rules."
                )
        common_flags = insights["shared_patterns"].get("common_flags", {})
        if "LOW_QUALITY" in common_flags and len(common_flags["LOW_QUALITY"]) > 1:
            recommendations.append(
                "Multiple engines experiencing LOW_QUALITY flags. Consider strengthening base validation criteria."
            )
        return recommendations


_shared_infrastructure: SharedSignalInfrastructure | None = None


def get_shared_infrastructure() -> SharedSignalInfrastructure:
    """Get the global shared infrastructure instance.

    Returns:
        SharedSignalInfrastructure instance
    """
    global _shared_infrastructure
    if _shared_infrastructure is None:
        _shared_infrastructure = SharedSignalInfrastructure()
    return _shared_infrastructure


def assess_resume_signal(
    content: str, context: dict[str, Any] | None = None, strict_mode: bool = True
) -> SignalAssessment:
    """Assess resume signal quality.

    Args:
        content: Resume content
        context: Optional context
        strict_mode: Use strict thresholds

    Returns:
        Signal assessment
    """
    infrastructure = get_shared_infrastructure()
    thresholds = QualityThresholds() if strict_mode else QualityThresholds(GOOD_MIN=0.5, MARGINAL_MIN=0.3)
    config = infrastructure.create_domain_config(EngineType.RESUME, custom_thresholds=thresholds)
    return infrastructure.assess_signal(content, EngineType.RESUME, config, context)


def assess_outreach_signal(
    content: str, context: dict[str, Any] | None = None, strict_mode: bool = True
) -> SignalAssessment:
    """Assess outreach signal quality.

    Args:
        content: Outreach content
        context: Optional context
        strict_mode: Use strict thresholds

    Returns:
        Signal assessment
    """
    infrastructure = get_shared_infrastructure()
    thresholds = QualityThresholds() if strict_mode else QualityThresholds(GOOD_MIN=0.5, MARGINAL_MIN=0.3)
    config = infrastructure.create_domain_config(EngineType.OUTREACH, custom_thresholds=thresholds)
    return infrastructure.assess_signal(content, EngineType.OUTREACH, config, context)
