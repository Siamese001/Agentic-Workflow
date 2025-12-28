#!/usr/bin/env python3
"""
SovereignForensicsAgent - Drift Root-Cause Investigator
Analyzes immutable Redis audit trail for excessive structural modifications.
"""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from agentic_core.L4_state.validation_context.redis_sovereign_agent import (
    RedisSovereignAgent,
)


class SovereignForensicsAgent:
    """
    Sovereign forensics — detects uncontrolled structural drift.
    """
    def __init__(self, project_root: Path):
        self.redis = RedisSovereignAgent(project_root).get_client()
        self.threshold = 10  # Actions per hour

    def analyze_drift_patterns(self):
        cutoff = datetime.now() - timedelta(hours=1)
        keys = self.redis.keys("l4_audit:*trail")
        events = []
        for k in keys:
            for e in self.redis.lrange(k, 0, -1):
                data = json.loads(e)
                if datetime.fromisoformat(data['timestamp']) > cutoff:
                    events.append(data)
        
        counts = Counter(e['agent'] for e in events if e.get('action') in {'move', 'heal'})
        alerts = {a: c for a, c in counts.items() if c >= self.threshold}
        return {"status": "drift_alert" if alerts else "clean", "offenders": alerts}

    def analyze_drift(self) -> Dict:
        """Scan Redis audit trails for high-frequency agents."""
        if self.redis:
            trail_keys = self.redis.keys("l4_audit:*:trail")
            if not trail_keys:
                return {"status": "clean"}

            recent_events = []
            cutoff = datetime.now() - timedelta(hours=self.window_hours)

            try:
                for key in trail_keys:
                    raw_events = self.redis.lrange(key, 0, -1)
                    for raw in raw_events:
                        event = json.loads(raw)
                        # Parse timestamp and filter for structural actions
                        timestamp_str = event.get("timestamp", "")
                        if timestamp_str:
                            try:
                                # Handle both naive and aware timestamps
                                if 'T' in timestamp_str:
                                    if '+' in timestamp_str or 'Z' in timestamp_str:
                                        # ISO format with timezone
                                        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                    else:
                                        # Naive ISO format
                                        ts = datetime.fromisoformat(timestamp_str)
                                else:
                                    # Fallback parsing
                                    ts = datetime.fromisoformat(timestamp_str)
                                
                                # Make both naive for comparison
                                if ts.tzinfo:
                                    ts = ts.replace(tzinfo=None)
                                if cutoff.tzinfo:
                                    cutoff = cutoff.replace(tzinfo=None)
                                    
                                if ts > cutoff and event.get("action") in {"move", "heal", "archive", "prune"}:
                                    recent_events.append(event)
                            except (ValueError, TypeError):
                                # Skip events with invalid timestamps
                                continue
            except Exception as e:
                return {"status": "error", "message": str(e)}
        else:
            # Use in-memory audit trail for testing
            cutoff = datetime.now() - timedelta(hours=self.window_hours)
            recent_events = []
            for e in self._audit_trail:
                if e.get("action") in {"move", "heal", "archive", "prune"}:
                    # Parse timestamp for in-memory events
                    timestamp_str = e.get("timestamp", "")
                    if timestamp_str:
                        try:
                            event_time = datetime.fromisoformat(timestamp_str)
                            # Make both naive for comparison
                            if event_time.tzinfo:
                                event_time = event_time.replace(tzinfo=None)
                            if cutoff.tzinfo:
                                cutoff = cutoff.replace(tzinfo=None)
                            
                            if event_time > cutoff:
                                recent_events.append(e)
                        except (ValueError, TypeError):
                            # Include events without valid timestamps for testing
                            recent_events.append(e)

        if not recent_events:
            return {"status": "clean"}

        # Categorize by the agent responsible
        agent_stats = Counter(e.get("agent", "unknown") for e in recent_events)
        high_freq = {a: c for a, c in agent_stats.items() if c >= self.frequency_threshold}

        if high_freq:
            max_hits = max(high_freq.values())
            severity = next((v for k, v in sorted(self.severity_map.items(), reverse=True) if max_hits >= k), "MODERATE")
            
            report = {
                "status": "DRIFT_ALERT",
                "severity": severity,
                "offenders": high_freq,
                "total_events": len(recent_events),
                "high_frequency_agents": high_freq,
                "recommendation": "Investigate agent behavior — possible healing loop or uncontrolled fission"
            }
            
            # [MISSION AWARENESS] Check for active hops
            if self.redis:
                try:
                    active_missions = self.redis.keys("l3_mission:*:steps")
                    if active_missions:
                        report["impacted_missions"] = [k.split(":")[1] for k in active_missions]
                        report["safety_action"] = "HALT_RESUME"
                except Exception:
                    pass
            
            # [ETERNAL AUDIT] Store forensics report in Redis
            try:
                report_key = f"l4_forensics:report:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if self.redis:
                    self.redis.set(report_key, json.dumps(report), ex=604800) # 7 Day TTL
            except Exception: pass
            
            return report

        return {"status": "stable", "event_count": len(recent_events)}

    async def execute(self, ctx):
        """Standard execution hook for the validator loop."""
        report = self.analyze_drift()
        if report["status"] == "DRIFT_ALERT":
            msg = f"Forensic Alert ({report['severity']}): Excessive structural changes by {report['offenders']}"
            print(f"\n[!] SovereignForensicsAgent: {msg}")
            print(f"    Recommendation: {report['recommendation']}")
            ctx.report("Forensics", 0, False, f"Drift {report['severity']}: {report['high_frequency_agents']}")
            
            # [AUTO-IMMUNE TRIGGER]
            if report["severity"] == "CRITICAL_DRIFT":
                print("    [🚨 LOCKDOWN SUGGESTED] Critical drift detected. Consider manual quarantine.")
        else:
            print(f"   [OK] SovereignForensicsAgent: Structural pulse normal ({report.get('event_count', 0)} events)")
            ctx.report("Forensics", 1, True, "Structural changes within sovereign limits.")
