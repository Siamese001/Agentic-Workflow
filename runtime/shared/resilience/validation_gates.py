"""
Validation Gates - Self-healing validation pipeline with atomic checkpointing.

Implements the ResilientValidationChain that manages sequential validation
gates with repair loops and progress persistence.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass, field

from .atomic_state_manager import AtomicStateManager, WorkflowState

logger = logging.getLogger(__name__)

@dataclass
class ValidationMetrics:
    """Metrics collected during validation chain execution."""
    total_gates: int = 0
    passed_gates: int = 0
    failed_gates: int = 0
    total_repairs: int = 0
    total_time_seconds: float = 0.0
    gate_times: Dict[str, float] = field(default_factory=dict)
    repair_counts: Dict[str, int] = field(default_factory=dict)
    oscillations_detected: int = 0
    timeouts: Dict[str, int] = field(default_factory=lambda: {"gate": 0, "repair": 0})

class SentinelDecision(BaseModel):
    """Decision returned by a validation Sentinel."""
    status: str = Field(..., description="PASS or FAIL")
    confidence: float = Field(..., description="Confidence score (0-1)")
    failure_reason: Optional[str] = Field(None, description="Reason for failure")
    retry_suggestion: Optional[str] = Field(None, description="Suggestion for retry/repair")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationGate(BaseModel):
    """A single checkpoint in the validation chain."""
    gate_name: str = Field(..., description="Unique identifier (e.g., 'SyntaxCheck').")
    rubric: str = Field(..., description="The specific criteria the Sentinel uses for this gate.")

    # Hardening config
    max_repair_attempts: int = Field(3,
        description="How many times to attempt repair before fatal failure.")
    fatal_on_fail: bool = Field(True,
        description="If True,
        failure stops the chain. If False,
        it logs a warning.")

    # Oscillation detection
    detect_oscillation: bool = Field(True,
        description="Detect if repair agent is oscillating between states.")
    oscillation_threshold: int = Field(3,
        description="Number of repeated failures before detecting oscillation.")

    # Timeout configuration
    gate_timeout_seconds: float = Field(60.0, description="Max time for gate validation (seconds).")
    repair_timeout_seconds: float = Field(120.0,
        description="Max time for each repair attempt (seconds).")

class GateHistory(BaseModel):
    """Tracks repair history for a gate to detect oscillation."""
    gate_name: str
    attempts: List[Dict[str, Any]] = Field(default_factory=list)
    last_failure_reasons: List[str] = Field(default_factory=list)

    def is_oscillating(self, threshold: int = 3) -> bool:
        """Check if repair is oscillating between failure states."""
        if len(self.last_failure_reasons) < threshold:
            return False

        # Check if the last N failures are all the same reason
        recent_failures = self.last_failure_reasons[-threshold:]
        return len(set(recent_failures)) == 1

class ChainFailureError(Exception):
    """Raised when a gate fails and repair attempts are exhausted."""
    pass

class ResilientValidationChain:
    """
    Manages sequential validation with self-healing capabilities.

    Features:
    - Sequential gate execution with repair loops
    - Atomic checkpointing after each successful gate
    - Oscillation detection to prevent infinite repair loops
    - Progress persistence for recovery from failures
    """

    def __init__(
        self,
        executor: Any,  # HardenedGeminiExecutor or similar
        state_manager: AtomicStateManager,
        workflow_id: str
    ):
        """Initialize validation chain.

        Args:
            executor: Hardened executor for running validation and repair
            state_manager: Atomic state manager for checkpointing
            workflow_id: Unique workflow identifier
        """
        self.executor = executor
        self.state_manager = state_manager
        self.workflow_id = workflow_id
        self.logger = logging.getLogger(f"ValidationChain-{workflow_id}")

        # Track gate histories for oscillation detection
        self._gate_histories: Dict[str, GateHistory] = {}

        # Metrics collection
        self.metrics = ValidationMetrics()

    async def _run_sentinel(self, content: str, gate: ValidationGate) -> SentinelDecision:
        """Execute the Sentinel K-Node for a specific gate.

        Args:
            content: Content to validate
            gate: Validation gate configuration

        Returns:
            Sentinel decision
        """
        # Build validation prompt
        messages = [
            {
                "role": "system",
                "content": "You are a validation Sentinel. Evaluate content against the given rubric."
            },
            {
                "role": "user",
                "content": f"Rubric: {gate.rubric}\n\nContent to validate:\n{content}"
            }
        ]

        # Use structured output for consistent decisions
        response_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["PASS", "FAIL"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "failure_reason": {"type": "string"},
                "retry_suggestion": {"type": "string"}
            },
            "required": ["status", "confidence"]
        }

        try:
            # Execute with hardened executor and timeout
            result = await asyncio.wait_for(
                self.executor.execute_k_node(
                    messages=messages,
                    response_schema=response_schema,
                    temperature=0.1  # Low temperature for consistent validation
                ),
                timeout=gate.gate_timeout_seconds
            )

            # Parse structured response
            import json
            decision_data = json.loads(result)

            return SentinelDecision(
                status=decision_data.get("status"),
                confidence=decision_data.get("confidence", 0.0),
                failure_reason=decision_data.get("failure_reason"),
                retry_suggestion=decision_data.get("retry_suggestion"),
                metadata={"gate_name": gate.gate_name}
            )

        except asyncio.TimeoutError:
            self.logger.error(f"Sentinel timeout for gate {gate.gate_name} after {gate.gate_timeout_seconds}s")
            self.metrics.timeouts["gate"] += 1
            return SentinelDecision(
                status="FAIL",
                confidence=0.0,
                failure_reason=f"Validation timeout after {gate.gate_timeout_seconds} seconds",
                retry_suggestion="Try with simpler content or increase timeout"
            )
        except Exception as e:
            self.logger.error(f"Sentinel execution failed for gate {gate.gate_name}: {e}")
            return SentinelDecision(
                status="FAIL",
                confidence=0.0,
                failure_reason=f"Execution error: {str(e)}",
                retry_suggestion="Retry with simpler content"
            )

    async def _attempt_repair(
        self,
        content: str,
        decision: SentinelDecision,
        gate: ValidationGate,
        repair_agent_func: Callable[[str, str, str, str], Awaitable[str]]
    ) -> str:
        """Attempt to repair content based on Sentinel feedback.

        Args:
            content: Original content
            decision: Sentinel decision with failure details
            gate: The gate that failed
            repair_agent_func: Async function that performs repair

        Returns:
            Repaired content
        """
        self.logger.info(
            f"🔧 Initiating repair for gate {gate.gate_name}. "
            f"Reason: {decision.failure_reason}"
        )

        try:
            # Call repair agent with timeout
            repaired_content = await asyncio.wait_for(
                repair_agent_func(
                    original_content=content,
                    feedback=decision.failure_reason or "Validation failed",
                    instruction=decision.retry_suggestion or "Fix the issues",
                    gate_rubric=gate.rubric  # Include rubric so repair knows what to fix
                ),
                timeout=gate.repair_timeout_seconds
            )
            return repaired_content

        except asyncio.TimeoutError:
            self.logger.error(
                f"Repair timeout for gate {gate.gate_name} after {gate.repair_timeout_seconds}s"
            )
            self.metrics.timeouts["repair"] += 1
            raise ChainFailureError(
                f"Repair agent timed out for gate {gate.gate_name}. "
                f"Consider increasing timeout or simplifying content."
            )
        except Exception as e:
            self.logger.error(f"Repair attempt failed: {e}")
            raise

    async def _checkpoint_gate_success(
        self,
        gate: ValidationGate,
        content: str,
        repair_attempts: int
    ) -> None:
        """Atomically checkpoint after successful gate completion.

        Args:
            gate: The gate that was passed
            content: Validated content
            repair_attempts: Number of repair attempts used
        """
        checkpoint_data = {
            "valid_content": content,
            "last_passed_gate": gate.gate_name,
            "repair_attempts": {
                gate.gate_name: repair_attempts
            },
            "gate_histories": {
                name: history.model_dump()
                for name, history in self._gate_histories.items()
            }
        }

        state = WorkflowState(
            workflow_id=self.workflow_id,
            current_step=f"GATE_PASSED_{gate.gate_name}",
            last_checkpoint_time=datetime.now(),
            data_payload=checkpoint_data,
            checksum=""  # Will be computed
        )

        await self.state_manager.commit_state(state)
        self.logger.info(f"✅ Checkpointed after gate {gate.gate_name}")

    async def _load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load last checkpoint to resume from failure.

        Returns:
            Checkpoint data or None if no checkpoint exists
        """
        try:
            state = await self.state_manager.load_state(self.workflow_id)
            if state:
                return state.data_payload
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")

        return None

    async def execute_chain(
        self,
        initial_content: str,
        gates: List[ValidationGate],
        repair_agent_func: Callable[[str, str, str, str], Awaitable[str]]
    ) -> str:
        """
        Execute the full validation pipeline.

        Args:
            initial_content: Initial content to validate
            gates: List of validation gates to execute
            repair_agent_func: Async function that repairs content

        Returns:
            Final validated (and potentially repaired) content

        Raises:
            ChainFailureError: If a fatal gate fails after all repair attempts
        """
        # Try to resume from checkpoint
        checkpoint = await self._load_checkpoint()
        current_content = initial_content
        start_from_gate = 0

        if checkpoint:
            current_content = checkpoint.get("valid_content", initial_content)
            last_passed = checkpoint.get("last_passed_gate")

            # Restore gate histories
            if "gate_histories" in checkpoint:
                for name, history_data in checkpoint["gate_histories"].items():
                    self._gate_histories[name] = GateHistory(**history_data)

            # Find where to resume
            if last_passed:
                for i, gate in enumerate(gates):
                    if gate.gate_name == last_passed:
                        start_from_gate = i + 1
                        break

            self.logger.info(f"Resuming from gate {start_from_gate}")

        # Execute gates
        chain_start_time = datetime.now()
        self.metrics.total_gates = len(gates)

        for gate_idx in range(start_from_gate, len(gates)):
            gate = gates[gate_idx]
            gate_start_time = datetime.now()
            self.logger.info(f"🚦 Entering Gate: {gate.gate_name}")

            # Initialize gate history
            if gate.gate_name not in self._gate_histories:
                self._gate_histories[gate.gate_name] = GateHistory(gate_name=gate.gate_name)

            history = self._gate_histories[gate.gate_name]

            # Validation loop with repair
            attempts = 0
            passed = False

            while attempts < gate.max_repair_attempts + 1:  # +1 for initial attempt
                # Run Sentinel
                decision = await self._run_sentinel(current_content, gate)

                # Record attempt
                history.attempts.append({
                    "attempt": attempts + 1,
                    "status": decision.status,
                    "reason": decision.failure_reason,
                    "timestamp": datetime.now().isoformat()
                })

                if decision.status == "PASS":
                    self.logger.info(f"✅ Gate {gate.gate_name} Passed (attempt {attempts + 1})")
                    self.metrics.passed_gates += 1
                    passed = True
                    break

                # Handle failure
                self.logger.warning(
                    f"❌ Gate {gate.gate_name} Failed. "
                    f"Attempt {attempts + 1}/{gate.max_repair_attempts + 1}"
                )

                # Track failure for oscillation detection
                if decision.failure_reason:
                    history.last_failure_reasons.append(decision.failure_reason)

                # Check for oscillation
                if gate.detect_oscillation and history.is_oscillating(gate.oscillation_threshold):
                    self.logger.error(
                        f"🔄 Oscillation detected in gate {gate.gate_name}. "
                        f"Same failure repeated {gate.oscillation_threshold} times."
                    )
                    self.metrics.oscillations_detected += 1
                    if gate.fatal_on_fail:
                        raise ChainFailureError(
                            f"Oscillation detected in gate {gate.gate_name}. "
                            f"Repair is stuck in a loop."
                        )
                    break

                # Check if we've exhausted attempts
                if attempts == gate.max_repair_attempts:  # No more repairs allowed
                    break

                # Attempt repair (only if we haven't exhausted attempts)
                try:
                    current_content = await self._attempt_repair(
                        current_content,
                        decision,
                        gate,
                        repair_agent_func
                    )
                    self.metrics.total_repairs += 1
                except Exception as e:
                    self.logger.error(f"Repair attempt failed: {e}")
                    # If repair fails, we may want to continue to next attempt or fail fast
                    if attempts == gate.max_repair_attempts - 1:  # Last repair attempt failed
                        self.logger.error("Last repair attempt failed, failing gate.")
                        break

                attempts += 1

            # Check if gate ultimately passed
            if not passed:
                self.metrics.failed_gates += 1
                if gate.fatal_on_fail:
                    raise ChainFailureError(
                        f"Validation failed at {gate.gate_name} after "
                        f"{attempts} repair attempts."
                    )
                else:
                    self.logger.warning(
                        f"⚠️ Non-fatal gate {gate.gate_name} failed. "
                        f"Proceeding with risk."
                    )

            # Record gate timing and repair count
            gate_end_time = datetime.now()
            gate_duration = (gate_end_time - gate_start_time).total_seconds()
            self.metrics.gate_times[gate.gate_name] = gate_duration
            self.metrics.repair_counts[gate.gate_name] = attempts

            # Checkpoint after successful gate
            await self._checkpoint_gate_success(gate, current_content, attempts)

        # Calculate total chain time
        chain_end_time = datetime.now()
        self.metrics.total_time_seconds = (chain_end_time - chain_start_time).total_seconds()

        # Log final metrics
        self.logger.info(
            f"🎯 Validation chain completed: "
            f"{self.metrics.passed_gates}/{self.metrics.total_gates} gates passed, "
            f"{self.metrics.total_repairs} repairs, "
            f"{self.metrics.total_time_seconds:.2f}s total"
        )

        return current_content

    def get_chain_status(self) -> Dict[str, Any]:
        """Get status of the validation chain.

        Returns:
            Status dictionary with gate histories and statistics
        """
        return {
            "workflow_id": self.workflow_id,
            "metrics": {
                "total_gates": self.metrics.total_gates,
                "passed_gates": self.metrics.passed_gates,
                "failed_gates": self.metrics.failed_gates,
                "total_repairs": self.metrics.total_repairs,
                "total_time_seconds": self.metrics.total_time_seconds,
                "oscillations_detected": self.metrics.oscillations_detected,
                "timeouts": self.metrics.timeouts
            },
            "gate_histories": {
                name: {
                    "attempts": len(history.attempts),
                    "last_failures": history.last_failure_reasons[-3:],
                    "is_oscillating": history.is_oscillating()
                }
                for name, history in self._gate_histories.items()
            }
        }

    def get_metrics(self) -> ValidationMetrics:
        """Get the validation metrics object.

        Returns:
            ValidationMetrics instance with all collected metrics
        """
        return self.metrics

# Factory function for creating common gate configurations
def create_standard_gates() -> List[ValidationGate]:
    """Create a standard set of validation gates.

    Returns:
        List of common validation gates
    """
    return [
        ValidationGate(
            gate_name="SyntaxCheck",
            rubric="Ensure strict JSON compliance and schema validity.",
            fatal_on_fail=True,
            max_repair_attempts=2
        ),
        ValidationGate(
            gate_name="SafetyCheck",
            rubric="Ensure no PII is leaked and tone is professional.",
            fatal_on_fail=True,
            max_repair_attempts=3
        ),
        ValidationGate(
            gate_name="QualityCheck",
            rubric="Ensure confidence score is above 0.8 and content meets quality standards.",
            fatal_on_fail=False,  # Allow proceeding with lower quality
            max_repair_attempts=5
        ),
        ValidationGate(
            gate_name="ComplianceCheck",
            rubric="Ensure content complies with legal and policy requirements.",
            fatal_on_fail=True,
            max_repair_attempts=2
        )
    ]

# Example repair agent function signature
async def default_repair_agent(
    original_content: str,
    feedback: str,
    instruction: str,
    gate_rubric: str
) -> str:
    """Default repair agent that fixes content based on feedback.

    Args:
        original_content: The content that failed validation
        feedback: Why the content failed
        instruction: Suggestion for fixing
        gate_rubric: The rubric that was used for validation

    Returns:
        Repaired content
    """
    # This would be implemented with an LLM call
    # Example implementation:
    messages = [
        {
            "role": "system",
            "content": "You are a repair agent. Fix content based on validation feedback."
        },
        {
            "role": "user",
            "content": f"""
            Original content:
            {original_content}

            Validation rubric:
            {gate_rubric}

            Failure reason:
            {feedback}

            Repair instruction:
            {instruction}

            Please provide the fixed content:
            """
        }
    ]

    # Would call executor here
    # return await executor.execute_k_node(messages=messages)
    return "Repaired content placeholder"
