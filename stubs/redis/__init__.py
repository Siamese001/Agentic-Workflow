"""
Redis Stub Package - External Client Integration

PURPOSE:
    Provides stub implementations for Redis cache operations.
    Enables testing of caching functionality without live Redis connection.

STATUS: Active - Used for testing L4 State layer
INTEGRATION: Connected via Redis at localhost:6379 when available

CLASSES:
    - Redis: Stub for Redis client operations (get, set, ping)
    - StrictRedis: Strict mode Redis stub (inherits from Redis)
"""
from .client import Redis, StrictRedis
__all__ = ["Redis", "StrictRedis"]
