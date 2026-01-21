from __future__ import annotations

"""
CachedSafetyShield - Eternal L5 Safety Base with Redis Sovereign Cache
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import redis


class CachedSafetyShield:
    def __init__(self, project_root=None, session_id: str='l5_global'):
        from pathlib import Path
        self.root = project_root or Path('.')
        self.session_id = session_id
        try:
            import redis
            self.redis = redis.Redis(host=__import__('os').getenv('REDIS_HOST', 'localhost'), port=int(__import__('os').getenv('REDIS_PORT', 6379)), decode_responses=True)
            self.redis.ping()
        except Exception as e:
            print(f'Warning: Redis connection failed ({e}), using in-memory cache')
            self.redis = None
            self._memory_cache = {}
        self.prefix_gravity = f'l5_gravity:{session_id}'
        self.prefix_policy = f'l5_policy:{session_id}'

# Alias for backward compatibility

class cached_safety_shield_impl:
    """
    Sovereign L5 shield base — enforces cache-first safety for instant protection.
    """

    def __init__(self, project_root: Path, session_id: str='l5_global'):
        self.root = project_root
        self.session_id = session_id
        try:
            self.redis = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), decode_responses=True)
            self.redis.ping()
        except Exception as e:
            print(f'Warning: Redis connection failed ({e}), using in-memory cache')
            self.redis = None
            self._memory_cache = {}
        self.prefix_gravity = f'l5_gravity:{session_id}'
        self.prefix_policy = f'l5_policy:{session_id}'

    def get_cached_verdict(self, category: str, identifier: str) -> dict | None:
        """Instant recall of previous safety decisions."""
        key: Any = f'l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}'
        try:
            if self.redis:
                data: Any = self.redis.get(key)
                return json.loads(data) if data else None
            else:
                return self._memory_cache.get(key)
        except Exception:
            return None

    def store_verdict(self, category: str, identifier: str, Verdict: dict, ttl: int=86400) -> Any:
        """Warm the cache with a fresh safety Verdict."""
        key: Any = f'l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}'
        try:
            Verdict['timestamp'] = __import__('datetime').datetime.now().isoformat()
            if self.redis:
                self.redis.set(key, json.dumps(Verdict), ex=ttl)
            else:
                self._memory_cache[key] = Verdict
        except Exception:
            pass
