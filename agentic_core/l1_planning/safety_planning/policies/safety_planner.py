"""
Safety Planner Module
LEVEL 5 - Safety planning and risk assessment for agentic operations
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SafetyPlan:
    """Represents a safety plan with risk assessments and mitigation strategies"""
    plan_id: str
    risk_level: str
    safety_policies: List[str]
    mitigation_strategies: List[str]
    monitoring_requirements: Dict[str, Any]

class SafetyPlanner:
    """Handles safety planning and risk assessment"""

    def __init__(self):
        self.risk_levels = ["low", "medium", "high", "critical"]
        self.safety_policies = [
            "data_privacy_protection",
            "content_filtering",
            "access_control",
            "audit_logging",
            "error_handling"
        ]

    async def create_safety_plan(
        self,
        operation_type: str,
        data_sensitivity: str,
        context: Dict[str, Any]
    ) -> SafetyPlan:
        """Create a safety plan with risk assessments and mitigation"""
        try:
            plan_id = f"safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Assess risk level
            risk_level = self._assess_risk_level(operation_type, data_sensitivity)

            # Select applicable safety policies
            safety_policies = self._select_safety_policies(
                operation_type, data_sensitivity, risk_level
            )

            # Define mitigation strategies
            mitigation_strategies = self._define_mitigation_strategies(
                risk_level, safety_policies
            )

            # Set monitoring requirements
            monitoring_requirements = self._set_monitoring_requirements(
                risk_level, operation_type
            )

            return SafetyPlan(
                plan_id=plan_id,
                risk_level=risk_level,
                safety_policies=safety_policies,
                mitigation_strategies=mitigation_strategies,
                monitoring_requirements=monitoring_requirements
            )

        except Exception as e:
            raise Exception(f"Safety planning failed: {str(e)}")

    def _assess_risk_level(self, operation_type: str, data_sensitivity: str) -> str:
        """Assess risk level based on operation and data sensitivity"""
        base_risk = "medium"

        # Adjust based on operation type
        if "external" in operation_type.lower():
            base_risk = "high"
        if "delete" in operation_type.lower() or "modify" in operation_type.lower():
            base_risk = "high"
        if "read" in operation_type.lower() or "query" in operation_type.lower():
            base_risk = "low"

        # Adjust based on data sensitivity
        if data_sensitivity.lower() in ["pii", "financial", "health"]:
            if base_risk == "high":
                return "critical"
            else:
                return "high"
        elif data_sensitivity.lower() in ["public", "general"]:
            if base_risk == "low":
                return "low"
            else:
                return "medium"

        return base_risk

    def _select_safety_policies(
        self, operation_type: str, data_sensitivity: str, risk_level: str
    ) -> List[str]:
        """Select applicable safety policies based on operation and risk"""
        policies = ["error_handling"]  # Base policy

        if "external" in operation_type.lower():
            policies.extend(["content_filtering", "access_control"])

        if data_sensitivity.lower() in ["pii", "financial", "health"]:
            policies.extend(["data_privacy_protection", "audit_logging"])

        if risk_level in ["high", "critical"]:
            policies.extend(["audit_logging", "access_control"])

        return list(set(policies))

    def _define_mitigation_strategies(
        self, risk_level: str, safety_policies: List[str]
    ) -> List[str]:
        """Define mitigation strategies based on risk and policies"""
        strategies = []

        for policy in safety_policies:
            if policy == "data_privacy_protection":
                strategies.append("encrypt_sensitive_data")
                strategies.append("anonymize_pii")
            if policy == "content_filtering":
                strategies.append("validate_input_content")
                strategies.append("sanitize_output_content")
            if policy == "access_control":
                strategies.append("verify_user_permissions")
                strategies.append("implement_rate_limiting")
            if policy == "audit_logging":
                strategies.append("log_all_operations")
                strategies.append("monitor_access_patterns")

        if risk_level == "critical":
            strategies.append("require_manual_approval")
            strategies.append("implement_real_time_monitoring")

        return list(set(strategies))

    def _set_monitoring_requirements(
        self, risk_level: str, operation_type: str
    ) -> Dict[str, Any]:
        """Set monitoring requirements based on risk and operation"""
        requirements = {
            "logging_level": "info",
            "alert_threshold": "medium",
            "retention_period": "30_days"
        }

        if risk_level in ["high", "critical"]:
            requirements["logging_level"] = "debug"
            requirements["alert_threshold"] = "low"
            requirements["retention_period"] = "90_days"
            requirements["real_time_monitoring"] = True

        if "external" in operation_type.lower():
            requirements["external_api_monitoring"] = True
            requirements["rate_limit_monitoring"] = True

        return requirements

__all__ = ["SafetyPlanner", "SafetyPlan"]
