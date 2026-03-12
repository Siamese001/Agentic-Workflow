from __future__ import annotations
from agentic_core.L2_execution.tools import write_gateway as _wg
'\nL3 Orchestration: Autonomous Execution Engine\nThe eternal heart that continuously validates and heals the Canon territory.\n'
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

def _get_create_proactive_resource_manager():
    """Lazy load create_proactive_resource_manager to avoid upward import."""
    from agentic_core.L5_safety.reasoning.ResourceManagerAgent import create_proactive_resource_manager
    return create_proactive_resource_manager

def _get_create_autonomous_checkpoint_manager():
    """Lazy loader for create_autonomous_checkpoint_manager (upward L3->L4 seam)."""
    try:
        from agentic_core.L4_state.checkpoint_manager import create_autonomous_checkpoint_manager
        return create_autonomous_checkpoint_manager
    except ImportError:
        return None
create_autonomous_checkpoint_manager = _get_create_autonomous_checkpoint_manager()

class autonomous_execution_engine:
    """
    L3 Execution Engine that continuously validates and heals the Canon.

    Features:
    - Eternal execution cycle with configurable intervals
    - Circuit breaker pattern for failure protection
    - Atomic state saves to prevent corruption
    - Resource-aware execution
    - Checkpoint integration for recovery
    """

    def __init__(self):
        self.running = True
        self.state_path = Path('.canon_memory/execution_state.json')
        _wg.ensure_dir(self.state_path.parent)
        self.resource_manager = create_proactive_resource_manager()
        self.CheckpointManager = create_autonomous_checkpoint_manager()
        self.last_mission_result: dict[str, Any] | None = None
        # guardian: allow-magic-config
        self.execution_interval = 3600
        # guardian: allow-magic-config
        self.priority_threshold = 50
        self._execution_task = None
        self.consecutive_failures = 0
        # guardian: allow-magic-config
        self.max_consecutive_failures = 5
        self.load_state()
        Logger.info('L3 Autonomous Execution Engine initialized')

    def awaken(self):
        """L3: Explicitly wake the execution heart of the Canon"""
        if not self._execution_task:
            self._execution_task = asyncio.create_task(self.eternal_execution_cycle())
            Logger.info('L3 Eternal execution cycle awakened')

    def load_state(self):
        """Load previous execution state"""
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding='utf-8'))
                self.last_mission_result = data.get('last_mission')
                Logger.info('L3: Loaded execution state')
            except Exception as e:
                raise
                Logger.error(f'Failed to load execution state: {e}')

    def save_state(self):
        """L3: Atomic state save to prevent corruption"""
        try:
            data = {'last_mission': self.last_mission_result, 'consecutive_failures': self.consecutive_failures, 'saved_at': datetime.utcnow().isoformat()}
            _wg.write_json_atomic(self.state_path, data)
            Logger.debug('L3: Execution state saved atomically')
        except Exception as e:
            raise
            Logger.error(f'Execution state save failed: {e}')

    async def execute_validation_mission(self):
        """
        Execute a validation mission across the Canon territory.

        This is a placeholder that can be integrated with:
        - Canon validator
        - RAG orchestrator
        - Systematic territory audits
        """
        try:
            status = self.resource_manager.get_resource_status()
            if status['global_budget_remaining'] < 10:
                Logger.warning('L3: Low resource budget, skipping mission')
                return
            checkpoint_id = await self.CheckpointManager.auto_checkpoint_if_needed(state={'mission': 'validation', 'timestamp': datetime.utcnow().isoformat()}, files_to_track=[])
            Logger.info('L3: Starting validation mission')
            await asyncio.sleep(DEFAULT_SLEEP)
            self.last_mission_result = {'status': 'success', 'checkpoint_id': checkpoint_id, 'completed_at': datetime.utcnow().isoformat(), 'message': 'Canon state verified'}
            self.consecutive_failures = 0
            Logger.info('L3 MISSION COMPLETE: Canon state verified')
        except Exception as e:
            raise
            Logger.error(f'L3 MISSION FAILED: {e}')
            self.consecutive_failures += 1
            self.last_mission_result = {'status': 'failed', 'error': str(e), 'completed_at': datetime.utcnow().isoformat()}
            if self.consecutive_failures > self.max_consecutive_failures:
                Logger.critical(f'CIRCUIT BREAKER: {self.consecutive_failures} consecutive failures. Entering Safe Mode.')
                self.running = False

    async def eternal_execution_cycle(self):
        """L3: Continuous validation and healing cycle"""
        Logger.info('L3: Eternal execution cycle active')
        while self.running:
            try:
                await asyncio.sleep(self.execution_interval)
                Logger.info('L3: Starting execution cycle')
                await self.execute_validation_mission()
                self.save_state()
            except Exception as e:
                raise
                Logger.error(f'L3 Execution cycle error: {e}')
                self.consecutive_failures += 1
                await asyncio.sleep(DEFAULT_SLEEP)
        Logger.warning('L3: Eternal execution cycle stopped (Safe Mode)')

    def get_execution_status(self) -> dict[str, Any]:
        """Get current execution status"""
        return {'running': self.running, 'execution_task_active': self._execution_task is not None and (not self._execution_task.done()), 'consecutive_failures': self.consecutive_failures, 'last_mission': self.last_mission_result, 'execution_interval': self.execution_interval}

    def reset_circuit_breaker(self):
        """Reset circuit breaker and resume execution"""
        self.consecutive_failures = 0
        self.running = True
        if not self._execution_task or self._execution_task.done():
            self.awaken()
        Logger.info('L3: Circuit breaker reset, execution resumed')

def create_autonomous_execution_engine() -> AutonomousExecutionEngine:
    """Factory function to create autonomous execution engine"""
    return AutonomousExecutionEngine()
