"""Configuration to prevent pytest from collecting deprecated tests."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)