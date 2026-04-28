"""Tests for boot_sequence.py module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.boot_sequence import (
    check_compliance,
    BootSequence,
    main,
    boot_sequence,
)


class TestCheckCompliance:
    """Tests for check_compliance function."""

    def test_check_compliance_empty_agents(self):
        """Test check_compliance with empty agents list."""
        result = check_compliance([])
        assert result == []

    def test_check_compliance_none_agents(self):
        """Test check_compliance with None agents."""
        result = check_compliance(None)
        assert result == []

    def test_check_compliance_with_agents(self):
        """Test check_compliance with agents list."""
        agents = [{"name": "agent1"}, {"name": "agent2"}]
        result = check_compliance(agents)
        assert result == []

    def test_check_compliance_non_iterable(self):
        """Test check_compliance with non-iterable input."""
        result = check_compliance("not_a_list")
        assert result == []


class TestBootSequence:
    """Tests for BootSequence class."""

    def test_boot_sequence_init_default_strict(self):
        """Test BootSequence initialization with default strict mode."""
        boot = BootSequence()
        assert boot.strict_mode is True

    def test_boot_sequence_init_strict_false(self):
        """Test BootSequence initialization with strict mode disabled."""
        boot = BootSequence(strict_mode=False)
        assert boot.strict_mode is False

    def test_boot_sequence_init_creates_registry(self):
        """Test BootSequence initialization creates registry."""
        boot = BootSequence()
        assert boot.registry is not None
        assert boot.discovered_agents == []
        assert boot.compliance_violations == []

    def test_boot_sequence_execute_boot_success(self):
        """Test execute_boot with successful boot."""
        boot = BootSequence(strict_mode=False)
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = True
            boot.registry = MagicMock()
            boot.registry.discover_all.return_value = []
            
            result = boot.execute_boot()
            
            assert result["status"] == "success"
            assert result["integrity_verified"] is True
            assert "cryptographic_handshake" in result["phases_completed"]

    def test_boot_sequence_execute_boot_integrity_failure(self):
        """Test execute_boot with integrity failure."""
        boot = BootSequence()
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = False
            
            with pytest.raises(SystemExit):
                boot.execute_boot()

    def test_boot_sequence_execute_boot_strict_mode_violations(self):
        """Test execute_boot with violations in strict mode raises RuntimeError."""
        boot = BootSequence(strict_mode=True)
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = True
            boot.registry = MagicMock()
            boot.registry.discover_all.return_value = []
            
            with patch("agentic_core.L0_routing.enforcement.boot_sequence.check_compliance") as mock_check:
                mock_check.return_value = ["violation1", "violation2"]
                
                with pytest.raises(RuntimeError, match="Compliance violations"):
                    boot.execute_boot()

    def test_boot_sequence_execute_boot_non_strict_mode_violations(self):
        """Test execute_boot with violations in non-strict mode continues."""
        boot = BootSequence(strict_mode=False)
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = True
            boot.registry = MagicMock()
            boot.registry.discover_all.return_value = []
            
            with patch("agentic_core.L0_routing.enforcement.boot_sequence.check_compliance") as mock_check:
                mock_check.return_value = ["violation1"]
                
                result = boot.execute_boot()
                
                assert result["status"] == "success"
                assert result["compliance_violations"] == ["violation1"]

    def test_boot_sequence_execute_boot_runtime_error(self):
        """Test execute_boot handles RuntimeError gracefully."""
        boot = BootSequence(strict_mode=False)
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = True
            boot.registry = MagicMock()
            boot.registry.discover_all.side_effect = RuntimeError("Registry error")
            
            result = boot.execute_boot()
            
            assert result["status"] == "failed"
            assert "Registry error" in result["errors"]

    def test_boot_sequence_execute_boot_os_error(self):
        """Test execute_boot handles OSError gracefully."""
        boot = BootSequence(strict_mode=False)
        
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.ManifestGuardian") as mock_guardian:
            mock_guardian.verify_integrity.return_value = True
            boot.registry = MagicMock()
            boot.registry.discover_all.side_effect = OSError("File error")
            
            result = boot.execute_boot()
            
            assert result["status"] == "failed"
            assert "File error" in result["errors"]

    def test_boot_sequence_module_instance(self):
        """Test that boot_sequence instance is created at module level."""
        assert boot_sequence is not None
        assert isinstance(boot_sequence, BootSequence)


class TestMain:
    """Tests for main function."""

    def test_main_success(self):
        """Test main with successful boot."""
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.BootSequence") as mock_boot_class:
            mock_boot = MagicMock()
            mock_boot_class.return_value = mock_boot
            mock_boot.execute_boot.return_value = {"status": "success"}
            
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_once_with(0)

    def test_main_failure(self):
        """Test main with failed boot."""
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.BootSequence") as mock_boot_class:
            mock_boot = MagicMock()
            mock_boot_class.return_value = mock_boot
            mock_boot.execute_boot.return_value = {"status": "failed"}
            
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_once_with(1)

    def test_main_system_exit(self):
        """Test main with SystemExit during boot."""
        with patch("agentic_core.L0_routing.enforcement.boot_sequence.BootSequence") as mock_boot_class:
            mock_boot = MagicMock()
            mock_boot_class.return_value = mock_boot
            mock_boot.execute_boot.side_effect = SystemExit("Aborted")
            
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_once()
