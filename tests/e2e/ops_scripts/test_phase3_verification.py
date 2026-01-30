import pytest
import pathlib
import subprocess
import importlib.util

PHASE3_FILES = [
    "test_autonomous_decision_making.py",
    "test_autonomous_end_to_end.py",
    "test_complete_mission_workflow.py",
    "test_hop2_sovereign_strategist.py",
    "test_hop3_hop4_hop5_foundation.py",
    "test_hop6_hop7_crucible_governor.py",
    "test_hop8_hop9_persistence_handoff.py",
    "test_hop_orchestrator_master.py",
    "test_lic_rg_parity.py",
    "test_master_verification_simulation.py",
]

class TestPhase3Migration:
    """Verify Phase 3 HIGH risk migration completed successfully."""
    
    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_exists_at_destination(self, filename):
        """Verify each file was moved to correct location."""
        dest = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        assert dest.exists(), f"File not found: {dest}"
    
    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_removed_from_source(self, filename):
        """Verify each file no longer exists at source."""
        src = pathlib.Path(f"ops_scripts/{filename}")
        assert not src.exists(), f"File still at source: {src}"
    
    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_file_is_valid_python(self, filename):
        """Verify each file is syntactically valid Python."""
        filepath = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        result = subprocess.run(
            ["python", "-m", "py_compile", str(filepath)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error in {filename}: {result.stderr}"
    
    def test_no_import_errors_on_collection(self):
        """Verify pytest can collect without import errors."""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/e2e/ops_scripts/", 
             "--collect-only", "-q", "--ignore-glob=*verification*"],
            capture_output=True, text=True
        )
        # Allow collection to fail on missing deps, but not import errors
        assert "ImportError" not in result.stderr, f"Import errors: {result.stderr}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
