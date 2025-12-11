from __future__ import annotations

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel, Field

from archives.legacy_root_folders.core.models.models import ContextBudget


class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""

    context_budget: ContextBudget = Field(default_factory=ContextBudget)



