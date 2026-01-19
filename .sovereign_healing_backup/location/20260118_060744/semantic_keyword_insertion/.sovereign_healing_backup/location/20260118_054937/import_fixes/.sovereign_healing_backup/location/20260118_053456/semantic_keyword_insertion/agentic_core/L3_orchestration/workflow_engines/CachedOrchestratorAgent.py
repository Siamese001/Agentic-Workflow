from __future__ import annotations
from dataclasses import dataclass
#!/usr/bin/env python3
"""
CachedOrchestratorAgent - Eternal L3 Orchestration with Redis Sovereign Cache
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

# NAMING FIXED: CachedOrchestratorAgent → CachedOrchestratorAgent
@dataclass
class CachedOrchestratorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Sovereign L3 orchestration base — Redis cache for all decisions and state.
    """
    def __init__(self, project_root: Path, mission_id: str) -> None:
        """Initialize the instance."""
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

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def get_cached_decision(self, category: str, identifier: str) -> Optional[Dict]:
        """Check if we've already solved this specific problem."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        key = self._get_cache_key(category, identifier)
        return self.get(key)

    def store_decision(self, category: str, identifier: str, decision: Dict, ttl: int = 3600) -> Any:
        """Save the result of a reasoning step."""
        key = self._get_cache_key(category, identifier)
        try:
            self.redis.set(key, json.dumps(decision), ex=ttl)
        except Exception: pass

    def cache_fission_decision(self, file_path: Path, decision: Dict) -> Any:
        """Execute cache_fission_decision operation."""
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_fission}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(decision), ex=604800)  # 7 days
        except: pass

    def get_cached_fission(self, file_path: Path) -> Optional[Dict]:
        """Execute get_cached_fission operation."""
        rel = str(file_path.relative_to(self.root))
        key = f"{self.prefix_fission}:{hashlib.sha256(rel.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except: return None

    def cache_routing_decision(self, Task: str, delegation: Dict) -> Any:
        """Execute cache_routing_decision operation."""
        key = f"{self.prefix_routing}:{hashlib.sha256(Task.encode()).hexdigest()}"
        try:
            self.redis.set(key, json.dumps(delegation), ex=3600) # 1 hour
        except: pass

    def get_cached_routing(self, Task: str) -> Optional[Dict]:
        """Execute get_cached_routing operation."""
        key = f"{self.prefix_routing}:{hashlib.sha256(Task.encode()).hexdigest()}"
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except: return None
