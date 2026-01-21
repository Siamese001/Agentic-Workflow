from __future__ import annotations

"""
Naming utilities module.

Provides naming agents for file naming compliance and drift detection.
"""

# [GUARDED IMPORTS] Prevent cascading failures during agent discovery
try:
    from .NamingAgent import NamingAgent
except ImportError:
    NamingAgent = None

try:
    from .DriftDetectorAgent import DriftDetectorAgent
except ImportError:
    DriftDetectorAgent = None

__all__ = ["NamingAgent", "DriftDetectorAgent"]
