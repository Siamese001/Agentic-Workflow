#!/usr/bin/env python3
"""
CachedOrchestrator - Eternal L3 Orchestration with Redis
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

class CachedOrchestrator:
    """
    Sovereign orchestration base — all L3 engines inherit this for instant memory.
    """
    def __init__(self, project_root: Path, mission_id: str):
        self.root = project_root
        self.mission_id = mission_id
        # Single gateway to state
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

    def _get_cache_key(self, prefix: str, data: str) -> str:
        """Sovereign key generation."""
        h = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"l3:{prefix}:{self.mission_id}:{h}"

    def get_cached_decision(self, category: str, identifier: str) -> Optional[Dict]:
        """Check if we've already solved this specific problem."""
        key = self._get_cache_key(category, identifier)
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception: return None

    def store_decision(self, category: str, identifier: str, decision: Dict, ttl: int = 3600):
        """Save the result of a reasoning step."""
        key = self._get_cache_key(category, identifier)
        try:
            self.redis.set(key, json.dumps(decision), ex=ttl)
        except Exception: pass
