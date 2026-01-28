"""Phase 16 Tests: google.genai SDK Migration & Hardening.

Tests for new SDK client initialization, JSON mode enforcement, and model compatibility.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


class TestNewSDKClientInitialization:
    """Phase 16 Tests: google.genai Client initialization verification."""

    def test_new_sdk_client_initialization(self, tmp_path):
        """[Phase 16] Verify agent initializes google.genai Client using .env key."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Set API key
        original_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "test_api_key"

        try:
            agent = CognitiveDispositionAgent(
                project_root=tmp_path,
                api_key="test_api_key",
            )

            # Mock the genai import
            with patch("google.genai.Client") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                # Force re-initialization
                agent._client = None
                client = agent._get_client()

                # Verify Client was called with API key
                mock_client_class.assert_called_once_with(api_key="test_api_key")

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
            else:
                os.environ.pop("GEMINI_API_KEY", None)

    def test_client_lazy_loading(self, tmp_path):
        """[Phase 16] Verify client is lazy-loaded on first access."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(
            project_root=tmp_path,
            api_key="test_key",
        )

        # Client should be None initially
        assert agent._client is None

    def test_client_not_initialized_without_key(self, tmp_path):
        """[Phase 16] Verify client is not initialized without API key."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            with patch("dotenv.find_dotenv", return_value=None):
                agent = CognitiveDispositionAgent(
                    project_root=tmp_path,
                    api_key=None,
                )

            client = agent._get_client()
            assert client is None

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key


class TestJSONModeEnforcement:
    """Phase 16 Tests: JSON response mode verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_json_mode_enforcement(self, clean_project):
        """[Phase 16] Verify SDK call uses response_mime_type='application/json'."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            llm_enabled=True,
            api_key="test_key",
        )

        # Create test file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test file")

        # Mock the client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"action": "MOVE", "target_path": "agentic_core/L5_safety", "confidence": 0.9}'
        mock_client.models.generate_content.return_value = mock_response
        agent._client = mock_client

        # Call _generate_llm_decision
        decision = agent._generate_llm_decision(test_file, "ORPHAN", {})

        # Verify generate_content was called
        mock_client.models.generate_content.assert_called_once()

        # Get the call arguments
        call_kwargs = mock_client.models.generate_content.call_args

        # Verify config has response_mime_type
        config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
        assert config is not None
        assert config.response_mime_type == "application/json"

    def test_json_response_parsing(self, clean_project):
        """[Phase 16] Verify JSON response is correctly parsed."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )

        # Test JSON parsing
        json_response = '{"action": "ARCHIVE", "target_path": "archives/test", "reason": "Test reason", "confidence": 0.85}'

        decision = agent._parse_llm_json_response(json_response)

        assert decision.action == "ARCHIVE"
        assert decision.target_path == "archives/test"
        assert decision.confidence == 0.85


class TestFlash20Compatibility:
    """Phase 16 Tests: gemini-2.0-flash model compatibility."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_flash_2_0_compatibility(self, clean_project):
        """[Phase 16] Verify script functions with gemini-2.0-flash model."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
            DispositionDecision,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            llm_enabled=True,
            api_key="test_key",
        )

        # Create test file
        test_file = clean_project / "TestAgent.py"
        test_file.write_text("# Test agent file")

        # Mock the client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"action": "MOVE", "target_path": "agentic_core/L5_safety/validators", "reason": "Agent file", "confidence": 0.92}'
        mock_client.models.generate_content.return_value = mock_response
        agent._client = mock_client

        # Set model to gemini-2.0-flash
        original_model = os.environ.get("GEMINI_MODEL")
        os.environ["GEMINI_MODEL"] = "gemini-2.0-flash"

        try:
            decision = agent._generate_llm_decision(test_file, "ORPHAN", {})

            # Verify decision is valid
            assert isinstance(decision, DispositionDecision)
            assert decision.action in ("MOVE", "ARCHIVE", "IGNORE", "MANUAL_REVIEW", "REFACTOR")
            assert 0.0 <= decision.confidence <= 1.0

            # Verify model was used
            call_kwargs = mock_client.models.generate_content.call_args
            assert call_kwargs.kwargs.get("model") == "gemini-2.0-flash"

        finally:
            if original_model:
                os.environ["GEMINI_MODEL"] = original_model
            else:
                os.environ.pop("GEMINI_MODEL", None)

    def test_model_from_environment(self, clean_project):
        """[Phase 16] Verify model name is read from GEMINI_MODEL env var."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )

        # Create test file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test")

        # Mock client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"action": "ARCHIVE", "confidence": 0.5}'
        mock_client.models.generate_content.return_value = mock_response
        agent._client = mock_client

        # Set custom model
        original_model = os.environ.get("GEMINI_MODEL")
        os.environ["GEMINI_MODEL"] = "gemini-3-flash-preview"

        try:
            agent._generate_llm_decision(test_file, "ORPHAN", {})

            # Verify custom model was used
            call_kwargs = mock_client.models.generate_content.call_args
            assert call_kwargs.kwargs.get("model") == "gemini-3-flash-preview"

        finally:
            if original_model:
                os.environ["GEMINI_MODEL"] = original_model
            else:
                os.environ.pop("GEMINI_MODEL", None)


class TestPhase16Integration:
    """Phase 16 Tests: Full integration verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_sdk_migration_backward_compatibility(self, clean_project):
        """[Phase 16] Verify heuristic mode still works without SDK."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear API key
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            with patch("dotenv.find_dotenv", return_value=None):
                agent = CognitiveDispositionAgent(
                    project_root=clean_project,
                    llm_enabled=False,
                )

            # Create test file
            test_file = clean_project / "test_validator.py"
            test_file.write_text("# Test")

            # Should use heuristics
            decision = agent.analyze_violation(test_file, "ORPHAN")

            assert decision is not None
            assert decision.action in ("MOVE", "ARCHIVE", "MANUAL_REVIEW")

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_error_handling_on_sdk_failure(self, clean_project):
        """[Phase 16] Verify graceful error handling when SDK fails."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )

        # Create test file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test")

        # Mock client to raise exception
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        agent._client = mock_client

        # Should return MANUAL_REVIEW on error
        decision = agent._generate_llm_decision(test_file, "ORPHAN", {})

        assert decision.action == "MANUAL_REVIEW"
        assert "LLM Error" in decision.reason

    def test_tiered_processor_compatibility(self, clean_project):
        """[Phase 16] Verify TieredBatchProcessor works with new SDK."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.cognition.TieredBatchProcessor import (
            TieredBatchProcessor,
        )

        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )

        processor = TieredBatchProcessor(
            agent=agent,
            heuristic_threshold=0.75,
            checkpoint_file=str(clean_project / "checkpoint.json"),
        )

        # Verify processor initialized correctly
        assert processor.agent == agent
        assert processor.heuristic_threshold == 0.75
