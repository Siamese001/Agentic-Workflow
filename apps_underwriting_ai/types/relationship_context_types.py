"""
Relationship Context Types - Domain contracts for customer relationship data.
"""

from pydantic import BaseModel, Field


class RelationshipContext(BaseModel):
    """
    Existing banking relationship context.
    """

    existing_customer: bool = Field(False, description="Is existing customer")
    tenure_years: float | None = Field(None, ge=0, description="Years as customer")
    prior_exposure: float | None = Field(None, ge=0, description="Prior credit exposure")
    deposit_relationship: bool = Field(False, description="Has deposit relationship")
    historical_exceptions: list[str] = Field(
        default_factory=list, description="Historical exceptions granted",
    )
    past_due_history: list[str] = Field(default_factory=list, description="Past due incidents")

    class Config:
        json_schema_extra = {
            "example": {
                "existing_customer": True,
                "tenure_years": 5.5,
                "prior_exposure": 1500000.0,
                "deposit_relationship": True,
                "historical_exceptions": [],
                "past_due_history": [],
            },
        }
