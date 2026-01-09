"""
Tests for MCPHardenedMixin retry and observability.

Validates:
- Exponential backoff retry on transient failures
- CRITIQUE emission on exhausted retries
- Timeout enforcement
- SovereignEvent emission
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestMCPHardenedMixin:
    """Test suite for MCPHardenedMixin."""

    @pytest.fixture
    def mixin_client(self):
        """Create a test client with MCPHardenedMixin."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import (
            MCPHardenedMixin)

        class TestClient():
            MAX_RETRIES = 3
            BASE_DELAY = 0.01  # Fast for testing

        return TestClient()

    @pytest.mark.asyncio
    async def test_successful_call_on_first_attempt(self, mixin_client):
        """Test that successful calls return immediately."""
        mock_call = AsyncMock(return_value={"status": "success"})

        with patch.object(mixin_client, "_emit_sovereign_event"):
            result = await mixin_client._hardened_call(
                "test_op", mock_call
            )

        assert result == {"status": "success"}
        assert mock_call.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self, mixin_client):
        """Test exponential backoff retry on failures."""
        mock_call = AsyncMock(
            side_effect=[Exception("Transient"), {"status": "success"}]
        )

        with patch.object(mixin_client, "_emit_sovereign_event"):
            result = await mixin_client._hardened_call(
                "test_op", mock_call
            )

        assert result == {"status": "success"}
        assert mock_call.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_multiple_failures(self, mixin_client):
        """Test retry through multiple failures before success."""
        mock_call = AsyncMock(
            side_effect=[
                Exception("Fail 1"),
                Exception("Fail 2"),
                {"status": "success"},
            ]
        )

        with patch.object(mixin_client, "_emit_sovereign_event"):
            result = await mixin_client._hardened_call(
                "test_op", mock_call
            )

        assert result == {"status": "success"}
        assert mock_call.call_count == 3

    @pytest.mark.asyncio
    async def test_emit_critique_on_exhaustion(self, mixin_client):
        """Test CRITIQUE emission after all retries fail."""
        mock_call = AsyncMock(side_effect=Exception("Permanent failure"))

        with patch.object(
            mixin_client, "_emit_critique"
        ) as mock_critique:
            with patch.object(mixin_client, "_emit_sovereign_event"):
                with pytest.raises(RuntimeError) as exc_info:
                    await mixin_client._hardened_call(
                        "test_op", mock_call
                    )

            mock_critique.assert_called_once()
            assert "Permanent failure" in mock_critique.call_args[0][1]

        assert "failed after 3 attempts" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_enforcement(self, mixin_client):
        """Test timeout triggers retry."""

        async def slow_call():
            await asyncio.sleep(10)
            return {"status": "never_reached"}

        mock_call = AsyncMock(side_effect=slow_call)

        with patch.object(mixin_client, "_emit_sovereign_event"):
            with patch.object(mixin_client, "_emit_critique"):
                with pytest.raises(RuntimeError) as exc_info:
                    await mixin_client._hardened_call(
                        "test_op", mock_call, timeout=0.01
                    )

        assert "failed after 3 attempts" in str(exc_info.value)
        assert "Timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_sovereign_events_emitted(self, mixin_client):
        """Test that SovereignEvents are emitted on success."""
        mock_call = AsyncMock(return_value={"status": "success"})
        events = []

        def capture_event(event_type, data):
            events.append((event_type, data))

        with patch.object(
            mixin_client, "_emit_sovereign_event", side_effect=capture_event
        ):
            await mixin_client._hardened_call("test_op", mock_call)

        event_types = [e[0] for e in events]
        assert "MCP_CALL_START" in event_types
        assert "MCP_CALL_SUCCESS" in event_types

    @pytest.mark.asyncio
    async def test_sovereign_events_on_failure(self, mixin_client):
        """Test that failure events are emitted."""
        mock_call = AsyncMock(
            side_effect=[Exception("Fail"), {"status": "success"}]
        )
        events = []

        def capture_event(event_type, data):
            events.append((event_type, data))

        with patch.object(
            mixin_client, "_emit_sovereign_event", side_effect=capture_event
        ):
            await mixin_client._hardened_call("test_op", mock_call)

        event_types = [e[0] for e in events]
        assert "MCP_CALL_FAIL" in event_types
        assert "MCP_CALL_SUCCESS" in event_types


class TestSovereignEvents:
    """Test suite for sovereign_events module."""

    def test_emit_event_logs_correctly(self):
        """Test that emit_event logs structured events."""
        from agentic_core.observability.telemetry.sovereign_events import (
            emit_event)

        with patch(
            "agentic_core.observability.telemetry.sovereign_events.logger"
        ) as mock_logger:
            emit_event("TEST_EVENT", {"key": "value"})

            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "SOVEREIGN_EVENT" in log_message
            assert "TEST_EVENT" in log_message

    def test_handler_registration(self):
        """Test external handler registration and invocation."""
        from agentic_core.observability.telemetry.sovereign_events import (
            emit_event,
            register_handler,
            _event_handlers)

        handler_calls = []

        def test_handler(event_type, event_data):
            handler_calls.append((event_type, event_data))

        # Clear any existing handlers
        _event_handlers.clear()
        register_handler(test_handler)

        emit_event("HANDLER_TEST", {"data": 123})

        assert len(handler_calls) == 1
        assert handler_calls[0][0] == "HANDLER_TEST"

        # Clean up
        _event_handlers.clear()


class TestNoHardcodedCredentials:
    """Test to verify no hardcoded credentials in MCP files."""

    def test_neo4j_no_default_password(self):
        """Verify Neo4j store requires password from environment."""
        import os
        from pathlib import Path

        neo4j_file = Path(
            "C:/Git/Agentic-Workflow/agentic_core/config/blueprint_sovereign/graph_store_neo4j.py"
        )
        content = neo4j_file.read_text()

        # Should NOT contain default password
        assert 'NEO4J_PASSWORD", "password"' not in content
        # Should require password from environment
        assert "NEO4J_PASSWORD must be set" in content

    def test_sovereign_env_includes_mcp_vars(self):
        """Verify sovereign_env.py includes MCP configuration."""
        from pathlib import Path

        env_file = Path(
            "C:/Git/Agentic-Workflow/agentic_core/config/blueprint_sovereign/sovereign_env.py"
        )
        content = env_file.read_text()

        # Should include MCP timeout and retry config
        assert "MCP_TIMEOUT_SECONDS" in content
        assert "MCP_MAX_RETRIES" in content
        # Should include Neo4j vars
        assert "NEO4J_URI" in content
        assert "NEO4J_USERNAME" in content


class TestRedisMCPClientHardening:
    """Test Redis MCP client uses MCPHardenedMixin."""

    def test_redis_client_inherits_mixin(self):
        """Verify Redis MCP client inherits MCPHardenedMixin."""
        from pathlib import Path

        redis_file = Path(
            "C:/Git/Agentic-Workflow/agentic_core/L4_state/validation_context/caching_redis_mcp_client.py"
        )
        content = redis_file.read_text()

        # Should import mixin
        assert "MCPHardenedMixin" in content
        # Should inherit from mixin
        assert "sovereign_redis_mcp_client(MCPHardenedMixin)" in content
        # Should use _hardened_call
        assert "_hardened_call" in content
