"""
L5 - Safety/Policy Layer - Policy Interface and Engine

Defines the policy interface and implements the safety engine.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, TypeVar, Generic, Type
from dataclasses import dataclass, field
import logging
import uuid
from datetime import datetime

from .types import (
    SafetyContext,
    SafetyFinding,
    PolicyDecision,
    Verdict,
    Severity,
    SafetyPolicy,
    SafetyError,
    PolicyEvaluationError,
    PolicyConfigurationError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class PolicyResult:
    """Result of evaluating multiple policies."""
    decisions: List[PolicyDecision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def final_verdict(self) -> Verdict:
        """Determine the overall verdict based on all policy decisions."""
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
        """Get all findings that would cause a block."""
        return [f for f in self.all_findings if f.severity >= Severity.HIGH]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'verdict': self.final_verdict.value,
            'decisions': [d.to_dict() for d in self.decisions],
            'metadata': self.metadata
        }

class SafetyEngine:
    """
    Executes safety policies and aggregates their results.
    
    The safety engine is responsible for:
    1. Managing a collection of safety policies
    2. Evaluating content against all relevant policies
    3. Aggregating and resolving policy decisions
    4. Providing detailed feedback on policy violations
    """
    
    def __init__(self, policies: Optional[List[SafetyPolicy]] = None):
        """Initialize the safety engine with optional initial policies."""
        self._policies: Dict[str, SafetyPolicy] = {}
        self._default_severity_threshold = Severity.HIGH
        
        if policies:
            for policy in policies:
                self.add_policy(policy)
    
    def add_policy(self, policy: SafetyPolicy) -> None:
        """Add a policy to the engine."""
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
        """Remove a policy from the engine."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            logger.info(f"Removed policy: {policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[SafetyPolicy]:
        """Get a policy by ID."""
        return self._policies.get(policy_id)
    
    def list_policies(self) -> List[SafetyPolicy]:
        """Get all registered policies."""
        return list(self._policies.values())
    
    def evaluate(
        self,
        context: SafetyContext,
        policy_ids: Optional[List[str]] = None,
        severity_threshold: Optional[Severity] = None
    ) -> PolicyResult:
        """
        Evaluate the given context against all relevant policies.
        
        Args:
            context: The safety context to evaluate
            policy_ids: Optional list of policy IDs to evaluate against.
                      If None, evaluates against all policies.
            severity_threshold: Minimum severity level to consider for blocking.
                             If None, uses the engine's default.
        
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
                "evaluated_at": datetime.utcnow().isoformat(),
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
        """Get the list of policies to evaluate."""
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
