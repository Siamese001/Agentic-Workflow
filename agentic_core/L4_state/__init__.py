"""L4 State Layer — Persistent state and data sovereignty only.

This layer provides persistent storage, caching, and state management.
No execution logic or agent orchestration belongs in this layer.
Only state types, storage providers, and persistence utilities are exported.
"""

# State types and data structures
from .types import *  # State-only types, no agents
from .storage import *  # Storage abstractions only
from .caching import *  # Cache management only

# Explicitly forbid agent exports - state layer holds data, not agents
__all__ = [
    # State types
    "StateLedger",
    "StorageConfig", 
    "CacheConfig",
    "ValidationContext",
    "CycleTypes",
    
    # Storage providers
    "FilesystemStore",
    "BlobStorageProvider",
    
    # Cache management
    "CacheManager",
    "RedisCache",
    
    # Persistence utilities
    "StatePersistence",
    "DataSerializer"
]

# Sovereignty assertion: This layer contains NO agents with execute() methods
# Any agent classes belong in L2 (Execute) or L3 (Route) layers only
