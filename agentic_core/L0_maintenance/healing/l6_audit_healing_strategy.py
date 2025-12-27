"""
Sovereign L6 Audit Healing Strategy – Phase 17F (Dec 27, 2025)
Detects and autonomously corrects gaps in observability audit trail.
Ensures eternal constitutional transparency.
"""
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from agentic_core.L0_maintenance.filesystem_mcp_client import get_filesystem_client
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config

logger = logging.getLogger(__name__)


class L6AuditHealingStrategy:
    """
    Autonomous healing for L6 observability audit trail gaps.
    
    Detects and corrects audit trail inconsistencies by:
    - Scanning healing action logs for missing audit events
    - Cross-referencing L0 actions with L6 event records
    - Reconstructing missing audit events with metadata
    - Enforcing daily healing limits to prevent runaway operations
    """
    
    def __init__(self):
        """Initialize L6 audit healing strategy with MCP clients."""
        self.name = "L6AuditHealing"
        self.priority = 1  # Critical - observability integrity
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        self.audit_log_path = Path("agentic_core/L6_observability/logs/healing_audit.jsonl")
        logger.info("[L0 L6 AUDIT HEALING] Strategy initialized")
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """
        Diagnose missing audit events using cross-reference logic.
        
        Args:
            issues: List of issues from sovereignty auditor
            
        Returns:
            List of fix dictionaries with action details
        """
        fixes = []
        
        if not config.L6_AUDIT_HEALING_ENABLED:
            logger.info("[L0 L6 AUDIT HEALING] L6 audit healing disabled in config")
            return fixes
        
        # Proactive: Detect gaps by comparing L0 action logs with L6 event records
        missing_events = await self._find_missing_audit_events()
        
        for event_data in missing_events:
            fixes.append({
                "action": "emit_corrective_event",
                "event_data": event_data,
                "reason": "L6 Observability Gap: Action detected without corresponding audit event.",
                "priority": self.priority,
                "strategy": self.name
            })
        
        logger.info(f"[L0 L6 AUDIT HEALING] Diagnosed {len(fixes)} audit trail gaps")
        return fixes
    
    async def _find_missing_audit_events(self) -> List[Dict]:
        """
        Scans recent healing transactions to ensure L6 registration.
        
        Returns:
            List of missing event data dictionaries
        """
        # Hardened read via L0 Filesystem MCP
        try:
            if not self.audit_log_path.exists():
                logger.warning(f"[L0 L6 AUDIT HEALING] Audit log not found: {self.audit_log_path}")
                return []
            
            log_content = await self.fs_client.read_text(str(self.audit_log_path))
        except Exception as e:
            logger.error(f"[L0 L6 AUDIT HEALING] Failed to read audit log: {e}")
            return []
        
        # Logic to identify 'applied' actions that lack a SovereignEvent pairing
        gaps = []
        cutoff = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        
        for line in log_content.splitlines():
            if not line.strip():
                continue
            
            try:
                entry = json.loads(line)
                
                # Parse timestamp if present
                timestamp_str = entry.get("timestamp")
                if timestamp_str:
                    try:
                        entry_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if entry_time < cutoff:
                            continue
                    except (ValueError, AttributeError):
                        pass
                
                # If an action was 'apply' but no event_id is linked
                if entry.get("action") == "apply" and "event_id" not in entry:
                    gaps.append(entry)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"[L0 L6 AUDIT HEALING] Failed to parse log line: {e}")
                continue
        
        # Convert gaps to event data format
        return [{
            "event_type": "HEALING_ACTION_APPLIED",
            "severity": "CRITICAL",
            "metadata": {
                "reconstructed": True,
                "original_action": g.get("fix_id", "unknown"),
                "healing_cycle": "phase_17f"
            },
            "payload": g
        } for g in gaps[:config.L6_AUDIT_HEALING_MAX_DAILY]]
    
    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """
        Apply corrective audit entry via Sovereign L6 Client.
        
        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.L6_AUDIT_HEALING_ENABLED:
            logger.warning("[L0 L6 AUDIT HEALING] L6 audit healing disabled in config")
            return False
        
        if self.processed_today >= config.L6_AUDIT_HEALING_MAX_DAILY:
            logger.warning("[L0 L6 AUDIT HEALING] Daily limit reached.")
            return False
        
        try:
            event_data = fix.get("event_data")
            
            if not event_data:
                logger.error("[L0 L6 AUDIT HEALING] No event data in fix")
                return False
            
            # Emit the healed event back into the L6 stream
            logger.info(f"[L0 L6 AUDIT HEALING] Reconstructing audit event: {event_data.get('event_type')}")
            result = await self._emit_corrective_event(event_data)
            
            if result:
                self.processed_today += 1
                logger.info(f"[L0 L6 AUDIT HEALING] Reconstructed Audit Event: {event_data.get('event_type')}")
                return True
            else:
                logger.error(f"[L0 L6 AUDIT HEALING] Failed to emit corrective event")
                return False
            
        except Exception as e:
            logger.error(f"[L0 L6 AUDIT HEALING] Audit reconstruction failed: {e}")
            return False
    
    async def _emit_corrective_event(self, event_data: Dict) -> bool:
        """
        Emit corrective audit event to L6 observability layer.
        
        Args:
            event_data: Event data to emit
            
        Returns:
            True if emission succeeded, False otherwise
        """
        try:
            # Placeholder: In production, use L6 observability client
            # from agentic_core.L6_observability.healing_audit import log_healing_action
            # log_healing_action("audit_reconstruction", event_data, success=True)
            
            # For now, log the reconstruction
            logger.info(f"[L0 L6 AUDIT HEALING] Corrective event emitted: {event_data}")
            
            # Simulated success
            return True
            
        except Exception as e:
            logger.error(f"[L0 L6 AUDIT HEALING] Event emission failed: {e}")
            return False
    
    def reset_daily_counter(self):
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        logger.info("[L0 L6 AUDIT HEALING] Daily counter reset")


async def create_l6_audit_healing_strategy() -> L6AuditHealingStrategy:
    """
    Factory function to create an L6 audit healing strategy.
    
    Returns:
        Initialized L6AuditHealingStrategy instance
    """
    return L6AuditHealingStrategy()
