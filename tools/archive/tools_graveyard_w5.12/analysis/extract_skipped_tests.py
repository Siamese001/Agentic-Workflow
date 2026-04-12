#!/usr/bin/env python3
"""
Extract all skipped tests from pytest collection output and categorize by phase.
"""

import json


def extract_skipped_tests():
    """Extract skipped tests from pytest collection."""
    # Run pytest collection
    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", "--collect-only", "--tb=no"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )

    output = result.stdout

    # Parse skipped tests
    skipped_tests = []
    current_test = None
    current_reason = ""

    for line in output.split("\n"):
        line = line.strip()

        # Detect test function
        if line.startswith("<Function test_"):
            if "skip" in line.lower():
                current_test = line.replace("<Function ", "").replace(">", "")
                skipped_tests.append(
                    {
                        "test_name": current_test,
                        "reason": current_reason or "skip decorator detected",
                        "file_path": extract_file_path(line),
                    }
                )
                current_reason = ""
            else:
                current_test = None
                current_reason = ""

        # Detect module skip
        elif line.startswith("<Module ") and "skip" in line.lower():
            module_name = line.replace("<Module ", "").replace(">", "")
            skipped_tests.append(
                {
                    "test_name": module_name,
                    "reason": current_reason or "module skip",
                    "file_path": module_name,
                }
            )
            current_reason = ""

        # Collect reason lines (non-test lines between test entries)
        elif current_test and line and not line.startswith(("<", "collecting", "collected")):
            current_reason += line + " "

    return skipped_tests


def extract_file_path(test_line):
    """Extract file path from test line."""
    # Simple heuristic - look for .py in the line
    if ".py::" in test_line:
        return test_line.split("::")[0]
    return "unknown"


def categorize_by_phase(skipped_tests):
    """Categorize skipped tests by phase based on file path."""
    phases = {
        "Phase 1 - Foundation": [],
        "Phase 2 - Dependency Management": [],
        "Phase 3 - Test Quality": [],
        "Phase 4 - Documentation": [],
        "Phase 5 - Integration": [],
        "Uncategorized": [],
    }

    for test in skipped_tests:
        file_path = test["file_path"].lower()

        if "guardian" in file_path or "core" in file_path:
            phases["Phase 1 - Foundation"].append(test)
        elif "dependency" in file_path or "import" in file_path:
            phases["Phase 2 - Dependency Management"].append(test)
        elif "test_" in file_path and "quality" in file_path:
            phases["Phase 3 - Test Quality"].append(test)
        elif "docs" in file_path or "readme" in file_path:
            phases["Phase 4 - Documentation"].append(test)
        elif "integration" in file_path or "e2e" in file_path:
            phases["Phase 5 - Integration"].append(test)
        else:
            phases["Uncategorized"].append(test)

    return phases


def create_burndown_plan(phases):
    """Create burndown plan with 5-10 files per wave."""
    plan = {}
    wave_num = 1

    for phase_name, tests in phases.items():
        if not tests:
            continue

        # Group by file path
        files = {}
        for test in tests:
            file_path = test["file_path"]
            if file_path not in files:
                files[file_path] = []
            files[file_path].append(test)

        # Create waves with 5-10 files each
        file_list = list(files.keys())
        for i in range(0, len(file_list), 7):  # 7 files per wave (within 5-10 range)
            wave_files = file_list[i : i + 7]
            wave_key = f"Wave {wave_num} - {phase_name}"
            plan[wave_key] = {
                "phase": phase_name,
                "files": wave_files,
                "test_count": sum(len(files[f]) for f in wave_files),
                "description": f"Fix {len(wave_files)} files with {sum(len(files[f]) for f in wave_files)} skipped tests",
            }
            wave_num += 1

    return plan


def main():
    print("Extracting skipped tests...")
    skipped_tests = extract_skipped_tests()
    print(f"Found {len(skipped_tests)} skipped tests")

    print("Categorizing by phase...")
    phases = categorize_by_phase(skipped_tests)

    for phase_name, tests in phases.items():
        print(f"{phase_name}: {len(tests)} tests")

    print("Creating burndown plan...")
    plan = create_burndown_plan(phases)

    # Save results
    results = {
        "total_skipped": len(skipped_tests),
        "phases": {k: len(v) for k, v in phases.items()},
        "burndown_plan": plan,
        "all_skipped_tests": skipped_tests,
    }

    with open("artifacts/skip_burndown_plan.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Burndown plan saved to artifacts/skip_burndown_plan.json")
    print(f"Total waves: {len(plan)}")

    # Print summary
    for wave_key, wave_data in plan.items():
        print(f"{wave_key}: {wave_data['files']}")

    return results


if __name__ == "__main__":
    main()
