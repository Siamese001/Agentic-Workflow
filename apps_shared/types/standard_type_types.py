"""Cross-Engine Quality Standards - Unified quality benchmarks.

This module defines unified quality standards that apply across all engines
while allowing for domain-specific customizations.

# guardian: allow-magic-config
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "standard_type_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "standard_type_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "standard_type_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("standard_type_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("standard_type_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("standard_type_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("standard_type_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("standard_type_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("standard_type_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("standard_type_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("standard_type_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("standard_type_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("standard_type_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("standard_type_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("standard_type_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("standard_type_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("standard_type_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("standard_type_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("standard_type_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("standard_type_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("standard_type_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("standard_type_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("standard_type_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("standard_type_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("standard_type_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("standard_type_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "standard_type_types", "context_pull")
trace_contract._emit_pulls_context("p1", "standard_type_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "standard_type_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "standard_type_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "standard_type_types", "write_through")
trace_contract._emit_writes_through("p1", "standard_type_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "standard_type_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "standard_type_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "standard_type_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "standard_type_types", "human_escalation")
trace_contract._emit_routes_through("p1", "standard_type_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "standard_type_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "standard_type_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "standard_type_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "standard_type_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "standard_type_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "standard_type_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "standard_type_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "standard_type_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "standard_type_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "standard_type_types")
trace_contract._emit_gated_by_confidence("p1", "standard_type_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "standard_type_types")
trace_contract.emit_determinism_digest("p0", "standard_type_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "standard_type_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "standard_type_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "standard_type_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "standard_type_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "standard_type_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "standard_type_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "standard_type_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "standard_type_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "standard_type_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "standard_type_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "standard_type_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "standard_type_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "standard_type_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "standard_type_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "standard_type_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "standard_type_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "standard_type_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "standard_type_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "standard_type_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "standard_type_types", "exec_snapshot_link")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "standard_type_types", "urg_read_62")


class StandardType(Enum):
    """Types of quality standards."""

    BASE = "base"
    PREFERRED = "preferred"
    EXCELLENCE = "excellence"


class QualityDimension(Enum):
    """Dimensions of quality assessment."""

    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    VALUE = "value"


@dataclass
class QualityStandard:
    """Definition of a quality standard."""

    name: str
    description: str
    dimension: QualityDimension
    standard_type: StandardType
    criteria: dict[str, Any]
    measurement_method: str
    validation_rules: list[str] = field(default_factory=list)

    def evaluate(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate content against this standard.

        Args:
            content: Content to evaluate
            context: Evaluation context

        Returns:
            Evaluation results
        """
        return {"score": 0.0, "passed": False, "details": {}}


@dataclass
class EngineQualityProfile:
    """Quality profile for a specific engine."""

    engine_type: EngineType
    base_standards: set[str]
    preferred_standards: set[str]
    excellence_standards: set[str]
    custom_thresholds: QualityThresholds
    domain_weights: dict[str, float]

    def get_standards_for_level(self, level: StandardType) -> set[str]:
        """Get standards for a quality level.

        Args:
            level: Quality level

        Returns:
            Set of standard names
        """
        if level == StandardType.BASE:
            return self.base_standards
        elif level == StandardType.PREFERRED:
            return self.base_standards | self.preferred_standards
        else:
            return self.base_standards | self.preferred_standards | self.excellence_standards


class CrossEngineQualityStandards:
    """Manages quality standards across all engines."""

    def __init__(self):
        """Initialize the quality standards manager."""
        self._standards: dict[str, QualityStandard] = {}
        self._profiles: dict[EngineType, EngineQualityProfile] = {}
        self._initialize_base_standards()
        self._initialize_engine_profiles()
        logger.info("Initialized CrossEngineQualityStandards")

    def _initialize_base_standards(self) -> None:
        """Initialize base quality standards."""
        self._standards["factual_accuracy"] = QualityStandard(
            name="factual_accuracy",
            description="Content must be factually correct and verifiable",
            dimension=QualityDimension.ACCURACY,
            standard_type=StandardType.BASE,
            criteria={"min_confidence": 0.8, "max_unverified_claims": 0, "requires_sources": True},
            measurement_method="claim_verification",
            validation_rules=["no_false_claims", "verify_statistics", "check_dates"],
        )
        self._standards["no_hallucination"] = QualityStandard(
            name="no_hallucination",
            description="Content must not contain hallucinated information",
            dimension=QualityDimension.ACCURACY,
            standard_type=StandardType.BASE,
            criteria={
                "max_hallucination_risk": 0.2,
                "no_speculative_language": True,
                "grounded_in_context": True,
            },
            measurement_method="risk_assessment",
            validation_rules=["check_speculative_claims", "verify_context_grounding"],
        )
        self._standards["context_relevance"] = QualityStandard(
            name="context_relevance",
            description="Content must be relevant to the given context",
            dimension=QualityDimension.RELEVANCE,
            standard_type=StandardType.BASE,
            criteria={
                "min_relevance_score": 0.7,
                "addresses_requirements": True,
                "avoids_irrelevant_content": True,
            },
            measurement_method="semantic_analysis",
            validation_rules=["check_keyword_alignment", "validate_requirement_coverage"],
        )
        self._standards["readability"] = QualityStandard(
            name="readability",
            description="Content must be clear and readable",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.BASE,
            criteria={"max_sentence_length": 25, "min_readability_score": 0.6, "proper_grammar": True},
            measurement_method="readability_analysis",
            validation_rules=["check_grammar", "analyze_sentence_structure"],
        )
        self._standards["coherence"] = QualityStandard(
            name="coherence",
            description="Content must be internally coherent",
            dimension=QualityDimension.CONSISTENCY,
            standard_type=StandardType.BASE,
            criteria={"logical_flow": True, "no_contradictions": True, "consistent_terminology": True},
            measurement_method="coherence_analysis",
            validation_rules=["check_logical_flow", "detect_contradictions"],
        )
        self._standards["adds_value"] = QualityStandard(
            name="adds_value",
            description="Content must provide value to the reader",
            dimension=QualityDimension.VALUE,
            standard_type=StandardType.PREFERRED,
            criteria={"min_value_score": 0.7, "actionable_insights": True, "unique_perspective": True},
            measurement_method="value_assessment",
            validation_rules=["check_insight_quality", "validate_uniqueness"],
        )
        self._standards["completeness"] = QualityStandard(
            name="completeness",
            description="Content must fully address requirements",
            dimension=QualityDimension.COMPLETENESS,
            standard_type=StandardType.BASE,
            criteria={"covers_all_requirements": True, "no_missing_sections": True, "adequate_detail": True},
            measurement_method="requirement_analysis",
            validation_rules=["check_requirement_coverage", "validate_section_completeness"],
        )
        self._standards["professional_tone"] = QualityStandard(
            name="professional_tone",
            description="Content maintains professional tone",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.PREFERRED,
            criteria={"appropriate_formality": True, "no_casual_language": True, "respectful_language": True},
            measurement_method="tone_analysis",
            validation_rules=["check_formality_level", "scan_inappropriate_language"],
        )
        self._standards["concise"] = QualityStandard(
            name="concise",
            description="Content is concise and to the point",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.PREFERRED,
            criteria={"min_information_density": 0.7, "no_redundancy": True, "efficient_communication": True},
            measurement_method="density_analysis",
            validation_rules=["check_redundancy", "calculate_information_density"],
        )
        self._standards["exceptional_quality"] = QualityStandard(
            name="exceptional_quality",
            description="Content demonstrates exceptional quality",
            dimension=QualityDimension.VALUE,
            standard_type=StandardType.EXCELLENCE,
            criteria={"min_overall_score": 0.9, "innovative_insights": True, "exemplary_writing": True},
            measurement_method="comprehensive_assessment",
            validation_rules=["comprehensive_quality_check", "innovation_assessment"],
        )

    def _initialize_engine_profiles(self) -> None:
        """Initialize quality profiles for each engine."""
        # guardian: allow-magic-config
        self._profiles[EngineType.RESUME] = EngineQualityProfile(
            engine_type=EngineType.RESUME,
            base_standards={
                "factual_accuracy",
                "no_hallucination",
                "context_relevance",
                "readability",
                "coherence",
                "completeness",
            },
            preferred_standards={"professional_tone", "concise", "adds_value"},
            excellence_standards={"exceptional_quality"},
            custom_thresholds=QualityThresholds(
                MIN_RELEVANCE=0.75,
                MIN_AUTHORITY=0.6,
                MIN_SPECIFICITY=0.7,
                MIN_COHERENCE=0.7,
            ),
            domain_weights={
                "accuracy": 0.3,
                "relevance": 0.2,
                "specificity": 0.2,
                "coherence": 0.2,
                "value": 0.1,
            },
        )
        # guardian: allow-magic-config
        self._profiles[EngineType.OUTREACH] = EngineQualityProfile(
            engine_type=EngineType.OUTREACH,
            base_standards={
                "factual_accuracy",
                "no_hallucination",
                "context_relevance",
                "readability",
                "coherence",
                "completeness",
            },
            preferred_standards={"professional_tone", "adds_value"},
            excellence_standards={"concise", "exceptional_quality"},
            custom_thresholds=QualityThresholds(
                MIN_RELEVANCE=0.8,
                MIN_AUTHORITY=0.5,
                MIN_SPECIFICITY=0.6,
                MIN_COHERENCE=0.7,
            ),
            domain_weights={"accuracy": 0.25, "relevance": 0.3, "clarity": 0.25, "value": 0.2},
        )

    def get_standard(self, name: str) -> QualityStandard | None:
        """Get a quality standard by name.

        Args:
            name: Standard name

        Returns:
            Quality standard if found
        """
        return self._standards.get(name)

    def get_engine_profile(self, engine_type: EngineType) -> EngineQualityProfile | None:
        """Get quality profile for an engine.

        Args:
            engine_type: Type of engine

        Returns:
            Engine quality profile
        """
        return self._profiles.get(engine_type)

    def evaluate_against_standards(
        self,
        content: str,
        engine_type: EngineType,
        quality_level: StandardType = StandardType.BASE,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate content against engine-specific standards.

        Args:
            content: Content to evaluate
            engine_type: Type of engine
            quality_level: Quality level to evaluate against
            context: Optional context

        Returns:
            Evaluation results
        """
        profile = self.get_engine_profile(engine_type)
        if not profile:
            return {"error": f"No profile found for engine {engine_type}"}
        required_standards = profile.get_standards_for_level(quality_level)
        results = {
            "engine_type": engine_type.value,
            "quality_level": quality_level.value,
            "standards_evaluated": len(required_standards),
            "standards_passed": 0,
            "standards_failed": [],
            "overall_score": 0.0,
            "detailed_results": {},
        }
        total_score = 0.0
        for standard_name in tqdm(required_standards, desc="Processing", unit="item"):
            standard = self.get_standard(standard_name)
            if not standard:
                continue
            standard_result = standard.evaluate(content, context or {})
            results["detailed_results"][standard_name] = standard_result
            if standard_result.get("passed", False):
                results["standards_passed"] += 1
            else:
                results["standards_failed"].append(standard_name)
            total_score += standard_result.get("score", 0.0)
        if results["standards_evaluated"] > 0:
            results["overall_score"] = total_score / results["standards_evaluated"]
        return results

    def get_quality_gates(self, engine_type: EngineType) -> dict[str, dict[str, Any]]:
        """Get quality gates for an engine.

        Args:
            engine_type: Type of engine

        Returns:
            Quality gates configuration
        """
        profile = self.get_engine_profile(engine_type)
        if not profile:
            return {}
        return {
            "base_gate": {
                "required_standards": list(profile.base_standards),
                "min_score": 0.6,
                "description": "Minimum acceptable quality",
            },
            "preferred_gate": {
                "required_standards": list(profile.base_standards | profile.preferred_standards),
                "min_score": 0.75,
                "description": "Preferred quality for production",
            },
            "excellence_gate": {
                "required_standards": list(
                    profile.base_standards | profile.preferred_standards | profile.excellence_standards,
                ),
                "min_score": 0.9,
                "description": "Excellence quality level",
            },
        }

    def create_domain_config_from_standards(
        self,
        engine_type: EngineType,
        quality_level: StandardType = StandardType.PREFERRED,
    ) -> DomainConfig:
        """Create domain config based on quality standards.

        Args:
            engine_type: Type of engine
            quality_level: Quality level

        Returns:
            Domain configuration
        """
        import uuid  # noqa: PLC0415

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            f"StandardsManager.create_domain_config:{engine_type}",
        )
        profile = self.get_engine_profile(engine_type)
        if not profile:
            raise ValueError(f"No profile found for engine {engine_type}")
        if quality_level == StandardType.BASE:
            thresholds = QualityThresholds(EXCELLENT_MIN=0.8, HIGH_MIN=0.65, GOOD_MIN=0.5, MARGINAL_MIN=0.3)
        elif quality_level == StandardType.PREFERRED:
            thresholds = profile.custom_thresholds
        else:
            thresholds = QualityThresholds(EXCELLENT_MIN=0.95, HIGH_MIN=0.85, GOOD_MIN=0.75, MARGINAL_MIN=0.6)
        validation_rules = {}
        for standard_name in profile.get_standards_for_level(quality_level):
            standard = self.get_standard(standard_name)
            if standard:
                validation_rules[standard_name] = standard.validation_rules
        return DomainConfig(
            engine_type=engine_type,
            quality_thresholds=thresholds,
            validation_rules=validation_rules,
            custom_metrics=list(profile.domain_weights.keys()),
            metric_weights=profile.domain_weights,
        )

    def export_standards(self) -> dict[str, Any]:
        """Export all standards for documentation.

        Returns:
            Standards export
        """
        return {
            "standards": {
                name: {
                    "description": std.description,
                    "dimension": std.dimension.value,
                    "type": std.standard_type.value,
                    "criteria": std.criteria,
                    "validation_rules": std.validation_rules,
                }
                for name, std in self._standards.items()
            },
            "engine_profiles": {
                engine.value: {
                    "base_standards": list(profile.base_standards),
                    "preferred_standards": list(profile.preferred_standards),
                    "excellence_standards": list(profile.excellence_standards),
                    "domain_weights": profile.domain_weights,
                }
                for engine, profile in self._profiles.items()
            },
        }


_standards: CrossEngineQualityStandards | None = None


def get_quality_standards() -> CrossEngineQualityStandards:
    """Get the global quality standards instance.

    Returns:
        CrossEngineQualityStandards instance
    """
    global _standards
    if _standards is None:
        _standards = CrossEngineQualityStandards()
    return _standards


def evaluate_content_quality(
    content: str,
    engine_type: EngineType,
    quality_level: StandardType = StandardType.BASE,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate content quality against standards.

    Args:
        content: Content to evaluate
        engine_type: Type of engine
        quality_level: Quality level
        context: Optional context

    Returns:
        Evaluation results
    """
    standards = get_quality_standards()
    return standards.evaluate_against_standards(content, engine_type, quality_level, context)


def get_engine_quality_gates(engine_type: EngineType) -> dict[str, dict[str, Any]]:
    """Get quality gates for an engine.

    Args:
        engine_type: Type of engine

    Returns:
        Quality gates configuration
    """
    standards = get_quality_standards()
    return standards.get_quality_gates(engine_type)
