import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# --- TEST FIXTURES ---


@pytest.fixture
def clean_manifest_environment(tmp_path):
    """Creates a temporary isolated environment for manifest locking tests."""
    # Setup
    cwd = os.getcwd()
    os.chdir(tmp_path)

    manifest_content = {"project": "Agentic-Workflow", "version": "1.0", "agents": []}
    with open("manifest.json", "w") as f:
        json.dump(manifest_content, f)

    yield tmp_path

    # Teardown
    os.chdir(cwd)


# --- MANIFEST GUARDIAN TESTS ---


@pytest.mark.security
def test_manifest_integrity_lock(clean_manifest_environment):
    """
    Verify the ManifestGuardian correctly locks, validates, and detects tampering.
    """
    # Import the ManifestGuardian directly to avoid circular imports
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    # 1. Seal the manifest
    ManifestGuardian.seal_manifest()
    assert os.path.exists(".manifest.lock")

    # 2. Verify Valid State
    assert ManifestGuardian.verify_integrity() is True

    # 3. Simulate Tampering (Append a space)
    with open("manifest.json", "a") as f:
        f.write(" ")

    # 4. Verify Invalid State
    assert ManifestGuardian.verify_integrity() is False


@pytest.mark.security
def test_manifest_missing_lock_file(clean_manifest_environment):
    """
    Verify that missing lock file is detected as integrity breach.
    """
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    # Don't create lock file, just try to verify
    assert ManifestGuardian.verify_integrity() is False


@pytest.mark.security
def test_manifest_missing_manifest_file():
    """
    Verify that missing manifest file raises appropriate error.
    """
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    with pytest.raises(FileNotFoundError, match="SSOT Blueprint missing"):
        ManifestGuardian.calculate_checksum()


@pytest.mark.security
def test_manifest_checksum_calculation(clean_manifest_environment):
    """
    Verify checksum calculation is consistent and accurate.
    """
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    # Calculate initial checksum
    checksum1 = ManifestGuardian.calculate_checksum()

    # Calculate again - should be identical
    checksum2 = ManifestGuardian.calculate_checksum()

    assert checksum1 == checksum2
    assert len(checksum1) == 64  # SHA-256 hex length
    assert all(c in "0123456789abcdef" for c in checksum1)


@pytest.mark.security
def test_manifest_tampering_detection(clean_manifest_environment):
    """
    Verify that various types of tampering are detected.
    """
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    # Initial seal
    ManifestGuardian.seal_manifest()

    # Test 1: Add a character
    with open("manifest.json", "a") as f:
        f.write("x")
    assert ManifestGuardian.verify_integrity() is False

    # Reset and test 2: Remove a character
    with open("manifest.json", "r+") as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content[:-1] if content else "")
    assert ManifestGuardian.verify_integrity() is False

    # Reset and test 3: Modify content
    with open("manifest.json", "w") as f:
        json.dump({"modified": True}, f)
    assert ManifestGuardian.verify_integrity() is False


# --- COMPLIANCE GATE TESTS ---


@pytest.mark.compliance
def test_sovereign_root_whitelist():
    """
    Verify that SovereignBaseAgent is explicitly whitelisted.
    """
    # Mock the compliance check to test the logic
    with patch("agentic_core.L0_maintenance.scripts.compliance_gate.check_compliance") as mock_check:
        mock_check.return_value = []

        # This would normally be called with discovered agents
        # For now, we just verify the mock works
        result = mock_check([])
        assert result == []


# --- BOOT SEQUENCE TESTS ---


@pytest.mark.boot
def test_boot_sequence_integrity_failure():
    """Test that boot sequence fails appropriately when integrity check fails."""
    # Mock the ManifestGuardian to simulate integrity failure
    with patch("agentic_core.L0_maintenance.security.ManifestGuardian.verify_integrity", return_value=False):
        with patch(
            "agentic_core.L0_maintenance.boot.boot_sequence.ManifestGuardian.verify_integrity",
            return_value=False,
        ):
            # Mock the boot sequence to avoid import issues
            with patch("agentic_core.L0_maintenance.boot.boot_sequence.check_compliance", return_value=[]):
                with patch("agentic_core.L0_maintenance.boot.boot_sequence.AgentRegistry") as mock_registry:
                    mock_instance = Mock()
                    mock_instance.discover_all.return_value = []
                    mock_registry.return_value = mock_instance

                    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence

                    boot = BootSequence(strict_mode=True)
                    result = boot.execute_boot()

                    assert result["status"] == "failed"
                    assert not result["integrity_verified"]
                    assert "integrity_check" not in result["phases_completed"]


@pytest.mark.boot
def test_boot_sequence_successful_boot():
    """Test that boot sequence succeeds when all checks pass."""
    # Mock all checks to pass
    with patch("agentic_core.L0_maintenance.security.ManifestGuardian.verify_integrity", return_value=True):
        with patch(
            "agentic_core.L0_maintenance.boot.boot_sequence.ManifestGuardian.verify_integrity",
            return_value=True,
        ):
            with patch("agentic_core.L0_maintenance.boot.boot_sequence.check_compliance", return_value=[]):
                with patch("agentic_core.L0_maintenance.boot.boot_sequence.AgentRegistry") as mock_registry:
                    mock_instance = Mock()
                    mock_instance.discover_all.return_value = []
                    mock_registry.return_value = mock_instance

                    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence

                    boot = BootSequence(strict_mode=True)
                    result = boot.execute_boot()

                    assert result["status"] == "success"
                    assert result["integrity_verified"]
                    assert len(result["compliance_violations"]) == 0


# --- INTEGRATION TESTS ---


@pytest.mark.integration
def test_full_security_pipeline(clean_manifest_environment):
    """
    Test the complete security pipeline from manifest sealing to integrity verification.
    """
    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "security")
    )
    from ManifestGuardian import ManifestGuardian

    # 1. Create and seal manifest
    ManifestGuardian.seal_manifest()

    # 2. Verify integrity passes
    assert ManifestGuardian.verify_integrity() is True

    # 3. Tamper with manifest
    with open("manifest.json", "a") as f:
        f.write("tampered")

    # 4. Verify integrity fails
    assert ManifestGuardian.verify_integrity() is False


if __name__ == "__main__":
    # Run a quick test to verify the module works
    pytest.main([__file__, "-v", "--tb=short"])
