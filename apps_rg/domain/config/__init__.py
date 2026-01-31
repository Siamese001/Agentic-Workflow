"""
RG Configuration Module - LIC-Aligned Sovereign Architecture.

Provides configuration loading and schema definitions.
"""

from __future__ import annotations

from apps_rg.domain.config.AgentSpec import RGAgentSpecs
from apps_rg.domain.config.SovereignConfigLoader import (
    get_config_path,
    load_rg_specs,
    reload_config,
)

__all__ = ["load_rg_specs", "get_config_path", "RGAgentSpecs", "reload_config"]
