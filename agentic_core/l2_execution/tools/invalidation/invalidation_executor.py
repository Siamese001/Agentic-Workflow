"""Invalidation Executor for L2 execution layer."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class InvalidationType(Enum):
    """Type of invalidation operations."""
    ENTITY_INVALIDATION = "entity_invalidation"
    RELATIONSHIP_INVALIDATION = "relationship_invalidation"
    TEMPORAL_INVALIDATION = "temporal_invalidation"
    CONFIDENCE_INVALIDATION = "confidence_invalidation"

@dataclass
class InvalidationConfig:
    """Configuration for invalidation operations."""
    invalidation_type: InvalidationType = InvalidationType.ENTITY_INVALIDATION
    cascade_invalidations: bool = True
    preserve_history: bool = True
    confidence_threshold: float = 0.3
    temporal_window_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InvalidationPlan:
    """Plan for invalidation operations."""
    plan_id: str = ""
    invalidation_type: InvalidationType = InvalidationType.ENTITY_INVALIDATION
    target_ids: List[str] = field(default_factory=list)
    criteria: Dict[str, Any] = field(default_factory=dict)
    cascade_rules: List[str] = field(default_factory=list)
    estimated_impact: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.plan_id:
            self.plan_id = f"invalidation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

@dataclass
class InvalidationResult:
    """Result from invalidation operations."""
    plan_id: str = ""
    invalidated_items: List[str] = field(default_factory=list)
    cascaded_invalidations: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class InvalidationExecutor:
    """Invalidation Executor for knowledge graph operations."""
    
    def __init__(self, config: Optional[InvalidationConfig] = None):
        """Initialize invalidation executor with configuration."""
        self.config = config or InvalidationConfig()
        self.execution_history = []
        self.stats = {
            "total_invalidations": 0,
            "successful_invalidations": 0,
            "cascaded_invalidations": 0,
            "average_execution_time": 0.0
        }
    
    def execute_invalidation(self, plan: InvalidationPlan) -> InvalidationResult:
        """Execute invalidation plan."""
        start_time = datetime.now()
        
        try:
            # Mock invalidation implementation
            invalidated_items = self._invalidate_targets(plan)
            cascaded_invalidations = []
            
            if self.config.cascade_invalidations:
                cascaded_invalidations = self._execute_cascade_invalidations(plan)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = InvalidationResult(
                plan_id=plan.plan_id,
                invalidated_items=invalidated_items,
                cascaded_invalidations=cascaded_invalidations,
                execution_time=execution_time,
                success=True,
                metadata={
                    "invalidation_type": plan.invalidation_type.value,
                    "cascade_enabled": self.config.cascade_invalidations
                }
            )
            
            self._update_stats(result)
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            error_result = InvalidationResult(
                plan_id=plan.plan_id,
                execution_time=execution_time,
                success=False,
                error_message=str(e),
                metadata={"error_occurred": True}
            )
            
            self.execution_history.append(error_result)
            return error_result
    
    def _invalidate_targets(self, plan: InvalidationPlan) -> List[str]:
        """Mock target invalidation."""
        # Simple mock implementation
        invalidated = []
        
        for target_id in plan.target_ids:
            # Apply invalidation criteria
            if self._meets_invalidation_criteria(target_id, plan.criteria):
                invalidated.append(target_id)
        
        return invalidated
    
    def _execute_cascade_invalidations(self, plan: InvalidationPlan) -> List[str]:
        """Mock cascade invalidation execution."""
        # Simple mock implementation
        cascaded = []
        
        for cascade_rule in plan.cascade_rules:
            # Mock cascade logic
            cascaded.append(f"cascade_{cascade_rule}_{plan.plan_id}")
        
        return cascaded
    
    def _meets_invalidation_criteria(self, target_id: str, criteria: Dict[str, Any]) -> bool:
        """Check if target meets invalidation criteria."""
        # Simple mock implementation
        if "confidence_below" in criteria:
            return True  # Mock: assume targets meet criteria
        
        if "older_than_days" in criteria:
            return True  # Mock: assume targets meet criteria
        
        return True  # Default: invalidate all targets
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update executor configuration."""
        if "invalidation_type" in new_config:
            self.config.invalidation_type = InvalidationType(new_config["invalidation_type"])
        if "cascade_invalidations" in new_config:
            self.config.cascade_invalidations = new_config["cascade_invalidations"]
        if "preserve_history" in new_config:
            self.config.preserve_history = new_config["preserve_history"]
        if "confidence_threshold" in new_config:
            self.config.confidence_threshold = new_config["confidence_threshold"]
        if "temporal_window_days" in new_config:
            self.config.temporal_window_days = new_config["temporal_window_days"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics."""
        return {
            **self.stats,
            "config": {
                "invalidation_type": self.config.invalidation_type.value,
                "cascade_invalidations": self.config.cascade_invalidations,
                "preserve_history": self.config.preserve_history,
                "confidence_threshold": self.config.confidence_threshold
            },
            "execution_count": len(self.execution_history)
        }
    
    def _update_stats(self, result: InvalidationResult) -> None:
        """Update execution statistics."""
        self.stats["total_invalidations"] += 1
        
        if result.success:
            self.stats["successful_invalidations"] += 1
            self.stats["cascaded_invalidations"] += len(result.cascaded_invalidations)
        
        # Update average execution time
        total_time = self.stats["average_execution_time"] * (self.stats["total_invalidations"] - 1) + result.execution_time
        self.stats["average_execution_time"] = total_time / self.stats["total_invalidations"]

def create_invalidation_plan(target_ids: List[str] = None, 
                            target_subject: str = "",
                            max_age_days: int = 30,
                            invalidation_type: InvalidationType = InvalidationType.ENTITY_INVALIDATION,
                            criteria: Dict[str, Any] = None,
                            cascade_rules: List[str] = None) -> InvalidationPlan:
    """Factory function to create an invalidation plan."""
    if target_subject and not target_ids:
        target_ids = [target_subject]
    
    # Add max_age_days to criteria if provided
    if criteria is None:
        criteria = {}
    if max_age_days > 0:
        criteria["max_age_days"] = max_age_days
    
    return InvalidationPlan(
        invalidation_type=invalidation_type,
        target_ids=target_ids or [],
        criteria=criteria,
        cascade_rules=cascade_rules or [],
        estimated_impact=len(target_ids or [])
    )
