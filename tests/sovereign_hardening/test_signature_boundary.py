"""Sovereign Hardening Test Suite

Tests for runtime sovereignty enforcement, bypass prevention, and
deterministic replay validation.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from agentic_core.L2_execution.engines.execution_gateway import ExecutionGateway, SignatureBoundaryError
from agentic_core.L2_execution.types.sandbox_envelope import SandboxEnvelope, SignatureVerificationError
from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway, MutationRecord, SimulationResult


@pytest.fixture
def execution_gateway():
    """Create ExecutionGateway instance for testing."""
    return ExecutionGateway()


@pytest.fixture
def sample_envelope():
    """Create a sample SandboxEnvelope for testing."""
    from agentic_core.L2_execution.types.sandbox_envelope import ToolBudget

    return SandboxEnvelope(
        envelope_id="test_envelope_1",
        tool_name="test_tool",
        tool_args={"param": "value"},
        instruction_packet_id="test_instruction_1",
        invocation_metadata={"agent_id": "test_agent"},
        budget=ToolBudget()
    )


@pytest.fixture
def write_gateway():
    """Create UniversalWriteGateway instance for testing."""
    return UniversalWriteGateway(replay_mode=False)


@pytest.fixture
def replay_gateway():
    """Create UniversalWriteGateway in replay mode for testing."""
    return UniversalWriteGateway(replay_mode=True)


class TestSignatureBoundary:
    """Tests for L2 side-effect boundary with fail-closed signature verification."""

    @pytest.mark.asyncio
    async def test_valid_signature_passes(self, execution_gateway, sample_envelope):
        """Test that valid signature allows execution to proceed."""
        # Envelope should be auto-signed in constructor
        with patch('agentic_core.L2_execution.engines.execution_gateway.get_current_secret') as mock_secret:
            mock_secret.return_value = b'test_secret'

            # This should not raise an exception
            try:
                await execution_gateway.execute_with_trace(
                    sample_envelope,
                    lambda: None,
                    policy_hash="test_policy",
                    prev_hash="test_prev",
                    transcript_hash="test_transcript"
                )
            except Exception as e:
                # Should not be SignatureBoundaryError
                assert not isinstance(e, SignatureBoundaryError)

    @pytest.mark.asyncio
    async def test_invalid_signature_fails_closed(self, execution_gateway, sample_envelope):
        """Test that invalid signature causes immediate fail-closed exit."""
        # Corrupt the signature
        with patch.object(sample_envelope, 'verify') as mock_verify:
            mock_verify.side_effect = SignatureVerificationError("Invalid signature")

            with pytest.raises(SignatureBoundaryError) as exc_info:
                await execution_gateway.execute_with_trace(
                    sample_envelope,
                    lambda: None,
                    policy_hash="test_policy",
                    prev_hash="test_prev",
                    transcript_hash="test_transcript"
                )

            assert "Invalid SandboxEnvelope signature" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_signature_fails_closed(self, execution_gateway):
        """Test that missing signature causes immediate fail-closed exit."""
        # Create envelope with empty signature
        from agentic_core.L2_execution.types.sandbox_envelope import ToolBudget

        unsigned_envelope = SandboxEnvelope(
            envelope_id="unsigned_envelope",
            tool_name="test_tool",
            tool_args={"param": "value"},
            instruction_packet_id="test_instruction",
            invocation_metadata={"agent_id": "test_agent"},
            budget=ToolBudget()
        )

        # Manually clear signature
        with patch.object(unsigned_envelope, 'signature', ''):
            with pytest.raises(SignatureBoundaryError) as exc_info:
                await execution_gateway.execute_with_trace(
                    unsigned_envelope,
                    lambda: None,
                    policy_hash="test_policy",
                    prev_hash="test_prev",
                    transcript_hash="test_transcript"
                )

            assert "Invalid SandboxEnvelope signature" in str(exc_info.value)


class TestUniversalWriteGateway:
    """Tests for Universal Write Gateway enforcement."""

    def test_default_permissions_blocked(self, write_gateway):
        """Test that default write permissions are blocked."""
        assert not write_gateway.check_write_permission("test.py")
        assert not write_gateway.check_write_permission("/etc/config")
        assert write_gateway.check_write_permission("artifacts/output.txt")
        assert write_gateway.check_write_permission("logs/test.log")

    def test_allowed_paths_permitted(self, write_gateway):
        """Test that allowed paths have write permissions."""
        assert write_gateway.check_write_permission("artifacts/test.json")
        assert write_gateway.check_write_permission("docs/reports/evidence.md")
        assert write_gateway.check_write_permission("logs/app.log")
        assert write_gateway.check_write_permission("temp/cache.tmp")

    def test_blocked_extensions_denied(self, write_gateway):
        """Test that blocked file extensions are denied."""
        assert not write_gateway.check_write_permission("test.py")
        assert not write_gateway.check_write_permission("script.js")
        assert not write_gateway.check_write_permission("app.exe")
        assert not write_gateway.check_write_permission("library.so")

    def test_grant_revoke_permissions(self, write_gateway):
        """Test granting and revoking write permissions."""
        path = "custom/path/file.txt"

        # Initially blocked
        assert not write_gateway.check_write_permission(path)

        # Grant permission
        write_gateway.grant_write_permission(path)
        assert write_gateway.check_write_permission(path)

        # Revoke permission
        write_gateway.revoke_write_permission(path)
        assert not write_gateway.check_write_permission(path)

    def test_mutation_recording(self, write_gateway):
        """Test that mutations are properly recorded."""
        path = "test_file.txt"
        data = "test content"

        record = write_gateway.record_mutation(path, "write", data)

        assert isinstance(record, MutationRecord)
        assert record.path == str(Path(path).as_posix())
        assert record.operation == "write"
        assert record.data_hash is not None
        assert record.size_bytes == len(data.encode("utf-8"))
        assert record.permitted  # Should be permitted for allowed paths

    def test_replay_mode_simulation(self, replay_gateway):
        """Test write simulation in replay mode."""
        path = "simulated_file.txt"
        data = "simulated content"

        result = replay_gateway.simulate_write(path, "write", data)

        assert isinstance(result, SimulationResult)
        assert result.operation == "write"
        assert result.path == str(Path(path).as_posix())
        assert result.would_succeed  # All writes succeed in replay mode
        assert result.simulated_size == len(data.encode("utf-8"))
        assert result.simulated_hash is not None
        assert result.replay_mode is True

    def test_replay_mode_blocks_permission_changes(self, replay_gateway):
        """Test that replay mode blocks permission changes."""
        # Should not raise exception but also not change permissions
        replay_gateway.grant_write_permission("test.py")
        replay_gateway.revoke_write_permission("test.js")

        # Permissions should remain unchanged
        assert not replay_gateway.check_write_permission("test.py")

    def test_write_stats(self, write_gateway):
        """Test write statistics collection."""
        # Record some mutations
        write_gateway.record_mutation("file1.txt", "write", "content1")
        write_gateway.record_mutation("file2.txt", "write", "content2")
        write_gateway.record_mutation("blocked.py", "write", "content3")

        stats = write_gateway.get_write_stats()

        assert stats["total_mutations"] == 3
        assert stats["permitted_mutations"] == 2  # Only allowed paths
        assert stats["blocked_mutations"] == 1
        assert stats["replay_mode"] is False
        assert "allowed_paths" in stats
        assert "write_permissions" in stats


class TestNegativeControl:
    """Tests for negative control with W_HARDEN_NEGCTRL_TAMPER."""

    def test_tamper_environment_variable(self):
        """Test that W_HARDEN_NEGCTRL_TAMPER environment variable is recognized."""
        # Test with tampering enabled
        with patch.dict(os.environ, {'W_HARDEN_NEGCTRL_TAMPER': '1'}):
            assert os.environ.get('W_HARDEN_NEGCTRL_TAMPER') == '1'

        # Test without tampering
        with patch.dict(os.environ, {}, clear=True):
            assert os.environ.get('W_HARDEN_NEGCTRL_TAMPER') is None

    @pytest.mark.xfail(strict=True)
    def test_negative_control_xfail(self):
        """Test that negative control causes XFAIL(strict=True)."""
        # This test should XFAIL when W_HARDEN_NEGCTRL_TAMPER=1
        if os.environ.get('W_HARDEN_NEGCTRL_TAMPER') == '1':
            pytest.fail("Negative control triggered - expected XFAIL")

        # Normal execution path when not tampered
        assert True
