import pytest
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_core.L0_maintenance.scripts.compliance_gate import check_compliance
from agentic_core.L0_maintenance.security.ManifestGuardian import ManifestGuardian
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.discovery import DiscoveredAgent
from dataclasses import dataclass

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

@pytest.fixture
def mock_sovereign_base_agent():
    """Creates a mock SovereignBaseAgent instance for testing."""
    return Mock(spec=SovereignBaseAgent)

@pytest.fixture
def sample_discovered_agent():
    """Creates a sample discovered agent for testing."""
    @dataclass
    class SampleAgent:
        name: str
        layer: str
        instance: object
        class_ref: type
        
    return SampleAgent

# --- COMPLIANCE TESTS ---

@pytest.mark.compliance
def test_sovereign_root_whitelist():
    """
    Verify that SovereignBaseAgent is explicitly whitelisted and does not 
    trigger a compliance violation despite not inheriting from itself.
    """
    # Create a mock agent that IS the SovereignBaseAgent
    @dataclass
    class MockSovereignRoot:
        name = "SovereignBaseAgent"
        layer = "L0_maintenance"
        instance = Mock()  # Mock instance
        class_ref = type("SovereignBaseAgent", (), {
            "__mro__": (object,)  # Minimal MRO for testing
        })
            
    # Run compliance check
    violations = check_compliance([MockSovereignRoot()])
    
    # Should be 0 violations because of the specific 'name' check
    assert len(violations) == 0, f"SovereignBaseAgent should be whitelisted! Got: {violations}"

@pytest.mark.compliance
def test_sovereign_base_agent_inheritance():
    """
    Verify that agents properly inheriting from SovereignBaseAgent pass compliance.
    """
    @dataclass
    class ValidAgent:
        name = "ValidTestAgent"
        layer = "L1_planning"
        instance = Mock()
        class_ref = type("ValidTestAgent", (SovereignBaseAgent,), {
            "__mro__": (type("ValidTestAgent"), SovereignBaseAgent, object)
        })
    
    violations = check_compliance([ValidAgent()])
    assert len(violations) == 0, f"Valid agent should pass compliance. Got: {violations}"

@pytest.mark.compliance
def test_orphaned_agent_detection():
    """
    Verify that agents not inheriting from SovereignBaseAgent are flagged.
    """
    @dataclass
    class OrphanedAgent:
        name = "OrphanedTestAgent"
        layer = "L1_planning"
        instance = Mock()
        class_ref = type("OrphanedTestAgent", (object,), {
            "__mro__": (type("OrphanedTestAgent"), object)
        })
    
    violations = check_compliance([OrphanedAgent()])
    assert len(violations) == 1
    assert "Orphaned: No Sovereign Inheritance" in violations[0]

@pytest.mark.compliance
def test_unknown_layer_detection():
    """
    Verify that agents with unknown layers are flagged.
    """
    @dataclass
    class UnknownLayerAgent:
        name = "UnknownLayerAgent"
        layer = "unknown"
        instance = Mock()
        class_ref = type("UnknownLayerAgent", (SovereignBaseAgent,), {
            "__mro__": (type("UnknownLayerAgent"), SovereignBaseAgent, object)
        })
    
    violations = check_compliance([UnknownLayerAgent()])
    assert len(violations) == 1
    assert "Unknown Layer" in violations[0]

@pytest.mark.compliance
def test_multiple_violations():
    """
    Verify that multiple violations in multiple agents are all detected.
    """
    @dataclass
    class OrphanedAgent:
        name = "OrphanedAgent"
        layer = "unknown"
        instance = Mock()
        class_ref = type("OrphanedAgent", (object,), {
            "__mro__": (type("OrphanedAgent"), object)
        })
    
    @dataclass
    class ValidAgent:
        name = "ValidAgent"
        layer = "L1_planning"
        instance = Mock()
        class_ref = type("ValidAgent", (SovereignBaseAgent,), {
            "__mro__": (type("ValidAgent"), SovereignBaseAgent, object)
        })
    
    violations = check_compliance([OrphanedAgent(), ValidAgent()])
    assert len(violations) == 2
    assert any("Orphaned: No Sovereign Inheritance" in v for v in violations)
    assert any("Unknown Layer" in v for v in violations)

# --- SECURITY TESTS ---

@pytest.mark.security
def test_manifest_integrity_lock(clean_manifest_environment):
    """
    Verify the ManifestGuardian correctly locks, validates, and detects tampering.
    """
    # 1. Seal the manifest
    checksum = ManifestGuardian.seal_manifest()
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
    # Don't create lock file, just try to verify
    assert ManifestGuardian.verify_integrity() is False

@pytest.mark.security
def test_manifest_missing_manifest_file():
    """
    Verify that missing manifest file raises appropriate error.
    """
    with pytest.raises(FileNotFoundError, match="SSOT Blueprint missing"):
        ManifestGuardian.calculate_checksum()

@pytest.mark.security
def test_manifest_checksum_calculation(clean_manifest_environment):
    """
    Verify checksum calculation is consistent and accurate.
    """
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
    # Initial seal
    original_checksum = ManifestGuardian.seal_manifest()
    
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

@pytest.mark.security
def test_manifest_permission_lock(clean_manifest_environment):
    """Verify that sealing the manifest makes it read-only (on supported OS)."""
    if os.name == 'nt': 
        pytest.skip("File permission checks vary on Windows")
        
    ManifestGuardian.seal_manifest()
    
    # Check file permissions (should be read-only)
    file_stat = os.stat("manifest.json")
    # Check if write permissions are removed for owner, group, and others
    assert not (file_stat.st_mode & 0o200)  # Owner write
    assert not (file_stat.st_mode & 0o020)  # Group write
    assert not (file_stat.st_mode & 0o002)  # Others write

# --- BOOT SEQUENCE TESTS ---

@pytest.mark.boot
def test_boot_sequence_integrity_failure():
    """Test that boot sequence fails appropriately when integrity check fails."""
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    with patch.object(ManifestGuardian, 'verify_integrity', return_value=False):
        boot = BootSequence(strict_mode=True)
        result = boot.execute_boot()
        
        assert result["status"] == "failed"
        assert not result["integrity_verified"]
        assert "integrity_check" not in result["phases_completed"]
        assert any("SSOT Integrity Violation" in error for error in result["errors"])

@pytest.mark.boot
def test_boot_sequence_compliance_violations_strict_mode():
    """Test that boot sequence fails in strict mode with compliance violations."""
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    # Mock integrity check to pass
    with patch.object(ManifestGuardian, 'verify_integrity', return_value=True):
        # Mock compliance check to return violations
        with patch('agentic_core.L0_maintenance.scripts.compliance_gate.check_compliance', 
                  return_value=["Test violation"]):
            boot = BootSequence(strict_mode=True)
            result = boot.execute_boot()
            
            assert result["status"] == "failed"
            assert len(result["compliance_violations"]) > 0
            assert "compliance" in result["phases_completed"]

@pytest.mark.boot
def test_boot_sequence_compliance_violations_lenient_mode():
    """Test that boot sequence continues in lenient mode with compliance violations."""
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    # Mock integrity check to pass
    with patch.object(ManifestGuardian, 'verify_integrity', return_value=True):
        # Mock compliance check to return violations
        with patch('agentic_core.L0_maintenance.scripts.compliance_gate.check_compliance', 
                  return_value=["Test violation"]):
            boot = BootSequence(strict_mode=False)
            result = boot.execute_boot()
            
            assert result["status"] == "success"
            assert len(result["compliance_violations"]) > 0
            assert "compliance" in result["phases_completed"]

@pytest.mark.boot
def test_boot_sequence_successful_boot():
    """Test that boot sequence succeeds when all checks pass."""
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    # Mock all checks to pass
    with patch.object(ManifestGuardian, 'verify_integrity', return_value=True):
        with patch('agentic_core.L0_maintenance.scripts.compliance_gate.check_compliance', 
                  return_value=[]):
            boot = BootSequence(strict_mode=True)
            result = boot.execute_boot()
            
            assert result["status"] == "success"
            assert result["integrity_verified"]
            assert len(result["compliance_violations"]) == 0
            assert all(phase in result["phases_completed"] for phase in [
                "integrity_check", "discovery", "compliance", "sovereignty", "runtime"
            ])

# --- INTEGRATION TESTS ---

@pytest.mark.integration
def test_full_security_pipeline(clean_manifest_environment):
    """
    Test the complete security pipeline from manifest sealing to boot sequence.
    """
    # 1. Create and seal manifest
    initial_checksum = ManifestGuardian.verify_integrity()
    
    # 2. Seal the manifest
    seal_checksum = ManifestGuardian.seal_manifest()
    
    # 3. Verify integrity passes
    assert ManifestGuardian.verify_integrity() is True
    
    # 4. Run boot sequence (should succeed)
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    with patch('agentic_core.L0_maintenance.scripts.compliance_gate.check_compliance', 
              return_value=[]):
        boot = BootSequence(strict_mode=True)
        result = boot.execute_boot()
        
        assert result["status"] == "success"
        assert result["integrity_verified"]

@pytest.mark.integration
def test_security_breach_detection(clean_manifest_environment):
    """
    Test that security breaches are properly detected and handled.
    """
    # 1. Seal manifest
    ManifestGuardian.seal_manifest()
    
    # 2. Tamper with manifest
    with open("manifest.json", "a") as f:
        f.write("tampered")
    
    # 3. Verify integrity fails
    assert ManifestGuardian.verify_integrity() is False
    
    # 4. Boot sequence should fail
    from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence
    
    boot = BootSequence(strict_mode=True)
    result = boot.execute_boot()
    
    assert result["status"] == "failed"
    assert not result["integrity_verified"]
