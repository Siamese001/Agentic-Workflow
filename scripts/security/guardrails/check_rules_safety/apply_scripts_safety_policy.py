"""Scripts Safety Policy Application - Applies safety policies to script operations.

This module provides safety policy enforcement for script operations,
including script validation, permission checks, and security controls.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of safety policies."""
    EXECUTION_POLICY = "execution_policy"
    RESOURCE_POLICY = "resource_policy"
    NETWORK_POLICY = "network_policy"
    FILE_SYSTEM_POLICY = "file_system_policy"
    PERMISSION_POLICY = "permission_policy"
    DATA_POLICY = "data_policy"


class PolicyAction(Enum):
    """Actions for policy violations."""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"
    QUARANTINE = "quarantine"


@dataclass
class SafetyPolicy:
    """Definition of a safety policy."""
    id: str
    name: str
    policy_type: PolicyType
    description: str
    condition: str
    action: PolicyAction
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyViolation:
    """Record of a policy violation."""
    policy_id: str
    policy_name: str
    policy_type: PolicyType
    action: PolicyAction
    description: str
    script_content: Optional[str] = None
    violation_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyApplicationResult:
    """Result of policy application."""
    allowed: bool
    applied_policies: List[str] = field(default_factory=list)
    violations: List[PolicyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScriptsSafetyPolicyConfig:
    """Configuration for scripts safety policy application."""
    enabled_policies: List[PolicyType] = field(default_factory=lambda: [
        PolicyType.EXECUTION_POLICY, PolicyType.PERMISSION_POLICY, PolicyType.RESOURCE_POLICY
    ])
    strict_mode: bool = False
    audit_all: bool = True
    default_action: PolicyAction = PolicyAction.DENY
    custom_policies: List[SafetyPolicy] = field(default_factory=list)
    trusted_scripts: List[str] = field(default_factory=list)
    log_level: str = "INFO"


class ScriptsSafetyPolicyApplier:
    """Main class for applying scripts safety policies."""

    def __init__(self, config: Optional[ScriptsSafetyPolicyConfig] = None):
        self.config = config or ScriptsSafetyPolicyConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._policies = []
        self._load_default_policies()

    def apply_policy(self, script: Dict[str, Any]) -> PolicyApplicationResult:
        """Apply safety policies to a script.
        
        Args:
            script: Script information and content
            
        Returns:
            PolicyApplicationResult: Policy application results
        """
        self.logger.info(f"Applying safety policies to script: {script.get('id', 'unknown')}")
        
        applied_policies = []
        violations = []
        warnings = []
        conditions = []
        
        try:
            script_id = script.get("id", "unknown")
            script_content = script.get("content", "")
            
            # Check if script is trusted
            if script_id in self.config.trusted_scripts:
                return PolicyApplicationResult(
                    allowed=True,
                    applied_policies=["trusted_script"],
                    metadata={"trusted": True}
                )
            
            # Apply each enabled policy type
            for policy_type in self.config.enabled_policies:
                type_policies = [p for p in self._policies if p.policy_type == policy_type and p.enabled]
                type_policies.sort(key=lambda x: x.priority, reverse=True)
                
                for policy in type_policies:
                    result = self._evaluate_policy(policy, script)
                    
                    if result["applied"]:
                        applied_policies.append(policy.id)
                        
                        if result["violation"]:
                            violations.append(result["violation"])
                            
                            # Take action based on policy
                            if policy.action == PolicyAction.DENY:
                                return PolicyApplicationResult(
                                    allowed=False,
                                    applied_policies=applied_policies,
                                    violations=violations,
                                    metadata={"denied_by": policy.id}
                                )
                            elif policy.action == PolicyAction.WARN:
                                warnings.append(f"Policy warning: {policy.name}")
                            elif policy.action == PolicyAction.AUDIT:
                                self._audit_policy_violation(policy, script, result["violation"])
                    
                    if result["condition"]:
                        conditions.append(result["condition"])
            
            # Apply custom policies
            for policy in self.config.custom_policies:
                if policy.enabled:
                    result = self._evaluate_policy(policy, script)
                    if result["applied"]:
                        applied_policies.append(policy.id)
                        if result["violation"]:
                            violations.append(result["violation"])
            
            # Determine if script is allowed
            allowed = not any(v.action == PolicyAction.DENY for v in violations)
            
            policy_result = PolicyApplicationResult(
                allowed=allowed,
                applied_policies=applied_policies,
                violations=violations,
                warnings=warnings,
                conditions=conditions,
                metadata={
                    "applied_at": datetime.utcnow().isoformat(),
                    "script_id": script_id,
                    "script_length": len(script_content),
                    "applier": "ScriptsSafetyPolicyApplier"
                }
            )
            
            # Log audit information
            if self.config.audit_all:
                self._log_policy_application(script, policy_result)
            
            self.logger.info(
                f"Policy application completed: {'allowed' if allowed else 'denied'} "
                f"({len(applied_policies)} policies applied, {len(violations)} violations)"
            )
            
            return policy_result
            
        except Exception as e:
            self.logger.error(f"Policy application failed: {str(e)}")
            return PolicyApplicationResult(
                allowed=False,
                violations=[PolicyViolation(
                    policy_id="system_error",
                    policy_name="System Error",
                    policy_type=PolicyType.EXECUTION_POLICY,
                    action=PolicyAction.DENY,
                    description=f"Policy application failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def _evaluate_policy(self, policy: SafetyPolicy, script: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy against a script."""
        try:
            # Evaluate policy condition
            condition_met = self._evaluate_condition(policy.condition, script)
            
            if condition_met:
                # Create violation if condition is met
                violation = PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    policy_type=policy.policy_type,
                    action=policy.action,
                    description=policy.description,
                    script_content=script.get("content", "")[:100],
                    violation_details={"condition": policy.condition}
                )
                
                return {
                    "applied": True,
                    "violation": violation,
                    "condition": f"Policy {policy.name} triggered"
                }
            
            return {"applied": False, "violation": None, "condition": None}
            
        except Exception as e:
            self.logger.warning(f"Policy evaluation {policy.id} failed: {str(e)}")
            return {"applied": False, "violation": None, "condition": None}

    def _evaluate_condition(self, condition: str, script: Dict[str, Any]) -> bool:
        """Evaluate policy condition."""
        try:
            # Simple keyword-based conditions
            if "dangerous_commands" in condition:
                dangerous = ["rm -rf", "sudo", "chmod 777", "system(", "exec(", "eval("]
                content = script.get("content", "")
                return any(cmd in content for cmd in dangerous)
            
            elif "network_access" in condition:
                network_keywords = ["requests.", "urllib.", "socket.", "http", "ftp", "telnet"]
                content = script.get("content", "")
                return any(keyword in content for keyword in network_keywords)
            
            elif "file_access" in condition:
                file_keywords = ["open(", "file(", "os.remove", "shutil.", "pathlib"]
                content = script.get("content", "")
                return any(keyword in content for keyword in file_keywords)
            
            elif "resource_usage" in condition:
                resource_keywords = ["memory.", "cpu.", "psutil", "subprocess"]
                content = script.get("content", "")
                return any(keyword in content for keyword in resource_keywords)
            
            elif "user_input" in condition:
                input_keywords = ["input(", "raw_input(", "sys.argv", "getopt"]
                content = script.get("content", "")
                return any(keyword in content for keyword in input_keywords)
            
            elif "script_size" in condition:
                size_limit = 1000  # Default limit
                if ">" in condition:
                    size_limit = int(condition.split(">")[1].strip())
                return len(script.get("content", "")) > size_limit
            
            # Evaluate as Python expression if needed
            return eval(condition, {"script": script})
            
        except:
            return False

    def _load_default_policies(self) -> None:
        """Load default safety policies."""
        # Execution policies
        self._policies.extend([
            SafetyPolicy(
                id="no_dangerous_commands",
                name="No Dangerous Commands",
                policy_type=PolicyType.EXECUTION_POLICY,
                description="Blocks scripts with dangerous system commands",
                condition="dangerous_commands",
                action=PolicyAction.DENY,
                priority=100
            ),
            SafetyPolicy(
                id="no_user_input",
                name="No User Input",
                policy_type=PolicyType.EXECUTION_POLICY,
                description="Warns about scripts that accept user input",
                condition="user_input",
                action=PolicyAction.WARN,
                priority=50
            ),
            SafetyPolicy(
                id="script_size_limit",
                name="Script Size Limit",
                policy_type=PolicyType.EXECUTION_POLICY,
                description="Limits script size to prevent large executions",
                condition="script_size > 5000",
                action=PolicyAction.AUDIT,
                priority=30
            )
        ])
        
        # Resource policies
        self._policies.extend([
            SafetyPolicy(
                id="resource_monitoring",
                name="Resource Monitoring",
                policy_type=PolicyType.RESOURCE_POLICY,
                description="Monitors resource usage in scripts",
                condition="resource_usage",
                action=PolicyAction.AUDIT,
                priority=40
            )
        ])
        
        # Network policies
        self._policies.extend([
            SafetyPolicy(
                id="network_access_control",
                name="Network Access Control",
                policy_type=PolicyType.NETWORK_POLICY,
                description="Controls network access in scripts",
                condition="network_access",
                action=PolicyAction.WARN,
                priority=60
            )
        ])
        
        # File system policies
        self._policies.extend([
            SafetyPolicy(
                id="file_access_control",
                name="File Access Control",
                policy_type=PolicyType.FILE_SYSTEM_POLICY,
                description="Controls file system access in scripts",
                condition="file_access",
                action=PolicyAction.AUDIT,
                priority=50
            )
        ])

    def _audit_policy_violation(self, policy: SafetyPolicy, script: Dict[str, Any], violation: PolicyViolation) -> None:
        """Audit a policy violation."""
        audit_log = {
            "timestamp": violation.timestamp.isoformat(),
            "policy_id": policy.id,
            "policy_type": policy.policy_type.value,
            "script_id": script.get("id"),
            "violation": violation.description
        }
        self.logger.warning(f"Policy violation audit: {audit_log}")

    def _log_policy_application(self, script: Dict[str, Any], result: PolicyApplicationResult) -> None:
        """Log policy application details."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "script_id": script.get("id"),
            "allowed": result.allowed,
            "policies_applied": len(result.applied_policies),
            "violations": len(result.violations)
        }
        self.logger.info(f"Policy application log: {log_entry}")

    def add_policy(self, policy: SafetyPolicy) -> None:
        """Add a custom safety policy.
        
        Args:
            policy: Policy to add
        """
        self.logger.info(f"Adding safety policy: {policy.id}")
        self.config.custom_policies.append(policy)

    def remove_policy(self, policy_id: str) -> bool:
        """Remove a safety policy.
        
        Args:
            policy_id: ID of policy to remove
            
        Returns:
            bool: True if policy was removed
        """
        original_length = len(self._policies)
        self._policies = [p for p in self._policies if p.id != policy_id]
        self.config.custom_policies = [p for p in self.config.custom_policies if p.id != policy_id]
        return len(self._policies) < original_length

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of policy configuration.
        
        Returns:
            Dict: Policy configuration summary
        """
        return {
            "enabled_policies": [p.value for p in self.config.enabled_policies],
            "total_policies": len(self._policies) + len(self.config.custom_policies),
            "strict_mode": self.config.strict_mode,
            "audit_all": self.config.audit_all,
            "default_action": self.config.default_action.value,
            "trusted_scripts": len(self.config.trusted_scripts)
        }


# Factory function for easy instantiation
def create_scripts_safety_policy_applier(
    enabled_policies: List[str] = None,
    strict_mode: bool = False,
    audit_all: bool = True,
    **kwargs
) -> ScriptsSafetyPolicyApplier:
    """Create a configured scripts safety policy applier."""
    config = ScriptsSafetyPolicyConfig(
        enabled_policies=[PolicyType(p) for p in (enabled_policies or ["execution_policy", "permission_policy", "resource_policy"])],
        strict_mode=strict_mode,
        audit_all=audit_all,
        **kwargs
    )
    return ScriptsSafetyPolicyApplier(config)


# Convenience function for direct usage
def apply_scripts_safety_policy(
    script: Dict[str, Any],
    policies: List[str] = None,
    strict_mode: bool = False,
    audit_all: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Apply safety policies to a script.
    
    Args:
        script: Script information and content
        policies: List of policy types to apply
        strict_mode: Whether to use strict mode
        audit_all: Whether to audit all applications
        config: Optional applier configuration
        
    Returns:
        Dict: Policy application results
    """
    # Create applier and execute
    applier_config = ScriptsSafetyPolicyConfig(
        enabled_policies=[PolicyType(p) for p in (policies or ["execution_policy", "permission_policy", "resource_policy"])],
        strict_mode=strict_mode,
        audit_all=audit_all,
        **config or {}
    )
    applier = ScriptsSafetyPolicyApplier(applier_config)
    result = applier.apply_policy(script)
    
    # Convert result to dict for JSON serialization
    return {
        "allowed": result.allowed,
        "applied_policies": result.applied_policies,
        "violations": [
            {
                "policy_id": v.policy_id,
                "policy_name": v.policy_name,
                "policy_type": v.policy_type.value,
                "action": v.action.value,
                "description": v.description,
                "script_content": v.script_content,
                "violation_details": v.violation_details,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "conditions": result.conditions,
        "metadata": result.metadata
    }
