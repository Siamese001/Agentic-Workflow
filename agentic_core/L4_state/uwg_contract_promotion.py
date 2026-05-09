"""
DS-3: UWG Promotion of Core Contracts to L4 State
Implements the T7s.4 evaluation/promotion pipeline for contracts.
"""
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class PromotionOutcome(Enum):
    """Outcome of contract promotion attempt."""
    PROMOTED = "promoted"
    REJECTED_SCHEMA_INVALID = "rejected_schema_invalid"
    REJECTED_VALIDATION_FAILED = "rejected_validation_failed"
    REJECTED_QUALITY_THRESHOLD = "rejected_quality_threshold"
    PENDING_REVIEW = "pending_review"


@dataclass(frozen=True)
class ContractEvaluation:
    """T7s.4 evaluation result for a contract."""
    contract_digest: str
    contract_type: str
    
    # Schema validation
    schema_valid: bool
    schema_errors: List[str] = field(default_factory=list)
    
    # Content validation
    required_fields_present: bool
    forbidden_fields_absent: bool
    field_errors: List[str] = field(default_factory=list)
    
    # Quality metrics
    quality_score: float  # 0.0 - 1.0
    quality_threshold: float = 0.8
    
    # Final outcome
    outcome: PromotionOutcome = PromotionOutcome.PENDING_REVIEW
    evaluated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_digest": self.contract_digest,
            "contract_type": self.contract_type,
            "schema_valid": self.schema_valid,
            "schema_errors": self.schema_errors,
            "required_fields_present": self.required_fields_present,
            "forbidden_fields_absent": self.forbidden_fields_absent,
            "field_errors": self.field_errors,
            "quality_score": self.quality_score,
            "quality_threshold": self.quality_threshold,
            "outcome": self.outcome.value,
            "evaluated_at": self.evaluated_at,
        }


@dataclass(frozen=True)
class PromotedContract:
    """A contract that has been promoted to L4 state store."""
    contract_digest: str
    contract_type: str
    contract_bytes: bytes
    
    # Promotion metadata
    promoted_at: str
    promotion_request_id: str
    evaluation_result: ContractEvaluation
    
    # Query indices
    key_space: str  # e.g., "apps_rg", "global"
    created_by_request: str  # Trace ID of creating request
    
    # TTL
    ttl_seconds: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_digest": self.contract_digest,
            "contract_type": self.contract_type,
            "contract_bytes_length": len(self.contract_bytes),
            "promoted_at": self.promoted_at,
            "promotion_request_id": self.promotion_request_id,
            "evaluation_result": self.evaluation_result.to_dict(),
            "key_space": self.key_space,
            "created_by_request": self.created_by_request,
            "ttl_seconds": self.ttl_seconds,
        }


# PROMOTABLE_CONTRACTS: Contract types eligible for UWG promotion
PROMOTABLE_CONTRACTS = {
    "AppsRgIngressPayload",
    "AppsRgProfileManifest",
    "AppsRgRuntimeAuthorityPolicy",
    "L1PlanContract",
    "RouteContract",
    "FinalEvidenceContract",
    "L7RuntimeAuditTrace",
    "SealedL2Artifact",
    "X3Disposition",
    "LLMGatewayRequest",
    "LLMGatewayResponse",
}


class ContractEvaluator:
    """
    T7s.4 Evaluation Gate implementation.
    
    Evaluates contracts before they can be promoted to L4 state store.
    """
    
    QUALITY_THRESHOLD = 0.8
    
    def __init__(self):
        self._validators: Dict[str, Callable[[Any], List[str]]] = {}
    
    def register_validator(self, contract_type: str, validator: Callable[[Any], List[str]]):
        """Register a validator for a contract type."""
        self._validators[contract_type] = validator
    
    def evaluate(self, contract: Any, contract_type: str) -> ContractEvaluation:
        """
        Evaluate a contract for promotion eligibility.
        
        This implements the T7s.4 gate logic.
        """
        # Compute digest
        contract_bytes = json.dumps(contract, default=str).encode("utf-8")
        contract_digest = hashlib.sha256(contract_bytes).hexdigest()
        
        # Check if contract type is promotable
        if contract_type not in PROMOTABLE_CONTRACTS:
            return ContractEvaluation(
                contract_digest=contract_digest,
                contract_type=contract_type,
                schema_valid=False,
                schema_errors=[f"Contract type '{contract_type}' not in PROMOTABLE_CONTRACTS"],
                required_fields_present=False,
                forbidden_fields_absent=False,
                field_errors=["Non-promotable contract type"],
                quality_score=0.0,
                outcome=PromotionOutcome.REJECTED_SCHEMA_INVALID,
            )
        
        # Run schema validation
        schema_errors = self._validate_schema(contract, contract_type)
        schema_valid = len(schema_errors) == 0
        
        # Run field validation
        field_errors = self._validate_fields(contract, contract_type)
        required_fields_present = all(
            "missing" not in e.lower() for e in field_errors
        )
        forbidden_fields_absent = all(
            "forbidden" not in e.lower() for e in field_errors
        )
        
        # Compute quality score
        quality_score = self._compute_quality_score(
            schema_valid, required_fields_present, forbidden_fields_absent, field_errors
        )
        
        # Determine outcome
        if not schema_valid:
            outcome = PromotionOutcome.REJECTED_SCHEMA_INVALID
        elif not required_fields_present or not forbidden_fields_absent:
            outcome = PromotionOutcome.REJECTED_VALIDATION_FAILED
        elif quality_score < self.QUALITY_THRESHOLD:
            outcome = PromotionOutcome.REJECTED_QUALITY_THRESHOLD
        else:
            outcome = PromotionOutcome.PENDING_REVIEW  # Final promotion requires human/AG review
        
        return ContractEvaluation(
            contract_digest=contract_digest,
            contract_type=contract_type,
            schema_valid=schema_valid,
            schema_errors=schema_errors,
            required_fields_present=required_fields_present,
            forbidden_fields_absent=forbidden_fields_absent,
            field_errors=field_errors,
            quality_score=quality_score,
            quality_threshold=self.QUALITY_THRESHOLD,
            outcome=outcome,
        )
    
    def _validate_schema(self, contract: Any, contract_type: str) -> List[str]:
        """Validate contract schema."""
        errors = []
        
        # Basic structure validation
        if not hasattr(contract, "__dict__") and not isinstance(contract, dict):
            errors.append("Contract must be a dataclass instance or dict")
            return errors
        
        # Contract-specific validation
        validator = self._validators.get(contract_type)
        if validator:
            errors.extend(validator(contract))
        
        return errors
    
    def _validate_fields(self, contract: Any, contract_type: str) -> List[str]:
        """Validate contract fields."""
        errors = []
        
        # Extract fields
        if hasattr(contract, "__dataclass_fields__"):
            fields = contract.__dataclass_fields__
            values = {f: getattr(contract, f) for f in fields}
        elif isinstance(contract, dict):
            values = contract
        else:
            errors.append("Cannot extract fields from contract")
            return errors
        
        # Check for empty required fields
        for key, value in values.items():
            if value is None or value == "":
                # Check if this is a required field (simplified)
                if key in ["prompt", "target_company", "jd_text"]:
                    errors.append(f"Required field '{key}' is missing or empty")
        
        # Check for forbidden runtime fields (AG-RGGOV-1 compliance)
        forbidden_patterns = [
            "planner", "router", "orchestrator", "executor", "provider", 
            "gateway", "judge", "disposition", "state_write"
        ]
        for key in values.keys():
            for pattern in forbidden_patterns:
                if pattern in key.lower():
                    errors.append(f"Forbidden runtime field '{key}' detected (violates AG-RGGOV-1)")
        
        return errors
    
    def _compute_quality_score(
        self, 
        schema_valid: bool, 
        required_present: bool, 
        forbidden_absent: bool,
        field_errors: List[str]
    ) -> float:
        """Compute quality score (0.0 - 1.0)."""
        score = 1.0
        
        if not schema_valid:
            score -= 0.4
        if not required_present:
            score -= 0.3
        if not forbidden_absent:
            score -= 0.3
        
        # Penalize field errors
        score -= len(field_errors) * 0.05
        
        return max(0.0, min(1.0, score))


class L4ContractStore:
    """
    L4 State Store for promoted contracts.
    
    This is the UWG durable state implementation for contracts.
    """
    
    def __init__(self):
        # In-memory store (production would use Redis/SQLite)
        self._contracts: Dict[str, PromotedContract] = {}
        self._indices: Dict[str, List[str]] = {
            "by_type": {},
            "by_key_space": {},
            "by_request": {},
        }
    
    def promote(
        self,
        contract: Any,
        contract_type: str,
        request_id: str,
        key_space: str = "default",
        ttl_seconds: Optional[int] = None,
    ) -> Optional[PromotedContract]:
        """
        Promote a contract to L4 state store after evaluation.
        
        Returns the promoted contract or None if rejected.
        """
        # Evaluate
        evaluator = ContractEvaluator()
        evaluation = evaluator.evaluate(contract, contract_type)
        
        # Only promote if evaluation passed
        if evaluation.outcome != PromotionOutcome.PENDING_REVIEW:
            return None
        
        # Serialize contract
        contract_bytes = json.dumps(contract, default=str).encode("utf-8")
        contract_digest = evaluation.contract_digest
        
        # Create promoted contract
        promoted = PromotedContract(
            contract_digest=contract_digest,
            contract_type=contract_type,
            contract_bytes=contract_bytes,
            promoted_at=datetime.utcnow().isoformat(),
            promotion_request_id=request_id,
            evaluation_result=evaluation,
            key_space=key_space,
            created_by_request=request_id,
            ttl_seconds=ttl_seconds,
        )
        
        # Store
        self._contracts[contract_digest] = promoted
        
        # Update indices
        self._indices["by_type"].setdefault(contract_type, []).append(contract_digest)
        self._indices["by_key_space"].setdefault(key_space, []).append(contract_digest)
        self._indices["by_request"].setdefault(request_id, []).append(contract_digest)
        
        return promoted
    
    def get(self, contract_digest: str) -> Optional[PromotedContract]:
        """Retrieve a promoted contract by digest."""
        return self._contracts.get(contract_digest)
    
    def query_by_type(self, contract_type: str) -> List[PromotedContract]:
        """Query contracts by type."""
        digests = self._indices["by_type"].get(contract_type, [])
        return [self._contracts[d] for d in digests if d in self._contracts]
    
    def query_by_key_space(self, key_space: str) -> List[PromotedContract]:
        """Query contracts by key space."""
        digests = self._indices["by_key_space"].get(key_space, [])
        return [self._contracts[d] for d in digests if d in self._contracts]


# Global store instance (singleton pattern)
_contract_store: Optional[L4ContractStore] = None


def get_contract_store() -> L4ContractStore:
    """Get the global L4 contract store."""
    global _contract_store
    if _contract_store is None:
        _contract_store = L4ContractStore()
    return _contract_store
