"""RAG Contracts Checker - Checks RAG operations against defined contracts and SLAs.

This module provides contract checking for RAG operations,
ensuring compliance with service level agreements and operational contracts.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of RAG contracts."""
    PERFORMANCE_CONTRACT = "performance_contract"
    QUALITY_CONTRACT = "quality_contract"
    AVAILABILITY_CONTRACT = "availability_contract"
    SECURITY_CONTRACT = "security_contract"
    COST_CONTRACT = "cost_contract"


class ContractStatus(Enum):
    """Contract compliance status."""
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    EXEMPT = "exempt"


@dataclass
class ContractClause:
    """Definition of a contract clause."""
    id: str
    name: str
    contract_type: ContractType
    condition: str
    threshold: Optional[float] = None
    unit: Optional[str] = None
    penalty: Optional[str] = None
    enabled: bool = True
    description: str = ""


@dataclass
class ContractViolation:
    """Record of a contract violation."""
    clause_id: str
    clause_name: str
    contract_type: ContractType
    severity: str
    actual_value: Optional[Any] = None
    threshold_value: Optional[Any] = None
    penalty_applied: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContractCheckResult:
    """Result of contract checking."""
    operation_id: str
    overall_status: ContractStatus
    violations: List[ContractViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    met_clauses: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGContractsConfig:
    """Configuration for RAG contracts checking."""
    enabled_contracts: List[ContractType] = field(default_factory=lambda: [
        ContractType.PERFORMANCE_CONTRACT, ContractType.QUALITY_CONTRACT
    ])
    auto_apply_penalties: bool = False
    warning_threshold: float = 0.9
    violation_threshold: float = 0.8
    custom_clauses: List[ContractClause] = field(default_factory=list)
    exempt_operations: List[str] = field(default_factory=list)
    log_level: str = "INFO"


class RAGContractsChecker:
    """Main class for RAG contracts checking."""

    def __init__(self, config: Optional[RAGContractsConfig] = None):
        self.config = config or RAGContractsConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._clauses = []
        self._load_default_clauses()

    def check_contracts(self, operation: Dict[str, Any]) -> ContractCheckResult:
        """Check RAG operation against contracts.
        
        Args:
            operation: RAG operation to check
            
        Returns:
            ContractCheckResult: Contract check results
        """
        self.logger.info(f"Checking contracts for operation: {operation.get('id', 'unknown')}")
        
        violations = []
        warnings = []
        met_clauses = []
        performance_metrics = {}
        
        try:
            operation_id = operation.get("id", "unknown")
            
            # Skip exempt operations
            if operation_id in self.config.exempt_operations:
                return ContractCheckResult(
                    operation_id=operation_id,
                    overall_status=ContractStatus.EXEMPT,
                    metadata={"exempt": True}
                )
            
            # Check each enabled contract type
            for contract_type in self.config.enabled_contracts:
                type_clauses = [c for c in self._clauses if c.contract_type == contract_type and c.enabled]
                
                for clause in type_clauses:
                    # Check clause compliance
                    violation = self._check_clause(clause, operation)
                    
                    if violation:
                        violations.append(violation)
                        
                        # Apply penalty if configured
                        if self.config.auto_apply_penalties and violation.penalty_applied:
                            self._apply_penalty(operation, violation)
                    else:
                        met_clauses.append(clause.id)
            
            # Check custom clauses
            for clause in self.config.custom_clauses:
                if clause.enabled:
                    violation = self._check_clause(clause, operation)
                    if violation:
                        violations.append(violation)
                    else:
                        met_clauses.append(clause.id)
            
            # Extract performance metrics
            performance_metrics = self._extract_performance_metrics(operation)
            
            # Determine overall status
            overall_status = self._determine_contract_status(violations, warnings)
            
            result = ContractCheckResult(
                operation_id=operation_id,
                overall_status=overall_status,
                violations=violations,
                warnings=warnings,
                met_clauses=met_clauses,
                performance_metrics=performance_metrics,
                metadata={
                    "checked_at": datetime.utcnow().isoformat(),
                    "contracts_checked": [c.value for c in self.config.enabled_contracts],
                    "total_clauses": len(self._clauses) + len(self.config.custom_clauses),
                    "checker": "RAGContractsChecker"
                }
            )
            
            self.logger.info(
                f"Contract check completed: {overall_status.value} "
                f"(violations: {len(violations)}, met: {len(met_clauses)})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Contract check failed: {str(e)}")
            return ContractCheckResult(
                operation_id=operation.get("id", "unknown"),
                overall_status=ContractStatus.VIOLATION,
                violations=[ContractViolation(
                    clause_id="system_error",
                    clause_name="System Error",
                    contract_type=ContractType.PERFORMANCE_CONTRACT,
                    severity="critical",
                    penalty_applied="Operation blocked"
                )],
                metadata={"error": str(e)}
            )

    def _check_clause(self, clause: ContractClause, operation: Dict[str, Any]) -> Optional[ContractViolation]:
        """Check a single contract clause."""
        try:
            # Extract relevant metric
            actual_value = self._extract_metric_value(operation, clause.condition)
            
            if actual_value is None:
                return None
            
            # Check against threshold
            if clause.threshold is not None:
                if self._is_violation(actual_value, clause.threshold, clause.condition):
                    return ContractViolation(
                        clause_id=clause.id,
                        clause_name=clause.name,
                        contract_type=clause.contract_type,
                        severity="high" if actual_value < clause.threshold * 0.5 else "medium",
                        actual_value=actual_value,
                        threshold_value=clause.threshold,
                        penalty_applied=clause.penalty
                    )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Clause check {clause.id} failed: {str(e)}")
            return None

    def _extract_metric_value(self, operation: Dict[str, Any], condition: str) -> Optional[float]:
        """Extract metric value from operation based on condition."""
        if "response_time" in condition:
            return operation.get("response_time_ms", 0) / 1000.0  # Convert to seconds
        elif "accuracy" in condition:
            return operation.get("accuracy_score", 0.0)
        elif "availability" in condition:
            return operation.get("availability_percentage", 100.0)
        elif "cost" in condition:
            return operation.get("operation_cost", 0.0)
        elif "throughput" in condition:
            return operation.get("requests_per_second", 0.0)
        elif "latency" in condition:
            return operation.get("latency_ms", 0)
        elif "error_rate" in condition:
            return operation.get("error_rate", 0.0)
        
        return None

    def _is_violation(self, actual: float, threshold: float, condition: str) -> bool:
        """Determine if actual value violates threshold."""
        # For metrics where lower is better (response time, latency, error rate, cost)
        if any(metric in condition.lower() for metric in ["response_time", "latency", "error_rate", "cost"]):
            return actual > threshold
        
        # For metrics where higher is better (accuracy, availability, throughput)
        return actual < threshold

    def _extract_performance_metrics(self, operation: Dict[str, Any]) -> Dict[str, float]:
        """Extract performance metrics from operation."""
        return {
            "response_time_s": operation.get("response_time_ms", 0) / 1000.0,
            "accuracy": operation.get("accuracy_score", 0.0),
            "availability": operation.get("availability_percentage", 100.0),
            "cost": operation.get("operation_cost", 0.0),
            "throughput": operation.get("requests_per_second", 0.0),
            "latency_ms": operation.get("latency_ms", 0),
            "error_rate": operation.get("error_rate", 0.0)
        }

    def _determine_contract_status(self, violations: List[ContractViolation], warnings: List[str]) -> ContractStatus:
        """Determine overall contract status."""
        if not violations and not warnings:
            return ContractStatus.COMPLIANT
        elif any(v.severity == "critical" for v in violations):
            return ContractStatus.VIOLATION
        elif violations:
            return ContractStatus.VIOLATION
        elif warnings:
            return ContractStatus.WARNING
        else:
            return ContractStatus.COMPLIANT

    def _apply_penalty(self, operation: Dict[str, Any], violation: ContractViolation) -> None:
        """Apply penalty for contract violation."""
        if violation.penalty_applied:
            operation["penalty"] = violation.penalty_applied
            operation["violation_reason"] = f"Contract violation: {violation.clause_name}"
            self.logger.warning(f"Applied penalty for {violation.clause_id}: {violation.penalty_applied}")

    def _load_default_clauses(self) -> None:
        """Load default contract clauses."""
        # Performance contract clauses
        self._clauses.extend([
            ContractClause(
                id="response_time_sla",
                name="Response Time SLA",
                contract_type=ContractType.PERFORMANCE_CONTRACT,
                condition="response_time",
                threshold=2.0,  # 2 seconds
                unit="seconds",
                penalty="Throttle requests",
                description="Maximum response time for operations"
            ),
            ContractClause(
                id="throughput_sla",
                name="Throughput SLA",
                contract_type=ContractType.PERFORMANCE_CONTRACT,
                condition="throughput",
                threshold=100.0,  # 100 requests per second
                unit="requests/second",
                penalty="Scale down resources",
                description="Minimum throughput requirement"
            ),
            ContractClause(
                id="latency_sla",
                name="Latency SLA",
                contract_type=ContractType.PERFORMANCE_CONTRACT,
                condition="latency",
                threshold=500.0,  # 500 milliseconds
                unit="milliseconds",
                penalty="Add latency warning",
                description="Maximum latency allowed"
            )
        ])
        
        # Quality contract clauses
        self._clauses.extend([
            ContractClause(
                id="accuracy_sla",
                name="Accuracy SLA",
                contract_type=ContractType.QUALITY_CONTRACT,
                condition="accuracy",
                threshold=0.85,  # 85% accuracy
                unit="percentage",
                penalty="Quality review required",
                description="Minimum accuracy requirement"
            ),
            ContractClause(
                id="error_rate_sla",
                name="Error Rate SLA",
                contract_type=ContractType.QUALITY_CONTRACT,
                condition="error_rate",
                threshold=0.05,  # 5% error rate
                unit="percentage",
                penalty="Error notification sent",
                description="Maximum error rate allowed"
            )
        ])
        
        # Availability contract clauses
        self._clauses.extend([
            ContractClause(
                id="availability_sla",
                name="Availability SLA",
                contract_type=ContractType.AVAILABILITY_CONTRACT,
                condition="availability",
                threshold=99.9,  # 99.9% availability
                unit="percentage",
                penalty="Service credit applied",
                description="Minimum availability requirement"
            )
        ])
        
        # Cost contract clauses
        self._clauses.extend([
            ContractClause(
                id="cost_threshold",
                name="Cost Threshold",
                contract_type=ContractType.COST_CONTRACT,
                condition="cost",
                threshold=0.10,  # $0.10 per operation
                unit="dollars",
                penalty="Cost alert triggered",
                description="Maximum cost per operation"
            )
        ])

    def add_clause(self, clause: ContractClause) -> None:
        """Add a custom contract clause.
        
        Args:
            clause: Clause to add
        """
        self.logger.info(f"Adding contract clause: {clause.id}")
        self.config.custom_clauses.append(clause)

    def get_contract_summary(self) -> Dict[str, Any]:
        """Get summary of contract configuration.
        
        Returns:
            Dict: Contract configuration summary
        """
        return {
            "enabled_contracts": [c.value for c in self.config.enabled_contracts],
            "total_clauses": len(self._clauses) + len(self.config.custom_clauses),
            "auto_apply_penalties": self.config.auto_apply_penalties,
            "warning_threshold": self.config.warning_threshold,
            "violation_threshold": self.config.violation_threshold,
            "exempt_operations": len(self.config.exempt_operations)
        }


# Factory function for easy instantiation
def create_rag_contracts_checker(
    enabled_contracts: List[str] = None,
    auto_apply_penalties: bool = False,
    warning_threshold: float = 0.9,
    **kwargs
) -> RAGContractsChecker:
    """Create a configured RAG contracts checker."""
    config = RAGContractsConfig(
        enabled_contracts=[ContractType(c) for c in (enabled_contracts or ["performance_contract", "quality_contract"])],
        auto_apply_penalties=auto_apply_penalties,
        warning_threshold=warning_threshold,
        **kwargs
    )
    return RAGContractsChecker(config)


# Convenience function for direct usage
def check_rag_contracts(
    operation: Dict[str, Any],
    contracts: List[str] = None,
    auto_apply_penalties: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Check RAG operation against contracts.
    
    Args:
        operation: RAG operation to check
        contracts: List of contract types to check
        auto_apply_penalties: Whether to automatically apply penalties
        config: Optional checker configuration
        
    Returns:
        Dict: Contract check results
    """
    # Create checker and execute
    checker_config = RAGContractsConfig(
        enabled_contracts=[ContractType(c) for c in (contracts or ["performance_contract", "quality_contract"])],
        auto_apply_penalties=auto_apply_penalties,
        **config or {}
    )
    checker = RAGContractsChecker(checker_config)
    result = checker.check_contracts(operation)
    
    # Convert result to dict for JSON serialization
    return {
        "operation_id": result.operation_id,
        "overall_status": result.overall_status.value,
        "violations": [
            {
                "clause_id": v.clause_id,
                "clause_name": v.clause_name,
                "contract_type": v.contract_type.value,
                "severity": v.severity,
                "actual_value": v.actual_value,
                "threshold_value": v.threshold_value,
                "penalty_applied": v.penalty_applied,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "met_clauses": result.met_clauses,
        "performance_metrics": result.performance_metrics,
        "metadata": result.metadata
    }
