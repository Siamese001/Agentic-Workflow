"""RAG Contracts Enforcement - Enforces RAG system contracts and policies.

This module provides contract validation and enforcement for RAG operations,
ensuring compliance with defined policies and constraints.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of RAG contracts."""
    RETRIEVAL_CONTRACT = "retrieval_contract"
    GENERATION_CONTRACT = "generation_contract"
    SECURITY_CONTRACT = "security_contract"
    PERFORMANCE_CONTRACT = "performance_contract"
    QUALITY_CONTRACT = "quality_contract"


class EnforcementLevel(Enum):
    """Levels of contract enforcement."""
    WARN = "warn"
    BLOCK = "block"
    LOG = "log"
    AUDIT = "audit"


class ViolationSeverity(Enum):
    """Severity levels for contract violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContractRule:
    """Definition of a contract rule."""
    id: str
    name: str
    contract_type: ContractType
    condition: str  # Expression to evaluate
    enforcement_level: EnforcementLevel
    severity: ViolationSeverity
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractViolation:
    """Record of a contract violation."""
    rule_id: str
    rule_name: str
    severity: ViolationSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EnforcementResult:
    """Result of contract enforcement."""
    compliant: bool
    violations: List[ContractViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    enforced_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGContractsConfig:
    """Configuration for RAG contracts enforcement."""
    enable_enforcement: bool = True
    default_enforcement_level: str = "warn"
    max_violations_per_request: int = 10
    audit_logging: bool = True
    violation_threshold: Dict[str, int] = field(default_factory=lambda: {
        "low": 100,
        "medium": 50,
        "high": 10,
        "critical": 1
    })
    custom_validators: Dict[str, Callable] = field(default_factory=dict)
    log_level: str = "INFO"


class RAGContractsEnforcer:
    """Main class for enforcing RAG contracts."""

    def __init__(self, config: Optional[RAGContractsConfig] = None):
        self.config = config or RAGContractsConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._rules = {}
        self._violation_counts = {}
        self._load_default_rules()

    def enforce(self, operation: Dict[str, Any]) -> EnforcementResult:
        """Enforce contracts on a RAG operation.
        
        Args:
            operation: RAG operation data to validate
            
        Returns:
            EnforcementResult: Result of contract enforcement
        """
        self.logger.info(f"Enforcing RAG contracts on operation: {operation.get('type', 'unknown')}")
        
        if not self.config.enable_enforcement:
            return EnforcementResult(
                compliant=True,
                metadata={"enforcement_disabled": True}
            )
        
        violations = []
        warnings = []
        enforced_actions = []
        
        try:
            # Get relevant rules for operation type
            relevant_rules = self._get_relevant_rules(operation)
            
            # Evaluate each rule
            for rule in relevant_rules:
                violation = self._evaluate_rule(rule, operation)
                
                if violation:
                    violations.append(violation)
                    
                    # Track violation counts
                    self._track_violation(rule.id, violation.severity)
                    
                    # Take enforcement action
                    action = self._take_enforcement_action(rule, violation, operation)
                    if action:
                        enforced_actions.append(action)
                    
                    # Add warning if needed
                    if rule.enforcement_level == EnforcementLevel.WARN:
                        warnings.append(f"Warning: {violation.message}")
            
            # Determine compliance
            compliant = len(violations) == 0
            
            result = EnforcementResult(
                compliant=compliant,
                violations=violations,
                warnings=warnings,
                enforced_actions=enforced_actions,
                metadata={
                    "enforced_at": datetime.utcnow().isoformat(),
                    "rules_evaluated": len(relevant_rules),
                    "enforcer": "RAGContractsEnforcer"
                }
            )
            
            # Log audit information
            if self.config.audit_logging:
                self._log_audit_result(operation, result)
            
            self.logger.info(
                f"Contract enforcement completed: {'compliant' if compliant else 'non-compliant'} "
                f"({len(violations)} violations)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Contract enforcement failed: {str(e)}")
            return EnforcementResult(
                compliant=False,
                violations=[ContractViolation(
                    rule_id="system_error",
                    rule_name="System Error",
                    severity=ViolationSeverity.HIGH,
                    message=f"Enforcement failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def add_rule(self, rule: ContractRule) -> None:
        """Add a new contract rule.
        
        Args:
            rule: Contract rule to add
        """
        self.logger.info(f"Adding contract rule: {rule.id}")
        self._rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a contract rule.
        
        Args:
            rule_id: ID of rule to remove
            
        Returns:
            bool: True if rule was removed
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            self.logger.info(f"Removed contract rule: {rule_id}")
            return True
        return False

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of contract violations.
        
        Returns:
            Dict: Violation statistics
        """
        summary = {
            "total_violations": 0,
            "by_severity": {},
            "by_rule": {},
            "recent_violations": []
        }
        
        for severity, count in self._violation_counts.items():
            summary["by_severity"][severity] = count
            summary["total_violations"] += count
        
        return summary

    def _load_default_rules(self) -> None:
        """Load default RAG contract rules."""
        # Retrieval contract rules
        self.add_rule(ContractRule(
            id="max_retrieval_docs",
            name="Maximum Retrieval Documents",
            contract_type=ContractType.RETRIEVAL_CONTRACT,
            condition="operation.get('retrieved_docs', 0) > 50",
            enforcement_level=EnforcementLevel.WARN,
            severity=ViolationSeverity.MEDIUM,
            description="Limits number of documents retrieved in a single operation"
        ))
        
        self.add_rule(ContractRule(
            id="min_similarity_threshold",
            name="Minimum Similarity Threshold",
            contract_type=ContractType.RETRIEVAL_CONTRACT,
            condition="operation.get('similarity_threshold', 1.0) < 0.5",
            enforcement_level=EnforcementLevel.BLOCK,
            severity=ViolationSeverity.HIGH,
            description="Enforces minimum similarity threshold for retrieval"
        ))
        
        # Generation contract rules
        self.add_rule(ContractRule(
            id="max_generation_tokens",
            name="Maximum Generation Tokens",
            contract_type=ContractType.GENERATION_CONTRACT,
            condition="operation.get('generated_tokens', 0) > 1000",
            enforcement_level=EnforcementLevel.WARN,
            severity=ViolationSeverity.MEDIUM,
            description="Limits tokens generated in a single response"
        ))
        
        # Security contract rules
        self.add_rule(ContractRule(
            id="no_pii_in_query",
            name="No PII in Query",
            contract_type=ContractType.SECURITY_CONTRACT,
            condition="'ssn' in operation.get('query', '').lower() or 'credit_card' in operation.get('query', '').lower()",
            enforcement_level=EnforcementLevel.BLOCK,
            severity=ViolationSeverity.CRITICAL,
            description="Blocks queries containing potential PII"
        ))
        
        # Performance contract rules
        self.add_rule(ContractRule(
            id="max_response_time",
            name="Maximum Response Time",
            contract_type=ContractType.PERFORMANCE_CONTRACT,
            condition="operation.get('response_time_ms', 0) > 5000",
            enforcement_level=EnforcementLevel.AUDIT,
            severity=ViolationSeverity.MEDIUM,
            description="Audits operations exceeding response time threshold"
        ))

    def _get_relevant_rules(self, operation: Dict[str, Any]) -> List[ContractRule]:
        """Get rules relevant to the operation."""
        relevant = []
        op_type = operation.get("type", "").lower()
        
        for rule in self._rules.values():
            # Check if rule applies to operation type
            if self._rule_applies_to_operation(rule, op_type):
                relevant.append(rule)
        
        return relevant

    def _rule_applies_to_operation(self, rule: ContractRule, operation_type: str) -> bool:
        """Check if rule applies to operation type."""
        if rule.contract_type == ContractType.RETRIEVAL_CONTRACT:
            return "retrieval" in operation_type or "search" in operation_type
        elif rule.contract_type == ContractType.GENERATION_CONTRACT:
            return "generation" in operation_type or "llm" in operation_type
        elif rule.contract_type == ContractType.SECURITY_CONTRACT:
            return True  # Security applies to all
        elif rule.contract_type == ContractType.PERFORMANCE_CONTRACT:
            return True  # Performance applies to all
        elif rule.contract_type == ContractType.QUALITY_CONTRACT:
            return "retrieval" in operation_type or "generation" in operation_type
        
        return False

    def _evaluate_rule(self, rule: ContractRule, operation: Dict[str, Any]) -> Optional[ContractViolation]:
        """Evaluate a rule against the operation."""
        try:
            # Evaluate condition
            if eval(rule.condition, {"operation": operation}):
                return ContractViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Contract violation: {rule.description}",
                    context={"operation_type": operation.get("type")}
                )
        except Exception as e:
            self.logger.warning(f"Failed to evaluate rule {rule.id}: {str(e)}")
        
        return None

    def _take_enforcement_action(self, rule: ContractRule, violation: ContractViolation, operation: Dict[str, Any]) -> Optional[str]:
        """Take enforcement action based on rule and violation."""
        if rule.enforcement_level == EnforcementLevel.BLOCK:
            # Block the operation
            operation["blocked"] = True
            operation["block_reason"] = violation.message
            return f"Blocked operation due to {rule.id} violation"
        
        elif rule.enforcement_level == EnforcementLevel.WARN:
            # Add warning to operation
            if "warnings" not in operation:
                operation["warnings"] = []
            operation["warnings"].append(violation.message)
            return f"Added warning for {rule.id} violation"
        
        elif rule.enforcement_level == EnforcementLevel.AUDIT:
            # Log for audit
            self.logger.warning(f"Audit: {violation.message}")
            return f"Audited {rule.id} violation"
        
        return None

    def _track_violation(self, rule_id: str, severity: ViolationSeverity) -> None:
        """Track violation counts."""
        key = f"{rule_id}_{severity.value}"
        self._violation_counts[key] = self._violation_counts.get(key, 0) + 1
        
        # Check if threshold exceeded
        threshold = self.config.violation_threshold.get(severity.value, 0)
        if self._violation_counts[key] > threshold:
            self.logger.error(
                f"Violation threshold exceeded for {rule_id} ({severity.value}): "
                f"{self._violation_counts[key]} > {threshold}"
            )

    def _log_audit_result(self, operation: Dict[str, Any], result: EnforcementResult) -> None:
        """Log audit information."""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_id": operation.get("id"),
            "operation_type": operation.get("type"),
            "compliant": result.compliant,
            "violation_count": len(result.violations),
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity.value,
                    "message": v.message
                }
                for v in result.violations
            ]
        }
        
        self.logger.info(f"Audit log: {audit_log}")


# Factory function for easy instantiation
def create_rag_contracts_enforcer(
    enable_enforcement: bool = True,
    default_enforcement_level: str = "warn",
    audit_logging: bool = True,
    **kwargs
) -> RAGContractsEnforcer:
    """Create a configured RAG contracts enforcer."""
    config = RAGContractsConfig(
        enable_enforcement=enable_enforcement,
        default_enforcement_level=default_enforcement_level,
        audit_logging=audit_logging,
        **kwargs
    )
    return RAGContractsEnforcer(config)


# Convenience function for direct usage
def enforce_rag_contracts(
    operation: Dict[str, Any],
    enable_enforcement: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enforce RAG contracts on an operation.
    
    Args:
        operation: RAG operation to validate
        enable_enforcement: Whether to enable enforcement
        config: Optional enforcer configuration overrides
        
    Returns:
        Dict: Enforcement result with violations and actions
    """
    # Create enforcer and execute
    enforcer_config = RAGContractsConfig(
        enable_enforcement=enable_enforcement,
        **config or {}
    )
    enforcer = RAGContractsEnforcer(enforcer_config)
    result = enforcer.enforce(operation)
    
    # Convert result to dict for JSON serialization
    return {
        "compliant": result.compliant,
        "violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "severity": v.severity.value,
                "message": v.message,
                "context": v.context,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "enforced_actions": result.enforced_actions,
        "metadata": result.metadata
    }
