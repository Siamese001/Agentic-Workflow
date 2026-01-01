"""
Test to prevent snake_case regression in codebase.
Ensures eternal PascalCase sovereignty by relying on PascalSovereigntyEnforcerAgent as SSOT.
"""
import subprocess
import pytest
from pathlib import Path


class TestPascalCaseSovereignty:
    """Enforce PascalCase naming convention across the codebase."""
    
    def test_pascal_enforcer_reports_zero_violations(self):
        """
        Test that PascalSovereigntyEnforcerAgent reports zero violations.
        
        This is the authoritative test - the enforcer is the SSOT for what
        constitutes a PascalCase violation. It handles exemptions, special cases,
        and backward compatibility correctly.
        """
        project_root = Path(__file__).parent.parent.parent
        
        result = subprocess.run(
            ["python", "run_pascal_enforcer.py", "--dry-run", "--scope", "all"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=120
        )
        
        # Check for zero violations
        assert "Purged: 0" in result.stdout, (
            f"❌ PascalCase violations detected!\n"
            f"The enforcer found snake_case that needs fixing.\n"
            f"Run: python run_pascal_enforcer.py --scope all\n\n"
            f"Output:\n{result.stdout}"
        )
        
        assert result.returncode == 0, (
            f"Pascal enforcer execution failed:\n{result.stderr}"
        )
    
    def test_enforcer_scans_all_layers(self):
        """Test that enforcer scans all expected layers."""
        project_root = Path(__file__).parent.parent.parent
        
        result = subprocess.run(
            ["python", "run_pascal_enforcer.py", "--dry-run", "--scope", "all"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=120
        )
        
        # Verify all layers were scanned
        expected_layers = ["schemas", "config", "L1_cognition", "L2_execution", 
                          "L3_orchestration", "L4_state", "L5_safety", "L0_maintenance"]
        
        for layer in expected_layers:
            assert layer in result.stdout, (
                f"Layer {layer} not scanned by enforcer"
            )
    
    @pytest.mark.asyncio
    async def test_pascal_enforcer_dry_run_passes(self):
        """Test that PascalSovereigntyEnforcerAgent dry-run reports zero violations."""
        result = subprocess.run(
            ["python", "run_pascal_enforcer.py", "--dry-run", "--scope", "all"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Check that output contains "Purged: 0"
        assert "Purged: 0" in result.stdout, (
            f"PascalCase violations detected:\n{result.stdout}"
        )
        assert result.returncode == 0, (
            f"Pascal enforcer failed:\n{result.stderr}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
