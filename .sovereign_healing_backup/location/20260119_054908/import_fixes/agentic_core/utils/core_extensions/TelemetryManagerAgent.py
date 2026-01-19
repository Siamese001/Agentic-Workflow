"""
Centralized telemetry system using Redis Pub/Sub for real-time dashboarding.
Replaces legacy file-based 'runtime_state.json' polling.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class TelemetryManager:
    """
    Centralized telemetry system using Redis Pub/Sub for real-time dashboarding.
    Replaces legacy file-based 'runtime_state.json' polling.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.redis = None
            cls._instance.stream_key = "runtime:events"
            cls._instance.state_key = "runtime:live_state"
        return cls._instance

    def ensure_redis(self):
        """Lazy load Redis connection to avoid circular imports during boot."""
        if self.redis is None:
            try:
                from agentic_core.utils.core_extensions.redis import SovereignRedisClient
                self.redis = SovereignRedisClient()
            except ImportError:
                pass  # Graceful degradation if core isn't loaded

    def push_state(self, updates: Dict[str, Any]):
        """
        Push state updates (merged client-side) and publish change event.
        Used for persistent values like 'strategy_weights' or 'current_agent'.
        """
        self.ensure_redis()
        if not self.redis or not self.redis._get_client():
            return

        # 1. Update persistent state hash in Redis (Snapshot)
        current = self.redis.get(self.state_key) or "{}"
        state = json.loads(current) if isinstance(current, str) else {}
        state.update(updates)
        self.redis.execute('set', key=self.state_key, value=json.dumps(state))

        # 2. Publish update event for live stream
        msg = json.dumps({"type": "state_update", "data": updates, "timestamp": datetime.now().isoformat()})
        self.redis._get_client().publish(self.stream_key, msg)

    def log_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Publish a discrete event (fire-and-forget).
        Used for 'cache_hit', 'experience_stored', 'error'.
        """
        self.ensure_redis()
        if not self.redis or not self.redis._get_client():
            return

        msg = json.dumps({
            "type": "event",
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        })
        self.redis._get_client().publish(self.stream_key, msg)
