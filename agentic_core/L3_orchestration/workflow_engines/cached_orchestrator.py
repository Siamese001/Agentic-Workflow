#!/usr/bin/env python3
"""
CachedOrchestrator - Eternal L3 Orchestration with Redis Sovereign Cache
"""

import json
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List

import hashlib

from agentic_core.L4_state.validation_context.redis_sovereign_agent import RedisSovereignAgent

class CachedOrchestrator:
    """
    Sovereign L3 orchestration base — Redis cache for all decisions and state.
    """
    def __init__(self, project_root: Path, mission_id: str):
        self.root = project_root
        self.mission_id = mission_id
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

        # Cache prefixes for L3 orchestration
        self.prefix_mission = f"l3_mission:{mission_id}"
        self.prefix_fission = f"l3_fission:{mission_id}"
        self.prefix_routing = f"l3_routing:{mission_id}"
        self.prefix_healing = f"l3_healing:{mission_id}"

    def _get_cache_key(self, prefix: str, data: str) -> str:
        """Sovereign key generation."""
        h = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"{prefix}:{h}"

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

    def cache_fission_decision(self, file_path: Path, decision: Dict):
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_fission}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(decision), ex=604800)  # 7 days
        except: pass

    def get_cached_fission(self, file_path: Path) -> Optional[Dict]:
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_fission}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except: return None

    def cache_routing_decision(self, task: str, delegation: Dict):
        key = f"{self.prefix_routing}:{hashlib.sha256(task.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(delegation), ex=3600) # 1 hour
        except: pass

    def get_cached_routing(self, task: str) -> Optional[Dict]:
        key = f"{self.prefix_routing}:{hashlib.sha256(task.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except: return None