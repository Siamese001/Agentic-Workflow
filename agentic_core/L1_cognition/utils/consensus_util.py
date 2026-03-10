# [PHASE 7 MIGRATION SHIM]
import warnings

from .supreme_court import *

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

warnings.warn("Deprecated. Import from 'supreme_court' instead.", DeprecationWarning, stacklevel=2)
