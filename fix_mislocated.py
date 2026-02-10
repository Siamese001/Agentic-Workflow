#!/usr/bin/env python3
"""
Fix remaining mislocated test.
"""

import json
import pathlib
import shutil


def main():
    """Fix the single remaining mislocated test."""
    with open("tests/_contracts/mirror_discovery_snapshot.json") as f:
        snapshot = json.load(f)

    mislocated = [m for m in snapshot["modules"] if m["status"] == "MISLOCATED"]
    print(f"Found {len(mislocated)} mislocated tests")

    for module_info in mislocated:
        module_path = pathlib.Path(module_info["module"])
        expected_test_path = pathlib.Path(module_info["expected_test"])

        # Find the actual test file
        module_name = module_path.stem
        test_root = pathlib.Path("tests")

        actual_test = None
        for test_file in test_root.rglob("test_*.py"):
            if test_file.name == f"test_{module_name}.py":
                actual_test = test_file
                break

        if actual_test and actual_test != expected_test_path:
            print(f"Moving: {actual_test} -> {expected_test_path}")

            # Create target directory
            expected_test_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            try:
                shutil.move(str(actual_test), str(expected_test_path))
                print("Successfully moved mislocated test")
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"Failed to move {actual_test}: {e}")


if __name__ == "__main__":
    main()
