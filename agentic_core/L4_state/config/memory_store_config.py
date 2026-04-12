import os
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "memory_store_config")
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@dataclass
class MemoryStoreConfig:
    """
    L4 Configuration: Memory Storage Parameters.
    Controls the physical and semantic limits of the Sovereign Memory.
    """

    # Vector Database (Pinecone/Chroma)
    VECTOR_DIMENSIONS: int = 1536
    VECTOR_METRIC: str = "cosine"

    # Short-Term Memory (Redis)
    STM_TTL_SECONDS: int = 3600  # 1 hour
    MAX_THOUGHTS_IN_CONTEXT: int = 50

    # Snapshotting
    ENABLE_AUTO_CHECKPOINTS: bool = True
    CHECKPOINT_INTERVAL_SECONDS: int = 300  # 5 minutes
    MAX_SNAPSHOTS_TO_RETAIN: int = 10

    # Paths
    STORAGE_ROOT: str = os.getenv("L4_STORAGE_ROOT", "./data/l4_state")


memory_config = MemoryStoreConfig()
