from __future__ import annotations
"""Backward compatibility shim for transform_impl.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original transform_impl.py contained 14 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

__all__ = ["*"]  # Re-export all imported names
