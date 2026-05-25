"""Runtime ADG — canonical public API (agentic_core-owned).

As of 2026-05-01, the canonical import path for runtime ADG surfaces is
``agentic_core.L6_observability.runtime_trace.runtime_adg``. This module
re-exports every public name from the legacy ``system_learning.runtime_adg``
location, so new code imports from agentic_core while existing callers
continue to work through the legacy path.

Architectural boundary:
    - agentic_core OWNS the public types (``RuntimeADGSnapshot``,
      ``RuntimeADGNode``, ``RuntimeADGEdge``, store/materializer public
      surfaces).
    - system_learning continues to OWN the L4-backed persistence
      adapter (``system_learning.stores.version_store``). That backend
      coupling is why the code bytes remain in the legacy location —
      moving them would force a cross-layer shift of the version_store
      too, which is out of scope for the auditability pass.
    - The re-export establishes ``import from agentic_core`` as the
      canonical SSOT path. When a future pass promotes the version
      store into agentic_core, the implementation moves here without
      any consumer-side changes.

New code MUST import from this module. The legacy
``system_learning.runtime_adg`` path is retained for existing callers
only.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.materializer import (  # noqa: F401
    RuntimeADGMaterializer,
)
from agentic_core.L6_system_learning.snapshot import (  # noqa: F401
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    create_runtime_adg_snapshot,
)
from agentic_core.L6_system_learning.store import (  # noqa: F401
    FileBackedRuntimeADGStore,
    InMemoryRuntimeADGStore,
)

__all__ = [
    "FileBackedRuntimeADGStore",
    "InMemoryRuntimeADGStore",
    "RuntimeADGEdge",
    "RuntimeADGMaterializer",
    "RuntimeADGNode",
    "RuntimeADGSnapshot",
    "create_runtime_adg_snapshot",
]
