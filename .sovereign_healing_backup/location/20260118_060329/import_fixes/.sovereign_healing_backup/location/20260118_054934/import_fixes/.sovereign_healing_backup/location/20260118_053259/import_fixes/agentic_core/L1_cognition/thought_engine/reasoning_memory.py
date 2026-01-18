from __future__ import annotations
"""L1 Cognition: Sovereign Reasoning Memory — ULTRA-HARDENED
Eternal thought history, scratchpad, and Redis persistence with L5 shielding.
Zero tolerance for corruption or overflow.
"""
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import redis


# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


Logger = logging.getLogger(__name__)

# Sovereign limits enforced at L5
# NAMING FIXED: MAX_THOUGHT_LENGTH → max_thought_length
max_thought_length = 4000      # Prevent reasoning overflow
# NAMING FIXED: MAX_SCRATCHPAD_SIZE → max_scratchpad_size
max_scratchpad_size = 16000    # 16k chars max
# NAMING FIXED: MAX_HISTORY_PER_FILE → max_history_per_file
max_history_per_file = 50      # Prevent unbounded growth
# NAMING FIXED: REDIS_TIMEOUT → redis_timeout
redis_timeout = 5
# NAMING FIXED: REDIS_CACHE_TTL → redis_cache_ttl
redis_cache_ttl = 60 * 60 * 24 * 7  # 7-day mission persistence

# NAMING FIXED: SovereignReasoningMemory → SovereignReasoningMemory
class SovereignReasoningMemory:
    """Ultra-hardened sovereign manager for cognitive artifacts."""
    
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, mission_id: str):
        with cls._lock:
            if mission_id not in cls._instances:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[mission_id] = instance
            return cls._instances[mission_id]
    
    def __init__(self, mission_id: str):
        if getattr(self, '_initialized', False):
            return
        
        self.mission_id = mission_id
        self.thought_history: List[Dict] = []
        self.scratchpad: Dict[str, str] = {}
        self.history_lock = threading.RLock()
        self.redis_pool = None
        self.redis_reasoning_key = f"reasoning_steps:{mission_id}"
        self.max_redis_steps = 1000  # Sovereign bound on total mission thoughts
        self._initialize_redis()
        self._initialized = True
    
    def _initialize_redis(self):
        """L4-hardened Redis connection with immediate failover logic."""
        try:
            url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_pool = redis.ConnectionPool.from_url(
                url,
                socket_connect_timeout=REDIS_TIMEOUT,
                socket_timeout=REDIS_TIMEOUT,
                health_check_interval=30
            )
            client = redis.Redis(connection_pool=self.redis_pool)
            client.ping()
            Logger.info("[L1 MEMORY] Eternal Redis link established")
        except Exception as e:
            Logger.critical(f"[L1 MEMORY BREACH] Redis link failed: {e}")
            mcp_authority.record_breach(f"Persistence Failure: {str(e)}")
            raise
    
    def add_thought(self, file_path: str, key_id: int, thought: str, step: int) -> None:
        """Record a cognitive step with L5 input shielding and hashing."""
        if len(thought) > MAX_THOUGHT_LENGTH:
            raise ValueError(f"Thought exceeds sovereign limit ({MAX_THOUGHT_LENGTH} chars)")
        
        import hashlib
        thought_hash = hashlib.sha256(thought.encode()).hexdigest()[:16]
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "mission_id": self.mission_id,
            "file": Path(file_path).name,
            "key_id": key_id,
            "step": step,
            "hash": thought_hash,
            "thought": thought
        }
        
        with self.history_lock:
            self.thought_history.append(entry)
            # Prune local cache to keep it lean
            file_entries = [e for e in self.thought_history if e["file"] == entry["file"]]
            if len(file_entries) > MAX_HISTORY_PER_FILE:
                self.thought_history = [e for e in self.thought_history if e["file"] != entry["file"]] + file_entries[-MAX_HISTORY_PER_FILE:]
        
        # [REDIS ETERNAL CACHE] Push reasoning step immediately for L4 persistence
        try:
            r = redis.Redis(connection_pool=self.redis_pool)
            entry_json = json.dumps(entry)
            # L5 Shield: Guard against massive payloads that could clog Redis
            if len(entry_json) > 8192:
                entry_json = json.dumps({**entry, "thought": entry["thought"][:4000] + "..."})
            
            r.rpush(self.redis_reasoning_key, entry_json)
            
            # Enforce sovereign bound: keep the mission log from ballooning
            if r.llen(self.redis_reasoning_key) > self.max_redis_steps:
                r.ltrim(self.redis_reasoning_key, -self.max_redis_steps, -1)
            
            r.expire(self.redis_reasoning_key, REDIS_CACHE_TTL)
            Logger.info(f"[L4 REASONING CACHE] Step persisted to Redis: {Path(file_path).name}")
        except Exception as e:
            Logger.critical(f"[L4 REASONING BREACH] Redis cache failed: {e}")
            mcp_authority.record_breach(f"Redis Reasoning Failure: {str(e)}")

    def update_scratchpad(self, file_path: str, content: str):
                    
        if len(content) > MAX_SCRATCHPAD_SIZE:
            raise ValueError("Scratchpad overflow.")
        self.scratchpad[file_path] = content

    def get_scratchpad(self, file_path: str) -> str:
                    
        return self.scratchpad.get(file_path, "")

    def _get_redis(self):
        """Get Redis client from pool."""
        return redis.Redis(connection_pool=self.redis_pool)

    def get_thought_history(self, file_path: Optional[str] = None, key_id: Optional[int] = None) -> List[Dict]:
        """Fast local recall from Redis with in-memory fallback."""
        try:
            r = self._get_redis()
            raw_steps = r.lrange(self.redis_reasoning_key, 0, -1)
            if raw_steps:
                cached_history = [json.loads(s) for s in raw_steps]
                if file_path or key_id:
                    return [
                        e for e in cached_history 
                        if (not file_path or e["file"] == Path(file_path).name) and
                           (key_id is None or e["key_id"] == key_id)
                    ]
                return cached_history
        except Exception as e:
            Logger.warning(f"Redis reasoning recall failed: {e} — falling back to memory")
            
        with self.history_lock:
            if file_path or key_id:
                filtered = [
                    dict(t) for t in self.thought_history
                    if (not file_path or t["file"] == Path(file_path).name) and
                       (key_id is None or t["key_id"] == key_id)
                ]
                return filtered
            return [dict(t) for t in self.thought_history]

    def export_history(self) -> str:
                    
        return json.dumps({
            "mission_id": self.mission_id,
            "exported_at": datetime.utcnow().isoformat(),
            "history": self.thought_history
        }, indent=2)