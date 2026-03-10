"""
apps_rg.config - Configuration for Resume Generation app.
"""

from apps_rg.config.AgentSpec import RGAgentSpecs
from apps_rg.config.sovereign_config_loader_config import (
    get_config_path,
    load_rg_specs,
    reload_config,
)

__all__ = ["load_rg_specs", "get_config_path", "RGAgentSpecs", "reload_config"]
