"""
L2 Feature Extractor

Extracts features for L2 healer selection model including
healer type compatibility, success probability, resource requirements,
escalation history, healing complexity, and availability metrics.
"""

import math
from datetime import datetime
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class L2FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L2 healer selection.

    Extracts deterministic features for healer selection:
    - Healer type compatibility and specialization
    - Historical success rates and performance metrics
    - Resource requirements and availability
    - Escalation history and patterns
    - Healing complexity and severity assessment
    - System state and context factors
    - Retry probability and rollback likelihood
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l2_healer_selector")
        if not schema:
            # Create schema for L2 healer selector
            schema = self._create_l2_schema()
        super().__init__(schema)

    def _create_l2_schema(self) -> FeatureSchema:
        """Create feature schema for L2 healer selector."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="healer_compatibility_score",
                feature_type=FeatureType.NUMERIC,
                description="Compatibility score of healer with error type",
                provenance="healer.compatibility.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="historical_success_rate",
                feature_type=FeatureType.NUMERIC,
                description="Historical success rate for this healer",
                provenance="healer.history.success_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="resource_availability",
                feature_type=FeatureType.NUMERIC,
                description="Resource availability for healer execution",
                provenance="healer.resources.availability",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="error_severity_score",
                feature_type=FeatureType.NUMERIC,
                description="Severity score of the error to be healed",
                provenance="error.severity.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="healing_complexity",
                feature_type=FeatureType.NUMERIC,
                description="Complexity of the healing operation",
                provenance="healing.operation.complexity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="escalation_history",
                feature_type=FeatureType.NUMERIC,
                description="Historical escalation patterns for similar errors",
                provenance="history.escalation.pattern_score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="retry_probability",
                feature_type=FeatureType.NUMERIC,
                description="Probability that retry will be needed",
                provenance="healing.retry.probability",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="rollback_likelihood",
                feature_type=FeatureType.NUMERIC,
                description="Likelihood that rollback will be required",
                provenance="healing.rollback.likelihood",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="system_load_factor",
                feature_type=FeatureType.NUMERIC,
                description="Current system load affecting healing",
                provenance="system.load.factor",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="time_sensitivity",
                feature_type=FeatureType.NUMERIC,
                description="Time sensitivity of the healing operation",
                provenance="healing.time.sensitivity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
        ]

        return FeatureSchema(
            schema_name="l2_healer_selector",
            schema_version="1.0",
            description="Features for L2 healer selection model",
            features=features,
        )

    def _register_extraction_functions(self) -> None:
        """Register L2-specific feature extraction functions."""
        self.register_extraction_function(
            "healer_compatibility_score", self._extract_healer_compatibility_score
        )
        self.register_extraction_function("historical_success_rate", self._extract_historical_success_rate)
        self.register_extraction_function("resource_availability", self._extract_resource_availability)
        self.register_extraction_function("error_severity_score", self._extract_error_severity_score)
        self.register_extraction_function("healing_complexity", self._extract_healing_complexity)
        self.register_extraction_function("escalation_history", self._extract_escalation_history)
        self.register_extraction_function("retry_probability", self._extract_retry_probability)
        self.register_extraction_function("rollback_likelihood", self._extract_rollback_likelihood)
        self.register_extraction_function("system_load_factor", self._extract_system_load_factor)
        self.register_extraction_function("time_sensitivity", self._extract_time_sensitivity)

    def _extract_healer_compatibility_score(self, context: dict[str, Any]) -> float:
        """Extract healer compatibility score (0.0-1.0)."""
        healer = context.get("healer", {})
        error = context.get("error", {})

        # Direct compatibility score if provided
        if "compatibility_score" in healer:
            return float(healer["compatibility_score"])

        # Calculate from healer specialization and error type
        healer_specialization = healer.get("specialization", [])
        error_type = error.get("type", "")
        error_category = error.get("category", "")

        # Base compatibility from specialization match
        compatibility_score = 0.0

        # Direct type match
        if error_type in healer_specialization:
            compatibility_score += 0.6

        # Category match
        if error_category in healer_specialization:
            compatibility_score += 0.4

        # Partial matches (substrings)
        for spec in healer_specialization:
            if spec.lower() in error_type.lower() or spec.lower() in error_category.lower():
                compatibility_score += 0.2

        # Healer capabilities match
        healer_capabilities = healer.get("capabilities", [])
        error_requirements = error.get("requirements", [])

        capability_matches = 0
        for requirement in error_requirements:
            if requirement in healer_capabilities:
                capability_matches += 1

        if error_requirements:
            capability_score = capability_matches / len(error_requirements)
            compatibility_score += capability_score * 0.3

        # Healer experience level
        experience_level = healer.get("experience_level", "junior")
        experience_scores = {"junior": 0.7, "mid": 0.85, "senior": 0.95, "expert": 1.0}
        experience_multiplier = experience_scores.get(experience_level, 0.7)

        compatibility_score *= experience_multiplier

        return round(min(1.0, compatibility_score), 3)

    def _extract_historical_success_rate(self, context: dict[str, Any]) -> float:
        """Extract historical success rate (0.0-1.0)."""
        healer = context.get("healer", {})

        # Direct success rate if provided
        if "historical_success_rate" in healer:
            return float(healer["historical_success_rate"])

        # Calculate from healing history
        healing_history = healer.get("healing_history", [])

        if not healing_history:
            return 0.5  # Default if no history

        successful_healings = sum(1 for healing in healing_history if healing.get("success", False))
        total_healings = len(healing_history)

        success_rate = successful_healings / total_healings

        # Weight recent healings more heavily
        now = datetime.now()
        weighted_success = 0.0
        total_weight = 0.0

        for healing in healing_history:
            healing_date = healing.get("timestamp")
            if healing_date:
                if isinstance(healing_date, str):
                    try:
                        healing_time = datetime.fromisoformat(healing_date.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                else:
                    healing_time = healing_date

                # Calculate weight (more recent = higher weight)
                days_ago = (now - healing_time).days
                weight = math.exp(-days_ago / 30.0)  # 30-day half-life

                if healing.get("success", False):
                    weighted_success += weight

                total_weight += weight

        if total_weight > 0:
            weighted_success_rate = weighted_success / total_weight
            # Blend simple and weighted rates
            final_rate = (success_rate * 0.3) + (weighted_success_rate * 0.7)
        else:
            final_rate = success_rate

        return round(final_rate, 3)

    def _extract_resource_availability(self, context: dict[str, Any]) -> float:
        """Extract resource availability (0.0-1.0)."""
        healer = context.get("healer", {})
        system_resources = context.get("system_resources", {})

        # Direct availability if provided
        if "resource_availability" in healer:
            return float(healer["resource_availability"])

        # Calculate from healer resource requirements and system availability
        required_resources = healer.get("required_resources", {})

        if not required_resources:
            return 0.9  # High availability if no special requirements

        availability_scores = []

        for resource, amount in required_resources.items():
            available = system_resources.get(resource, 0)

            if available > 0:
                availability_ratio = min(1.0, available / amount)
                availability_scores.append(availability_ratio)
            else:
                availability_scores.append(0.0)  # No availability

        if availability_scores:
            # Use minimum availability (bottleneck resource)
            overall_availability = min(availability_scores)
        else:
            overall_availability = 0.9

        # Adjust for healer current load
        current_load = healer.get("current_load", 0)
        max_capacity = healer.get("max_capacity", 10)

        if max_capacity > 0:
            load_factor = 1.0 - (current_load / max_capacity)
            overall_availability *= load_factor

        return round(max(0.0, min(1.0, overall_availability)), 3)

    def _extract_error_severity_score(self, context: dict[str, Any]) -> float:
        """Extract error severity score (0.0-1.0)."""
        error = context.get("error", {})

        # Direct severity score if provided
        if "severity_score" in error:
            return float(error["severity_score"])

        # Calculate from error characteristics
        severity_indicators = {
            "error_type": 0.3,
            "impact_scope": 0.25,
            "user_impact": 0.2,
            "system_impact": 0.15,
            "data_impact": 0.1,
        }

        score = 0.0

        # Error type contribution
        error_type = error.get("type", "").lower()
        high_severity_types = ["critical", "fatal", "security", "data_loss", "corruption"]
        medium_severity_types = ["error", "exception", "timeout", "connection"]

        if any(hs_type in error_type for hs_type in high_severity_types):
            score += severity_indicators["error_type"]
        elif any(ms_type in error_type for ms_type in medium_severity_types):
            score += severity_indicators["error_type"] * 0.6
        else:
            score += severity_indicators["error_type"] * 0.3

        # Impact scope contribution
        impact_scope = error.get("impact_scope", "local")
        scope_scores = {"local": 0.2, "service": 0.5, "system": 0.8, "global": 1.0}
        score += severity_indicators["impact_scope"] * scope_scores.get(impact_scope, 0.2)

        # User impact contribution
        user_impact = error.get("user_impact", "low")
        user_scores = {"low": 0.1, "medium": 0.4, "high": 0.7, "critical": 1.0}
        score += severity_indicators["user_impact"] * user_scores.get(user_impact, 0.1)

        # System impact contribution
        system_impact = error.get("system_impact", "low")
        system_scores = {"low": 0.1, "medium": 0.4, "high": 0.7, "critical": 1.0}
        score += severity_indicators["system_impact"] * system_scores.get(system_impact, 0.1)

        # Data impact contribution
        data_impact = error.get("data_impact", "none")
        data_scores = {"none": 0.0, "read": 0.2, "write": 0.5, "corruption": 0.8, "loss": 1.0}
        score += severity_indicators["data_impact"] * data_scores.get(data_impact, 0.0)

        return round(min(1.0, score), 3)

    def _extract_healing_complexity(self, context: dict[str, Any]) -> float:
        """Extract healing complexity (0.0-1.0)."""
        error = context.get("error", {})
        healing_context = context.get("healing_context", {})

        # Direct complexity if provided
        if "healing_complexity" in healing_context:
            return float(healing_context["healing_complexity"])

        # Calculate from healing requirements
        complexity_indicators = {
            "steps_required": 0.3,
            "dependencies": 0.2,
            "rollback_complexity": 0.2,
            "data_recovery": 0.15,
            "coordination": 0.15,
        }

        score = 0.0

        # Steps required contribution
        healing_steps = healing_context.get("required_steps", [])
        if healing_steps:
            steps_score = min(1.0, len(healing_steps) / 10.0)  # Normalize to 10 steps
            score += complexity_indicators["steps_required"] * steps_score

        # Dependencies contribution
        dependencies = healing_context.get("dependencies", [])
        if dependencies:
            dependency_score = min(1.0, len(dependencies) / 8.0)  # Normalize to 8 dependencies
            score += complexity_indicators["dependencies"] * dependency_score

        # Rollback complexity contribution
        rollback_requirements = healing_context.get("rollback_requirements", {})
        if rollback_requirements:
            rollback_score = 0.5  # Base score for having rollback
            if rollback_requirements.get("complex_rollback", False):
                rollback_score = 1.0
            score += complexity_indicators["rollback_complexity"] * rollback_score

        # Data recovery contribution
        data_recovery = healing_context.get("data_recovery", {})
        if data_recovery:
            recovery_score = 0.3  # Base score for data recovery
            if data_recovery.get("requires_point_in_time", False):
                recovery_score += 0.4
            if data_recovery.get("large_volume", False):
                recovery_score += 0.3
            score += complexity_indicators["data_recovery"] * min(1.0, recovery_score)

        # Coordination contribution
        coordination = healing_context.get("coordination_requirements", [])
        if coordination:
            coordination_score = min(1.0, len(coordination) / 5.0)  # Normalize to 5 coordination points
            score += complexity_indicators["coordination"] * coordination_score

        return round(min(1.0, score), 3)

    def _extract_escalation_history(self, context: dict[str, Any]) -> float:
        """Extract escalation history pattern score (0.0-1.0)."""
        error = context.get("error", {})
        history = context.get("history", {})

        # Direct pattern score if provided
        if "escalation_pattern_score" in history:
            return float(history["escalation_pattern_score"])

        # Calculate from escalation history
        escalation_history = history.get("escalations", [])

        if not escalation_history:
            return 0.1  # Low escalation history if none

        # Look for similar error escalations
        error_type = error.get("type", "")
        error_category = error.get("category", "")

        similar_escalations = 0
        total_escalations = len(escalation_history)

        for escalation in escalation_history:
            esc_error_type = escalation.get("error_type", "")
            esc_error_category = escalation.get("error_category", "")

            if (
                esc_error_type == error_type
                or esc_error_category == error_category
                or error_type in esc_error_type
                or esc_error_type in error_type
            ):
                similar_escalations += 1

        # Calculate escalation frequency
        if total_escalations > 0:
            escalation_frequency = similar_escalations / total_escalations
        else:
            escalation_frequency = 0.0

        # Calculate escalation recency
        now = datetime.now()
        recent_escalations = 0

        for escalation in escalation_history:
            esc_date = escalation.get("timestamp")
            if esc_date:
                if isinstance(esc_date, str):
                    try:
                        esc_time = datetime.fromisoformat(esc_date.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                else:
                    esc_time = esc_date

                # Count escalations in last 30 days
                if (now - esc_time).days <= 30:
                    recent_escalations += 1

        recency_score = min(1.0, recent_escalations / 5.0)  # Normalize to 5 escalations

        # Combine frequency and recency
        pattern_score = (escalation_frequency * 0.6) + (recency_score * 0.4)

        return round(pattern_score, 3)

    def _extract_retry_probability(self, context: dict[str, Any]) -> float:
        """Extract retry probability (0.0-1.0)."""
        error = context.get("error", {})
        healing_context = context.get("healing_context", {})

        # Direct probability if provided
        if "retry_probability" in healing_context:
            return float(healing_context["retry_probability"])

        # Calculate from error characteristics and healing history
        base_probability = 0.3  # Base retry probability

        # Adjust based on error type
        error_type = error.get("type", "").lower()
        retryable_types = ["timeout", "connection", "network", "temporary", "transient"]
        non_retryable_types = ["fatal", "critical", "security", "authentication", "authorization"]

        if any(rt_type in error_type for rt_type in retryable_types):
            base_probability += 0.4
        elif any(nrt_type in error_type for nrt_type in non_retryable_types):
            base_probability -= 0.2

        # Adjust based on healing history
        history = context.get("history", {})
        similar_errors = history.get("similar_errors", [])

        if similar_errors:
            retry_attempts = sum(error.get("retry_attempts", 0) for error in similar_errors)
            successful_retries = sum(error.get("successful_retries", 0) for error in similar_errors)

            if retry_attempts > 0:
                retry_success_rate = successful_retries / retry_attempts
                base_probability *= 0.5 + retry_success_rate * 0.5  # Scale based on success rate

        # Adjust based on system state
        system_state = context.get("system_state", {})
        system_stability = system_state.get("stability", "stable")

        stability_multipliers = {"stable": 1.0, "unstable": 1.3, "degraded": 1.5, "critical": 2.0}
        stability_multiplier = stability_multipliers.get(system_stability, 1.0)

        base_probability *= stability_multiplier

        return round(max(0.0, min(1.0, base_probability)), 3)

    def _extract_rollback_likelihood(self, context: dict[str, Any]) -> float:
        """Extract rollback likelihood (0.0-1.0)."""
        healing_context = context.get("healing_context", {})
        history = context.get("history", {})

        # Direct likelihood if provided
        if "rollback_likelihood" in healing_context:
            return float(healing_context["rollback_likelihood"])

        # Calculate from healing complexity and history
        base_likelihood = 0.2  # Base rollback likelihood

        # Adjust based on healing complexity
        healing_complexity = self._extract_healing_complexity(context)
        base_likelihood += healing_complexity * 0.4

        # Adjust based on rollback history
        rollback_history = history.get("rollbacks", [])

        if rollback_history:
            rollback_rate = len(rollback_history) / max(1, history.get("total_healings", 1))
            base_likelihood += rollback_rate * 0.3

        # Adjust based on data impact
        error = context.get("error", {})
        data_impact = error.get("data_impact", "none")

        if data_impact in ["corruption", "loss"]:
            base_likelihood += 0.3
        elif data_impact in ["write"]:
            base_likelihood += 0.1

        return round(max(0.0, min(1.0, base_likelihood)), 3)

    def _extract_system_load_factor(self, context: dict[str, Any]) -> float:
        """Extract system load factor (0.0-1.0)."""
        system_state = context.get("system_state", {})

        # Direct load factor if provided
        if "load_factor" in system_state:
            return float(system_state["load_factor"])

        # Calculate from system metrics
        cpu_utilization = system_state.get("cpu_utilization", 0.0)
        memory_utilization = system_state.get("memory_utilization", 0.0)
        active_requests = system_state.get("active_requests", 0)
        max_requests = system_state.get("max_requests", 100)

        # Calculate individual load factors
        cpu_load = min(1.0, cpu_utilization / 100.0)
        memory_load = min(1.0, memory_utilization / 100.0)
        request_load = min(1.0, active_requests / max_requests) if max_requests > 0 else 0.0

        # Weighted average
        overall_load = (cpu_load * 0.4) + (memory_load * 0.3) + (request_load * 0.3)

        return round(overall_load, 3)

    def _extract_time_sensitivity(self, context: dict[str, Any]) -> float:
        """Extract time sensitivity (0.0-1.0)."""
        error = context.get("error", {})
        healing_context = context.get("healing_context", {})

        # Direct sensitivity if provided
        if "time_sensitivity" in healing_context:
            return float(healing_context["time_sensitivity"])

        # Calculate from timing constraints
        sensitivity_score = 0.0

        # SLA impact
        sla_impact = error.get("sla_impact", "low")
        sla_scores = {"low": 0.1, "medium": 0.4, "high": 0.7, "critical": 1.0}
        sensitivity_score += sla_scores.get(sla_impact, 0.1)

        # User impact timing
        user_impact = error.get("user_impact", "low")
        if user_impact in ["high", "critical"]:
            sensitivity_score += 0.3

        # Business hours consideration
        now = datetime.now()
        business_hours = healing_context.get("business_hours", {})

        if business_hours:
            is_business_hours = business_hours.get("is_business_hours", True)
            if not is_business_hours:
                sensitivity_score += 0.2  # Higher sensitivity outside business hours

        # Deadline proximity
        deadline = healing_context.get("deadline")
        if deadline:
            try:
                if isinstance(deadline, str):
                    deadline_time = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                else:
                    deadline_time = deadline

                time_to_deadline = (deadline_time - now).total_seconds()

                if time_to_deadline < 0:
                    sensitivity_score += 0.5  # Past deadline
                elif time_to_deadline < 3600:  # Less than 1 hour
                    sensitivity_score += 0.4
                elif time_to_deadline < 86400:  # Less than 1 day
                    sensitivity_score += 0.2
            except ValueError:
                pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow

        return round(min(1.0, sensitivity_score), 3)
