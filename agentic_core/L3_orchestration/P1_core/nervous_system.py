from typing import Any, Optional, Protocol, Dict, List, TYPE_CHECKING
import re

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentic_core.L1_cognition.P1_interfaces import (
    ActionRequest,
    ExecutionContext,
    ExecutionResult,
    IActionPlane,
    ICognitivePlane,
    OrchestratorConfig,
)
from agentic_core.L1_cognition.P1_interfaces.governance import ArchitectureGovernor
if TYPE_CHECKING:
    from agentic_core.L1_cognition.sovereign_cognitive_plane import (
        create_sovereign_cognitive_plane,
    )
    from agentic_core.L2_execution.sovereign_action_plane import (
        create_sovereign_action_plane,
    )
    from agentic_core.telepathy import (
        process_telepathy_instructions,
        InterventionServer,
        check_intervention_required,
    )

LOGGER = logging.getLogger(__name__)

class NervousSystemCheckpointing:
    """Handles checkpointing operations for the NervousSystem."""

    def __init__(
        self,
        checkpoint_manager: VerifiableCheckpointManager,
        signal_ledger: SignalLedger,
        session_id: str,
        logger: logging.Logger,
    ):
        self.checkpoint_manager = checkpoint_manager
        self.signal_ledger = signal_ledger
        self.session_id = session_id
        self.logger = logger

    async def save_phase_checkpoint(
        self,
        phase_name: str,
        current_state: Dict[str, Any],
        current_results: Dict[str, Any],
        current_signals: set,
        current_modified_files: set,
        current_iteration: int,
        mission: str,
        scene: Dict[str, Any],
        success_rate: float,
    ) -> None:
        """Save checkpoint after phase completion.

        Args:
            phase_name: Name of the completed phase
            current_state: Current orchestrator state
            current_results: Current agent results
            current_signals: Current signals
            current_modified_files: Current modified files
            current_iteration: Current iteration number
            mission: Mission description
            scene: Current scene context
            success_rate: Current mission success rate
        """
        # Prepare checkpoint state
        checkpoint_state = {
            "phase": phase_name,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "iteration": current_iteration,
            "state": current_state.copy(),
            "results": current_results.copy(),
            "signals": list(current_signals),
            "modified_files": list(current_modified_files),
            "mission": mission,
            "scene": scene,
            "success_rate": success_rate
        }

        # Save checkpoint
        try:
            await self.checkpoint_manager.save_checkpoint(
                session_id=self.session_id,
                node_id=phase_name,
                state=checkpoint_state
            )
            self.logger.info(f"Checkpoint saved for phase: {phase_name}")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint for phase {phase_name}: {e}")

    async def find_last_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Find the most recent checkpoint for this mission.

        Returns:
            Dictionary with checkpoint state or None if not found
        """
        # List all checkpoints for this session
        try:
            # Get list of phase names in order
            phase_order = [
                "integrity_seq", "curation_seq", "test_seq", "memory_parallel",
                "resilience_parallel", "resource_safety_parallel", "engineering_parallel",
                "refinement_parallel", "benchmarking_seq", "optimization_conditional"
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
            self.logger.error(f"Error finding checkpoint: {e}")
            return None

    def restore_from_checkpoint(self, checkpoint: Dict[str, Any]) -> (
        Dict[str, Any], Dict[str, Any], set, set, int, str
    ):
        """Restore system state from checkpoint.

        Args:
            checkpoint: Checkpoint state dictionary

        Returns:
            Tuple of (state, results, signals, modified_files, iteration, resume_phase)
        """
        try:
            # Restore state
            state = checkpoint.get("state", {})
            iteration = checkpoint.get("iteration", 0)
            results = checkpoint.get("results", {})
            signals = set(checkpoint.get("signals", []))
            modified_files = set(checkpoint.get("modified_files", []))
            resume_phase = checkpoint.get("phase")

            self.logger.info(f"Restored from checkpoint phase: {resume_phase}")
            self.logger.info(f"Restored state: {len(state)} keys, {len(results)} results")
            return state, results, signals, modified_files, iteration, resume_phase
        except Exception as e:
            self.logger.error(f"Error restoring from checkpoint: {e}")
            return {}, {}, set(), set(), 0, ""

class NervousSystemResultReporting:
    """Handles mission result generation and reporting."""

    def __init__(self, config: OrchestratorConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def _is_converged(self, results: Dict[str, Any]) -> bool:
        """Check if all agents have passed (from SwarmScheduler)."""
        if not results:
            return False
        return all(r.get("passed", False) for r in results.values())

    def _generate_mission_report(self, results: Dict[str, Any], state: Dict[str, Any]):
        """Generate final mission report (from SwarmScheduler)."""
        self.logger.info("Generating mission report")

        total_keys = len(results)
        passed_keys = sum(1 for r in results.values() if r.get("passed", False))

        # Calculate success rate safely
        success_rate = passed_keys / total_keys * 100 if total_keys > 0 else 0

        self.logger.info(f"SUMMARY: Total Keys Checked: {total_keys}, "
                           f"Keys Passed: {passed_keys}, "
                           f"Keys Failed: {total_keys - passed_keys}, "
                           f"Success Rate: {success_rate:.1f}%")

        if self._is_converged(results):
            self.logger.info("MISSION SUCCESS - Full convergence achieved!")
        else:
            self.logger.warning("MISSION INCOMPLETE - Some issues remain")

        # Store success rate in state for later retrieval
        state["success_rate"] = success_rate

        self.logger.info("DETAILED RESULTS:")
        for key, result in sorted(results.items()):
            status = "PASS" if result.get("passed", False) else "FAIL"
            self.logger.info(f"Key {key}: {status} - {result.get('agent', 'Unknown')}")

    def _calculate_success_rate(self, results: Dict[str, Any]) -> float:
        """Calculate current success rate based on results.

        Returns:
            Success rate as percentage (0-100)
        """
        total_keys = len(results)
        if total_keys == 0:
            return 0.0

        passed_keys = sum(1 for r in results.values() if r.get("passed", False))
        return (passed_keys / total_keys) * 100

    def create_execution_result(
        self,
        context: ExecutionContext,
        execution_trace: List[Dict],
        errors: List[str],
        start_time: float,
        results: Dict[str, Any],
        state: Dict[str, Any],
        iteration: int,
        signals: set,
        modified_files: set,
    ) -> ExecutionResult:
        """Create final execution result."""
        success = len(errors) == 0 and self._is_converged(results)

        result = ExecutionResult(
            success=success,
            output=state.get("final_output"),
            final_state=state,
            execution_trace=execution_trace,
            iterations=iteration,
            errors=errors,
            metadata={
                "execution_time_seconds": time.time() - start_time,
                "total_phases": len(execution_trace),
                "success_rate": state.get("success_rate", 0),
                "converged": self._is_converged(results),
                "signals": list(signals),
                "modified_files": list(modified_files)
            }
        )

        self.logger.info("execution_completed",
            extra={"success": success,
            "iterations": iteration,
            "execution_time": result.metadata["execution_time_seconds"]})
        return result

    def handle_execution_error(
        self,
        context: ExecutionContext,
        execution_trace: List[Dict],
        start_time: float,
        error: Exception,
        iteration: int,
        state: Dict[str, Any],
    ) -> ExecutionResult:
        """Handle execution error."""
        self.logger.error("execution_failed", extra={"error": str(error)}, exc_info=True)
        return ExecutionResult(
            success=False, final_state=state, execution_trace=execution_trace,
            iterations=iteration, errors=[f"Execution failed: {str(error)}"],
            metadata={"execution_time_seconds": time.time() - start_time}
        )

class NervousSystemStateManagement:
    """Handles state persistence and retrieval for the NervousSystem."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def get_state(self, iteration: int, state: Dict[str, Any], config: OrchestratorConfig) -> Dict[str, Any]:
        """Get current orchestrator state.

        Returns:
            Current state snapshot
        """
        return {
            "iteration": iteration,
            "state": state.copy(),
            "config": config.to_dict(),
        }

    async def save_state(self, path: str, iteration: int, state: Dict[str, Any], config: OrchestratorConfig) -> None:
        """Save orchestrator state to disk.

        Args:
            path: Path to save state
            iteration: Current iteration
            state: Current state dictionary
            config: Orchestrator configuration
        """
        current_state = self.get_state(iteration, state, config)

        with open(path, 'w') as f:
            json.dump(current_state, f, indent=2, default=str)

        self.logger.info("state_saved", extra={"path": path})

    async def load_state(self, path: str) -> Dict[str, Any]:
        """Load orchestrator state from disk.

        Args:
            path: Path to load state from

        Returns:
            Loaded state dictionary
        """
        with open(path, 'r') as f:
            loaded_state = json.load(f)

        self.logger.info("state_loaded", extra={"path": path, "iteration": loaded_state.get("iteration", 0)})
        return loaded_state

class NervousSystemPhaseExecution:
    """Manages the execution of phases (sequential and parallel) and agent interactions."""

    def __init__(
        self,
        brain: ICognitivePlane,
        safety_layer: Any, # Type hint for L5_safety.safety_layer.SafetyLayer
        signal_ledger: SignalLedger,
        modified_files_set: set, # Added
        logger: logging.Logger,
    ):
        self.brain = brain
        self.safety_layer = safety_layer
        self.signal_ledger = signal_ledger
        self.modified_files_set = modified_files_set # Stored
        self.logger = logger
        self._phase_failure_counts: Dict[str, int] = {} # Internal to this executor
        self.phases = self._initialize_phases() # Call new method

    def _initialize_phases(self) -> Dict[str, List]:
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

    async def _get_previous_phase_signals(self, current_phase: str) -> Dict[str, Any]:
        """Get signals from the previous phase for blackboard communication.

        Args:
            current_phase: Name of the current phase

        Returns:
            Dictionary with signals from previous phase
        """
        phase_order = [
            "integrity_seq", "curation_seq", "test_seq", "memory_parallel",
            "resilience_parallel", "resource_safety_parallel", "engineering_parallel",
            "refinement_parallel", "benchmarking_seq", "optimization_conditional"
        ]

        try:
            current_index = phase_order.index(current_phase)
            if current_index > 0:
                previous_phase = phase_order[current_index - 1]
                return await self.signal_ledger.get_phase_summary(previous_phase)
        except ValueError:
            pass

        return {}

    async def _reconcile_signals(self, results: Dict[str, Any], signals: set) -> Dict[str, Any]:
        """Reconcile conflicting signals from different agents.

        Args:
            results: Dictionary of agent results with potential conflicts
            signals: Current set of global signals

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
            signals.add("CONFLICTS_DETECTED") # Update global signals
        else:
            reconciled['has_conflicts'] = False
            reconciled['signal'] = 'NO_CONFLICTS'

        return reconciled

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

    async def run_sequential(
        self,
        phase_name: str,
        context: ExecutionContext,
        execution_trace: List[Dict],
        results: Dict[str, Any],
        signals: set,
    ) -> bool:
        """Execute a phase sequentially (from SwarmScheduler)."""
        # Check circuit breaker before executing phase
        if self._phase_failure_counts.get(phase_name, 0) >= 3:
            self.logger.error(f"Circuit breaker OPEN for {phase_name} - 3 consecutive failures detected")
            self.logger.error("Entering SAFE MODE - Phase 0")
            signals.add("CIRCUIT_BREAKER_TRIPPED")
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
                        self.logger.warning(f"Agent {agent.name} prerequisites not satisfied: {prereq_result.get('message', 'Unknown')}")
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
                        results[agent.name] = result
                        # Add signal for prerequisite failure
                        signals.add("PREREQ_FAIL")
                        phase_passed = False
                        continue

                # Execute agent with context
                if hasattr(agent, 'execute_with_context'):
                    result = await agent.execute_with_context(context)
                else:
                    result = await agent.execute()

                results[agent.name] = result
                if result.get("modified_files"): # NEW
                    self.modified_files_set.update(result["modified_files"]) # NEW
                if not result.get("passed", True):
                    signals.add("CRITICAL_FAIL")
                    phase_passed = False

            # Early abort for critical failures in integrity phase
            if phase_name == "integrity_seq" and ("CRITICAL_FAIL" in signals or "PREREQ_FAIL" in signals):
                self.logger.error(f"Critical failure in {phase_name} - Aborting")
                # Update failure count
                self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
                return False

        # Update failure count based on phase result
        if not phase_passed:
            self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
            self.logger.warning(f"Phase {phase_name} failed - Strike {self._phase_failure_counts[phase_name]}/3")
        else:
            # Reset failure count on success
            if phase_name in self._phase_failure_counts:
                del self._phase_failure_counts[phase_name]
                self.logger.info(f"Phase {phase_name} succeeded - Resetting failure count")

        return phase_passed

    async def run_parallel(
        self,
        phase_name: str,
        context: ExecutionContext,
        execution_trace: List[Dict],
        results: Dict[str, Any],
        signals: set,
    ):
        """Execute a phase in parallel (from SwarmScheduler)."""
        # Check circuit breaker before executing phase
        if self._phase_failure_counts.get(phase_name, 0) >= 3:
            self.logger.error(f"Circuit breaker OPEN for {phase_name} - 3 consecutive failures detected")
            self.logger.error("Entering SAFE MODE - Phase 0")
            signals.add("CIRCUIT_BREAKER_TRIPPED")
            return

        # Check memory pressure before parallel execution
        if hasattr(self.safety_layer, 'cost_governor'):
            try:
                memory_info = self.safety_layer.cost_governor.check_memory_pressure()
                if not memory_info.get("pressure_ok", True):
                    self.logger.error(f"Memory pressure too high: {memory_info.get('available_gb', -1):.2f}GB available")
                    signals.add("MEMORY_PRESSURE")
                    return
            except Exception as e:
                self.logger.warning(f"Could not check memory pressure: {e}")

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
                            self.logger.warning(f"Agent {agent.name} prerequisites not satisfied: {prereq_result.get('message', 'Unknown')}")
                            result = {
                                'passed': False,
                                'error': 'Prerequisites not satisfied',
                                'details': prereq_result.get('message', 'Unknown'),
                                'recommendation': prereq_result.get('recommendation', 'Re-run prerequisite phase')
                            }
                            results[agent.name] = result
                            signals.add("PREREQ_FAIL")
                            return result

                    # Execute agent with context
                    if hasattr(agent, 'execute_with_context'):
                        result = await agent.execute_with_context(context)
                    else:
                        result = await agent.execute()

                    results[agent.name] = result
                    if result.get("modified_files"): # NEW
                        self.modified_files_set.update(result["modified_files"]) # NEW
                    if not result.get("passed", True):
                        signals.add("CRITICAL_FAIL")
                    return result

                task = self._rate_limited_retry(lambda a=agent: execute_agent_with_context(a))
                tasks.append(task)

        # Execute all agents in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

            # Check if phase passed and update failure count
            phase_passed = all(
                results.get(agent.name, {}).get("passed", True)
                for agent in agents if hasattr(agent, 'name')
            )

            if not phase_passed:
                self._phase_failure_counts[phase_name] = self._phase_failure_counts.get(phase_name, 0) + 1
                self.logger.warning(f"Phase {phase_name} failed - Strike {self._phase_failure_counts[phase_name]}/3")
            else:
                # Reset failure count on success
                if phase_name in self._phase_failure_counts:
                    del self._phase_failure_counts[phase_name]
                    self.logger.info(f"Phase {phase_name} succeeded - Resetting failure count")

            # Reconcile signals to detect conflicts
            conflicts = await self._reconcile_signals(results, signals)
            if conflicts.get('has_conflicts'):
                self.logger.warning(f"Phase {phase_name} conflicts detected: {len(conflicts['conflicts'])}")
                for conflict in conflicts['conflicts']:
                    self.logger.warning(f"  {conflict['description']}")
                # Add conflict signal is already handled by _reconcile_signals

    async def execute_forced_agents(
        self,
        context: ExecutionContext,
        execution_trace: List[Dict[str, Any]],
        signals: set,
    ):
        """
        Execute agents forced by telepathic instructions.

        Args:
            context: Current execution context
            execution_trace: Trace to record execution results
            signals: Global signals set to update
        """
        if not hasattr(context, 'forced_agents') or not context.forced_agents:
            return

        self.logger.info(f"🎯 Executing forced agents from telepathy: {', '.join(context.forced_agents)}")

        for agent_name in context.forced_agents:
            try:
                # Find the agent in our phases
                agent_found = False
                for phase_name, phase_agents in self.phases.items():
                    for agent in phase_agents:
                        if hasattr(agent, 'name') and agent.name == agent_name:
                            self.logger.info(f"  → Executing forced agent: {agent_name} (from {phase_name})")

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
                                if result.get("modified_files"): # NEW
                                    self.modified_files_set.update(result["modified_files"]) # NEW
                                if result.get("passed", False):
                                    signals.add(f"{agent_name.upper()}_FORCED_SUCCESS")
                                else:
                                    signals.add(f"{agent_name.upper()}_FORCED_FAILED")

                            agent_found = True
                            break

                if not agent_found:
                    self.logger.warning(f"  [!]  Forced agent not found: {agent_name}")

            except Exception as e:
                self.logger.error(f"  [X] Error executing forced agent {agent_name}: {e}")
                signals.add(f"{agent_name.upper()}_FORCED_ERROR")

        # Clear forced agents after execution
        context.forced_agents.clear()
        self.logger.info("Forced agents execution complete")

class NervousSystemArchitectureGovernance:
    """Handles architecture validation and impact analysis."""

    def __init__(self, architecture_governor: ArchitectureGovernor, logger: logging.Logger):
        self.architecture_governor = architecture_governor
        self.logger = logger

    async def get_impact_radius(self, modified_files: List[str] = None, current_modified_files: set = None) -> Dict[str, Any]:
        """
        Calculate the blast radius for modified files.

        Args:
            modified_files: List of modified file paths (uses tracked files if None)
            current_modified_files: The NervousSystem's internal set of modified files to update

        Returns:
            Dictionary with impact analysis
        """
        if modified_files is None:
            modified_files = list(current_modified_files) if current_modified_files else []

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
        self.logger.info(f"☢️ BLAST RADIUS: {impact_analysis['total_impacted']} files in scope")

        # Add impacted files to modified set for verification
        if current_modified_files is not None:
            for file_path in impact_analysis["blast_radius"]:
                current_modified_files.add(file_path)

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

class NervousSystemInterventionManager:
    """Manages human intervention requests and approvals."""

    def __init__(self, intervention_server: InterventionServer, logger: logging.Logger):
        self.intervention_server = intervention_server
        self.logger = logger

    async def handle_intervention_if_required(
        self,
        cycle: int,
        modified_count: int,
        signals_list: List[str],
        modified_files: List[str],
        timeout: int = 300,
    ) -> Optional[bool]:
        """
        Checks if intervention is required and handles the approval process.

        Returns:
            True if approved, False if vetoed, None if no intervention was required.
        """
        intervention_required, risk_factors = check_intervention_required(
            cycle=cycle,
            modified_count=modified_count,
            signals_list=signals_list
        )

        if intervention_required:
            self.logger.warning(f"High-risk state detected: {risk_factors}")
            await self.intervention_server.start_server()

            approved = await self.intervention_server.request_approval(
                risk_factors=risk_factors,
                cycle=cycle,
                modified_files=modified_files,
                timeout=timeout
            )

            await self.intervention_server.stop_server() # Stop server regardless of approval

            if not approved:
                self.logger.error("Human intervention vetoed - aborting mission")
                return False
            else:
                self.logger.info("Human intervention approved - continuing mission")
                return True
        return None # No intervention required

class NervousSystemPhaseOrchestrator:
    """Orchestrates the execution of all phases within a mission cycle."""

    def __init__(
        self,
        phase_execution_manager: NervousSystemPhaseExecution,
        checkpointing_manager: NervousSystemCheckpointing,
        result_reporting_manager: NervousSystemResultReporting,
        signals_set: set, # Direct reference to NervousSystem's _signals
        results_dict: Dict[str, Any], # Direct reference to NervousSystem's _results
        state_dict: Dict[str, Any], # Direct reference to NervousSystem's _state
        iteration_ref: List[int], # Pass as list to allow modification
        modified_files_set: set, # Direct reference to NervousSystem's _modified_files
        config: OrchestratorConfig,
        logger: logging.Logger,
    ):
        self._phase_execution = phase_execution_manager
        self._checkpointing = checkpointing_manager
        self._result_reporting = result_reporting_manager
        self._signals = signals_set
        self._results = results_dict
        self._state = state_dict
        self._iteration_ref = iteration_ref # [self._iteration]
        self._modified_files = modified_files_set # Stored
        self.config = config
        self.logger = logger

    @property
    def _iteration(self):
        return self._iteration_ref[0]

    @_iteration.setter
    def _iteration(self, value):
        self._iteration_ref[0] = value

    async def _process_phase(
        self,
        phase_name: str,
        phase_type: str, # "sequential", "parallel", "conditional"
        phase_number: int,
        context: ExecutionContext,
        resume_phase: Optional[str],
    ) -> bool:
        """Helper to run a single phase with common logic."""
        def should_skip_phase_local(phase_name: str) -> bool:
            if not resume_phase:
                return False
            phase_order = [
                "integrity_seq", "curation_seq", "test_seq", "memory_parallel",
                "resilience_parallel", "resource_safety_parallel", "engineering_parallel",
                "refinement_parallel", "benchmarking_seq", "optimization_conditional"
            ]
            try:
                resume_index = phase_order.index(resume_phase)
                phase_index = phase_order.index(phase_name)
                return phase_index <= resume_index
            except ValueError:
                return False

        if not should_skip_phase_local(phase_name):
            self.logger.info(f"Phase {phase_number}: {phase_name.replace('_', ' ').upper()} ({phase_type.capitalize()})")
            context.previous_phase_signals = await self._phase_execution._get_previous_phase_signals(phase_name)

            phase_passed = True
            if phase_type == "sequential":
                phase_passed = await self._phase_execution.run_sequential(phase_name, context, context.execution_trace, self._results, self._signals)
            elif phase_type == "parallel":
                await self._phase_execution.run_parallel(phase_name, context, context.execution_trace, self._results, self._signals)
                # For parallel, we assume it passed unless critical signals are set
                phase_passed = "CRITICAL_FAIL" not in self._signals and "PREREQ_FAIL" not in self._signals and "CONFLICTS_DETECTED" not in self._signals
            elif phase_type == "conditional": # For optimization_conditional
                 if self._result_reporting._is_converged(self._results):
                    phase_passed = await self._phase_execution.run_sequential(phase_name, context, context.execution_trace, self._results, self._signals)
                 else:
                    self.logger.info("Skipping optimization - not fully converged")
                    return True # Considered passed if skipped due to non-convergence
            
            await self._checkpointing.save_phase_checkpoint(
                phase_name, self._state, self._results, self._signals, self._modified_files, # Use the set
                self._iteration, context.mission, context.scene, self._result_reporting._calculate_success_rate(self._results)
            )
            return phase_passed
        else:
            self.logger.info(f"Phase {phase_number}: {phase_name.replace('_', ' ').upper()} (Skipping - already completed)")
            return True # Considered passed if skipped

    async def execute_all_phases_in_cycle(self, context: ExecutionContext, resume_phase: Optional[str] = None) -> bool:
        """Execute all phases in order with early abort logic."""
        # The execution_trace is now part of context
        context.execution_trace = context.execution_trace or []

        # Phase 1: Integrity (Sequential - Hard Gate)
        if not await self._process_phase("integrity_seq", "sequential", 1, context, resume_phase):
            if "CRITICAL_FAIL" in self._signals:
                return False

        # Phase 2: Curation (Sequential)
        await self._process_phase("curation_seq", "sequential", 2, context, resume_phase)

        # Phase 3: Testing (Sequential)
        await self._process_phase("test_seq", "sequential", 3, context, resume_phase)

        # Phase 4: Memory (Parallel)
        await self._process_phase("memory_parallel", "parallel", 4, context, resume_phase)

        # Phase 5: RESILIENCE (Parallel)
        await self._process_phase("resilience_parallel", "parallel", 5, context, resume_phase)

        # Phase 6: Resource Safety (Parallel)
        await self._process_phase("resource_safety_parallel", "parallel", 6, context, resume_phase)

        # Phase 7: ENGINEERING (Parallel)
        await self._process_phase("engineering_parallel", "parallel", 7, context, resume_phase)

        # Phase 8: Refinement (Parallel)
        await self._process_phase("refinement_parallel", "parallel", 8, context, resume_phase)

        # Phase 9: Benchmarking (Sequential)
        await self._process_phase("benchmarking_seq", "sequential", 9, context, resume_phase)

        # Phase 10: Optimization (Conditional - Sequential)
        await self._process_phase("optimization_conditional", "conditional", 10, context, resume_phase)

        # Return convergence status
        return self._result_reporting._is_converged(self._results)

    async def run_execution_loop(self, context: ExecutionContext, resume_phase: Optional[str] = None) -> (bool, List[str]):
        """Runs the main execution loop for the mission."""
        errors: List[str] = []
        converged = False

        # Only reset cycle state if not resuming from checkpoint
        if not resume_phase:
            self._iteration = 0 # This will update self._iteration_ref[0]
            self._state.clear()
            self._state.update(context.state.copy())
            self._results.clear()
        self._signals.clear()
        self._modified_files.clear() # Reset modified files for the cycle
        self._state.update(context.state) # Update state with context's state

        # If resuming from final checkpoint, check convergence immediately
        if resume_phase == "optimization_conditional" and self._result_reporting._is_converged(self._results):
            self.logger.info("Resuming from final checkpoint - already converged")
            converged = True
        else:
            max_cycles = self.config.max_iterations or 10
            for cycle in range(max_cycles):
                self._iteration = cycle # Update iteration for current cycle
                self.logger.info(f"Cycle {self._iteration + 1}/{max_cycles}")

                # Execute all phases (only on first cycle when resuming)
                if cycle == 0 or not resume_phase:
                    converged = await self.execute_all_phases_in_cycle(context, resume_phase=resume_phase)
                else:
                    # On subsequent cycles, run without skipping
                    converged = await self.execute_all_phases_in_cycle(context, resume_phase=None)

                # Execute any forced agents from telepathy
                if hasattr(context, 'forced_agents') and context.forced_agents:
                    await self._phase_execution.execute_forced_agents(context, context.execution_trace, self._signals)

                # Check for convergence
                if converged:
                    self.logger.info("Convergence achieved - all checks passed!")
                    break

                # Check for critical failures
                if "CRITICAL_FAIL" in self._signals:
                    errors.append("Critical failure detected")
                    break
        
        return converged, errors

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
        self._iteration_val = [0] # Use a list to pass by reference for iteration

        # Execution tracking
        self._results: Dict[str, Dict[str, Any]] = {}
        self._signals: set = set()
        self._modified_files: set = set() # This will be passed to context.modified_files

        # L5 Intervention Server
        self.intervention_server = InterventionServer()

        # L6 Architecture Governor
        self.architecture_governor = ArchitectureGovernor()

        # Initialize helper classes
        self._checkpointing = NervousSystemCheckpointing(
            self.checkpoint_manager, self.signal_ledger, self.session_id, LOGGER
        )
        self._result_reporting = NervousSystemResultReporting(self.config, LOGGER)
        self._state_management = NervousSystemStateManagement(LOGGER)
        self._phase_execution = NervousSystemPhaseExecution(
            self.brain,
            self.safety_layer, self.signal_ledger, self._modified_files, LOGGER # Pass _modified_files
        )
        self.phases = self._phase_execution.phases

        self._architecture_governance = NervousSystemArchitectureGovernance(
            self.architecture_governor, LOGGER
        )
        self._intervention_manager = NervousSystemInterventionManager(
            self.intervention_server, LOGGER
        )
        self._phase_orchestrator = NervousSystemPhaseOrchestrator( # New orchestrator
            self._phase_execution,
            self._checkpointing,
            self._result_reporting,
            self._signals,
            self._results,
            self._state,
            self._iteration_val, # Pass reference
            self._modified_files, # Pass reference
            self.config,
            LOGGER,
        )

        LOGGER.info(
            "nervous_system_initialized",
            extra={
                "cognitive_capabilities": [c.value if hasattr(c, 'value') else c for c in self.brain.get_capabilities()],
                "action_capabilities": [c.value if hasattr(c, 'value') else c for c in self.hands.get_capabilities()],
                "config": self.config.to_dict(),
                "phases_populated": len([p for p in self.phases.values() if p])
            }
        )

    @property
    def _iteration(self):
        return self._iteration_val[0]

    @_iteration.setter
    def _iteration(self, value):
        self._iteration_val[0] = value

    async def run_mission(self, max_phases: Optional[int] = None) -> ExecutionResult:
        """Run the full mission with phase-based execution.

        Args:
            max_phases: Maximum number of phases to execute (None for all)

        Returns:
            ExecutionResult with mission status and report
        """
        start_time = time.time()

        # Check for existing checkpoint to resume from
        last_checkpoint = await self._checkpointing.find_last_checkpoint()
        resume_phase = None
        if last_checkpoint:
            LOGGER.info(f"L4: Checkpoint found. Resuming from Phase 2.")
            (self._state, self._results, self._signals,
             self._modified_files, self._iteration, resume_phase) = \
                self._checkpointing.restore_from_checkpoint(last_checkpoint)

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

        # Handle intervention
        intervention_status = await self._intervention_manager.handle_intervention_if_required(
            cycle=cycle,
            modified_count=modified_count,
            signals_list=signals_list,
            modified_files=list(self._modified_files),
            timeout=300
        )

        if intervention_status is False: # Vetoed
            self._signals.add("VETOED")
            return ExecutionResult(
                success=False,
                output="",
                error="Mission vetoed by human intervention",
                execution_time=time.time() - start_time
            )
        # If intervention_status is True (approved) or None (not required), continue

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
        # Initialize context.execution_trace
        context.execution_trace = []

        # The internal state (_iteration, _state, _results, _signals, _modified_files)
        # will be managed by NervousSystemPhaseOrchestrator via direct references.
        # NervousSystem needs to ensure they are correctly initialized or restored
        # before passing to orchestrator.

        # Only reset cycle state if not resuming from checkpoint
        if not resume_phase:
            self._iteration = 0 # Reset NervousSystem's iteration
            self._state = context.state.copy() # Reset NervousSystem's state
            self._results = {} # Reset NervousSystem's results
            self._signals = set() # Reset NervousSystem's signals
            self._modified_files = set() # Reset NervousSystem's modified files
        self._state.update(context.state) # Update NervousSystem's state with context's state

        LOGGER.info("execution_started",
            extra={"mission": context.mission,
            "scene_keys": list(context.scene.keys())})

        try:
            # Run the main execution loop via the orchestrator
            converged, errors = await self._phase_orchestrator.run_execution_loop(context, resume_phase=resume_phase)

            # After the loop, NervousSystem's internal state (_iteration, _state, _results, _signals, _modified_files)
            # is already updated via direct references.

            # Generate mission report and calculate success rate
            self._result_reporting._generate_mission_report(self._results, self._state)

            # Create execution result
            result = self._result_reporting.create_execution_result(
                context, context.execution_trace, errors, start_time,
                self._results, self._state, self._iteration, self._signals, self._modified_files
            )

            # Log result to signal ledger
            await self.signal_ledger.append_result(result)

            return result
        except Exception as e:
            return self._result_reporting.handle_execution_error(
                context, context.execution_trace, start_time, e, self._iteration, self._state
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
        return self._state_management.get_state(self._iteration, self._state, self.config)

    async def save_state(self, path: str) -> None:
        """Save orchestrator state to disk.

        Args:
            path: Path to save state
        """
        await self._state_management.save_state(path, self._iteration, self._state, self.config)

    async def load_state(self, path: str) -> None:
        """Load orchestrator state from disk.

        Args:
            path: Path to load state from
        """
        loaded_state = await self._state_management.load_state(path)
        self._iteration = loaded_state.get("iteration", 0)
        self._state = loaded_state.get("state", {})

    def _extract_actions(self, think_result: Dict[str, Any]) -> List[ActionRequest]:
        """Extract action requests from planning result.

        Args:
            think_result: Result from think phase

        Returns:
            List of action requests
        """
        actions: List[ActionRequest] = []

        plan = think_result.get("plan", [])

        for step in plan:
            if step.get("type") == "action":
                action = ActionRequest(
                    action_type=step.get("action_type", "tool_call"),
                    tool_name=step.get("tool", "unknown"),
                    parameters=step.get("parameters", {}),
                    context=step.get("context", {}),
                )
                actions.append(action)

        return actions

    async def get_impact_radius(self, modified_files: List[str] = None) -> Dict[str, Any]:
        """
        Calculate the blast radius for modified files.

        Args:
            modified_files: List of modified file paths (uses tracked files if None)

        Returns:
            Dictionary with impact analysis
        """
        return await self._architecture_governance.get_impact_radius(modified_files, self._modified_files)

    def validate_architecture(self, file_paths: List[str] = None) -> Dict[str, Any]:
        """
        Validate architecture compliance.

        Args:
            file_paths: Specific files to validate

        Returns:
            Validation report
        """
        return self._architecture_governance.validate_architecture(file_paths)