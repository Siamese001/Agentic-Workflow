#!/usr/bin/env python3
"""
test_unified_state_management.py - Phase 5 State Management Test Suite

Tests:
1. Atomic State Transaction Test: Simultaneous cleanup and manifest update
2. Drift Detection Verification: Detect file modifications without manifest update
3. Registry Synchronization: Verify callbacks are notified on state changes
4. Self-tests: Internal validation

Usage:
    python scripts/test_unified_state_management.py
    python scripts/test_unified_state_management.py --atomic-test
    python scripts/test_unified_state_management.py --drift-test
    python scripts/test_unified_state_management.py --registry-test
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_self_tests() -> dict[str, Any]:
    """Run the UnifiedStateManagementAgent's internal self-tests."""
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))
        return manager._run_self_tests()


def test_atomic_state_transaction() -> dict[str, Any]:
    """
    Atomic State Transaction Test:
    - Trigger a "deep cleanup" and a manifest update simultaneously
    - Verify that the state remains consistent (no manifest entry exists for a deleted file)
    """
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    results = {
        "status": "PASS",
        "states_created": 0,
        "cleanup_performed": False,
        "consistency_verified": False,
        "race_condition_detected": False,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))

        try:
            # Create multiple state entries
            for i in range(10):
                manager.set_state(f"test_state_{i}", {"index": i, "data": "x" * 100})
                results["states_created"] += 1

            # Simulate concurrent operations using threads
            errors = []

            def cleanup_thread():
                try:
                    # Perform cleanup with 0-day retention (delete all)
                    manager.perform_cleanup(retention_days=0)
                except Exception as e:
                    errors.append(f"Cleanup error: {e}")

            def update_thread():
                try:
                    # Try to update states during cleanup
                    for i in range(5):
                        manager.set_state(f"concurrent_state_{i}", {"concurrent": True})
                except Exception as e:
                    errors.append(f"Update error: {e}")

            # Run concurrently
            t1 = threading.Thread(target=cleanup_thread)
            t2 = threading.Thread(target=update_thread)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            results["cleanup_performed"] = True

            if errors:
                results["status"] = "FAIL"
                results["errors"] = errors
                return results

            # Verify consistency: no orphan entries
            report = manager.validate_and_sync()

            if report.orphan_entries:
                results["status"] = "FAIL"
                results["race_condition_detected"] = True
                results["orphan_entries"] = report.orphan_entries
            else:
                results["consistency_verified"] = True

            # Verify manifest matches physical files
            manifest_keys = set(manager._manifest.keys())
            for key in manifest_keys:
                entry = manager._manifest[key]
                file_path = manager.memory_root / entry.file_path
                if not file_path.exists():
                    results["status"] = "FAIL"
                    results["race_condition_detected"] = True
                    break

        except Exception as e:
            results["status"] = "FAIL"
            results["error"] = str(e)

    return results


def test_drift_detection() -> dict[str, Any]:
    """
    Drift Detection Verification:
    - Manually modify a file in .canon_memory/ without updating the manifest
    - Verify the Unified State Agent flags the integrity violation
    """
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    results = {
        "status": "PASS",
        "state_created": False,
        "file_modified": False,
        "drift_detected": False,
        "hash_mismatch_found": False,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))

        try:
            # Create a state entry
            test_key = "drift_test_state"
            original_data = {"original": True, "value": 42}
            manager.set_state(test_key, original_data)
            results["state_created"] = True

            # Get the file path
            entry = manager._manifest[test_key]
            file_path = manager.memory_root / entry.file_path

            # Manually modify the file WITHOUT updating manifest
            modified_data = {"modified": True, "value": 999}
            with open(file_path, "w") as f:
                json.dump(modified_data, f)
            results["file_modified"] = True

            # Run integrity check
            report = manager.validate_and_sync()

            # Verify drift was detected
            if test_key in report.hash_mismatches:
                results["drift_detected"] = True
                results["hash_mismatch_found"] = True
            else:
                results["status"] = "FAIL"
                results["error"] = "Drift not detected - hash mismatch not found"

            # Verify report shows unhealthy state
            if not report.is_healthy:
                results["integrity_flagged"] = True

        except Exception as e:
            results["status"] = "FAIL"
            results["error"] = str(e)

    return results


def test_ghost_detection() -> dict[str, Any]:
    """
    Ghost File Detection:
    - Create a file in .canon_memory/ without adding to manifest
    - Verify the agent detects it as a ghost file
    """
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    results = {
        "status": "PASS",
        "ghost_file_created": False,
        "ghost_detected": False,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))

        try:
            # Create a file directly without using set_state
            ghost_path = manager.memory_root / "state" / "ghost_file.json"
            ghost_path.parent.mkdir(parents=True, exist_ok=True)

            with open(ghost_path, "w") as f:
                json.dump({"ghost": True}, f)
            results["ghost_file_created"] = True

            # Run integrity check
            report = manager.validate_and_sync()

            # Verify ghost was detected
            ghost_rel_path = str(ghost_path.relative_to(manager.memory_root))
            if ghost_rel_path in report.ghost_files or any(
                "ghost_file" in g for g in report.ghost_files
            ):
                results["ghost_detected"] = True
            else:
                results["status"] = "FAIL"
                results["error"] = f"Ghost not detected. Ghost files: {report.ghost_files}"

        except Exception as e:
            results["status"] = "FAIL"
            results["error"] = str(e)

    return results


def test_registry_synchronization() -> dict[str, Any]:
    """
    Registry Synchronization Test:
    - Register a callback for state changes
    - Update an agent's status in the state
    - Verify the callback is notified
    """
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    results = {
        "status": "PASS",
        "callback_registered": False,
        "state_updated": False,
        "callback_notified": False,
        "notifications": [],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))

        try:
            # Create a callback to track notifications
            notifications = []

            def registry_callback(key: str, action: str):
                notifications.append(
                    {"key": key, "action": action, "timestamp": datetime.now().isoformat()}
                )

            # Register callback
            manager.register_callback(registry_callback)
            results["callback_registered"] = True

            # Perform state operations
            manager.set_state("agent_status_1", {"status": "active"})
            manager.set_state("agent_status_2", {"status": "idle"})
            manager.delete_state("agent_status_1")
            results["state_updated"] = True

            # Verify callbacks were notified
            if len(notifications) >= 3:
                results["callback_notified"] = True
                results["notifications"] = notifications

                # Verify correct actions
                actions = [n["action"] for n in notifications]
                if "set" in actions and "delete" in actions:
                    results["correct_actions"] = True
                else:
                    results["status"] = "FAIL"
                    results["error"] = f"Missing expected actions. Got: {actions}"
            else:
                results["status"] = "FAIL"
                results["error"] = f"Expected 3+ notifications, got {len(notifications)}"

            # Cleanup
            manager.unregister_callback(registry_callback)

        except Exception as e:
            results["status"] = "FAIL"
            results["error"] = str(e)

    return results


def test_cleanup_with_retention() -> dict[str, Any]:
    """
    Cleanup with Retention Test:
    - Create states with different ages
    - Run cleanup with retention policy
    - Verify only old states are removed
    """
    from datetime import timedelta

    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import (
        get_state_manager,
    )

    results = {
        "status": "PASS",
        "states_created": 0,
        "cleanup_performed": False,
        "correct_retention": False,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = get_state_manager(Path(tmpdir))

        try:
            # Create states
            for i in range(5):
                manager.set_state(f"retention_test_{i}", {"index": i})
                results["states_created"] += 1

            # Manually age some entries
            for key in ["retention_test_0", "retention_test_1"]:
                if key in manager._manifest:
                    entry = manager._manifest[key]
                    entry.updated_at = datetime.now() - timedelta(days=10)

            manager._save_manifest()

            # Run cleanup with 7-day retention
            cleanup_results = manager.perform_cleanup(retention_days=7)
            results["cleanup_performed"] = True
            results["cleanup_results"] = cleanup_results

            # Verify old entries were removed
            remaining_keys = list(manager._manifest.keys())

            if (
                "retention_test_0" not in remaining_keys
                and "retention_test_1" not in remaining_keys
            ):
                if "retention_test_2" in remaining_keys:
                    results["correct_retention"] = True
                else:
                    results["status"] = "FAIL"
                    results["error"] = "Recent entries were incorrectly removed"
            else:
                results["status"] = "FAIL"
                results["error"] = "Old entries were not removed"

        except Exception as e:
            results["status"] = "FAIL"
            results["error"] = str(e)

    return results


def main():
    parser = argparse.ArgumentParser(description="Test UnifiedStateManagementAgent")
    parser.add_argument("--self-test", action="store_true", help="Run only self-tests")
    parser.add_argument(
        "--atomic-test", action="store_true", help="Run only atomic transaction test"
    )
    parser.add_argument("--drift-test", action="store_true", help="Run only drift detection test")
    parser.add_argument("--registry-test", action="store_true", help="Run only registry sync test")
    parser.add_argument("--output-dir", type=str, default="test_results", help="Output directory")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("UnifiedStateManagementAgent Test Suite (Phase 5)")
    print("=" * 60)

    results = {
        "timestamp": timestamp,
        "tests": {},
    }

    all_passed = True
    run_all = not any([args.self_test, args.atomic_test, args.drift_test, args.registry_test])

    # Self-tests
    if args.self_test or run_all:
        print("\n[1/6] Running self-tests...")
        try:
            self_test_results = run_self_tests()
            results["tests"]["self_tests"] = self_test_results
            passed = self_test_results.get("passed", 0)
            failed = self_test_results.get("failed", 0)
            print(f"  ✓ Self-tests: {passed} passed, {failed} failed")
            if failed > 0:
                all_passed = False
        except Exception as e:
            print(f"  ✗ Self-tests failed: {e}")
            results["tests"]["self_tests"] = {"error": str(e)}
            all_passed = False

    # Atomic transaction test
    if args.atomic_test or run_all:
        print("\n[2/6] Running atomic state transaction test...")
        try:
            atomic_results = test_atomic_state_transaction()
            results["tests"]["atomic_transaction"] = atomic_results

            if atomic_results.get("status") == "PASS":
                print("  ✓ Atomic transaction PASSED")
                print(f"    States created: {atomic_results.get('states_created')}")
                print(f"    Consistency verified: {atomic_results.get('consistency_verified')}")
            else:
                print(f"  ✗ Atomic transaction FAILED: {atomic_results.get('error', 'Unknown')}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Atomic transaction test failed: {e}")
            results["tests"]["atomic_transaction"] = {"error": str(e)}
            all_passed = False

    # Drift detection test
    if args.drift_test or run_all:
        print("\n[3/6] Running drift detection test...")
        try:
            drift_results = test_drift_detection()
            results["tests"]["drift_detection"] = drift_results

            if drift_results.get("status") == "PASS":
                print("  ✓ Drift detection PASSED")
                print(f"    File modified: {drift_results.get('file_modified')}")
                print(f"    Drift detected: {drift_results.get('drift_detected')}")
            else:
                print(f"  ✗ Drift detection FAILED: {drift_results.get('error', 'Unknown')}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Drift detection test failed: {e}")
            results["tests"]["drift_detection"] = {"error": str(e)}
            all_passed = False

    # Ghost detection test
    if run_all:
        print("\n[4/6] Running ghost file detection test...")
        try:
            ghost_results = test_ghost_detection()
            results["tests"]["ghost_detection"] = ghost_results

            if ghost_results.get("status") == "PASS":
                print("  ✓ Ghost detection PASSED")
                print(f"    Ghost file created: {ghost_results.get('ghost_file_created')}")
                print(f"    Ghost detected: {ghost_results.get('ghost_detected')}")
            else:
                print(f"  ✗ Ghost detection FAILED: {ghost_results.get('error', 'Unknown')}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Ghost detection test failed: {e}")
            results["tests"]["ghost_detection"] = {"error": str(e)}
            all_passed = False

    # Registry synchronization test
    if args.registry_test or run_all:
        print("\n[5/6] Running registry synchronization test...")
        try:
            registry_results = test_registry_synchronization()
            results["tests"]["registry_sync"] = registry_results

            if registry_results.get("status") == "PASS":
                print("  ✓ Registry synchronization PASSED")
                print(f"    Callback registered: {registry_results.get('callback_registered')}")
                print(f"    Callback notified: {registry_results.get('callback_notified')}")
                print(f"    Notifications: {len(registry_results.get('notifications', []))}")
            else:
                print(
                    f"  ✗ Registry synchronization FAILED: {registry_results.get('error', 'Unknown')}"
                )
                all_passed = False
        except Exception as e:
            print(f"  ✗ Registry synchronization test failed: {e}")
            results["tests"]["registry_sync"] = {"error": str(e)}
            all_passed = False

    # Cleanup with retention test
    if run_all:
        print("\n[6/6] Running cleanup with retention test...")
        try:
            cleanup_results = test_cleanup_with_retention()
            results["tests"]["cleanup_retention"] = cleanup_results

            if cleanup_results.get("status") == "PASS":
                print("  ✓ Cleanup with retention PASSED")
                print(f"    States created: {cleanup_results.get('states_created')}")
                print(f"    Correct retention: {cleanup_results.get('correct_retention')}")
            else:
                print(
                    f"  ✗ Cleanup with retention FAILED: {cleanup_results.get('error', 'Unknown')}"
                )
                all_passed = False
        except Exception as e:
            print(f"  ✗ Cleanup with retention test failed: {e}")
            results["tests"]["cleanup_retention"] = {"error": str(e)}
            all_passed = False

    # Save results
    output_file = output_dir / f"unified_state_management_test_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")

    if all_passed:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
