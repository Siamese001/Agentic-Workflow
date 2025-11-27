"""Model routing infrastructure for cost/quality optimization.

Provides policy-driven model selection based on stage, archetype, and budget constraints.
"""

from .policies import ModelRoutingPolicy

__all__ = ["ModelRoutingPolicy"]
