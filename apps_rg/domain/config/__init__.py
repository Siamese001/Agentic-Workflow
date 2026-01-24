"""
RG Configuration Module - LIC-Aligned Sovereign Architecture.

Provides configuration loading and schema definitions.
"""

from __future__ import annotations

from apps_rg.domain.config.loader import load_rg_specs, get_config_path
from apps_rg.domain.config.schemas import RGAgentSpecs

__all__ = ["load_rg_specs", "get_config_path", "RGAgentSpecs"]
