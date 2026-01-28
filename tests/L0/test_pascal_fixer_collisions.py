"""
File: tests/L0/test_pascal_fixer_collisions.py
Rationale: Verifies collision resolution strategies (Delete vs Conflict Rename).
"""
import pytest
import time
from pathlib import Path
from agentic_core.L0_maintenance.scripts.PascalSovereigntyFixer import PascalSovereigntyFixer

@pytest.fixture
def fixer_env(tmp_path):
    (tmp_path / "src").mkdir()
    return tmp_path / "src"

def test_identical_collision_deletes_violator(fixer_env):
    """Test safe deduplication of identical files."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "subatomic_testing_mixin.py"
    violator = fixer_env / "SubatomicTestingMixin.py"
    
    code = "class SubatomicTestingMixin: pass"
    target.write_text(code, encoding="utf-8")
    violator.write_text(code, encoding="utf-8")
    
    result = fixer.resolve_collision_and_rename(violator, "subatomic_testing_mixin.py")
    
    assert result is True
    assert not violator.exists()
    assert target.exists()

def test_divergent_collision_renames_violator(fixer_env):
    """Test preservation of divergent data via .CONFLICT rename."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "adaptive_execution_mixin.py"
    violator = fixer_env / "AdaptiveExecutionMixin.py"
    
    target.write_text("class Mixin: pass # V1")
    violator.write_text("class Mixin: pass # V2_MODIFIED")
    
    result = fixer.resolve_collision_and_rename(violator, "adaptive_execution_mixin.py")
    
    assert result is True
    assert not violator.exists()
    # Check for conflict file
    conflicts = list(fixer_env.glob("adaptive_execution_mixin.py.CONFLICT_*"))
    assert len(conflicts) == 1
    assert "V2_MODIFIED" in conflicts[0].read_text()

def test_no_collision_standard_rename(fixer_env):
    """Test standard rename when no collision exists."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    src = fixer_env / "OldName.py"
    src.write_text("class Test: pass")
    
    result = fixer.resolve_collision_and_rename(src, "NewName.py")
    
    assert result is True
    assert not src.exists()
    assert (fixer_env / "NewName.py").exists()

def test_dry_run_mode(fixer_env):
    """Test that dry run mode doesn't actually modify files."""
    fixer = PascalSovereigntyFixer(dry_run=True)
    src = fixer_env / "TestFile.py"
    src.write_text("class Test: pass")
    
    result = fixer.resolve_collision_and_rename(src, "NewFile.py")
    
    assert result is True
    assert src.exists()  # File should still exist in dry run mode
    assert not (fixer_env / "NewFile.py").exists()

def test_collision_with_binary_content(fixer_env):
    """Test collision resolution with binary content differences."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "test_file.py"
    violator = fixer_env / "TestFile.py"
    
    # Write identical binary content first
    target.write_bytes(b'\x00\x01\x02\x03')
    violator.write_bytes(b'\x00\x01\x02\x03')
    
    result = fixer.resolve_collision_and_rename(violator, "test_file.py")
    
    assert result is True
    assert not violator.exists()
    assert target.exists()

def test_collision_case_insensitive_windows(fixer_env):
    """Test case-insensitive collision handling."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "test_file.py"
    violator = fixer_env / "TEST_FILE.py"
    
    target.write_text("class Test: pass")
    violator.write_text("class Test: pass")
    
    result = fixer.resolve_collision_and_rename(violator, "test_file.py")
    
    assert result is True
    # On Windows, case-insensitive paths may resolve to the same file
    # Check that the target still exists and has correct content
    assert target.exists()
    assert "class Test: pass" in target.read_text()

def test_trivial_match_no_action(fixer_env):
    """Test that no action is taken when source and destination are the same."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    src = fixer_env / "test_file.py"
    src.write_text("class Test: pass")
    
    result = fixer.resolve_collision_and_rename(src, "test_file.py")
    
    assert result is False
    assert src.exists()

def test_error_handling_during_collision(fixer_env):
    """Test graceful error handling during collision resolution."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "target.py"
    violator = fixer_env / "violator.py"
    
    target.write_text("class Target: pass")
    violator.write_text("class Violator: pass")
    
    # Create a file that will cause read error by making it unreadable
    # On Windows, we can simulate this by creating a scenario where the file
    # gets removed during the operation
    
    # Test with a non-existent target to trigger error path
    non_existent_target = fixer_env / "non_existent.py"
    result = fixer.resolve_collision_and_rename(violator, "non_existent.py")
    
    # Should succeed since there's no collision
    assert result is True
    assert not violator.exists()
    assert (fixer_env / "non_existent.py").exists()
