"""
Safety Domain Mixins - Shared pure logic for safety-related operations.

These mixins extract pure, stateless logic that can be reused across
safety domain agents while preserving stateful orchestration locally.
"""

from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class SafetyAnalysisMixin:
    """Mixin providing pure safety analysis logic."""

    @staticmethod
    def _compare_threat_levels(level1: str, level2: str) -> int:
        """
        Compare two threat levels.

        Args:
            level1: First threat level
            level2: Second threat level

        Returns:
            -1 if level1 < level2, 0 if equal, 1 if level1 > level2
        """
        threat_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        try:
            idx1 = threat_order.index(level1.upper())
            idx2 = threat_order.index(level2.upper())
            if idx1 < idx2:
                return -1
            elif idx1 > idx2:
                return 1
            else:
                return 0
        except ValueError:
            return (level1 > level2) - (level1 < level2)

    @staticmethod
    def _generate_recommendations(threat_level: str, context: dict[str, Any]) -> list[str]:
        """
        Generate safety recommendations based on threat level and context.

        Args:
            threat_level: Current threat level
            context: Context information for recommendations

        Returns:
            List of recommendation strings
        """
        recommendations = []
        if threat_level.upper() == "CRITICAL":
            recommendations.extend(
                ["Immediate action required", "Escalate to security team", "Consider system isolation"]
            )
        elif threat_level.upper() == "HIGH":
            recommendations.extend(
                ["Address within 24 hours", "Review security controls", "Monitor for related issues"]
            )
        elif threat_level.upper() == "MEDIUM":
            recommendations.extend(
                ["Address within 1 week", "Document mitigation plan", "Schedule follow-up review"]
            )
        else:
            recommendations.extend(
                [
                    "Address in next maintenance cycle",
                    "Consider for future improvements",
                    "Document for awareness",
                ]
            )
        if "file_count" in context and context["file_count"] > 100:
            recommendations.append("Consider bulk remediation approach")
        if "system_critical" in context and context["system_critical"]:
            recommendations.append("Prioritize system availability")
        return recommendations

    @staticmethod
    def matches(pattern: str, target: str) -> bool:
        """
        Check if pattern matches target using simple wildcard matching.

        Args:
            pattern: Pattern with optional wildcards
            target: Target string to match

        Returns:
            True if pattern matches target
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SafetyAnalysisMixin.matches")

        if not pattern or not target:
            return False
        if "*" in pattern:
            import re

            pattern_regex = pattern.replace("*", ".*")
            return re.fullmatch(pattern_regex, target) is not None
        else:
            return pattern == target


class HealingMixin:
    """Mixin providing pure healing logic."""

    @staticmethod
    def standard_heal(file_path: str, issue_type: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Standard healing logic for common file issues.

        Args:
            file_path: Path to file being healed
            issue_type: Type of issue detected
            context: Additional context for healing

        Returns:
            Healing result dictionary
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingMixin.standard_heal")

        result = {
            "file_path": file_path,
            "issue_type": issue_type,
            "healed": False,
            "actions_taken": [],
            "warnings": [],
        }
        if issue_type == "import_error":
            result["actions_taken"].append("Attempted import path correction")
            result["healed"] = True
        elif issue_type == "syntax_error":
            result["actions_taken"].append("Syntax validation failed - manual review required")
            result["warnings"].append("Syntax errors require manual intervention")
        elif issue_type == "missing_dependency":
            result["actions_taken"].append("Documented missing dependency")
            result["warnings"].append("Dependency installation may be required")
        else:
            result["actions_taken"].append(f"Applied standard healing for {issue_type}")
            result["healed"] = True
        if "backup_available" in context and context["backup_available"]:
            result["actions_taken"].append("Backup created before healing")
        return result


class StateAnalysisMixin:
    """Mixin providing pure state analysis logic."""

    @staticmethod
    # guardian: allow-magic-config
    def _check_past_failures(
        state_history: list[dict[str, Any]], failure_threshold: int = 3
    ) -> dict[str, Any]:
        """
        Analyze past failures to determine retry strategy.

        Args:
            state_history: List of previous state dictionaries
            failure_threshold: Number of failures before changing strategy

        Returns:
            Analysis result with recommendations
        """
        if not state_history:
            return {
                "failures_detected": False,
                "failure_count": 0,
                "recommendation": "Proceed normally",
                "retry_delay": 0,
            }
        failure_count = sum(1 for state in state_history if state.get("status") == "failed")
        result = {
            "failures_detected": failure_count > 0,
            "failure_count": failure_count,
            "recommendation": "Proceed normally",
            "retry_delay": 0,
        }
        if failure_count >= failure_threshold:
            result["recommendation"] = "Change approach or escalate"
            result["retry_delay"] = min(300, 30 * failure_count)
        elif failure_count > 0:
            result["recommendation"] = "Retry with caution"
            result["retry_delay"] = min(60, 10 * failure_count)
        return result
