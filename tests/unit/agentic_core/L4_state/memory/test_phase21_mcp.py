"""
[PHASE 21] Unit Tests for Production-Grade Privacy & Knowledge Graph Integration.

Tests:
1. PIISanitizer - Email, IPv4/v6, and API key pattern detection and redaction
2. GraphMemoryBridge - Entity creation, relation creation, graceful degradation

[SSOT] Tests for Phase 21 features in SemanticCacheManager and GraphMemoryBridge.
"""

from __future__ import annotations

import hashlib
from unittest.mock import MagicMock

import pytest

# =============================================================================
# PIISanitizer Tests
# =============================================================================


class TestPIISanitizer:
    """Tests for the production-grade PIISanitizer."""

    @pytest.fixture
    def sanitizer(self):
        """Get the PIISanitizer class."""
        from agentic_core.L4_state.memory.SemanticCacheManager import PIISanitizer

        return PIISanitizer

    def test_sanitize_email(self, sanitizer):
        """Test that email addresses are properly redacted."""
        content = "Contact me at john.doe@example.com for more info."
        result = sanitizer.sanitize(content)

        assert "john.doe@example.com" not in result
        assert "[REDACTED_EMAIL]" in result
        assert "Contact me at" in result
        assert "for more info." in result

    def test_sanitize_multiple_emails(self, sanitizer):
        """Test that multiple email addresses are all redacted."""
        content = "Send to alice@test.org and bob@company.co.uk"
        result = sanitizer.sanitize(content)

        assert "alice@test.org" not in result
        assert "bob@company.co.uk" not in result
        assert result.count("[REDACTED_EMAIL]") == 2

    def test_sanitize_ipv4(self, sanitizer):
        """Test that IPv4 addresses are properly redacted."""
        content = "Server IP is 192.168.1.100 and gateway is 10.0.0.1"
        result = sanitizer.sanitize(content)

        assert "192.168.1.100" not in result
        assert "10.0.0.1" not in result
        assert result.count("[REDACTED_IPV4]") == 2

    def test_sanitize_ipv6(self, sanitizer):
        """Test that IPv6 addresses are properly redacted."""
        content = "IPv6 address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = sanitizer.sanitize(content)

        assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" not in result
        assert "[REDACTED_IPV6]" in result

    def test_sanitize_openai_api_key(self, sanitizer):
        """Test that OpenAI API keys (sk-...) are properly redacted."""
        content = "My API key is sk-abcdefghijklmnopqrstuvwxyz1234567890"
        result = sanitizer.sanitize(content)

        assert "sk-abcdefghijklmnopqrstuvwxyz1234567890" not in result
        assert "[REDACTED_OPENAI_KEY]" in result

    def test_sanitize_anthropic_api_key(self, sanitizer):
        """Test that Anthropic API keys (sk-ant-...) are properly redacted."""
        content = "Anthropic key: sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
        result = sanitizer.sanitize(content)

        assert "sk-ant-api03-abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED_ANTHROPIC_KEY]" in result

    def test_sanitize_aws_key(self, sanitizer):
        """Test that AWS access key IDs are properly redacted."""
        content = "AWS key: AKIAIOSFODNN7EXAMPLE"
        result = sanitizer.sanitize(content)

        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[REDACTED_AWS_KEY]" in result

    def test_sanitize_combined_pii(self, sanitizer):
        """Test that multiple PII types are all redacted in one pass."""
        content = (
            "User john@example.com connected from 192.168.1.50 "
            "using API key sk-testkey1234567890abcdefghij"
        )
        result = sanitizer.sanitize(content)

        # All PII should be redacted
        assert "john@example.com" not in result
        assert "192.168.1.50" not in result
        assert "sk-testkey1234567890abcdefghij" not in result

        # Placeholders should be present
        assert "[REDACTED_EMAIL]" in result
        assert "[REDACTED_IPV4]" in result
        assert "[REDACTED_OPENAI_KEY]" in result

    def test_sanitize_preserves_safe_content(self, sanitizer):
        """Test that content without PII is preserved unchanged."""
        content = "This is a normal message with no sensitive data."
        result = sanitizer.sanitize(content)

        assert result == content

    def test_sanitize_empty_string(self, sanitizer):
        """Test that empty strings are handled correctly."""
        assert sanitizer.sanitize("") == ""
        assert sanitizer.sanitize(None) is None

    def test_is_safe_with_pii(self, sanitizer):
        """Test that is_safe returns False when PII is present."""
        assert sanitizer.is_safe("Contact: user@example.com") is False
        assert sanitizer.is_safe("IP: 10.0.0.1") is False
        assert sanitizer.is_safe("Key: sk-abc123def456ghi789jkl012") is False

    def test_is_safe_without_pii(self, sanitizer):
        """Test that is_safe returns True when no PII is present."""
        assert sanitizer.is_safe("Hello world") is True
        assert sanitizer.is_safe("The quick brown fox") is True
        assert sanitizer.is_safe("") is True

    def test_detect_pii_returns_findings(self, sanitizer):
        """Test that detect_pii returns all found PII by type."""
        content = "Email: test@example.com, IP: 192.168.0.1"
        findings = sanitizer.detect_pii(content)

        assert "EMAIL" in findings
        assert "IPV4" in findings
        assert len(findings["EMAIL"]) == 1
        assert len(findings["IPV4"]) == 1


# =============================================================================
# GraphMemoryBridge Tests
# =============================================================================


class TestGraphMemoryBridge:
    """Tests for the GraphMemoryBridge MCP interface."""

    @pytest.fixture
    def bridge(self):
        """Get a fresh GraphMemoryBridge instance."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        # Reset singleton for clean test
        GraphMemoryBridge.reset_instance()
        return GraphMemoryBridge.get_instance()

    def test_singleton_pattern(self):
        """Test that GraphMemoryBridge follows singleton pattern."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        GraphMemoryBridge.reset_instance()
        instance1 = GraphMemoryBridge.get_instance()
        instance2 = GraphMemoryBridge.get_instance()

        assert instance1 is instance2

    def test_create_agent_entity_with_mock(self, bridge):
        """Test creating an agent entity with mocked MCP functions."""
        # Mock the MCP function
        mock_create_entities = MagicMock(return_value={"success": True})
        bridge.set_mcp_functions(create_entities=mock_create_entities)

        # Create entity
        result = bridge.create_agent_entity(
            agent_name="TestAgent",
            agent_type="Agent",
            observations=["Test observation"],
        )

        assert result is True
        mock_create_entities.assert_called_once()

        # Verify the call arguments
        call_args = mock_create_entities.call_args
        entities = call_args.kwargs.get("entities") or call_args[1].get("entities")
        assert entities[0]["name"] == "TestAgent"
        assert entities[0]["entityType"] == "Agent"

    def test_create_agent_entity_idempotent(self, bridge):
        """Test that creating the same entity twice is idempotent."""
        mock_create_entities = MagicMock(return_value={"success": True})
        bridge.set_mcp_functions(create_entities=mock_create_entities)

        # Create entity twice
        bridge.create_agent_entity("TestAgent")
        bridge.create_agent_entity("TestAgent")

        # Should only call MCP once (second call is cached)
        assert mock_create_entities.call_count == 1

    def test_create_mastered_task_relation(self, bridge):
        """Test creating a MASTERED_TASK relation."""
        mock_create_entities = MagicMock(return_value={"success": True})
        mock_create_relations = MagicMock(return_value={"success": True})
        bridge.set_mcp_functions(
            create_entities=mock_create_entities,
            create_relations=mock_create_relations,
        )

        # Create relation
        result = bridge.create_mastered_task_relation(
            agent_name="GovernorAgent",
            task_description="Heal repository violations",
            feedback_score=0.95,
        )

        assert result is True

        # Verify relation was created
        mock_create_relations.assert_called_once()
        call_args = mock_create_relations.call_args
        relations = call_args.kwargs.get("relations") or call_args[1].get("relations")
        assert relations[0]["from"] == "GovernorAgent"
        assert relations[0]["relationType"] == "MASTERED_TASK"

    def test_graceful_degradation_no_mcp(self, bridge):
        """Test that operations degrade gracefully when MCP is unavailable."""
        # Don't set any MCP functions (simulating unavailability)
        bridge._mcp_available = False

        # Operations should not crash
        result = bridge.create_agent_entity("TestAgent")
        assert result is True  # Returns True but doesn't actually create

        # Stats should track skipped operations
        stats = bridge.get_statistics()
        assert stats["operations_skipped"] >= 1

    def test_graceful_degradation_mcp_error(self, bridge):
        """Test that operations handle MCP errors gracefully."""
        # Mock function that raises an exception
        mock_create_entities = MagicMock(side_effect=Exception("MCP connection failed"))
        bridge.set_mcp_functions(create_entities=mock_create_entities)

        # Operation should not crash
        result = bridge.create_agent_entity("TestAgent")

        # Should return False on error
        assert result is False

        # Stats should track errors
        stats = bridge.get_statistics()
        assert stats["mcp_errors"] >= 1

    def test_add_observation(self, bridge):
        """Test adding an observation to an entity."""
        mock_add_observations = MagicMock(return_value={"success": True})
        bridge.set_mcp_functions(add_observations=mock_add_observations)

        result = bridge.add_observation(
            entity_name="TestAgent",
            observation="Agent successfully healed 5 violations",
        )

        assert result is True
        mock_add_observations.assert_called_once()

    def test_search_entities(self, bridge):
        """Test searching for entities in the graph."""
        mock_search = MagicMock(
            return_value=[
                {"name": "GovernorAgent", "type": "Agent"},
                {"name": "ValidatorAgent", "type": "Agent"},
            ]
        )
        bridge.set_mcp_functions(search_nodes=mock_search)

        results = bridge.search_entities("Agent")

        assert len(results) == 2
        assert results[0]["name"] == "GovernorAgent"

    def test_statistics_tracking(self, bridge):
        """Test that statistics are properly tracked."""
        mock_create_entities = MagicMock(return_value={"success": True})
        mock_create_relations = MagicMock(return_value={"success": True})
        mock_add_observations = MagicMock(return_value={"success": True})

        bridge.set_mcp_functions(
            create_entities=mock_create_entities,
            create_relations=mock_create_relations,
            add_observations=mock_add_observations,
        )

        # Perform operations
        bridge.create_agent_entity("Agent1")
        bridge.create_agent_entity("Agent2")
        bridge.create_relation("Agent1", "Agent2", "INTERACTS_WITH")
        bridge.add_observation("Agent1", "Test observation")

        stats = bridge.get_statistics()

        assert stats["entities_created"] == 2
        assert stats["relations_created"] == 1
        assert stats["observations_added"] == 1
        assert stats["mcp_available"] is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase21Integration:
    """Integration tests for Phase 21 features."""

    def test_pii_sanitizer_in_semantic_cache(self):
        """Test that PIISanitizer is used in SemanticCacheManager."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            PIISanitizer,
        )

        # Verify PIISanitizer is imported and functional
        assert hasattr(PIISanitizer, "sanitize")
        assert hasattr(PIISanitizer, "is_safe")
        assert hasattr(PIISanitizer, "detect_pii")

        # Test sanitization
        test_content = "User email: test@example.com with key sk-abc123def456ghi789jkl012mno"
        sanitized = PIISanitizer.sanitize(test_content)

        assert "test@example.com" not in sanitized
        assert "sk-abc123def456ghi789jkl012mno" not in sanitized

    def test_graph_memory_bridge_task_hash(self):
        """Test that task descriptions are properly hashed."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        GraphMemoryBridge.reset_instance()
        bridge = GraphMemoryBridge.get_instance()

        # Mock the MCP functions
        mock_create_entities = MagicMock(return_value={"success": True})
        mock_create_relations = MagicMock(return_value={"success": True})
        bridge.set_mcp_functions(
            create_entities=mock_create_entities,
            create_relations=mock_create_relations,
        )

        # Create a mastered task relation
        task_description = "Heal repository violations"
        bridge.create_mastered_task_relation(
            agent_name="TestAgent",
            task_description=task_description,
            feedback_score=0.9,
        )

        # Verify the task entity name is a hash
        call_args = mock_create_entities.call_args
        entities = call_args.kwargs.get("entities") or call_args[1].get("entities")
        task_entity_name = entities[0]["name"]

        # Should be "Task_" + first 16 chars of SHA256 hash
        expected_hash = hashlib.sha256(task_description.encode()).hexdigest()[:16]
        assert task_entity_name == f"Task_{expected_hash}"


# =============================================================================
# MetaLearningMixin Integration Tests
# =============================================================================


class TestMetaLearningMixinPhase21:
    """Tests for Phase 21 features in MetaLearningMixin."""

    @pytest.fixture(autouse=True)
    def reset_singletons(self):
        """Reset all singletons before each test."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge
        from agentic_core.base_agents.meta_learning_mixin import meta_learning_mixin

        MetaLearningMixin.reset_lobotomy()
        MetaLearningMixin.reset_kg()
        MetaLearningMixin.reset_graph_bridge()
        GraphMemoryBridge.reset_instance()

        yield

        # Cleanup after test
        MetaLearningMixin.reset_lobotomy()
        MetaLearningMixin.reset_kg()
        MetaLearningMixin.reset_graph_bridge()
        GraphMemoryBridge.reset_instance()

    def test_meta_learning_mixin_has_graph_bridge_methods(self):
        """Test that MetaLearningMixin has Phase 21 methods."""
        from agentic_core.base_agents.meta_learning_mixin import meta_learning_mixin

        # Verify Phase 21 methods exist
        assert hasattr(MetaLearningMixin, "_ensure_graph_bridge_connection")
        assert hasattr(MetaLearningMixin, "_register_agent_entity")
        assert hasattr(MetaLearningMixin, "learn_with_feedback")
        assert hasattr(MetaLearningMixin, "_create_mastered_task_relation")
        assert hasattr(MetaLearningMixin, "get_graph_stats")
        assert hasattr(MetaLearningMixin, "reset_graph_bridge")

    def test_learn_with_feedback_creates_relation_on_promotion(self):
        """Test that learn_with_feedback creates MASTERED_TASK relation when promoted."""
        from agentic_core.base_agents.meta_learning_mixin import meta_learning_mixin

        # Create a test class that uses the mixin
        class TestAgent(MetaLearningMixin):
            def __init__(self):
                # Skip full initialization for testing
                self._discovered_context = {}

        # Mock the memory and graph bridge
        mock_memory = MagicMock()
        mock_memory.promotion_threshold = 0.8
        mock_memory.learn = MagicMock()
        mock_memory.promote_to_long_term = MagicMock(return_value=True)

        mock_graph_bridge = MagicMock()
        mock_graph_bridge.create_mastered_task_relation = MagicMock(return_value=True)

        # Inject mocks
        MetaLearningMixin._memory = mock_memory
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._graph_bridge = mock_graph_bridge

        # Create agent and call learn_with_feedback
        agent = TestAgent()
        result = agent.learn_with_feedback(
            context="Test task context",
            result={"status": "success"},
            feedback_score=0.9,  # Above threshold
        )

        # Verify promotion happened
        assert result is True
        mock_memory.promote_to_long_term.assert_called_once()

        # Verify MASTERED_TASK relation was created
        mock_graph_bridge.create_mastered_task_relation.assert_called_once_with(
            agent_name="TestAgent",
            task_description="Test task context",
            feedback_score=0.9,
        )

    def test_learn_with_feedback_no_relation_below_threshold(self):
        """Test that learn_with_feedback doesn't create relation below threshold."""
        from agentic_core.base_agents.meta_learning_mixin import meta_learning_mixin

        class TestAgent(MetaLearningMixin):
            def __init__(self):
                self._discovered_context = {}

        # Mock the memory
        mock_memory = MagicMock()
        mock_memory.promotion_threshold = 0.8
        mock_memory.learn = MagicMock()
        mock_memory.promote_to_long_term = MagicMock()

        mock_graph_bridge = MagicMock()

        MetaLearningMixin._memory = mock_memory
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._graph_bridge = mock_graph_bridge

        agent = TestAgent()
        result = agent.learn_with_feedback(
            context="Test task context",
            result={"status": "success"},
            feedback_score=0.5,  # Below threshold
        )

        # Should not promote
        assert result is False
        mock_memory.promote_to_long_term.assert_not_called()
        mock_graph_bridge.create_mastered_task_relation.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
