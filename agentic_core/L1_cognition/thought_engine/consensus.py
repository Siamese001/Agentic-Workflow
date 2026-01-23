# [PHASE 7 MIGRATION SHIM]
import warnings
from .supreme_court import *

warnings.warn("Deprecated. Import from 'supreme_court' instead.", DeprecationWarning, stacklevel=2)
