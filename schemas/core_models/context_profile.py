from __future__ import annotations

from pydantic import BaseModel, Field

# from archives.legacy_root_folders.core.models.models import ContextBudget  # DEPRECATED: Archive import removed to protect archives from validation edits

class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""

    context_budget: ContextBudget = Field(default_factory=ContextBudget)
