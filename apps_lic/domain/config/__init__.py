"""
configuration Domain for LIC.
Exposes type-safe configuration objects loaded from JSON.
"""

from .loader import get_config_path, load_agent_specs

__all__ = ["load_agent_specs", "get_config_path"]
