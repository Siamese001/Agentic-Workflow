#!/usr/bin/env python3
"""
SovereignForensicsAgent - Drift Root-Cause Auditor
"""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

class SovereignForensicsAgent:
    def __init__(self, project_root: Path):
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()
        self.alert_threshold = 10 # 10 actions/hour is suspicious

    def analyze_drift(self):
        cutoff = datetime.now() - timedelta(hours=1)
        keys = self.redis.keys("l4_audit:*")
        
        actions = []
        for k in keys:
            events = self.redis.lrange(k, 0, -1)
            for e in events:
                data = json.loads(e)
                # Filter for structural changes in the last hour
                if data.get('action') in ['move', 'archive']:
                    actions.append(data.get('agent', 'unknown'))

        counts = Counter(actions)
        rogue_agents = {a: c for a, c in counts.items() if c > self.alert_threshold}
        return rogue_agents

    async def execute(self, ctx=None):
        rogue = self.analyze_drift()
        if rogue:
            msg = f"Potential instability! High-freq agents: {rogue}"
            print(f"   [!] Forensics: {msg}")
            if ctx: ctx.report("Forensics", 0, False, msg)
        else:
            print("   [OK] Forensics: Structural evolution stable.")
