"""Fallback shim to replace deprecated archive imports."""
import logging



logger = logging.getLogger(__name__)
# This file serves as a fallback to break import chains into the immutable archives/
# Any import from archives/ should be replaced with this shim to prevent Python
# from loading archived files during validation.

class ArchiveFileAccessDeprecated:
    """Fallback class for deprecated archive imports."""

# Common fallback objects that might be imported

# Add more as needed during the import replacement process
