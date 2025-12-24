"""
Gravity Enforcement Module

This module provides the GravityEnforcerAgent that seals neural leaks
by commenting out forbidden imports from upstream to downstream.
"""

from .gravity_enforcer_agent import GravityEnforcerAgent

__all__ = ["GravityEnforcerAgent"]
