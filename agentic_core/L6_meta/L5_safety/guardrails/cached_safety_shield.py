#!/usr/bin/env python3
"""
CachedSafetyShield - Eternal L5 Safety Base with Redis Sovereign Cache
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import redis


class CachedSafetyShield:
    """
    Sovereign L5 shield base — enforces cache-first safety for instant protection.
    """
    def __init__(self, project_root: Path, session_id: str = "l5_global"):
        self.root = project_root
        self.session_id = session_id
        
        # Direct Redis connection for testing
        try:
            self.redis = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
        except Exception as e:
            print(f"Warning: Redis connection failed ({e}), using in-memory cache")
            self.redis = None
            self._memory_cache = {}

        # Sovereign prefixes
        self.prefix_gravity = f"l5_gravity:{session_id}"
        self.prefix_policy = f"l5_policy:{session_id}"

    def get_cached_verdict(self, category: str, identifier: str) -> Optional[Dict]:
        """Instant recall of previous safety decisions."""
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        try:
            if self.redis:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            else:
                return self._memory_cache.get(key)
        except Exception: 
            return None

    def store_verdict(self, category: str, identifier: str, verdict: Dict, ttl: int = 86400):
        """Warm the cache with a fresh safety verdict."""
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        try:
            # We add a timestamp to help the AutoImmune agent track frequency
            verdict["timestamp"] = __import__('datetime').datetime.now().isoformat()
            if self.redis:
                self.redis.set(key, json.dumps(verdict), ex=ttl)
            else:
                self._memory_cache[key] = verdict
        except Exception: 
            pass