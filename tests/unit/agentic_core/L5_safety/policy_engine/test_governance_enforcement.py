"""
File: tests/L0/test_governance_enforcement.py
Rationale: Verifies the hardened Governance agents (StructuralValidator, GravityRepair).
"""

import pytest

from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import GravityFix, GravityLeakRepairAgent
from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
    StructuralValidatorAgent,
)


@pytest.fixture
def governance_env(tmp_path):
    """Sets up a layered environment with gravity violations."""
    root = tmp_path / "repo"
    root.mkdir()

    # Setup Layers
    (root / "agentic_core" / "L2_execution").mkdir(parents=True)
    (root / "agentic_core" / "L5_safety").mkdir(parents=True)

    # Create L2 file importing L5 (Violation!)
    l2_file = root / "agentic_core" / "L2_execution" / "bad_actor.py"
    l2_file.write_text("from agentic_core.L5_safety import Guardrail\nclass Actor: pass")

    return root


def test_structural_validator_detects_gravity(governance_env):
    """Ensure Validator detects the L2->L5 import."""
    from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
        StructureConfig,
    )

    cfg = StructureConfig(project_root=governance_env)
    validator = StructuralValidatorAgent(config=cfg)

    report = validator.validate_structure(governance_env)

    assert len(report.violations) == 1
    v = report.violations[0]
    assert v.violation_type == "GRAVITY"
    assert "L2" in v.message and "L5" in v.message


def test_gravity_repair_atomic_write(governance_env):
    """Ensure Repair Agent uses atomic writes and fixes import."""
    l2_file = governance_env / "agentic_core" / "L2_execution" / "bad_actor.py"

    healer = GravityLeakRepairAgent(project_root=governance_env)

    # Manually construct fix request (simulating Governor)
    fix = GravityFix(
        file_path=l2_file,
        line_number=1,
        old_import="from agentic_core.L5_safety import Guardrail",
        new_import="# TODO: Abstraction needed for L5_safety",
        fix_type="ABSTRACT",
        rationale="Gravity",
    )

    result = healer.apply_fix(fix, dry_run=False)

    assert result["status"] == "fixed"
    assert "# TODO: Abstraction" in l2_file.read_text()

    # Verify backup created
    backup_dir = governance_env / "archives" / "healing_backups" / "gravity"
    assert len(list(backup_dir.glob("*.bak"))) == 1
