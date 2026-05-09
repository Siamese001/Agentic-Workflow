"""
DS-3: UWG Promotion Pipeline
Full implementation of contract evaluation and promotion pipeline.
"""
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .uwg_contract_promotion import (
    ContractEvaluator, ContractEvaluation, PromotionOutcome,
    PromotedContract, L4ContractStore, get_contract_store,
    PROMOTABLE_CONTRACTS
)


class PipelineStage(Enum):
    """Stages in the promotion pipeline."""
    SUBMITTED = "submitted"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    PROMOTED = "promoted"
    REJECTED = "rejected"


@dataclass
class PromotionRequest:
    """A request to promote a contract to L4 state."""
    request_id: str
    contract: Any
    contract_type: str
    requested_by: str  # Trace ID of requesting component
    key_space: str = "default"
    ttl_seconds: Optional[int] = None
    submitted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "contract_type": self.contract_type,
            "requested_by": self.requested_by,
            "key_space": self.key_space,
            "ttl_seconds": self.ttl_seconds,
            "submitted_at": self.submitted_at,
        }


@dataclass
class PromotionPipelineResult:
    """Result of running a contract through the promotion pipeline."""
    request: PromotionRequest
    stage: PipelineStage
    evaluation: Optional[ContractEvaluation] = None
    promoted_contract: Optional[PromotedContract] = None
    error_message: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "stage": self.stage.value,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "promoted": self.promoted_contract is not None,
            "error": self.error_message,
            "completed_at": self.completed_at,
        }


class UWGPromotionPipeline:
    """
    DS-3: Full UWG Promotion Pipeline.
    
    Implements T7s.4 evaluation gate + promotion decision flow.
    """
    
    def __init__(self):
        self._evaluator = ContractEvaluator()
        self._store = get_contract_store()
        self._pipeline_history: List[PromotionPipelineResult] = []
    
    def submit(
        self,
        contract: Any,
        contract_type: str,
        requested_by: str,
        key_space: str = "default",
        ttl_seconds: Optional[int] = None,
    ) -> PromotionRequest:
        """
        Submit a contract for promotion evaluation.
        
        This is the entry point for the promotion pipeline.
        """
        # Generate request ID
        contract_bytes = json.dumps(contract, default=str).encode("utf-8")
        contract_digest = hashlib.sha256(contract_bytes).hexdigest()
        request_id = f"promote_{contract_type}_{contract_digest[:16]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        request = PromotionRequest(
            request_id=request_id,
            contract=contract,
            contract_type=contract_type,
            requested_by=requested_by,
            key_space=key_space,
            ttl_seconds=ttl_seconds,
        )
        
        return request
    
    def evaluate(self, request: PromotionRequest) -> ContractEvaluation:
        """
        Run T7s.4 evaluation gate on a submitted contract.
        
        Returns evaluation result (does not promote yet).
        """
        return self._evaluator.evaluate(
            request.contract,
            request.contract_type,
        )
    
    def promote(
        self,
        request: PromotionRequest,
        evaluation: ContractEvaluation,
        auto_promote_if_passed: bool = False,
    ) -> PromotionPipelineResult:
        """
        Promote a contract to L4 state store.
        
        Requires evaluation to have passed quality threshold.
        """
        # Check if evaluation allows promotion
        if evaluation.outcome == PromotionOutcome.REJECTED_SCHEMA_INVALID:
            return PromotionPipelineResult(
                request=request,
                stage=PipelineStage.REJECTED,
                evaluation=evaluation,
                error_message="Schema validation failed - cannot promote",
                completed_at=datetime.utcnow().isoformat(),
            )
        
        if evaluation.outcome == PromotionOutcome.REJECTED_VALIDATION_FAILED:
            return PromotionPipelineResult(
                request=request,
                stage=PipelineStage.REJECTED,
                evaluation=evaluation,
                error_message="Field validation failed - cannot promote",
                completed_at=datetime.utcnow().isoformat(),
            )
        
        if evaluation.outcome == PromotionOutcome.REJECTED_QUALITY_THRESHOLD:
            if not auto_promote_if_passed:
                return PromotionPipelineResult(
                    request=request,
                    stage=PipelineStage.REJECTED,
                    evaluation=evaluation,
                    error_message=f"Quality score {evaluation.quality_score:.2f} below threshold {evaluation.quality_threshold}",
                    completed_at=datetime.utcnow().isoformat(),
                )
        
        # Attempt promotion
        promoted = self._store.promote(
            contract=request.contract,
            contract_type=request.contract_type,
            request_id=request.request_id,
            key_space=request.key_space,
            ttl_seconds=request.ttl_seconds,
        )
        
        if promoted:
            result = PromotionPipelineResult(
                request=request,
                stage=PipelineStage.PROMOTED,
                evaluation=evaluation,
                promoted_contract=promoted,
                completed_at=datetime.utcnow().isoformat(),
            )
        else:
            result = PromotionPipelineResult(
                request=request,
                stage=PipelineStage.REJECTED,
                evaluation=evaluation,
                error_message="Promotion to L4 store failed",
                completed_at=datetime.utcnow().isoformat(),
            )
        
        self._pipeline_history.append(result)
        return result
    
    def run_full_pipeline(
        self,
        contract: Any,
        contract_type: str,
        requested_by: str,
        key_space: str = "default",
        ttl_seconds: Optional[int] = None,
        auto_promote: bool = True,
    ) -> PromotionPipelineResult:
        """
        Run a contract through the full promotion pipeline.
        
        This is the main entry point for one-shot promotion.
        """
        # Submit
        request = self.submit(
            contract=contract,
            contract_type=contract_type,
            requested_by=requested_by,
            key_space=key_space,
            ttl_seconds=ttl_seconds,
        )
        
        # Evaluate
        evaluation = self.evaluate(request)
        
        # Promote (if auto_promote enabled and evaluation passed)
        if auto_promote and evaluation.outcome in [
            PromotionOutcome.PENDING_REVIEW,
            PromotionOutcome.PROMOTED,
        ]:
            return self.promote(request, evaluation, auto_promote_if_passed=True)
        
        # Return evaluation result without promoting
        return PromotionPipelineResult(
            request=request,
            stage=PipelineStage.EVALUATED,
            evaluation=evaluation,
            completed_at=datetime.utcnow().isoformat(),
        )
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        total = len(self._pipeline_history)
        promoted = len([r for r in self._pipeline_history if r.stage == PipelineStage.PROMOTED])
        rejected = len([r for r in self._pipeline_history if r.stage == PipelineStage.REJECTED])
        
        return {
            "total_requests": total,
            "promoted": promoted,
            "rejected": rejected,
            "success_rate": promoted / total if total > 0 else 0.0,
        }


# Global pipeline instance
_promotion_pipeline: Optional[UWGPromotionPipeline] = None


def get_promotion_pipeline() -> UWGPromotionPipeline:
    """Get the global UWG promotion pipeline."""
    global _promotion_pipeline
    if _promotion_pipeline is None:
        _promotion_pipeline = UWGPromotionPipeline()
    return _promotion_pipeline


def promote_contract(
    contract: Any,
    contract_type: str,
    requested_by: str,
    **kwargs
) -> PromotionPipelineResult:
    """
    Convenience function to promote a contract via the global pipeline.
    
    Example:
        result = promote_contract(
            contract=my_contract,
            contract_type="AppsRgIngressPayload",
            requested_by="apps_rg_ingress_abc123",
        )
        if result.promoted_contract:
            print(f"Promoted with digest: {result.promoted_contract.contract_digest}")
    """
    pipeline = get_promotion_pipeline()
    return pipeline.run_full_pipeline(
        contract=contract,
        contract_type=contract_type,
        requested_by=requested_by,
        **kwargs
    )
