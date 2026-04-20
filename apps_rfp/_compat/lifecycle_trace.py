"""Optional lifecycle trace compatibility shim.

Allows apps_rfp to import and run in standalone mode when agentic_core is absent.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        LayerSegment,
        L0_ROUTING,
        L1_REASONING,
        L2_EXECUTION,
        L3_ORCHESTRATION,
        L4_STATE,
        L5_SAFETY,
        L6_OBSERVABILITY,
        _STANDALONE,
        _real_contract,
        name,
    )  # noqa: F401
    import agentic_core.runtime.contracts.lifecycle_trace_contract as _real_contract  # noqa: F401

    _STANDALONE = False
except ImportError:
    _real_contract = None  # type: ignore[assignment]
    _STANDALONE = True

    class LayerSegment(str, Enum):  # type: ignore[no-redef]
        L0_ROUTING = "L0_ROUTING"
        L1_REASONING = "L1_REASONING"
        L2_EXECUTION = "L2_EXECUTION"
        L3_ORCHESTRATION = "L3_ORCHESTRATION"
        L4_STATE = "L4_STATE"
        L5_SAFETY = "L5_SAFETY"
        L6_OBSERVABILITY = "L6_OBSERVABILITY"

    def _noop(*args: Any, **kwargs: Any) -> None:
        return None

    def emit_replay_key(*args: Any, **kwargs: Any) -> str:
        return "standalone"

    def emit_determinism_digest(*args: Any, **kwargs: Any) -> str:
        return "standalone"


def __getattr__(name: str) -> Any:
    if not _STANDALONE and _real_contract is not None:
        try:
            return getattr(_real_contract, name)
        except AttributeError:
            pass
    if name.startswith("_emit_"):
        return lambda *args, **kwargs: None
    raise AttributeError(name)
