"""ADG-Driven Test Failure Analysis & Wave Prioritization

This script analyzes test failures using ADG to identify patterns and
prioritize waves that maximize burndown rate.
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def run_pytest_analysis():
    """Run pytest to collect failure patterns."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q", "--no-header"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent.parent.parent))

    return result.stdout + result.stderr


def parse_failure_patterns(output: str):
    """Parse pytest output to extract failure patterns."""
    patterns = {
        "collection_errors": [],
        "import_errors": [],
        "name_errors": [],
        "type_errors": [],
        "fixture_errors": [],
        "assertion_failures": [],
        "other_failures": [],
    }

    lines = output.split("\n")
    current_file = None

    for line in lines:
        # Extract test file paths
        if "tests/" in line and ("::" in line or ".py" in line):
            parts = line.split("::")
            if parts:
                file_part = parts[0].strip()
                if "tests/" in file_part:
                    current_file = file_part

        # Categorize errors
        if "ImportError" in line or "ModuleNotFoundError" in line:
            patterns["import_errors"].append((current_file, line.strip()))
        elif "NameError" in line:
            patterns["name_errors"].append((current_file, line.strip()))
        elif "TypeError" in line:
            patterns["type_errors"].append((current_file, line.strip()))
        elif "fixture" in line.lower() and "error" in line.lower():
            patterns["fixture_errors"].append((current_file, line.strip()))
        elif "AssertionError" in line or "assert" in line.lower():
            patterns["assertion_failures"].append((current_file, line.strip()))
        elif "ERROR collecting" in line:
            patterns["collection_errors"].append((current_file, line.strip()))
        elif "FAILED" in line and "::" in line:
            # General failure
            patterns["other_failures"].append((current_file, line.strip()))

    return patterns


def analyze_by_layer(patterns: dict):
    """Group failures by architectural layer."""
    layer_mapping = {"L0": [], "L1": [], "L2": [], "L3": [], "L4": [], "L5": [], "L6": [], "unknown": []}

    def get_layer(file_path: str) -> str:
        if not file_path:
            return "unknown"
        path_lower = file_path.lower()
        if "l0" in path_lower or "routing" in path_lower:
            return "L0"
        elif "l1" in path_lower or "reasoning" in path_lower:
            return "L1"
        elif "l2" in path_lower or "execution" in path_lower:
            return "L2"
        elif "l3" in path_lower or "orchestrator" in path_lower:
            return "L3"
        elif "l4" in path_lower or "state" in path_lower or "memory" in path_lower:
            return "L4"
        elif "l5" in path_lower or "safety" in path_lower or "guardian" in path_lower:
            return "L5"
        elif "l6" in path_lower or "observability" in path_lower or "telemetry" in path_lower:
            return "L6"
        elif "e2e" in path_lower:
            return "E2E"
        elif "integration" in path_lower:
            return "Integration"
        return "unknown"

    for category, errors in patterns.items():
        for file_path, error_line in errors:
            layer = get_layer(file_path)
            layer_mapping.setdefault(layer, []).append(
                {"file": file_path, "error": error_line, "category": category}
            )

    return layer_mapping


def identify_missing_imports(patterns: dict) -> Counter:
    """Identify most commonly missing imports."""
    missing = Counter()

    for file_path, error_line in patterns.get("import_errors", []):
        # Extract module name from error
        if "No module named" in error_line:
            parts = error_line.split("No module named")
            if len(parts) > 1:
                module = parts[1].strip("'\" ")
                missing[module] += 1
        elif "cannot import name" in error_line:
            parts = error_line.split("cannot import name")
            if len(parts) > 1:
                name = parts[1].strip("'\" ")
                missing[f"name:{name}"] += 1

    return missing


def generate_wave_plan(layer_mapping: dict, missing_imports: Counter) -> list:
    """Generate prioritized wave plan based on impact analysis."""

    # Calculate impact scores
    waves = []

    # Wave 1: Collection errors (blocks all testing)
    collection_errors = len(layer_mapping.get("unknown", [])) + sum(
        1 for e in layer_mapping.get("L0", []) if "collection" in e.get("category", "")
    )
    if collection_errors > 0:
        waves.append(
            {
                "wave": 1,
                "focus": "Collection Errors & Import Resolution",
                "files": list(
                    {
                        e["file"]
                        for layer in layer_mapping.values()
                        for e in layer
                        if "collection" in e.get("category", "")
                    }
                )[:20],
                "impact": "High - Blocks test discovery",
                "count": collection_errors,
            }
        )

    # Wave 2: Most common missing imports (high blast radius)
    if missing_imports:
        top_missing = missing_imports.most_common(5)
        waves.append(
            {
                "wave": 2,
                "focus": "High-Impact Missing Imports",
                "targets": [m[0] for m in top_missing],
                "impact": f"High - {sum(m[1] for m in top_missing)} test files affected",
                "count": len(top_missing),
            }
        )

    # Wave 3: L5 Safety (critical path)
    l5_errors = layer_mapping.get("L5", [])
    if l5_errors:
        waves.append(
            {
                "wave": 3,
                "focus": "L5 Safety Layer Fixes",
                "files": list({e["file"] for e in l5_errors})[:15],
                "impact": "Critical - Safety infrastructure",
                "count": len(l5_errors),
            }
        )

    # Wave 4: L4 State (data layer)
    l4_errors = layer_mapping.get("L4", [])
    if l4_errors:
        waves.append(
            {
                "wave": 4,
                "focus": "L4 State/Memory Layer Fixes",
                "files": list({e["file"] for e in l4_errors})[:15],
                "impact": "High - State management",
                "count": len(l4_errors),
            }
        )

    # Wave 5: E2E tests
    e2e_errors = layer_mapping.get("E2E", [])
    if e2e_errors:
        waves.append(
            {
                "wave": 5,
                "focus": "E2E Test Fixes",
                "files": list({e["file"] for e in e2e_errors})[:15],
                "impact": "Medium - Integration testing",
                "count": len(e2e_errors),
            }
        )

    # Wave 6: Remaining layers
    remaining = (
        layer_mapping.get("L0", [])
        + layer_mapping.get("L1", [])
        + layer_mapping.get("L2", [])
        + layer_mapping.get("L3", [])
    )
    if remaining:
        waves.append(
            {
                "wave": 6,
                "focus": "Core Runtime Layer Fixes (L0-L3)",
                "files": list({e["file"] for e in remaining})[:20],
                "impact": "Medium - Core functionality",
                "count": len(remaining),
            }
        )

    return waves


def main():
    """Main analysis entry point."""
    print("=" * 70)
    print("ADG-DRIVEN TEST FAILURE ANALYSIS")
    print("=" * 70)

    # Run pytest analysis
    print("\n[1/4] Running pytest failure collection...")
    output = run_pytest_analysis()

    # Parse patterns
    print("[2/4] Parsing failure patterns...")
    patterns = parse_failure_patterns(output)

    # Analyze by layer
    print("[3/4] Analyzing by architectural layer...")
    layer_mapping = analyze_by_layer(patterns)

    # Identify missing imports
    print("[4/4] Identifying common missing imports...")
    missing_imports = identify_missing_imports(patterns)

    # Generate wave plan
    waves = generate_wave_plan(layer_mapping, missing_imports)

    # Print summary
    print("\n" + "=" * 70)
    print("FAILURE SUMMARY BY CATEGORY")
    print("=" * 70)
    for category, errors in patterns.items():
        print(f"  {category}: {len(errors)} occurrences")

    print("\n" + "=" * 70)
    print("FAILURE SUMMARY BY LAYER")
    print("=" * 70)
    for layer, errors in sorted(layer_mapping.items()):
        if errors:
            print(f"  {layer}: {len(errors)} errors")

    print("\n" + "=" * 70)
    print("TOP MISSING IMPORTS (Blast Radius)")
    print("=" * 70)
    for module, count in missing_imports.most_common(10):
        print(f"  {module}: {count} test files affected")

    print("\n" + "=" * 70)
    print("PRIORITIZED WAVE PLAN")
    print("=" * 70)
    for wave in waves:
        print(f"\n📊 Wave {wave['wave']}: {wave['focus']}")
        print(f"   Impact: {wave['impact']}")
        print(f"   Items: {wave['count']}")
        if "targets" in wave:
            print(f"   Targets: {', '.join(wave['targets'])}")
        if "files" in wave:
            print("   Key Files:")
            for f in wave["files"][:5]:
                print(f"     - {f}")

    # Save report
    report_path = Path("docs/reports/test_failure_analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(
            {
                "patterns": {k: len(v) for k, v in patterns.items()},
                "by_layer": {k: len(v) for k, v in layer_mapping.items()},
                "missing_imports": dict(missing_imports.most_common(20)),
                "waves": waves,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Full report saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
