"""
NeuralAutoImmuneAgent - Eternal Sovereign Self-Defense System
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
import redis

class NeuralAutoImmuneAgent:
    """
    Sovereign auto-immune response — isolates territories after repeated breaches.
    """

    def __init__(self, project_root: Path):
        self.root = project_root
        try:
            self.redis = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), decode_responses=True)
            self.redis.ping()
        except Exception as e:
            print(f'Warning: Redis connection failed ({e}), using in-memory cache')
            self.redis = None
            self._memory_cache = {}
        self.breach_threshold = int(os.getenv('IMMUNE_BREACH_THRESHOLD', '5'))
        self.window_minutes = int(os.getenv('IMMUNE_WINDOW_MINUTES', '30'))
        self.lockdown_prefix = 'l5_immune_lockdown:'

    def detect_repeated_breaches(self) -> Dict:
        """Scan L5 cache for high-frequency violations."""
        try:
            if self.redis:
                keys: Any = self.redis.keys('l5_policy:*') + self.redis.keys('l5_gravity:*')
            else:
                keys: Any = [k for k in self._memory_cache.keys() if k.startswith('l5_policy:') or k.startswith('l5_gravity:')]
            breaches: Any = defaultdict(list)
            cutoff: Any = datetime.now() - timedelta(minutes=self.window_minutes)
            for key in keys:
                if self.redis:
                    cached: Any = self.redis.get(key)
                else:
                    cached: Any = json.dumps(self._memory_cache.get(key, {}))
                if not cached:
                    continue
                verdict: Any = json.loads(cached)
                if not verdict.get('compliant', True):
                    ts: Any = datetime.fromisoformat(verdict.get('timestamp', datetime.now().isoformat()))
                    if ts > cutoff:
                        t: Any = verdict.get('territory', 'unknown')
                        a: Any = verdict.get('source_agent', 'unknown')
                        breaches[f'{t}:{a}'].append(verdict)
            lockdowns: Any = {}
            for source_id, events in breaches.items():
                if len(events) >= self.breach_threshold:
                    lockdown_key: Any = f'{self.lockdown_prefix}{source_id}'
                    info: Any = {'count': len(events), 'locked_at': datetime.now().isoformat(), 'reason': 'Repeated structural/policy breaches'}
                    if self.redis:
                        self.redis.set(lockdown_key, json.dumps(info), ex=604800)
                    else:
                        self._memory_cache[lockdown_key] = info
                    lockdowns[source_id] = info
            return {'status': 'success', 'lockdowns': lockdowns}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def execute(self, ctx: Any) -> Any:
        """Run the defense scan."""
        report: Any = self.detect_repeated_breaches()
        if report.get('lockdowns'):
            print(f"\n[🚨 IMMUNE RESPONSE] {len(report['lockdowns'])} lockdowns issued.")
            for sid, info in report['lockdowns'].items():
                print(f"   -> {sid} | Breaches: {info['count']}")
            ctx.report('AutoImmune', 0, False, f"Lockdowns: {list(report['lockdowns'].keys())}")
        else:
            print('   [OK] AutoImmune: Shield status green. No outbreaks.')
            ctx.report('AutoImmune', 1, True, 'No repeated breaches detected.')


# PascalCase is now the canonical name
