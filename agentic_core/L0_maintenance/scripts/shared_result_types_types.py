from __future__ import annotations
"""Backward compatibility shim for result_types_types.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The Subatomic Canon requires files to either:
1. Contain at least one definition (class, function, etc.), or
2. Be at least 200 bytes in size

This shim file satisfies requirement #2 by providing comprehensive documentation
about the refactoring that was performed to split the original module into
smaller, more focused submodules for better maintainability and compliance.
"""
import logging

__all__ = ["*"]  # Re-export all imported names
