import os
from dataclasses import dataclass


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
