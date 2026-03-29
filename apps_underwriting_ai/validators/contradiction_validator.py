"""
Contradiction Validator - Inspects reconciliation findings.
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ..engines.document_reconciliation_engine import ReconciliationResult, ContradictionSeverity


@dataclass
class ContradictionValidationResult:
    """Result of contradiction validation."""
    acceptable: bool = True
    critical_count: int = 0
    major_count: int = 0
    requires_reconciliation: bool = False
    pend_recommended: bool = False
    escalation_recommended: bool = False
    findings: List[Dict[str, Any]] = field(default_factory=list)


class ContradictionValidator:
    """
    Validates that contradictions are within acceptable limits.

    Classifies severity and recommends action:
    - Minor: Accept with note
    - Moderate: May require explanation
    - Major: Consider PEND
    - Critical: ESCALATE or DECLINE
    """

    def validate(
        self,
        reconciliation: ReconciliationResult
    ) -> ContradictionValidationResult:
        """
        Validate reconciliation results.

        Args:
            reconciliation: ReconciliationResult from DocumentReconciliationEngine

        Returns:
            ContradictionValidationResult
        """
        result = ContradictionValidationResult()

        # Count by severity
        for contradiction in reconciliation.contradictions:
            if contradiction.severity == ContradictionSeverity.CRITICAL:
                result.critical_count += 1
            elif contradiction.severity == ContradictionSeverity.MAJOR:
                result.major_count += 1

            # Add to findings
            result.findings.append({
                "field": contradiction.field_name,
                "variance_pct": contradiction.variance_pct,
                "severity": contradiction.severity.value,
                "explanation": contradiction.explanation
            })

        # Determine acceptability
        if result.critical_count > 0:
            result.acceptable = False
            result.escalation_recommended = True
            result.requires_reconciliation = True
        elif result.major_count >= 2:
            result.acceptable = False
            result.pend_recommended = True
            result.requires_reconciliation = True
        elif result.major_count == 1:
            result.acceptable = True  # With explanation
            result.requires_reconciliation = True
        elif reconciliation.pass_rate < 0.7:
            result.acceptable = False
            result.pend_recommended = True

        return result
