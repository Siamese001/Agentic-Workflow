# [PHASE 7 MIGRATION SHIM]
import warnings

from agentic_core.L4_state.memory.omni_context_agent import *  # noqa: F401,F403

warnings.warn("Deprecated. Import from 'omni_context' instead.", DeprecationWarning, stacklevel=2)
