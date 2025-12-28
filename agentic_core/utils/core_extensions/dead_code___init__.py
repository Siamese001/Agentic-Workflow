"""
Dead Code Detection Module

This module provides tools for detecting unused code across the Python codebase,
including imports, functions, classes, and methods with class-aware tracking.
"""

from .dead_code_detector_agent import DeadCodeDetectorAgent

__all__ = ["DeadCodeDetectorAgent"]
