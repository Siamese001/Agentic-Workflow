"""Dataclass models for lic_routing_rules."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""
    _minimum: int = 0
    _maximum: int = 20
    _guidance: Dict[str, str] = field(default_factory=dict)
