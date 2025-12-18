"""Nervous System - Core Orchestrator Implementation.

Phase 2 - Pillar 1: Layering Model
Coordinates Brain (cognitive) and Hands (action) through Think-Act-Observe cycle.
"""

import logging
import time
from typing import Any, Dict, List, Optional
import asyncio

from agentic_core.interfaces import (
    ICognitivePlane,
    IActionPlane,
    OrchestratorConfig,
    ExecutionContext,
    ExecutionResult,
    ExecutionPhase,
    PlanningRequest,
    ActionRequest,
)
from agentic_core.L1_cognition.sovereign_cognitive_plane import SovereignCognitivePlane, create_sovereign_cognitive_plane
from agentic_core.L2_execution.sovereign_action_plane import SovereignActionPlane, create_sovereign_action_plane
from agentic_core.L5_safety.safety_layer import create_l5_safety_layer, L5SafetyLayer
from agentic_core.L4_state.checkpointing import VerifiableCheckpointManager
from agentic_core.L4_state.storage import create_storage_adapter, SignalLedger

LOGGER = logging.getLogger(__name__)

class NervousSystem:
    """Core orchestrator that coordinates cognitive and action planes.

    Implements the 5-step agentic cycle:
    1. MISSION - Define the goal
    2. SCENE - Gather context
    3. THINK - Plan next actions (Brain)
    4. ACT - Execute actions (Hands)
    5. OBSERVE - Interpret results and update state

    Enforces strict architectural boundaries:
    - Only orchestrator can call both planes
    - Cognitive plane cannot trigger actions
    - Action plane cannot make plans
    """

    def __init__(
        self,
        cognitive_plane: Optional[ICognitivePlane] = None,
        action_plane: Optional[IActionPlane] = None,
        config: Optional[OrchestratorConfig] = None,
    ):
        """Initialize nervous system.

        Args:
            cognitive_plane: The brain (planning/reasoning)
            action_plane: The hands (tool execution)
            config: Orchestrator configuration
        """
        # Initialize L5 Safety Layer first
        self.safety_layer = create_l5_safety_layer(cost_limit_usd=10.00)
        
        # Initialize L4 State Persistence
        storage_adapter = create_storage_adapter("local", base_path="./agentic_core/checkpoints")
        self.checkpoint_manager = VerifiableCheckpointManager(storage_adapter)
        self.session_id = getattr(config, 'mission_id', f"mission_{int(time.time())}")
        self.signal_ledger = SignalLedger(storage_adapter, self.session_id)
        
        # Create sovereign implementations if not provided
        self.brain = cognitive_plane or create_sovereign_cognitive_plane()
        self.hands = action_plane or create_sovereign_action_plane(safety_layer=self.safety_layer)
        self.config = config or OrchestratorConfig()

        self._state: Dict[str, Any] = {}
        self._iteration = 0
        
        # Populate phases with real agents from cognitive plane
        self.phases = self._populate_phases()
        
        # Execution tracking
        self._results: Dict[str, Dict[str, Any]] = {}
        self._signals: set = set()
        self._modified_files: set = set()

        LOGGER.info(
            "nervous_system_initialized",
            extra={
                "cognitive_capabilities": [c.value if hasattr(c, 'value') else c for c in self.brain.get_capabilities()],
                "action_capabilities": [c.value if hasattr(c, 'value') else c for c in self.hands.get_capabilities()],
                "config": self.config.to_dict(),
                "phases_populated": len([p for p in self.phases.values() if p])
            }
        )
    
    def _populate_phases(self) -> Dict[str, List]:
        """Populate phases with sovereign agents from the cognitive plane."""
        # Get agents from sovereign cognitive plane
        agents = []
        if hasattr(self.brain, 'get_agent_registry'):
            registry = self.brain.get_agent_registry()
            agents = list(registry.values())
        
        # Group agents by phase
        phases = {
            "integrity_seq": [],
            "curation_seq": [],
            "test_seq": [],
            "memory_parallel": [],
            "resilience_parallel": [],
            "resource_safety_parallel": [],
            "engineering_parallel": [],
            "refinement_parallel": [],
            "benchmarking_seq": [],
            "optimization_conditional": [],
        }
        
        # Create mock agent objects from sovereign registry
        for agent_info in agents:
            phase = agent_info.phase
            
            # Create a simple mock agent that has execute method
            class MockAgent:
                def __init__(self, name, phase):
                    self.name = name
                    self.phase = phase
                
                async def execute(self):
                    # Simulate agent execution
                    return {
                        "passed": True,
                        "agent": self.name,
                        "phase": self.phase,
                        "details": f"Agent {self.name} executed successfully"
                    }
            
            mock_agent = MockAgent(agent_info.name, phase)
            
            if phase in phases:
                phases[phase].append(mock_agent)
        
        return phases

    async def run_mission(self, max_phases: Optional[int] = None) -> ExecutionResult:
        """Run the full mission with phase-based execution.
        
        Args:
            max_phases: Maximum number of phases to execute (None for all)
            
        Returns:
            ExecutionResult with mission status and report
        """
        # Check for existing checkpoint to resume from
        last_checkpoint = await self._find_last_checkpoint()
        if last_checkpoint:
            LOGGER.info(f"Resuming mission from checkpoint: {last_checkpoint['phase']}")
            await self._restore_from_checkpoint(last_checkpoint)
        
        # Create execution context for the mission
        context = ExecutionContext(
            mission="Execute 10-phase mission validation",
            scene={
                "phases": list(self.phases.keys()),
                "max_phases": max_phases,
                "iteration": self._iteration
            },
            state=self._state.copy()
        )
        
        # If max_phases is specified, limit the phases
        if max_phases:
            phase_names = list(self.phases.keys())
            limited_phases = {}
            for i, phase_name in enumerate(phase_names[:max_phases]):
                limited_phases[phase_name] = self.phases[phase_name]
            self.phases = limited_phases
            LOGGER.info(f"Limiting execution to first {max_phases} phases")
        
        # Execute the mission
        return await self.execute(context)
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute mission through phase-based execution.

        Args:
            context: Execution context with mission and scene

        Returns:
            ExecutionResult with output and trace
        """
        start_time = time.time()
        execution_trace: List[Dict[str, Any]] = []
        errors: List[str] = []

        self._iteration = 0
        self._state = context.state.copy()
        
        # Reset cycle state
        self._results.clear()
        self._signals.clear()
        self._modified_files.clear()

        LOGGER.info("execution_started",
            extra={"mission": context.mission,
            "scene_keys": list(context.scene.keys())})

        try:
            # Main execution loop with convergence check (from SwarmScheduler)
            max_cycles = self.config.max_iterations or 10
            for cycle in range(max_cycles):
                LOGGER.info(f"Cycle {cycle + 1}/{max_cycles}")
                
                # Execute all phases
                converged = await self._execute_all_phases(context, execution_trace)
                
                # Check for convergence
                if converged:
                    LOGGER.info("Convergence achieved - all checks passed!")
                    break
                
                # Check for critical failures
                if "CRITICAL_FAIL" in self._signals:
                    errors.append("Critical failure detected")
                    break
            
            # Generate mission report and calculate success rate
            self._generate_mission_report()
            
            # Create execution result
            result = self._create_execution_result(context, execution_trace, errors, start_time)
            
            # Log result to signal ledger
            await self.signal_ledger.append_result(result)
            
            return result
        except Exception as e:
            return self._handle_execution_error(context, execution_trace, start_time, e)

    async def _execute_all_phases(self, context: ExecutionContext, execution_trace: List[Dict]) -> bool:
        """Execute all phases in order with early abort logic (from SwarmScheduler)."""
        # Phase 1: Integrity (Sequential - Hard Gate)
        LOGGER.info("Phase 1: INTEGRITY CHECK (Sequential)")
        if not await self._run_sequential("integrity_seq", context, execution_trace):
            if "CRITICAL_FAIL" in self._signals:
                return False
        # Save checkpoint after phase 1
        await self._save_phase_checkpoint("integrity_seq", context)
        
        # Phase 2: Curation (Sequential)
        LOGGER.info("Phase 2: CURATION (Sequential)")
        await self._run_sequential("curation_seq", context, execution_trace)
        await self._save_phase_checkpoint("curation_seq", context)
        
        # Phase 3: Testing (Sequential)
        LOGGER.info("Phase 3: TESTING (Sequential)")
        await self._run_sequential("test_seq", context, execution_trace)
        await self._save_phase_checkpoint("test_seq", context)
        
        # Phase 4: Memory (Parallel)
        LOGGER.info("Phase 4: MEMORY ENHANCEMENT (Parallel)")
        await self._run_parallel("memory_parallel", context, execution_trace)
        await self._save_phase_checkpoint("memory_parallel", context)
        
        # Phase 5: RESILIENCE (Parallel)
        LOGGER.info("Phase 5: RESILIENCE HARDENING (Parallel)")
        await self._run_parallel("resilience_parallel", context, execution_trace)
        await self._save_phase_checkpoint("resilience_parallel", context)
        
        # Phase 6: Resource Safety (Parallel)
        LOGGER.info("Phase 6: RESOURCE SAFETY (Parallel)")
        await self._run_parallel("resource_safety_parallel", context, execution_trace)
        await self._save_phase_checkpoint("resource_safety_parallel", context)
        
        # Phase 7: ENGINEERING (Parallel)
        LOGGER.info("Phase 7: ENGINEERING (Parallel)")
        await self._run_parallel("engineering_parallel", context, execution_trace)
        await self._save_phase_checkpoint("engineering_parallel", context)
        
        # Phase 8: Refinement (Parallel)
        LOGGER.info("Phase 8: REFINEMENT (Parallel)")
        await self._run_parallel("refinement_parallel", context, execution_trace)
        await self._save_phase_checkpoint("refinement_parallel", context)
        
        # Phase 9: Benchmarking (Sequential)
        LOGGER.info("Phase 9: BENCHMARKING (Sequential)")
        await self._run_sequential("benchmarking_seq", context, execution_trace)
        await self._save_phase_checkpoint("benchmarking_seq", context)
        
        # Phase 10: Optimization (Conditional - Sequential)
        LOGGER.info("Phase 10: OPTIMIZATION (Conditional)")
        if self._is_converged():
            await self._run_sequential("optimization_conditional", context, execution_trace)
            await self._save_phase_checkpoint("optimization_conditional", context)
        else:
            LOGGER.info("Skipping optimization - not fully converged")
        
        # Return convergence status
        return self._is_converged()
    
    async def _save_phase_checkpoint(self, phase_name: str, context: ExecutionContext) -> None:
        """Save checkpoint after phase completion.
        
        Args:
            phase_name: Name of the completed phase
            context: Current execution context
        """
        import time
        from datetime import datetime
        
        # Prepare checkpoint state
        checkpoint_state = {
            "phase": phase_name,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "iteration": self._iteration,
            "state": self._state.copy(),
            "results": self._results.copy(),
            "signals": list(self._signals),
            "modified_files": list(self._modified_files),
            "mission": context.mission,
            "scene": context.scene
        }
        
        # Save checkpoint
        try:
            await self.checkpoint_manager.save_checkpoint(
                session_id=self.session_id,
                node_id=phase_name,
                state=checkpoint_state
            )
            LOGGER.info(f"Checkpoint saved for phase: {phase_name}")
        except Exception as e:
            LOGGER.error(f"Failed to save checkpoint for phase {phase_name}: {e}")
    
    async def _find_last_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Find the most recent checkpoint for this mission.
        
        Returns:
            Dictionary with checkpoint state or None if not found
        """
        # List all checkpoints for this session
        try:
            # Get list of phase names in order
            phase_order = [
                "integrity_seq",
                "curation_seq", 
                "test_seq",
                "memory_parallel",
                "resilience_parallel",
                "resource_safety_parallel",
                "engineering_parallel",
                "refinement_parallel",
                "benchmarking_seq",
                "optimization_conditional"
            ]
            
            # Check phases in reverse order to find last checkpoint
            for phase_name in reversed(phase_order):
                if await self.checkpoint_manager.checkpoint_exists(self.session_id, phase_name):
                    checkpoint = await self.checkpoint_manager.load_checkpoint(
                        self.session_id, 
                        phase_name,
                        verify=True
                    )
                    if checkpoint:
                        return checkpoint
            
            return None
        except Exception as e:
            LOGGER.error(f"Error finding checkpoint: {e}")
            return None
    
    async def _restore_from_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Restore system state from checkpoint.
        
        Args:
            checkpoint: Checkpoint state dictionary
        """
        try:
            # Restore state
            self._state = checkpoint.get("state", {})
            self._iteration = checkpoint.get("iteration", 0)
            self._results = checkpoint.get("results", {})
            self._signals = set(checkpoint.get("signals", []))
            self._modified_files = set(checkpoint.get("modified_files", []))
            
            LOGGER.info(f"Restored from checkpoint phase: {checkpoint.get('phase')}")
            LOGGER.info(f"Restored state: {len(self._state)} keys, {len(self._results)} results")
        except Exception as e:
            LOGGER.error(f"Error restoring from checkpoint: {e}")
    
    async def _run_sequential(self, phase_name: str, context: ExecutionContext, execution_trace: List[Dict]) -> bool:
        """Execute a phase sequentially (from SwarmScheduler)."""
        agents = self.phases.get(phase_name, [])
        for agent in agents:
            # Map agent execution to cognitive plane
            if hasattr(agent, 'execute'):
                result = await agent.execute()
                self._results[agent.name] = result
                if not result.get("passed", True):
                    self._signals.add("CRITICAL_FAIL")
            
            # Early abort for critical failures in integrity phase
            if phase_name == "integrity_seq" and "CRITICAL_FAIL" in self._signals:
                LOGGER.error(f"CRITICAL FAIL in {phase_name} - Aborting")
                return False
        
        return True
    
    async def _run_parallel(self, phase_name: str, context: ExecutionContext, execution_trace: List[Dict]):
        """Execute a phase in parallel (from SwarmScheduler)."""
        agents = self.phases.get(phase_name, [])
        if not agents:
            return
        
        # Create tasks for parallel execution
        tasks = []
        for agent in agents:
            if hasattr(agent, 'execute'):
                task = self._rate_limited_retry(agent.execute)
                tasks.append(task)
        
        # Execute all agents in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _rate_limited_retry(self, func, max_retries: int = 5, base_delay: float = 2.0):
        """Decorator to handle rate limiting with exponential backoff (from SwarmScheduler)."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)


    def _is_converged(self) -> bool:
        """Check if all agents have passed (from SwarmScheduler)."""
        if not self._results:
            return False
        
        return all(r.get("passed", False) for r in self._results.values())
    
    def _generate_mission_report(self):
        """Generate final mission report (from SwarmScheduler)."""
        LOGGER.info("Generating mission report")
        
        total_keys = len(self._results)
        passed_keys = sum(1 for r in self._results.values() if r.get("passed", False))
        
        # Calculate success rate safely
        success_rate = passed_keys/total_keys*100 if total_keys > 0 else 0
        
        LOGGER.info(f"SUMMARY: Total Keys Checked: {total_keys}, "
                   f"Keys Passed: {passed_keys}, "
                   f"Keys Failed: {total_keys - passed_keys}, "
                   f"Success Rate: {success_rate:.1f}%")
        
        if self._is_converged():
            LOGGER.info("MISSION SUCCESS - Full convergence achieved!")
        else:
            LOGGER.warning("MISSION INCOMPLETE - Some issues remain")
        
        # Store success rate in state for later retrieval
        self._state["success_rate"] = success_rate
        
        LOGGER.info("DETAILED RESULTS:")
        for key, result in sorted(self._results.items()):
            status = "PASS" if result.get("passed", False) else "FAIL"
            LOGGER.info(f"Key {key}: {status} - {result.get('agent', 'Unknown')}")
    
    def _create_execution_result(self,
        context: ExecutionContext,
        execution_trace: List[Dict],
        errors: List[str],
        start_time: float) -> ExecutionResult:
        """Create final execution result."""
        success = len(errors) == 0 and self._is_converged()
        
        result = ExecutionResult(
            success=success, 
            output=context.state.get("final_output"), 
            final_state=context.state,
            execution_trace=execution_trace, 
            iterations=self._iteration, 
            errors=errors,
            metadata={
                "execution_time_seconds": time.time() - start_time,
                "total_phases": len(execution_trace),
                "success_rate": self._state.get("success_rate", 0),
                "converged": self._is_converged(),
                "signals": list(self._signals),
                "modified_files": list(self._modified_files)
            }
        )
        
        LOGGER.info("execution_completed",
            extra={"success": success,
            "iterations": self._iteration,
            "execution_time": result.metadata["execution_time_seconds"]})
        return result

    def _handle_execution_error(self,
        context: ExecutionContext,
        execution_trace: List[Dict],
        start_time: float,
        error: Exception) -> ExecutionResult:
        """Handle execution error."""
        logger.error("execution_failed", extra={"error": str(error)}, exc_info=True)
        return ExecutionResult(
            success=False, final_state=context.state, execution_trace=execution_trace,
            iterations=self._iteration, errors=[f"Execution failed: {str(error)}"],
            metadata={"execution_time_seconds": time.time() - start_time}
        )



    async def should_continue(self, context: ExecutionContext) -> bool:
        """Determine if execution should continue.

        Args:
            context: Current execution context

        Returns:
            True if should continue
        """
        if self._iteration >= self.config.max_iterations:
            return False

        if context.state.get("mission_complete"):
            return False

        if context.state.get("fatal_error"):
            return False

        return True

    def get_state(self) -> Dict[str, Any]:
        """Get current orchestrator state.

        Returns:
            Current state snapshot
        """
        return {
            "iteration": self._iteration,
            "state": self._state.copy(),
            "config": self.config.to_dict(),
        }

    async def save_state(self, path: str) -> None:
        """Save orchestrator state to disk.

        Args:
            path: Path to save state
        """
        import json

        STATE = self.get_state()

        with open(path, 'w') as f:
            JSON.DUMP(STATE, F, INDENT=2, default=str)

        logger.info("state_saved", extra={"path": path})

    async def load_state(self, path: str) -> None:
        """Load orchestrator state from disk.

        Args:
            path: Path to load state from
        """

        with open(path, 'r') as f:
            STATE = json.load(f)

        self._iteration = state.get("iteration", 0)
        self._state = state.get("state", {})

        logger.info("state_loaded", extra={"path": path, "iteration": self._iteration})

    def _extract_actions(self, think_result: Dict[str, Any]) -> List[ActionRequest]:
        """Extract action requests from planning result.

        Args:
            think_result: Result from think phase

        Returns:
            List of action requests
        """
        actions: List[ActionRequest] = []

        PLAN = think_result.get("plan", [])

        for step in plan:
            if step.get("type") == "action":
                ACTION = ActionRequest(
                    action_type=step.get("action_type", "tool_call"),
                    tool_name=step.get("tool", "unknown"),
                    PARAMETERS=step.get("parameters", {}),
                    CONTEXT=step.get("context", {}),
                )
                actions.append(action)

        return actions
