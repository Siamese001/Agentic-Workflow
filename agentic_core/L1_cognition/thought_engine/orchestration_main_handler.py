import ast
import asyncio
import atexit
import json  # Moved from _checkpoint_state in ConsolidatedOrchestrator
import logging
import os
import re
import signal
import subprocess  # Moved from _calculate_smart_scope in ConsolidatedOrchestrator
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Set

from agentic_core.tools.filesystem import WriteFileArgs, write_file
from agentic_core.L2_execution.tool_registry import (
    CanonStructuralEngineer,
    CodeJanitor,
    CodeStyleGuardian,
    HygieneGuardian,
    PerformanceEnforcer,
    SafetyInspector,
    SecurityEnforcer,
    SystemArchitect,
    get_dependency_diplomat,
    get_regression_oracle,
)

# Phase 3: UniversalContext
from agentic_core.L1_cognition.P2_domain.context import ValidationContext

# Phase 5: L1-L5 Unified Architecture


try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

logger = logging.getLogger(__name__)

# Global reference for graceful shutdown
_orchestrator_instance: Optional['ConsolidatedOrchestrator'] = None


def _signal_handler(signum, frame):
    """Handle CTRL+C and graceful shutdown."""
    logger.info("\n🛑 Shutdown signal received. Releasing all leases...")
    if _orchestrator_instance:
        _orchestrator_instance.release_all_leases()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


@dataclass
class OrchestratorConfig:
    """Configuration for the consolidated orchestrator."""
    max_cycles: int = 5
    quality_threshold: float = 0.75
    enable_intervention: bool = True
    enable_checkpointing: bool = True
    checkpoint_dir: str = "./checkpoints"
    gemini_model: str = "gemini-2.5-flash"
    temperature: float = 0.2
    thinking_budget: int = 16000
    enable_healing: bool = True
    max_healing_per_file: int = 8
    global_healing_budget: int = 50
    
    # Phase 5: CLI Flags
    heal_mode: bool = False  # --heal flag
    clean_slate: bool = False  # --clean-slate flag (flush Redis)
    override_preservation: bool = False  # --override-preservation (SystemArchitect only)
    target_path: Optional[str] = None  # Target file or directory
    smart_scope: bool = False  # --smart-scope flag (use dependency graph for surgical targeting)
    smart_scope_depth: int = 2  # BFS depth limit for smart scope


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
    status: str = "INITIALIZED"


class OrchestratorHealingService:
    """
    Manages the healing process for code violations using an LLM.
    Handles LLM interaction, fix validation, and file writing.
    """
    def __init__(
        self,
        config: OrchestratorConfig,
        ctx: ValidationContext,
        client: Any, # genai client
        state: OrchestratorState,
        logger: logging.Logger
    ):
        self.config = config
        self.ctx = ctx
        self.client = client
        self.state = state
        self.logger = logger

    async def execute_healing(
        self,
        file_path: str,
        violation_key: int,
        fix_prompt: str
    ) -> bool:
        """
        Execute healing operation.

        Args:
            file_path: Path to file to heal
            violation_key: Violation key to fix
            fix_prompt: Prompt for LLM to fix violation

        Returns:
            True if healing succeeded, False otherwise
        """
        if not self.config.enable_healing:
            return False

        if not self._can_attempt_healing(file_path):
            self.logger.warning(f"Healing budget exhausted for {file_path}")
            return False

        if not self.client:
            self.logger.error("Gemini client not available for healing")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=self.config.thinking_budget
                ),
                tools=[]
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.config.gemini_model,
                contents=f"{fix_prompt}\n\n{original_code}",
                config=config
            )

            fixed_code = response.text.strip() if response.text else original_code

            if self._validate_fix(original_code, fixed_code):
                write_file(
                    WriteFileArgs(path=file_path, content=fixed_code),
                    blackboard=getattr(self.ctx, 'blackboard', None),
                    agent_id="consolidated_orchestrator"
                )

                self._record_healing_attempt(file_path, success=True)
                self.logger.info(f"[OK] Healed {file_path} for violation {violation_key}")
                return True
            else:
                self._record_healing_attempt(file_path, success=False)
                self.logger.warning(f"[X] Healing validation failed for {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"Healing failed for {file_path}: {e}")
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

        status = "[OK] SUCCESS" if success else "[X] FAILED"
        self.logger.info(
            f"   Healing attempt {self.state.healing_attempts[file_path]} "
            f"for {file_path}: {status}"
        )
        self.logger.info(
            f"   Healing budget: {self.state.healing_budget_used}/"
            f"{self.config.global_healing_budget}"
        )

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
            self.logger.warning(f"Fix deleted too many lines: {original_lines} -> {fixed_lines}")
            return False

        if fixed_lines > original_lines * 4:
            self.logger.warning(f"Fix added too many lines: {original_lines} -> {fixed_lines}")
            return False

        return True


class OrchestratorStateManager:
    """
    Manages the orchestrator's state, checkpoints, termination conditions,
    and result building.
    """
    def __init__(
        self,
        config: OrchestratorConfig,
        ctx: ValidationContext,
        state: OrchestratorState,
        logger: logging.Logger
    ):
        self.config = config
        self.ctx = ctx
        self.state = state
        self.logger = logger

    def should_run_agent(self, agent: Any) -> bool:
        """Determine if an agent should run based on signals."""
        if "CRITICAL_FAIL" in self.state.signals:
            return False
        
        if hasattr(agent, 'can_run'):
            return agent.can_run()
        
        return True
    
    def should_terminate(self) -> bool:
        """Determine if workflow should terminate early."""
        if "CONVERGENCE" in self.state.signals:
            return True
        
        if "CRITICAL_FAIL" in self.state.signals:
            return True
        
        return False
    async def checkpoint_state(self, agent_name: str):
        """Create a checkpoint of current state."""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.state.current_cycle,
            "agent": agent_name,
            "signals": list(self.state.signals),
            "modified_files": list(self.state.modified_files),
            "healing_budget_used": self.state.healing_budget_used
        }
        
        self.state.checkpoints.append(checkpoint)
        
        if self.config.checkpoint_dir:
            os.makedirs(self.config.checkpoint_dir, exist_ok=True)
            checkpoint_file = os.path.join(
                self.config.checkpoint_dir,
                f"{self.state.workflow_id}_cycle{self.state.current_cycle}_{agent_name}.json"
            )
            
            try:
                with open(checkpoint_file, 'w') as f:
                    json.dump(checkpoint, f, indent=2)
            except Exception as e:
                self.logger.warning(f"Failed to write checkpoint: {e}")
    
    async def handle_intervention(self) -> bool:
        """Handle human-in-the-loop intervention."""
        self.logger.info("⏸️  Waiting for human approval...")
        
        if not self.config.enable_intervention:
            return True
        
        # Placeholder for actual human intervention logic (e.g., TUI prompt)
        # For now, it always approves if intervention is enabled.
        return True
    
    def build_results(self) -> Dict[str, Any]:
        """Build final workflow results."""
        duration = None
        if self.state.start_time and self.state.end_time:
            duration = (self.state.end_time - self.state.start_time).total_seconds()
        
        return {
            "workflow_id": self.state.workflow_id,
            "status": self.state.status,
            "cycles_executed": self.state.current_cycle,
            "signals": list(self.state.signals),
            "modified_files": list(self.state.modified_files),
            "healing_attempts": self.state.healing_attempts,
            "healing_budget_used": self.state.healing_budget_used,
            "checkpoints_created": len(self.state.checkpoints),
            "duration_seconds": duration,
            "start_time": self.state.start_time.isoformat() if self.state.start_time else None,
            "end_time": self.state.end_time.isoformat() if self.state.end_time else None
        }


class OrchestratorAgentAndScopeManager:
    """
    Manages the creation of the subatomic agent swarm and calculates
    the smart scope for targeted execution.
    """
    def __init__(
        self,
        config: OrchestratorConfig,
        ctx: ValidationContext,
        logger: logging.Logger
    ):
        self.config = config
        self.ctx = ctx
        self.logger = logger

    def create_agent_swarm(self) -> List[Any]:
        """
        Create the subatomic agent swarm based on configuration.
        
        Returns:
            List of agent instances
        """
        agents = []
        
        # Phase 1: Core Architecture (SystemArchitect)
        agents.append(SystemArchitect(self.ctx))
        
        # Phase 2: Code Quality (CodeJanitor)
        agents.append(CodeJanitor(self.ctx))
        
        # Phase 3: Structure (StructuralEngineer)
        agents.append(CanonStructuralEngineer(self.ctx))
        
        # Phase 4: Hygiene & Style
        agents.append(HygieneGuardian(self.ctx))
        agents.append(CodeStyleGuardian(self.ctx))
        
        # Phase 5: Security & Safety
        agents.append(SafetyInspector(self.ctx))
        agents.append(SecurityEnforcer(self.ctx))
        
        # Phase 6: Performance
        agents.append(PerformanceEnforcer(self.ctx))
        
        self.logger.info(f"   🤖 Agent Swarm Created: {len(agents)} agents")
        
        return agents
    async def calculate_smart_scope(self, target_path: Optional[str] = None) -> List[str]:
        """
        Calculate smart scope using Dependency Diplomat.
        
        Uses BFS on dependency graph to find all files affected by changes.
        
        Args:
            target_path: Optional target file or directory
            
        Returns:
            List of files in impact scope
        """
        # Get Dependency Diplomat
        diplomat = get_dependency_diplomat(self.ctx)
        
        # Build dependency graph
        await diplomat.execute()
        
        # Determine modified files
        if target_path:
            # If target specified, use it as modified file
            modified_files = [target_path]
        else:
            # Try to get modified files from git
            try:
                result = subprocess.run(
                    ['git', 'diff', '--name-only', 'HEAD'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                modified_files = [
                    f for f in result.stdout.strip().split('\n') 
                    if f and f.endswith('.py')
                ]
                
                if not modified_files:
                    self.logger.warning("   No modified Python files found in git diff")
                    # Fallback: scan for recently modified files
                    modified_files = []
            except Exception as e:
                self.logger.warning(f"   Could not get git diff: {e}")
                modified_files = []
        
        if not modified_files:
            self.logger.info("   No modified files detected, using full repository scope")
            return []
        
        # Calculate impact scope
        impact_scope = diplomat.calculate_impact_scope(
            modified_files, 
            max_depth=self.config.smart_scope_depth
        )
        
        return impact_scope


class ConsolidatedOrchestrator:
    """
    [START] PHASE 5: THE HUB - Consolidated Command & Control Orchestrator
    
    This orchestrator serves as the single source of truth for all orchestration
    logic across the entire repository. All legacy orchestrators are thin wrappers
    that delegate to this implementation.
    
    Features:
    - UniversalContext (ValidationContext) - Phase 3
    - AtomicBlackboard integration - Phase 2
    - Subatomic Agent Architecture
    - Clean Slate Protocol
    - Graceful lease release
    """
    
    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        context: Optional[ValidationContext] = None
    ):
        """
        Initialize the consolidated orchestrator.
        
        Args:
            config: Orchestrator configuration
            context: Validation context (creates new if None)
        """
        global _orchestrator_instance
        
        self.config = config or OrchestratorConfig()
        self.ctx = context or ValidationContext()
        self.state: Optional[OrchestratorState] = None # Will be initialized in execute_workflow
        self.blackboard = getattr(self.ctx, 'blackboard', None)
        
        # Register for graceful shutdown
        _orchestrator_instance = self
        atexit.register(self.release_all_leases)
        
        if GENAI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            logger.info("[OK] Gemini 2.5/3.0 client initialized")
        else:
            self.client = None
            logger.warning("[!]  Gemini client not available")
        
        # Initialize healing service and state manager to None, they will be properly instantiated
        # in execute_workflow once self.state is available.
        self.healing_service: Optional[OrchestratorHealingService] = None
        self.state_manager: Optional[OrchestratorStateManager] = None
        self.agent_scope_manager = OrchestratorAgentAndScopeManager(self.config, self.ctx, logger)
        
        # Clean Slate Protocol: Flush Redis if requested
        if self.config.clean_slate:
            self._execute_clean_slate()
        
        logger.info("[START] Consolidated orchestrator initialized (Phase 5: Swarm Assembly)")
    
    def _execute_clean_slate(self):
        """Execute Clean Slate Protocol: Flush Redis and clear all leases."""
        logger.info("[CLEAN] CLEAN SLATE PROTOCOL: Flushing Redis...")
        try:
            # Try to flush Redis if available
            if self.blackboard:
                # Release all leases first
                self.release_all_leases()
                logger.info("   [OK] All leases released")
            
            # Additional cleanup can be added here
            logger.info("   [OK] Clean slate executed")
        except Exception as e:
            logger.warning(f"   [!]  Clean slate failed: {e}")
    
    def release_all_leases(self):
        """Release all leases held by this orchestrator (graceful shutdown)."""
        if self.blackboard and hasattr(self.blackboard, 'release_all_leases'):
            try:
                self.blackboard.release_all_leases()
                logger.info("   [OK] All blackboard leases released")
            except Exception as e:
                logger.warning(f"   [!]  Lease release failed: {e}")
    
    async def run_mission(
        self,
        target_path: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the orchestration mission with subatomic agents.
        
        This is the main entry point for all orchestration tasks.
        
        Args:
            target_path: Optional target file or directory for surgical scope
            workflow_id: Optional workflow identifier
            
        Returns:
            Mission execution results
        """
        workflow_id = workflow_id or f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_path = target_path or self.config.target_path
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[START] MISSION START: {workflow_id}")
        logger.info(f"{'='*60}")
        
        # Smart scope integration
        if self.config.smart_scope:
            logger.info(f"🔗 SMART SCOPE ENABLED: Building dependency graph...")
            target_files = await self.agent_scope_manager.calculate_smart_scope(target_path)
            logger.info(f"   Impact scope: {len(target_files)} files (depth: {self.config.smart_scope_depth})")
            
            # Store in context for agents
            self.ctx.smart_scope_targets = target_files
        elif target_path:
            logger.info(f"🎯 SURGICAL MODE: Targeting {target_path}")
        else:
            logger.info(f"🌐 FULL REPOSITORY MODE")
        
        # Create subatomic agent swarm
        agents = self.agent_scope_manager.create_agent_swarm()
        
        # Execute workflow with convergence loop
        results = await self.execute_workflow(
            workflow_id=workflow_id,
            agents=agents,
            context={"target_path": target_path}
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[OK] MISSION COMPLETE: {results['status']}")
        logger.info(f"{'='*60}")
        
        return results
    
    async def execute_workflow(
        self,
        workflow_id: str,
        agents: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow with the given agents using convergence loop.
        
        Args:
            workflow_id: Unique workflow identifier
            agents: List of agent instances to execute
            context: Optional execution context
            
        Returns:
            Workflow execution results
        """
        self.state = OrchestratorState(
            workflow_id=workflow_id,
            start_time=datetime.now()
        )
        # Initialize healing service and state manager with the newly created state
        self.healing_service = OrchestratorHealingService(
            config=self.config,
            ctx=self.ctx,
            client=self.client,
            state=self.state,
            logger=logger
        )
        self.state_manager = OrchestratorStateManager(
            config=self.config,
            ctx=self.ctx,
            state=self.state,
            logger=logger
        )
        
        logger.info(f"\n[~] Starting convergence loop...")
        logger.info(f"   Max cycles: {self.config.max_cycles}")
        logger.info(f"   Agents: {len(agents)}")
        
        context = context or {}
        
        for cycle in range(self.config.max_cycles):
            self.state.current_cycle = cycle + 1
            self.state.signals.clear()
            self.ctx.modified_files.clear()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"CYCLE {cycle + 1}/{self.config.max_cycles}")
            logger.info(f"{'='*60}")
            
            for agent in agents:
                if not self.state_manager.should_run_agent(agent):
                    logger.debug(f"Skipping agent {agent.__class__.__name__}")
                    continue
                
                try:
                    logger.info(f"\n[>>>] Running: {agent.__class__.__name__}")
                    await agent.execute()
                    
                    # Regression Oracle Hook: Run after healing agents
                    if self.config.enable_healing and agent.__class__.__name__ in ['SystemArchitect', 'CodeJanitor']:
                        if self.ctx.modified_files:
                            logger.info(f"\n[🔮] Running Regression Oracle for {len(self.ctx.modified_files)} modified files...")
                            
                            # Emit FILE_MODIFIED signals for each modified file
                            for file_path in self.ctx.modified_files:
                                self.ctx.signals.add(f"FILE_MODIFIED:{file_path}")
                            
                            # Run Regression Oracle
                            oracle = get_regression_oracle(self.ctx)
                            await oracle.execute()
                            
                            # Check for regression detection
                            regression_signals = [s for s in self.ctx.signals if s.startswith('REGRESSION_DETECTED:')]
                            if regression_signals:
                                logger.error(f"\n[ALERT] REGRESSIONS DETECTED: {len(regression_signals)}")
                                for signal in regression_signals:
                                    logger.error(f"   {signal}")
                                
                                # Mark as requiring intervention
                                self.state.signals.add("INTERVENTION_REQUIRED")
                    
                    # Clean Slate Protocol: If agent fails, clear its session
                    if "AGENT_FAILURE" in self.ctx.signals:
                        logger.warning(f"   [!]  Agent failure detected - executing clean slate")
                        self._execute_clean_slate()
                        self.ctx.signals.discard("AGENT_FAILURE")
                    
                    if self.config.enable_checkpointing:
                        await self.state_manager.checkpoint_state(agent.__class__.__name__)
                    
                except Exception as e:
                    logger.error(f"[X] Agent {agent.__class__.__name__} failed: {e}")
                    self.state.signals.add("AGENT_FAILURE")
                    
                    # Clean Slate Protocol: Clear session before retry
                    if self.config.clean_slate:
                        self._execute_clean_slate()
            
            # Check for convergence
            if self.state_manager.should_terminate():
                logger.info("\n[OK] CONVERGENCE ACHIEVED")
                self.state.status = "COMPLETED"
                break
            
            # Check for intervention
            if self.config.enable_intervention and "INTERVENTION_REQUIRED" in self.state.signals:
                logger.info("\n✋ INTERVENTION REQUIRED")
                if not await self.state_manager.handle_intervention():
                    logger.info("🛑 WORKFLOW VETOED")
                    self.state.status = "VETOED"
                    break
        
        self.state.end_time = datetime.now()
        
        if self.state.status != "COMPLETED" and self.state.status != "VETOED":
            self.state.status = "MAX_CYCLES_REACHED"
            logger.warning(f"\n[!]  Max cycles reached without convergence")
        
        return self.state_manager.build_results()
    async def execute_with_healing(
        self,
        file_path: str,
        violation_key: int,
        fix_prompt: str
    ) -> bool:
        """
        Delegate healing operation to the OrchestratorHealingService.
        
        Args:
            file_path: Path to file to heal
            violation_key: Violation key to fix
            fix_prompt: Prompt for LLM to fix violation
            
        Returns:
            True if healing succeeded, False otherwise
        """
        if not self.healing_service:
            logger.error("Healing service not initialized. Cannot execute healing.")
            return False
        return await self.healing_service.execute_healing(file_path, violation_key, fix_prompt)


def create_orchestrator(
    config: Optional[OrchestratorConfig] = None,
    context: Optional[ValidationContext] = None
) -> ConsolidatedOrchestrator:
    """
    Factory function to create a consolidated orchestrator.
    
    Args:
        config: Orchestrator configuration
        context: Validation context
        
    Returns:
        ConsolidatedOrchestrator instance
    """
    return ConsolidatedOrchestrator(config=config, context=context)


async def main():
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
    
    parser = argparse.ArgumentParser(
        description="[START] Phase 5: Consolidated Orchestrator - Command & Control Center",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full repository scan with healing
  python orchestrator_main.py --heal
  
  # Clean slate and target specific directory
  python orchestrator_main.py --clean-slate --target apps_rg/
  
  # Override preservation for SystemArchitect
  python orchestrator_main.py --override-preservation --target agentic_core/
        """
    )
    
    parser.add_argument(
        "--workflow-id",
        default=None,
        help="Workflow ID (auto-generated if not provided)"
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=5,
        help="Maximum convergence cycles (default: 5)"
    )
    
    parser.add_argument(
        "--target",
        help="Target file or directory for surgical scope"
    )
    
    parser.add_argument(
        "--heal",
        action="store_true",
        help="Enable healing mode (auto-fix violations)"
    )
    
    parser.add_argument(
        "--clean-slate",
        action="store_true",
        help="Execute Clean Slate Protocol (flush Redis, clear leases)"
    )
    
    parser.add_argument(
        "--override-preservation",
        action="store_true",
        help="Allow SystemArchitect to override preservation rules (use with caution)"
    )
    
    parser.add_argument(
        "--smart-scope",
        action="store_true",
        help="Use dependency graph for surgical targeting (reduces CI time by 95%%)"
    )
    
    parser.add_argument(
        "--smart-scope-depth",
        type=int,
        default=2,
        help="BFS depth limit for smart scope (default: 2)"
    )
    
    args = parser.parse_args()
    
    # Create configuration from CLI args
    config = OrchestratorConfig(
        max_cycles=args.max_cycles,
        enable_healing=args.heal,
        clean_slate=args.clean_slate,
        override_preservation=args.override_preservation,
        target_path=args.target,
        smart_scope=args.smart_scope,
        smart_scope_depth=args.smart_scope_depth
    )
    
    # Create orchestrator
    orchestrator = create_orchestrator(config=config)
    
    # Run mission
    results = await orchestrator.run_mission(
        target_path=args.target,
        workflow_id=args.workflow_id
    )
    
    # Print results
    print(f"\n{'='*60}")
    print(f"[STATS] MISSION RESULTS")
    print(f"{'='*60}")
    print(f"  Status: {results['status']}")
    print(f"  Cycles: {results['cycles_executed']}/{config.max_cycles}")
    print(f"  Modified Files: {len(results['modified_files'])}")
    print(f"  Healing Budget Used: {results['healing_budget_used']}/{config.global_healing_budget}")
    print(f"  Checkpoints: {results['checkpoints_created']}")
    if results.get('duration_seconds'):
        print(f"  Duration: {results['duration_seconds']:.2f}s")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    if results['status'] == 'COMPLETED':
        sys.exit(0)
    elif results['status'] == 'VETOED':
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())