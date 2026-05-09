"""system_learning.runtime_adg — per-execution-trace snapshot-based runtime ADG.

Public surface
--------------
RuntimeADGNode        — a span captured as a graph node
RuntimeADGEdge        — a parent-child or temporal-sequence edge
RuntimeADGSnapshot    — immutable, content-addressed execution graph
create_runtime_adg_snapshot — factory (handles hashing + sorting)

RuntimeADGMaterializer — converts drained OTel spans → RuntimeADGSnapshot

InMemoryRuntimeADGStore    — in-memory store (tests / single-process)
FileBackedRuntimeADGStore  — file-backed L4 store (production)
L6MetaLearningBridge        — L6 meta-learning integration (system learning)
"""

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from system_learning.runtime_adg.l6_integration import L6MetaLearningBridge
from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    attributes_to_json,
    create_runtime_adg_snapshot,
)
from system_learning.runtime_adg.store import (
    FileBackedRuntimeADGStore,
    InMemoryRuntimeADGStore,
)

emit_determinism_digest("runtime_adg_init", "runtime_adg_init_digest")
record_execution_trace("runtime_adg_init", "runtime_adg_init_trace")

__all__ = [
    "RuntimeADGNode",
    "RuntimeADGEdge",
    "RuntimeADGSnapshot",
    "RuntimeADGMaterializer",
    "InMemoryRuntimeADGStore",
    "FileBackedRuntimeADGStore",
    "L6MetaLearningBridge",
    "attributes_to_json",
    "create_runtime_adg_snapshot",
]


__layer__ = "L6"
__l6_chapter__ = "06.1"
