#!/usr/bin/env python3
"""
Phase 4.3: Sovereign Health Monitor - Historical Health Persistence (L6 -> L4)

This module persists health metrics to L4 State (Redis) for historical analysis
and trend tracking across autonomous healing cycles.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


class SovereignHealthMonitor:
    """
    Monitors and persists sovereign health metrics to L4 State.
    
    Tracks:
    - Domain compliance scores over time
    - Healing fix counts per domain
    - Historical health snapshots for trend analysis
    """
    
    def __init__(self, redis_client):
        """
        Initialize the health monitor with Redis client.
        
        Args:
            redis_client: Redis client instance for L4 State persistence
        """
        self.redis = redis_client
    
    def log_snapshot(self, domain: str, score: int, fixes: int) -> None:
        """
        Phase 4.3: Persists health metrics to L4 for historical analysis.
        
        Stores snapshots in a Redis list for time-series tracking, enabling:
        - Historical compliance trend analysis
        - Healing effectiveness metrics
        - Cross-domain health comparison
        
        Args:
            domain: Domain name (e.g., AGENTIC_CORE_DIR, APPS_LIC_DIR)
            score: Compliance score (0-100)
            fixes: Number of fixes applied in this healing cycle
        """
        timestamp = datetime.now().isoformat()
        snapshot = {
            "timestamp": timestamp,
            "domain": domain,
            "compliance_score": score,
            "total_fixes": fixes
        }
        
        try:
            # Store in Redis list for time-series tracking
            self.redis.lpush("sovereign_health_history", json.dumps(snapshot))
            
            # Also update current domain health
            self.redis.set(f"sovereign_health:{domain}", json.dumps({
                "compliance_score": score,
                "total_fixes": fixes,
                "last_updated": timestamp
            }))
            
            # Increment global fix counter
            self.redis.incr("autonomous_fixes_total", amount=fixes)
            
        except Exception as e:
            # Graceful degradation - health monitoring is optional
            print(f"[WARNING] Failed to persist health snapshot: {e}")
    
    def get_domain_health(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve current health metrics for a specific domain.
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dict with compliance_score, total_fixes, and last_updated, or None
        """
        try:
            data = self.redis.get(f"sovereign_health:{domain}")
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None
    
    def get_health_history(self, limit: int = 100) -> list:
        """
        Retrieve historical health snapshots.
        
        Args:
            limit: Maximum number of snapshots to retrieve
            
        Returns:
            List of health snapshot dictionaries, newest first
        """
        try:
            snapshots = self.redis.lrange("sovereign_health_history", 0, limit - 1)
            return [json.loads(s) for s in snapshots]
        except Exception:
            return []
    
    def get_total_fixes(self) -> int:
        """
        Get total number of autonomous fixes across all domains.
        
        Returns:
            Total fix count
        """
        try:
            total = self.redis.get("autonomous_fixes_total")
            return int(total) if total else 0
        except Exception:
            return 0
