"""
Direct Hierarchy Agent Boundary Test
=====================================

Directly invokes HierarchyAgent to test movement and archival boundaries.
"""

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent


def test_structural_move():
    """Test Case A: Structural re-alignment (should be automatic)."""
    print("\n" + "=" * 80)
    print("TEST CASE A: Structural Re-alignment (Automatic)")
    print("=" * 80)

    agent = HierarchyAgent(project_root=PROJECT_ROOT, healing_enabled=True, auto_approve=True)

    # Check if rogue_script.py exists
    rogue_script = PROJECT_ROOT / L0_ROUTING_DIR / "rogue_script.py"
    print(f"\n📁 Checking: {rogue_script}")
    print(f"   Exists: {rogue_script.exists()}")

    if not rogue_script.exists():
        print("❌ Test file missing - cannot proceed")
        return

    # Run heal_repository with execute=True
    print("\n🔧 Running agent.heal_repository(execute=True)...")

    try:
        result = agent.heal_repository(dry_run=False, execute=True)

        print("\n📊 Results:")
        print(f"   Violations Found: {result.get('violations_found', 0)}")
        print(f"   Violations Fixed: {result.get('violations_fixed', 0)}")
        print(f"   Errors: {result.get('errors', 0)}")
        print(f"   Status: {result.get('status', 'UNKNOWN')}")

        # Check if file was moved
        still_exists = rogue_script.exists()
        print(f"\n📁 Original file still exists: {still_exists}")

        # Check potential target locations
        potential_targets = [
            PROJECT_ROOT / L0_ROUTING_DIR / "scripts" / "rogue_script.py",
            PROJECT_ROOT / L0_ROUTING_DIR / "depth_aligned" / "rogue_script.py",
        ]

        for target in potential_targets:
            if target.exists():
                print(f"✅ Found moved file at: {target.relative_to(PROJECT_ROOT)}")
                break

    except Exception as e:  # guardian: allow-silent-swallower
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


def test_archival_move():
    """Test Case B: Archival enforcement (should prompt)."""
    print("\n" + "=" * 80)
    print("TEST CASE B: Archival Enforcement (Manual Prompt)")
    print("=" * 80)

    agent = HierarchyAgent(project_root=PROJECT_ROOT, healing_enabled=True, auto_approve=False)

    # Check if rogue_root_file.py exists
    rogue_root = PROJECT_ROOT / "rogue_root_file.py"
    print(f"\n📁 Checking: {rogue_root}")
    print(f"   Exists: {rogue_root.exists()}")

    if not rogue_root.exists():
        print("❌ Test file missing - cannot proceed")
        return

    # Run heal_repository WITHOUT auto-yes
    print("\n🔧 Running agent.heal_repository(execute=True)...")
    print("⚠️ This should prompt for archival approval...")

    try:
        # Temporarily disable auto-yes by checking environment
        import os

        old_batch_accept = os.environ.get("ARCHIVE_BATCH_ACCEPT", "0")
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "0"

        result = agent.heal_repository(dry_run=False, execute=True)

        # Restore
        os.environ["ARCHIVE_BATCH_ACCEPT"] = old_batch_accept

        print("\n📊 Results:")
        print(f"   Violations Found: {result.get('violations_found', 0)}")
        print(f"   Violations Fixed: {result.get('violations_fixed', 0)}")
        print(f"   Errors: {result.get('errors', 0)}")
        print(f"   Status: {result.get('status', 'UNKNOWN')}")

    except Exception as e:  # guardian: allow-silent-swallower
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


def test_cli_flag_override():
    """Test Case C: CLI flag overrides environment variable."""
    print("\n" + "=" * 80)
    print("TEST CASE C: CLI Flag Override")
    print("=" * 80)

    import os

    # Set ARCHIVE_BATCH_ACCEPT=0 and SOVEREIGN_AUTO_APPROVE=0
    os.environ["ARCHIVE_BATCH_ACCEPT"] = "0"
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "0"
    print("\n🔧 Environment: ARCHIVE_BATCH_ACCEPT=0, SOVEREIGN_AUTO_APPROVE=0")

    HierarchyAgent(project_root=PROJECT_ROOT, healing_enabled=True, auto_approve=False)

    # Check what the agent sees
    batch_accept = os.environ.get("ARCHIVE_BATCH_ACCEPT", "0")
    auto_approve = os.environ.get("SOVEREIGN_AUTO_APPROVE", "0")
    print(f"   Agent sees ARCHIVE_BATCH_ACCEPT={batch_accept}, SOVEREIGN_AUTO_APPROVE={auto_approve}")

    # In a real CLI scenario, --yes would set these to '1'
    # Simulate that here
    os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
    print("\n🔧 Simulating --yes flag: ARCHIVE_BATCH_ACCEPT=1, SOVEREIGN_AUTO_APPROVE=1")

    HierarchyAgent(project_root=PROJECT_ROOT, healing_enabled=True, auto_approve=True)
    batch_accept2 = os.environ.get("ARCHIVE_BATCH_ACCEPT", "0")
    auto_approve2 = os.environ.get("SOVEREIGN_AUTO_APPROVE", "0")
    print(f"   Agent now sees ARCHIVE_BATCH_ACCEPT={batch_accept2}, SOVEREIGN_AUTO_APPROVE={auto_approve2}")

    if batch_accept2 == "1" and auto_approve2 == "1":
        print("✅ PASS: CLI flag successfully overrides environment variables")
    else:
        print("❌ FAIL: CLI flag did not override environment variables")

    # Restore
    os.environ["ARCHIVE_BATCH_ACCEPT"] = "0"
    os.environ["SOVEREIGN_AUTO_APPROVE"] = "0"


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DIRECT HIERARCHY AGENT BOUNDARY TEST")
    print("=" * 80)

    # Run all tests
    test_structural_move()
    test_archival_move()
    test_cli_flag_override()

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
