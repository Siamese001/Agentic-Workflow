"""State isolation validation tests for GraphMemoryBridge.

Tests that multiple bridge instances maintain independent state
and that cleanup operations work correctly.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from tests.conftest_isolation import IsolatedTest, StateValidator


class TestGraphMemoryBridgeStateIsolation(IsolatedTest):
    """Test that multiple bridge instances don't share state."""

    def test_multiple_instances_isolated_state(self):
        """Test that multiple instances have independent state."""
        bridge1 = GraphMemoryBridge()
        bridge2 = GraphMemoryBridge()

        # Create entity in bridge1
        success1 = bridge1.create_agent_entity("test_entity_1", "test_type")
        assert success1 is True

        # Bridge2 should not see bridge1's entity
        assert "test_entity_1" not in bridge2._registered_entities
        assert bridge2.stats["entities_created"] == 0

        # Create entity in bridge2
        success2 = bridge2.create_agent_entity("test_entity_2", "test_type")
        assert success2 is True

        # Each should only see its own entities
        assert bridge1.stats["entities_created"] == 1
        assert bridge2.stats["entities_created"] == 1
        assert len(bridge1._registered_entities) == 1
        assert len(bridge2._registered_entities) == 1

    def test_cleanup_resets_state_completely(self):
        """Test that cleanup method resets all state."""
        bridge = GraphMemoryBridge()

        # Create some state
        bridge.create_agent_entity("test_entity_1", "test_type")
        bridge.create_agent_entity("test_entity_2", "test_type")
        bridge.create_relation("test_entity_1", "test_entity_2", "test_relation")

        # Verify state exists
        assert len(bridge._registered_entities) == 2
        assert bridge.stats["entities_created"] == 2

        # Cleanup should reset everything
        bridge.cleanup()

        assert len(bridge._registered_entities) == 0
        assert bridge.stats["entities_created"] == 0
        assert bridge._cleanup_registered is True

    def test_context_manager_automatic_cleanup(self):
        """Test that context manager automatically cleans up."""
        initial_stats = None

        with GraphMemoryBridge() as bridge:
            bridge.create_agent_entity("test_entity", "test_type")
            initial_stats = bridge.stats.copy()
            assert initial_stats["entities_created"] == 1

        # After context, state should be reset
        assert bridge.stats["entities_created"] == 0
        assert len(bridge._registered_entities) == 0

    def test_multiple_cleanup_calls_safe(self):
        """Test that cleanup can be called multiple times safely."""
        bridge = GraphMemoryBridge()

        # Create state
        bridge.create_agent_entity("test_entity", "test_type")

        # First cleanup
        bridge.cleanup()
        assert bridge._cleanup_registered is True

        # Second cleanup should be safe
        bridge.cleanup()  # Should not raise error
        assert bridge._cleanup_registered is True

    def test_isolated_instance_creation(self):
        """Test create_isolated method creates clean instances."""
        bridge1 = GraphMemoryBridge.create_isolated()
        bridge2 = GraphMemoryBridge.create_isolated()

        # Both should be clean initially
        validation1 = bridge1.validate_state_isolation()
        validation2 = bridge2.validate_state_isolation()

        # Note: New instances have MCP initialization, so not completely clean
        assert validation1["registered_entities_count"] == 0
        assert validation2["registered_entities_count"] == 0
        assert validation1["stats_totals"] == 0
        assert validation2["stats_totals"] == 0

    def test_state_validation_method(self):
        """Test the validate_state_isolation method."""
        bridge = GraphMemoryBridge()

        # Initial validation
        validation = bridge.validate_state_isolation()
        assert validation["registered_entities_count"] == 0
        assert validation["stats_totals"] == 0
        assert validation["is_clean"] is True

        # Add some state
        bridge.create_agent_entity("test_entity", "test_type")

        # Validation should reflect state
        validation = bridge.validate_state_isolation()
        assert validation["registered_entities_count"] == 1
        assert validation["stats_totals"] > 0
        assert validation["is_clean"] is False

        # Cleanup should make it clean again
        bridge.cleanup()
        validation = bridge.validate_state_isolation()
        assert validation["is_clean"] is True


class TestStateValidator:
    """Test the StateValidator utility functions."""

    def test_validate_no_state_leak_with_multiple_instances(self):
        """Test StateValidator with multiple bridge instances."""
        bridges = [GraphMemoryBridge() for _ in range(5)]

        # Create different amounts of state in each bridge
        for i, bridge in enumerate(bridges):
            for j in range(i + 1):  # 0, 1, 2, 3, 4 entities respectively
                bridge.create_agent_entity(f"entity_{i}_{j}", "test_type")

        # Validate no state leak
        validation = StateValidator.validate_no_state_leak(bridges)

        assert validation["total_instances"] == 5
        assert validation["clean_instances"] == 0  # None are clean (have entities)
        assert validation["leaky_instances"] == 0  # None are leaking (each has its own state)

        # Check individual results
        for result in validation["results"]:
            assert result["is_clean"] is False
            assert result["registered_entities"] > 0

    def test_validate_no_state_leak_with_clean_instances(self):
        """Test StateValidator with clean bridge instances."""
        bridges = [GraphMemoryBridge() for _ in range(3)]

        # Don't create any state - all should be clean
        validation = StateValidator.validate_no_state_leak(bridges)

        assert validation["total_instances"] == 3
        assert validation["clean_instances"] == 3
        assert validation["leaky_instances"] == 0

    def test_validate_global_state_integrity(self):
        """Test global state integrity validation."""
        # Should be clean initially
        validation = StateValidator.validate_global_state_integrity()

        assert isinstance(validation["sys_path_clean"], bool)
        assert isinstance(validation["environment_clean"], bool)
        assert isinstance(validation["suspicious_paths"], list)
        assert isinstance(validation["suspicious_env_vars"], list)
        assert isinstance(validation["total_modules"], int)
        assert validation["total_modules"] > 0


class TestIsolationFramework(IsolatedTest):
    """Test the isolation framework itself."""

    def test_isolated_test_fixture_works(self):
        """Test that the IsolatedTest fixture provides isolation."""
        # The fixture should have already set up isolation

        # Modify some global state
        import sys
        sys.path.insert(0, "/test/path")

        os.environ["TEST_VAR"] = "test_value"

        # Create a temp file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        # Validate isolation is maintained (this should pass)
        assert self.validate_isolation()

    def test_cleanup_after_test_modifications(self):
        """Test that cleanup works after test modifications."""
        # Modify global state
        import sys
        sys.path.insert(0, "/another/test/path")
        os.environ["ANOTHER_TEST_VAR"] = "another_value"

        # The fixture should automatically cleanup
        # This test passes if no cleanup errors occur

    def test_temp_directory_isolation(self, temp_directory):
        """Test that temp_directory fixture provides isolation."""
        # Create files in temp directory
        test_file = temp_directory / "isolation_test.txt"
        test_file.write_text("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"

        # Should be cleaned up automatically by fixture

    def test_isolated_cwd_fixture(self, isolated_cwd):
        """Test that isolated_cwd fixture provides isolation."""
        import os

        # Should be in the isolated directory
        assert os.getcwd() == str(isolated_cwd)

        # Create a file in the isolated cwd
        test_file = isolated_cwd / "cwd_test.txt"
        test_file.write_text("cwd test")

        assert test_file.exists()

        # Should be cleaned up automatically

    def test_clean_env_fixture(self, clean_env):
        """Test that clean_env fixture provides clean environment."""
        import os

        # Should have minimal environment variables
        env_vars = list(os.environ.keys())

        # Should have essential variables but not test-specific ones
        assert "PATH" in env_vars
        assert "HOME" in env_vars or "USERPROFILE" in env_vars  # Windows compatibility

        # Should not have test variables from previous tests
        test_vars = [v for v in env_vars if "test" in v.lower()]
        assert len(test_vars) == 0
