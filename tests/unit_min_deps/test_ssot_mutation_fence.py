"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

import pytest
import json
from pathlib import Path
from tests.helpers.robust_fs import robust_rmtree
from unittest.mock import patch, MagicMock, mock_open

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    enforce_protected_root,
    SourceMutationBlocked,
    ProtectedRootPolicy,
    get_default_protected_root_policy,
)
from agentic_core.L2_execution.tools import write_gateway


@pytest.mark.unit_min_deps
class TestProtectedRootEnforcement:
    """Test protected-root enforcement primitives."""

    def test_enforce_protected_root_blocks_agentic_core(self):
        """Test that writes to agentic_core are blocked."""
        target_path = Path("agentic_core/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_allows_outside(self):
        """Test that writes outside protected roots are allowed."""
        target_path = Path("docs/evidence/test.md")
        # Should not raise
        enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_override_allows(self):
        """Test that override allows writes to protected roots."""
        target_path = Path("agentic_core/test_file.py")
        # Should not raise when override is enabled
        enforce_protected_root(target_path, allow_override=True)

    def test_enforce_protected_root_blocks_tests(self):
        """Test that writes to tests directory are blocked."""
        target_path = Path("tests/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_blocks_github(self):
        """Test that writes to .github directory are blocked."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)
    
    def test_exception_includes_matched_root_agentic_core(self):
        """Test that exception message includes the matched immutable root."""
        target_path = Path("agentic_core/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)
    
    def test_exception_includes_matched_root_tests(self):
        """Test that exception message includes matched root for tests directory."""
        target_path = Path("tests/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="matched_root=tests"):
            enforce_protected_root(target_path, allow_override=False)
    
    def test_exception_includes_matched_root_github(self):
        """Test that exception message includes matched root for .github directory."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match=r"matched_root=\.github"):
            enforce_protected_root(target_path, allow_override=False)


@pytest.mark.unit_min_deps
class TestWriteGatewayIntegration:
    """Test write gateway integration with protected-root enforcement."""

    @patch("pathlib.Path.write_text")
    def test_write_gateway_blocks_protected_root(self, mock_write):
        """Test that write_gateway blocks protected root writes."""
        target_path = Path("agentic_core/test_file.py")
        
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_text(target_path, "test content")
        
        # Ensure no actual write occurred
        mock_write.assert_not_called()

    @patch("pathlib.Path.write_text")
    def test_write_gateway_allows_outside_protected_root(self, mock_write):
        """Test that write_gateway allows writes outside protected roots."""
        target_path = Path("docs/evidence/test.md")
        
        # Should not raise
        write_gateway.write_text(target_path, "test content")
        
        # Verify write was attempted
        mock_write.assert_called_once_with("test content", encoding="utf-8")

    @patch("pathlib.Path.write_bytes")
    def test_write_bytes_blocks_protected_root(self, mock_write):
        """Test that write_bytes blocks protected root writes."""
        target_path = Path("agentic_core/test_file.bin")
        
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_bytes(target_path, b"test data")
        
        # Ensure no actual write occurred
        mock_write.assert_not_called()


@pytest.mark.unit_min_deps
class TestBlockEventEmission:
    """Test block event emission to JSONL log."""
    
    def test_block_emits_jsonl_event(self, tmp_path):
        """Test that a block attempt produces exactly one JSONL line with required fields."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "blocks.jsonl"
        
        # Monkeypatch the log path
        with patch("agentic_core.L0_routing.enforcement.mutation_prohibition.Path") as mock_path_cls:
            # Make Path() constructor work normally for target_path
            mock_path_cls.side_effect = lambda x: Path(x) if x != "logs/ssot_protected_root_blocks.jsonl" else log_file
            
            # Also need to patch the open call to use our tmp_path
            original_open = open
            def patched_open(path, *args, **kwargs):
                if "logs/ssot_protected_root_blocks.jsonl" in str(path):
                    return original_open(log_file, *args, **kwargs)
                return original_open(path, *args, **kwargs)
            
            with patch("builtins.open", side_effect=patched_open):
                with pytest.raises(SourceMutationBlocked):
                    enforce_protected_root(target_path, allow_override=False)
        
        # Verify JSONL event was written
        assert log_file.exists()
        lines = log_file.read_text().strip().split('\n')
        assert len(lines) == 1
        
        # Parse and verify event structure
        event = json.loads(lines[0])
        assert "ts_utc" in event
        assert "target" in event
        assert "matched_root" in event
        assert event["matched_root"] == "agentic_core"
        assert "caller" in event
        assert event["caller"] == "mutation_prohibition:enforce_protected_root"
    
    def test_logging_failure_does_not_mask_exception(self):
        """Test that logging failures do not mask SourceMutationBlocked."""
        target_path = Path("agentic_core/test_file.py")
        
        # Monkeypatch open to raise an exception
        with patch("builtins.open", side_effect=PermissionError("Simulated logging failure")):
            # Should still raise SourceMutationBlocked, not PermissionError
            with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                enforce_protected_root(target_path, allow_override=False)
    
    def test_exception_message_still_includes_diagnostics(self):
        """Test that exception message still includes target and matched_root after adding emission."""
        target_path = Path("tests/test_file.py")
        
        try:
            enforce_protected_root(target_path, allow_override=False)
            assert False, "Should have raised SourceMutationBlocked"
        except SourceMutationBlocked as e:
            msg = str(e)
            assert "target=" in msg
            assert "matched_root=tests" in msg


@pytest.mark.unit_min_deps
class TestPolicyContract:
    """Test protected-root policy contract and configurability."""
    
    def test_default_policy_immutable_roots(self):
        """Test that default policy has exactly the canonical immutable roots."""
        policy = get_default_protected_root_policy()
        assert policy.immutable_roots == ("agentic_core", "tests", ".github")
    
    def test_default_policy_log_path(self):
        """Test that default policy has the canonical log path."""
        policy = get_default_protected_root_policy()
        assert policy.log_path == "logs/ssot_protected_root_blocks.jsonl"
    
    def test_policy_override_log_path_writes_to_tmp(self, tmp_path):
        """Test that overriding policy.log_path writes JSONL to tmp_path (no writes to repo logs)."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"
        
        # Create custom policy with tmp_path log
        custom_policy = ProtectedRootPolicy(
            immutable_roots=("agentic_core", "tests", ".github"),
            log_path=str(log_file)
        )
        
        # Ensure tmp log doesn't exist before test
        assert not log_file.exists()
        
        # Attempt block with custom policy
        with pytest.raises(SourceMutationBlocked):
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)
        
        # Verify JSONL was written to tmp_path
        assert log_file.exists()
        
        # Verify event structure
        lines = log_file.read_text().strip().split('\n')
        assert len(lines) == 1  # Exactly one event written
        event = json.loads(lines[0])
        assert event["matched_root"] == "agentic_core"
        assert "target" in event
        assert "ts_utc" in event
        assert "caller" in event
    
    def test_policy_override_immutable_roots_changes_matched_root(self, tmp_path):
        """Test that changing policy.immutable_roots changes matched_root in exception and event."""
        target_path = Path("custom_protected/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"
        
        # Create custom policy with different immutable roots
        custom_policy = ProtectedRootPolicy(
            immutable_roots=("custom_protected",),
            log_path=str(log_file)
        )
        
        # Attempt block with custom policy
        try:
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)
            assert False, "Should have raised SourceMutationBlocked"
        except SourceMutationBlocked as e:
            msg = str(e)
            assert "matched_root=custom_protected" in msg
        
        # Verify event has correct matched_root
        assert log_file.exists()
        lines = log_file.read_text().strip().split('\n')
        event = json.loads(lines[-1])
        assert event["matched_root"] == "custom_protected"
    
    def test_policy_none_uses_default(self):
        """Test that policy=None uses the default policy."""
        target_path = Path("agentic_core/test_file.py")
        
        # Should block with default policy
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False, policy=None)
