from __future__ import annotations

from pydantic import BaseModel, Field

from core.models.models import ContextBudget


class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""

    context_budget: ContextBudget = Field(default_factory=ContextBudget)



