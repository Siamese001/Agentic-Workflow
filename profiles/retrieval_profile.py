from __future__ import annotations

from pydantic import BaseModel, Field

from core.models.models import RetrievalConfig


class RetrievalProfile(BaseModel):
    """Retrieval configuration profile wrapping RetrievalConfig.

    Kept as a thin wrapper so that higher-level profiles can evolve
    without changing the RetrievalConfig schema used by META.
    """

    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
