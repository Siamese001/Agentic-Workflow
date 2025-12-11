from __future__ import annotations

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel, Field

from archives.legacy_root_folders.core.models.models import RetrievalConfig


class RetrievalProfile(BaseModel):
    """Retrieval configuration profile wrapping RetrievalConfig.

    Kept as a thin wrapper so that higher-level profiles can evolve
    without changing the RetrievalConfig schema used by META.
    """

    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)



