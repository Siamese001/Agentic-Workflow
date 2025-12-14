import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class ContextProfile(BaseModel):
    """Profile capturing context budget hints used by planning and routing."""
    _context_budget: ContextBudget = Field(default_factory=ContextBudget)