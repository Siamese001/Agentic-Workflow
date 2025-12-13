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


@dataclass
class SubatomicHopConfig:
    """Configuration for a Subatomic Hop."""
    hop_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    checkpoint_dir: Path = field(default=Path("./checkpoints"))
    enable_checkpoints: bool = True
    enable_observability: bool = True
    max_execution_time: float = 300.0  # 5 minutes default


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
                
                # Save checkpoint
                checkpoint = MicroCheckpoint(
                    hop_id=self.config.hop_id,
                    stage=stage,
                    partial_result=result,
                    context=self.context.copy(),
                    retry_count=retry_count
                )
                await self._save_checkpoint(checkpoint)
                
                # Stage completed successfully
                break
                
            except Exception as e:
                retry_count += 1
                self.stage_retry_counts[stage] = retry_count
                
                if retry_count > max_retries or stage not in self.config.retry_policy.retryable_stages:
                    # Save error checkpoint
                    error_checkpoint = MicroCheckpoint(
                        hop_id=self.config.hop_id,
                        stage=stage,
                        error=str(e),
                        context=self.context.copy(),
                        retry_count=retry_count - 1
                    )
                    await self._save_checkpoint(error_checkpoint)
                    
                    if isinstance(e, (InputValidationError, QualityGateFailure)):
                        raise
                    else:
                        raise StageExecutionError(f"Stage {stage} failed after {max_retries} retries: {e}")
                
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
        """Plan the execution (Chain of Thought)."""
        logger.debug(f"Think stage for hop {self.config.hop_id}")
        
        # For now, just prepare the execution plan
        # In a full implementation, this would use an LLM for planning
        plan = {
            "action": "execute_hop_function",
            "parameters": kwargs,
            "expected_output_type": "dict"
        }
        
        # Store plan in context for ACT stage
        self.context["execution_plan"] = plan
        
        return plan
    
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
        """Review and validate the output."""
        logger.debug(f"Critique stage for hop {self.config.hop_id}")
        
        raw_output = self.context.get("raw_output")
        
        # Basic validation
        if raw_output is None:
            raise QualityGateFailure("No output produced")
        
        # Validate output type
        if not isinstance(raw_output, (dict, list, str)):
            raise QualityGateFailure(f"Invalid output type: {type(raw_output)}")
        
        # Store validated output
        self.context["validated_output"] = raw_output
        
        return {
            "is_valid": True,
            "output_type": type(raw_output).__name__,
            "size": len(str(raw_output))
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
