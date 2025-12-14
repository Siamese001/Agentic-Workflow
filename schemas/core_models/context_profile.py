import logging




logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.core.models.models import ContextBudget  # DEPRECATED: Archiv...

class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""

    _context_budget: ContextBudget = Field(default_factory=ContextBudget)
