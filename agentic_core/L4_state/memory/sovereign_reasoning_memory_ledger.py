from __future__ import annotations

"\nL1 Cognition: Sovereign Reasoning Memory — ULTRA-HARDENED\n[PHASE 17 REFACTOR] Uses SovereignBaseAgent native Redis capabilities.\n"
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


class SovereignReasoningMemory(SovereignBaseAgent):
    """
    Ultra-hardened sovereign manager for cognitive artifacts.
    Inherits Redis connection from SovereignBaseAgent -> RedisCacheMixin.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        super().__init__()
        # guardian: allow-magic-config
        self.max_thought_length = 4000
        # guardian: allow-magic-config
        self.max_history_per_file = 50
        self.redis_cache_ttl = 604800
        self.mission_id = "default_mission"
        self.thought_history: list[dict] = []
        self.history_lock = threading.RLock()
        self.redis_reasoning_key = f"reasoning:{self.mission_id}:history"

    @classmethod
    def get_instance(cls) -> SovereignReasoningMemory:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def add_thought(self, file_path: str, thought: str, key_id: str = None) -> None:
        if len(thought) > self.max_thought_length:
            thought = thought[: self.max_thought_length] + "...[TRUNCATED]"
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "file": Path(file_path).name,
            "thought": thought,
            "key_id": key_id or "general",
        }
        with self.history_lock:
            self.thought_history.append(entry)
            if len(self.thought_history) > self.max_history_per_file * 10:
                self.thought_history = self.thought_history[-self.max_history_per_file :]
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                self.redis_client.rpush(self.redis_reasoning_key, json.dumps(entry))
                self.redis_client.ltrim(self.redis_reasoning_key, -self.max_history_per_file, -1)
                self.redis_client.expire(self.redis_reasoning_key, self.redis_cache_ttl)
            # guardian: allow-silent-swallow
            except Exception as e:
                self.log_warning(f"Redis write failed: {e}")

    def get_history(self, file_path: str = None) -> list[dict]:
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                raw = self.redis_client.lrange(self.redis_reasoning_key, 0, -1)
                return [json.loads(x) for x in raw]
            # guardian: allow-silent-swallow
            except Exception:
                pass
        with self.history_lock:
            return list(self.thought_history)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
