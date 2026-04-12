"""Tests for Phase 7 — Governed Prompt Adapter.

Validates the apps_* → execute_artifact() integration path.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import with graceful fallback for collection-time import issues
try:
    from apps_shared.utils.governed_prompt_adapter import (
        GovernedPromptAdapter,
        create_governed_adapter,
    )
except ImportError as _import_err:
    pytest.skip(f"governed_prompt_adapter not available: {_import_err}", allow_module_level=True)

import unittest
from unittest.mock import MagicMock, patch


class TestGovernedPromptAdapter(unittest.TestCase):
    """Test GovernedPromptAdapter functionality."""

    def test_adapter_creation(self) -> None:
        """Test adapter can be created."""
        adapter = GovernedPromptAdapter(
            agent_id="test-agent",
            provider="openai",
            secret_key=b"test-key",
        )
        self.assertEqual(adapter.agent_id, "test-agent")
        self.assertEqual(adapter.provider, "openai")

    def test_factory_function(self) -> None:
        """Test factory function creates adapter."""
        adapter = create_governed_adapter(
            agent_id="factory-agent",
            provider="anthropic",
        )
        self.assertIsInstance(adapter, GovernedPromptAdapter)
        self.assertEqual(adapter.agent_id, "factory-agent")

    def test_default_secret_key(self) -> None:
        """Test default secret key is provided."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")
        self.assertIsNotNone(adapter.secret_key)

    @patch("apps_shared.utils.governed_prompt_adapter.GovernedPromptAdapter._build_prompt_bom")
    @patch("apps_shared.utils.governed_prompt_adapter.GovernedPromptAdapter._assemble_artifact")
    @patch("apps_shared.utils.governed_prompt_adapter.GovernedPromptAdapter._execute_artifact")
    def test_execute_prompt_flow(
        self,
        mock_execute: MagicMock,
        mock_assemble: MagicMock,
        mock_build_bom: MagicMock,
    ) -> None:
        """Test the full execute_prompt flow."""
        # Setup mocks
        mock_bom = MagicMock()
        mock_bom.trace_id = "trace-123"
        mock_bom.mixins_required = ("mixin1",)
        mock_bom.raw_c0 = {}
        mock_bom.raw_u0 = "test input"
        mock_build_bom.return_value = mock_bom

        mock_artifact = MagicMock()
        mock_artifact.trace_id = "trace-123"
        mock_assemble.return_value = mock_artifact

        mock_execute.return_value = {
            "content": "Test response",
            "usage": {"total_tokens": 100},
        }

        # Execute
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")
        result = adapter.execute_prompt(
            user_prompt="Hello",
            system_prompt="System",
            mixins=("mixin1",),
        )

        # Verify
        self.assertEqual(result["content"], "Test response")
        self.assertTrue(result["governed"])
        mock_build_bom.assert_called_once()
        mock_assemble.assert_called_once()
        mock_execute.assert_called_once()

    def test_compose_system_prompt(self) -> None:
        """Test system prompt composition."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")

        with patch(
            "agentic_core.L4_state.memory.template_registry.get_template_registry"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.get_i0_mixin.return_value = "Mixin content"
            mock_get_registry.return_value = mock_registry

            result = adapter._compose_system_prompt(
                base_s0="Base system",
                mixins=("mixin1",),
            )

            self.assertIn("Base system", result)
            self.assertIn("Mixin content", result)
            self.assertIn("<D0>", result)  # Defensive fence

    def test_compose_user_prompt_with_context(self) -> None:
        """Test user prompt composition with context."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")

        result = adapter._compose_user_prompt(
            context={
                "rag_chunks": ["chunk1", "chunk2"],
                "ast_snapshot": "def foo(): pass",
            },
            user_input="Hello",
        )

        self.assertIn("<C0 type='rag'>", result)
        self.assertIn("chunk1", result)
        self.assertIn("<C0 type='ast'>", result)
        self.assertIn("<U0>", result)
        self.assertIn("Hello", result)

    def test_compose_user_prompt_without_context(self) -> None:
        """Test user prompt composition without context."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")

        result = adapter._compose_user_prompt(
            context={},
            user_input="Hello",
        )

        self.assertIn("<U0>", result)
        self.assertIn("Hello", result)
        self.assertNotIn("<C0", result)

    def test_sign_artifact(self) -> None:
        """Test artifact signing."""
        adapter = GovernedPromptAdapter(
            agent_id="test",
            provider="openai",
            secret_key=b"test-secret",
        )

        mock_artifact = MagicMock()
        mock_artifact.to_dict.return_value = {"trace_id": "test", "content": "data"}

        signature = adapter._sign_artifact(mock_artifact)

        self.assertEqual(len(signature), 64)  # SHA-256 hex length


class TestPhase7Integration(unittest.TestCase):
    """Integration tests for Phase 7 wiring."""

    def test_adapter_imports(self) -> None:
        """Test that adapter module can be imported."""
        from apps_shared.utils import governed_prompt_adapter

        self.assertIsNotNone(governed_prompt_adapter.GovernedPromptAdapter)
        self.assertIsNotNone(governed_prompt_adapter.create_governed_adapter)

    def test_instruction_packet_building(self) -> None:
        """Test InstructionPacket is built correctly."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")

        packet = adapter._build_instruction_packet(
            trace_id="trace-123",
            path="A",
            intent_class="test_intent",
            required_mixins=("mixin1", "mixin2"),
        )

        self.assertEqual(packet.trace_id, "trace-123")
        self.assertEqual(packet.path, "A")
        self.assertEqual(packet.intent_class, "test_intent")

    def test_all_paths_supported(self) -> None:
        """Test that all routing paths are supported."""
        adapter = GovernedPromptAdapter(agent_id="test", provider="openai")

        for path in ("A", "B", "C", "D"):
            packet = adapter._build_instruction_packet(
                trace_id=f"trace-{path}",
                path=path,
                intent_class="test",
                required_mixins=(),
            )
            self.assertEqual(packet.path, path)


class TestAgentExecutorIntegration(unittest.TestCase):
    """Test AgentExecutor integration with governed pipeline."""

    @patch("apps_shared.utils.governed_prompt_adapter.GovernedPromptAdapter.execute_prompt")
    def test_execute_via_governed_pipeline(self, mock_execute: MagicMock) -> None:
        """Test AgentExecutor.execute_via_governed_pipeline method."""
        from apps_rg.utils.agent_executor_util import AgentExecutor, AgentMessage

        mock_execute.return_value = {
            "content": "Governed response",
            "usage": {"total_tokens": 50},
            "trace_id": "trace-123",
            "governed": True,
            "provider": "openai",
        }

        executor = AgentExecutor()
        messages = [
            AgentMessage(role="user", content="Hello"),
            AgentMessage(role="assistant", content="Hi there"),
        ]

        response = executor.execute_via_governed_pipeline(
            messages=messages,
            system_prompt="System prompt",
            mixins=("mixin1",),
            path="B",
        )

        self.assertEqual(response.content, "Governed response")
        self.assertTrue(response.metadata.get("governed"))
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
