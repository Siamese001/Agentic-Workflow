#!/usr/bin/env python3
"""
Verification Script for Universal Healing Implementation
Tests the actual execute_ssot.py with the Universal Healing patch.
"""

import subprocess
import sys
from pathlib import Path


def run_verification():
    """Run verification tests on the Universal Healing implementation."""
    print("🔍 Universal Healing Implementation Verification")
    print("=" * 60)

    project_root = Path.cwd()

    # Test 1: Dry-run mode (should not trigger healing)
    print("\n📋 Test 1: Dry-run Mode Verification")
    print("-" * 40)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "agentic_core/L0_maintenance/scripts/execute_ssot.py",
                "--territory",
                "prompt_governance",
                "--dry-run",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ Dry-run execution completed successfully")
            if "🛡️ Triggering Sovereignty Purge" in result.stdout:
                print("❌ FAIL: Sovereignty purge triggered in dry-run mode")
                return False
            else:
                print("✅ PASS: Sovereignty purge correctly skipped in dry-run mode")
        else:
            print(f"❌ Dry-run failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Dry-run test timed out")
        return False
    except Exception as e:
        print(f"❌ Dry-run test failed: {e}")
        return False

    # Test 2: Agent availability check
    print("\n📋 Test 2: Agent Registry Verification")
    print("-" * 40)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "agentic_core/L0_maintenance/scripts/execute_ssot.py",
                "--list-agents",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Agent listing completed successfully")

            # Check for key agents
            required_agents = [
                "PascalSovereigntyAgent",
                "RootHygieneAgent",
                "ArchitectureGovernorAgent",
                "HierarchyAgent",
                "LocationAgent",
            ]

            missing_agents = []
            for agent in required_agents:
                if agent not in result.stdout:
                    missing_agents.append(agent)

            if missing_agents:
                print(f"❌ FAIL: Missing agents: {missing_agents}")
                return False
            else:
                print("✅ PASS: All required agents are available")
        else:
            print(f"❌ Agent listing failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Agent listing timed out")
        return False
    except Exception as e:
        print(f"❌ Agent listing failed: {e}")
        return False

    # Test 3: Help/usage verification
    print("\n📋 Test 3: Help System Verification")
    print("-" * 40)
    try:
        result = subprocess.run(
            [sys.executable, "agentic_core/L0_maintenance/scripts/execute_ssot.py", "--help"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Help system working")

            # Check for key flags
            required_flags = ["--dry-run", "--territory", "--domains", "--list-agents"]
            missing_flags = [flag for flag in required_flags if flag not in result.stdout]

            if missing_flags:
                print(f"❌ FAIL: Missing flags: {missing_flags}")
                return False
            else:
                print("✅ PASS: All required flags are present")
        else:
            print(f"❌ Help system failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Help system timed out")
        return False
    except Exception as e:
        print(f"❌ Help system failed: {e}")
        return False

    # Test 4: Import verification for the patched module
    print("\n📋 Test 4: Module Import Verification")
    print("-" * 40)
    try:
        # Test that the patched module can be imported
        sys.path.insert(0, str(project_root))
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            AutonomousDecisionEngine,
            RuntimeStateManager,
            main,
        )

        print("✅ PASS: Patched module imports successfully")

        # Test decision engine functionality
        decision_engine = AutonomousDecisionEngine(enable_llm=False)
        confidence = decision_engine.calculate_healing_confidence(
            violations_count=5, violation_types=["NAMING"], territory="prompt_governance"
        )
        print(f"✅ PASS: Decision engine working (confidence: {confidence.value:.2f})")

    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Module test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 VERIFICATION COMPLETE")
    print("=" * 60)
    print("✅ Universal Healing Implementation is READY")
    print("\nKey Features Verified:")
    print("- Dry-run safety (prevents accidental healing)")
    print("- Agent registry (all agents discoverable)")
    print("- Help system (all flags available)")
    print("- Module imports (patched code loads correctly)")
    print("- Decision engine (confidence calculations working)")

    return True


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
