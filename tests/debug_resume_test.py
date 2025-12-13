#!/usr/bin/env python3
"""Debug test for resume functionality."""

import asyncio
import tempfile


async def test_resume_debug():
    """Docstring."""
import logging

logger = logging.getLogger(__name__)

    """Debug the resume functionality."""
    logger.info("\n=== Debug Resume Test ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Reset singletons
        reset_state_manager()

        # Create workflow spec
        workflow_spec = WorkflowSpec(
            name="Debug Test",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test.py", description="Step 1"),
                HopSpec(id="K.2", script="test.py", description="Step 2"),
            ],
        )

        # Create first orchestrator and run to completion
        logger.info("\n--- First run ---")
        orchestrator1 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            run_base_dir=temp_dir,
            storage_path=temp_dir,
        )

        # Mock router
        async def mock_execute(tier, prompt, **kwargs):
                """Docstring."""
            return AgentResponse(
                content="Response",
                finish_reason="stop",
                metadata={"provider": "openai"},
            )

        orchestrator1.router.execute_with_fallback = mock_execute

        results1 = await orchestrator1.execute_workflow_with_resilience(
            "debug_test",
            {"prompt": "Test"},
        )
        logger.info(f"First run status: {results1['status']}")
        logger.info(f"First run resumed: {results1['resumed_from_checkpoint']}")

        # Check state
        state_manager = get_state_manager()
        state = state_manager.resume_workflow("debug_test")
        logger.info(f"State after first run: current_k_node={state.current_k_node if state else 'Non
    e'}")

        # Create second orchestrator
        logger.info("\n--- Second run (should resume) ---")
        orchestrator2 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            run_base_dir=temp_dir,
            storage_path=temp_dir,
        )
        orchestrator2.router.execute_with_fallback = mock_execute

        # Check if state manager is the same instance
        logger.info(f"Same state manager instance: {orchestrator1.state_manager is orchestrator2.sta
    te_manager}")

        results2 = await orchestrator2.execute_workflow_with_resilience(
            "debug_test",
            {"prompt": "Test"},
        )
        logger.info(f"Second run status: {results2['status']}")
        logger.info(f"Second run resumed: {results2['resumed_from_checkpoint']}")

if __name__ == "__main__":
    asyncio.run(test_resume_debug())
