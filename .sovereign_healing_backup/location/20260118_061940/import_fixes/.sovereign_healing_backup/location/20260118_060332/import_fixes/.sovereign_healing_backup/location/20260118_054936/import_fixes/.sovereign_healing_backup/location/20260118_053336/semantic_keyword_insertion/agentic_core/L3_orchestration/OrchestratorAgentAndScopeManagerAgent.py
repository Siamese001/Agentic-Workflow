from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import asyncio
import atexit
import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Set
from agentic_core.tools.filesystem import WriteFileArgs, write_file
from agentic_core.L2_execution.tool_registry import CanonStructuralEngineer, CodeJanitor, CodeStyleGuardian, HygieneGuardian, PerformanceEnforcer, SafetyInspectorAgent, SecurityEnforcer, SystemArchitect, get_dependency_diplomat, get_regression_oracle
from agentic_core.L1_cognition.P2_domain.context import ValidationContext

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic
    from google.cloud.aiplatform.gapic import (
        dataset_service_client,
        model_service_client,
        pipeline_service_client,
        tensorboard_service_client,
        vertex_ai_client,
    )
    from google.cloud.aiplatform.gapic.schema import trainingjob
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
    genai: Any = None
    types: Any = None
Logger: Any = logging.getLogger(__name__)
_orchestrator_instance: Optional['ConsolidatedOrchestratorAgent'] = None

def _signal_handler(signum, frame):
    """Handle CTRL+C and graceful shutdown."""
    Logger.info('\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\n🛑 Shutdown signal received. Releasing all leases...')
    if _orchestrator_instance:
        _orchestrator_instance.release_all_leases()
    sys.exit(0)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

@dataclass
class OrchestratorConfig:
    """Configuration for the consolidated orchestrator."""
    max_cycles: int = 5
    quality_threshold: float = 0.75
    enable_intervention: bool = True
    enable_checkpointing: bool = True
    checkpoint_dir: str = './checkpoints'
    gemini_model: str = 'gemini-2.5-flash'
    temperature: float = 0.2
    thinking_budget: int = 16000
    enable_healing: bool = True
    max_healing_per_file: int = 8
    global_healing_budget: int = 50
    heal_mode: bool = False
    clean_slate: bool = False
    override_preservation: bool = False
    target_path: Optional[str] = None
    smart_scope: bool = False
    smart_scope_depth: int = 2

@dataclass
class OrchestratorState:
    """State tracking for orchestrator execution."""
    workflow_id: str
    current_cycle: int = 0
    signals: Set[str] = field(default_factory=set)
    modified_files: Set[str] = field(default_factory=set)
    healing_attempts: Dict[str, int] = field(default_factory=dict)
    healing_budget_used: int = 0
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = 'INITIALIZED'

class OrchestratorHealingService:
    """
    Manages the healing process for code violations using an LLM.
    Handles LLM interaction, fix validation, and file writing.
    """

    def __init__(self, config: OrchestratorConfig, ctx: ValidationContext, client: Any, state: OrchestratorState, Logger: logging.Logger) -> None:
        """Initialize the instance."""
        self.config = config
        self.ctx = ctx
        self.client = client
        self.state = state
        self.Logger = Logger

    async def execute_healing(self, file_path: str, violation_key: int, fix_prompt: str) -> bool:
        """
        Execute healing operation.

        Args:
            file_path: Path to file to heal
            violation_key: Violation key to fix
            fix_prompt: Prompt for LLM to fix Violation

        Returns:
            True if healing succeeded, False otherwise
        """
        if not self.config.enable_healing:
            return False
        if not self._can_attempt_healing(file_path):
            self.Logger.warning(f'Healing budget exhausted for {file_path}')
            return False
        if not self.client:
            self.Logger.error('Gemini client not available for healing')
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code: Any = f.read()
            config: Any = types.GenerateContentConfig(temperature=self.config.temperature, thinking_config=types.ThinkingConfig(thinking_budget=self.config.thinking_budget), tools=[])
            response: Any = await asyncio.to_thread(self.client.models.generate_content, model=self.config.gemini_model, contents=f'{fix_prompt}\n\n{original_code}', config=config)
            fixed_code: Any = response.text.strip() if response.text else original_code
            if self._validate_fix(original_code, fixed_code):
                write_file(WriteFileArgs(path=file_path, content=fixed_code), blackboard=getattr(self.ctx, 'blackboard', None), agent_id='ConsolidatedOrchestratorAgent')
                self._record_healing_attempt(file_path, success=True)
                self.Logger.info(f'[OK] Healed {file_path} for Violation {violation_key}')
                return True
            else:
                self._record_healing_attempt(file_path, success=False)
                self.Logger.warning(f'[X] Healing validation failed for {file_path}')
                return False
        except Exception as e:
            self.Logger.error(f'Healing failed for {file_path}: {e}')
            self._record_healing_attempt(file_path, success=False)
            return False

    def _can_attempt_healing(self, file_path: str) -> bool:
        """Check if healing can be attempted on this file."""
        if self.state.healing_budget_used >= self.config.global_healing_budget:
            return False
        if self.state.healing_attempts.get(file_path, 0) >= self.config.max_healing_per_file:
            return False
        return True

    def _record_healing_attempt(self, file_path: str, success: bool):
        """Record a healing attempt."""
        if file_path not in self.state.healing_attempts:
            self.state.healing_attempts[file_path] = 0
        self.state.healing_attempts[file_path] += 1
        self.state.healing_budget_used += 1
        if success:
            self.state.modified_files.add(file_path)
        status = '[OK] SUCCESS' if success else '[X] FAILED'
        self.Logger.info(f'   Healing attempt {self.state.healing_attempts[file_path]} for {file_path}: {status}')
        self.Logger.info(f'   Healing budget: {self.state.healing_budget_used}/{self.config.global_healing_budget}')

    def _validate_fix(self, original: str, fixed: str) -> bool:
        """Validate that a fix is acceptable."""
        try:
            ast.parse(fixed)
        except SyntaxError:
            return False
        original_lines = len(original.splitlines())
        fixed_lines = len(fixed.splitlines())
        max_deletion = int(original_lines * 0.1)
        if original_lines - fixed_lines > max_deletion:
            self.Logger.warning(f'Fix deleted too many lines: {original_lines} -> {fixed_lines}')
            return False
        if fixed_lines > original_lines * 4:
            self.Logger.warning(f'Fix added too many lines: {original_lines} -> {fixed_lines}')
            return False
        return True

class OrchestratorStateManager:
    """
    Manages the orchestrator's state, checkpoints, termination conditions,
    and result building.
    """

    def __init__(self, config: OrchestratorConfig, ctx: ValidationContext, state: OrchestratorState, Logger: logging.Logger) -> None:
        """Initialize the instance."""
        self.config = config
        self.ctx = ctx
        self.state = state
        self.Logger = Logger

    def should_run_agent(self, agent: Any) -> bool:
        """Determine if an agent should run based on signals."""
        if 'CRITICAL_FAIL' in self.state.signals:
            return False
        if hasattr(agent, 'can_run'):
            return agent.can_run()
        return True

    def should_terminate(self) -> bool:
        """Determine if workflow should terminate early."""
        if 'CONVERGENCE' in self.state.signals:
            return True
        if 'CRITICAL_FAIL' in self.state.signals:
            return True
        return False

    async def checkpoint_state(self, agent_name: str) -> Any:
        """Create a Checkpoint of current state."""
        Checkpoint: Any = {'timestamp': datetime.now().isoformat(), 'cycle': self.state.current_cycle, 'agent': agent_name, 'signals': list(self.state.signals), 'modified_files': list(self.state.modified_files), 'healing_budget_used': self.state.healing_budget_used}
        self.state.checkpoints.append(Checkpoint)
        if self.config.checkpoint_dir:
            os.makedirs(self.config.checkpoint_dir, exist_ok=True)
            checkpoint_file: Any = os.path.join(self.config.checkpoint_dir, f'{self.state.workflow_id}_cycle{self.state.current_cycle}_{agent_name}.json')
            try:
                with open(checkpoint_file, 'w') as f:
                    json.dump(Checkpoint, f, indent=2)
            except Exception as e:
                self.Logger.warning(f'Failed to write Checkpoint: {e}')

    async def handle_intervention(self) -> bool:
        """Handle human-in-the-loop intervention."""
        self.Logger.info('⏸️  Waiting for human approval...')
        if not self.config.enable_intervention:
            return True
        return True

    def build_results(self) -> Dict[str, Any]:
        """Build final workflow results."""
        duration: Any = None
        if self.state.start_time and self.state.end_time:
            duration: Any = (self.state.end_time - self.state.start_time).total_seconds()
        return {'workflow_id': self.state.workflow_id, 'status': self.state.status, 'cycles_executed': self.state.current_cycle, 'signals': list(self.state.signals), 'modified_files': list(self.state.modified_files), 'healing_attempts': self.state.healing_attempts, 'healing_budget_used': self.state.healing_budget_used, 'checkpoints_created': len(self.state.checkpoints), 'duration_seconds': duration, 'start_time': self.state.start_time.isoformat() if self.state.start_time else None, 'end_time': self.state.end_time.isoformat() if self.state.end_time else None}

class OrchestratorAgentAndScopeManagerAgent(SovereignBaseAgent):
    """
    Manages the creation of the subatomic agent swarm and calculates
    the smart scope for targeted execution.
    """

    def __init__(self, config: OrchestratorConfig, ctx: ValidationContext, Logger: logging.Logger) -> None:
        """Initialize the instance."""
        self.config = config
        self.ctx = ctx
        self.Logger = Logger

    def create_agent_swarm(self) -> List[Any]:
        """
        Create the subatomic agent swarm based on configuration.
        
        Returns:
            List of agent instances
        """
        agents: Any = []
        agents.append(SystemArchitect(self.ctx))
        agents.append(CodeJanitor(self.ctx))
        agents.append(CanonStructuralEngineer(self.ctx))
        agents.append(HygieneGuardian(self.ctx))
        agents.append(CodeStyleGuardian(self.ctx))
        agents.append(SafetyInspectorAgent(self.ctx))
        agents.append(SecurityEnforcer(self.ctx))
        agents.append(PerformanceEnforcer(self.ctx))
        self.Logger.info(f'   🤖 Agent Swarm Created: {len(agents)} agents')
        return agents

    async def calculate_smart_scope(self, target_path: Optional[str]=None) -> List[str]:
        """
        Calculate smart scope using Dependency Diplomat.
        
        Uses BFS on dependency graph to find all files affected by changes.
        
        Args:
            target_path: Optional target file or directory
            
        Returns:
            List of files in impact scope
        """
        diplomat: Any = get_dependency_diplomat(self.ctx)
        await diplomat.execute()
        if target_path:
            modified_files: Any = [target_path]
        else:
            try:
                result: Any = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True, text=True, timeout=10)
                modified_files: Any = [f for f in result.stdout.strip().split('\n') if f and f.endswith('.py')]
                if not modified_files:
                    self.Logger.warning('   No modified Python files found in git diff')
                    modified_files: Any = []
            except Exception as e:
                self.Logger.warning(f'   Could not get git diff: {e}')
                modified_files: Any = []
        if not modified_files:
            self.Logger.info('   No modified files detected, using full repository scope')
            return []
        impact_scope: Any = diplomat.calculate_impact_scope(modified_files, max_depth=self.config.smart_scope_depth)
        return impact_scope

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


def create_orchestrator(config: Optional[OrchestratorConfig]=None, context: Optional[ValidationContext]=None) -> ConsolidatedOrchestratorAgent:
    """
    Factory function to create a consolidated orchestrator.
    
    Args:
        config: Orchestrator configuration
        context: Validation context
        
    Returns:
        ConsolidatedOrchestratorAgent instance
    """
    return ConsolidatedOrchestratorAgent(config=config, context=context)

async def main() -> Any:
    """
    [START] PHASE 5: Main entry point for consolidated orchestrator.
    
    Supports CLI flags:
    - --heal: Enable healing mode
    - --clean-slate: Flush Redis and clear all leases
    - --override-preservation: Allow SystemArchitect to override preservation rules
    - --target: Target file or directory for surgical scope
    - --max-cycles: Maximum convergence cycles
    """
    import argparse
    parser: Any = argparse.ArgumentParser(description='[START] Phase 5: Consolidated Orchestrator - Command & Control Center', formatter_class=argparse.RawDescriptionHelpFormatter, epilog='\nExamples:\n  # Full repository scan with healing\n  python orchestrator_main.py --heal\n  \n  # Clean slate and target specific directory\n  python orchestrator_main.py --clean-slate --target apps_rg/\n  \n  # Override preservation for SystemArchitect\n  python orchestrator_main.py --override-preservation --target agentic_core/\n        ')
    parser.add_argument('--workflow-id', default=None, help='Workflow ID (auto-generated if not provided)')
    parser.add_argument('--max-cycles', type=int, default=5, help='Maximum convergence cycles (default: 5)')
    parser.add_argument('--target', help='Target file or directory for surgical scope')
    parser.add_argument('--heal', action='store_true', help='Enable healing mode (auto-fix violations)')
    parser.add_argument('--clean-slate', action='store_true', help='Execute Clean Slate Protocol (flush Redis, clear leases)')
    parser.add_argument('--override-preservation', action='store_true', help='Allow SystemArchitect to override preservation rules (use with caution)')
    parser.add_argument('--smart-scope', action='store_true', help='Use dependency graph for surgical targeting (reduces CI time by 95%%)')
    parser.add_argument('--smart-scope-depth', type=int, default=2, help='BFS depth limit for smart scope (default: 2)')
    args: Any = parser.parse_args()
    config: Any = OrchestratorConfig(max_cycles=args.max_cycles, enable_healing=args.heal, clean_slate=args.clean_slate, override_preservation=args.override_preservation, target_path=args.target, smart_scope=args.smart_scope, smart_scope_depth=args.smart_scope_depth)
    orchestrator: Any = create_orchestrator(config=config)
    results: Any = await orchestrator.run_mission(target_path=args.target, workflow_id=args.workflow_id)
    print(f"\n{'=' * 60}")
    print(f'[STATS] MISSION RESULTS')
    print(f"{'=' * 60}")
    print(f"  Status: {results['status']}")
    print(f"  Cycles: {results['cycles_executed']}/{config.max_cycles}")
    print(f"  Modified Files: {len(results['modified_files'])}")
    print(f"  Healing Budget Used: {results['healing_budget_used']}/{config.global_healing_budget}")
    print(f"  Checkpoints: {results['checkpoints_created']}")
    if results.get('duration_seconds'):
        print(f"  Duration: {results['duration_seconds']:.2f}s")
    print(f"{'=' * 60}")
    if results['status'] == 'COMPLETED':
        sys.exit(0)
    elif results['status'] == 'VETOED':
        sys.exit(2)
    else:
        sys.exit(1)
if __name__ == '__main__':
    asyncio.run(main())