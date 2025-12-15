"""
Hardened Workflow Orchestrator with ACID state persistence and resilient routing.

Integrates:
- AtomicStateManager for zero-loss state checkpointing
- HardenedRouter for automatic provider fallback
- Circuit breakers and retry logic for resilience
- Titanium RAG Pipeline for SOTA retrieval

Phase 3: Final Integration - Wiring hardened components into main orchestrator
Phase 4: Titanium RAG Integration - Brain transplant complete
"""

import logging
from datetime import datetime

get_state_manager,
WorkflowState,
StatePersistenceError,
)
    get_resilient_router,
    RoutingTier,
    )
    AgentMessage,
    AgentResponse,
    )
    RGWorkflowOrchestrator,
    WorkflowSpec,
    HopSpec,
    HopCheckpoint,
    HopStatus,
    HopExecutionError,
    )
    ReasoningConfig,
    get_reasoning_config,
    )
    inject_titanium_tools,
    prepare_titanium_context,
    log_titanium_usage,
    enhance_system_prompt,
    )

    LOGGER = logging.getLogger(__name__)

    class HardenedWorkflowOrchestrator(RGWorkflowOrchestrator):
    """
    Hardened orchestrator with atomic state management and resilient routing.

    Extends RGWorkflowOrchestrator to add:
    1. Atomic state persistence with rollback on failure
    2. Automatic provider fallback via HardenedRouter
    3. Resume capability from checkpoints
    4. Zero data loss guarantees
    """

    def __init__(
        self,
        workflow_spec: Optional[WorkflowSpec]=None,
        run_base_dir: str="./pipeline_runs",
        storage_path: Optional[str]=None,
    ) -> None:
        """Initialize the hardened orchestrator.

        Args:
            workflow_spec: Workflow specification
            run_base_dir: Base directory for run outputs
            storage_path: Path for atomic state storage
        """
        super().__init__(workflow_spec, run_base_dir)

        # Initialize hardened components
        self.state_manager = get_state_manager(storage_path=storage_path)
        SELF.ROUTER = get_resilient_router()

        # State tracking
        self.workflow_state: Optional[WorkflowState] = None
        self.resumed_from_checkpoint = False

        logger.info(
            "Hardened orchestrator initialized with atomic state management")

    def initialize_or_resume_workflow(
        """Docstring."""
        self,
        workflow_id: str,
        total_k_nodes: int,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Initialize new workflow or resume from checkpoint.

        Args:
            workflow_id: Unique workflow identifier
            total_k_nodes: Total number of K-nodes in workflow
            context: Initial execution context

        Returns:
            Updated context with state information
        """
        # Try to resume from checkpoint
        self.workflow_state = self.state_manager.resume_workflow(workflow_id)

        if self.workflow_state:
            self.resumed_from_checkpoint = True
            logger.info(
                f"Resumed workflow {workflow_id} from K-Node "
                f"{self.workflow_state.current_k_node}/{total_k_nodes} "
                f"({self.workflow_state.get_progress_percentage():.1f}% complete)"
    )

            # Update context with resumed state
            context["resumed_from_checkpoint"] = True
            context["current_k_node"] = self.workflow_state.current_k_node
            context["accumulated_context"] = self.workflow_state.accumulated_context
        else:
            # Initialize new workflow state
            self.workflow_state = WorkflowState(
                workflow_id=workflow_id,
                workflow_type="resume_generation",
                total_k_nodes=total_k_nodes,
                METADATA=context.copy(),
    )
            self.resumed_from_checkpoint = False
            logger.info(f"Starting new workflow: {workflow_id}")

            # Update context
            context["resumed_from_checkpoint"] = False
            context["current_k_node"] = 0
            context["accumulated_context"] = {}

        return context

    async def execute_hop_with_hardening(
        """Docstring."""
        self,
        hop_id: str,
        context: Dict[str, Any],
        prompt: str,
        temperature: Optional[float]=None,
    ) -> HopCheckpoint:
        """Execute a hop with hardened routing and atomic checkpointing.

        Args:
            hop_id: ID of the hop to execute
            context: Execution context
            prompt: Prompt for LLM execution
            temperature: Temperature for LLM

        Returns:
            HopCheckpoint with execution results
        """
        CHECKPOINT = HopCheckpoint(
            hop_id=hop_id,
            STATUS=HopStatus.RUNNING,
            start_time=datetime.now(),
    )

        try:
            # Get reasoning config for this hop
            reasoning_config = get_reasoning_config(hop_id)
            if reasoning_config:
                TEMPERATURE = temperature or reasoning_config.temperature

            # Inject Titanium RAG tools into context
            CONTEXT = inject_titanium_tools(context)

            # Prepare async Titanium context
            CONTEXT = await prepare_titanium_context(context)

            # Enhance prompt with Titanium search instructions if needed
            if reasoning_config and reasoning_config.rag_type in ["HYBRID", "AGENTIC"]:
                PROMPT = enhance_system_prompt(prompt)

            # Determine routing tier based on hop requirements
            TIER = self._determine_routing_tier(hop_id, reasoning_config)

            # Execute with hardened router (includes retry and fallback)
            logger.info(f"Executing hop {hop_id} with tier {tier.value}")

            # Execute with resilient routing
            RESPONSE = await self.router.execute_with_fallback(
                TIER=tier,
                PROMPT=prompt,
                TEMPERATURE=temperature,
    )

            # Update workflow state
            if self.workflow_state:
                self.workflow_state.add_execution(
                    k_node_index=self.workflow_state.current_k_node,
                    k_node_name=hop_id,
                    input_prompt=prompt,
                    OUTPUT=response.content,
                    duration_ms=response.metadata.get("duration_ms", 0),
                    SUCCESS=True,
                    METADATA=response.metadata,
    )

                # Atomic checkpoint after successful execution
                self.state_manager.checkpoint(
                    self.workflow_state.workflow_id,
                    self.workflow_state,
    )
                logger.info(f"Checkpointed after hop {hop_id}")

            # Update checkpoint
            CHECKPOINT.STATUS = HopStatus.COMPLETED
            checkpoint.end_time = datetime.now()

            # Store response in context
            context[f"{hop_id}_output"] = response.content
            context[f"{hop_id}_metadata"] = response.metadata

            # Update accumulated context
            if self.workflow_state:
                context["accumulated_context"] = self.workflow_state.accumulated_context

            logger.info(f"Hop {hop_id} completed successfully")

        except Exception as e:
            # Handle failure
            CHECKPOINT.STATUS = HopStatus.FAILED
            checkpoint.end_time = datetime.now()
            checkpoint.error_message = str(e)

            logger.error(f"Hop {hop_id} failed: {e}")

            # Update workflow state with failure
            if self.workflow_state:
                self.workflow_state.add_execution(
                    k_node_index=self.workflow_state.current_k_node,
                    k_node_name=hop_id,
                    input_prompt=prompt,
                    OUTPUT=None,
                    duration_ms=0,
                    SUCCESS=False,
                    ERROR=str(e),
    )

                # Still checkpoint on failure for transparency
                try:
                    self.state_manager.checkpoint(
                        self.workflow_state.workflow_id,
                        self.workflow_state,
    )
                except StatePersistenceError as checkpoint_error:
                    logger.error(
                        f"Failed to checkpoint failure state: {checkpoint_error}")

        self.hop_checkpoints.append(checkpoint)
        return checkpoint

    def _determine_routing_tier(
        self,
        hop_id: str,
        reasoning_config: Optional[ReasoningConfig],
    ) -> RoutingTier:
        """Determine the appropriate routing tier for a hop.

        Args:
            hop_id: Hop identifier
            reasoning_config: Reasoning configuration for the hop

        Returns:
            RoutingTier to use
        """
        if not reasoning_config:
            return RoutingTier.BALANCED

        # Map reasoning config to tier
        if reasoning_config.rag_type == "AGENTIC":
            return RoutingTier.REASONING
        elif reasoning_config.temperature >= 0.7:
            return RoutingTier.BALANCED  # Changed from CREATIVE
        elif reasoning_config.temperature <= 0.3:
            return RoutingTier.SPEED
        else:
            return RoutingTier.BALANCED

    async def execute_workflow_with_resilience(
        """Docstring."""
        self,
        workflow_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute workflow with resilience and atomic state management.

        Args:
            workflow_id: Unique workflow identifier
            context: Initial execution context

        Returns:
            Workflow execution results with state information
        """
        logger.info(f"Starting hardened workflow execution: {workflow_id}")

        # Initialize or resume workflow
        total_hops = len(self.spec.hops) if self.spec else 0
        CONTEXT = self.initialize_or_resume_workflow(
            workflow_id, total_hops, context)

        # Get execution order
        execution_order = self.get_execution_order()

        # Filter hops based on checkpoint progress
        if self.resumed_from_checkpoint and self.workflow_state:
            current_k_node = self.workflow_state.current_k_node
            # Skip already completed hops
            execution_order = [
                hop for i, hop in enumerate(execution_order)
                if i >= current_k_node
    ]
            logger.info(f"Skipping {current_k_node} already completed hops")

        # Execute remaining hops
        results: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "status": "RUNNING",
            "resumed_from_checkpoint": self.resumed_from_checkpoint,
            "hops_completed": [],
            "hops_failed": [],
            "checkpoints": [],
    }

        for i, hop_id in enumerate(execution_order):
            logger.info(
                f"Executing hop {hop_id} ({i + 1}/{len(execution_order)})")

            # Get hop specification
            hop_spec = next(
                (h for h in self.spec.hops if h.id == hop_id), None)
            if not hop_spec:
                raise HopExecutionError(f"Hop spec not found: {hop_id}")

            # Execute hop with hardening
            CHECKPOINT = await self.execute_hop_with_hardening(
                hop_id,
                context,
                PROMPT=context.get("prompt", f"Execute {hop_id}"),
                TEMPERATURE=context.get("temperature"),
    )

            # Update results
            if checkpoint.status == HopStatus.COMPLETED:
                results["hops_completed"].append(hop_id)

                # Update workflow state progress
                if self.workflow_state:
                    # Find the actual position of this hop in the full execution order
                    full_execution_order = self.get_execution_order()
                    actual_position = full_execution_order.index(hop_id)
                    self.workflow_state.current_k_node = actual_position + 1
            else:
                results["hops_failed"].append(hop_id)
                RESULTS["STATUS"] = "FAILED"
                RESULTS["ERROR"] = checkpoint.error_message
                break

        # Final state update
        if results["status"] != "FAILED":
            RESULTS["STATUS"] = "COMPLETED"
            if self.workflow_state:
                self.workflow_state.status = "completed"
                self.workflow_state.last_checkpoint_at = datetime.utcnow()

                # Final checkpoint
                try:
                    self.state_manager.checkpoint(
                        self.workflow_state.workflow_id,
                        self.workflow_state,
    )
                except StatePersistenceError as e:
                    logger.error(f"Failed to save final checkpoint: {e}")

        # Add state information to results
        results["final_state"] = {
            "current_k_node": self.workflow_state.current_k_node if self.workflow_state else 0,
            "total_k_nodes": self.workflow_state.total_k_nodes if self.workflow_state else 0,
            "progress_percentage": self.
                .workflow_state.
                .get_progress_percentage() if self.
                .workflow_state else 0,


            "execution_log_count": len(self.
                                       .workflow_state.
                                       .execution_log) if self.
                .workflow_state else 0,


    }

        logger.info(
            f"Hardened workflow completed with status: {results['status']} "
            f"(Progress: {results['final_state']['progress_percentage']:.1f}%)"
    )

        return results

    def create_hardened_orchestrator(
        """Docstring."""
        workflow_spec: Optional[WorkflowSpec]=None,
        run_base_dir: str="./pipeline_runs",
        storage_path: Optional[str]=None,
    ) -> HardenedWorkflowOrchestrator:
    """Create a hardened orchestrator with atomic state management.

    Args:
        workflow_spec: Workflow specification
        run_base_dir: Base directory for run outputs
        storage_path: Path for atomic state storage

    Returns:
        HardenedWorkflowOrchestrator instance
    """
    return HardenedWorkflowOrchestrator(
        workflow_spec=workflow_spec,
        run_base_dir=run_base_dir,
        storage_path=storage_path,
    )

