"""Generic fact writeback routing and promotion primitives."""
from agentic_core.L4_state.fact_writeback.contracts import (
    FactWritebackProfile,
    FactWritebackStore,
    PromotedFactRow,
    PromotionRequest,
    ScalarMetadataValue,
    SparseSyncCallback,
    StagedFactRow,
    WriteBackDecision,
)
from agentic_core.L4_state.fact_writeback.engine import (
    FactWritebackEngine,
    norm,
    scalarize_metadata,
)

__all__ = [
    "FactWritebackEngine",
    "FactWritebackProfile",
    "FactWritebackStore",
    "PromotedFactRow",
    "PromotionRequest",
    "ScalarMetadataValue",
    "SparseSyncCallback",
    "StagedFactRow",
    "WriteBackDecision",
    "norm",
    "scalarize_metadata",
]
