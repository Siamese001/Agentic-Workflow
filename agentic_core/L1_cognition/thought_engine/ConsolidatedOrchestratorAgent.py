"""
ConsolidatedOrchestratorAgent - Extracted for one-class-per-file pattern.

Originally from: OrchestratorAgentAndScopeManagerAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
import ast
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

class ConsolidatedOrchestratorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
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

    def __init__(self, config: Optional[OrchestratorConfig]=None, context: Optional[ValidationContext]=None) -> None:
        """
        Initialize the consolidated orchestrator.
        
        Args:
            config: Orchestrator configuration
            context: Validation context (creates new if None)
        """
        global _orchestrator_instance
        self.config = config or OrchestratorConfig()
        self.ctx = context or ValidationContext()
        self.state: Optional[OrchestratorState] = None
        self.blackboard = getattr(self.ctx, 'blackboard', None)
        _orchestrator_instance = self
        atexit.register(self.release_all_leases)
        if GENAI_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            Logger.info('[OK] Gemini 2.5/3.0 client initialized')
        else:
            self.client = None
            Logger.warning('[!]  Gemini client not available')
        self.healing_service: Optional[OrchestratorHealingService] = None
        self.state_manager: Optional[OrchestratorStateManager] = None
        self.agent_scope_manager = OrchestratorAgentAndScopeManagerAgent(self.config, self.ctx, Logger)
        if self.config.clean_slate:
            self._execute_clean_slate()
        Logger.info('[START] Consolidated orchestrator initialized (Phase 5: Swarm Assembly)')

    def _execute_clean_slate(self):
        """Execute Clean Slate Protocol: Flush Redis and clear all leases."""
        Logger.info('[CLEAN] CLEAN SLATE PROTOCOL: Flushing Redis...')
        try:
            if self.blackboard:
                self.release_all_leases()
                Logger.info('   [OK] All leases released')
            Logger.info('   [OK] Clean slate executed')
        except Exception as e:
            Logger.warning(f'   [!]  Clean slate failed: {e}')

    def release_all_leases(self) -> Any:
        """Release all leases held by this orchestrator (graceful shutdown)."""
        if self.blackboard and hasattr(self.blackboard, 'release_all_leases'):
            try:
                self.blackboard.release_all_leases()
                Logger.info('   [OK] All blackboard leases released')
            except Exception as e:
                Logger.warning(f'   [!]  Lease release failed: {e}')

    async def run_mission(self, target_path: Optional[str]=None, workflow_id: Optional[str]=None) -> Dict[str, Any]:
        """
        Run the orchestration mission with subatomic agents.
        
        This is the main entry point for all orchestration tasks.
        
        Args:
            target_path: Optional target file or directory for surgical scope
            workflow_id: Optional workflow identifier
            
        Returns:
            Mission execution results
        """
        workflow_id: Any = workflow_id or f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_path: Any = target_path or self.config.target_path
        Logger.info(f"\n{'=' * 60}")
        Logger.info(f'[START] MISSION START: {workflow_id}')
        Logger.info(f"{'=' * 60}")
        if self.config.smart_scope:
            Logger.info(f'🔗 SMART SCOPE ENABLED: Building dependency graph...')
            target_files: Any = await self.agent_scope_manager.calculate_smart_scope(target_path)
            Logger.info(f'   Impact scope: {len(target_files)} files (depth: {self.config.smart_scope_depth})')
            self.ctx.smart_scope_targets = target_files
        elif target_path:
            Logger.info(f'🎯 SURGICAL MODE: Targeting {target_path}')
        else:
            Logger.info(f'🌐 FULL REPOSITORY MODE')
        agents: Any = self.agent_scope_manager.create_agent_swarm()
        results: Any = await self.execute_workflow(workflow_id=workflow_id, agents=agents, context={'target_path': target_path})
        Logger.info(f"\n{'=' * 60}")
        Logger.info(f"[OK] MISSION COMPLETE: {results['status']}")
        Logger.info(f"{'=' * 60}")
        return results

    async def execute_workflow(self, workflow_id: str, agents: List[Any], context: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        """
        Execute a workflow with the given agents using convergence loop.
        
        Args:
            workflow_id: Unique workflow identifier
            agents: List of agent instances to execute
            context: Optional execution context
            
        Returns:
            Workflow execution results
        """
        self.state = OrchestratorState(workflow_id=workflow_id, start_time=datetime.now())
        self.healing_service = OrchestratorHealingService(config=self.config, ctx=self.ctx, client=self.client, state=self.state, Logger=Logger)
        self.state_manager = OrchestratorStateManager(config=self.config, ctx=self.ctx, state=self.state, Logger=Logger)
        Logger.info(f'\n[~] Starting convergence loop...')
        Logger.info(f'   Max cycles: {self.config.max_cycles}')
        Logger.info(f'   Agents: {len(agents)}')
        context: Any = context or {}
        for cycle in range(self.config.max_cycles):
            self.state.current_cycle = cycle + 1
            self.state.signals.clear()
            self.ctx.modified_files.clear()
            Logger.info(f"\n{'=' * 60}")
            Logger.info(f'CYCLE {cycle + 1}/{self.config.max_cycles}')
            Logger.info(f"{'=' * 60}")
            for agent in agents:
                if not self.state_manager.should_run_agent(agent):
                    Logger.debug(f'Skipping agent {agent.__class__.__name__}')
                    continue
                try:
                    Logger.info(f'\n[>>>] Running: {agent.__class__.__name__}')
                    await agent.execute()
                    if self.config.enable_healing and agent.__class__.__name__ in ['SystemArchitect', 'CodeJanitor']:
                        if self.ctx.modified_files:
                            Logger.info(f'\n[🔮] Running Regression Oracle for {len(self.ctx.modified_files)} modified files...')
                            for file_path in self.ctx.modified_files:
                                self.ctx.signals.add(f'FILE_MODIFIED:{file_path}')
                            oracle: Any = get_regression_oracle(self.ctx)
                            await oracle.execute()
                            regression_signals: Any = [s for s in self.ctx.signals if s.startswith('REGRESSION_DETECTED:')]
                            if regression_signals:
                                Logger.error(f'\n[ALERT] REGRESSIONS DETECTED: {len(regression_signals)}')
                                for signal in regression_signals:
                                    Logger.error(f'   {signal}')
                                self.state.signals.add('INTERVENTION_REQUIRED')
                    if 'AGENT_FAILURE' in self.ctx.signals:
                        Logger.warning(f'   [!]  Agent failure detected - executing clean slate')
                        self._execute_clean_slate()
                        self.ctx.signals.discard('AGENT_FAILURE')
                    if self.config.enable_checkpointing:
                        await self.state_manager.checkpoint_state(agent.__class__.__name__)
                except Exception as e:
                    Logger.error(f'[X] Agent {agent.__class__.__name__} failed: {e}')
                    self.state.signals.add('AGENT_FAILURE')
                    if self.config.clean_slate:
                        self._execute_clean_slate()
            if self.state_manager.should_terminate():
                Logger.info('\n[OK] CONVERGENCE ACHIEVED')
                self.state.status = 'COMPLETED'
                break
            if self.config.enable_intervention and 'INTERVENTION_REQUIRED' in self.state.signals:
                Logger.info('\n✋ INTERVENTION REQUIRED')
                if not await self.state_manager.handle_intervention():
                    Logger.info('🛑 WORKFLOW VETOED')
                    self.state.status = 'VETOED'
                    break
        self.state.end_time = datetime.now()
        if self.state.status != 'COMPLETED' and self.state.status != 'VETOED':
            self.state.status = 'MAX_CYCLES_REACHED'
            Logger.warning(f'\n[!]  Max cycles reached without convergence')
        return self.state_manager.build_results()

    async def execute_with_healing(self, file_path: str, violation_key: int, fix_prompt: str) -> bool:
        """
        Delegate healing operation to the OrchestratorHealingService.
        
        Args:
            file_path: Path to file to heal
            violation_key: Violation key to fix
            fix_prompt: Prompt for LLM to fix Violation
            
        Returns:
            True if healing succeeded, False otherwise
        """
        if not self.healing_service:
            Logger.error('Healing service not initialized. Cannot execute healing.')
            return False
        return await self.healing_service.execute_healing(file_path, violation_key, fix_prompt)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
