"""Configuration to prevent pytest from collecting deprecated tests."""
import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)