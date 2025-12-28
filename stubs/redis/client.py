"""
Redis Client Stub - Cache Operations

PURPOSE:
    Stub implementations for Redis client operations.
    Provides in-memory cache storage for testing.

STATUS: Active - Used when Redis is unavailable
"""


class Redis:
    """
    Sovereign Stub for Redis State Caching.
    
    Provides in-memory dict-based storage that mimics Redis API.
    Used for testing cache operations without network calls.
    """
    def __init__(self, **kwargs):
        self.store = {}

    def get(self, key): return self.store.get(key)
    def set(self, key, value, **kwargs): 
        self.store[key] = value
        return True
    
    def ping(self): return True
    def hgetall(self, name): return self.store.get(name, {})

class StrictRedis(Redis): pass
