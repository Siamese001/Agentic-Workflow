"""
File: tests/L0/test_integrated_sovereignty.py
Rationale: 
    Rigorous verification of the Unified Lifecycle.
    Ensures that execute_ssot.py correctly triggers collision resolution 
    and import refactoring in a single pass.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import shutil
from unittest.mock import patch, MagicMock

# Import the agents
from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent
from agentic_core.L5_safety.validators.RootHygieneAgent import RootHygieneAgent


@pytest.fixture
def sovereign_env(tmp_path):
    """Creates a 'drifting' repo state with naming and hygiene violations."""
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "pyproject.toml").touch()
    
    # 1. Hygiene Violation - illegal root scripts directory
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "tool.py").write_text("# Standalone tool\nprint('hello')")
    (scripts_dir / "core_tool.py").write_text("from agentic_core import something\nprint('core')")
    
    # 2. Naming Collision (Divergent content)
    l5 = tmp_path / "agentic_core" / "L5_safety" / "validators"
    l5.mkdir(parents=True)
    target = l5 / "subatomic_testing_mixin.py"
    violator = l5 / "SubatomicTestingMixin.py"
    target.write_text("class Mixin:\n    pass  # V1\n")
    violator.write_text("class Mixin:\n    pass  # V2_CONFLICT\n")
    
    # 3. Import Drift - consumer imports the wrong name
    consumer = l5 / "consumer.py"
    consumer.write_text("from SubatomicTestingMixin import Mixin\n")
    
    # 4. Naming Collision (Identical content)
    identical_target = l5 / "helper_utils.py"
    identical_violator = l5 / "HelperUtils.py"
    identical_content = "def helper():\n    return 42\n"
    identical_target.write_text(identical_content)
    identical_violator.write_text(identical_content)
    
    return tmp_path


def test_root_hygiene_agent_evacuates_scripts(sovereign_env):
    """
    Scenario: Run RootHygieneAgent on environment with illegal root scripts/.
    Expectation: scripts/ is evacuated to appropriate locations.
    """
    agent = RootHygieneAgent(project_root=sovereign_env, dry_run=False)
    result = agent.run()
    
    assert result["success"], "Root hygiene enforcement should succeed"
    assert not (sovereign_env / "scripts").exists(), "Root scripts/ should be eliminated"
    
    # Check repatriation logic
    ops_scripts = sovereign_env / "ops_scripts"
    l0_scripts = sovereign_env / "agentic_core" / "L0_maintenance" / "scripts"
    
    assert (ops_scripts / "tool.py").exists(), "Standalone tool should move to ops_scripts"
    assert (l0_scripts / "core_tool.py").exists(), "Core tool should move to L0_maintenance/scripts"
    
    assert agent.stats["scripts_evacuated"] == 2, "Should evacuate 2 scripts"


def test_pascal_sovereignty_resolves_divergent_collision(sovereign_env):
    """
    Scenario: Run PascalSovereigntyAgent on divergent collision.
    Expectation: SubatomicTestingMixin.py is moved to .CONFLICT file.
    """
    agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    result = agent.run()
    
    assert result["success"], "Pascal sovereignty should succeed"
    
    # Check that the violator was moved to .CONFLICT
    l5 = sovereign_env / "agentic_core" / "L5_safety" / "validators"
    conflicts = list(l5.glob("*.CONFLICT_*"))
    
    assert len(conflicts) >= 1, "Should create at least one .CONFLICT file"
    assert any("SubatomicTestingMixin" in c.name for c in conflicts), \
        "SubatomicTestingMixin.py should be renamed to .CONFLICT"
    
    # Verify the canonical file still exists
    assert (l5 / "subatomic_testing_mixin.py").exists(), \
        "Canonical subatomic_testing_mixin.py should remain"


def test_pascal_sovereignty_deletes_identical_collision(sovereign_env):
    """
    Scenario: Run PascalSovereigntyAgent on identical collision.
    Expectation: HelperUtils.py is deleted (redundant).
    """
    agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    result = agent.run()
    
    assert result["success"], "Pascal sovereignty should succeed"
    
    l5 = sovereign_env / "agentic_core" / "L5_safety" / "validators"
    
    # The violator should be deleted
    assert not (l5 / "HelperUtils.py").exists(), \
        "HelperUtils.py should be deleted (identical to helper_utils.py)"
    
    # The canonical file should remain
    assert (l5 / "helper_utils.py").exists(), \
        "Canonical helper_utils.py should remain"


def test_pascal_sovereignty_updates_imports(sovereign_env):
    """
    Scenario: Run PascalSovereigntyAgent with import drift.
    Expectation: consumer.py imports are updated to canonical name.
    """
    agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    result = agent.run()
    
    assert result["success"], "Pascal sovereignty should succeed"
    
    l5 = sovereign_env / "agentic_core" / "L5_safety" / "validators"
    consumer_code = (l5 / "consumer.py").read_text()
    
    # Import should be updated to canonical name
    assert "from subatomic_testing_mixin" in consumer_code, \
        "Import should be refactored to canonical snake_case name"
    assert "from SubatomicTestingMixin" not in consumer_code, \
        "Old PascalCase import should be removed"


def test_unified_healing_mission(sovereign_env):
    """
    Scenario: Run integrated lifecycle on a drifting environment.
    Expectation: 
        1. scripts/ is evacuated.
        2. SubatomicTestingMixin.py is moved to .CONFLICT.
        3. consumer.py imports are updated to subatomic_testing_mixin.
        4. HelperUtils.py is deleted (identical).
    """
    # Step 1: Run Root Hygiene
    hygiene_agent = RootHygieneAgent(project_root=sovereign_env, dry_run=False)
    hygiene_result = hygiene_agent.run()
    assert hygiene_result["success"], "Root hygiene should succeed"
    
    # Step 2: Run Pascal Sovereignty
    pascal_agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    pascal_result = pascal_agent.run()
    assert pascal_result["success"], "Pascal sovereignty should succeed"
    
    # Verify all expectations
    assert not (sovereign_env / "scripts").exists(), "Root hygiene failed"
    assert (sovereign_env / "ops_scripts" / "tool.py").exists(), "Repatriation failed"
    
    l5 = sovereign_env / "agentic_core" / "L5_safety" / "validators"
    conflicts = list(l5.glob("*.CONFLICT_*"))
    assert len(conflicts) >= 1, "Collision resolution failed to create .CONFLICT file"
    
    consumer_code = (l5 / "consumer.py").read_text()
    assert "from subatomic_testing_mixin" in consumer_code, \
        "Import refactoring failed during integration"
    
    assert not (l5 / "HelperUtils.py").exists(), \
        "Identical collision should be deleted"


def test_zero_violation_audit_pass(sovereign_env):
    """
    Ensures that after a healing pass, a second audit returns 0 violations.
    """
    # First pass: heal
    hygiene_agent = RootHygieneAgent(project_root=sovereign_env, dry_run=False)
    hygiene_agent.run()
    
    pascal_agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    pascal_agent.run()
    
    # Second pass: validate (dry_run + validate_only)
    validator = PascalSovereigntyAgent(
        project_root=sovereign_env, 
        dry_run=True, 
        validate_only=True
    )
    result = validator.run()
    
    # After healing, validation should pass with 0 violations
    total_violations = sum(validator.stats["violations"].values())
    assert total_violations == 0, \
        f"After healing, should have 0 violations, got {total_violations}"


def test_heal_repository_interface(sovereign_env):
    """
    Test the standard heal_repository() interface for execute_ssot.py integration.
    """
    # Test PascalSovereigntyAgent heal_repository
    pascal_agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    heal_result = pascal_agent.heal_repository(dry_run=False, execute=True)
    
    assert 'violations_found' in heal_result, "Should return canonical keys"
    assert 'violations_fixed' in heal_result, "Should return canonical keys"
    assert 'errors' in heal_result, "Should return canonical keys"
    assert 'skipped' in heal_result, "Should return canonical keys"
    
    # Test RootHygieneAgent heal_repository
    hygiene_agent = RootHygieneAgent(project_root=sovereign_env, dry_run=False)
    heal_result = hygiene_agent.heal_repository(dry_run=False, execute=True)
    
    assert 'violations_found' in heal_result, "Should return canonical keys"
    assert 'violations_fixed' in heal_result, "Should return canonical keys"
    assert heal_result['violations_fixed'] > 0, "Should fix violations"


def test_dry_run_mode(sovereign_env):
    """
    Test that dry_run mode doesn't make actual changes.
    """
    # Run in dry_run mode
    pascal_agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=True)
    result = pascal_agent.run()
    
    # Violations should be detected
    total_violations = sum(pascal_agent.stats["violations"].values())
    assert total_violations > 0, "Should detect violations in dry_run"
    
    # But no actual changes should be made
    assert pascal_agent.stats["renamed"] == 0, "Dry run should not rename files"
    
    l5 = sovereign_env / "agentic_core" / "L5_safety" / "validators"
    assert (l5 / "SubatomicTestingMixin.py").exists(), \
        "Violator should still exist in dry_run mode"


def test_cycle_detection_in_heal_repository(sovereign_env):
    """
    Test that heal_repository prevents infinite cycles.
    """
    agent = PascalSovereigntyAgent(project_root=sovereign_env, dry_run=False)
    
    # Create a call path that includes this agent
    call_path = {f"PascalSovereigntyAgent@{sovereign_env}"}
    
    # Call heal_repository with existing call_path
    result = agent.heal_repository(dry_run=False, execute=True, _call_path=call_path)
    
    # Should return immediately with 0 violations (cycle detected)
    assert result['violations_found'] == 0, "Should detect cycle and return early"
    assert result['violations_fixed'] == 0, "Should not fix anything on cycle"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
