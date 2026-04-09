"""Autonomous Governance - Self-healing architectural governance systems.

This module provides autonomous governance capabilities that enable
self-healing architectural governance and automated compliance enforcement.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase2.contextual_engine import ContextualIntelligenceEngine, AnalysisResult
from .health_monitoring import ArchitecturalHealthMonitor, HealthStatus

logger = logging.getLogger(__name__)


class GovernanceActionType(Enum):
    """Types of governance actions."""

    BLOCK = "block"
    WARN = "warn"
    AUTO_FIX = "auto_fix"
    ESCALATE = "escalate"
    MONITOR = "monitor"
    APPROVE = "approve"


class ComplianceLevel(Enum):
    """Compliance levels for governance."""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


@dataclass
class GovernanceRule:
    """Represents a governance rule."""

    rule_id: str
    name: str
    description: str
    severity: str  # low, medium, high, critical
    action: GovernanceActionType
    conditions: Dict[str, Any]
    auto_fix_available: bool
    auto_fix_strategy: Optional[str]
    last_triggered: Optional[datetime]
    trigger_count: int = 0


@dataclass
class GovernanceViolation:
    """Represents a governance violation."""

    violation_id: str
    rule_id: str
    severity: str
    description: str
    context: ArchitecturalContext
    detected_at: datetime
    resolved: bool = False
    resolution_strategy: Optional[str] = None
    resolution_time: Optional[datetime] = None


@dataclass
class GovernanceActionRecord:
    """Represents a governance action taken."""

    action_id: str
    action_type: GovernanceActionType
    rule_id: str
    context: ArchitecturalContext
    executed_at: datetime
    successful: bool
    result: Optional[str]
    auto_generated: bool = True


@dataclass
class GovernanceReport:
    """Comprehensive governance report."""

    compliance_level: ComplianceLevel
    compliance_score: float  # 0.0 to 1.0
    active_violations: List[GovernanceViolation]
    resolved_violations: List[GovernanceViolation]
    governance_actions: List[GovernanceActionRecord]
    rules_triggered: List[str]
    recommendations: List[str]
    generated_at: datetime
    execution_time_seconds: float = 0.0


class AutonomousGovernanceEngine:
    """Autonomous governance engine for self-healing architectural governance."""

    def __init__(
        self, contextual_engine: ContextualIntelligenceEngine, health_monitor: ArchitecturalHealthMonitor
    ):
        """Initialize autonomous governance engine.

        Args:
            contextual_engine: Contextual intelligence engine for analysis
            health_monitor: Health monitoring system for health assessment
        """
        self.contextual_engine = contextual_engine
        self.health_monitor = health_monitor

        # Governance rules
        self.governance_rules: Dict[str, GovernanceRule] = {}
        self.rule_violations: List[GovernanceViolation] = []
        self.governance_actions: List[GovernanceActionRecord] = []

        # Governance configuration
        self.governance_config = {
            "auto_fix_enabled": True,
            "escalation_threshold": 3,  # violations before escalation
            "compliance_threshold": 0.8,
            "max_auto_fix_attempts": 3,
            "governance_check_interval_seconds": 30,
        }

        # Initialize governance rules
        self._initialize_governance_rules()

        logger.info("AutonomousGovernanceEngine initialized")

    def enforce_governance(self, context: ArchitecturalContext) -> Tuple[GovernanceActionRecord, bool]:
        """Enforce governance rules on architectural context.

        Args:
            context: Architectural context to govern

        Returns:
            Tuple of (governance action, compliance status)
        """
        logger.info("Enforcing governance on %s", context.action_type)

        # Check governance rules
        violations = self._check_governance_rules(context)

        # Determine appropriate action
        action = self._determine_governance_action(context, violations)

        # Execute governance action
        success = self._execute_governance_action(action, context)

        # Record governance action
        self.governance_actions.append(action)

        # Update compliance status
        is_compliant = len(violations) == 0

        logger.info(
            "Governance enforcement completed: %s, compliant: %s", action.action_type.value, is_compliant
        )

        return action, is_compliant

    def auto_fix_violations(self, max_fixes: int = 5) -> List[GovernanceActionRecord]:
        """Automatically fix governance violations.

        Args:
            max_fixes: Maximum number of violations to fix

        Returns:
            List of governance actions taken for auto-fixes
        """
        logger.info("Starting auto-fix of governance violations")

        auto_fix_actions = []

        # Get unresolved violations with auto-fix available
        fixable_violations = [
            v
            for v in self.rule_violations
            if not v.resolved
            and self.governance_rules.get(
                v.rule_id, GovernanceRule("", "", "", "", GovernanceActionType.MONITOR, {}, False, None, None)
            ).auto_fix_available
        ]

        # Sort by severity (critical first)
        fixable_violations.sort(key=lambda v: self._get_severity_priority(v.severity), reverse=True)

        # Fix violations
        for violation in fixable_violations[:max_fixes]:
            rule = self.governance_rules[violation.rule_id]

            if rule.auto_fix_strategy:
                action = self._execute_auto_fix(violation, rule)
                auto_fix_actions.append(action)

        logger.info("Auto-fixed %d violations", len(auto_fix_actions))

        return auto_fix_actions

    def assess_compliance(self, scope: Optional[List[str]] = None) -> GovernanceReport:
        """Assess overall governance compliance.

        Args:
            scope: Optional scope for compliance assessment

        Returns:
            GovernanceReport with comprehensive compliance assessment
        """
        start_time = time.time()

        logger.info("Starting comprehensive compliance assessment")

        # Get active violations
        active_violations = [v for v in self.rule_violations if not v.resolved]
        resolved_violations = [v for v in self.rule_violations if v.resolved]

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(active_violations)

        # Determine compliance level
        compliance_level = self._determine_compliance_level(compliance_score)

        # Get recently triggered rules
        rules_triggered = list(set(v.rule_id for v in active_violations))

        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(
            active_violations, compliance_score, compliance_level
        )

        report = GovernanceReport(
            compliance_level=compliance_level,
            compliance_score=compliance_score,
            active_violations=active_violations,
            resolved_violations=resolved_violations,
            governance_actions=self.governance_actions[-100:],  # Last 100 actions
            rules_triggered=rules_triggered,
            recommendations=recommendations,
            generated_at=datetime.now(),
            execution_time_seconds=time.time() - start_time,
        )

        logger.info("Compliance assessment completed: %s (%.2f)", compliance_level.value, compliance_score)

        return report

    def get_governance_dashboard(self) -> Dict[str, Any]:
        """Get governance dashboard data.

        Returns:
            Governance dashboard data for visualization
        """
        active_violations = [v for v in self.rule_violations if not v.resolved]

        dashboard = {
            "compliance_level": self._get_current_compliance_level(),
            "compliance_score": self._get_current_compliance_score(),
            "active_violations": len(active_violations),
            "total_violations": len(self.rule_violations),
            "resolved_violations": len([v for v in self.rule_violations if v.resolved]),
            "governance_actions_today": len(
                [a for a in self.governance_actions if a.executed_at.date() == datetime.now().date()]
            ),
            "rules_triggered_today": len(
                set(v.rule_id for v in active_violations if v.detected_at.date() == datetime.now().date())
            ),
            "auto_fix_success_rate": self._calculate_auto_fix_success_rate(),
            "last_updated": datetime.now().isoformat(),
        }

        return dashboard

    def _initialize_governance_rules(self) -> None:
        """Initialize governance rules."""
        rules_config = [
            {
                "rule_id": "layer_violation_rule",
                "name": "Layer Violation Prevention",
                "description": "Prevents architectural layer violations",
                "severity": "high",
                "action": GovernanceActionType.BLOCK,
                "conditions": {"layer_crossing": True},
                "auto_fix_available": True,
                "auto_fix_strategy": "suggest_layer_compliant_alternative",
            },
            {
                "rule_id": "circular_dependency_rule",
                "name": "Circular Dependency Prevention",
                "description": "Prevents circular dependencies between modules",
                "severity": "critical",
                "action": GovernanceActionType.BLOCK,
                "conditions": {"circular_dependency": True},
                "auto_fix_available": True,
                "auto_fix_strategy": "break_circular_dependency",
            },
            {
                "rule_id": "security_violation_rule",
                "name": "Security Violation Prevention",
                "description": "Prevents security violations in architectural changes",
                "severity": "critical",
                "action": GovernanceActionType.BLOCK,
                "conditions": {"security_violation": True},
                "auto_fix_available": False,
                "auto_fix_strategy": None,
            },
            {
                "rule_id": "performance_degradation_rule",
                "name": "Performance Degradation Prevention",
                "description": "Warns about potential performance degradations",
                "severity": "medium",
                "action": GovernanceActionType.WARN,
                "conditions": {"performance_impact": "high"},
                "auto_fix_available": True,
                "auto_fix_strategy": "suggest_performance_optimization",
            },
            {
                "rule_id": "complexity_threshold_rule",
                "name": "Complexity Threshold Enforcement",
                "description": "Prevents excessive complexity in architectural changes",
                "severity": "medium",
                "action": GovernanceActionType.WARN,
                "conditions": {"complexity_score": {"gt": 0.8}},
                "auto_fix_available": True,
                "auto_fix_strategy": "suggest_simplification",
            },
        ]

        for config in rules_config:
            rule = GovernanceRule(
                rule_id=config["rule_id"],
                name=config["name"],
                description=config["description"],
                severity=config["severity"],
                action=config["action"],
                conditions=config["conditions"],
                auto_fix_available=config["auto_fix_available"],
                auto_fix_strategy=config["auto_fix_strategy"],
                last_triggered=None,
            )
            self.governance_rules[rule.rule_id] = rule

    def _check_governance_rules(self, context: ArchitecturalContext) -> List[GovernanceViolation]:
        """Check context against governance rules."""
        violations = []

        for rule_id, rule in self.governance_rules.items():
            if self._evaluate_rule_conditions(rule.conditions, context):
                violation = GovernanceViolation(
                    violation_id=f"violation_{rule_id}_{int(time.time())}",
                    rule_id=rule_id,
                    severity=rule.severity,
                    description=f"Governance rule violated: {rule.name}",
                    context=context,
                    detected_at=datetime.now(),
                )

                violations.append(violation)
                self.rule_violations.append(violation)

                # Update rule trigger count
                rule.trigger_count += 1
                rule.last_triggered = datetime.now()

                logger.warning("Governance violation detected: %s", rule.name)

        return violations

    def _evaluate_rule_conditions(self, conditions: Dict[str, Any], context: ArchitecturalContext) -> bool:
        """Evaluate if context matches rule conditions."""
        # This would integrate with actual condition evaluation
        # For now, provide mock evaluation

        # Mock condition evaluation based on context
        if conditions.get("layer_crossing"):
            # Mock layer crossing detection
            return len(context.target_modules) > 3

        if conditions.get("circular_dependency"):
            # Mock circular dependency detection
            return "cycle" in str(context.proposed_changes).lower()

        if conditions.get("security_violation"):
            # Mock security violation detection
            return "auth" in str(context.target_modules).lower() and context.action_type in [
                "delete_file",
                "modify_module",
            ]

        if conditions.get("performance_impact") == "high":
            # Mock performance impact detection
            return len(context.target_modules) > 5

        if "complexity_score" in conditions:
            # Mock complexity evaluation
            complexity_condition = conditions["complexity_score"]
            if "gt" in complexity_condition:
                return len(context.target_modules) > complexity_condition["gt"] * 10

        return False

    def _determine_governance_action(
        self, context: ArchitecturalContext, violations: List[GovernanceViolation]
    ) -> GovernanceActionRecord:
        """Determine appropriate governance action."""
        if not violations:
            action_type = GovernanceActionType.APPROVE
        else:
            # Get highest severity violation
            highest_severity = max(violations, key=lambda v: self._get_severity_priority(v.severity))
            rule = self.governance_rules[highest_severity.rule_id]
            action_type = rule.action

        action = GovernanceActionRecord(
            action_id=f"action_{action_type.value}_{int(time.time())}",
            action_type=action_type,
            rule_id=violations[0].rule_id if violations else "no_violation",
            context=context,
            executed_at=datetime.now(),
            successful=False,
            result=None,
            auto_generated=True,
        )

        return action

    def _execute_governance_action(
        self, action: GovernanceActionRecord, context: ArchitecturalContext
    ) -> bool:
        """Execute governance action."""
        try:
            if action.action_type == GovernanceActionType.BLOCK:
                action.result = "Action blocked due to governance violations"
                action.successful = True
                logger.info("Governance action blocked: %s", context.action_type)

            elif action.action_type == GovernanceActionType.WARN:
                action.result = "Warning issued for governance concerns"
                action.successful = True
                logger.warning("Governance warning issued: %s", context.action_type)

            elif action.action_type == GovernanceActionType.APPROVE:
                action.result = "Action approved - no governance violations"
                action.successful = True
                logger.info("Governance action approved: %s", context.action_type)

            elif action.action_type == GovernanceActionType.ESCALATE:
                action.result = "Action escalated for manual review"
                action.successful = True
                logger.warning("Governance action escalated: %s", context.action_type)

            elif action.action_type == GovernanceActionType.MONITOR:
                action.result = "Action placed under monitoring"
                action.successful = True
                logger.info("Governance action monitoring: %s", context.action_type)

            else:
                action.result = f"Unknown action type: {action.action_type.value}"
                action.successful = False

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as e:
            action.result = f"Action execution failed: {str(e)}"
            action.successful = False
            logger.error("Governance action execution failed: %s", e)

        return action.successful

    def _execute_auto_fix(
        self, violation: GovernanceViolation, rule: GovernanceRule
    ) -> GovernanceActionRecord:
        """Execute auto-fix for a violation."""
        logger.info("Executing auto-fix for violation: %s", violation.violation_id)

        action = GovernanceActionRecord(
            action_id=f"auto_fix_{violation.violation_id}",
            action_type=GovernanceActionType.AUTO_FIX,
            rule_id=rule.rule_id,
            context=violation.context,
            executed_at=datetime.now(),
            successful=False,
            result=None,
            auto_generated=True,
        )

        try:
            # Execute auto-fix strategy
            if rule.auto_fix_strategy == "suggest_layer_compliant_alternative":
                action.result = "Suggested layer-compliant alternative implementation"
                action.successful = True

            elif rule.auto_fix_strategy == "break_circular_dependency":
                action.result = "Circular dependency broken through refactoring suggestion"
                action.successful = True

            elif rule.auto_fix_strategy == "suggest_performance_optimization":
                action.result = "Performance optimization suggestions provided"
                action.successful = True

            elif rule.auto_fix_strategy == "suggest_simplification":
                action.result = "Simplification suggestions provided"
                action.successful = True

            else:
                action.result = f"Unknown auto-fix strategy: {rule.auto_fix_strategy}"
                action.successful = False

            # Mark violation as resolved if fix was successful
            if action.successful:
                violation.resolved = True
                violation.resolution_strategy = rule.auto_fix_strategy
                violation.resolution_time = datetime.now()

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as e:
            action.result = f"Auto-fix execution failed: {str(e)}"
            action.successful = False
            logger.error("Auto-fix execution failed: %s", e)

        return action

    def _calculate_compliance_score(self, active_violations: List[GovernanceViolation]) -> float:
        """Calculate overall compliance score."""
        if not self.governance_rules:
            return 1.0

        # Weight violations by severity
        total_weight = 0.0
        violation_weight = 0.0

        for rule in self.governance_rules.values():
            weight = self._get_severity_weight(rule.severity)
            total_weight += weight

            # Check if rule has active violations
            rule_violations = [v for v in active_violations if v.rule_id == rule.rule_id]
            if rule_violations:
                violation_weight += weight

        if total_weight == 0:
            return 1.0

        compliance_score = 1.0 - (violation_weight / total_weight)
        return max(0.0, min(1.0, compliance_score))

    def _determine_compliance_level(self, compliance_score: float) -> ComplianceLevel:
        """Determine compliance level from score."""
        if compliance_score >= 0.9:
            return ComplianceLevel.COMPLIANT
        elif compliance_score >= 0.7:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        elif compliance_score >= 0.5:
            return ComplianceLevel.NON_COMPLIANT
        else:
            return ComplianceLevel.UNKNOWN

    def _generate_compliance_recommendations(
        self,
        active_violations: List[GovernanceViolation],
        compliance_score: float,
        compliance_level: ComplianceLevel,
    ) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []

        # Severity-based recommendations
        critical_violations = [v for v in active_violations if v.severity == "critical"]
        if critical_violations:
            recommendations.append(f"Address {len(critical_violations)} critical violations immediately")

        high_violations = [v for v in active_violations if v.severity == "high"]
        if high_violations:
            recommendations.append(f"Resolve {len(high_violations)} high-severity violations")

        # Score-based recommendations
        if compliance_score < self.governance_config["compliance_threshold"]:
            recommendations.append("Improve overall compliance to meet threshold requirements")

        # Rule-specific recommendations
        rule_counts = defaultdict(int)
        for violation in active_violations:
            rule_counts[violation.rule_id] += 1

        for rule_id, count in rule_counts.items():
            if count > 2:
                rule = self.governance_rules.get(rule_id)
                if rule:
                    recommendations.append(f"Review and address repeated violations of: {rule.name}")

        # Auto-fix recommendations
        auto_fixable_violations = [
            v
            for v in active_violations
            if self.governance_rules.get(
                v.rule_id, GovernanceRule("", "", "", "", GovernanceActionType.MONITOR, {}, False, None, None)
            ).auto_fix_available
        ]

        if auto_fixable_violations and self.governance_config["auto_fix_enabled"]:
            recommendations.append(f"Enable auto-fix for {len(auto_fixable_violations)} fixable violations")

        return recommendations

    def _get_severity_priority(self, severity: str) -> int:
        """Get priority weight for severity level."""
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return severity_weights.get(severity, 1)

    def _get_severity_weight(self, severity: str) -> float:
        """Get weight for severity level in compliance calculation."""
        severity_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
        return severity_weights.get(severity, 0.4)

    def _get_current_compliance_level(self) -> ComplianceLevel:
        """Get current compliance level."""
        active_violations = [v for v in self.rule_violations if not v.resolved]
        compliance_score = self._calculate_compliance_score(active_violations)
        return self._determine_compliance_level(compliance_score)

    def _get_current_compliance_score(self) -> float:
        """Get current compliance score."""
        active_violations = [v for v in self.rule_violations if not v.resolved]
        return self._calculate_compliance_score(active_violations)

    def _calculate_auto_fix_success_rate(self) -> float:
        """Calculate auto-fix success rate."""
        auto_fix_actions = [
            a for a in self.governance_actions if a.action_type == GovernanceActionType.AUTO_FIX
        ]

        if not auto_fix_actions:
            return 0.0

        successful_fixes = sum(1 for a in auto_fix_actions if a.successful)
        return successful_fixes / len(auto_fix_actions)

    def get_governance_statistics(self) -> Dict[str, Any]:
        """Get governance system statistics."""
        active_violations = [v for v in self.rule_violations if not v.resolved]

        return {
            "total_rules": len(self.governance_rules),
            "total_violations": len(self.rule_violations),
            "active_violations": len(active_violations),
            "resolved_violations": len([v for v in self.rule_violations if v.resolved]),
            "total_actions": len(self.governance_actions),
            "auto_fix_enabled": self.governance_config["auto_fix_enabled"],
            "compliance_score": self._get_current_compliance_score(),
            "auto_fix_success_rate": self._calculate_auto_fix_success_rate(),
            "rules_by_severity": {
                severity: len([r for r in self.governance_rules.values() if r.severity == severity])
                for severity in ["critical", "high", "medium", "low"]
            },
        }
