#!/usr/bin/env python3
"""
CachedStateLedger - Eternal L4 State with Redis Sovereign Cache
"""

import json
import redis
import os
from pathlib import Path
from typing import Dict, List, Optional

class CachedStateLedger:
    """
    Sovereign L4 state base — Redis cache for context, audit, historian.
    All L4 components inherit from this.
    """
    def __init__(self, project_root: Path, session_id: str):
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
            self._audit_trail = []

        # Eternal cache prefixes
        self.prefix_context = f"l4_context:{session_id}"
        self.prefix_audit = f"l4_audit:{session_id}"
        self.prefix_historian = f"l4_historian:{session_id}"

    def cache_validation_context(self, key: str, context: Dict):
        """Cache validation context for instant access"""
        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                self.redis.set(full_key, json.dumps(context), ex=86400)  # 24h
            else:
                self._memory_cache[full_key] = context
        except Exception: pass

    def get_cached_validation_context(self, key: str) -> Optional[Dict]:
        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                data = self.redis.get(full_key)
                if data:
                    return json.loads(data)
            else:
                return self._memory_cache.get(full_key)
        except Exception: pass
        return None

    def append_audit_event(self, event: Dict):
        """Immutable append-only audit trail via Redis List"""
        try:
            if self.redis:
                trail_key = f"{self.prefix_audit}:trail"
                self.redis.rpush(trail_key, json.dumps(event))
                self.redis.expire(trail_key, 31536000)  # 1 year TTL
            else:
                self._audit_trail.append(event)
        except Exception: pass
