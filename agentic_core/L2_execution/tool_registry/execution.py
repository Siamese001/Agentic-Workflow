# [PHASE 7 MIGRATION SHIM]
import warnings

from .subprocess_executor import *

warnings.warn(
    "Deprecated. Import from 'subprocess_executor' instead.", DeprecationWarning, stacklevel=2
)
