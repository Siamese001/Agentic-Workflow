import pytest
import pathlib
import subprocess

PHASE2_FILES = [
    "test_batch_performance_optimization.py",
    "test_location_agent_telemetry.py",
    "test_mission_script_integrity.py",
    "test_phase1_interface.py",
    "test_phase2_interface.py",
]

class TestPhase2Migration:
    """Verify Phase 2 migration completed successfully."""
    
    @pytest.mark.parametrize("filename", PHASE2_FILES)
    def test_file_exists_at_destination(self, filename):
        """Verify each file was moved to correct location."""
        dest = pathlib.Path(f"tests/e2e/ops_scripts/{filename}")
        assert dest.exists(), f"File not found: {dest}"
    
    @pytest.mark.parametrize("filename", PHASE2_FILES)
    def test_file_removed_from_source(self, filename):
        """Verify each file no longer exists at source."""
        src = pathlib.Path(f"ops_scripts/{filename}")
        assert not src.exists(), f"File still at source: {src}"
    
    def test_pytest_discovers_all_files(self):
        """Verify pytest can discover all migrated tests."""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/e2e/ops_scripts/", "--collect-only", "-q"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Collection failed: {result.stderr}"
        
        # Verify each file appears in collection
        for filename in PHASE2_FILES:
            assert filename in result.stdout, f"{filename} not discovered"
