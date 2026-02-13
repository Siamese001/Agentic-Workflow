"""
Residual rglob/glob Audit Script

This script provides a detailed audit of the remaining 81 rglob/glob calls
in agentic_core to identify patterns and prioritize refactoring.

Author: Cascade
Date: January 19, 2026
Phase: 6.9 - Final Mile
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any


def audit_residual_rglob_calls(project_root: Path) -> dict[str, Any]:
    """
    Audit all remaining rglob/glob calls in agentic_core.

    Returns:
        Dictionary with detailed audit results
    """
    agentic_core = project_root / "agentic_core"

    # Track rglob/glob calls with detailed context
    rglob_calls = []
    files_scanned = 0

    # Scan all Python files
    for py_file in agentic_core.rglob("*.py"):
        # Skip SSOT files (legitimate usage)
        if "ssot_discovery.py" in str(py_file) or "scan_guard.py" in str(py_file):
            continue

        files_scanned += 1

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Detect .rglob() and .glob() attribute calls
                if isinstance(node, ast.Attribute) and node.attr in ["rglob", "glob"]:
                    line_no = getattr(node, "lineno", 0)

                    # Get context (the line of code)
                    context = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                    # Determine the pattern
                    pattern = "unknown"
                    if "*.py" in context or '"*.py"' in context or "'*.py'" in context:
                        pattern = "*.py"
                    elif "*.json" in context or '"*.json"' in context or "'*.json'" in context:
                        pattern = "*.json"
                    elif "*.md" in context or '"*.md"' in context or "'*.md'" in context:
                        pattern = "*.md"
                    elif "*Agent.py" in context:
                        pattern = "*Agent.py"
                    elif "*" in context:
                        pattern = "other_pattern"

                    rglob_calls.append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "line": line_no,
                            "method": node.attr,
                            "context": context[:100],
                            "pattern": pattern,
                            "directory": str(py_file.parent.relative_to(project_root)),
                        },
                    )

        except SyntaxError:
            continue
        # guardian: allow-silent-swallow
        except Exception:
            continue

    # Analyze by directory
    by_directory = defaultdict(list)
    for call in rglob_calls:
        by_directory[call["directory"]].append(call)

    # Analyze by pattern
    by_pattern = defaultdict(list)
    for call in rglob_calls:
        by_pattern[call["pattern"]].append(call)

    # Analyze by file
    by_file = defaultdict(list)
    for call in rglob_calls:
        by_file[call["file"]].append(call)

    return {
        "total_calls": len(rglob_calls),
        "files_scanned": files_scanned,
        "calls": rglob_calls,
        "by_directory": dict(by_directory),
        "by_pattern": dict(by_pattern),
        "by_file": dict(by_file),
    }


def print_audit_report(audit_results: dict[str, Any]) -> None:
    """Print a formatted audit report."""
    print("=" * 80)
    print("RESIDUAL RGLOB/GLOB AUDIT REPORT")
    print("=" * 80)

    print(f"\nTotal rglob/glob calls: {audit_results['total_calls']}")
    print(f"Files scanned: {audit_results['files_scanned']}")

    # By Directory
    print("\n" + "=" * 80)
    print("BREAKDOWN BY DIRECTORY")
    print("=" * 80)

    sorted_dirs = sorted(audit_results["by_directory"].items(), key=lambda x: len(x[1]), reverse=True)

    for directory, calls in sorted_dirs[:15]:
        print(f"{len(calls):3d} calls: {directory}")

    # By Pattern
    print("\n" + "=" * 80)
    print("BREAKDOWN BY PATTERN")
    print("=" * 80)

    sorted_patterns = sorted(audit_results["by_pattern"].items(), key=lambda x: len(x[1]), reverse=True)

    for pattern, calls in sorted_patterns:
        print(f"{len(calls):3d} calls: {pattern}")
        # Show sample files
        sample_files = list({call["file"] for call in calls[:3]})
        for file in sample_files:
            print(f"      - {file}")

    # Top Offending Files
    print("\n" + "=" * 80)
    print("TOP 20 OFFENDING FILES")
    print("=" * 80)

    sorted_files = sorted(audit_results["by_file"].items(), key=lambda x: len(x[1]), reverse=True)

    for file_path, calls in sorted_files[:20]:
        print(f"{len(calls):2d} calls: {file_path}")
        for call in calls:
            print(f"      Line {call['line']:4d}: {call['context'][:80]}")

    # Refactoring Priority
    print("\n" + "=" * 80)
    print("REFACTORING PRIORITY (High to Low)")
    print("=" * 80)

    print("\n1. HIGH PRIORITY - L0_routing/scripts (Easy wins, 1 call each)")
    l0_scripts = [f for f, calls in sorted_files if "L0_routing/scripts" in f]
    print(f"   {len(l0_scripts)} files to refactor")
    for file in l0_scripts[:10]:
        print(f"   - {file}")

    print("\n2. MEDIUM PRIORITY - Other directories")
    other_files = [f for f, calls in sorted_files if "L0_routing/scripts" not in f]
    print(f"   {len(other_files)} files to refactor")
    for file in other_files[:10]:
        print(f"   - {file}")

    # Estimated effort to sub-50
    print("\n" + "=" * 80)
    print("PATH TO SUB-50")
    print("=" * 80)

    current = audit_results["total_calls"]
    target = 50
    needed = current - target

    print(f"Current count: {current}")
    print(f"Target count: {target}")
    print(f"Calls to eliminate: {needed}")
    print("\nRecommended approach:")
    print(f"  1. Refactor all L0_routing/scripts files ({len(l0_scripts)} files)")
    print("  2. Refactor remaining high-value targets")
    print("  3. Verify with AST scanner")


def main():
    """Run the audit."""
    project_root = Path(__file__).parent.parent

    print("Scanning agentic_core for residual rglob/glob calls...")
    audit_results = audit_residual_rglob_calls(project_root)

    print_audit_report(audit_results)

    # Save detailed results to JSON
    import json

    output_file = project_root / "audit_residual_rglob_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print(f"\n\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
