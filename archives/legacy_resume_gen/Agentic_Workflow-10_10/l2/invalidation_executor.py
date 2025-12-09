"""
Temporal fact invalidation executor for résumé processing workflows.

Implements L2 executor for detecting and marking outdated or contradictory facts in résumé enhancement operations.

Layer: L2 (Execution)
Responsibilities:
- Execute invalidation checks based on L1 plans for résumé fact management
- Detect contradictory facts in résumé processing data
- Mark facts as invalidated for accurate résumé enhancement
- Return invalidation results for workflow coordination

Non-responsibilities:
- Invalidation planning (L1)
- State storage (L4)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta, UTC
from enum import Enum

from l4.triplet_store import Triplet, TripletStore, TripletStatus, TripletQuery


class InvalidationReason(str, Enum):
    """Reasons for fact invalidation in résumé processing workflows."""
    SUPERSEDED = "superseded"           # Replaced by newer fact
    CONTRADICTED = "contradicted"       # Contradicts another fact
    EXPIRED = "expired"                 # Temporal validity expired
    RETRACTED = "retracted"             # Source retracted the fact
    LOW_CONFIDENCE = "low_confidence"   # Below confidence threshold
    MANUAL = "manual"                   # Manual invalidation


@dataclass
class InvalidationRule:
    """Rule for automatic invalidation in résumé processing fact management."""
    
    id: str
    name: str
    predicate_pattern: Optional[str] = None  # Applies to specific predicates
    
    # Conditions
    max_age_days: Optional[int] = None       # Invalidate facts older than N days
    min_confidence: float = 0.0               # Invalidate below threshold
    supersession_predicates: List[str] = field(default_factory=list)  # Predicates that supersede
    
    # Actions
    reason: InvalidationReason = InvalidationReason.EXPIRED
    
    def matches_triplet(self, triplet: Triplet) -> bool:
        """
        Checks if invalidation rule applies to a résumé processing triplet.

        Ensures proper fact validation for accurate résumé enhancement workflows.
        """
        if self.predicate_pattern:
            if triplet.predicate != self.predicate_pattern:
                return False
        return True


@dataclass
class InvalidationResult:
    """Result of invalidation check for résumé processing fact management."""
    
    triplet_id: str
    invalidated: bool
    reason: Optional[InvalidationReason] = None
    superseded_by: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvalidationPlan:
    """Plan for invalidation execution in résumé processing workflows (from L1)."""
    
    target_subject: Optional[str] = None
    target_predicate: Optional[str] = None
    rules: List[InvalidationRule] = field(default_factory=list)
    check_contradictions: bool = True
    check_supersession: bool = True
    check_expiration: bool = True
    max_age_days: int = 365


class InvalidationExecutor:
    """
    Executor for fact invalidation in résumé processing workflows.
    
    Checks triplets against invalidation rules and marks outdated or contradictory facts for accurate résumé enhancement.
    """
    
    def __init__(self, triplet_store: TripletStore):
        """
        Initializes invalidation executor for résumé processing fact management.
        
        Args:
            triplet_store: L4 TripletStore instance for résumé workflow coordination
        """
        self.store = triplet_store
        self._default_rules = self._build_default_rules()
    
    def _build_default_rules(self) -> List[InvalidationRule]:
        """Build default invalidation rules."""
        return [
            # Current employment supersedes past employment
            InvalidationRule(
                id="employment_supersession",
                name="Employment Supersession",
                predicate_pattern="worked_at",
                supersession_predicates=["works_at", "currently_employed_at"],
                reason=InvalidationReason.SUPERSEDED,
            ),
            # Current role supersedes past role
            InvalidationRule(
                id="role_supersession",
                name="Role Supersession",
                predicate_pattern="held_role",
                supersession_predicates=["current_role", "holds_role"],
                reason=InvalidationReason.SUPERSEDED,
            ),
            # Skills can become outdated
            InvalidationRule(
                id="skill_expiration",
                name="Skill Expiration",
                predicate_pattern="has_skill",
                max_age_days=730,  # 2 years
                reason=InvalidationReason.EXPIRED,
            ),
            # Low confidence facts
            InvalidationRule(
                id="low_confidence",
                name="Low Confidence Invalidation",
                min_confidence=0.3,
                reason=InvalidationReason.LOW_CONFIDENCE,
            ),
        ]
    
    def execute(self, plan: InvalidationPlan) -> List[InvalidationResult]:
        """Execute invalidation based on plan.
        
        Args:
            plan: Invalidation plan from L1
            
        Returns:
            List of invalidation results
        """
        results: List[InvalidationResult] = []
        
        # Build query for target triplets
        query = TripletQuery(
            subject=plan.target_subject,
            predicate=plan.target_predicate,
            include_invalidated=False,
        )
        
        triplets = self.store.query(query)
        
        # Combine default rules with plan rules
        all_rules = self._default_rules + plan.rules
        
        for triplet in triplets:
            result = self._check_triplet(triplet, all_rules, plan)
            if result.invalidated:
                # Apply invalidation to store
                self.store.invalidate_triplet(
                    triplet.id,
                    reason=result.reason.value if result.reason else "unknown",
                    invalidated_by=result.superseded_by,
                )
            results.append(result)
        
        return results
    
    def _check_triplet(
        self,
        triplet: Triplet,
        rules: List[InvalidationRule],
        plan: InvalidationPlan,
    ) -> InvalidationResult:
        """Check a single triplet for invalidation.
        
        Args:
            triplet: Triplet to check
            rules: Invalidation rules
            plan: Invalidation plan
            
        Returns:
            Invalidation result
        """
        # Check rule-based invalidation
        for rule in rules:
            if not rule.matches_triplet(triplet):
                continue
            
            # Check age
            if rule.max_age_days:
                age = datetime.now(UTC) - triplet.extracted_at
                if age.days > rule.max_age_days:
                    return InvalidationResult(
                        triplet_id=triplet.id,
                        invalidated=True,
                        reason=InvalidationReason.EXPIRED,
                        details={"age_days": age.days, "max_age_days": rule.max_age_days},
                    )
            
            # Check confidence
            if triplet.confidence < rule.min_confidence:
                return InvalidationResult(
                    triplet_id=triplet.id,
                    invalidated=True,
                    reason=InvalidationReason.LOW_CONFIDENCE,
                    details={"confidence": triplet.confidence, "min_confidence": rule.min_confidence},
                )
            
            # Check supersession
            if plan.check_supersession and rule.supersession_predicates:
                superseding = self._find_superseding_triplet(triplet, rule.supersession_predicates)
                if superseding:
                    return InvalidationResult(
                        triplet_id=triplet.id,
                        invalidated=True,
                        reason=InvalidationReason.SUPERSEDED,
                        superseded_by=superseding.id,
                        details={"superseding_predicate": superseding.predicate},
                    )
        
        # Check contradictions
        if plan.check_contradictions:
            contradiction = self._find_contradiction(triplet)
            if contradiction:
                return InvalidationResult(
                    triplet_id=triplet.id,
                    invalidated=True,
                    reason=InvalidationReason.CONTRADICTED,
                    superseded_by=contradiction.id,
                    details={"contradicting_triplet": contradiction.to_text()},
                )
        
        # Check expiration based on plan
        if plan.check_expiration:
            age = datetime.now(UTC) - triplet.extracted_at
            if age.days > plan.max_age_days:
                return InvalidationResult(
                    triplet_id=triplet.id,
                    invalidated=True,
                    reason=InvalidationReason.EXPIRED,
                    details={"age_days": age.days, "max_age_days": plan.max_age_days},
                )
        
        # Not invalidated
        return InvalidationResult(
            triplet_id=triplet.id,
            invalidated=False,
        )
    
    def _find_superseding_triplet(
        self,
        triplet: Triplet,
        supersession_predicates: List[str],
    ) -> Optional[Triplet]:
        """Find a triplet that supersedes the given triplet.
        
        Args:
            triplet: Triplet to check
            supersession_predicates: Predicates that would supersede
            
        Returns:
            Superseding triplet or None
        """
        for predicate in supersession_predicates:
            query = TripletQuery(
                subject=triplet.subject,
                predicate=predicate,
                include_invalidated=False,
            )
            candidates = self.store.query(query)
            
            for candidate in candidates:
                # Newer triplet with superseding predicate
                if candidate.extracted_at > triplet.extracted_at:
                    return candidate
        
        return None
    
    def _find_contradiction(self, triplet: Triplet) -> Optional[Triplet]:
        """Find a triplet that contradicts the given triplet.
        
        Contradiction detection is based on:
        - Same subject and predicate but different object (for single-value predicates)
        - Mutually exclusive predicates
        
        Args:
            triplet: Triplet to check
            
        Returns:
            Contradicting triplet or None
        """
        # Single-value predicates (only one can be true at a time)
        single_value_predicates = {
            "current_employer",
            "current_role",
            "current_title",
            "current_location",
            "primary_skill",
        }
        
        if triplet.predicate in single_value_predicates:
            query = TripletQuery(
                subject=triplet.subject,
                predicate=triplet.predicate,
                include_invalidated=False,
            )
            candidates = self.store.query(query)
            
            for candidate in candidates:
                if candidate.id != triplet.id and candidate.object != triplet.object:
                    # Prefer newer triplet
                    if candidate.extracted_at > triplet.extracted_at:
                        return candidate
        
        # Mutually exclusive predicates
        exclusive_pairs = [
            ("is_employed", "is_unemployed"),
            ("is_student", "is_professional"),
            ("seeking_job", "not_seeking_job"),
        ]
        
        for pred1, pred2 in exclusive_pairs:
            if triplet.predicate == pred1:
                query = TripletQuery(
                    subject=triplet.subject,
                    predicate=pred2,
                    include_invalidated=False,
                )
                candidates = self.store.query(query)
                if candidates:
                    return candidates[0]
            elif triplet.predicate == pred2:
                query = TripletQuery(
                    subject=triplet.subject,
                    predicate=pred1,
                    include_invalidated=False,
                )
                candidates = self.store.query(query)
                if candidates:
                    return candidates[0]
        
        return None
    
    def invalidate_by_subject(
        self,
        subject: str,
        reason: InvalidationReason = InvalidationReason.MANUAL,
        details: Optional[Dict[str, Any]] = None,
    ) -> List[InvalidationResult]:
        """Invalidate all triplets for a subject.
        
        Args:
            subject: Subject entity
            reason: Invalidation reason
            details: Additional details
            
        Returns:
            List of invalidation results
        """
        query = TripletQuery(subject=subject, include_invalidated=False)
        triplets = self.store.query(query)
        
        results = []
        for triplet in triplets:
            self.store.invalidate_triplet(triplet.id, reason.value)
            results.append(InvalidationResult(
                triplet_id=triplet.id,
                invalidated=True,
                reason=reason,
                details=details or {},
            ))
        
        return results


# =============================================================================
# Invalidation Plan Helpers
# =============================================================================

def create_invalidation_plan(
    target_subject: Optional[str] = None,
    target_predicate: Optional[str] = None,
    max_age_days: int = 365,
    custom_rules: Optional[List[InvalidationRule]] = None,
) -> InvalidationPlan:
    """Create an invalidation plan.
    
    Args:
        target_subject: Optional subject filter
        target_predicate: Optional predicate filter
        max_age_days: Maximum age for facts
        custom_rules: Additional custom rules
        
    Returns:
        InvalidationPlan
    """
    return InvalidationPlan(
        target_subject=target_subject,
        target_predicate=target_predicate,
        rules=custom_rules or [],
        max_age_days=max_age_days,
    )


__all__ = [
    "InvalidationReason",
    "InvalidationRule",
    "InvalidationResult",
    "InvalidationPlan",
    "InvalidationExecutor",
    "create_invalidation_plan",
]
