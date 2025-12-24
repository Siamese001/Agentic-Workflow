#!/usr/bin/env python3
"""
NeuralAutoImmuneAgent - Sovereign Territory Lockdown
"""
import json
import redis
import os
from collections import Counter
from pathlib import Path

class NeuralAutoImmuneAgent:
    def __init__(self, project_root: Path):
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
        
        self.lockdown_threshold = 5 # 5 breaches = Lockdown

    def scan_for_outbreaks(self):
        """Scans the L5 cache for repeated non-compliance."""
        if self.redis:
            keys = self.redis.keys("l5_*:*")
            failures = []
            for k in keys:
                try:
                    v = json.loads(self.redis.get(k))
                    if not v.get("compliant", True):
                        failures.append(v.get("territory", "unknown"))
                except:
                    continue
        else:
            # Use memory cache for testing
            failures = []
            for k, v in self._memory_cache.items():
                if isinstance(v, dict) and not v.get("compliant", True):
                    failures.append(v.get("territory", "unknown"))
        
        counts = Counter(failures)
        lockdowns = [t for t, c in counts.items() if c >= self.lockdown_threshold]
        return lockdowns

    async def execute(self, ctx):
        targets = self.scan_for_outbreaks()
        if targets:
            for t in targets:
                # Mark territory as locked in Redis
                if self.redis:
                    self.redis.set(f"l5_lockdown:{t}", "true", ex=86400)
                else:
                    self._memory_cache[f"l5_lockdown:{t}"] = "true"
                print(f"   [🚨 LOCKDOWN] territory '{t}' isolated due to repeated breaches.")
            ctx.report("AutoImmune", 0, False, f"Lockdowns issued: {targets}")
        else:
            print("   [OK] AutoImmune: No active outbreaks.")
