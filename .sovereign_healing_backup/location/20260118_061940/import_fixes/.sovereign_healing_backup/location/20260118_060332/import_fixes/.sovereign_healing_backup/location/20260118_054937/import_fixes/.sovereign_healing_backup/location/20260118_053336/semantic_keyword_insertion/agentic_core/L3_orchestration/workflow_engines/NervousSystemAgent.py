from dataclasses import dataclass
"""
NervousSystemAgent - Extracted for one-class-per-file pattern.

Originally from: NervousSystemPhaseOrchestratorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from typing import Any, Dict, List, Optional
import asyncio
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

from agentic_core.L5_safety.validators.structure_blueprint import (
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

@dataclass
class NervousSystemAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin):
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
    ) -> None:
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
        self.CheckpointManager = VerifiableCheckpointManager(storage_adapter)
        self.session_id = getattr(config, 'mission_id', f"mission_{int(time.time())}")
        self.SignalLedger = SignalLedger(storage_adapter, self.session_id)

        # Create sovereign implementations if not provided
        self.brain = cognitive_plane or create_sovereign_cognitive_plane()
        self.hands = action_plane or create_sovereign_action_plane(
            safety_layer=self.safety_layer,
            SignalLedger=self.SignalLedger
        )
        self.config = config or OrchestratorConfig()

        self._state: Dict[str, Any] = {}
        self._iteration_val = [0] # Use a list to pass by reference for iteration

        # Execution tracking
        self._results: Dict[str, Dict[str, Any]] = {}
        self._signals: set = set()
        self._modified_files: set = set() # This will be passed to context.modified_files

        # L5 Intervention Server
        self.InterventionServer = InterventionServer()

        # L6 Architecture Governor
        self.ArchitectureGovernor = ArchitectureGovernor()

        # GOLD STANDARD: Domain-specific agent integrations for post-phase validation
        self.project_root = Path(__file__).resolve().parents[3]
        # [SSOT DYNAMIC] Runtime-only L5 imports for validation agents
        try:
            from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
            self.location_agent = LocationAgent(self.project_root)
        except ImportError:
            self.location_agent = None
        # [SSOT DYNAMIC] Runtime-only L5 imports for validation agents
        try:
            from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
            self.hierarchy_agent = HierarchyAgent(self.project_root)
        except ImportError:
            self.hierarchy_agent = None
        # [SSOT DYNAMIC] Runtime-only L5 imports for validation agents
        try:
            from agentic_core.L5_safety.gravity.ImportAgent import ImportAgent
            self.import_agent = ImportAgent(self.project_root)
        except ImportError:
            self.import_agent = None
        self._backup_dir: Optional[Path] = None

        # Initialize helper classes
        self._checkpointing = NervousSystemCheckpointing(
            self.CheckpointManager, self.SignalLedger, self.session_id, LOGGER
        )
        self._result_reporting = NervousSystemResultReporting(self.config, LOGGER)
        self._state_management = NervousSystemStateManagement(LOGGER)
        self._phase_execution = NervousSystemPhaseExecution(
            self.brain,
            self.safety_layer, self.SignalLedger, self._modified_files, LOGGER # Pass _modified_files
        )
        self.phases = self._phase_execution.phases

        self._architecture_governance = NervousSystemArchitectureGovernance(
            self.ArchitectureGovernor, LOGGER
        )
        self._intervention_manager = NervousSystemInterventionManager(
            self.InterventionServer, LOGGER
        )

        self._phase_orchestrator = NervousSystemPhaseOrchestratorAgent( # New orchestrator
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

        # PHASE 5: Coverage bias tracking for dynamic layer prioritization
        self.coverage_bias_state: Dict[str, Dict] = {}
        self.bias_hysteresis_threshold = 0.15
        self.max_concurrent_biases = 3
        subscribe_event("coverage_bias_update", self._handle_bias_update)

        # PHASE 9: Reinforcement-learned orchestration
        self.rl_orchestrator = RLOrchestratorAgent(
            layers=["L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
                   "L4_state", "L5_safety", "config", "schemas", "prompt_governance",
                   "observability", "utils", APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR],
            fallback_orchestrator=self
        )
        self.last_entropy = 0.0
        self.rl_update_interval = 100

        LOGGER.info(
            "nervous_system_initialized",
            extra={
                "cognitive_capabilities": [c.value if hasattr(c, 'value') else c for c in self.brain.get_capabilities()],
                "action_capabilities": [c.value if hasattr(c, 'value') else c for c in self.hands.get_capabilities()],
                "config": self.config.to_dict(),
                "phases_populated": len([p for p in self.phases.values() if p]),
                "coverage_bias_enabled": True,
                "rl_orchestration_enabled": True
            }
        )

    def _handle_bias_update(self, event_data: Dict) -> None:
        """Process CoverageAgent bias events — multi-layer queue."""
        layer = event_data.get("underrepresented_layer")
        weight = event_data.get("selection_weight_multiplier")
        cycles = event_data.get("remaining_orchestration_cycles")

        if not layer or not weight or not cycles:
            return

        # Enforce max concurrent
        if len(self.coverage_bias_state) >= self.max_concurrent_biases:
            lowest_layer = min(self.coverage_bias_state, key=lambda k: self.coverage_bias_state[k]["weight"])
            del self.coverage_bias_state[lowest_layer]

        self.coverage_bias_state[layer] = {
            "weight": weight,
            "remaining_cycles": cycles,
            "last_updated": time.time(),
        }
        LOGGER.info(f"Coverage bias activated: {layer} *{weight} for {cycles} cycles")

    def _decay_biases(self) -> None:
        """Decrement and cleanup expired biases with dynamic decay based on health."""
        expired = [l for l, info in self.coverage_bias_state.items() if info["remaining_cycles"] <= 0]
        for l in expired:
            del self.coverage_bias_state[l]
        
        # Decrement active and apply dynamic decay
        for layer, info in list(self.coverage_bias_state.items()):
            info["remaining_cycles"] = max(0, info["remaining_cycles"] - 1)
            
            # Dynamic decay: Reduce weight if proportion healthy
            try:
                from agentic_core.L6_observability.metrics.CoverageAgent import CoverageAgent
                coverage_agent = CoverageAgent()
                metrics = coverage_agent._fetch_metrics()
                if metrics:
                    current_props = coverage_agent._compute_proportions(metrics)
                    if current_props.get(layer, 0) > 0.25:  # Healthy threshold
                        info["weight"] = max(1.0, info["weight"] * 0.8)  # Gradual decay
                        if info["weight"] <= 1.1:
                            del self.coverage_bias_state[layer]
            except Exception:
                # If metrics unavailable, just decrement cycles
                pass

    def force_exerciser_fallback(self, task: Dict) -> Optional[str]:
        """If no candidates in target layer, direct to exerciser."""
        target = task.get("target_territory")
        if target:
            exerciser_map = {
                "L5_safety": "L5SafetyExerciserAgent",
                "L4_state": "L4StateExerciserAgent",
                "L1_cognition": "L1CognitionExerciserAgent",
            }
            return exerciser_map.get(target)
        return None

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, 'brain'), "Missing brain"
        assert hasattr(self, 'hands'), "Missing hands"
        assert hasattr(self, 'safety_layer'), "Missing safety_layer"
        return True

    @property
    def _iteration(self) -> Any:
        """Iteration."""
        return self._iteration_val[0]

    @_iteration.setter
    def _iteration(self, value) -> Any:
        """Iteration."""
        self._iteration_val[0] = value

    async def _restore_checkpoint_if_exists(self) -> Optional[str]:
        """Restore from checkpoint if one exists."""
        last_checkpoint = await self._checkpointing.find_last_checkpoint()
        if last_checkpoint:
            LOGGER.info(f"L4: Checkpoint found. Resuming from Phase 2.")
            (self._state, self._results, self._signals,
             self._modified_files, self._iteration, resume_phase) = \
                self._checkpointing.restore_from_checkpoint(last_checkpoint)
            return resume_phase
        return None

    async def run_mission(self, max_phases: Optional[int] = None) -> ExecutionResult:
        """Run the full mission with phase-based execution.

        Args:
            max_phases: Maximum number of phases to execute (None for all)

        Returns:
            ExecutionResult with mission status and report
        """
        start_time = time.time()

        # Check for existing Checkpoint to resume from
        resume_phase = await self._restore_checkpoint_if_exists()

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
        # will be managed by NervousSystemPhaseOrchestratorAgent via direct references.
        # NervousSystem needs to ensure they are correctly initialized or restored
        # before passing to orchestrator.

        # Only reset cycle state if not resuming from Checkpoint
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
            await self.SignalLedger.append_result(result)
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

    def post_phase_validation(self, phase_name: str, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        GOLD STANDARD: Post-phase validation using domain-specific agents.
        Validates location, hierarchy, and import compliance after phase completion.
        
        Args:
            phase_name: Name of the completed phase
            affected_paths: List of file paths affected by the phase
            dry_run: If True, only preview without applying fixes
            
        Returns:
            Dict with validation results from all integrated agents
        """
        report = {
            "phase_name": phase_name,
            "post_phase_status": "SKIPPED",
            "location_validation": {},
            "hierarchy_validation": {},
            "import_validation": {},
            "message": "",
        }

        if dry_run:
            report["message"] = "PREVIEW: Post-phase validation skipped in dry-run"
            return report

        try:
            valid_files = [p for p in affected_paths if p.suffix == ".py" and p.exists()]
            
            # LocationAgent validation
            if self.location_agent and valid_files:
                location_violations = []
                for path in valid_files:
                    is_valid, msg = self.location_agent.validate_file_location(path)
                    if not is_valid:
                        location_violations.append({"file": str(path), "issue": msg})
                report["location_validation"] = {
                    "violations": location_violations,
                    "status": "FULL_SUCCESS" if not location_violations else "NEEDS_REVIEW"
                }

            # HierarchyAgent validation
            if self.hierarchy_agent and valid_files:
                hierarchy_violations = []
                for path in valid_files:
                    result = self.hierarchy_agent.validate_file_hierarchy(path)
                    if not result.get("is_valid", True):
                        hierarchy_violations.append({"file": str(path), "issue": result.get("message", "")})
                report["hierarchy_validation"] = {
                    "violations": hierarchy_violations,
                    "status": "FULL_SUCCESS" if not hierarchy_violations else "NEEDS_REVIEW"
                }

            # ImportAgent validation
            if self.import_agent and valid_files:
                import_violations = self.import_agent.run(valid_files)
                report["import_validation"] = {
                    "violations": [{"file": str(p), "issues": m} for p, m in import_violations],
                    "status": "FULL_SUCCESS" if not import_violations else "NEEDS_REVIEW"
                }

            # Determine overall status
            all_statuses = [
                report["location_validation"].get("status", "SKIPPED"),
                report["hierarchy_validation"].get("status", "SKIPPED"),
                report["import_validation"].get("status", "SKIPPED"),
            ]
            if all(s == "FULL_SUCCESS" for s in all_statuses if s != "SKIPPED"):
                report["post_phase_status"] = "FULL_SUCCESS"
                report["message"] = f"Phase {phase_name} post-validation: All checks passed"
            elif "NEEDS_REVIEW" in all_statuses:
                report["post_phase_status"] = "NEEDS_REVIEW"
                report["message"] = f"Phase {phase_name} post-validation: Some violations detected"
            else:
                report["post_phase_status"] = "PARTIAL"
                report["message"] = f"Phase {phase_name} post-validation: Partial completion"

            Logger.info(f"[NervousSystemAgent] {report['message']}")

        except Exception as e:
            report["post_phase_status"] = "ERROR"
            report["message"] = f"Post-phase validation error: {e}"
            Logger.error(f"[NervousSystemAgent] Post-phase validation failed: {e}")

        return report

    def cleanup_violations(
        self,
        violations: List[PhaseViolation],
        dry_run: bool = True,
        max_actions: int = 50
    ) -> List[Dict[str, Any]]:
        """
        GOLD STANDARD: Cleanup violations using integrated domain agents.
        Prioritizes healing based on violation severity and type.
        
        Args:
            violations: List of PhaseViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run
            
        Returns:
            List of action dicts with results and batch summary
        """
        actions = []
        affected_paths: List[Path] = []

        for i, violation in enumerate(violations):
            if i >= max_actions:
                Logger.warning(f"[NervousSystemAgent] Cleanup budget exhausted ({max_actions})")
                break

            action = {
                "type": "PHASE_VIOLATION_HEALING",
                "phase": violation.phase_name,
                "agent": violation.agent_name,
                "violation": violation.message,
                "applied": False,
                "action_taken": "",
            }

            try:
                # Route to appropriate agent based on violation type
                if violation.file_path and self.location_agent:
                    if "LOCATION" in violation.message.upper() or "TERRITORY" in violation.message.upper():
                        cleanup_result = self.location_agent.cleanup_violations(
                            [(violation.file_path, violation.message)], dry_run=dry_run
                        )
                        if cleanup_result:
                            action.update(cleanup_result[0])
                            if not dry_run:
                                affected_paths.append(violation.file_path)

                    elif "HIERARCHY" in violation.message.upper() and self.hierarchy_agent:
                        cleanup_result = self.hierarchy_agent.cleanup_violations(
                            [(violation.file_path, violation.message)], dry_run=dry_run
                        )
                        if cleanup_result:
                            action.update(cleanup_result[0])
                            if not dry_run:
                                affected_paths.append(violation.file_path)

                    elif "IMPORT" in violation.message.upper() or "GRAVITY" in violation.message.upper():
                        if self.import_agent:
                            cleanup_result = self.import_agent.cleanup_violations(
                                [(violation.file_path, violation.message)], dry_run=dry_run
                            )
                            if cleanup_result:
                                action.update(cleanup_result[0])
                                if not dry_run:
                                    affected_paths.append(violation.file_path)

            except Exception as e:
                action["error"] = str(e)
                Logger.error(f"[NervousSystemAgent] Cleanup error: {e}")

            actions.append(action)

        # Batch post-heal summary
        batch_report = {
            "batch_post_heal_status": "PREVIEW" if dry_run else "APPLIED",
            "batch_healed_count": sum(1 for a in actions if a.get("applied")),
            "batch_affected_paths": len(affected_paths),
            "batch_message": f"Processed {len(actions)} violations",
        }

        for action in actions:
            action["batch_post_heal"] = batch_report

        return actions

    def run_with_cleanup(self, files: List[Path] = None, dry_run: bool = True) -> Dict[str, Any]:
        """
        GOLD STANDARD: Full orchestration with autonomous cleanup.
        Runs all phases, validates, and cleans up violations.
        
        Args:
            files: Optional list of files to process
            dry_run: If True, only preview cleanup actions
            
        Returns:
            Dict with comprehensive execution and cleanup summaries
        """
        # Collect violations from post-phase validation
        all_violations: List[PhaseViolation] = []
        affected_paths = [Path(f) for f in (files or list(self._modified_files))]

        # Run post-phase validation for all phases
        for phase_name in self.phases.keys():
            validation_report = self.post_phase_validation(phase_name, affected_paths, dry_run=dry_run)
            
            # Convert validation issues to PhaseViolation objects
            for loc_viol in validation_report.get("location_validation", {}).get("violations", []):
                all_violations.append(PhaseViolation(
                    phase_name=phase_name,
                    is_valid=False,
                    message=loc_viol.get("issue", "Location violation"),
                    file_path=Path(loc_viol.get("file", "")) if loc_viol.get("file") else None,
                    severity=5
                ))
            for hier_viol in validation_report.get("hierarchy_validation", {}).get("violations", []):
                all_violations.append(PhaseViolation(
                    phase_name=phase_name,
                    is_valid=False,
                    message=hier_viol.get("issue", "Hierarchy violation"),
                    file_path=Path(hier_viol.get("file", "")) if hier_viol.get("file") else None,
                    severity=4
                ))
            for imp_viol in validation_report.get("import_validation", {}).get("violations", []):
                all_violations.append(PhaseViolation(
                    phase_name=phase_name,
                    is_valid=False,
                    message=str(imp_viol.get("issues", "Import violation")),
                    file_path=Path(imp_viol.get("file", "")) if imp_viol.get("file") else None,
                    severity=3
                ))

        # Cleanup violations
        cleanup_results = self.cleanup_violations(all_violations, dry_run=dry_run) if all_violations else []
        batch_summary = cleanup_results[0].get("batch_post_heal", {}) if cleanup_results else {}

        return {
            "violations_detected": len(all_violations),
            "actions_applied": sum(1 for a in cleanup_results if a.get("applied")),
            "detailed_actions": cleanup_results,
            "batch_post_heal_summary": batch_summary,
            "location_summary": {"violations": len([v for v in all_violations if "LOCATION" in v.message.upper()])},
            "hierarchy_summary": {"violations": len([v for v in all_violations if "HIERARCHY" in v.message.upper()])},
            "import_summary": {"violations": len([v for v in all_violations if "IMPORT" in v.message.upper() or "GRAVITY" in v.message.upper()])},
            "dry_run": dry_run,
        }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        if _call_path is None:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
