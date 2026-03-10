"""
apps_rg.config - Configuration for Resume Generation app.
"""

from apps_rg.config.AgentSpec import RGAgentSpecs
from apps_rg.config.sovereign_config_loader_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    get_config_path,
    load_rg_specs,
    reload_config,
)

__all__ = ["load_rg_specs", "get_config_path", "RGAgentSpecs", "reload_config"]
