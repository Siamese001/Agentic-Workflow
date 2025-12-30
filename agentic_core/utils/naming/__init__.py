"""
Naming utilities module.

Provides naming agents for file naming compliance and drift detection.
"""

# [GUARDED IMPORTS] Prevent cascading failures during agent discovery
try:
    from .naming_agent import naming_agent, NamingAgent
except ImportError:
    naming_agent = None
    NamingAgent = None

try:
    from .drift_detector_agent import drift_detector_agent, DriftDetectorAgent
except ImportError:
    drift_detector_agent = None
    DriftDetectorAgent = None

__all__ = ["naming_agent", "NamingAgent", "drift_detector_agent", "DriftDetectorAgent"]
