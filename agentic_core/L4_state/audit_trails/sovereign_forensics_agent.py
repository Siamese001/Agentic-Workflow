#!/usr/bin/env python3
"""
SovereignForensicsAgent - Drift Root-Cause Investigator
Analyzes immutable Redis audit trail for excessive structural modifications.
"""

import json
import redis
import os
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict

class SovereignForensicsAgent:
    """
    Sovereign forensics — detects uncontrolled structural drift.
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
            self._audit_trail = []

        # [SOVEREIGN THRESHOLDS]
        self.frequency_threshold = 15  # Events/hour
        self.window_hours = 1
        self.severity_map = {15: "MODERATE", 30: "HIGH", 50: "CRITICAL"}

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
            
            return {
                "status": "DRIFT_ALERT",
                "severity": severity,
                "offenders": high_freq,
                "total_events": len(recent_events)
            }

        return {"status": "stable", "event_count": len(recent_events)}

    async def execute(self, ctx):
        """Standard execution hook for the validator loop."""
        report = self.analyze_drift()
        if report["status"] == "DRIFT_ALERT":
            msg = f"Forensic Alert ({report['severity']}): Excessive structural changes by {report['offenders']}"
            print(f"\n[!] SovereignForensicsAgent: {msg}")
            ctx.report("Forensics", 0, False, msg)
        else:
            print(f"   [OK] SovereignForensicsAgent: Structural pulse normal ({report.get('event_count', 0)} events)")
            ctx.report("Forensics", 1, True, "Structural changes within sovereign limits.")
