"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

print("DEBUG: test_ssot_mutation_fence.py is being imported")

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    enforce_protected_root,
    SourceMutationBlocked,
)
from agentic_core.L2_execution.tools import write_gateway


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

    def test_write_gateway_override_context(self):
        """Test that global override context works."""
        target_path = Path("agentic_core/test_file.py")
        
        # Set override to True
        write_gateway.set_protected_root_override(True)
        assert write_gateway.get_protected_root_override() is True
        
        # Should not raise when override is enabled
        with patch("pathlib.Path.write_text"):
            write_gateway.write_text(target_path, "test content")
        
        # Reset override
        write_gateway.set_protected_root_override(False)
        assert write_gateway.get_protected_root_override() is False


class TestCLIOverride:
    """Test CLI override functionality."""

    @patch("agentic_core.L0_routing.scripts.execute_ssot._legacy_main")
    @patch("sys.argv", ["execute_ssot.py", "--allow-protected-root-mutation"])
    @patch("builtins.print")
    def test_cli_override_enables_protection_override(self, mock_print, mock_legacy_main):
        """Test that CLI flag enables protected root override."""
        from agentic_core.L0_routing.scripts.execute_ssot import main
        
        # Import and run main
        result = main()
        
        # Verify override was logged
        mock_print.assert_any_call("[PROTECTED-ROOT] override ENABLED: protected root mutation permitted")
        
        # Verify _legacy_main was called with override=True
        mock_legacy_main.assert_called_once()
        args, kwargs = mock_legacy_main.call_args
        assert kwargs.get("allow_protected_root_mutation") is True

    @patch("agentic_core.L0_routing.scripts.execute_ssot._legacy_main")
    @patch("sys.argv", ["execute_ssot.py"])
    @patch("builtins.print")
    def test_cli_default_disables_protection_override(self, mock_print, mock_legacy_main):
        """Test that default CLI state disables protected root override."""
        from agentic_core.L0_routing.scripts.execute_ssot import main
        
        # Import and run main
        result = main()
        
        # Verify override was logged as disabled
        mock_print.assert_any_call("[PROTECTED-ROOT] override DISABLED: protected root mutation blocked")
        
        # Verify _legacy_main was called with override=False
        mock_legacy_main.assert_called_once()
        args, kwargs = mock_legacy_main.call_args
        assert kwargs.get("allow_protected_root_mutation") is False


class TestDomainTargeting:
    """Test domain targeting hardening."""

    @patch("agentic_core.L0_routing.scripts.execute_ssot.execute_phase1_discovery")
    @patch("agentic_core.L0_routing.scripts.execute_ssot.set_protected_root_override")
    @patch("builtins.print")
    def test_domains_mode_forces_dry_run_for_protected_domains(self, mock_print, mock_set_override, mock_phase1):
        """Test that domains mode forces dry_run=True for protected domains."""
        from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main
        
        # Mock args for domains mode without override
        mock_args = MagicMock()
        mock_args.domains = True
        mock_args.dry_run = False
        mock_args.interactive = False
        mock_args.manual = False
        mock_args.territory = None
        mock_args.enable_cda = False
        
        # Mock the argument parser
        with patch("argparse.ArgumentParser.parse_known_args") as mock_parse:
            mock_parse.return_value = (mock_args, [])
            
            # Mock project root
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path("/test")):
                # Create test domain directory
                (Path("/test") / "agentic_core" / "L0_routing").mkdir(parents=True, exist_ok=True)
                
                try:
                    _legacy_main(repo_root=Path("/test"), allow_protected_root_mutation=False)
                except SystemExit:
                    pass
        
        # Verify dry_run was forced and warning was printed
        mock_print.assert_any_call("[PROTECTED-ROOT] domain L0_routing forced dry_run=True (protected root)")
        mock_set_override.assert_called_once_with(False)


class TestImportPreflight:
    """Test import preflight functionality."""

    @patch("importlib.import_module")
    def test_import_preflight_fails_fast_on_missing_symbol(self, mock_import):
        """Test that preflight check fails fast when _legacy_main is missing."""
        from agentic_core.L0_routing.scripts.execute_ssot import _preflight_import_check
        
        # Mock module without _legacy_main
        mock_module = MagicMock()
        del mock_module._legacy_main  # Remove the attribute
        mock_import.return_value = mock_module
        
        with pytest.raises(RuntimeError, match="Symbol '_legacy_main' not found in module"):
            _preflight_import_check()

    @patch("importlib.import_module")
    def test_import_preflight_fails_fast_on_missing_module(self, mock_import):
        """Test that preflight check fails fast when module is missing."""
        from agentic_core.L0_routing.scripts.execute_ssot import _preflight_import_check
        
        # Mock import failure
        mock_import.side_effect = ImportError("No module named 'test'")
        
        with pytest.raises(RuntimeError, match="Failed to import module"):
            _preflight_import_check()

    @patch("importlib.import_module")
    def test_import_preflight_succeeds_when_symbol_exists(self, mock_import):
        """Test that preflight check succeeds when symbol exists."""
        from agentic_core.L0_routing.scripts.execute_ssot import _preflight_import_check
        
        # Mock module with _legacy_main
        mock_module = MagicMock()
        mock_module._legacy_main = MagicMock()
        mock_import.return_value = mock_module
        
        # Should not raise
        _preflight_import_check()
