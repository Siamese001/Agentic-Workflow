"""Phase 14 Tests: Environment Loading & API Key Validation.

Tests for .env file loading, manual override priority, and graceful degradation.
"""

from __future__ import annotations

import os
from unittest.mock import patch


class TestEnvFileLoading:
    """Phase 14 Tests: Environment file loading verification."""

    def test_env_file_loading(self, tmp_path):
        """[Phase 14] Verify agent loads variables from .env file using python-dotenv."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Create temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY=test_key_123\n")

        # Clear any existing env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return our temp .env file
            with patch("dotenv.find_dotenv", return_value=str(env_file)):
                agent = CognitiveDispositionAgent(project_root=tmp_path)

            # Verify API key was loaded
            assert agent.api_key == "test_key_123"

        finally:
            # Restore original env var
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_env_file_loading_with_real_dotenv(self, tmp_path):
        """[Phase 14] Verify agent loads .env using actual dotenv logic."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Create .env in tmp_path with proper format
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY='real_test_key'")

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return our temp .env
            with patch("dotenv.find_dotenv", return_value=str(env_file)):
                agent = CognitiveDispositionAgent(project_root=tmp_path)

                # Should have loaded from .env
                assert agent.api_key == "real_test_key"

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_env_file_not_found_graceful(self, tmp_path):
        """[Phase 14] Verify agent handles missing .env file gracefully."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return None (no .env found)
            with patch("dotenv.find_dotenv", return_value=None):
                agent = CognitiveDispositionAgent(project_root=tmp_path)

            # Should not crash, just have no API key
            assert agent.api_key is None

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key


class TestManualOverridePriority:
    """Phase 14 Tests: Manual API key override verification."""

    def test_manual_override_priority(self, tmp_path):
        """[Phase 14] Verify explicit key overrides .env file."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Set env var
        original_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "env_key"

        try:
            # Initialize with manual key
            agent = CognitiveDispositionAgent(
                project_root=tmp_path,
                api_key="manual_key",
            )

            # Manual key should take priority
            assert agent.api_key == "manual_key"

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
            else:
                os.environ.pop("GEMINI_API_KEY", None)

    def test_env_var_priority_over_dotenv(self, tmp_path):
        """[Phase 14] Verify existing env var prevents .env loading."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Set env var before initialization
        original_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "existing_env_key"

        try:
            # Create .env with different key
            env_file = tmp_path / ".env"
            env_file.write_text("GEMINI_API_KEY=dotenv_key\n")

            agent = CognitiveDispositionAgent(project_root=tmp_path)

            # Should use existing env var, not load from .env
            assert agent.api_key == "existing_env_key"

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
            else:
                os.environ.pop("GEMINI_API_KEY", None)


class TestMissingKeyGracefulDegradation:
    """Phase 14 Tests: Graceful degradation when API key is missing."""

    def test_missing_key_graceful_degradation(self, tmp_path):
        """[Phase 14] Verify behavior when no key is found."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return None
            with patch("dotenv.find_dotenv", return_value=None):
                agent = CognitiveDispositionAgent(project_root=tmp_path)

            # Should not crash
            assert agent.api_key is None

            # Should default to heuristic mode
            test_file = tmp_path / "test.py"
            test_file.write_text("# Test")

            decision = agent.analyze_violation(test_file, "ORPHAN")

            # Should return a decision (from heuristics)
            assert decision is not None
            assert decision.action in ("MOVE", "ARCHIVE", "MANUAL_REVIEW")

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_missing_key_logs_warning(self, tmp_path, caplog):
        """[Phase 14] Verify warning is logged when API key is missing."""
        import logging

        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            with patch("dotenv.find_dotenv", return_value=None):
                with caplog.at_level(logging.WARNING):
                    agent = CognitiveDispositionAgent(project_root=tmp_path)

            # Should have logged warning
            assert any("GEMINI_API_KEY not found" in record.message for record in caplog.records)

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_heuristic_mode_without_api_key(self, tmp_path):
        """[Phase 14] Verify agent works in heuristic mode without API key."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return None
            with patch("dotenv.find_dotenv", return_value=None):
                agent = CognitiveDispositionAgent(
                    project_root=tmp_path,
                    llm_enabled=False,  # Explicitly disable LLM
                )

            assert agent.api_key is None

            # Create test file
            test_file = tmp_path / "TestValidatorAgent.py"
            test_file.write_text("# Validator agent")

            # Should use heuristics
            decision = agent.analyze_violation(test_file, "ORPHAN")

            # Validator pattern should suggest L5_safety
            assert decision.action == "MOVE"
            assert "L5_safety" in decision.target_path

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key


class TestPhase14Integration:
    """Phase 14 Tests: Full integration verification."""

    def test_dotenv_import_optional(self, tmp_path):
        """[Phase 14] Verify agent works without python-dotenv installed."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock ImportError for dotenv
            with patch("builtins.__import__", side_effect=ImportError("No module named 'dotenv'")):
                # Should not crash
                agent = CognitiveDispositionAgent(project_root=tmp_path)

                assert agent.api_key is None

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_api_key_validation_success_log(self, tmp_path, caplog):
        """[Phase 14] Verify success message when API key is configured."""
        import logging

        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        with caplog.at_level(logging.INFO):
            agent = CognitiveDispositionAgent(
                project_root=tmp_path,
                api_key="test_key",
            )

        # Should have logged success
        assert any("API key configured successfully" in record.message for record in caplog.records)

    def test_env_loading_with_project_root(self, tmp_path):
        """[Phase 14] Verify .env loading respects project_root."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Create .env in project root
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY='project_root_key'")

        # Clear env var
        original_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            # Mock find_dotenv to return our temp .env
            with patch("dotenv.find_dotenv", return_value=str(env_file)):
                agent = CognitiveDispositionAgent(project_root=tmp_path)

                # Should load from project root .env
                assert agent.api_key == "project_root_key"

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_priority_order(self, tmp_path):
        """[Phase 14] Verify priority: manual > env var > .env file."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        # Create .env
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY='dotenv_key'")

        original_key = os.environ.get("GEMINI_API_KEY")

        try:
            # Test 1: Manual key wins
            agent1 = CognitiveDispositionAgent(
                project_root=tmp_path,
                api_key="manual_key",
            )
            assert agent1.api_key == "manual_key"

            # Test 2: Env var wins over .env
            os.environ["GEMINI_API_KEY"] = "env_var_key"
            agent2 = CognitiveDispositionAgent(project_root=tmp_path)
            assert agent2.api_key == "env_var_key"

            # Test 3: .env file used when no env var
            os.environ.pop("GEMINI_API_KEY", None)
            with patch("dotenv.find_dotenv", return_value=str(env_file)):
                agent3 = CognitiveDispositionAgent(project_root=tmp_path)
                assert agent3.api_key == "dotenv_key"

        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
            else:
                os.environ.pop("GEMINI_API_KEY", None)
