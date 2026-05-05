"""HITL Escalation Integration for apps_lic — L5 Safety.

Wave 3, Phase 3 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides the integration layer between HITL policy evaluation
and coordination fabric wake handling, implementing the escalation path.

App: apps_lic
Layer: Integration (apps_lic/coordination/)

Dependencies:
    - HITL Policy Evaluator (agentic_core/L5_safety/evaluators/apps_lic_reengagement.py)
    - Wake Handler (apps_lic/coordination/wake_handler.py)
    - Touch State (agentic_core/L4_state/uwg/touch_state_writer.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime, timezone

from agentic_core.L5_safety.evaluators.apps_lic_reengagement import (
    PolicyEvalRequest,
    PolicyEvalResult,
    ReengagementPolicyEvaluator,
)
from agentic_core.L5_safety.policy.apps_lic_reengagement import (
    HITLReviewRequest,
    HITLReviewResult,
    HITLResolution,
    HITLReviewType,
    HITLPolicyRegistry,
)


# -----------------------------------------------------------------------------
# HITL Client Interface
# -----------------------------------------------------------------------------

class HITLClient:
    """Client interface for HITL operations.
    
    This is the abstract interface that must be implemented by the
    actual HITL system. The apps_lic coordination layer uses this
    interface to create and check reviews.
    
    Implementations should handle:
    - Review queue management
    - Notification to human reviewers
    - Review resolution tracking
    - SLA enforcement
    """
    
    def create_review(self, request: HITLReviewRequest) -> str:
        """Create a new HITL review.
        
        Parameters
        ----------
        request : HITLReviewRequest
            Review request details
        
        Returns
        -------
        str
            Review ID
        
        Raises
        ------
        HITLEscalationError
            If review creation fails
        """
        raise NotImplementedError("HITLClient.create_review must be implemented")
    
    def get_review_status(self, review_id: str) -> dict[str, Any]:
        """Get status of a review.
        
        Parameters
        ----------
        review_id : str
            Review to check
        
        Returns
        -------
        dict
            {"status": "pending|resolved", "result": HITLReviewResult|None}
        """
        raise NotImplementedError("HITLClient.get_review_status must be implemented")
    
    def resolve_review(
        self,
        review_id: str,
        resolution: HITLResolution,
        resolved_by: str,
        notes: str = "",
        modifications: Optional[dict] = None,
    ) -> HITLReviewResult:
        """Resolve a review (called by HITL UI/workflow).
        
        Parameters
        ----------
        review_id : str
            Review to resolve
        resolution : HITLResolution
            Resolution outcome
        resolved_by : str
            Who resolved it
        notes : str
            Reviewer notes
        modifications : Optional[dict]
            Any modifications made
        
        Returns
        -------
        HITLReviewResult
            Resolution result
        """
        raise NotImplementedError("HITLClient.resolve_review must be implemented")


# -----------------------------------------------------------------------------
# Escalation Error
# -----------------------------------------------------------------------------

class HITLEscalationError(Exception):
    """Error during HITL escalation."""
    
    def __init__(
        self,
        message: str,
        touch_id: Optional[str] = None,
        review_id: Optional[str] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.touch_id = touch_id
        self.review_id = review_id
        self.retryable = retryable


# -----------------------------------------------------------------------------
# Escalation Integration
# -----------------------------------------------------------------------------

class HITLEscalationIntegration:
    """Integration between HITL policy and coordination fabric.
    
    This class wires together:
    - Policy evaluation (when wake happens)
    - HITL client (creating reviews)
    - State updates (tracking review status)
    - Wake routing (blocking/resuming sends)
    
    Parameters
    ----------
    policy_evaluator : ReengagementPolicyEvaluator
        Policy evaluator instance
    hitl_client : HITLClient
        HITL client implementation
    state_adapter : Any  # TouchStateUWGAdapter
        UWG adapter for state updates
    """
    
    def __init__(
        self,
        policy_evaluator: ReengagementPolicyEvaluator,
        hitl_client: HITLClient,
        state_adapter: Any,
    ):
        self._evaluator = policy_evaluator
        self._hitl = hitl_client
        self._state = state_adapter
    
    def evaluate_wake_for_hitl(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        context_carry_forward: dict[str, Any],
        **kwargs,
    ) -> tuple[bool, Optional[str], PolicyEvalResult]:
        """Evaluate a wake for HITL requirements and escalate if needed.
        
        This is the main entry point called during wake processing.
        
        Parameters
        ----------
        touch_id : str
        recipient_hash : str
        campaign_id : str
        touch_sequence : int
        context_carry_forward : dict
        **kwargs
            Additional policy eval context (recipient_tier, prior_replies, etc.)
        
        Returns
        -------
        tuple[bool, Optional[str], PolicyEvalResult]
            (requires_hitl, review_id, eval_result)
        """
        # Build evaluation request
        eval_request = PolicyEvalRequest(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            context_carry_forward=context_carry_forward,
            **kwargs,
        )
        
        # Evaluate policy
        result = self._evaluator.evaluate(eval_request)
        
        if not result.requires_hitl:
            return False, None, result
        
        # HITL required - create review
        if result.review_request is None:
            # Should not happen if requires_hitl=True
            return False, None, result
        
        try:
            review_id = self._hitl.create_review(result.review_request)
            
            # Update touch state with HITL pending
            self._update_touch_hitl_status(
                touch_id=touch_id,
                review_id=review_id,
                review_type=result.review_type,
            )
            
            return True, review_id, result
        
        except Exception as e:
            # Escalation failed - fail open or closed based on policy
            raise HITLEscalationError(
                message=f"HITL escalation failed: {e}",
                touch_id=touch_id,
                retryable=True,
            )
    
    def check_review_resolution(
        self,
        touch_id: str,
        review_id: str,
    ) -> tuple[bool, Optional[HITLReviewResult]]:
        """Check if a HITL review has been resolved.
        
        Called during wake processing to check if previously-escalated
touch can now proceed.
        
        Parameters
        ----------
        touch_id : str
            Touch being checked
        review_id : str
            HITL review ID
        
        Returns
        -------
        tuple[bool, Optional[HITLReviewResult]]
            (resolved, result) - result is None if not resolved
        """
        status = self._hitl.get_review_status(review_id)
        
        if status.get("status") != "resolved":
            return False, None
        
        result = status.get("result")
        if result is None:
            return False, None
        
        # Update touch state with resolution
        self._update_touch_hitl_resolution(
            touch_id=touch_id,
            review_id=review_id,
            resolution=result.resolution,
        )
        
        return True, result
    
    def should_proceed_after_resolution(
        self,
        result: HITLReviewResult,
    ) -> tuple[bool, Optional[dict]]:
        """Determine if touch should proceed after HITL resolution.
        
        Parameters
        ----------
        result : HITLReviewResult
            HITL review result
        
        Returns
        -------
        tuple[bool, Optional[dict]]
            (should_proceed, modifications) - modifications if edits required
        """
        if result.resolution == HITLResolution.APPROVED:
            return True, None
        
        if result.resolution == HITLResolution.APPROVED_WITH_EDITS:
            return True, result.modifications
        
        if result.resolution == HITLResolution.REJECTED:
            return False, None
        
        if result.resolution == HITLResolution.DEFERRED:
            # Keep pending - will check again later
            return False, None
        
        if result.resolution == HITLResolution.ESCALATED:
            # Higher authority needed - keep pending
            return False, None
        
        # Unknown resolution - fail closed
        return False, None
    
    def _update_touch_hitl_status(
        self,
        touch_id: str,
        review_id: str,
        review_type: HITLReviewType,
    ) -> bool:
        """Update touch state to reflect HITL pending."""
        from agentic_core.L4_state.uwg.touch_state_writer import TouchStateWriteRequest
        
        request = TouchStateWriteRequest(
            touch_id=touch_id,
            recipient_hash="",  # Populated from lookup in production
            campaign_id="",
            touch_sequence=0,
            touch_state="hitl_pending",
            hitl_review_required=True,
        )
        
        # Set metadata fields via setattr workaround
        request.__dict__["hitl_review_id"] = review_id
        request.__dict__["hitl_review_type"] = review_type.value
        
        receipt, blocked = self._state.write_touch_state(request)
        return receipt is not None
    
    def _update_touch_hitl_resolution(
        self,
        touch_id: str,
        review_id: str,
        resolution: HITLResolution,
    ) -> bool:
        """Update touch state with HITL resolution."""
        from agentic_core.L4_state.uwg.touch_state_writer import TouchStateWriteRequest
        
        # Map resolution to touch state
        state_map = {
            HITLResolution.APPROVED: "hitl_approved",
            HITLResolution.APPROVED_WITH_EDITS: "hitl_approved",
            HITLResolution.REJECTED: "hitl_rejected",
            HITLResolution.DEFERRED: "hitl_deferred",
            HITLResolution.ESCALATED: "hitl_escalated",
        }
        
        request = TouchStateWriteRequest(
            touch_id=touch_id,
            recipient_hash="",
            campaign_id="",
            touch_sequence=0,
            touch_state=state_map.get(resolution, "hitl_unknown"),
            hitl_review_required=False,  # Review complete
        )
        
        request.__dict__["hitl_decision"] = resolution.value
        request.__dict__["hitl_review_id"] = review_id
        
        receipt, blocked = self._state.write_touch_state(request)
        return receipt is not None


# -----------------------------------------------------------------------------
# Mock HITL Client (for testing/deployment without full HITL system)
# -----------------------------------------------------------------------------

class MockHITLClient(HITLClient):
    """Mock HITL client for testing and development.
    
    Stores reviews in memory and allows manual resolution.
    """
    
    def __init__(self):
        self._reviews: dict[str, HITLReviewRequest] = {}
        self._results: dict[str, HITLReviewResult] = {}
        self._auto_approve: bool = False
    
    def set_auto_approve(self, enabled: bool = True) -> None:
        """Enable auto-approval mode (for testing)."""
        self._auto_approve = enabled
    
    def create_review(self, request: HITLReviewRequest) -> str:
        """Create mock review."""
        self._reviews[request.review_id] = request
        
        if self._auto_approve:
            # Auto-resolve with approval
            result = HITLReviewResult(
                review_id=request.review_id,
                touch_id=request.touch_id,
                resolution=HITLResolution.APPROVED,
                resolved_by="mock_auto",
                resolved_at=datetime.now(timezone.utc).isoformat(),
                notes="Auto-approved by mock client",
            )
            self._results[request.review_id] = result
        
        return request.review_id
    
    def get_review_status(self, review_id: str) -> dict[str, Any]:
        """Get mock review status."""
        if review_id not in self._reviews:
            return {"status": "not_found", "result": None}
        
        if review_id in self._results:
            return {"status": "resolved", "result": self._results[review_id]}
        
        return {"status": "pending", "result": None}
    
    def resolve_review(
        self,
        review_id: str,
        resolution: HITLResolution,
        resolved_by: str,
        notes: str = "",
        modifications: Optional[dict] = None,
    ) -> HITLReviewResult:
        """Resolve mock review."""
        if review_id not in self._reviews:
            raise ValueError(f"Review not found: {review_id}")
        
        request = self._reviews[review_id]
        
        result = HITLReviewResult(
            review_id=review_id,
            touch_id=request.touch_id,
            resolution=resolution,
            resolved_by=resolved_by,
            resolved_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
            modifications=modifications or {},
        )
        
        self._results[review_id] = result
        return result
    
    def list_pending_reviews(self) -> list[HITLReviewRequest]:
        """List all pending reviews (mock-specific helper)."""
        pending = []
        for review_id, request in self._reviews.items():
            if review_id not in self._results:
                pending.append(request)
        return pending


# -----------------------------------------------------------------------------
# Integration Factory
# -----------------------------------------------------------------------------

def create_hitl_escalation_integration(
    state_adapter: Any,
    hitl_client: Optional[HITLClient] = None,
) -> HITLEscalationIntegration:
    """Create HITL escalation integration with default or provided client.
    
    Parameters
    ----------
    state_adapter : TouchStateUWGAdapter
        UWG state adapter
    hitl_client : Optional[HITLClient]
        HITL client. If None, uses MockHITLClient.
    
    Returns
    -------
    HITLEscalationIntegration
        Configured integration
    """
    from agentic_core.L5_safety.evaluators.apps_lic_reengagement import ReengagementPolicyEvaluator
    
    evaluator = ReengagementPolicyEvaluator()
    client = hitl_client or MockHITLClient()
    
    return HITLEscalationIntegration(
        policy_evaluator=evaluator,
        hitl_client=client,
        state_adapter=state_adapter,
    )


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "HITLClient",
    "HITLEscalationError",
    "HITLEscalationIntegration",
    "MockHITLClient",
    "create_hitl_escalation_integration",
]
