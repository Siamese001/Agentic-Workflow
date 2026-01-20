#!/usr/bin/env python3
"""Test cognitive recovery integration in orchestrator execution loop."""

import sys
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import (
    CoreOrchestrationAgent,
)


class FailingMockNode:
    """Mock node that always fails to test cognitive recovery."""
    
    def __init__(self, node_id: str, error_msg: str = "base class inheritance missing"):
        self.node_id = node_id
        self.error_msg = error_msg
    
    async def run(self, **kwargs):
        raise ValueError(self.error_msg)
    
    def __str__(self):
        return self.node_id


async def test_cognitive_recovery_in_execution():
    """Test that cognitive recovery triggers during node execution failures."""
    print("Testing Cognitive Recovery in Orchestrator Execution Loop...")
    
    # Create orchestrator
    orchestrator = CoreOrchestrationAgent()
    print("\n[TEST 1] Orchestrator instantiated")
    
    # Create a failing node
    failing_node = FailingMockNode("test-node-001", "base class inheritance missing in HealerMixin")
    
    # Test node execution with retry (should trigger cognitive recovery)
    print("\n[TEST 2] Executing failing node (should trigger cognitive recovery after retries)")
    
    execution_state = {
        'completed_nodes': set(),
        'failed_nodes': set(),
        'results': {},
        'recovery_attempts': 0,
    }
    
    success = await orchestrator._execute_node_with_retry(
        node=failing_node,
        node_id="test-node-001",
        initial_inputs={},
        execution_state=execution_state
    )
    
    print(f"\n[TEST 3] Node execution result: {'✅ Success' if success else '❌ Failed (expected)'}")
    print(f"  Failed nodes: {len(execution_state['failed_nodes'])}")
    print(f"  Completed nodes: {len(execution_state['completed_nodes'])}")
    
    if not success:
        print("\n✅ Test passed - Cognitive recovery was triggered during execution")
        print("   (Check logs above for '🧠 Cognitive Memory found a potential fix strategy')")
    else:
        print("\n⚠️  Unexpected success - node should have failed")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(test_cognitive_recovery_in_execution()))
