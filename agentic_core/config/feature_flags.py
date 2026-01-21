"""
Feature Flags for Redis/Pinecone Integration

Environment-controlled flags for safe rollout of caching and vector features.
Set to 'false' to disable any integration without code changes.

SSOT Location: agentic_core/config/feature_flags.py
Migrated from: archives/location_violations/flags.py
"""

import os

# Redis caching - enables distributed cache for AST, compliance, and validation results
USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "true").lower() == "true"

# Pinecone vector store - enables semantic search for patterns, healing, and deduplication
USE_PINECONE = os.getenv("USE_PINECONE", "true").lower() == "true"

# Cache metrics collection - enables hit/miss/latency tracking for dashboard
CACHE_METRICS_ENABLED = os.getenv("CACHE_METRICS_ENABLED", "true").lower() == "true"

# Graceful degradation - if True, failures fall back to local cache silently
GRACEFUL_DEGRADATION = os.getenv("GRACEFUL_DEGRADATION", "true").lower() == "true"

__all__ = [
    "USE_REDIS_CACHE",
    "USE_PINECONE",
    "CACHE_METRICS_ENABLED",
    "GRACEFUL_DEGRADATION",
]
