"""
Policy Engine Module
LEVEL 5 - Policy enforcement and safety compliance engine for agentic operations
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

class PolicyType(Enum):
    CONTENT_FILTER = "content_filter"
    DATA_PRIVACY = "data_privacy"
    ACCESS_CONTROL = "access_control"
    RATE_LIMITING = "rate_limiting"
    AUDIT_LOGGING = "audit_logging"
    ERROR_HANDLING = "error_handling"

class PolicyAction(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    WARN = "warn"
    LOG = "log"

class PolicySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PolicyRule:
    """Represents a policy rule"""
    rule_id: str
    policy_type: PolicyType
    condition: str
    action: PolicyAction
    severity: PolicySeverity
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PolicyViolation:
    """Represents a policy violation"""
    violation_id: str
    rule_id: str
    policy_type: PolicyType
    severity: PolicySeverity
    description: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False

@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""
    action: PolicyAction
    violations: List[PolicyViolation]
    modified_content: Optional[Any] = None
    warnings: List[str] = field(default_factory=list)
    evaluation_time: float = 0.0

@dataclass
class PolicyEngineConfig:
    """Configuration for policy engine"""
    enable_logging: bool = True
    log_violations: bool = True
    auto_resolve_low_severity: bool = True
    max_violations_per_request: int = 100
    evaluation_timeout_seconds: float = 5.0

class PolicyEngine:
    """Policy enforcement and safety compliance engine"""

    def __init__(self, config: PolicyEngineConfig = None):
        self.config = config or PolicyEngineConfig()
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[str, PolicyRule] = {}
        self.violations: List[PolicyViolation] = []
        self.policy_handlers: Dict[PolicyType, Callable] = {}
        self._setup_default_handlers()

    def add_rule(self, rule: PolicyRule) -> str:
        """Add a policy rule"""
        try:
            self.rules[rule.rule_id] = rule
            self.logger.info(f"Added policy rule {rule.rule_id} for {rule.policy_type.value}")
            return rule.rule_id
        except Exception as e:
            self.logger.error(f"Failed to add policy rule: {str(e)}")
            raise e

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule"""
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                self.logger.info(f"Removed policy rule {rule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove policy rule: {str(e)}")
            return False

    async def evaluate_policies(
        self,
        content: Any,
        context: Dict[str, Any],
        policy_types: List[PolicyType] = None
    ) -> PolicyEvaluationResult:
        """Evaluate policies against content"""
        try:
            start_time = datetime.utcnow()

            # Get applicable rules
            applicable_rules = self._get_applicable_rules(policy_types)

            violations = []
            warnings = []
            final_action = PolicyAction.ALLOW
            modified_content = content

            # Evaluate each rule
            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                try:
                    rule_result = await self._evaluate_rule(rule, content, context)

                    if rule_result["violated"]:
                        violation = PolicyViolation(
                            violation_id=f"vio_{int(datetime.utcnow().timestamp())}",
                            rule_id=rule.rule_id,
                            policy_type=rule.policy_type,
                            severity=rule.severity,
                            description=rule_result["description"],
                            context=context.copy()
                        )
                        violations.append(violation)

                        # Determine action based on rule and severity
                        if rule.action == PolicyAction.BLOCK or rule.severity == PolicySeverity.CRITICAL:
                            final_action = PolicyAction.BLOCK
                        elif rule.action == PolicyAction.MODIFY and final_action != PolicyAction.BLOCK:
                            final_action = PolicyAction.MODIFY
                            modified_content = rule_result.get("modified_content", content)
                        elif rule.action == PolicyAction.WARN and final_action == PolicyAction.ALLOW:
                            final_action = PolicyAction.WARN
                            warnings.append(rule_result["description"])

                except Exception as e:
                    self.logger.error(f"Failed to evaluate rule {rule.rule_id}: {str(e)}")
                    continue

            # Auto-resolve low severity violations if enabled
            if self.config.auto_resolve_low_severity:
                for violation in violations:
                    if violation.severity == PolicySeverity.LOW:
                        violation.resolved = True

            # Log violations
            if self.config.log_violations and violations:
                self.violations.extend(violations)
                if self.config.enable_logging:
                    self.logger.warning(f"Policy violations detected: {len(violations)}")

            evaluation_time = (datetime.utcnow() - start_time).total_seconds()

            result = PolicyEvaluationResult(
                action=final_action,
                violations=violations,
                modified_content=modified_content,
                warnings=warnings,
                evaluation_time=evaluation_time
            )

            return result

        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {str(e)}")
            return PolicyEvaluationResult(
                action=PolicyAction.BLOCK,
                violations=[],
                evaluation_time=0.0
            )

    async def check_content_safety(self, content: str, context: Dict[str, Any] = None) -> PolicyEvaluationResult:
        """Check content safety against content filter policies"""
        if context is None:
            context = {}

        return await self.evaluate_policies(content, context, [PolicyType.CONTENT_FILTER])

    async def check_data_privacy(self, data: Any, context: Dict[str, Any] = None) -> PolicyEvaluationResult:
        """Check data privacy compliance"""
        if context is None:
            context = {}

        return await self.evaluate_policies(data, context, [PolicyType.DATA_PRIVACY])

    async def check_access_control(self, user_id: str, resource: str, action: str, context: Dict[str, Any] = None) -> PolicyEvaluationResult:
        """Check access control permissions"""
        if context is None:
            context = {}

        context.update({
            "user_id": user_id,
            "resource": resource,
            "action": action
        })

        return await self.evaluate_policies(action, context, [PolicyType.ACCESS_CONTROL])

    def get_violations(
        self,
        policy_type: PolicyType = None,
        severity: PolicySeverity = None,
        resolved: bool = None
    ) -> List[PolicyViolation]:
        """Get policy violations with optional filtering"""
        violations = self.violations

        # Filter by policy type
        if policy_type:
            violations = [v for v in violations if v.policy_type == policy_type]

        # Filter by severity
        if severity:
            violations = [v for v in violations if v.severity == severity]

        # Filter by resolution status
        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]

        return violations

    def resolve_violation(self, violation_id: str) -> bool:
        """Mark a violation as resolved"""
        try:
            for violation in self.violations:
                if violation.violation_id == violation_id:
                    violation.resolved = True
                    self.logger.info(f"Resolved violation {violation_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to resolve violation: {str(e)}")
            return False

    def get_policy_statistics(self) -> Dict[str, Any]:
        """Get policy engine statistics"""
        total_violations = len(self.violations)
        resolved_violations = sum(1 for v in self.violations if v.resolved)

        policy_type_counts = {}
        severity_counts = {}

        for violation in self.violations:
            # Count by policy type
            policy_type = violation.policy_type.value
            policy_type_counts[policy_type] = policy_type_counts.get(policy_type, 0) + 1

            # Count by severity
            severity = violation.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "total_violations": total_violations,
            "resolved_violations": resolved_violations,
            "unresolved_violations": total_violations - resolved_violations,
            "violations_by_policy_type": policy_type_counts,
            "violations_by_severity": severity_counts,
            "policy_types": list(self.policy_handlers.keys())
        }

    def _get_applicable_rules(self, policy_types: List[PolicyType] = None) -> List[PolicyRule]:
        """Get applicable rules based on policy types"""
        if policy_types is None:
            return list(self.rules.values())

        return [rule for rule in self.rules.values() if rule.policy_type in policy_types]

    async def _evaluate_rule(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy rule"""
        try:
            # Get handler for policy type
            if rule.policy_type in self.policy_handlers:
                handler = self.policy_handlers[rule.policy_type]
                return await handler(rule, content, context)
            else:
                return {"violated": False, "description": "No handler for policy type"}

        except Exception as e:
            self.logger.error(f"Rule evaluation failed: {str(e)}")
            return {"violated": False, "description": f"Evaluation error: {str(e)}"}

    def _setup_default_handlers(self) -> None:
        """Setup default policy handlers"""
        self.policy_handlers[PolicyType.CONTENT_FILTER] = self._handle_content_filter
        self.policy_handlers[PolicyType.DATA_PRIVACY] = self._handle_data_privacy
        self.policy_handlers[PolicyType.ACCESS_CONTROL] = self._handle_access_control
        self.policy_handlers[PolicyType.RATE_LIMITING] = self._handle_rate_limiting
        self.policy_handlers[PolicyType.AUDIT_LOGGING] = self._handle_audit_logging
        self.policy_handlers[PolicyType.ERROR_HANDLING] = self._handle_error_handling

    async def _handle_content_filter(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content filter policy"""
        if isinstance(content, str):
            # Mock content filtering
            forbidden_words = ["password", "secret", "private_key", "token"]
            content_lower = content.lower()

            for word in forbidden_words:
                if word in content_lower:
                    return {
                        "violated": True,
                        "description": f"Content contains forbidden word: {word}",
                        "modified_content": content.replace(word, "[REDACTED]")
                    }

        return {"violated": False, "description": "Content passed filter"}

    async def _handle_data_privacy(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data privacy policy"""
        # Mock privacy check
        if isinstance(content, dict):
            sensitive_fields = ["ssn", "credit_card", "bank_account"]

            for field in sensitive_fields:
                if field in content:
                    return {
                        "violated": True,
                        "description": f"Sensitive data field detected: {field}",
                        "modified_content": {**content, field: "[REDACTED]"}
                    }

        return {"violated": False, "description": "Data privacy check passed"}

    async def _handle_access_control(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle access control policy"""
        # Mock access control
        user_id = context.get("user_id")
        resource = context.get("resource")
        action = context.get("action")

        # Simple mock rules
        if resource == "admin" and user_id != "admin":
            return {
                "violated": True,
                "description": "Unauthorized access to admin resource"
            }

        if action == "delete" and not user_id:
            return {
                "violated": True,
                "description": "Delete action requires authentication"
            }

        return {"violated": False, "description": "Access control check passed"}

    async def _handle_rate_limiting(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rate limiting policy"""
        # Mock rate limiting
        _ = context.get("user_id", "anonymous")  # Placeholder for future rate limiting logic
        return {"violated": False, "description": "Rate limit check passed"}

    async def _handle_audit_logging(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle audit logging policy"""
        # Mock audit logging
        if self.config.enable_logging:
            self.logger.info(f"Audit log: {context}")

        return {"violated": False, "description": "Audit logging completed"}

    async def _handle_error_handling(self, rule: PolicyRule, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error handling policy"""
        # Mock error handling check
        return {"violated": False, "description": "Error handling check passed"}

__all__ = [
    "PolicyEngine", "PolicyRule", "PolicyViolation",
    "PolicyEvaluationResult", "PolicyEngineConfig",
    "PolicyType", "PolicyAction", "PolicySeverity"
]
