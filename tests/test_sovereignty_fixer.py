"""
File: tests/test_sovereignty_fixer.py
Path: C:\Git\Agentic-Workflow\tests\test_sovereignty_fixer.py
Status: FINAL - GOLD MASTER (Phase 4)
Rationale: 
    Adds 'test_healer_mixin_legacy' to explicitly regression test the removal 
    of the hardcoded whitelist. This confirms the new logic is robust enough 
    to handle the previously manually exempted files.
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core" / "L0_maintenance" / "scripts"))

from PascalSovereigntyFixer import PascalSovereigntyFixer

# --- FIXTURES ---

@pytest.fixture
def workspace(tmp_path):
    """
    Creates a volatile workspace simulating the Agentic-Workflow directory structure.
    """
    # 1. Standard Agent (Target: Rename to PascalCase)
    (tmp_path / "deployment_agent.py").write_text("class DeploymentAgent:\n    pass", encoding="utf-8")
    
    # 2. Mixin - Snake Case (Target: EXEMPT)
    (tmp_path / "adaptive_execution_mixin.py").write_text("class AdaptiveExecutionMixin:\n    pass", encoding="utf-8")
    
    # 3. LEGACY TEST: Healer Mixin (Target: EXEMPT via Pattern, NOT Whitelist)
    (tmp_path / "healer_mixin.py").write_text("class HealerMixin:\n    pass", encoding="utf-8")
    
    # 4. Critical SSOT (Target: EXEMPT via Whitelist)
    (tmp_path / "structure_blueprint.py").write_text("class Blueprint:\n    pass", encoding="utf-8")
    
    return tmp_path

# --- TEST CASES ---

def test_healer_mixin_regression_proof(workspace):
    """
    CRITICAL: Explicitly tests 'healer_mixin.py'. 
    We removed this from the hardcoded 'critical_ssot_files' list in Phase 1.
    This test proves that the new 'endswith(_mixin.py)' logic correctly catches it.
    """
    fixer = PascalSovereigntyFixer(dry_run=False)
    fixer.run(workspace)
    
    assert (workspace / "healer_mixin.py").exists(), \
        "REGRESSION: healer_mixin.py was renamed! The pattern matcher failed to replace the hardcoded exemption."
    
    assert not (workspace / "HealerMixin.py").exists()
    assert fixer.stats["violations"]["MIXIN"] == 0

def test_mixin_exemption_strict(workspace):
    """
    Verifies generic mixin exemption logic.
    """
    fixer = PascalSovereigntyFixer(dry_run=False)
    fixer.run(workspace)
    
    assert (workspace / "adaptive_execution_mixin.py").exists()
    assert not (workspace / "AdaptiveExecutionMixin.py").exists()

def test_agent_enforcement(workspace):
    """
    Verifies that Agents ARE renamed.
    """
    fixer = PascalSovereigntyFixer(dry_run=False)
    fixer.run(workspace)
    
    assert not (workspace / "deployment_agent.py").exists()
    assert (workspace / "DeploymentAgent.py").exists()
    assert fixer.stats["renamed"] >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
