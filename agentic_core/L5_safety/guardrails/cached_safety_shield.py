#!/usr/bin/env python3
"""
CachedSafetyShield - Eternal L5 Safety with Redis Sovereign Cache
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

class CachedSafetyShield:
    """
    Sovereign L5 shield base — enforces cache-first safety checks for instant protection.
    """
    def __init__(self, project_root: Path, session_id: str = "global"):
        self.root = project_root
        self.session_id = session_id
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

        # Cache prefixes for L5 safety
        self.prefix_gravity = f"l5_gravity:{session_id}"
        self.prefix_policy = f"l5_policy:{session_id}"
        self.prefix_guardrail = f"l5_guardrail:{session_id}"

    def cache_gravity_verdict(self, file_path: Path, verdict: Dict):
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_gravity}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(verdict), ex=604800)  # 7 days
        except Exception: pass

    def get_cached_gravity(self, file_path: Path) -> Optional[Dict]:
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_gravity}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception: return None

    def cache_policy_verdict(self, prompt: str, verdict: Dict):
        key = f"{self.prefix_policy}:{hashlib.sha256(prompt.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(verdict), ex=86400) # 24h
        except Exception: pass

    def get_cached_policy(self, prompt: str) -> Optional[Dict]:
        key = f"{self.prefix_policy}:{hashlib.sha256(prompt.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception: return None
