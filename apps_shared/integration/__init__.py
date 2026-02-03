"""
Shared integration module for domain applications.

Provides mixins and utilities for apps_rg and apps_lic to integrate
with the new feature-flagged agent system.
"""

from .domain_agent_mixin import DomainAgentMixin
from .integration_config import IntegrationConfig, get_domain_config

__all__ = [
    "DomainAgentMixin",
    "IntegrationConfig",
    "get_domain_config",
]
