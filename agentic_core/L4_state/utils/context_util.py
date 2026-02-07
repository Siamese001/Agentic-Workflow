# [PHASE 7 MIGRATION SHIM]
import warnings

from agentic_core.L3_orchestration.engine.omni_context_engine import *  # noqa: F401,F403

warnings.warn("Deprecated. Import from 'omni_context' instead.", DeprecationWarning, stacklevel=2)
