#!/usr/bin/env python3
"""
Generate detailed syntax error report with file paths and error details.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import UnifiedCodeValidatorAgent


def main():
    project_root = Path(__file__).parent.parent

    print("Generating comprehensive syntax error report...")
    print()

    # Initialize validator
    agent = UnifiedCodeValidatorAgent(project_root=project_root)

    # Run validation
    results = agent.validate_repository()
    errors = results.get("syntax_errors", [])

    print(f"Total syntax errors: {len(errors)}")
    print()

    if len(errors) == 0:
        print("SUCCESS: All files are syntactically valid!")
        return 0

    # Group by layer
    by_layer = {}
    for e in errors:
        path_str = str(e.file_path)
        if "L0_" in path_str:
            layer = "L0"
        elif "L1_" in path_str:
            layer = "L1"
        elif "L2_" in path_str:
            layer = "L2"
        elif "L3_" in path_str:
            layer = "L3"
        elif "L4_" in path_str:
            layer = "L4"
        elif "L5_" in path_str:
            layer = "L5"
        elif "config" in path_str:
            layer = "Config"
        elif "apps_" in path_str:
            layer = "Apps"
        else:
            layer = "Other"

        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(e)

    # Print summary
    print("Errors by layer:")
    for layer in sorted(by_layer.keys()):
        print(f"  {layer}: {len(by_layer[layer])} errors")
    print()

    # Print detailed errors
    print("=" * 80)
    print("DETAILED ERROR REPORT")
    print("=" * 80)

    for layer in sorted(by_layer.keys()):
        print(f"\n### {layer} Layer ({len(by_layer[layer])} errors)")
        print("-" * 80)

        for e in by_layer[layer]:
            rel_path = e.file_path.relative_to(project_root)
            print(f"\nFile: {rel_path}")
            print(f"Line: {e.line_number}, Column: {e.column_number}")
            print(f"Error: {e.error_message}")

    print()
    print("=" * 80)

    return 1


if __name__ == "__main__":
    sys.exit(main())
