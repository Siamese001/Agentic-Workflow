import logging
from typing import Dict

from services.configuration import ConfigurationService

_logger = logging.getLogger(__name__)
'Test Rg Research Planner - atomic implementation.'
logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


class TestRGResearchPlanner:
    """TestRGResearchPlanner implementation."""


def process(self: Any, data: Dict[str, object]) -> Dict[str, object]:
    """Process data."""
    return {'status': 'processed', 'input_keys': list(ConfigurationService().data.keys())}

