"""
L5 safety and policy engine for resume job alignment workflows.

Defines policy interface and implements safety engine for resume enhancement.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
import logging
import uuid
from datetime import datetime, UTC

from .types import (
    SafetyContext,
    SafetyFinding,
    PolicyDecision,
    Verdict,
    Severity,
    SafetyPolicy
)

logger = logging.getLogger(__name__)


class PolicyConfigurationError(Exception):
    """Raised when resume workflow policy configuration is invalid."""
    pass


T = TypeVar('T')

@dataclass
class PolicyResult:
    """Result of evaluating resume workflow policies for enhancement."""
    decisions: List[PolicyDecision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def final_verdict(self) -> Verdict:
        """Determines overall verdict for resume workflow policy decisions."""
        if not self.decisions:
            return Verdict.ALLOW
            
        # Most restrictive verdict wins
        verdicts = [d.verdict for d in self.decisions]
        if Verdict.BLOCK in verdicts:
            return Verdict.BLOCK
        elif Verdict.REVIEW in verdicts:
            return Verdict.REVIEW
        return Verdict.ALLOW
    
    @property
    def all_findings(self) -> List[SafetyFinding]:
        """Get all findings from all policy decisions."""
        findings = []
        for decision in self.decisions:
            findings.extend(decision.findings)
        return findings
    
    @property
    def blocking_findings(self) -> List[SafetyFinding]:
        """Gets all findings that would block resume workflow operations."""
        return [f for f in self.all_findings if f.severity >= Severity.HIGH]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts resume workflow policy result to dictionary format."""
        return {
            'verdict': self.final_verdict.value,
            'decisions': [d.to_dict() for d in self.decisions],
            'metadata': self.metadata
        }

class SafetyEngine:
    """
    Executes safety policies for resume job alignment workflows.

    Manages policies, evaluates content, and aggregates decisions for enhancement.
    """
    
    def __init__(self, policies: Optional[List[SafetyPolicy]] = None):
        """Initializes safety engine for resume workflow policies."""
        self._policies: Dict[str, SafetyPolicy] = {}
        self._default_severity_threshold = Severity.HIGH
        
        if policies:
            for policy in policies:
                self.add_policy(policy)
    
    def add_policy(self, policy: SafetyPolicy) -> None:
        """Adds resume workflow safety policy to the engine."""
        if not isinstance(policy, SafetyPolicy):
            raise PolicyConfigurationError(
                f"Policy {policy} does not implement SafetyPolicy protocol"
            )
        
        if policy.policy_id in self._policies:
            raise PolicyConfigurationError(
                f"Policy with ID '{policy.policy_id}' already exists"
            )
        
        self._policies[policy.policy_id] = policy
        logger.info(f"Added policy: {policy.policy_id} - {policy.description}")
    
    def remove_policy(self, policy_id: str) -> None:
        """Removes resume workflow safety policy from the engine."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            logger.info(f"Removed policy: {policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[SafetyPolicy]:
        """Gets resume workflow safety policy by ID."""
        return self._policies.get(policy_id)
    
    def list_policies(self) -> List[SafetyPolicy]:
        """Gets all registered resume workflow safety policies."""
        return list(self._policies.values())
    
    def evaluate(
        self,
        context: SafetyContext,
        policy_ids: Optional[List[str]] = None,
        severity_threshold: Optional[Severity] = None
    ) -> PolicyResult:
        """
        Evaluates resume workflow context against relevant safety policies.
        
        Args:
            context: Safety context for resume enhancement evaluation
            policy_ids: Optional policy IDs to evaluate against
            severity_threshold: Minimum severity for blocking operations
        
        Returns:
            PolicyResult with the combined results of all policy evaluations
        """
        if not self._policies:
            logger.warning("No policies registered in safety engine")
            return PolicyResult()
        
        threshold = severity_threshold or self._default_severity_threshold
        policies_to_evaluate = self._get_policies_to_evaluate(policy_ids)
        
        if not policies_to_evaluate:
            logger.warning(f"No matching policies found for IDs: {policy_ids}")
            return PolicyResult()
        
        decisions: List[PolicyDecision] = []
        
        for policy in policies_to_evaluate:
            try:
                decision = policy.evaluate(context)
                decisions.append(decision)
                
                logger.debug(
                    f"Policy '{policy.policy_id}' returned verdict: {decision.verdict} "
                    f"with {len(decision.findings)} findings"
                )
                
            except Exception as e:
                error_msg = f"Policy evaluation failed for {policy.policy_id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Create a blocking decision for the failed policy
                decisions.append(PolicyDecision(
                    policy_id=policy.policy_id,
                    verdict=Verdict.BLOCK,
                    findings=[
                        SafetyFinding(
                            id=f"error-{uuid.uuid4()}",
                            type="policy",
                            severity=Severity.CRITICAL,
                            message=f"Policy evaluation failed: {str(e)}",
                            details={"error": str(e)},
                            location=policy.policy_id
                        )
                    ]
                ))
        
        # Create the final result
        result = PolicyResult(
            decisions=decisions,
            metadata={
                "evaluated_at": datetime.now(UTC).isoformat(),
                "policy_count": len(decisions),
                "finding_count": sum(len(d.findings) for d in decisions),
                "severity_threshold": threshold.value,
                "context": {
                    "content_type": context.content_type,
                    "source": context.source,
                    "destination": context.destination,
                    "user_id": context.user_id,
                    "session_id": context.session_id,
                    "metadata_keys": list(context.metadata.keys())
                }
            }
        )
        
        logger.info(
            f"Safety evaluation complete. Verdict: {result.final_verdict}. "
            f"Findings: {len(result.all_findings)} total, "
            f"{len(result.blocking_findings)} blocking"
        )
        
        return result
    
    def _get_policies_to_evaluate(
        self,
        policy_ids: Optional[List[str]] = None
    ) -> List[SafetyPolicy]:
        """Gets list of resume workflow policies to evaluate."""
        if policy_ids is None:
            return list(self._policies.values())
        
        policies = []
        for pid in policy_ids:
            if pid in self._policies:
                policies.append(self._policies[pid])
            else:
                logger.warning(f"Policy not found: {pid}")
        
        return policies
    
    def check_safe(
        self,
        context: SafetyContext,
        policy_ids: Optional[List[str]] = None,
        severity_threshold: Optional[Severity] = None
    ) -> bool:
        """
        Check if the given context is safe according to the specified policies.
        
        This is a convenience method that returns a simple boolean indicating
        whether the content is safe (True) or should be blocked (False).
        
        Args:
            context: The safety context to evaluate
            policy_ids: Optional list of policy IDs to evaluate against
            severity_threshold: Minimum severity level to consider for blocking
            
        Returns:
            bool: True if the content is safe, False if it should be blocked
        """
        result = self.evaluate(context, policy_ids, severity_threshold)
        return result.final_verdict != Verdict.BLOCK



