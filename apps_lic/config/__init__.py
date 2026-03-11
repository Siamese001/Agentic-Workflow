"""
apps_lic.config - Configuration for LinkedIn Outreach app.
"""

from apps_lic.config.loader import get_config_path, load_agent_specs

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["load_agent_specs", "get_config_path"]
