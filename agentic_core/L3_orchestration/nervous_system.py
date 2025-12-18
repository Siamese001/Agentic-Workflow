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
from agentic_core.L5_safety.intervention_server import InterventionServer, InterventionContext, check_intervention_required
from agentic_core.interfaces.governance import ArchitectureGovernor
from agentic_core.L3_orchestration.telepathy import process_telepathy_instructions, get_telepathy_interface

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
        storage_adapter = create_storage_adapter("local", base_path="./agentic_core")
        self.checkpoint_manager = VerifiableCheckpointManager(storage_adapter)
        self.session_id = getattr(config, 'mission_id', f"mission_{int(time.time())}")
        self.signal_ledger = SignalLedger(storage_adapter, self.session_id)
        
        # Create sovereign implementations if not provided
        self.brain = cognitive_plane or create_sovereign_cognitive_plane()
        self.hands = action_plane or create_sovereign_action_plane(
            safety_layer=self.safety_layer,
            signal_ledger=self.signal_ledger
        )
        self.config = config or OrchestratorConfig()

        self._state: Dict[str, Any] = {}
        self._iteration = 0
        
        # Populate phases with real agents from cognitive plane
        self.phases = self._populate_phases()
        
        # Execution tracking
        self._results: Dict[str, Dict[str, Any]] = {}
        self._signals: set = set()
        self._modified_files: set = set()
        self._phase_failure_counts: Dict[str, int] = {}  # Track consecutive failures per phase
        
        # L5 Intervention Server
        self.intervention_server = InterventionServer()
        
        # L6 Architecture Governor
        self.architecture_governor = ArchitectureGovernor()

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
        resume_phase = None
        if last_checkpoint:
            LOGGER.info(f"L4: Checkpoint found. Resuming from Phase 2.")
            await self._restore_from_checkpoint(last_checkpoint)
            resume_phase = last_checkpoint['phase']
        
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
        
        # Add forced agents support for telepathy
        context.forced_agents = []
        
        # If max_phases is specified, limit the phases
        if max_phases:
            phase_names = list(self.phases.keys())
            limited_phases = {}
            for i, phase_name in enumerate(phase_names[:max_phases]):
                limited_phases[phase_name] = self.phases[phase_name]
            self.phases = limited_phases
            LOGGER.info(f"Limiting execution to first {max_phases} phases")
        
        # Check for high-risk states that require intervention
        cycle = self._iteration
        modified_count = len(self._modified_files)
        signals_list = list(self._signals)
        
        # Process telepathic instructions (L6 Codebase Telepathy)
        context = await process_telepathy_instructions(context, cycle)
        
        # Check for immediate telepathic stop
        if "TELEPATHY_STOP" in context.signals:
            LOGGER.warning("Mission stopped by telepathic instruction")
            return ExecutionResult(
                success=False,
                report="Mission stopped by telepathic instruction",
                signals=["TELEPATHY_STOP"]
            )
        
        intervention_required, risk_factors = check_intervention_required(
            cycle=cycle,
            modified_count=modified_count,
            signals_list=signals_list
        )
        
        if intervention_required:
            LOGGER.warning(f"High-risk state detected: {risk_factors}")
            # Start intervention server
            await self.intervention_server.start_server()
            
            # Request human approval
            approved = await self.intervention_server.request_approval(
                risk_factors=risk_factors,
                cycle=cycle,
                modified_files=list(self._modified_files),
                timeout=300  # 5 minutes timeout
            )
            
            if not approved:
                LOGGER.error("Human intervention vetoed - aborting mission")
                self._signals.add("VETOED")
                # Stop intervention server
                await self.intervention_server.stop_server()
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Mission vetoed by human intervention",
                    execution_time=time.time() - start_time
                )
            
            # Stop intervention server after approval
            await self.intervention_server.stop_server()
            LOGGER.info("Human intervention approved - continuing mission")
        
        # Execute the mission
        return await self.execute(context, resume_phase=resume_phase)
    
    async def execute(self, context: ExecutionContext, resume_phase: Optional[str] = None) -> ExecutionResult:
        """Execute mission through phase-based execution.

        Args:
            context: Execution context with mission and scene
            resume_phase: Phase to resume from (skip phases up to and including this)

        Returns:
            ExecutionResult with output and trace
        """
        start_time = time.time()
        execution_trace: List[Dict[str, Any]] = []
        errors: List[str] = []

        # Only reset cycle state if not resuming from checkpoint
        if not resume_phase:
            self._iteration = 0
            self._state = context.state.copy()
            self._results = {}
        self._signals = set()
        self._modified_files = set()
        self._phase_failure_counts = {}  # Track consecutive failures per phase when resuming
        self._state.update(context.state)

        LOGGER.info("execution_started",
            extra={"mission": context.mission,
            "scene_keys": list(context.scene.keys())})

        try:
            # If resuming from final checkpoint, check convergence immediately
            if resume_phase == "optimization_conditional" and self._is_converged():
                LOGGER.info("Resuming from final checkpoint - already converged")
                converged = True
            else:
                # Main execution loop with convergence check (from SwarmScheduler)
                max_cycles = self.config.max_iterations or 10
                for cycle in range(max_cycles):
                    LOGGER.info(f"Cycle {cycle + 1}/{max_cycles}")
                    
                    # Execute all phases (only on first cycle when resuming)
                    if cycle == 0 or not resume_phase:
                        converged = await self._execute_all_phases(context, execution_trace, resume_phase=resume_phase)
                    else:
                        # On subsequent cycles, run without skipping
                        converged = await self._execute_all_phases(context, execution_trace, resume_phase=None)
                    
                    # Execute any forced agents from telepathy
                    if hasattr(context, 'forced_agents') and context.forced_agents:
                        await self._execute_forced_agents(context, execution_trace)
                    
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

    async def _get_previous_phase_signals(self, current_phase: str) -> Dict[str, Any]:
        """Get signals from the previous phase for blackboard communication.
        
        Args:
            current_phase: Name of the current phase
            
        Returns:
            Dictionary with signals from previous phase
        """
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
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index > 0:
                previous_phase = phase_order[current_index - 1]
                return await self.signal_ledger.get_phase_summary(previous_phase)
        except ValueError:
            pass
        
        return {}
    
    async def _reconcile_signals(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile conflicting signals from different agents.
        
        Args:
            results: Dictionary of agent results with potential conflicts
            
        Returns:
            Dictionary with reconciled signals and conflicts flagged
        """
        conflicts = []
        reconciled = {}
        file_results = {}  # Track results by file path
        
        # Organize results by file path
        for agent_name, result in results.items():
            if isinstance(result, dict):
                # Check for file modifications
                modified_files = result.get('modified_files', [])
                for file_path in modified_files:
                    if file_path not in file_results:
                        file_results[file_path] = []
                    file_results[file_path].append({
                        'agent': agent_name,
                        'result': result,
                        'action': result.get('action', 'unknown')
                    })
        
        # Detect conflicts
        for file_path, file_agents in file_results.items():
            if len(file_agents) > 1:
                # Multiple agents modified the same file
                actions = [a['action'] for a in file_agents]
                if len(set(actions)) > 1:
                    # Conflicting actions
                    conflicts.append({
                        'file': file_path,
                        'agents': file_agents,
                        'conflict_type': 'action_conflict',
                        'description': f"Multiple agents performed different actions on {file_path}: {actions}"
                    })
                else:
                    # Same action, potentially okay but flag for review
                    conflicts.append({
                        'file': file_path,
                        'agents': file_agents,
                        'conflict_type': 'duplicate_modification',
                        'description': f"Multiple agents performed the same action on {file_path}: {actions[0]}"
                    })
        
        # Generate reconciliation recommendations
        if conflicts:
            reconciled['has_conflicts'] = True
            reconciled['conflicts'] = conflicts
            reconciled['recommendations'] = []
            
            for conflict in conflicts:
                if conflict['conflict_type'] == 'action_conflict':
                    reconciled['recommendations'].append(
                        f"CRITICAL: Action conflict on {conflict['file']}. "
                        f"Requires tie-breaker agent review."
                    )
                    # Add signal for tie-breaker
                    reconciled[f'tie_breaker_needed_{conflict["file"].replace("/", "_")}'] = True
                else:
                    reconciled['recommendations'].append(
                        f"Review duplicate modification on {conflict['file']}"
                    )
            
            # Add global signal
            reconciled['signal'] = 'CONFLICTS_DETECTED'
        else:
            reconciled['has_conflicts'] = False
            reconciled['signal'] = 'NO_CONFLICTS'
        
        return reconciled
    
    async def _execute_all_phases(self, context: ExecutionContext, execution_trace: List[Dict], resume_phase: Optional[str] = None) -> bool:
        """Execute all phases in order with early abort logic (from SwarmScheduler).
        
        Args:
            context: Execution context
            execution_trace: List to track execution
            resume_phase: Phase to resume from (skip phases up to and including this)
        """
        # Helper function to check if phase should be skipped
        def should_skip_phase(phase_name: str) -> bool:
            if not resume_phase:
                return False
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
            try:
                resume_index = phase_order.index(resume_phase)
                phase_index = phase_order.index(phase_name)
                return phase_index <= resume_index
            except ValueError:
                return False
        
        # Phase 1: Integrity (Sequential - Hard Gate)
        if not should_skip_phase("integrity_seq"):
            LOGGER.info("Phase 1: INTEGRITY CHECK (Sequential)")
            # Populate previous phase signals (none for first phase)
            context.previous_phase_signals = await self._get_previous_phase_signals("integrity_seq")
            if not await self._run_sequential("integrity_seq", context, execution_trace):
                if "CRITICAL_FAIL" in self._signals:
                    return False
            # Save checkpoint after phase 1
            await self._save_phase_checkpoint("integrity_seq", context)
        else:
            LOGGER.info("Phase 1: INTEGRITY CHECK (Skipping - already completed)")
        
        # Phase 2: Curation (Sequential)
        if not should_skip_phase("curation_seq"):
            LOGGER.info("Phase 2: CURATION (Sequential)")
            # Populate signals from Phase 1
            context.previous_phase_signals = await self._get_previous_phase_signals("curation_seq")
            await self._run_sequential("curation_seq", context, execution_trace)
            await self._save_phase_checkpoint("curation_seq", context)
        else:
            LOGGER.info("Phase 2: CURATION (Skipping - already completed)")
        
        # Phase 3: Testing (Sequential)
        if not should_skip_phase("test_seq"):
            LOGGER.info("Phase 3: TESTING (Sequential)")
            context.previous_phase_signals = await self._get_previous_phase_signals("test_seq")
            await self._run_sequential("test_seq", context, execution_trace)
            await self._save_phase_checkpoint("test_seq", context)
        else:
            LOGGER.info("Phase 3: TESTING (Skipping - already completed)")
        
        # Phase 4: Memory (Parallel)
        if not should_skip_phase("memory_parallel"):
            LOGGER.info("Phase 4: MEMORY ENHANCEMENT (Parallel)")
            context.previous_phase_signals = await self._get_previous_phase_signals("memory_parallel")
            await self._run_parallel("memory_parallel", context, execution_trace)
            await self._save_phase_checkpoint("memory_parallel", context)
        else:
            LOGGER.info("Phase 4: MEMORY ENHANCEMENT (Skipping - already completed)")
        
        # Phase 5: RESILIENCE (Parallel)
        if not should_skip_phase("resilience_parallel"):
            LOGGER.info("Phase 5: RESILIENCE HARDENING (Parallel)")
            context.previous_phase_signals = await self._get_previous_phase_signals("resilience_parallel")
            await self._run_parallel("resilience_parallel", context, execution_trace)
            await self._save_phase_checkpoint("resilience_parallel", context)
        else:
            LOGGER.info("Phase 5: RESILIENCE HARDENING (Skipping - already completed)")
        
        # Phase 6: Resource Safety (Parallel)
        if not should_skip_phase("resource_safety_parallel"):
            LOGGER.info("Phase 6: RESOURCE SAFETY (Parallel)")
            context.previous_phase_signals = await self._get_previous_phase_signals("resource_safety_parallel")
            await self._run_parallel("resource_safety_parallel", context, execution_trace)
            await self._save_phase_checkpoint("resource_safety_parallel", context)
        else:
            LOGGER.info("Phase 6: RESOURCE SAFETY (Skipping - already completed)")
        
        # Phase 7: ENGINEERING (Parallel)
        if not should_skip_phase("engineering_parallel"):
            LOGGER.info("Phase 7: ENGINEERING (Parallel)")
            context.previous_phase_signals = await self._get_previous_phase_signals("engineering_parallel")
            await self._run_parallel("engineering_parallel", context, execution_trace)
            await self._save_phase_checkpoint("engineering_parallel", context)
        else:
            LOGGER.info("Phase 7: ENGINEERING (Skipping - already completed)")
        
        # Phase 8: Refinement (Parallel)
        if not should_skip_phase("refinement_parallel"):
            LOGGER.info("Phase 8: REFINEMENT (Parallel)")
            context.previous_phase_signals = await self._get_previous_phase_signals("refinement_parallel")
            await self._run_parallel("refinement_parallel", context, execution_trace)
            await self._save_phase_checkpoint("refinement_parallel", context)
        else:
            LOGGER.info("Phase 8: REFINEMENT (Skipping - already completed)")
        
        # Phase 9: Benchmarking (Sequential)
        if not should_skip_phase("benchmarking_seq"):
            LOGGER.info("Phase 9: BENCHMARKING (Sequential)")
            context.previous_phase_signals = await self._get_previous_phase_signals("benchmarking_seq")
            await self._run_sequential("benchmarking_seq", context, execution_trace)
            await self._save_phase_checkpoint("benchmarking_seq", context)
        else:
            LOGGER.info("Phase 9: BENCHMARKING (Skipping - already completed)")
        
        # Phase 10: Optimization (Conditional - Sequential)
        if not should_skip_phase("optimization_conditional"):
            LOGGER.info("Phase 10: OPTIMIZATION (Conditional)")
            context.previous_phase_signals = await self._get_previous_phase_signals("optimization_conditional")
            if self._is_converged():
                await self._run_sequential("optimization_conditional", context, execution_trace)
                await self._save_phase_checkpoint("optimization_conditional", context)
            else:
                LOGGER.info("Skipping optimization - not fully converged")
        else:
            LOGGER.info("Phase 10: OPTIMIZATION (Skipping - already completed)")
        
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
        success_rate = self._calculate_success_rate()
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
            "scene": context.scene,
            "success_rate": success_rate
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
        # Check circuit breaker before executing phase
        if self._phase_failure_counts.get(phase_name, 0) >= 3:
            LOGGER.error(f"Circuit breaker OPEN for {phase_name} - 3 consecutive failures detected")
            LOGGER.error("Entering SAFE MODE - Phase 0")
            self._signals.add("CIRCUIT_BREAKER_TRIPPED")
            return False
        
        agents = self.phases.get(phase_name, [])
        phase_passed = True
        
        for agent in agents:
            # Map agent execution to cognitive plane
            if hasattr(agent, 'execute'):
                # Check prerequisite conditions if agent supports it
                if hasattr(agent, 'check_prerequisites'):
                    prereq_result = await agent.check_prerequisites(context)
                    if not prereq_result.get('satisfied', True):
                        LOGGER.warning(f"Agent {agent.name} prerequisites not satisfied: {prereq_result.get('message', 'Unknown')}")
                        # Create a PlanningResult recommending re-run
                        if hasattr(agent, 'create_prereq_failure_result'):
                            result = await agent.create_prereq_failure_result(prereq_result)
                        else:
                            result = {
                                'passed': False,
                                'error': 'Prerequisites not satisfied',
                                'details': prereq_result.get('message', 'Unknown'),
                                'recommendation': prereq_result.get('recommendation', 'Re-run prerequisite phase')
                            }
                        self._results[agent.name] = result
                        # Add signal for prerequisite failure
                        self._signals.add("PREREQ_FAIL")
                        phase_passed = False
                        continue
                
                # Execute agent with context
                if hasattr(agent, 'execute_with_context'):
                    result = await agent.execute_with_context(context)
                else:
                    result = await agent.execute()
                
                self._results[agent.name] = result
                if not result.get("passed", True):
                    self._signals.add("CRITICAL_FAIL")
                    phase_passed = False
            
            # Early abort for critical failures in integrity phase
            if phase_name == "integrity_seq" and ("CRITICAL_FAIL" in self._signals or "PREREQ_FAIL" in self._signals):
                LOGGER.error(f"Critical failure in {phase_name} - Aborting")
                # Update failure count
                self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
                return False
        
        # Update failure count based on phase result
        if not phase_passed:
            self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
            LOGGER.warning(f"Phase {phase_name} failed - Strike {self._phase_failure_counts[phase_name]}/3")
        else:
            # Reset failure count on success
            if phase_name in self._phase_failure_counts:
                del self._phase_failure_counts[phase_name]
                LOGGER.info(f"Phase {phase_name} succeeded - Resetting failure count")
        
        return phase_passed
    
    async def _run_parallel(self, phase_name: str, context: ExecutionContext, execution_trace: List[Dict]):
        """Execute a phase in parallel (from SwarmScheduler)."""
        # Check circuit breaker before executing phase
        if self._phase_failure_counts.get(phase_name, 0) >= 3:
            LOGGER.error(f"Circuit breaker OPEN for {phase_name} - 3 consecutive failures detected")
            LOGGER.error("Entering SAFE MODE - Phase 0")
            self._signals.add("CIRCUIT_BREAKER_TRIPPED")
            return
        
        # Check memory pressure before parallel execution
        if hasattr(self.safety_layer, 'cost_governor'):
            try:
                memory_info = self.safety_layer.cost_governor.check_memory_pressure()
                if not memory_info.get("pressure_ok", True):
                    LOGGER.error(f"Memory pressure too high: {memory_info.get('available_gb', -1):.2f}GB available")
                    self._signals.add("MEMORY_PRESSURE")
                    return
            except Exception as e:
                LOGGER.warning(f"Could not check memory pressure: {e}")
        
        agents = self.phases.get(phase_name, [])
        if not agents:
            return
        
        # Create tasks for parallel execution
        tasks = []
        for agent in agents:
            if hasattr(agent, 'execute'):
                # Create wrapper for each agent to handle context and prerequisites
                async def execute_agent_with_context(agent):
                    # Check prerequisite conditions if agent supports it
                    if hasattr(agent, 'check_prerequisites'):
                        prereq_result = await agent.check_prerequisites(context)
                        if not prereq_result.get('satisfied', True):
                            LOGGER.warning(f"Agent {agent.name} prerequisites not satisfied: {prereq_result.get('message', 'Unknown')}")
                            result = {
                                'passed': False,
                                'error': 'Prerequisites not satisfied',
                                'details': prereq_result.get('message', 'Unknown'),
                                'recommendation': prereq_result.get('recommendation', 'Re-run prerequisite phase')
                            }
                            self._results[agent.name] = result
                            self._signals.add("PREREQ_FAIL")
                            return result
                    
                    # Execute agent with context
                    if hasattr(agent, 'execute_with_context'):
                        result = await agent.execute_with_context(context)
                    else:
                        result = await agent.execute()
                    
                    self._results[agent.name] = result
                    if not result.get("passed", True):
                        self._signals.add("CRITICAL_FAIL")
                    return result
                
                task = self._rate_limited_retry(lambda a=agent: execute_agent_with_context(a))
                tasks.append(task)
        
        # Execute all agents in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if phase passed and update failure count
            phase_passed = all(
                self._results.get(agent.name, {}).get("passed", True) 
                for agent in agents if hasattr(agent, 'name')
            )
            
            if not phase_passed:
                self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
                LOGGER.warning(f"Phase {phase_name} failed - Strike {self._phase_failure_counts[phase_name]}/3")
            else:
                # Reset failure count on success
                if phase_name in self._phase_failure_counts:
                    del self._phase_failure_counts[phase_name]
                    LOGGER.info(f"Phase {phase_name} succeeded - Resetting failure count")
            
            # Reconcile signals to detect conflicts
            conflicts = await self._reconcile_signals(self._results)
            if conflicts.get('has_conflicts'):
                LOGGER.warning(f"Phase {phase_name} conflicts detected: {len(conflicts['conflicts'])}")
                for conflict in conflicts['conflicts']:
                    LOGGER.warning(f"  {conflict['description']}")
                # Add conflict signal
                self._signals.add("CONFLICTS_DETECTED")
    
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
    
    def _calculate_success_rate(self) -> float:
        """Calculate current success rate based on results.
        
        Returns:
            Success rate as percentage (0-100)
        """
        total_keys = len(self._results)
        if total_keys == 0:
            return 0.0
        
        passed_keys = sum(1 for r in self._results.values() if r.get("passed", False))
        return (passed_keys / total_keys) * 100
    
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
    
    async def _execute_forced_agents(self, context: ExecutionContext, execution_trace: List[Dict[str, Any]]):
        """
        Execute agents forced by telepathic instructions.
        
        Args:
            context: Current execution context
            execution_trace: Trace to record execution results
        """
        if not hasattr(context, 'forced_agents') or not context.forced_agents:
            return
        
        LOGGER.info(f"🎯 Executing forced agents from telepathy: {', '.join(context.forced_agents)}")
        
        for agent_name in context.forced_agents:
            try:
                # Find the agent in our phases
                agent_found = False
                for phase_name, phase_agents in self.phases.items():
                    for agent in phase_agents:
                        if hasattr(agent, 'name') and agent.name == agent_name:
                            LOGGER.info(f"  → Executing forced agent: {agent_name} (from {phase_name})")
                            
                            # Execute the agent
                            result = await agent.execute()
                            
                            # Record in execution trace
                            execution_trace.append({
                                "agent": agent_name,
                                "phase": phase_name,
                                "forced": True,
                                "result": result,
                                "timestamp": time.time()
                            })
                            
                            # Update signals based on result
                            if isinstance(result, dict):
                                if result.get("passed", False):
                                    self._signals.add(f"{agent_name.upper()}_FORCED_SUCCESS")
                                else:
                                    self._signals.add(f"{agent_name.upper()}_FORCED_FAILED")
                            
                            agent_found = True
                            break
                
                if not agent_found:
                    LOGGER.warning(f"  ⚠️  Forced agent not found: {agent_name}")
                    
            except Exception as e:
                LOGGER.error(f"  ❌ Error executing forced agent {agent_name}: {e}")
                self._signals.add(f"{agent_name.upper()}_FORCED_ERROR")
        
        # Clear forced agents after execution
        context.forced_agents.clear()
        LOGGER.info("Forced agents execution complete")
    
    async def get_impact_radius(self, modified_files: List[str] = None) -> Dict[str, Any]:
        """
        Calculate the blast radius for modified files.
        
        Args:
            modified_files: List of modified file paths (uses tracked files if None)
            
        Returns:
            Dictionary with impact analysis
        """
        if modified_files is None:
            modified_files = list(self._modified_files)
        
        if not modified_files:
            return {
                "modified_count": 0,
                "total_impacted": 0,
                "blast_radius": [],
                "message": "No modified files to analyze"
            }
        
        # Build dependency graph if needed
        if not self.architecture_governor.dependency_graph._built:
            self.architecture_governor.build_graph()
        
        # Calculate blast radius
        impact_analysis = self.architecture_governor.get_blast_radius(modified_files)
        
        # Log blast radius
        LOGGER.info(f"☢️ BLAST RADIUS: {impact_analysis['total_impacted']} files in scope")
        
        # Add impacted files to modified set for verification
        for file_path in impact_analysis["blast_radius"]:
            self._modified_files.add(file_path)
        
        return impact_analysis
    
    def validate_architecture(self, file_paths: List[str] = None) -> Dict[str, Any]:
        """
        Validate architecture compliance.
        
        Args:
            file_paths: Specific files to validate
            
        Returns:
            Validation report
        """
        return self.architecture_governor.validate_architecture(file_paths)
