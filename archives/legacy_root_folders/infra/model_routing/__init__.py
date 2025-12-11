"""Model routing infrastructure for cost/quality optimization.

Provides policy-driven model selection based on stage, archetype, and budget constraints.
"""

from archives.legacy_root_folders.infra.model_routing.policies import ModelRoutingPolicy

__all__ = ["ModelRoutingPolicy"]
