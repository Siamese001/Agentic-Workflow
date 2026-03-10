# [PHASE 7 MIGRATION SHIM]
import warnings

from agentic_core.L3_orchestration.engines.omni_context_engine import *  # noqa: F401,F403

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

warnings.warn("Deprecated. Import from 'omni_context' instead.", DeprecationWarning, stacklevel=2)
