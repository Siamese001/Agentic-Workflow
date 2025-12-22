"""Configuration to prevent pytest from collecting deprecated tests."""

import logging

_logger = logging.getLogger(__name__)
# Prevent pytest from collecting any test files in this directory
