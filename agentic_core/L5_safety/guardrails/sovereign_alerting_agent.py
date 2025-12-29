#!/usr/bin/env python3
"""
SovereignAlertingAgent - The System Voice
"""
import json
from datetime import datetime
from pathlib import Path

from agentic_core.L4_state.validation_context.redis_sovereign_agent import (
    RedisSovereignAgent,
)


# NAMING FIXED: SovereignAlertingAgent → sovereign_alerting_agent
class sovereign_alerting_agent:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.redis = RedisSovereignAgent(project_root).get_client()
        self.alert_key = "l5_alerts:critical"

    def trigger_alert(self, category: str, details: dict):
        """The Flare: Logs to Redis and prints to console."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "details": details
        }
        try:
            self.redis.rpush(self.alert_key, json.dumps(alert))
        except Exception: pass

        print(f"\n[🚨 SOVEREIGN ALERT] {category.upper()}")
        print(f"   Details: {json.dumps(details, indent=2)}\n")

    async def execute(self, ctx):
                    '''Brief description of functionality and purpose.'''
                    
        # Scan the report list for anything marked 'critical'
        critical_issues = [r for r in ctx.report_list if r.get("severity") == "critical"]
        if critical_issues:
            self.trigger_alert("CRITICAL_SYSTEM_BREACH", {"issues": critical_issues})
            ctx.report("Alerting", 0, False, "Critical alerts triggered!")
        else:
            print("   [OK] AlertingAgent: Perimeter quiet.")
            ctx.report("Alerting", 1, True, "No critical alerts.")
