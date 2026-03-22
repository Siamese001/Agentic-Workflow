"""
apps_lic.config - Configuration for LinkedIn Outreach app.
"""
from apps_lic.config.loader import get_config_path, load_agent_specs

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

__all__ = ['load_agent_specs', 'get_config_path']
