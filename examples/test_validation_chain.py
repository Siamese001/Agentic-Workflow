"""
Test and demonstration of the ResilientValidationChain.

Shows how the self-healing validation pipeline works with
atomic checkpointing and oscillation detection.
import logging

logger = logging.getLogger(__name__)

"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

# Mock dependencies for demonstration
class MockExecutor:
    """Mock executor for testing."""

    def __init__(self):
        self.call_count = 0

    async def execute_k_node(self, messages: List[Dict], **kwargs) -> str:
        """Mock execution that simulates validation responses."""
        self.call_count += 1

        # Extract the rubric from the user message
        user_content = messages[-1]["content"]
        rubric_start = user_content.find("Rubric:") + 8
        rubric_end = user_content.find("\n\nContent to validate:")
        rubric = user_content[rubric_start:rubric_end].strip()

        # Simulate different responses based on rubric
        if "Syntax" in rubric:
            # Fail first time, pass on retry
            if self.call_count <= 1:
                return json.dumps({
                    "status": "FAIL",
                    "confidence": 0.3,
                    "failure_reason": "Invalid JSON format",
                    "retry_suggestion": "Fix JSON syntax and ensure proper escaping"
                })
            else:
                return json.dumps({
                    "status": "PASS",
                    "confidence": 0.95
                })

        elif "Safety" in rubric:
            # Fail twice, pass on third attempt
            if self.call_count <= 2:
                return json.dumps({
                    "status": "FAIL",
                    "confidence": 0.2,
                    "failure_reason": "Contains potential PII",
                    "retry_suggestion": "Remove or mask any personal identifiers"
                })
            else:
                return json.dumps({
                    "status": "PASS",
                    "confidence": 0.88
                })

        elif "Quality" in rubric:
            # Oscillate to demonstrate detection
            if self.call_count % 2 == 0:
                return json.dumps({
                    "status": "FAIL",
                    "confidence": 0.6,
                    "failure_reason": "Confidence score below 0.8",
                    "retry_suggestion": "Improve content quality and detail"
                })
            else:
                return json.dumps({
                    "status": "FAIL",
                    "confidence": 0.7,
                    "failure_reason": "Confidence score below 0.8",
                    "retry_suggestion": "Add more specific details and examples"
                })

        return json.dumps({
            "status": "PASS",
            "confidence": 0.9
        })

class MockStateManager:
    """Mock state manager for testing."""

    def __init__(self):
        self.states = {}
        self.checkpoints = []

    async def load_state(self, workflow_id: str) -> Any:
        """Load state from mock storage."""
        return self.states.get(workflow_id)

    async def commit_state(self, state: Any) -> None:
        """Commit state to mock storage."""
        self.states[state.workflow_id] = state
        self.checkpoints.append({
            "workflow_id": state.workflow_id,
            "step": state.current_step,
            "timestamp": datetime.now()
        })
        logger.info(f"  💾 Checkpointed: {state.current_step}")

async def mock_repair_agent(
    original_content: str,
    feedback: str,
    instruction: str,
    gate_rubric: str
) -> str:
    """Mock repair agent that simulates content fixes."""
    logger.info(f"    🔧 Repairing: {feedback[:50]}...")

    # Simulate different repairs based on feedback
    if "JSON" in feedback:
        return '{"name": "John Doe", "role": "Software Engineer", "experience": 5}'
    elif "PII" in feedback:
        return '{"name": "J.D.", "role": "Software Engineer", "experience": 5}'
    else:
        return original_content + " [IMPROVED]"

async def demonstrate_validation_chain():
    """Demonstrate the ResilientValidationChain."""
    logger.info("\n=== DEMONSTRATION: ResilientValidationChain ===\n")

    # Import the validation chain components
    from runtime.shared.resilience.validation_gates import (
        ResilientValidationChain,
        ValidationGate,
        create_standard_gates,
        ChainFailureError
    )

    # Create mock components
    executor = MockExecutor()
    state_manager = MockStateManager()
    workflow_id = "demo_workflow_001"

    # Create validation chain
    chain = ResilientValidationChain(executor, state_manager, workflow_id)

    # Define gates
    gates = [
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
            rubric="Ensure confidence score is above 0.8.",
            fatal_on_fail=False,
            max_repair_attempts=5,
            detect_oscillation=True,
            oscillation_threshold=3
        )
    ]

    logger.info("Validation Gates:")
    for gate in gates:
        logger.info(f"  - {gate.gate_name}: {gate.rubric[:50]}...")

    # Initial content
    initial_content = '{"name": "John Doe", "email": "john@example.com"}'
    logger.info(f"\nInitial content: {initial_content}")

    # Execute the chain
    logger.info("\n--- Executing Validation Chain ---\n")

    try:
        final_content = await chain.execute_chain(
            initial_content=initial_content,
            gates=gates,
            repair_agent_func=mock_repair_agent
        )

        logger.info(f"\n✅ Chain completed successfully!")
        logger.info(f"Final content: {final_content}")

        # Show checkpoints
        logger.info(f"\nCheckpoints created: {len(state_manager.checkpoints)}")
        for i, checkpoint in enumerate(state_manager.checkpoints, 1):
            logger.info(f"  {i}. {checkpoint['step']}")

        # Show chain status
        status = chain.get_chain_status()
        logger.info(f"\nChain Status:")
        for gate_name, info in status["gate_histories"].items():
            logger.info(f"  {gate_name}:")
            logger.info(f"    Attempts: {info['attempts']}")
            logger.info(f"    Oscillating: {info['is_oscillating']}")

    except ChainFailureError as e:
        logger.info(f"\n❌ Chain failed: {e}")

    except Exception as e:
        logger.info(f"\n⚠️ Unexpected error: {e}")

async def demonstrate_checkpoint_recovery():
    """Demonstrate recovery from checkpoint after failure."""
    logger.info("\n=== DEMONSTRATION: Checkpoint Recovery ===\n")

        ResilientValidationChain,
        ValidationGate,
        ChainFailureError
    )

    # Create components
    executor = MockExecutor()
    state_manager = MockStateManager()
    workflow_id = "recovery_demo_001"

    # Simulate a previous checkpoint
    from runtime.shared.resilience.atomic_state_manager import WorkflowState
    checkpoint_state = WorkflowState(
        workflow_id=workflow_id,
        current_step="GATE_PASSED_SyntaxCheck",
        last_checkpoint_time=datetime.now(),
        data_payload={
            "valid_content": '{"name": "J.D.", "role": "Software Engineer"}',
            "last_passed_gate": "SyntaxCheck",
            "repair_attempts": {"SyntaxCheck": 1}
        },
        checksum=""
    )

    # Pre-populate state manager with checkpoint
    await state_manager.commit_state(checkpoint_state)

    logger.info("Simulating recovery from checkpoint...")
    logger.info(f"Last checkpoint: {checkpoint_state.current_step}")
    logger.info(f"Content: {checkpoint_state.data_payload['valid_content']}")

    # Create chain with remaining gates
    chain = ResilientValidationChain(executor, state_manager, workflow_id)

    gates = [
        ValidationGate(
            gate_name="SafetyCheck",
            rubric="Ensure no PII is leaked.",
            fatal_on_fail=True,
            max_repair_attempts=2
        ),
        ValidationGate(
            gate_name="QualityCheck",
            rubric="Ensure high quality content.",
            fatal_on_fail=False,
            max_repair_attempts=2
        )
    ]

    # Execute - should resume from SafetyCheck
    logger.info("\n--- Resuming from Checkpoint ---\n")

    try:
        final_content = await chain.execute_chain(
            initial_content="dummy",  # Won't be used due to checkpoint
            gates=gates,
            repair_agent_func=mock_repair_agent
        )

        logger.info(f"\n✅ Recovery successful!")
        logger.info(f"Final content: {final_content}")

    except Exception as e:
        logger.info(f"\n❌ Recovery failed: {e}")

async def demonstrate_oscillation_detection():
    """Demonstrate oscillation detection in repair loops."""
    logger.info("\n=== DEMONSTRATION: Oscillation Detection ===\n")

        ResilientValidationChain,
        ValidationGate,
        ChainFailureError
    )

    # Create executor that always returns the same failure
    class OscillatingExecutor:
        async def execute_k_node(self, messages: List[Dict], **kwargs) -> str:
            return json.dumps({
                "status": "FAIL",
                "confidence": 0.5,
                "failure_reason": "Same error every time",
                "retry_suggestion": "Try again"
            })

    executor = OscillatingExecutor()
    state_manager = MockStateManager()
    workflow_id = "oscillation_demo"

    chain = ResilientValidationChain(executor, state_manager, workflow_id)

    # Create gate with oscillation detection
    gate = ValidationGate(
        gate_name="OscillatingGate",
        rubric="A gate that will cause oscillation.",
        fatal_on_fail=True,
        max_repair_attempts=5,
        detect_oscillation=True,
        oscillation_threshold=3
    )

    logger.info("Testing oscillation detection...")
    logger.info(f"Oscillation threshold: {gate.oscillation_threshold}")

    try:
        await chain.execute_chain(
            initial_content="test content",
            gates=[gate],
            repair_agent_func=mock_repair_agent
        )

    except ChainFailureError as e:
        logger.info(f"\n✅ Oscillation detected and handled!")
        logger.info(f"Error: {e}")

        # Show chain status
        status = chain.get_chain_status()
        history = status["gate_histories"]["OscillatingGate"]
        logger.info(f"\nGate History:")
        logger.info(f"  Total attempts: {history['attempts']}")
        logger.info(f"  Last failures: {history['last_failures']}")

async def demonstrate_standard_gates():
    """Demonstrate the standard gate configurations."""
    logger.info("\n=== DEMONSTRATION: Standard Gates ===\n")

    from runtime.shared.resilience.validation_gates import create_standard_gates

    # Get standard gates
    gates = create_standard_gates()

    logger.info("Standard Validation Gates:")
    for gate in gates:
        logger.info(f"\n  🚦 {gate.gate_name}")
        logger.info(f"     Rubric: {gate.rubric}")
        logger.info(f"     Fatal: {gate.fatal_on_fail}")
        logger.info(f"     Max Repairs: {gate.max_repair_attempts}")
        logger.info(f"     Oscillation Detection: {gate.detect_oscillation}")

async def main():
    """Run all demonstrations."""
    logger.info("=" * 80)
    logger.info("RESILIENT VALIDATION CHAIN DEMONSTRATION")
    logger.info("Self-Healing Pipeline with Atomic Checkpointing")
    logger.info("=" * 80)

    await demonstrate_validation_chain()
    await demonstrate_checkpoint_recovery()
    await demonstrate_oscillation_detection()
    await demonstrate_standard_gates()

    logger.info("\n" + "=" * 80)
    logger.info("DEMONSTRATION COMPLETE")
    logger.info("\nKey Features Demonstrated:")
    logger.info("✓ Self-healing validation loops")
    logger.info("✓ Atomic checkpointing after each gate")
    logger.info("✓ Oscillation detection to prevent infinite loops")
    logger.info("✓ Recovery from checkpoints after failures")
    logger.info("✓ Configurable gate behaviors")
    logger.info("✓ Progress persistence and resume")
    logger.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
