"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

import pytest
import json
from pathlib import Path
from tests.helpers.robust_fs import robust_rmtree
from unittest.mock import patch, MagicMock, mock_open

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    enforce_protected_root,
    SourceMutationBlocked,
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
