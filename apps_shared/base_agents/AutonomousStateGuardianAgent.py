"""@deprecated
DEPRECATED: Use UnifiedStateManagementAgent instead.

This agent has been consolidated into UnifiedStateManagementAgent as part of
Phase 5 consolidation (2026-01-19). This file is retained for backward
compatibility during the transition period.

Migration:
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        UnifiedStateManagementAgent,
        get_state_manager,
        get_state_guardian,
    )
"""
import warnings
warnings.warn(
    "AutonomousStateGuardianAgent is deprecated. Use UnifiedStateManagementAgent instead.",
    DeprecationWarning,
    stacklevel=2
)

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
from dataclasses import dataclass
"""
L4 State: Autonomous State Guardian
Monitors and self-repairs state corruption with mirrored redundancy and state locking.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin

Logger = logging.getLogger(__name__)


# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
@dataclass
class AutonomousStateGuardianAgent(MCPHardenedMixin, HealerMixin):
    """
    L4 State Guardian that autonomously monitors and repairs state corruption.
    
    Features:
    - Continuous state integrity monitoring
    - Automatic corruption detection and repair
    - Mirrored manifest redundancy
    - Global state lock during recovery
    - Drift pattern learning
    """
    
    def __init__(self) -> None:
        """Initialize the instance."""
        # GRAVITY FIXED: Dynamic import for Checkpoint manager
        try:
            from agentic_core.L4_state.validation_context.autonomous_checkpoint_manager import create_autonomous_checkpoint_manager
            self.CheckpointManager = create_autonomous_checkpoint_manager()
        except ImportError:
            self.CheckpointManager = None
        self.state_manifest_path = Path(".canon_memory/state_manifest.json")
        self.state_manifest_backup = Path(".canon_memory/state_manifest.json.bak")
        self.corruption_log = Path(".canon_memory/corruption_events.json")
        self.meta_patterns = {}
        self.is_recovering = False  # Global L4 State Lock
        
        # Autonomy parameters
        self.verification_interval = 600  # 10 minutes
        self._guard_task = None
        
        # Ensure directories exist
        self.state_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self.load_meta_state()
        
        Logger.info("L4 Autonomous State Guardian initialized")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L4 compliance."""
        assert hasattr(self, 'state_manifest_path'), "Missing state_manifest_path"
        assert hasattr(self, 'is_recovering'), "Missing is_recovering"
        return True
    
    def awaken(self) -> Any:
        """L4: Explicitly activate the eternal guardianship"""
        if not self._guard_task:
            self._guard_task = asyncio.create_task(self.eternal_state_guardianship())
            Logger.info("L4 Eternal state guardianship awakened")
    
    def load_meta_state(self) -> Any:
        """Load manifest with mirrored redundancy"""
        if self.state_manifest_path.exists():
            try:
                raw = self.state_manifest_path.read_text(encoding="utf-8")
                data = json.loads(raw)
                # Mirror to backup immediately on successful load
                self.state_manifest_backup.write_text(raw, encoding="utf-8")
                self.meta_patterns = data.get("drift_patterns", {})
                Logger.info("L4 META: Loaded state manifest")
            except Exception as e:
                Logger.error(f"Primary manifest corrupt, attempting backup recovery: {e}")
                if self.state_manifest_backup.exists():
                    try:
                        backup_raw = self.state_manifest_backup.read_text(encoding="utf-8")
                        self.state_manifest_path.write_text(backup_raw, encoding="utf-8")
                        data = json.loads(backup_raw)
                        self.meta_patterns = data.get("drift_patterns", {})
                        Logger.info("L4 META: Recovered from backup manifest")
                    except Exception as backup_error:
                        Logger.error(f"Backup recovery failed: {backup_error}")
        else:
            Logger.info("L4 META: No existing manifest, starting fresh")
    
    def save_meta_state(self) -> Any:
        """Save manifest with mirrored redundancy"""
        try:
            data = {
                "drift_patterns": self.meta_patterns,
                "last_updated": datetime.now().isoformat()
            }
            raw = json.dumps(data, indent=2)
            
            # Write to primary
            self.state_manifest_path.write_text(raw, encoding="utf-8")
            
            # Mirror to backup
            self.state_manifest_backup.write_text(raw, encoding="utf-8")
            
            Logger.debug("L4 META: Saved state manifest with backup")
        except Exception as e:
            Logger.error(f"Failed to save meta state: {e}")
    
    async def verify_checkpoint_integrity(self, checkpoint_id: str) -> bool:
        """Verify a Checkpoint's integrity"""
        try:
            is_valid, errors = await self.CheckpointManager.verify_checkpoint(checkpoint_id)
            return is_valid
        except Exception as e:
            Logger.error(f"Checkpoint verification failed for {checkpoint_id}: {e}")
            return False
    
    async def detect_state_corruption(self) -> List[str]:
        """Detect corrupted checkpoints"""
        corrupt_ids = []
        
        try:
            history = self.CheckpointManager.get_checkpoint_history()
            
            for checkpoint_id in history:
                if not await self.verify_checkpoint_integrity(checkpoint_id):
                    corrupt_ids.append(checkpoint_id)
                    Logger.warning(f"L4: Detected corruption in Checkpoint {checkpoint_id}")
            
        except Exception as e:
            Logger.error(f"Corruption detection failed: {e}")
        
        return corrupt_ids
    
    async def initiate_self_repair(self, corrupt_ids: List[str]) -> Any:
        """L4: Sovereign recovery with State Lock"""
        self.is_recovering = True
        Logger.info(f"L4 SELF-REPAIR: Recovering {len(corrupt_ids)} states...")
        
        try:
            # Log corruption event
            self._log_corruption_event(corrupt_ids)
            
            # Find the most recent valid Checkpoint
            history = self.CheckpointManager.get_checkpoint_history()
            
            for cp_id in reversed(history):
                if cp_id not in corrupt_ids and await self.verify_checkpoint_integrity(cp_id):
                    Logger.info(f"L4: Rolling back to valid Checkpoint {cp_id}")
                    await self.CheckpointManager.rollback_to_checkpoint(cp_id)
                    
                    # Trigger reindex as a non-blocking Task
                    try:
                        from agentic_core.L2_execution.ToolRegistry.HybridRetriever import (
                            HybridRetriever,
                        )
                        asyncio.create_task(HybridRetriever()._rebuild_from_ingestion())
                        Logger.info("L4: Triggered background reindex")
                    except ImportError:
                        Logger.warning("L4: HybridRetriever not available for reindex")
                    
                    break
            else:
                Logger.error("L4: No valid Checkpoint found for recovery")
                
        except Exception as e:
            Logger.error(f"L4 Self-repair failed: {e}")
        finally:
            self.is_recovering = False
            Logger.info("L4: State lock released")
    
    def _log_corruption_event(self, corrupt_ids: List[str]) -> Any:
        """Log corruption events for pattern analysis"""
        try:
            events = []
            if self.corruption_log.exists():
                events = json.loads(self.corruption_log.read_text(encoding="utf-8"))
            
            event = {
                "timestamp": datetime.now().isoformat(),
                "corrupt_checkpoints": corrupt_ids,
                "count": len(corrupt_ids)
            }
            events.append(event)
            
            # Keep only last 100 events
            events = events[-100:]
            
            self.corruption_log.write_text(json.dumps(events, indent=2), encoding="utf-8")
            Logger.debug(f"L4: Logged corruption event with {len(corrupt_ids)} corrupted checkpoints")
            
        except Exception as e:
            Logger.error(f"Failed to log corruption event: {e}")
    
    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L4 state agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L4 state - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
    
    async def eternal_state_guardianship(self) -> Any:
        """L4: Continuous state monitoring and self-repair loop"""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Logger.info("L4: Eternal state guardianship active")
        
        while True:
            try:
                await asyncio.sleep(self.verification_interval)
                
                # Skip if already recovering
                if self.is_recovering:
                    Logger.debug("L4: Skipping verification during recovery")
                    continue
                
                # Detect corruption
                corrupt_ids = await self.detect_state_corruption()
                
                if corrupt_ids:
                    Logger.warning(f"L4: Detected {len(corrupt_ids)} corrupted states")
                    await self.initiate_self_repair(corrupt_ids)
                else:
                    Logger.debug("L4: State integrity verified")
                
                # Save meta state
                self.save_meta_state()
                
            except Exception as e:
                Logger.error(f"L4 Guardianship error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    def get_guardian_status(self) -> Dict[str, Any]:
        """Get guardian status"""
        return {
            "is_recovering": self.is_recovering,
            "verification_interval": self.verification_interval,
            "guard_task_active": self._guard_task is not None and not self._guard_task.done(),
            "manifest_exists": self.state_manifest_path.exists(),
            "backup_exists": self.state_manifest_backup.exists(),
            "drift_patterns_count": len(self.meta_patterns)
        }


def create_autonomous_state_guardian() -> AutonomousStateGuardian:
    """Factory function to create autonomous state guardian"""
    return AutonomousStateGuardian()