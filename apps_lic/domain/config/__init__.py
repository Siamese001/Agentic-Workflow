"""
Configuration Domain for LIC.
Exposes type-safe configuration objects loaded from JSON.
"""
from .loader import load_agent_specs, get_config_path

__all__ = ["load_agent_specs", "get_config_path"]
