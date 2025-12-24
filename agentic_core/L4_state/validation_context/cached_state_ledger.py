#!/usr/bin/env python3
"""
CachedStateLedger - Eternal L4 State with Redis Sovereign Cache
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

class CachedStateLedger:
    """
    Sovereign L4 state base — enforces cache-first state access and audit persistence.
    """
    def __init__(self, project_root: Path, session_id: str):
        self.root = project_root
        self.session_id = session_id
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

        # Cache prefixes for L4 state
        self.prefix_context = f"l4_context:{session_id}"
        self.prefix_audit = f"l4_audit:{session_id}"
        self.prefix_historian = f"l4_historian:{session_id}"

    def cache_validation_context(self, key: str, context: Dict):
        full_key = f"{self.prefix_context}:{key}"
        try:
            self.redis.set(full_key, json.dumps(context), ex=86400) # 24h
        except Exception: pass

    def get_cached_validation_context(self, key: str) -> Optional[Dict]:
        full_key = f"{self.prefix_context}:{key}"
        try:
            data = self.redis.get(full_key)
            return json.loads(data) if data else None
        except Exception: return None

    def append_audit_trail(self, event: Dict):
        """Immutable append-only audit via Redis Lists"""
        try:
            trail_key = f"{self.prefix_audit}:trail"
            self.redis.rpush(trail_key, json.dumps(event))
            self.redis.expire(trail_key, 31536000) # 1 year TTL
        except Exception: pass

    def get_audit_trail(self) -> List[Dict]:
        try:
            trail_key = f"{self.prefix_audit}:trail"
            raw = self.redis.lrange(trail_key, 0, -1)
            return [json.loads(r) for r in raw]
        except Exception: return []
