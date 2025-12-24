#!/usr/bin/env python3
"""
NeuralAutoImmuneAgent - Eternal Sovereign Self-Defense System
"""

import json
import os
import redis
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

class NeuralAutoImmuneAgent:
    """
    Sovereign auto-immune response — isolates territories after repeated breaches.
    """
    def __init__(self, project_root: Path):
        self.root = project_root
        
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

        # [SOVEREIGN THRESHOLDS] Configurable via .env
        self.breach_threshold = int(os.getenv("IMMUNE_BREACH_THRESHOLD", "5"))
        self.window_minutes = int(os.getenv("IMMUNE_WINDOW_MINUTES", "30"))
        self.lockdown_prefix = "l5_immune_lockdown:"

    def detect_repeated_breaches(self) -> Dict:
        """Scan L5 cache for high-frequency violations."""
        try:
            # Gather all safety verdicts from the last window
            if self.redis:
                keys = self.redis.keys("l5_policy:*") + self.redis.keys("l5_gravity:*")
            else:
                # Use memory cache for testing
                keys = [k for k in self._memory_cache.keys() if k.startswith("l5_policy:") or k.startswith("l5_gravity:")]
            
            breaches = defaultdict(list)
            cutoff = datetime.now() - timedelta(minutes=self.window_minutes)

            for key in keys:
                if self.redis:
                    cached = self.redis.get(key)
                else:
                    cached = json.dumps(self._memory_cache.get(key, {}))
                
                if not cached: continue
                
                verdict = json.loads(cached)
                if not verdict.get("compliant", True):
                    ts = datetime.fromisoformat(verdict.get("timestamp", datetime.now().isoformat()))
                    if ts > cutoff:
                        # Composite key: Territory + the Agent responsible
                        t = verdict.get("territory", "unknown")
                        a = verdict.get("source_agent", "unknown")
                        breaches[f"{t}:{a}"].append(verdict)

            lockdowns = {}
            for source_id, events in breaches.items():
                if len(events) >= self.breach_threshold:
                    lockdown_key = f"{self.lockdown_prefix}{source_id}"
                    info = {
                        "count": len(events),
                        "locked_at": datetime.now().isoformat(),
                        "reason": "Repeated structural/policy breaches"
                    }
                    # Set the lockdown (default 7 days, but requires manual clear)
                    if self.redis:
                        self.redis.set(lockdown_key, json.dumps(info), ex=604800)
                    else:
                        self._memory_cache[lockdown_key] = info
                    lockdowns[source_id] = info

            return {"status": "success", "lockdowns": lockdowns}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def execute(self, ctx):
        """Run the defense scan."""
        report = self.detect_repeated_breaches()
        if report.get("lockdowns"):
            print(f"\n[🚨 IMMUNE RESPONSE] {len(report['lockdowns'])} lockdowns issued.")
            for sid, info in report["lockdowns"].items():
                print(f"   -> {sid} | Breaches: {info['count']}")
            ctx.report("AutoImmune", 0, False, f"Lockdowns: {list(report['lockdowns'].keys())}")
        else:
            print("   [OK] AutoImmune: Shield status green. No outbreaks.")
            ctx.report("AutoImmune", 1, True, "No repeated breaches detected.")
