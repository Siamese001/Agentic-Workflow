import logging
from typing import Dict

from services.configuration import ConfigurationService

_logger = logging.getLogger(__name__)
'Check Message Compliance - atomic execution layer.'
logger = logging.getLogger(__name__)


def check_message_compliance(data: Dict[str, object]) -> Dict[str, object]:
    """Process check message compliance data."""
    return {'status': 'processed', 'input_keys': list(ConfigurationService().data.keys())}


def get_check_message_compliance_config() -> Dict[str, object]:
    """Get configuration for check_message_compliance."""
    return {'enabled': True, 'version': '1.0'}

