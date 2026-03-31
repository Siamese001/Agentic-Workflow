#!/usr/bin/env python3
"""Check ADG status and system_learning test results"""

import sys

sys.path.insert(0, ".")

import subprocess

from tools.adg.adg_mcp_server import adg_status


def check_adg_status():
    """Check ADG freshness and stats"""
    try:
        status = adg_status()
        data = status["data"]
        print(f"✅ ADG Fresh: {data['is_fresh']}")
        print(f"📊 Nodes: {data['node_count']}")
        print(f"🔗 Edges: {data['edge_count']}")
        print(f"⏱️  Age: {data['age_seconds']:.1f}s")
        return data["is_fresh"]
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ ADG Status Error: {e}")
        return False


def run_system_learning_tests():
    """Run system_learning test suite"""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/system_learning/stores/",
                "tests/unit/system_learning/adapters/",
                "tests/system_learning/test_system_learning_memory_bridge.py",
                "--tb=short",
                "-q",
            ],
            capture_output=True,
            text=True,
            cwd=".",
        )

        if result.returncode == 0:
            # Extract test count from output
            lines = result.stdout.split("\n")
            for line in lines:
                if "passed" in line and "skipped" in line:
                    print(f"✅ Tests: {line.strip()}")
                    break
            return True
        else:
            print(f"❌ Tests Failed: {result.stderr}")
            return False
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Test Error: {e}")
        return False


def check_persistent_memory():
    """Check if persistent memory database exists"""
    import os

    db_path = "artifacts/memory/unified_memory.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Memory DB: {size} bytes")
        return True
    else:
        print("⚠️  Memory DB: Not found (will be created)")
        return False


def main():
    print("=== System Learning CI Status Check ===")

    adg_ok = check_adg_status()
    tests_ok = run_system_learning_tests()
    memory_ok = check_persistent_memory()

    print("\n=== Summary ===")
    if adg_ok and tests_ok:
        print("✅ All checks passed - system_learning is continuously updated via CI")
        return 0
    else:
        print("❌ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
