"""Subatomic Hop Architecture - Breaking monolithic hops into atomic micro-stages.

This module implements the foundational architecture for the Brain Surgery phase,
transforming each hop from a single function execution into a state machine
with 5 distinct micro-stages, enabling granular error handling and recovery.
"""

import json
import logging
import time
import uuid
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import shutil
import asyncio
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .reflection_engine import (
    ReflectionEngine,
    ReflectionConfig,
    CritiqueResult,
    MutationRequest,
    get_reflection_engine,
    STANDARD_CRITERIA
)

logger = logging.getLogger(__name__)


class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    PRE_CHECK = "PRE_CHECK"     # Validate inputs and context
    THINK = "THINK"             # Plan the execution (CoT)
    ACT = "ACT"                 # Execute the tool/LLM call
    CRITIQUE = "CRITIQUE"       # Review and validate output
    COMMIT = "COMMIT"           # Write to state/memory


class HopState(Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEGOTIATING = "NEGOTIATING"  # For Phase 4


class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )


class MicroCheckpoint(BaseModel):
    """Checkpoint data for saving state between micro-stages."""
    hop_id: str
    stage: MicroStage
    partial_result: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    retry_count: int = Field(default=0)
    error: Optional[str] = None
    
    class Config:
        use_enum_values = True


class StageTransition(BaseModel):
    """Event for stage transitions."""
    hop_id: str
    from_stage: Optional[MicroStage]
    to_stage: MicroStage
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InputValidationError(Exception):
    """Raised when pre-check validation fails."""
    pass


class StageExecutionError(Exception):
    """Raised when a micro-stage execution fails."""
    pass


class QualityGateFailure(Exception):
    """Raised when critique stage fails repeatedly."""
    pass


class MutationRequired(Exception):
    """Raised when a DAG mutation is required."""
    def __init__(self, mutation_request: MutationRequest):
        self.mutation_request = mutation_request
        super().__init__(f"Mutation required: {mutation_request.reason}")


@dataclass
class SubatomicHopConfig:
    """Configuration for a Subatomic Hop."""
    hop_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    checkpoint_dir: Path = field(default=Path("./checkpoints"))
    enable_checkpoints: bool = True
    enable_observability: bool = True
    max_execution_time: float = 300.0  # 5 minutes default
    reflection_config: Optional[ReflectionConfig] = None
    critique_criteria: List[str] = field(default_factory=lambda: STANDARD_CRITERIA)


class SubatomicHop:
    """A hop broken into 5 atomic micro-stages with state management."""
    
    def __init__(
        self,
        hop_function: Callable,
        config: Optional[SubatomicHopConfig] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Subatomic Hop.
        
        Args:
            hop_function: The original function to execute
            config: Hop configuration
            initial_context: Initial context dictionary
        """
        self.hop_function = hop_function
        self.config = config or SubatomicHopConfig()
        self.context = initial_context or {}
        
        # Initialize reflection engine
        self.reflection_engine = get_reflection_engine(
            **self.config.reflection_config.dict() if self.config.reflection_config else {}
        )
        
        # State management
        self.current_stage: Optional[MicroStage] = None
        self.state: HopState = HopState.PENDING
        self.stage_history: List[StageTransition] = []
        self.checkpoints: Dict[MicroStage, MicroCheckpoint] = {}
        
        # Execution tracking
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.stage_retry_counts: Dict[MicroStage, int] = {
            stage: 0 for stage in MicroStage
        }
        
        # Critique loop tracking
        self.critique_loop_count = 0
        
        # DAG mutation support
        self.dag_manager: Optional[DAGManager] = None
        
        # Negotiation support
        self.node_negotiator: Optional[Any] = None
        self.negotiation_enabled: bool = True
        
        # Prompt injection support
        self.enable_prompt_injection: bool = True
        
        # Ensure checkpoint directory exists
        self.config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized SubatomicHop {self.config.hop_id}")
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the hop through all micro-stages.
        
        Args:
            **kwargs: Arguments to pass to the hop function
            
        Returns:
            Final result from the COMMIT stage
        """
        self.start_time = time.time()
        self.state = HopState.RUNNING
        
        try:
            # Check for existing checkpoint to resume from
            await self._load_checkpoint()
            
            # Execute stages in order
            stages = [
                MicroStage.PRE_CHECK,
                MicroStage.THINK,
                MicroStage.ACT,
                MicroStage.CRITIQUE,
                MicroStage.COMMIT
            ]
            
            # Find starting stage (resumes from checkpoint if exists)
            start_idx = 0
            if self.current_stage and self.current_stage in stages:
                start_idx = stages.index(self.current_stage)
            
            # Execute remaining stages
            for stage in stages[start_idx:]:
                await self._execute_stage(stage, **kwargs)
                
                # Check for timeout
                if time.time() - self.start_time > self.config.max_execution_time:
                    raise StageExecutionError(f"Hop timeout after {self.config.max_execution_time}s")
            
            self.state = HopState.COMPLETED
            self.end_time = time.time()
            
            # Return final result
            final_checkpoint = self.checkpoints.get(MicroStage.COMMIT)
            return final_checkpoint.partial_result or {}
            
        except Exception as e:
            self.state = HopState.FAILED
            self.end_time = time.time()
            logger.error(f"Hop {self.config.hop_id} failed: {e}")
            raise
    
    async def _execute_stage(self, stage: MicroStage, **kwargs) -> None:
        """Execute a specific micro-stage.
        
        Args:
            stage: The stage to execute
            **kwargs: Arguments for the stage
        """
        self._transition_to(stage)
        
        max_retries = self.config.retry_policy.max_retries
        retry_count = self.stage_retry_counts[stage]
        
        while retry_count <= max_retries:
            try:
                # Apply instructional injections for this stage
                if self.enable_prompt_injection:
                    kwargs = await self._apply_stage_injections(stage, kwargs)
                
                # Execute stage logic
                if stage == MicroStage.PRE_CHECK:
                    result = await self._pre_check(**kwargs)
                elif stage == MicroStage.THINK:
                    result = await self._think(**kwargs)
                elif stage == MicroStage.ACT:
                    result = await self._act(**kwargs)
                elif stage == MicroStage.CRITIQUE:
                    result = await self._critique(**kwargs)
                elif stage == MicroStage.COMMIT:
                    result = await self._commit(**kwargs)
                else:
                    raise ValueError(f"Unknown stage: {stage}")
                
                # Create checkpoint
                checkpoint = MicroCheckpoint(
                    stage=stage,
                    partial_result=result,
                    metadata=self.context.copy(),
                    timestamp=time.time()
                )
                
                await self._save_checkpoint(checkpoint)
                self.checkpoints[stage] = checkpoint
                
                # Stage completed successfully
                break
                
            except Exception as e:
                retry_count += 1
                self.stage_retry_counts[stage] = retry_count
                
                if retry_count > max_retries:
                    logger.error(f"Stage {stage} failed after {max_retries} retries: {e}")
                    raise StageExecutionError(f"Stage {stage} failed: {e}") from e
                
                # Apply retry delay
                delay = self.config.retry_policy.retry_delay
                if self.config.retry_policy.exponential_backoff:
                    delay *= (2 ** (retry_count - 1))
                
                logger.warning(f"Stage {stage} failed, retry {retry_count}/{max_retries} in {delay}s: {e}")
                await asyncio.sleep(delay)
    
    async def _pre_check(self, **kwargs) -> Dict[str, Any]:
        """Validate inputs and context."""
        logger.debug(f"Pre-check for hop {self.config.hop_id}")
        
        # Check required inputs
        if not kwargs:
            raise InputValidationError("No input provided")
        
        # Validate context
        if self.context is None:
            self.context = {}
        
        # Check for required context keys
        # This can be customized per hop type
        return {"valid": True, "inputs": list(kwargs.keys())}
    
    async def _think(self, **kwargs) -> Dict[str, Any]:
        """Plan the execution (Chain of Thought) with prompt injections."""
        logger.debug(f"Think stage for hop {self.config.hop_id}")
        
        # Create base plan
        plan = {
            "action": "execute_hop_function",
            "parameters": kwargs,
            "expected_output_type": "dict"
        }
        
        # Check if we have critique feedback to incorporate
        if "critique_feedback" in self.context:
            plan["feedback"] = self.context["critique_feedback"]
            plan["retry_attempt"] = self.critique_loop_count
            logger.info(f"Incorporating critique feedback: {self.context['critique_feedback']}")
        
        # Apply prompt injections if enabled
        if self.enable_prompt_injection:
            try:
                # Lazy import to avoid circular dependency
                from .prompt_injection_loader import enhance_prompt
                
                # Determine hop type from function name or context
                hop_type = self.context.get("hop_type", self.hop_function.__name__)
                
                # Create injection context
                injection_context = {
                    **kwargs,
                    **self.context,
                    "hop_id": self.config.hop_id,
                    "stage": "THINK"
                }
                
                # Extract content if available
                content = None
                if "input" in kwargs:
                    content = str(kwargs["input"])
                elif "data" in kwargs:
                    content = str(kwargs["data"])
                
                # Enhance plan with injections
                plan_str = json.dumps(plan, indent=2)
                enhanced_plan_str = enhance_prompt(
                    base_prompt=plan_str,
                    hop_type=hop_type,
                    stage="THINK",
                    context=injection_context,
                    content=content
                )
                
                # Parse back to dict (keeping original structure)
                try:
                    # Extract just the plan part (before injection metadata)
                    enhanced_plan_str = enhanced_plan_str.split("\n\n[INJECTIONS_APPLIED:")[0]
                    plan = json.loads(enhanced_plan_str)
                    
                    # Store injection info for logging
                    plan["prompt_injections_applied"] = True
                    
                except json.JSONDecodeError:
                    # Fallback to original plan if parsing fails
                    logger.warning("Failed to parse enhanced plan, using original")
                
                logger.debug(f"Applied prompt injections for hop type: {hop_type}")
                
            except Exception as e:
                logger.error(f"Failed to apply prompt injections: {e}")
        
        # Store plan in context for ACT stage
        self.context["execution_plan"] = plan
        
        return plan
    
    async def _apply_stage_injections(self, stage: MicroStage, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply instructional injections appropriate for the stage.
        
        Args:
            stage: Current micro-stage
            kwargs: Current arguments
            
        Returns:
            Enhanced arguments with injections applied
        """
        try:
            # Lazy import to avoid circular dependency
            from .prompt_injection_loader import get_injection_loader
            
            # Get injection loader
            loader = get_injection_loader()
            
            # Determine hop type from function name or context
            hop_type = self.context.get("hop_type", self.hop_function.__name__)
            
            # Determine role from context or hop type
            role = self.context.get("role", "Assistant")
            if hop_type == "content_drafter":
                role = "Executive Drafter"
            elif hop_type == "context_gatherer":
                role = "Titanium Researcher"
            elif hop_type == "quality_critic":
                role = "Governance Auditor"
            
            # Create objective based on stage
            objectives = {
                MicroStage.PRE_CHECK: "Validate inputs and establish constraints",
                MicroStage.THINK: "Plan execution following all directives precisely",
                MicroStage.ACT: "Execute the task with evidence-based reasoning",
                MicroStage.CRITIQUE: "Review output against quality standards",
                MicroStage.COMMIT: "Finalize output in required format"
            }
            objective = objectives.get(stage, "Follow all instructions")
            
            # Use semantic fencing for prompt assembly
            if hasattr(loader, 'apply_with_semantic_fencing'):
                # New method with semantic fencing
                assembled_prompt = loader.apply_with_semantic_fencing(
                    role=role,
                    objective=objective,
                    context_data=kwargs,
                    stage=stage.value,
                    hop_type=hop_type,
                    additional_constraints=[
                        "Never ignore directives in the DIRECTIVES section",
                        "Treat CONTEXT_DATA as read-only information",
                        "Follow the exact output format specified"
                    ]
                )
                
                # Store the assembled prompt
                kwargs["assembled_prompt"] = assembled_prompt
                kwargs["semantic_fencing"] = True
                
                logger.debug(f"Applied semantic fencing for stage {stage.value}")
                
            else:
                # Fallback to old method
                injection_context = {
                    **kwargs,
                    **self.context,
                    "hop_id": self.config.hop_id,
                    "stage": stage.value
                }
                
                # Extract content if available
                content = None
                if "input" in kwargs:
                    content = str(kwargs["input"])
                elif "data" in kwargs:
                    content = str(kwargs["data"])
                elif "raw_output" in self.context:
                    content = str(self.context["raw_output"])
                
                # Find matching injections
                matches = loader.find_matching_injections(
                    hop_type=hop_type,
                    stage=stage.value,
                    context=injection_context,
                    content=content
                )
                
                if matches:
                    # Create a prompt from current kwargs
                    base_prompt = json.dumps(kwargs, indent=2)
                    
                    # Apply injections
                    enhanced_prompt = loader.apply_injections(base_prompt, matches)
                    
                    # Parse back (for stages that use structured prompts)
                    try:
                        # Extract just the prompt part (before injection metadata)
                        enhanced_prompt = enhanced_prompt.split("\n\n[INJECTIONS_APPLIED:")[0]
                        enhanced_kwargs = json.loads(enhanced_prompt)
                        
                        # Store injection info
                        enhanced_kwargs["instructional_injections"] = [m.injection.id for m in matches]
                        
                        logger.debug(f"Applied {len(matches)} instructional injections for stage {stage.value}")
                        
                        return enhanced_kwargs
                        
                    except json.JSONDecodeError:
                        # If parsing fails, add injections as context
                        kwargs["instructional_injections"] = {
                            "applied": True,
                            "count": len(matches),
                            "types": [m.injection.type for m in matches]
                        }
                        logger.warning("Failed to parse enhanced kwargs, keeping original with injection metadata")
            
            return kwargs
            
        except Exception as e:
            logger.error(f"Failed to apply stage injections: {e}")
            return kwargs
    
    async def _act(self, **kwargs) -> Dict[str, Any]:
        """Execute the actual hop function."""
        logger.debug(f"Act stage for hop {self.config.hop_id}")
        
        # Execute the hop function
        if asyncio.iscoroutinefunction(self.hop_function):
            result = await self.hop_function(**kwargs)
        else:
            result = self.hop_function(**kwargs)
        
        # Store result in context
        self.context["raw_output"] = result
        
        return {"output": result}
    
    async def _critique(self, **kwargs) -> Dict[str, Any]:
        """Review and validate the output using Reflection Engine."""
        logger.debug(f"Critique stage for hop {self.config.hop_id}")
        
        raw_output = self.context.get("raw_output")
        
        # Basic validation
        if raw_output is None:
            raise QualityGateFailure("No output produced")
        
        # Use Reflection Engine for validation
        critique_result = await self.reflection_engine.evaluate(
            content=raw_output,
            criteria=self.config.critique_criteria,
            context={
                "hop_id": self.config.hop_id,
                "stage": "CRITIQUE",
                "retry_count": self.critique_loop_count
            }
        )
        
        # Check if validation passed
        if not critique_result.is_valid:
            self.critique_loop_count += 1
            
            # Check if a mutation is requested
            if critique_result.mutation_request:
                logger.info(f"Mutation requested: {critique_result.mutation_request.reason}")
                
                # Pause current hop
                self.state = HopState.PAUSED
                
                # Raise MutationRequired to trigger DAG mutation
                raise MutationRequired(critique_result.mutation_request)
            
            # Check if we've exceeded max critique loops
            if self.critique_loop_count > self.reflection_engine.config.max_critique_loops:
                raise QualityGateFailure(
                    f"Failed quality validation after {self.critique_loop_count} attempts. "
                    f"Last error: {critique_result.critique_reasoning}"
                )
            
            # Inject suggested fix into context for retry
            if critique_result.suggested_fix:
                self.context["critique_feedback"] = critique_result.suggested_fix
                logger.warning(f"Critique failed, retrying with feedback: {critique_result.suggested_fix}")
            
            # Raise to trigger retry
            raise QualityGateFailure(
                f"Quality validation failed: {critique_result.critique_reasoning}"
            )
        
        # Store validated output
        self.context["validated_output"] = raw_output
        self.context["critique_result"] = critique_result.dict()
        
        return {
            "is_valid": True,
            "output_type": type(raw_output).__name__,
            "size": len(str(raw_output)),
            "confidence": critique_result.confidence_score,
            "critique_loops": self.critique_loop_count
        }
    
    async def _commit(self, **kwargs) -> Dict[str, Any]:
        """Write to state/memory with atomic write pattern."""
        logger.debug(f"Commit stage for hop {self.config.hop_id}")
        
        validated_output = self.context.get("validated_output")
        
        if validated_output is None:
            raise StageExecutionError("No validated output to commit")
        
        # Atomic write pattern
        if self.config.enable_checkpoints:
            # Write to temporary file first
            temp_file = self.config.checkpoint_dir / f"{self.config.hop_id}_final.tmp"
            final_file = self.config.checkpoint_dir / f"{self.config.hop_id}_final.json"
            
            try:
                with open(temp_file, 'w') as f:
                    json.dump(validated_output, f, indent=2)
                
                # Verify file was written correctly
                with open(temp_file, 'r') as f:
                    loaded = json.load(f)
                    if loaded != validated_output:
                        raise IOError("Verification failed")
                
                # Atomic rename
                shutil.move(str(temp_file), str(final_file))
                
                logger.debug(f"Committed result to {final_file}")
                
            except Exception as e:
                # Clean up temp file if it exists
                if temp_file.exists():
                    temp_file.unlink()
                raise StageExecutionError(f"Failed to commit result: {e}")
        
        return {"committed": True, "result": validated_output}
    
    def _transition_to(self, stage: MicroStage) -> None:
        """Transition to a new stage and log the event."""
        from_stage = self.current_stage
        self.current_stage = stage
        
        # Log structured event
        if self.config.enable_observability:
            transition = StageTransition(
                hop_id=self.config.hop_id,
                from_stage=from_stage,
                to_stage=stage
            )
            self.stage_history.append(transition)
            
            logger.info(
                "STAGE_TRANSITION",
                extra={
                    "event": "STAGE_TRANSITION",
                    "hop_id": self.config.hop_id,
                    "from": from_stage.value if from_stage else None,
                    "to": stage.value,
                    "timestamp": transition.timestamp
                }
            )
    
    async def _save_checkpoint(self, checkpoint: MicroCheckpoint) -> None:
        """Save a checkpoint to disk."""
        if not self.config.enable_checkpoints:
            return
        
        self.checkpoints[checkpoint.stage] = checkpoint
        
        checkpoint_file = self.config.checkpoint_dir / f"{self.config.hop_id}_{checkpoint.stage.value}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.dict(), f, indent=2, default=str)
        
        logger.debug(f"Saved checkpoint for stage {checkpoint.stage.value}")
    
    async def _load_checkpoint(self) -> None:
        """Load the most recent checkpoint to resume from."""
        if not self.config.enable_checkpoints:
            return
        
        # Find the most recent checkpoint
        latest_checkpoint = None
        latest_time = 0
        
        for checkpoint_file in self.config.checkpoint_dir.glob(f"{self.config.hop_id}_*.json"):
            if checkpoint_file.name.endswith("_final.json"):
                continue  # Skip final result files
            
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    checkpoint = MicroCheckpoint(**data)
                    
                    if checkpoint.timestamp > latest_time:
                        latest_time = checkpoint.timestamp
                        latest_checkpoint = checkpoint
            except Exception as e:
                logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")
        
        if latest_checkpoint:
            self.current_stage = latest_checkpoint.stage
            self.context = latest_checkpoint.context
            self.stage_retry_counts[latest_checkpoint.stage] = latest_checkpoint.retry_count
            
            logger.info(f"Resumed hop {self.config.hop_id} from stage {latest_checkpoint.stage.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the hop."""
        return {
            "hop_id": self.config.hop_id,
            "state": self.state.value,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (self.end_time or time.time()) - (self.start_time or 0),
            "retry_counts": {k.value: v for k, v in self.stage_retry_counts.items()},
            "stage_history": [
                {
                    "from": t.from_stage.value if t.from_stage else None,
                    "to": t.to_stage.value,
                    "timestamp": t.timestamp
                }
                for t in self.stage_history
            ]
        }
    
    def cleanup(self) -> None:
        """Clean up checkpoints and temporary files."""
        if not self.config.enable_checkpoints:
            return
        
        # Remove checkpoint files
        for checkpoint_file in self.config.checkpoint_dir.glob(f"{self.config.hop_id}_*.json"):
            try:
                checkpoint_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup {checkpoint_file}: {e}")
        
        logger.debug(f"Cleaned up hop {self.config.hop_id}")
    
    async def request_upstream_change(
        self,
        upstream_hop_id: str,
        change_request: str,
        reason: str,
        **kwargs
    ):
        """Request a change from an upstream node.
        
        Args:
            upstream_hop_id: ID of upstream hop
            change_request: What to change
            reason: Why change is needed
            **kwargs: Additional context
            
        Returns:
            NegotiationResult
        """
        if not self.negotiation_enabled:
            raise RuntimeError("Negotiation not enabled for this hop")
        
        # Lazy import to avoid circular dependency
        from .node_negotiator import get_node_negotiator, request_upstream_change
        
        if not self.node_negotiator:
            self.node_negotiator = get_node_negotiator()
        
        return await request_upstream_change(
            downstream_hop=self,
            upstream_hop_id=upstream_hop_id,
            change_request=change_request,
            reason=reason,
            **kwargs
        )
    
    async def send_negotiation_message(
        self,
        to_hop_id: str,
        message_type: str,
        payload: str,
        **kwargs
    ) -> bool:
        """Send a negotiation message to another hop.
        
        Args:
            to_hop_id: ID of target hop
            message_type: Type of message
            payload: Message content
            **kwargs: Additional context
            
        Returns:
            True if sent successfully
        """
        if not self.negotiation_enabled:
            return False
        
        # Lazy import to avoid circular dependency
        from .node_negotiator import get_node_negotiator
        
        if not self.node_negotiator:
            self.node_negotiator = get_node_negotiator()
        
        return await self.node_negotiator.send_feedback(
            from_hop=self,
            to_hop_id=to_hop_id,
            message_type=message_type,
            payload=payload,
            context=kwargs
        )
    
    def handle_negotiation_request(self, request: Dict[str, Any]) -> None:
        """Handle a negotiation request from downstream.
        
        Args:
            request: Negotiation request details
        """
        if not self.negotiation_enabled:
            logger.warning(f"Ignoring negotiation request on {self.config.hop_id}")
            return
        
        # Store request in context
        self.context["negotiation_request"] = request
        
        # Log negotiation
        if "negotiation_log" not in self.context:
            self.context["negotiation_log"] = []
        
        self.context["negotiation_log"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "RECEIVED",
            "from": request.get("from_hop"),
            "message": request.get("request")
        })
        
        logger.info(f"Hop {self.config.hop_id} received negotiation request")


# Factory function for creating subatomic hops
def create_subatomic_hop(
    hop_function: Callable,
    config: Optional[SubatomicHopConfig] = None,
    **kwargs
) -> SubatomicHop:
    """Create a SubatomicHop from a regular function.
    
    Args:
        hop_function: The function to wrap
        config: Optional configuration
        **kwargs: Additional context
        
    Returns:
        Configured SubatomicHop instance
    """
    return SubatomicHop(
        hop_function=hop_function,
        config=config,
        initial_context=kwargs
    )


# Decorator for converting functions to subatomic hops
def subatomic_hop(config: Optional[SubatomicHopConfig] = None):
    """Decorator to convert a function into a SubatomicHop.
    
    Args:
        config: Optional configuration for the hop
        
    Returns:
        Decorated function that returns a SubatomicHop
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> SubatomicHop:
            return create_subatomic_hop(
                hop_function=func,
                config=config,
                **kwargs
            )
        return wrapper
    return decorator
