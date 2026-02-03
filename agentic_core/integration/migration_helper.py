"""
Migration Helper for tracking agent compliance with new protocols.

Provides utilities for checking agent compliance with the migration plan
and tracking migration progress across all layers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from agentic_core.primitives.feature_flags import FeatureFlagManager

logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """Result of agent compliance check."""

    agent_name: str
    compliant: bool
    has_feature_flag_mixin: bool
    has_verification_gate: bool
    has_human_review: bool
    has_meta_learning: bool
    has_audit_trail: bool
    missing_components: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "compliant": self.compliant,
            "has_feature_flag_mixin": self.has_feature_flag_mixin,
            "has_verification_gate": self.has_verification_gate,
            "has_human_review": self.has_human_review,
            "has_meta_learning": self.has_meta_learning,
            "has_audit_trail": self.has_audit_trail,
            "missing_components": self.missing_components,
            "recommendations": self.recommendations,
        }


@dataclass
class MigrationStatus:
    """Overall migration status."""

    total_agents: int
    compliant_agents: int
    non_compliant_agents: int
    compliance_percentage: float
    agents_by_status: Dict[str, List[str]] = field(default_factory=dict)
    feature_flag_status: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_agents": self.total_agents,
            "compliant_agents": self.compliant_agents,
            "non_compliant_agents": self.non_compliant_agents,
            "compliance_percentage": self.compliance_percentage,
            "agents_by_status": self.agents_by_status,
            "feature_flag_status": self.feature_flag_status,
        }


class MigrationHelper:
    """Helper for tracking migration compliance."""

    # Components required for full compliance
    REQUIRED_COMPONENTS = [
        "FeatureFlaggedAgentMixin",
        "verification_gate",
        "human_review",
        "meta_learning",
        "audit_trail",
    ]

    @classmethod
    def check_agent_compliance(
        cls,
        agent_class: Type,
        strict: bool = False,
    ) -> ComplianceResult:
        """Check if an agent class is compliant with migration requirements.

        Args:
            agent_class: The agent class to check
            strict: If True, require all components; if False, only require mixin

        Returns:
            ComplianceResult with compliance details
        """
        agent_name = agent_class.__name__
        missing = []
        recommendations = []

        # Check for FeatureFlaggedAgentMixin
        has_mixin = cls._has_feature_flag_mixin(agent_class)
        if not has_mixin:
            missing.append("FeatureFlaggedAgentMixin")
            recommendations.append(
                f"Add FeatureFlaggedAgentMixin to {agent_name}'s inheritance"
            )

        # Check for verification gate integration
        has_verification = cls._has_method(agent_class, "verify_action")
        if not has_verification:
            missing.append("verification_gate")
            recommendations.append(
                f"Implement verify_action method in {agent_name}"
            )

        # Check for human review integration
        has_review = cls._has_method(agent_class, "submit_for_review")
        if not has_review:
            missing.append("human_review")
            recommendations.append(
                f"Implement submit_for_review method in {agent_name}"
            )

        # Check for meta-learning integration
        has_ml = cls._has_method(agent_class, "flagged_recall_or_execute")
        if not has_ml:
            missing.append("meta_learning")
            recommendations.append(
                f"Implement flagged_recall_or_execute method in {agent_name}"
            )

        # Check for audit trail integration
        has_audit = cls._has_method(agent_class, "log_audit_event")
        if not has_audit:
            missing.append("audit_trail")
            recommendations.append(
                f"Implement log_audit_event method in {agent_name}"
            )

        # Determine compliance
        if strict:
            compliant = len(missing) == 0
        else:
            # Non-strict: only require mixin
            compliant = has_mixin

        return ComplianceResult(
            agent_name=agent_name,
            compliant=compliant,
            has_feature_flag_mixin=has_mixin,
            has_verification_gate=has_verification,
            has_human_review=has_review,
            has_meta_learning=has_ml,
            has_audit_trail=has_audit,
            missing_components=missing,
            recommendations=recommendations,
        )

    @classmethod
    def _has_feature_flag_mixin(cls, agent_class: Type) -> bool:
        """Check if agent has FeatureFlaggedAgentMixin in MRO."""
        for base in agent_class.__mro__:
            if base.__name__ == "FeatureFlaggedAgentMixin":
                return True
        return False

    @classmethod
    def _has_method(cls, agent_class: Type, method_name: str) -> bool:
        """Check if agent has a specific method."""
        return hasattr(agent_class, method_name) and callable(
            getattr(agent_class, method_name, None)
        )

    @classmethod
    def get_migration_status(
        cls,
        agent_classes: List[Type],
        strict: bool = False,
    ) -> MigrationStatus:
        """Get overall migration status for a list of agents.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            MigrationStatus with overall statistics
        """
        compliant = []
        non_compliant = []

        for agent_class in agent_classes:
            result = cls.check_agent_compliance(agent_class, strict)
            if result.compliant:
                compliant.append(result.agent_name)
            else:
                non_compliant.append(result.agent_name)

        total = len(agent_classes)
        compliance_pct = (len(compliant) / total * 100) if total > 0 else 0.0

        return MigrationStatus(
            total_agents=total,
            compliant_agents=len(compliant),
            non_compliant_agents=len(non_compliant),
            compliance_percentage=compliance_pct,
            agents_by_status={
                "compliant": compliant,
                "non_compliant": non_compliant,
            },
            feature_flag_status=FeatureFlagManager.get_all_flags(),
        )

    @classmethod
    def generate_migration_report(
        cls,
        agent_classes: List[Type],
        strict: bool = False,
    ) -> str:
        """Generate a human-readable migration report.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            Formatted migration report string
        """
        status = cls.get_migration_status(agent_classes, strict)

        lines = [
            "=" * 60,
            "AGENT MIGRATION STATUS REPORT",
            "=" * 60,
            "",
            f"Total Agents: {status.total_agents}",
            f"Compliant: {status.compliant_agents}",
            f"Non-Compliant: {status.non_compliant_agents}",
            f"Compliance: {status.compliance_percentage:.1f}%",
            "",
            "Feature Flag Status:",
        ]

        for flag, enabled in status.feature_flag_status.items():
            lines.append(f"  {flag}: {'ENABLED' if enabled else 'disabled'}")

        if status.agents_by_status.get("non_compliant"):
            lines.append("")
            lines.append("Non-Compliant Agents:")
            for agent in status.agents_by_status["non_compliant"]:
                lines.append(f"  - {agent}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# Convenience functions
def check_agent_compliance(
    agent_class: Type,
    strict: bool = False,
) -> ComplianceResult:
    """Check if an agent class is compliant with migration requirements."""
    return MigrationHelper.check_agent_compliance(agent_class, strict)


def get_migration_status(
    agent_classes: List[Type],
    strict: bool = False,
) -> MigrationStatus:
    """Get overall migration status for a list of agents."""
    return MigrationHelper.get_migration_status(agent_classes, strict)
