"""Schema Safety Policy Application - Applies safety policies to schema operations.

This module provides safety policy enforcement for schema operations,
including schema validation, permission checks, and security controls.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaPolicyType(Enum):
    """Types of schema safety policies."""
    VALIDATION_POLICY = "validation_policy"
    ACCESS_POLICY = "access_policy"
    TRANSFORMATION_POLICY = "transformation_policy"
    ENCRYPTION_POLICY = "encryption_policy"
    RETENTION_POLICY = "retention_policy"
    COMPLIANCE_POLICY = "compliance_policy"


class PolicyAction(Enum):
    """Actions for policy violations."""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"
    TRANSFORM = "transform"


@dataclass
class SchemaSafetyPolicy:
    """Definition of a schema safety policy."""
    id: str
    name: str
    policy_type: SchemaPolicyType
    description: str
    condition: str
    action: PolicyAction
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaPolicyViolation:
    """Record of a schema policy violation."""
    policy_id: str
    policy_name: str
    policy_type: SchemaPolicyType
    action: PolicyAction
    description: str
    schema_path: Optional[str] = None
    violation_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchemaPolicyApplicationResult:
    """Result of schema policy application."""
    allowed: bool
    applied_policies: List[str] = field(default_factory=list)
    violations: List[SchemaPolicyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    transformed_schema: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSafetyPolicyConfig:
    """Configuration for schema safety policy application."""
    enabled_policies: List[SchemaPolicyType] = field(default_factory=lambda: [
        SchemaPolicyType.VALIDATION_POLICY, SchemaPolicyType.ACCESS_POLICY, SchemaPolicyType.COMPLIANCE_POLICY
    ])
    strict_mode: bool = False
    audit_all: bool = True
    default_action: PolicyAction = PolicyAction.DENY
    custom_policies: List[SchemaSafetyPolicy] = field(default_factory=list)
    trusted_schemas: List[str] = field(default_factory=list)
    log_level: str = "INFO"


class SchemaSafetyPolicyApplier:
    """Main class for applying schema safety policies."""

    def __init__(self, config: Optional[SchemaSafetyPolicyConfig] = None):
        self.config = config or SchemaSafetyPolicyConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._policies = []
        self._load_default_policies()

    def apply_policy(self, schema: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> SchemaPolicyApplicationResult:
        """Apply safety policies to a schema.
        
        Args:
            schema: Schema definition
            context: Optional context information
            
        Returns:
            SchemaPolicyApplicationResult: Policy application results
        """
        self.logger.info(f"Applying safety policies to schema")
        
        applied_policies = []
        violations = []
        warnings = []
        conditions = []
        transformed_schema = schema.copy()
        
        try:
            schema_id = schema.get("id", "unknown")
            schema_path = context.get("schema_path", "") if context else ""
            
            # Check if schema is trusted
            if schema_id in self.config.trusted_schemas:
                return SchemaPolicyApplicationResult(
                    allowed=True,
                    applied_policies=["trusted_schema"],
                    metadata={"trusted": True}
                )
            
            # Apply each enabled policy type
            for policy_type in self.config.enabled_policies:
                type_policies = [p for p in self._policies if p.policy_type == policy_type and p.enabled]
                type_policies.sort(key=lambda x: x.priority, reverse=True)
                
                for policy in type_policies:
                    result = self._evaluate_policy(policy, schema, context)
                    
                    if result["applied"]:
                        applied_policies.append(policy.id)
                        
                        if result["violation"]:
                            violations.append(result["violation"])
                            
                            # Take action based on policy
                            if policy.action == PolicyAction.DENY:
                                return SchemaPolicyApplicationResult(
                                    allowed=False,
                                    applied_policies=applied_policies,
                                    violations=violations,
                                    metadata={"denied_by": policy.id}
                                )
                            elif policy.action == PolicyAction.WARN:
                                warnings.append(f"Policy warning: {policy.name}")
                            elif policy.action == PolicyAction.AUDIT:
                                self._audit_policy_violation(policy, schema, result["violation"])
                            elif policy.action == PolicyAction.TRANSFORM:
                                transformed_schema = self._transform_schema(transformed_schema, policy)
                    
                    if result["condition"]:
                        conditions.append(result["condition"])
            
            # Apply custom policies
            for policy in self.config.custom_policies:
                if policy.enabled:
                    result = self._evaluate_policy(policy, schema, context)
                    if result["applied"]:
                        applied_policies.append(policy.id)
                        if result["violation"]:
                            violations.append(result["violation"])
            
            # Determine if schema is allowed
            allowed = not any(v.action == PolicyAction.DENY for v in violations)
            
            policy_result = SchemaPolicyApplicationResult(
                allowed=allowed,
                applied_policies=applied_policies,
                violations=violations,
                warnings=warnings,
                conditions=conditions,
                transformed_schema=transformed_schema if transformed_schema != schema else None,
                metadata={
                    "applied_at": datetime.utcnow().isoformat(),
                    "schema_id": schema_id,
                    "schema_path": schema_path,
                    "applier": "SchemaSafetyPolicyApplier"
                }
            )
            
            # Log audit information
            if self.config.audit_all:
                self._log_policy_application(schema, policy_result)
            
            self.logger.info(
                f"Schema policy application completed: {'allowed' if allowed else 'denied'} "
                f"({len(applied_policies)} policies applied, {len(violations)} violations)"
            )
            
            return policy_result
            
        except Exception as e:
            self.logger.error(f"Schema policy application failed: {str(e)}")
            return SchemaPolicyApplicationResult(
                allowed=False,
                violations=[SchemaPolicyViolation(
                    policy_id="system_error",
                    policy_name="System Error",
                    policy_type=SchemaPolicyType.VALIDATION_POLICY,
                    action=PolicyAction.DENY,
                    description=f"Policy application failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def _evaluate_policy(self, policy: SchemaSafetyPolicy, schema: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a single policy against a schema."""
        try:
            # Evaluate policy condition
            condition_met = self._evaluate_condition(policy.condition, schema, context)
            
            if condition_met:
                # Create violation if condition is met
                violation = SchemaPolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    policy_type=policy.policy_type,
                    action=policy.action,
                    description=policy.description,
                    schema_path=context.get("schema_path", "") if context else "",
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

    def _evaluate_condition(self, condition: str, schema: Dict[str, Any], context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate policy condition."""
        try:
            # Simple keyword-based conditions
            if "sensitive_fields" in condition:
                return self._has_sensitive_fields(schema)
            
            elif "missing_validation" in condition:
                return self._has_missing_validation(schema)
            
            elif "public_schema" in condition:
                return context and context.get("access_level") == "public"
            
            elif "pii_fields" in condition:
                return self._has_pii_fields(schema)
            
            elif "unencrypted_fields" in condition:
                return self._has_unencrypted_fields(schema)
            
            elif "large_schema" in condition:
                field_count = self._count_fields(schema)
                threshold = 100  # Default threshold
                if ">" in condition:
                    threshold = int(condition.split(">")[1].strip())
                return field_count > threshold
            
            # Evaluate as Python expression if needed
            return eval(condition, {"schema": schema, "context": context or {}})
            
        except:
            return False

    def _has_sensitive_fields(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has sensitive fields."""
        sensitive_patterns = ["password", "secret", "token", "key", "credential"]
        fields = self._extract_field_names(schema)
        
        for field in fields:
            if any(pattern in field.lower() for pattern in sensitive_patterns):
                return True
        
        return False

    def _has_missing_validation(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has fields without validation."""
        if "properties" not in schema:
            return False
        
        for field_name, field_def in schema["properties"].items():
            if not any(key in field_def for key in ["type", "enum", "pattern", "minLength", "maxLength"]):
                return True
        
        return False

    def _has_pii_fields(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has PII fields."""
        pii_patterns = ["ssn", "social_security", "credit_card", "email", "phone", "address"]
        fields = self._extract_field_names(schema)
        
        for field in fields:
            if any(pattern in field.lower() for pattern in pii_patterns):
                return True
        
        return False

    def _has_unencrypted_fields(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has unencrypted sensitive fields."""
        if "properties" not in schema:
            return False
        
        sensitive_fields = ["password", "secret", "token", "ssn", "credit_card"]
        
        for field_name, field_def in schema["properties"].items():
            if any(pattern in field_name.lower() for pattern in sensitive_fields):
                if field_def.get("format") != "encrypted" and not field_def.get("encrypted"):
                    return True
        
        return False

    def _count_fields(self, schema: Dict[str, Any]) -> int:
        """Count total fields in schema."""
        if "properties" in schema:
            return len(schema["properties"])
        elif "fields" in schema:
            return len(schema["fields"])
        return 0

    def _extract_field_names(self, schema: Dict[str, Any]) -> List[str]:
        """Extract field names from schema."""
        fields = []
        
        if "properties" in schema:
            fields = list(schema["properties"].keys())
        elif "fields" in schema:
            fields = [f.get("name", "") for f in schema["fields"]]
        
        return fields

    def _transform_schema(self, schema: Dict[str, Any], policy: SchemaSafetyPolicy) -> Dict[str, Any]:
        """Transform schema based on policy."""
        transformed = schema.copy()
        
        if policy.policy_type == SchemaPolicyType.ENCRYPTION_POLICY:
            # Add encryption to sensitive fields
            if "properties" in transformed:
                for field_name, field_def in transformed["properties"].items():
                    if any(pattern in field_name.lower() for pattern in ["password", "secret", "token"]):
                        field_def["format"] = "encrypted"
        
        elif policy.policy_type == SchemaPolicyType.VALIDATION_POLICY:
            # Add default validation
            if "properties" in transformed:
                for field_name, field_def in transformed["properties"].items():
                    if "type" not in field_def:
                        field_def["type"] = "string"
        
        return transformed

    def _load_default_policies(self) -> None:
        """Load default safety policies."""
        # Validation policies
        self._policies.extend([
            SchemaSafetyPolicy(
                id="require_validation",
                name="Require Field Validation",
                policy_type=SchemaPolicyType.VALIDATION_POLICY,
                description="All fields must have validation rules",
                condition="missing_validation",
                action=PolicyAction.WARN,
                priority=100
            ),
            SchemaSafetyPolicy(
                id="limit_schema_size",
                name="Limit Schema Size",
                policy_type=SchemaPolicyType.VALIDATION_POLICY,
                description="Schemas should not exceed field limit",
                condition="large_schema > 200",
                action=PolicyAction.AUDIT,
                priority=50
            )
        ])
        
        # Access policies
        self._policies.extend([
            SchemaSafetyPolicy(
                id="restrict_public_schemas",
                name="Restrict Public Schemas",
                policy_type=SchemaPolicyType.ACCESS_POLICY,
                description="Public schemas cannot contain sensitive fields",
                condition="public_schema and sensitive_fields",
                action=PolicyAction.DENY,
                priority=100
            )
        ])
        
        # Encryption policies
        self._policies.extend([
            SchemaSafetyPolicy(
                id="encrypt_sensitive_data",
                name="Encrypt Sensitive Data",
                policy_type=SchemaPolicyType.ENCRYPTION_POLICY,
                description="Sensitive fields must be marked for encryption",
                condition="unencrypted_fields",
                action=PolicyAction.TRANSFORM,
                priority=80
            )
        ])
        
        # Compliance policies
        self._policies.extend([
            SchemaSafetyPolicy(
                id="pii_protection",
                name="PII Protection",
                policy_type=SchemaPolicyType.COMPLIANCE_POLICY,
                description="PII fields require special handling",
                condition="pii_fields",
                action=PolicyAction.AUDIT,
                priority=70
            )
        ])

    def _audit_policy_violation(self, policy: SchemaSafetyPolicy, schema: Dict[str, Any], violation: SchemaPolicyViolation) -> None:
        """Audit a policy violation."""
        audit_log = {
            "timestamp": violation.timestamp.isoformat(),
            "policy_id": policy.id,
            "policy_type": policy.policy_type.value,
            "schema_id": schema.get("id"),
            "violation": violation.description
        }
        self.logger.warning(f"Schema policy violation audit: {audit_log}")

    def _log_policy_application(self, schema: Dict[str, Any], result: SchemaPolicyApplicationResult) -> None:
        """Log policy application details."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "schema_id": schema.get("id"),
            "allowed": result.allowed,
            "policies_applied": len(result.applied_policies),
            "violations": len(result.violations)
        }
        self.logger.info(f"Schema policy application log: {log_entry}")

    def add_policy(self, policy: SchemaSafetyPolicy) -> None:
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
            "trusted_schemas": len(self.config.trusted_schemas)
        }


# Factory function for easy instantiation
def create_schema_safety_policy_applier(
    enabled_policies: List[str] = None,
    strict_mode: bool = False,
    audit_all: bool = True,
    **kwargs
) -> SchemaSafetyPolicyApplier:
    """Create a configured schema safety policy applier."""
    config = SchemaSafetyPolicyConfig(
        enabled_policies=[SchemaPolicyType(p) for p in (enabled_policies or ["validation_policy", "access_policy", "compliance_policy"])],
        strict_mode=strict_mode,
        audit_all=audit_all,
        **kwargs
    )
    return SchemaSafetyPolicyApplier(config)


# Convenience function for direct usage
def apply_schema_safety_policy(
    schema: Dict[str, Any],
    policies: List[str] = None,
    strict_mode: bool = False,
    audit_all: bool = True,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Apply safety policies to a schema.
    
    Args:
        schema: Schema definition
        policies: List of policy types to apply
        strict_mode: Whether to use strict mode
        audit_all: Whether to audit all applications
        context: Optional context information
        config: Optional applier configuration
        
    Returns:
        Dict: Policy application results
    """
    # Create applier and execute
    applier_config = SchemaSafetyPolicyConfig(
        enabled_policies=[SchemaPolicyType(p) for p in (policies or ["validation_policy", "access_policy", "compliance_policy"])],
        strict_mode=strict_mode,
        audit_all=audit_all,
        **config or {}
    )
    applier = SchemaSafetyPolicyApplier(applier_config)
    result = applier.apply_policy(schema, context)
    
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
                "schema_path": v.schema_path,
                "violation_details": v.violation_details,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "conditions": result.conditions,
        "transformed_schema": result.transformed_schema,
        "metadata": result.metadata
    }
