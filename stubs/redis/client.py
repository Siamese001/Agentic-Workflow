class Redis:
    """Sovereign Stub for Redis State Caching."""
    def __init__(self, **kwargs):
        self.store = {}

    def get(self, key): return self.store.get(key)
    def set(self, key, value, **kwargs): 
        self.store[key] = value
        return True
    
    def ping(self): return True
    def hgetall(self, name): return self.store.get(name, {})

class StrictRedis(Redis): pass
