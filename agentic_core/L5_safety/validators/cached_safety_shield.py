from __future__ import annotations

"""CachedSafetyShield - Eternal L5 Safety Base with Sovereign Cache."""
import hashlib
from pathlib import Path
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class CachedSafetyShield(SovereignBaseAgent):
    def __init__(self, project_root=None, session_id: str = "l5_global"):
        super().__init__()
        self.root = project_root or Path(".")
        self.session_id = session_id
        self.prefix_gravity = f"l5_gravity:{session_id}"
        self.prefix_policy = f"l5_policy:{session_id}"

    def get_cached_verdict(self, category: str, identifier: str) -> dict | None:
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        return self.cache_get(key)

    def store_verdict(
        self, category: str, identifier: str, verdict: dict, ttl: int = 86400
    ) -> None:
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        verdict["timestamp"] = __import__("datetime").datetime.now().isoformat()
        self.cache_set(key, verdict, ttl=ttl)


cached_safety_shield_impl = CachedSafetyShield
