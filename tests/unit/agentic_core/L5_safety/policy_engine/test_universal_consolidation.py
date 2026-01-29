#!/usr/bin/env python3
"""
File: tests/unit/L5_safety/test_universal_consolidation.py
Rationale:
    Verifies that the Execution Arm agents (Validator, Healer, Enforcer)
    are MRO-safe and perform atomic operations correctly.
"""

import pytest
from pathlib import Path
from agentic_core.L5_safety.policy_engine.CodeValidatorAgent import CodeValidatorAgent
from agentic_core.L5_safety.policy_engine.CodeHealerAgent import CodeHealerAgent
from agentic_core.L5_safety.policy_engine.CodeEnforcerAgent import CodeEnforcerAgent


@pytest.fixture
def mock_repo(tmp_path):
    d = tmp_path / "mock_project"
    d.mkdir()
    return d


def test_mro_stability():
    """
    CRITICAL: Verify that initializing agents does not trigger TypeError.
    This confirms the redundant mixin removal.
    """
    try:
        v = CodeValidatorAgent()
        h = CodeHealerAgent()
        e = CodeEnforcerAgent()
    except TypeError as e:
        pytest.fail(f"MRO Conflict detected: {e}")


def test_atomic_write_safety(mock_repo):
    """
    Verify CodeHealerAgent performs safe atomic writes with backups.
    """
    target_file = mock_repo / "critical_logic.py"
    target_file.write_text("old_content")

    agent = CodeHealerAgent()
    # Mock project root for backup dir
    agent.project_root = mock_repo
    agent._agent_config.backup_dir = mock_repo / "backups"
    agent._agent_config.backup_before_heal = True  # Enable backup

    # Perform Atomic Write
    success = agent.atomic_write(target_file, "new_content")

    assert success is True
    assert target_file.read_text() == "new_content"

    # Verify Backup (files are timestamped, not .bak extension)
    backup_files = list(agent._agent_config.backup_dir.glob("critical_logic.py.*"))
    assert len(backup_files) == 1
    assert backup_files[0].read_text() == "old_content"


def test_validator_syntax_check(mock_repo):
    """Verify CodeValidator catches syntax errors."""
    bad_file = mock_repo / "broken.py"
    bad_file.write_text("def broken(): return missing_quote '")

    agent = CodeValidatorAgent()
    violations = agent.validate_file(bad_file)

    assert len(violations) == 1
    assert violations[0].violation_type.name == "SYNTAX"


def test_heal_repository_canonical_keys():
    """Verify all agents return canonical keys in heal_repository."""
    v = CodeValidatorAgent()
    h = CodeHealerAgent()
    e = CodeEnforcerAgent()

    # Test CodeValidatorAgent
    result = v.heal_repository(dry_run=True)
    assert "violations_found" in result
    assert "violations_fixed" in result
    assert "errors" in result
    assert "skipped" in result
    assert "total_violations" not in result
    assert "violations" not in result

    # Test CodeHealerAgent
    result = h.heal_repository(dry_run=True)
    assert "violations_found" in result
    assert "violations_fixed" in result
    assert "errors" in result
    assert "skipped" in result
    assert "violations" not in result
    assert "fixed" not in result

    # Test CodeEnforcerAgent
    result = e.heal_repository(dry_run=True)
    assert "violations_found" in result
    assert "violations_fixed" in result
    assert "errors" in result
    assert "skipped" in result


def test_healer_import_removal(mock_repo):
    """Test CodeHealerAgent removes unused imports atomically."""
    test_file = mock_repo / "test_imports.py"
    test_file.write_text("""
import os
import sys
import unused_module

def test():
    print("hello")
""")

    agent = CodeHealerAgent()
    agent.project_root = mock_repo
    agent._agent_config.backup_dir = mock_repo / "backups"
    agent._agent_config.dry_run = False

    actions = agent.heal_imports(test_file)

    # Should detect unused import
    assert len(actions) >= 1
    assert any("unused_module" in a.description for a in actions)

    # Check atomic write was used (file should be modified)
    content = test_file.read_text()
    assert "unused_module" not in content


def test_enforcer_sovereignty_check():
    """Test CodeEnforcerAgent sovereignty checking."""
    enforcer = CodeEnforcerAgent()

    # Test layer extraction
    l5_file = Path("agentic_core/L5_safety/test.py")
    can_modify, reason = enforcer.check_sovereignty("L3", l5_file)
    assert not can_modify
    assert "sovereignty violation" in reason.lower()

    # Same layer should be allowed
    can_modify, reason = enforcer.check_sovereignty("L5", l5_file)
    assert can_modify


def test_no_direct_subatomic_testing_mixin():
    """Verify none of the agents directly inherit from SubatomicTestingMixin."""
    for agent_class in [CodeValidatorAgent, CodeHealerAgent, CodeEnforcerAgent]:
        # Check that SubatomicTestingMixin is not a direct parent
        direct_parents = [cls.__name__ for cls in agent_class.__bases__]
        assert "SubatomicTestingMixin" not in direct_parents, (
            f"{agent_class.__name__} directly inherits from SubatomicTestingMixin"
        )

        # But it should be in the MRO via SovereignBaseAgent (this is correct)
        mro = [cls.__name__ for cls in agent_class.__mro__]
        assert "SovereignBaseAgent" in mro, (
            f"{agent_class.__name__} missing SovereignBaseAgent in MRO"
        )


def test_sovereign_base_in_mro():
    """Verify all agents have SovereignBaseAgent in their MRO."""
    for agent_class in [CodeValidatorAgent, CodeHealerAgent, CodeEnforcerAgent]:
        mro = [cls.__name__ for cls in agent_class.__mro__]
        assert "SovereignBaseAgent" in mro, (
            f"{agent_class.__name__} missing SovereignBaseAgent in MRO"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
