import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""
    _context_budget: ContextBudget = Field(default_factory=ContextBudget)

