"""Configuration to prevent pytest from collecting deprecated tests."""
import logging


logger = logging.getLogger(__name__)
# Prevent pytest from collecting any test files in this directory
collect_ignore_glob = ["*.py"]
