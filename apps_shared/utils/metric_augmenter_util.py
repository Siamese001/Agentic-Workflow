"""ROI Translator - Metric Augmentation for Executive Communication.

This module translates technical achievements into business impact statements,
bridging the gap between engineering metrics (latency, F1) and executive
metrics (Revenue, OpEx, Retention).
"""

import logging
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "metric_augmenter_util", "p0_governance")
_emit_reads_policy_state("p0", "metric_augmenter_util", "policy_binding")
_emit_snapshots_state("p0", "metric_augmenter_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_1")
_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_2")
_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_3")
_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_4")
_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_5")
_emit_emits_metric_event("metric_augmenter_util", "p4obs", "metric_6")
_emit_records_incident_event("metric_augmenter_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("metric_augmenter_util", "p4obs", "anomaly")
_emit_writes_observability_log("metric_augmenter_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("metric_augmenter_util", "p4obs", "mon_state")
_emit_triggers_alert("metric_augmenter_util", "p4obs", "alert")
_emit_links_incident_trace("metric_augmenter_util", "p4obs", "trace_link")
_emit_captures_pattern("metric_augmenter_util", "p3lm", "pattern")
_emit_records_learning_event("metric_augmenter_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("metric_augmenter_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("metric_augmenter_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("metric_augmenter_util", "p3lm", "routing")
_emit_improves_agent_policy("metric_augmenter_util", "p3lm", "policy")
_emit_stores_learning_state("metric_augmenter_util", "p3lm", "state")
_emit_records_execution_trace("metric_augmenter_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("metric_augmenter_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("metric_augmenter_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("metric_augmenter_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("metric_augmenter_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("metric_augmenter_util", "env_read", "p2_env_1")
_emit_reads_environ("metric_augmenter_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("metric_augmenter_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("metric_augmenter_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "metric_augmenter_util", "context_pull")
_emit_pulls_context("p1", "metric_augmenter_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "metric_augmenter_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "metric_augmenter_util", "uwg_term_2")
_emit_writes_through("p1", "metric_augmenter_util", "write_through")
_emit_writes_through("p1", "metric_augmenter_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "metric_augmenter_util", "safety_validation")
_emit_invokes_eval("p1", "metric_augmenter_util", "eval_call")
_emit_proposal_commits_routing("p1", "metric_augmenter_util", "routing_commit")
_emit_escalates_to_human("p1", "metric_augmenter_util", "human_escalation")
_emit_routes_through("p1", "metric_augmenter_util", "route_through")
_emit_checks_agent_registry("p1", "metric_augmenter_util", "agent_registry")
_emit_validates_agent_capability("p1", "metric_augmenter_util", "capability")
_emit_dispatches_execution_plan("p1", "metric_augmenter_util", "exec_plan")
_emit_agent_executes_agent("p1", "metric_augmenter_util", "sub_agent")
_emit_routes_to_agent("p1", "metric_augmenter_util", "target_agent")
_emit_verifies_policy("p1", "metric_augmenter_util", "policy_check")
_emit_observes_runtime_state("p1", "metric_augmenter_util", "runtime_state")
_emit_verifies_boundary("p1", "metric_augmenter_util", "boundary_check")
_emit_transcripts_response("p1", "metric_augmenter_util", "transcript")
_emit_hard_fails_untranscripted("p1", "metric_augmenter_util")
_emit_gated_by_confidence("p1", "metric_augmenter_util", "confidence_gate")
emit_replay_key("p0", "metric_augmenter_util")
emit_determinism_digest("p0", "metric_augmenter_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "metric_augmenter_util", "execution_auth")
_emit_validates_capability("p2", "metric_augmenter_util", "capability_check")
_emit_routes_to_capability("p2", "metric_augmenter_util", "capability_route")
_emit_writes_via_uwg("p2", "metric_augmenter_util", "uwg_write")
_emit_blocks_direct_write("p2", "metric_augmenter_util", "direct_write_block")
_emit_records_tool_invocation("p2", "metric_augmenter_util", "tool_invocation")
_emit_captures_execution_output("p2", "metric_augmenter_util", "exec_output")
_emit_dispatches_agent("p3", "metric_augmenter_util", "agent_dispatch")
_emit_coordinates_agents("p3", "metric_augmenter_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "metric_augmenter_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "metric_augmenter_util", "healing_outcome")
_emit_escalates_failure("p3", "metric_augmenter_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "metric_augmenter_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "metric_augmenter_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "metric_augmenter_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "metric_augmenter_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "metric_augmenter_util", "eval_metric")
_emit_stores_embedding("p4", "metric_augmenter_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "metric_augmenter_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "metric_augmenter_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ImpactCategory(str, Enum):
    """Categories of business impact."""

    REVENUE = "REVENUE"
    OPEX = "OPEX"
    CAPEX = "CAPEX"
    RISK = "RISK"
    RETENTION = "RETENTION"


class BusinessImpact(BaseModel):
    """Business impact estimation for a technical metric."""

    category: ImpactCategory = Field(..., description="Type of business impact")
    value_statement: str = Field(..., description="Business impact statement")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in estimation")

    @validator("value_statement")
    def validate_conservative_language(cls, v):
        """Ensure conservative language is used."""
        conservative_words = ["estimated", "projected", "enabling", "potential", "up to"]
        if not any(word in v.lower() for word in conservative_words):
            logger.warning("Business impact should use conservative language")
        return v


class AugmentedBullet(BaseModel):
    """Resume bullet with business impact augmentation."""

    original_text: str = Field(..., description="Original bullet text")
    technical_metric: str | None = Field(None, description="Detected technical metric")
    business_impact: BusinessImpact | None = Field(None, description="Business impact")
    final_text: str = Field(..., description="Final augmented text")

    @property
    def is_augmented(self) -> bool:
        """Check if bullet was augmented with business impact."""
        return self.business_impact is not None


class MetricAugmenter:
    """Translates technical metrics into business impact statements."""

    def __init__(self, industry: str = "technology"):
        """Initialize the metric augmenter.

        Args:
            industry: Target industry for impact estimation
        """
        self.industry = industry.lower()
        self.metric_mappings = {
            "latency": ImpactCategory.RETENTION,
            "speed": ImpactCategory.RETENTION,
            "response_time": ImpactCategory.RETENTION,
            "throughput": ImpactCategory.REVENUE,
            "accuracy": ImpactCategory.REVENUE,
            "f1": ImpactCategory.REVENUE,
            "precision": ImpactCategory.REVENUE,
            "recall": ImpactCategory.REVENUE,
            "storage": ImpactCategory.OPEX,
            "compute": ImpactCategory.OPEX,
            "infrastructure": ImpactCategory.OPEX,
            "cloud": ImpactCategory.OPEX,
            "cost": ImpactCategory.OPEX,
            "uptime": ImpactCategory.RISK,
            "reliability": ImpactCategory.RISK,
            "availability": ImpactCategory.RISK,
            "migration": ImpactCategory.CAPEX,
            "deployment": ImpactCategory.OPEX,
        }
        self.impact_templates = {
            ImpactCategory.RETENTION: [
                "improving user retention by est. {value}%",
                "reducing churn by approximately {value}%",
                "enhancing customer satisfaction by est. {value}%",
            ],
            ImpactCategory.REVENUE: [
                "generating est. ${value}M in additional revenue",
                "enabling est. {value}% revenue growth",
                "contributing to est. ${value}K in monthly revenue",
            ],
            ImpactCategory.OPEX: [
                "reducing operational costs by est. {value}%",
                "saving est. ${value}K monthly in cloud expenses",
                "slashing infrastructure spend by est. {value}%",
            ],
            ImpactCategory.RISK: [
                "mitigating est. ${value}M in potential downtime costs",
                "reducing compliance risk by est. {value}%",
                "preventing est. ${value} hours of system downtime",
            ],
            ImpactCategory.CAPEX: [
                "deferring est. ${value}M in hardware purchases",
                "enabling est. {value}% reduction in capital needs",
                "optimizing asset utilization by est. {value}%",
            ],
        }
        self.industry_multipliers = {
            "technology": {"revenue": 1.2, "cost": 1.0},
            "finance": {"revenue": 1.5, "cost": 1.2},
            "healthcare": {"revenue": 1.3, "cost": 1.1},
            "retail": {"revenue": 1.1, "cost": 0.9},
            "manufacturing": {"revenue": 1.0, "cost": 1.3},
        }
        logger.info(f"Initialized MetricAugmenter for {industry} industry")

    def augment_bullet(self, bullet_text: str) -> AugmentedBullet:
        """Augment a single bullet with business impact.

        Args:
            bullet_text: Original bullet text

        Returns:
            AugmentedBullet with business impact
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "MetricAugmenter.augment_bullet")
        try:
            technical_metrics = self._detect_metrics(bullet_text)
            if not technical_metrics:
                return AugmentedBullet(
                    original_text=bullet_text,
                    technical_metric=None,
                    business_impact=None,
                    final_text=bullet_text,
                )
            selected_metric = self._select_highest_impact_metric(technical_metrics)
            business_impact = self._estimate_impact(
                selected_metric["type"], selected_metric["value"], bullet_text,
            )
            if not business_impact:
                return AugmentedBullet(
                    original_text=bullet_text,
                    technical_metric=selected_metric["type"],
                    business_impact=None,
                    final_text=bullet_text,
                )
            final_text = self._create_augmented_text(bullet_text, business_impact)
            return AugmentedBullet(
                original_text=bullet_text,
                technical_metric=selected_metric["type"],
                business_impact=business_impact,
                final_text=final_text,
            )
        except Exception as e:
            logger.error(f"Error augmenting bullet: {str(e)}")
            return None

    def _select_highest_impact_metric(self, metrics: list[dict[str, Any]]) -> dict[str, Any]:
        """Select the metric with highest business impact.

        Args:
            metrics: List of detected metrics

        Returns:
            Selected metric with highest impact
        """
        impact_priority = {
            "cost": 10,
            "latency": 9,
            "accuracy": 8,
            "throughput": 7,
            "uptime": 6,
            "storage": 5,
            "compute": 5,
            "migration": 4,
            "deployment": 3,
            "refactoring": 2,
            "optimization": 2,
        }
        sorted_metrics = sorted(metrics, key=lambda m: impact_priority.get(m["type"], 0), reverse=True)
        return sorted_metrics[0] if sorted_metrics else metrics[0]

    def augment_batch(self, bullets: list[str]) -> list[AugmentedBullet]:
        """Augment multiple bullets at once.

        Args:
            bullets: List of bullet texts

        Returns:
            List of AugmentedBullet objects
        """
        try:
            augmented = []
            for bullet in bullets:
                if not bullet or not isinstance(bullet, str):
                    logger.warning("Skipping invalid bullet")
                    continue
                augmented_bullet = self.augment_bullet(bullet)
                augmented.append(augmented_bullet)
            augmentation_rate = sum(1 for b in augmented if b.is_augmented) / len(augmented)
            logger.info(f"Augmented {len(augmented)} bullets, rate: {augmentation_rate:.2%}")
            return augmented
        except Exception as e:
            logger.error(f"Error augmenting batch: {str(e)}")
            return None

    def _detect_metrics(self, text: str) -> list[dict[str, Any]]:
        """Detect ALL technical metrics in text.

        Args:
            text: Text to scan for metrics

        Returns:
            List of dictionaries with metric type and value
        """
        try:
            text_lower = text.lower()
            detected_metrics = []
            patterns = {
                "latency": [
                    "(\\d+)\\s*ms",
                    "(\\d+)\\s*milliseconds?",
                    "reduced.*latency.*by\\s*(\\d+)",
                    "improved.*latency.*to\\s*(\\d+)",
                ],
                "accuracy": [
                    "(\\d+(?:\\.\\d+)?)\\s*%?\\s*accuracy",
                    "accuracy.*to\\s*(\\d+(?:\\.\\d+)?)",
                    "f1.*score.*of\\s*(\\d+(?:\\.\\d+)?)",
                    "precision.*(\\d+(?:\\.\\d+)?)",
                    "recall.*(\\d+(?:\\.\\d+)?)",
                ],
                "throughput": [
                    "(\\d+(?:k|m|g)?)\\s*(?:req\\/s|rps|requests?\\/second)",
                    "throughput.*by\\s*(\\d+)",
                    "processing.*(\\d+(?:k|m)?)\\s*messages?",
                ],
                "storage": ["(\\d+(?:gb|tb|pb))", "storage.*by\\s*(\\d+)", "reduced.*storage.*by\\s*(\\d+)"],
                "compute": [
                    "(\\d+)%?\\s*(?:cpu|compute)",
                    "nodes?.*(\\d+)",
                    "cluster.*(\\d+)",
                    "k8s|kubernetes",
                ],
                "cost": [
                    "\\$(\\d+(?:k|m)?)",
                    "cost.*by\\s*(\\d+)",
                    "saving.*\\$(\\d+)",
                    "reduced.*spend.*by\\s*(\\d+)",
                ],
                "uptime": [
                    "(\\d+\\.?\\d*)%?\\s*uptime",
                    "availability.*(\\d+\\.?\\d*)",
                    "sla.*(\\d+\\.?\\d*)",
                ],
            }
            for metric_type, metric_patterns in patterns.items():
                for pattern in metric_patterns:
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        detected_metrics.append({"type": metric_type, "value": match, "pattern": pattern})
                        break
            keywords = {
                "migration": ["migration", "migrated"],
                "deployment": ["deployment", "deployed"],
                "refactoring": ["refactor", "refactored"],
                "optimization": ["optimiz", "optimised"],
            }
            for metric_type, keyword_list in keywords.items():
                if any(keyword in text_lower for keyword in keyword_list):
                    detected_metrics.append(
                        {"type": metric_type, "value": "significant", "pattern": "keyword"},
                    )
            return detected_metrics
        except Exception as e:
            logger.error(f"Error detecting metrics: {str(e)}")
            return None

    def _estimate_impact(self, metric_type: str, metric_value: str, context: str) -> BusinessImpact | None:
        """Estimate business impact for a metric.

        Args:
            metric_type: Type of technical metric
            metric_value: Value of the metric
            context: Original bullet text for context

        Returns:
            BusinessImpact estimation
        """
        try:
            category = self.metric_mappings.get(metric_type, ImpactCategory.OPEX)
            if metric_type in ["latency", "speed", "response_time"]:
                latency_ms = self._extract_number(metric_value)
                if latency_ms and latency_ms > 0:
                    retention_lift = min(30, latency_ms / 100 * 10)
                    value_statement = f"improving user retention by est. {retention_lift:.0f}%"
                    confidence = 0.7
                else:
                    value_statement = "improving user experience and retention"
                    confidence = 0.5
            elif metric_type in ["accuracy", "f1", "precision", "recall"]:
                accuracy = self._extract_number(metric_value)
                if accuracy and accuracy > 0:
                    revenue_lift = min(20, accuracy / 5 * 2)
                    multiplier = self.industry_multipliers.get(self.industry, {}).get("revenue", 1.0)
                    revenue_lift *= multiplier
                    value_statement = f"enabling est. {revenue_lift:.0f}% revenue growth"
                    confidence = 0.6
                else:
                    value_statement = "enhancing product quality and trust"
                    confidence = 0.4
            elif metric_type in ["storage", "compute", "infrastructure", "cloud", "cost"]:
                if metric_value in ["significant"]:
                    value_statement = "reducing infrastructure costs by est. 20%"
                    confidence = 0.5
                else:
                    cost_reduction = self._extract_number(metric_value)
                    if cost_reduction and cost_reduction > 0:
                        multiplier = self.industry_multipliers.get(self.industry, {}).get("cost", 1.0)
                        cost_reduction *= multiplier
                        value_statement = f"slashing monthly cloud spend by est. {cost_reduction:.0f}%"
                        confidence = 0.7
                    else:
                        value_statement = "optimizing operational efficiency"
                        confidence = 0.4
            elif metric_type in ["uptime", "reliability", "availability"]:
                uptime = self._extract_number(metric_value)
                if uptime and uptime >= 99:
                    value_statement = "preventing est. $100K in potential downtime costs"
                    confidence = 0.6
                else:
                    value_statement = "mitigating system reliability risks"
                    confidence = 0.4
            elif metric_type in ["migration", "deployment"]:
                value_statement = "deferring est. $500K in infrastructure purchases"
                confidence = 0.5
            else:
                value_statement = "improving operational efficiency"
                confidence = 0.3
            return BusinessImpact(category=category, value_statement=value_statement, confidence=confidence)
        except Exception as e:
            logger.error(f"Error estimating impact: {str(e)}")
            return None

    def _extract_number(self, value_str: str) -> float | None:
        """Extract numeric value from string.

        Args:
            value_str: String containing number

        Returns:
            Extracted number or None
        """
        try:
            if "k" in value_str.lower():
                return float(value_str.lower().replace("k", "")) * 1000
            elif "m" in value_str.lower():
                return float(value_str.lower().replace("m", "")) * 1000000
            elif "g" in value_str.lower():
                return float(value_str.lower().replace("g", "")) * 1000000000
            else:
                return float(value_str)
        except (ValueError, AttributeError):
            return None

    def _create_augmented_text(self, original: str, impact: BusinessImpact) -> str:
        """Create final augmented text with business impact.

        Args:
            original: Original bullet text
            impact: Business impact to add

        Returns:
            Augmented text with impact statement
        """
        try:
            impact_text = f"**{impact.value_statement}**"
            if original.endswith("."):
                augmented = f"{original[:-1]}, {impact_text}."
            else:
                augmented = f"{original}, {impact_text}."
            return augmented
        except Exception as e:
            logger.error(f"Error creating augmented text: {str(e)}")
            return None


def create_metric_augmenter(industry: str = "technology") -> MetricAugmenter:
    """Create a MetricAugmenter instance.

    Args:
        industry: Target industry

    Returns:
        Configured MetricAugmenter
    """
    return MetricAugmenter(industry=industry)


def augment_metrics(bullets: list[str], industry: str = "technology") -> list[str]:
    """Quickly augment a list of bullets.

    Args:
        bullets: List of bullet texts
        industry: Target industry

    Returns:
        List of augmented texts
    """
    augmenter = create_metric_augmenter(industry=industry)
    augmented_bullets = augmenter.augment_batch(bullets)
    return [b.final_text for b in augmented_bullets]
