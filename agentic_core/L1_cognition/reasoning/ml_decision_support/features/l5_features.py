"""
L5 Feature Extractor

Extracts features for L5 risk calibration model including
policy complexity, compliance risk, false positive/negative rates,
business impact, stakeholder criticality, and audit requirements.
"""

from datetime import datetime, timedelta
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class L5FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L5 risk calibration.

    Extracts deterministic features for risk calibration:
    - Policy complexity and structure metrics
    - Compliance and regulatory risk indicators
    - False positive/negative historical rates
    - Business impact and criticality assessments
    - Stakeholder and governance considerations
    - Audit and monitoring requirements
    - Risk mitigation and control effectiveness
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l5_risk_calibrator")
        if not schema:
            # Create schema for L5 risk calibrator
            schema = self._create_l5_schema()
        super().__init__(schema)

    def _create_l5_schema(self) -> FeatureSchema:
        """Create feature schema for L5 risk calibrator."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="policy_complexity_score",
                feature_type=FeatureType.NUMERIC,
                description="Complexity score of policy being evaluated",
                provenance="policy.complexity.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="compliance_risk_level",
                feature_type=FeatureType.NUMERIC,
                description="Compliance and regulatory risk level",
                provenance="policy.compliance.risk_level",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="historical_false_positive_rate",
                feature_type=FeatureType.NUMERIC,
                description="Historical false positive rate for similar policies",
                provenance="history.metrics.false_positive_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="historical_false_negative_rate",
                feature_type=FeatureType.NUMERIC,
                description="Historical false negative rate for similar policies",
                provenance="history.metrics.false_negative_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="business_impact_score",
                feature_type=FeatureType.NUMERIC,
                description="Business impact score of policy decision",
                provenance="policy.business.impact_score",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="stakeholder_criticality",
                feature_type=FeatureType.NUMERIC,
                description="Criticality of affected stakeholders",
                provenance="policy.stakeholders.criticality",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="audit_requirement_level",
                feature_type=FeatureType.NUMERIC,
                description="Level of audit and monitoring requirements",
                provenance="policy.audit.requirement_level",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="risk_mitigation_effectiveness",
                feature_type=FeatureType.NUMERIC,
                description="Effectiveness of existing risk mitigations",
                provenance="policy.mitigation.effectiveness",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="regulatory_change_frequency",
                feature_type=FeatureType.NUMERIC,
                description="Frequency of regulatory changes in this domain",
                provenance="environment.regulatory.change_frequency",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="precedent_strength",
                feature_type=FeatureType.NUMERIC,
                description="Strength of existing precedents for this policy type",
                provenance="policy.precedent.strength",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="l5_risk_calibrator",
            schema_version="1.0",
            description="Features for L5 risk calibration model",
            features=features
        )

    def _register_extraction_functions(self) -> None:
        """Register L5-specific feature extraction functions."""
        self.register_extraction_function("policy_complexity_score", self._extract_policy_complexity_score)
        self.register_extraction_function("compliance_risk_level", self._extract_compliance_risk_level)
        self.register_extraction_function("historical_false_positive_rate", self._extract_historical_false_positive_rate)
        self.register_extraction_function("historical_false_negative_rate", self._extract_historical_false_negative_rate)
        self.register_extraction_function("business_impact_score", self._extract_business_impact_score)
        self.register_extraction_function("stakeholder_criticality", self._extract_stakeholder_criticality)
        self.register_extraction_function("audit_requirement_level", self._extract_audit_requirement_level)
        self.register_extraction_function("risk_mitigation_effectiveness", self._extract_risk_mitigation_effectiveness)
        self.register_extraction_function("regulatory_change_frequency", self._extract_regulatory_change_frequency)
        self.register_extraction_function("precedent_strength", self._extract_precedent_strength)

    def _extract_policy_complexity_score(self, context: dict[str, Any]) -> float:
        """Extract policy complexity score (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct complexity score if provided
        if "complexity_score" in policy:
            return float(policy["complexity_score"])

        # Calculate from policy characteristics
        complexity_indicators = {
            "rule_count": 0.25,
            "conditional_logic": 0.2,
            "exception_handling": 0.15,
            "cross_dependencies": 0.2,
            "temporal_constraints": 0.1,
            "stakeholder_count": 0.1
        }

        score = 0.0

        # Rule count contribution
        rules = policy.get("rules", [])
        if rules:
            rule_score = min(1.0, len(rules) / 50.0)  # Normalize to 50 rules
            score += complexity_indicators["rule_count"] * rule_score

        # Conditional logic contribution
        conditional_rules = [rule for rule in rules if "if" in rule.get("condition", "").lower()]
        if conditional_rules:
            conditional_score = min(1.0, len(conditional_rules) / 20.0)  # Normalize to 20 conditionals
            score += complexity_indicators["conditional_logic"] * conditional_score

        # Exception handling contribution
        exceptions = policy.get("exceptions", [])
        if exceptions:
            exception_score = min(1.0, len(exceptions) / 15.0)  # Normalize to 15 exceptions
            score += complexity_indicators["exception_handling"] * exception_score

        # Cross-dependencies contribution
        dependencies = policy.get("cross_dependencies", [])
        if dependencies:
            dependency_score = min(1.0, len(dependencies) / 10.0)  # Normalize to 10 dependencies
            score += complexity_indicators["cross_dependencies"] * dependency_score

        # Temporal constraints contribution
        temporal_constraints = policy.get("temporal_constraints", [])
        if temporal_constraints:
            temporal_score = min(1.0, len(temporal_constraints) / 8.0)  # Normalize to 8 constraints
            score += complexity_indicators["temporal_constraints"] * temporal_score

        # Stakeholder count contribution
        stakeholders = policy.get("stakeholders", [])
        if stakeholders:
            stakeholder_score = min(1.0, len(stakeholders) / 25.0)  # Normalize to 25 stakeholders
            score += complexity_indicators["stakeholder_count"] * stakeholder_score

        return round(min(1.0, score), 3)

    def _extract_compliance_risk_level(self, context: dict[str, Any]) -> float:
        """Extract compliance risk level (0.0-1.0)."""
        policy = context.get("policy", {})
        regulations = context.get("regulations", {})

        # Direct risk level if provided
        if "compliance_risk_level" in policy:
            return float(policy["compliance_risk_level"])

        # Calculate from compliance factors
        risk_indicators = {
            "regulatory_coverage": 0.3,
            "violation_severity": 0.25,
            "audit_frequency": 0.2,
            "reporting_complexity": 0.15,
            "change_management": 0.1
        }

        score = 0.0

        # Regulatory coverage contribution
        applicable_regulations = policy.get("applicable_regulations", [])
        if applicable_regulations:
            # Check coverage against known regulations
            coverage_count = 0
            for reg in applicable_regulations:
                if reg in regulations:
                    coverage_count += 1

            coverage_ratio = coverage_count / len(applicable_regulations) if applicable_regulations else 0
            # Higher coverage = higher risk (more regulations to comply with)
            score += risk_indicators["regulatory_coverage"] * coverage_ratio

        # Violation severity contribution
        violation_penalties = policy.get("violation_penalties", [])
        if violation_penalties:
            max_penalty = max(penalty.get("severity", 0) for penalty in violation_penalties)
            penalty_score = min(1.0, max_penalty / 10.0)  # Normalize to severity 1-10
            score += risk_indicators["violation_severity"] * penalty_score

        # Audit frequency contribution
        audit_requirements = policy.get("audit_requirements", {})
        audit_frequency = audit_requirements.get("frequency", "annual")
        frequency_scores = {"monthly": 1.0, "quarterly": 0.8, "semiannual": 0.6, "annual": 0.4, "biennial": 0.2}
        audit_score = frequency_scores.get(audit_frequency, 0.4)
        score += risk_indicators["audit_frequency"] * audit_score

        # Reporting complexity contribution
        reporting_requirements = policy.get("reporting_requirements", [])
        if reporting_requirements:
            reporting_score = min(1.0, len(reporting_requirements) / 12.0)  # Normalize to 12 reports
            score += risk_indicators["reporting_complexity"] * reporting_score

        # Change management contribution
        change_management = policy.get("change_management", {})
        if change_management:
            change_complexity = change_management.get("complexity", "low")
            complexity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
            change_score = complexity_scores.get(change_complexity, 0.2)
            score += risk_indicators["change_management"] * change_score

        return round(min(1.0, score), 3)

    def _extract_historical_false_positive_rate(self, context: dict[str, Any]) -> float:
        """Extract historical false positive rate (0.0-1.0)."""
        policy = context.get("policy", {})
        history = context.get("history", {})

        # Direct rate if provided
        if "historical_false_positive_rate" in policy:
            return float(policy["historical_false_positive_rate"])

        # Calculate from historical decisions
        similar_policies = history.get("similar_policies", [])
        if similar_policies:
            total_decisions = 0
            false_positives = 0

            for similar_policy in similar_policies:
                decisions = similar_policy.get("decisions", [])
                for decision in decisions:
                    total_decisions += 1
                    if decision.get("predicted_violation", False) and not decision.get("actual_violation", False):
                        false_positives += 1

            if total_decisions > 0:
                fp_rate = false_positives / total_decisions
                return round(fp_rate, 3)

        return 0.1  # Default conservative estimate

    def _extract_historical_false_negative_rate(self, context: dict[str, Any]) -> float:
        """Extract historical false negative rate (0.0-1.0)."""
        policy = context.get("policy", {})
        history = context.get("history", {})

        # Direct rate if provided
        if "historical_false_negative_rate" in policy:
            return float(policy["historical_false_negative_rate"])

        # Calculate from historical decisions
        similar_policies = history.get("similar_policies", [])
        if similar_policies:
            total_decisions = 0
            false_negatives = 0

            for similar_policy in similar_policies:
                decisions = similar_policy.get("decisions", [])
                for decision in decisions:
                    total_decisions += 1
                    if not decision.get("predicted_violation", False) and decision.get("actual_violation", False):
                        false_negatives += 1

            if total_decisions > 0:
                fn_rate = false_negatives / total_decisions
                return round(fn_rate, 3)

        return 0.05  # Default conservative estimate

    def _extract_business_impact_score(self, context: dict[str, Any]) -> float:
        """Extract business impact score (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct impact score if provided
        if "business_impact_score" in policy:
            return float(policy["business_impact_score"])

        # Calculate from business impact factors
        impact_indicators = {
            "financial_impact": 0.3,
            "operational_impact": 0.25,
            "reputational_impact": 0.2,
            "customer_impact": 0.15,
            "strategic_impact": 0.1
        }

        score = 0.0

        # Financial impact contribution
        financial_impact = policy.get("financial_impact", {})
        if financial_impact:
            impact_amount = financial_impact.get("amount", 0)
            # Normalize to $1M as maximum
            financial_score = min(1.0, abs(impact_amount) / 1000000.0)
            score += impact_indicators["financial_impact"] * financial_score

        # Operational impact contribution
        operational_impact = policy.get("operational_impact", "low")
        impact_scores = {"low": 0.1, "medium": 0.4, "high": 0.7, "critical": 1.0}
        operational_score = impact_scores.get(operational_impact, 0.1)
        score += impact_indicators["operational_impact"] * operational_score

        # Reputational impact contribution
        reputational_impact = policy.get("reputational_impact", "low")
        reputational_score = impact_scores.get(reputational_impact, 0.1)
        score += impact_indicators["reputational_impact"] * reputational_score

        # Customer impact contribution
        customer_impact = policy.get("customer_impact", {})
        if customer_impact:
            affected_customers = customer_impact.get("affected_customers", 0)
            total_customers = customer_impact.get("total_customers", 1000)
            customer_ratio = affected_customers / max(1, total_customers)
            customer_score = min(1.0, customer_ratio)
            score += impact_indicators["customer_impact"] * customer_score

        # Strategic impact contribution
        strategic_impact = policy.get("strategic_impact", "low")
        strategic_score = impact_scores.get(strategic_impact, 0.1)
        score += impact_indicators["strategic_impact"] * strategic_score

        return round(min(1.0, score), 3)

    def _extract_stakeholder_criticality(self, context: dict[str, Any]) -> float:
        """Extract stakeholder criticality (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct criticality if provided
        if "stakeholder_criticality" in policy:
            return float(policy["stakeholder_criticality"])

        # Calculate from stakeholder information
        stakeholders = policy.get("stakeholders", [])

        if not stakeholders:
            return 0.1  # Low criticality if no stakeholders

        # Stakeholder criticality levels
        criticality_levels = {
            "employee": 0.3,
            "customer": 0.5,
            "partner": 0.4,
            "regulator": 0.8,
            "investor": 0.7,
            "executive": 0.9,
            "board": 1.0
        }

        total_criticality = 0.0
        for stakeholder in stakeholders:
            stakeholder_type = stakeholder.get("type", "employee")
            influence = stakeholder.get("influence", "medium")

            base_criticality = criticality_levels.get(stakeholder_type, 0.3)

            # Adjust for influence level
            influence_multipliers = {"low": 0.7, "medium": 1.0, "high": 1.3, "critical": 1.5}
            influence_multiplier = influence_multipliers.get(influence, 1.0)

            total_criticality += base_criticality * influence_multiplier

        # Normalize by number of stakeholders
        average_criticality = total_criticality / len(stakeholders)

        return round(min(1.0, average_criticality), 3)

    def _extract_audit_requirement_level(self, context: dict[str, Any]) -> float:
        """Extract audit requirement level (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct requirement level if provided
        if "audit_requirement_level" in policy:
            return float(policy["audit_requirement_level"])

        # Calculate from audit requirements
        audit_requirements = policy.get("audit_requirements", {})

        if not audit_requirements:
            return 0.1  # Low requirements if none specified

        requirement_score = 0.0

        # Audit frequency contribution
        frequency = audit_requirements.get("frequency", "annual")
        frequency_scores = {"monthly": 1.0, "quarterly": 0.8, "semiannual": 0.6, "annual": 0.4, "biennial": 0.2}
        requirement_score += frequency_scores.get(frequency, 0.4) * 0.3

        # Audit scope contribution
        scope = audit_requirements.get("scope", "limited")
        scope_scores = {"limited": 0.2, "standard": 0.5, "comprehensive": 0.8, "full": 1.0}
        requirement_score += scope_scores.get(scope, 0.2) * 0.3

        # External audit requirement
        external_audit = audit_requirements.get("external_required", False)
        if external_audit:
            requirement_score += 0.2
        else:
            requirement_score += 0.05

        # Documentation requirements
        documentation = audit_requirements.get("documentation", [])
        if documentation:
            doc_score = min(1.0, len(documentation) / 10.0)  # Normalize to 10 documents
            requirement_score += doc_score * 0.2

        return round(min(1.0, requirement_score), 3)

    def _extract_risk_mitigation_effectiveness(self, context: dict[str, Any]) -> float:
        """Extract risk mitigation effectiveness (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct effectiveness if provided
        if "risk_mitigation_effectiveness" in policy:
            return float(policy["risk_mitigation_effectiveness"])

        # Calculate from mitigation measures
        mitigations = policy.get("risk_mitigations", [])

        if not mitigations:
            return 0.3  # Low effectiveness if no mitigations

        total_effectiveness = 0.0
        for mitigation in mitigations:
            effectiveness = mitigation.get("effectiveness", "medium")
            implementation = mitigation.get("implementation", "partial")

            # Effectiveness scores
            effectiveness_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "complete": 1.0}
            base_effectiveness = effectiveness_scores.get(effectiveness, 0.5)

            # Implementation multipliers
            implementation_multipliers = {"none": 0.0, "partial": 0.6, "full": 1.0}
            implementation_multiplier = implementation_multipliers.get(implementation, 0.6)

            total_effectiveness += base_effectiveness * implementation_multiplier

        # Average effectiveness across all mitigations
        average_effectiveness = total_effectiveness / len(mitigations)

        return round(min(1.0, average_effectiveness), 3)

    def _extract_regulatory_change_frequency(self, context: dict[str, Any]) -> float:
        """Extract regulatory change frequency (0.0-1.0)."""
        environment = context.get("environment", {})

        # Direct frequency if provided
        if "regulatory_change_frequency" in environment:
            return float(environment["regulatory_change_frequency"])

        # Calculate from regulatory history
        regulatory_history = environment.get("regulatory_history", [])

        if not regulatory_history:
            return 0.1  # Low frequency if no history

        # Count changes in last 12 months
        now = datetime.now()
        twelve_months_ago = now - timedelta(days=365)

        recent_changes = [
            change for change in regulatory_history
            if change.get("effective_date")
            and isinstance(change["effective_date"], str)
            and datetime.fromisoformat(change["effective_date"].replace('Z', '+00:00')) > twelve_months_ago
        ]

        change_count = len(recent_changes)

        # Normalize frequency (0-12 changes per year)
        frequency_score = min(1.0, change_count / 12.0)

        return round(frequency_score, 3)

    def _extract_precedent_strength(self, context: dict[str, Any]) -> float:
        """Extract precedent strength (0.0-1.0)."""
        policy = context.get("policy", {})

        # Direct strength if provided
        if "precedent_strength" in policy:
            return float(policy["precedent_strength"])

        # Calculate from precedents
        precedents = policy.get("precedents", [])

        if not precedents:
            return 0.1  # Low strength if no precedents

        total_strength = 0.0

        for precedent in precedents:
            # Precedent relevance
            relevance = precedent.get("relevance", "low")
            relevance_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "exact": 1.0}
            relevance_score = relevance_scores.get(relevance, 0.2)

            # Precedent authority
            authority = precedent.get("authority", "internal")
            authority_scores = {"internal": 0.3, "industry": 0.6, "regulatory": 0.9, "legal": 1.0}
            authority_score = authority_scores.get(authority, 0.3)

            # Precedent age (newer is stronger)
            created_date = precedent.get("created_date")
            if created_date and isinstance(created_date, str):
                try:
                    creation_time = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    age_days = (now - creation_time).days
                    # Stronger if recent (within last 2 years)
                    age_score = max(0.1, 1.0 - (age_days / 730.0))
                except ValueError:
                    age_score = 0.5
            else:
                age_score = 0.5

            # Combined strength for this precedent
            precedent_strength = relevance_score * authority_score * age_score
            total_strength += precedent_strength

        # Average strength across all precedents
        average_strength = total_strength / len(precedents)

        return round(min(1.0, average_strength), 3)
