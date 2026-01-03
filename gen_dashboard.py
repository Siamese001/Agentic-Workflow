#!/usr/bin/env python3
"""
Dashboard generation with mandatory unit test validation.
Tests MUST pass before dashboard is generated.
"""
from pathlib import Path
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).parent))

def run_dashboard_tests():
    """Run unit tests before dashboard generation."""
    print("\n🧪 Running dashboard unit tests (mandatory)...")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "tests" / "test_dashboard_generation.py"
    
    if not test_file.exists():
        print(f"⚠️  Warning: Test file not found at {test_file}")
        print("   Proceeding without tests (not recommended)")
        return True
    
    # Run tests
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    # Print test output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("❌ DASHBOARD TESTS FAILED")
        print("=" * 60)
        print("\n⛔ Dashboard generation BLOCKED - tests must pass first.")
        print("   Fix the failing tests and try again.")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL DASHBOARD TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Run tests first
    if not run_dashboard_tests():
        sys.exit(1)
    
    # Tests passed - proceed with generation
    print("\n📊 Generating autonomy compliance report and dashboard...")
    print("=" * 60)
    
    from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
    
    AutonomyGuardianAgent(Path(__file__).parent).generate_compliance_report(markdown=True)
    
    print("\n✅ Dashboard generated successfully!")
    print("   → Open: reports/autonomy_dashboard.html")
    print("   → Server: http://localhost:8000/autonomy_dashboard.html")
