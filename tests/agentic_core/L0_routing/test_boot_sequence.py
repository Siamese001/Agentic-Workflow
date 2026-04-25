"""Tests for L0_routing.enforcement.boot_sequence module."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement import boot_sequence


class TestBootSequence:
    """Test suite for L0 boot sequence orchestration."""

    def setup_method(self):
        """Reset boot sequence state before each test."""
        # Create a new instance for each test
        self.boot = boot_sequence.BootSequence(strict_mode=False)

    def test_boot_sequence_init(self):
        """Test BootSequence initialization."""
        boot = boot_sequence.BootSequence(strict_mode=True)
        assert boot.strict_mode is True
        assert boot.registry is not None
        assert boot.discovered_agents == []
        assert boot.compliance_violations == []

    def test_boot_sequence_init_non_strict(self):
        """Test BootSequence initialization with non-strict mode."""
        boot = boot_sequence.BootSequence(strict_mode=False)
        assert boot.strict_mode is False

    def test_execute_boot_success(self):
        """Test successful boot execution."""
        # Mock the dependencies
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=True
        ):
            with patch.object(
                self.boot.registry, "discover_all", return_value=["agent1", "agent2"]
            ):
                result = self.boot.execute_boot()
                assert result["status"] == "success"
                assert result["agents_discovered"] == 2
                assert result["integrity_verified"] is True
                assert "cryptographic_handshake" in result["phases_completed"]

    def test_execute_boot_integrity_failure(self):
        """Test boot execution fails on integrity check."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=False
        ):
            with pytest.raises(SystemExit):
                self.boot.execute_boot()

    def test_execute_boot_compliance_violation_strict(self):
        """Test boot execution fails on compliance violations in strict mode."""
        boot = boot_sequence.BootSequence(strict_mode=True)
        
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=True
        ):
            with patch.object(
                boot.registry, "discover_all", return_value=["agent1"]
            ):
                with patch.object(
                    boot_sequence, "check_compliance", return_value=["violation1"]
                ):
                    with pytest.raises(RuntimeError, match="Compliance violations detected"):
                        boot.execute_boot()

    def test_execute_boot_compliance_violation_non_strict(self):
        """Test boot execution continues with violations in non-strict mode."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=True
        ):
            with patch.object(
                self.boot.registry, "discover_all", return_value=["agent1"]
            ):
                with patch.object(
                    boot_sequence, "check_compliance", return_value=["violation1"]
                ):
                    result = self.boot.execute_boot()
                    assert result["status"] == "success"
                    assert result["compliance_violations"] == ["violation1"]

    def test_execute_boot_runtime_error(self):
        """Test boot execution handles runtime errors gracefully."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", side_effect=OSError("Test error")
        ):
            result = self.boot.execute_boot()
            assert result["status"] == "failed"
            assert len(result["errors"]) > 0

    def test_check_compliance_empty_agents(self):
        """Test check_compliance with empty agent list."""
        violations = boot_sequence.check_compliance([])
        assert violations == []

    def test_check_compliance_non_iterable(self):
        """Test check_compliance handles non-iterable input gracefully."""
        violations = boot_sequence.check_compliance(None)
        assert violations == []

    def test_check_compliance_with_agents(self):
        """Test check_compliance with agent list (placeholder)."""
        violations = boot_sequence.check_compliance(["agent1", "agent2"])
        # Placeholder implementation returns empty list
        assert violations == []

    def test_main_function(self):
        """Test main entry point."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=True
        ):
            with patch.object(
                boot_sequence.boot_sequence.registry, "discover_all", return_value=[]
            ):
                with patch("sys.exit") as mock_exit:
                    boot_sequence.main()
                    mock_exit.assert_called_once_with(0)

    def test_main_function_boot_failed(self):
        """Test main function exits with error on boot failure."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=False
        ):
            with patch("sys.exit") as mock_exit:
                boot_sequence.main()
                mock_exit.assert_called_once_with(1)

    def test_boot_sequence_instance(self):
        """Test module-level boot_sequence instance exists."""
        assert boot_sequence.boot_sequence is not None
        assert isinstance(boot_sequence.boot_sequence, boot_sequence.BootSequence)

    def test_execute_boot_phases_completed(self):
        """Test that all expected phases are marked as completed."""
        with patch.object(
            boot_sequence.ManifestGuardian, "verify_integrity", return_value=True
        ):
            with patch.object(
                self.boot.registry, "discover_all", return_value=[]
            ):
                result = self.boot.execute_boot()
                expected_phases = [
                    "cryptographic_handshake",
                    "discovery_compliance",
                    "sovereignty",
                    "runtime",
                ]
                for phase in expected_phases:
                    assert phase in result["phases_completed"]
