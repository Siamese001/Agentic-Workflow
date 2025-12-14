"""Dataclass models for lic_routing_rules."""
import logging


logger = logging.getLogger(__name__)
# from .lic_routing_rules_enums import *  # Star import removed

@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""
    minimum: int = 0
    maximum: int = 20
    guidance: Dict[str, str] = field(default_factory=dict)
