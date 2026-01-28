"""
File: tests/unit/L5_safety/test_golden_baseline.py
Path: tests/unit/L5_safety/test_golden_baseline.py
Rationale: 
    Rigorous verification of Phase 8 integrity mechanisms.
    Ensures that drift is detected at the bit-level.
"""
import pytest
import hashlib
import json
import os
from pathlib import Path
from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent

@pytest.fixture
def gold_master_env(tmp_path):
    """Sets up a clean repository and captures an initial baseline."""
    root = tmp_path / "gold_repo"
    root.mkdir()
    (root / "agentic_core").mkdir()
    (root / "pyproject.toml").touch()
    
    # Create a sovereign file
    f = root / "agentic_core" / "SovereignAgent.py"
    f.write_text("class SovereignAgent: pass", encoding="utf-8")
    
    # Initialize Governor and capture
    governor = ArchitectureGovernorAgent(project_root=root)
    governor.capture_golden_baseline()
    return root

def test_baseline_capture_integrity(gold_master_env):
    """
    Test Case 1: Baseline must contain correct SHA-256 hashes.
    Expectation: 100% Pass.
    """
    manifest_path = gold_master_env / "agentic_core" / "config" / "baselines" / "golden_baseline.json"
    assert manifest_path.exists()
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    # Manually calculate hash to verify agent's calculation
    agent_file = gold_master_env / "agentic_core" / "SovereignAgent.py"
    expected_hash = hashlib.sha256(agent_file.read_bytes()).hexdigest()
    
    # JSON keys use forward slashes even on Windows for portability
    key = "agentic_core/SovereignAgent.py"
    assert manifest["files"][key] == expected_hash

def test_drift_detection_bit_level(gold_master_env):
    """
    Test Case 2: Changing a single character must trigger drift detection.
    Expectation: 100% Pass.
    """
    agent_file = gold_master_env / "agentic_core" / "SovereignAgent.py"
    # Minor modification: Change 'pass' to 'pass ' (extra space)
    agent_file.write_text("class SovereignAgent: pass ", encoding="utf-8")
    
    governor = ArchitectureGovernorAgent(project_root=gold_master_env, ci_mode=True)
    report = governor.run_audit()
    
    assert report["success"] is False, "Drift should be detected"
    assert report["stats"]["drift_detected"] == 1
    assert report["drift_violations"][0]["type"] == "CONTENT_DRIFT"

def test_missing_file_detection(gold_master_env):
    """
    Test Case 3: Deleting a baseline file must trigger a MISSING_FILE violation.
    Expectation: 100% Pass.
    """
    agent_file = gold_master_env / "agentic_core" / "SovereignAgent.py"
    agent_file.unlink()
    
    governor = ArchitectureGovernorAgent(project_root=gold_master_env, ci_mode=True)
    report = governor.run_audit()
    
    assert report["stats"]["drift_detected"] == 1
    assert report["drift_violations"][0]["type"] == "MISSING_FILE"

def test_audit_persistence(gold_master_env):
    """
    Test Case 4: Audit reports must be saved to disk.
    Expectation: 100% Pass.
    """
    governor = ArchitectureGovernorAgent(project_root=gold_master_env)
    governor.run_audit()
    
    log_dir = gold_master_env / "logs" / "sovereign_audit"
    logs = list(log_dir.glob("audit_*.json"))
    assert len(logs) >= 1

def test_no_baseline_handling(gold_master_env):
    """
    Test Case 5: System should gracefully handle missing baseline.
    Expectation: 100% Pass.
    """
    # Remove baseline
    baseline_path = gold_master_env / "agentic_core" / "config" / "baselines" / "golden_baseline.json"
    baseline_path.unlink()
    
    governor = ArchitectureGovernorAgent(project_root=gold_master_env, ci_mode=True)
    report = governor.run_audit()
    
    # Should not crash, just no drift detected
    assert report["stats"]["drift_detected"] == 0
    assert len(report["drift_violations"]) == 0

def test_multiple_file_drift(gold_master_env):
    """
    Test Case 6: Multiple file changes should all be detected.
    Expectation: 100% Pass.
    """
    # Create additional files
    (gold_master_env / "agentic_core" / "TestAgent1.py").write_text("class Test1: pass", encoding="utf-8")
    (gold_master_env / "agentic_core" / "TestAgent2.py").write_text("class Test2: pass", encoding="utf-8")
    
    # Recapture baseline with new files
    governor = ArchitectureGovernorAgent(project_root=gold_master_env)
    governor.capture_golden_baseline()
    
    # Modify multiple files
    (gold_master_env / "agentic_core" / "TestAgent1.py").write_text("class Test1: modified", encoding="utf-8")
    (gold_master_env / "agentic_core" / "TestAgent2.py").write_text("class Test2: changed", encoding="utf-8")
    
    report = governor.run_audit()
    
    assert report["stats"]["drift_detected"] == 2
    assert len(report["drift_violations"]) == 2

def test_baseline_atomic_write(gold_master_env):
    """
    Test Case 7: Baseline capture should be atomic (no corruption).
    Expectation: 100% Pass.
    """
    governor = ArchitectureGovernorAgent(project_root=gold_master_env)
    baseline_path = governor.capture_golden_baseline()
    
    # Verify file exists and is valid JSON
    assert baseline_path.exists()
    
    with open(baseline_path, 'r') as f:
        manifest = json.load(f)
    
    # Should have required fields
    assert "version" in manifest
    assert "timestamp" in manifest
    assert "audit_id" in manifest
    assert "files" in manifest
    assert manifest["version"] == "1.0"

def test_ci_mode_failure(gold_master_env):
    """
    Test Case 8: CI mode should exit with failure on drift detection.
    Expectation: 100% Pass.
    """
    # Modify file to create drift
    agent_file = gold_master_env / "agentic_core" / "SovereignAgent.py"
    agent_file.write_text("class SovereignAgent: modified", encoding="utf-8")
    
    governor = ArchitectureGovernorAgent(project_root=gold_master_env, ci_mode=True)
    report = governor.run_audit()
    
    # In CI mode, drift should cause failure
    assert report["success"] is False
    assert report["stats"]["drift_detected"] > 0
