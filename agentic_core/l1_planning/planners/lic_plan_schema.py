# lic_plan_schema - Plan schema definitions
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LICPlan:
    """LIC Plan data structure"""
    plan_id: str = ""
    content: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def validate(self) -> bool:
        """Validate the plan structure"""
        return bool(self.plan_id and self.content)

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            "plan_id": self.plan_id,
            "content": self.content,
            "metadata": self.metadata
        }

class PlanSchema:
    """Plan schema validator and manager"""

    def __init__(self, schema_version: str = "1.0"):
        self.schema_version = schema_version

    def create_plan(self, plan_id: str, content: str, metadata: Dict[str, Any] = None) -> LICPlan:
        """Create a new LIC plan"""
        return LICPlan(
            plan_id=plan_id,
            content=content,
            metadata=metadata or {}
        )

    def validate_plan(self, plan: LICPlan) -> bool:
        """Validate a plan against the schema"""
        return plan.validate()

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information"""
        return {
            "version": self.schema_version,
            "required_fields": ["plan_id", "content"],
            "optional_fields": ["metadata"]
        }

# Global schema instance
_global_schema: Optional[PlanSchema] = None

def get_plan_schema() -> PlanSchema:
    """Get the global plan schema instance"""
    global _global_schema
    if _global_schema is None:
        _global_schema = PlanSchema()
    return _global_schema

def reset_plan_schema() -> None:
    """Reset the global plan schema instance (for testing)"""
    global _global_schema
    _global_schema = None
