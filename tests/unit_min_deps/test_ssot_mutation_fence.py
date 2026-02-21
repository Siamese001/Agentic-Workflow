"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

import pytest
from pathlib import Path
from tests.helpers.robust_fs import robust_rmtree
from unittest.mock import patch, MagicMock

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
