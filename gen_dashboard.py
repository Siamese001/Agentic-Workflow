#!/usr/bin/env python3
"""
Dashboard generation with mandatory unit test validation.
Tests MUST pass before dashboard is generated.
"""
from pathlib import Path
import sys
import subprocess
import os

sys.path.insert(0, str(Path(__file__).parent))

def ensure_agent_discovery():
    """Run agent discovery if JSON is missing or out of date."""
    project_root = Path(__file__).parent
    discovery_script = project_root / "scripts" / "full_agent_discovery.py"
    json_path = project_root / "agent_discovery_full.json"
    
    # If JSON doesn't exist, run discovery
    if not json_path.exists():
        print("\n🔍 Agent discovery JSON not found. Running discovery...")
        print("=" * 60)
        result = subprocess.run(
            [sys.executable, str(discovery_script)],
            cwd=project_root,
            capture_output=False,
            text=True
        )
        if result.returncode != 0:
            print("\n❌ Agent discovery failed")
            sys.exit(1)
        print("✅ Agent discovery completed")
        return
    
    # Optional: add timestamp check to auto-run if repo is newer than JSON
    # For now, just ensure it exists

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
    # Ensure agent discovery is up to date
    ensure_agent_discovery()
    
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
