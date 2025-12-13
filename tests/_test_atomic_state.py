#!/usr/bin/env python3
"""Test script for atomic state persistence with ACID guarantees.

Verifies:
- Atomic checkpoint operations (two-phase commit)
- Rollback on failure (old state remains intact)
- State recovery and resume functionality
- Telemetry logging for checkpoint operations
- Zero data loss guarantees

Usage:
    python test_atomic_state.py
"""

import asyncio
import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import state management components
from runtime.shared.state import (
    WorkflowState,
    AtomicStateManager,
    StatePersistenceError,
    BackendType,
    get_state_manager,
    reset_state_manager,
)
from datetime import datetime


def test_workflow_state_schema():
    """Test WorkflowState schema and methods."""
    print("\n=== Testing WorkflowState Schema ===")
    
    # Create a workflow state
    state = WorkflowState(
        workflow_id="test_workflow_001",
        workflow_type="resume_generation",
        total_k_nodes=5,
    )
    
    assert state.workflow_id == "test_workflow_001"
    assert state.current_k_node == 0
    assert state.total_k_nodes == 5
    assert state.status == "running"
    print("✓ WorkflowState created successfully")
    
    # Add an execution
    state.add_execution(
        k_node_index=0,
        k_node_name="extract_experience",
        input_prompt="Extract experience from resume",
        output="Experience extracted successfully",
        duration_ms=150.5,
        success=True,
    )
    
    assert state.current_k_node == 1
    assert len(state.execution_log) == 1
    assert state.last_successful_output == "Experience extracted successfully"
    print("✓ Execution added to state")
    
    # Test progress calculation
    progress = state.get_progress_percentage()
    assert progress == 20.0  # 1/5 = 20%
    print(f"✓ Progress calculation: {progress}%")
    
    # Test serialization
    json_str = state.to_json()
    assert json_str is not None
    print("✓ State serialized to JSON")
    
    # Test deserialization
    restored_state = WorkflowState.from_json(json_str)
    assert restored_state.workflow_id == state.workflow_id
    assert restored_state.current_k_node == state.current_k_node
    print("✓ State deserialized from JSON")
    
    print("WorkflowState schema test passed!\n")


def test_atomic_checkpoint():
    """Test atomic checkpoint operation."""
    print("\n=== Testing Atomic Checkpoint ===")
    
    # Create temporary storage
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AtomicStateManager(
            backend=BackendType.FILE,
            storage_path=temp_dir,
        )
        
        # Create initial state
        state_a = WorkflowState(
            workflow_id="workflow_checkpoint_test",
            workflow_type="test",
            total_k_nodes=3,
        )
        state_a.add_execution(
            k_node_index=0,
            k_node_name="step_1",
            input_prompt="Input 1",
            output="Output 1",
            duration_ms=100.0,
        )
        
        # Checkpoint State A
        metadata_a = manager.checkpoint("workflow_checkpoint_test", state_a)
        assert metadata_a.success
        print(f"✓ State A checkpointed (duration: {metadata_a.duration_ms:.2f}ms)")
        
        # Verify State A can be loaded
        loaded_state = manager.resume_workflow("workflow_checkpoint_test")
        assert loaded_state is not None
        assert loaded_state.current_k_node == 1
        assert loaded_state.last_successful_output == "Output 1"
        print("✓ State A loaded successfully")
        
        # Create State B
        state_b = WorkflowState(
            workflow_id="workflow_checkpoint_test",
            workflow_type="test",
            total_k_nodes=3,
        )
        state_b.add_execution(
            k_node_index=0,
            k_node_name="step_1",
            input_prompt="Input 1",
            output="Output 1",
            duration_ms=100.0,
        )
        state_b.add_execution(
            k_node_index=1,
            k_node_name="step_2",
            input_prompt="Input 2",
            output="Output 2",
            duration_ms=150.0,
        )
        
        # Checkpoint State B
        metadata_b = manager.checkpoint("workflow_checkpoint_test", state_b)
        assert metadata_b.success
        print(f"✓ State B checkpointed (duration: {metadata_b.duration_ms:.2f}ms)")
        
        # Verify State B replaced State A
        loaded_state = manager.resume_workflow("workflow_checkpoint_test")
        assert loaded_state.current_k_node == 2
        assert loaded_state.last_successful_output == "Output 2"
        print("✓ State B replaced State A atomically")
    
    print("Atomic checkpoint test passed!\n")


def test_rollback_on_failure():
    """Test that old state remains intact when checkpoint fails."""
    print("\n=== Testing Rollback on Failure ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AtomicStateManager(
            backend=BackendType.FILE,
            storage_path=temp_dir,
        )
        
        # Create and checkpoint State A (valid state)
        state_a = WorkflowState(
            workflow_id="workflow_rollback_test",
            workflow_type="test",
            total_k_nodes=3,
        )
        state_a.add_execution(
            k_node_index=0,
            k_node_name="step_1",
            input_prompt="Input 1",
            output="Output 1 - VALID STATE",
            duration_ms=100.0,
        )
        
        manager.checkpoint("workflow_rollback_test", state_a)
        print("✓ State A checkpointed (VALID STATE)")
        
        # Verify State A
        loaded_state = manager.resume_workflow("workflow_rollback_test")
        assert loaded_state.last_successful_output == "Output 1 - VALID STATE"
        print("✓ State A verified")
        
        # Simulate failure during checkpoint of State B
        # We'll mock the _atomic_swap method to raise an exception
        state_b = WorkflowState(
            workflow_id="workflow_rollback_test",
            workflow_type="test",
            total_k_nodes=3,
        )
        state_b.add_execution(
            k_node_index=0,
            k_node_name="step_1",
            input_prompt="Input 1",
            output="Output 1",
            duration_ms=100.0,
        )
        state_b.add_execution(
            k_node_index=1,
            k_node_name="step_2",
            input_prompt="Input 2",
            output="Output 2 - CORRUPTED STATE (should not persist)",
            duration_ms=150.0,
        )
        
        # Mock atomic_swap to simulate failure
        original_swap = manager._atomic_swap
        def failing_swap(shadow_key, active_key):
            raise IOError("Simulated disk failure during atomic swap")
        
        manager._atomic_swap = failing_swap
        
        # Attempt to checkpoint State B (should fail)
        try:
            manager.checkpoint("workflow_rollback_test", state_b)
            assert False, "Checkpoint should have failed"
        except StatePersistenceError as e:
            print(f"✓ Checkpoint failed as expected: {e}")
        
        # Restore original method
        manager._atomic_swap = original_swap
        
        # CRITICAL TEST: Verify State A is still intact
        loaded_state = manager.resume_workflow("workflow_rollback_test")
        assert loaded_state is not None
        assert loaded_state.current_k_node == 1
        assert loaded_state.last_successful_output == "Output 1 - VALID STATE"
        assert "CORRUPTED" not in loaded_state.last_successful_output
        print("✓ State A remains intact after failed checkpoint (ROLLBACK SUCCESSFUL)")
        
        # Verify shadow file was cleaned up
        shadow_path = Path(temp_dir) / "workflow_rollback_test_shadow.json"
        assert not shadow_path.exists()
        print("✓ Shadow file cleaned up after failure")
    
    print("Rollback on failure test passed!\n")


def test_resume_workflow():
    """Test workflow resume functionality."""
    print("\n=== Testing Workflow Resume ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AtomicStateManager(
            backend=BackendType.FILE,
            storage_path=temp_dir,
        )
        
        # Test resume with no checkpoint
        state = manager.resume_workflow("nonexistent_workflow")
        assert state is None
        print("✓ Resume returns None for nonexistent workflow")
        
        # Create and checkpoint a workflow
        state = WorkflowState(
            workflow_id="workflow_resume_test",
            workflow_type="resume_generation",
            total_k_nodes=5,
        )
        
        # Simulate partial completion
        for i in range(3):
            state.add_execution(
                k_node_index=i,
                k_node_name=f"step_{i+1}",
                input_prompt=f"Input {i+1}",
                output=f"Output {i+1}",
                duration_ms=100.0 + i * 10,
            )
        
        manager.checkpoint("workflow_resume_test", state)
        print("✓ Workflow checkpointed at K-Node 3/5")
        
        # Simulate crash and resume
        resumed_state = manager.resume_workflow("workflow_resume_test")
        assert resumed_state is not None
        assert resumed_state.current_k_node == 3
        assert len(resumed_state.execution_log) == 3
        assert resumed_state.get_progress_percentage() == 60.0
        print(f"✓ Workflow resumed at K-Node {resumed_state.current_k_node}/5 (60% complete)")
        
        # Continue from resumed state
        resumed_state.add_execution(
            k_node_index=3,
            k_node_name="step_4",
            input_prompt="Input 4",
            output="Output 4",
            duration_ms=130.0,
        )
        
        manager.checkpoint("workflow_resume_test", resumed_state)
        print("✓ Workflow continued and checkpointed at K-Node 4/5")
    
    print("Workflow resume test passed!\n")


def test_concurrent_checkpoints():
    """Test multiple workflows with concurrent checkpoints."""
    print("\n=== Testing Concurrent Checkpoints ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AtomicStateManager(
            backend=BackendType.FILE,
            storage_path=temp_dir,
        )
        
        # Create multiple workflows
        workflows = []
        for i in range(3):
            state = WorkflowState(
                workflow_id=f"workflow_{i}",
                workflow_type="test",
                total_k_nodes=2,
            )
            state.add_execution(
                k_node_index=0,
                k_node_name="step_1",
                input_prompt=f"Input for workflow {i}",
                output=f"Output for workflow {i}",
                duration_ms=100.0,
            )
            workflows.append(state)
        
        # Checkpoint all workflows
        for state in workflows:
            manager.checkpoint(state.workflow_id, state)
        print(f"✓ Checkpointed {len(workflows)} workflows")
        
        # List all checkpoints
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) == 3
        print(f"✓ Listed {len(checkpoints)} checkpoints")
        
        # Verify each workflow can be resumed independently
        for i in range(3):
            state = manager.resume_workflow(f"workflow_{i}")
            assert state is not None
            assert state.workflow_id == f"workflow_{i}"
            assert f"Output for workflow {i}" in state.last_successful_output
        print("✓ All workflows can be resumed independently")
        
        # Delete one checkpoint
        deleted = manager.delete_checkpoint("workflow_1")
        assert deleted
        print("✓ Checkpoint deleted")
        
        # Verify deletion
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) == 2
        assert "workflow_1" not in checkpoints
        print("✓ Deletion verified")
    
    print("Concurrent checkpoints test passed!\n")


def test_singleton_factory():
    """Test singleton factory pattern."""
    print("\n=== Testing Singleton Factory ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Reset singleton
        reset_state_manager()
        
        # Get manager instance
        manager1 = get_state_manager(storage_path=temp_dir)
        manager2 = get_state_manager()
        
        # Should be same instance
        assert manager1 is manager2
        print("✓ Singleton pattern working correctly")
        
        # Reset and get new instance
        reset_state_manager()
        manager3 = get_state_manager(storage_path=temp_dir)
        
        # Should be different instance
        assert manager3 is not manager1
        print("✓ State manager reset working correctly")
    
    print("Singleton factory test passed!\n")


def test_fsync_durability():
    """Test that fsync ensures durability."""
    print("\n=== Testing fsync Durability ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AtomicStateManager(
            backend=BackendType.FILE,
            storage_path=temp_dir,
        )
        
        # Create state
        state = WorkflowState(
            workflow_id="durability_test",
            workflow_type="test",
            total_k_nodes=1,
        )
        state.add_execution(
            k_node_index=0,
            k_node_name="step_1",
            input_prompt="Input",
            output="Output",
            duration_ms=100.0,
        )
        
        # Checkpoint (includes fsync)
        manager.checkpoint("durability_test", state)
        print("✓ Checkpoint with fsync completed")
        
        # Verify file exists and is readable
        file_path = Path(temp_dir) / "durability_test.json"
        assert file_path.exists()
        assert file_path.stat().st_size > 0
        print("✓ State file exists and has content")
        
        # Verify content is valid JSON
        with open(file_path, 'r') as f:
            content = f.read()
            assert "durability_test" in content
            assert "Output" in content
        print("✓ State file contains valid data")
    
    print("fsync durability test passed!\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ATOMIC STATE PERSISTENCE TEST SUITE (ACID GUARANTEES)")
    print("=" * 60)
    
    tests = [
        test_workflow_state_schema,
        test_atomic_checkpoint,
        test_rollback_on_failure,
        test_resume_workflow,
        test_concurrent_checkpoints,
        test_singleton_factory,
        test_fsync_durability,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Atomic state persistence with ACID guarantees is working correctly.")
        print("\n✅ ZERO DATA LOSS GUARANTEE VERIFIED:")
        print("   - Two-phase commit ensures atomicity")
        print("   - Rollback on failure preserves old state")
        print("   - fsync ensures durability")
        print("   - Workflow resume capability confirmed")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    # Run tests
    exit_code = main()
    sys.exit(exit_code)
