"""Fallback shim to replace deprecated archive imports."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class ArchiveFileAccessDeprecated:
    """Fallback class for deprecated archive imports."""