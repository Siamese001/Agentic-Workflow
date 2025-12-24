#!/usr/bin/env python3
"""
MissionResumeAgent - Mission Continuity
"""
from pathlib import Path
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

class MissionResumeAgent:
    def __init__(self, project_root: Path):
        self.redis = RedisSovereignAgent(project_root).get_client()

    def get_last_checkpoint(self, mission_id):
        state = self.redis.get(f"l3_mission:{mission_id}:last_step")
        return int(state) if state else 0

    async def execute(self, ctx=None):
        print("   [OK] MissionResumeAgent: Continuity engine primed.")
