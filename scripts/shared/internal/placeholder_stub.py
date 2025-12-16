"""Fallback shim to replace deprecated archive imports."""
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class ArchiveFileAccessDeprecated:
    """Fallback class for deprecated archive imports."""

