#!/usr/bin/env python3
"""Simple test to check the first test case."""

import asyncio
import tempfile
from unittest.mock import AsyncMock

from runtime.shared.state import get_state_manager, reset_state_manager
from runtime.shared.routing.factory import reset_router
from apps_rg.L3_orchestration.hardened_orchestrator import create_hardened_orchestrator
from apps_rg.L3_orchestration.orchestrate_workflow import WorkflowSpec, HopSpec
from runtime.shared.agent_executor import AgentResponse


async def test_first_case():
    """Test the first case that's failing."""
    print("\n=== Test First Case ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Reset singletons
        reset_state_manager()
        reset_router()
        
        # Create workflow spec
        workflow_spec = WorkflowSpec(
            name="Test Resume Generation",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_k1.py", description="Executive Summary"),
                HopSpec(id="K.4", script="test_k4.py", description="Professional Headline"),
                HopSpec(id="K.5", script="test_k5.py", description="Experience Bullets"),
            ],
        )
        
        # Create hardened orchestrator
        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            run_base_dir=temp_dir,
            storage_path=temp_dir,
        )
        
        # Mock the router
        mock_responses = {
            "K.1": "Executive summary with strategic positioning and quantified achievements.",
            "K.4": "Senior Software Engineer | Cloud Architecture | Team Leadership",
            "K.5": "• Led migration of 50+ services to cloud infrastructure, reducing costs by 30%\n• Developed microservices architecture serving 1M+ requests daily",
        }
        
        call_count = {"count": 0}
        
        async def mock_execute_with_fallback(tier, prompt, temperature=None, **kwargs):
            call_count["count"] += 1
            hop_id = ["K.1", "K.4", "K.5"][call_count["count"] - 1]
            return AgentResponse(
                content=mock_responses.get(hop_id, "Default response"),
                finish_reason="stop",
                metadata={
                    "provider": "openai",
                    "model": "gpt-4",
                    "duration_ms": 150.0,
                    "tier": tier.value if hasattr(tier, 'value') else str(tier),
                },
            )
        
        orchestrator.router.execute_with_fallback = mock_execute_with_fallback
        
        # Test 1: New workflow execution
        print("\n--- New Workflow Execution ---")
        workflow_id = "test_workflow_001"
        context = {
            "prompt": "Test prompt",
            "temperature": 0.7,
        }
        
        results = await orchestrator.execute_workflow_with_resilience(
            workflow_id,
            context,
        )
        
        print(f"Status: {results['status']}")
        print(f"Resumed: {results['resumed_from_checkpoint']}")
        print(f"Hops completed: {len(results['hops_completed'])}")
        
        if results['status'] != 'COMPLETED':
            print(f"ERROR: Expected COMPLETED but got {results['status']}")
            if 'error' in results:
                print(f"Error: {results['error']}")


if __name__ == "__main__":
    asyncio.run(test_first_case())
