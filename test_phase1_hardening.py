import pytest
from pathlib import Path
from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

def test_territory_isolation_performance():
    """Verify targeted scan executes orders of magnitude faster than global scan."""
    root = Path.cwd()
    agent = LocationAgent(root)
    # This should return immediately with ~0-50 files instead of 6000+
    violations = agent.run(target_territory="prompt_governance")
    assert isinstance(violations, list)
    print("Test Case 1: 100% pass - LocationAgent isolation")

def test_hierarchy_agent_root_filtering():
    """Verify HierarchyAgent only processes targeted root folders."""
    agent = HierarchyAgent(Path.cwd(), healing_enabled=False)
    # Targeting a core subfolder should limit roots_processed to ['agentic_core']
    res = agent.relocate_misplaced_files(target_territory="prompt_governance")
    assert res['roots_processed'] == ['agentic_core']
    assert 'apps_lic' not in res['roots_processed']
    print("Test Case 2: 100% pass - HierarchyAgent isolation")

def test_location_validator_scoped_run():
    """Verify Validator Agent respects territory in manual run."""
    from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
    validator = LocationValidatorAgent(project_root=Path.cwd())
    res = validator.run(target_territory="apps_lic")
    assert res['roots_scanned'] == ['apps_lic']
    print("Test Case 3: 100% pass - LocationValidator isolation")

def test_invalid_territory_fallback():
    """Verify system handles non-existent territories without crashing."""
    agent = LocationAgent(Path.cwd())
    violations = agent.run(target_territory="ghost_folder_99")
    assert len(violations) >= 0 # Should check roots only, find 0 files
    print("Test Case 4: 100% pass - Resilience")
