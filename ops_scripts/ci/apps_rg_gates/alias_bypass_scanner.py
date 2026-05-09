"""Alias Bypass Scanner — AG-RGGOV-W8 CI Gate

Scanner verifying agentic_core aliases cannot point to apps_rg
runtime engines, planners, orchestrators, hops, executors, or providers.

Ensures apps_engines_aliases.py cannot resurrect apps_rg runtime code.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


# Forbidden targets for aliases
FORBIDDEN_ALIAS_TARGETS: tuple[str, ...] = (
    # apps_rg runtime components
    "apps_rg.",
    # Runtime authority
    "planner", "planners",
    "router", "routers",
    "orchestrator", "orchestrators",
    "executor", "executors",
    "hop", "hops",
    "engine", "engines",
    "provider", "providers",
    # Specific problematic patterns
    "get_llm_gateway",
    "SovereignLLMGateway",
)

# Files to scan for aliases
ALIAS_FILES: tuple[str, ...] = (
    "apps_engines_aliases.py",
    "aliases.py",
    "_aliases.py",
)


def scan_for_alias_bypass(
    repo_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Scan for alias bypasses that resurrect apps_rg runtime code.

    Args:
        repo_path: Path to repository root

    Returns:
        Tuple of (passed, violations)
    """
    if repo_path is None:
        repo_path = Path(__file__).parent.parent.parent.parent.parent

    violations: list[str] = []

    for alias_file in ALIAS_FILES:
        for py_file in repo_path.rglob(alias_file):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError) as e:
                violations.append(f"{py_file}: parse error: {e}")
                continue

            for node in ast.walk(tree):
                # Check assignments (alias definitions)
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            target_name = target.id
                            # Check if target name suggests runtime component
                            for forbidden in FORBIDDEN_ALIAS_TARGETS:
                                if forbidden.lower() in target_name.lower():
                                    violations.append(
                                        f"{py_file}:{node.lineno}: "
                                        f"suspicious alias: {target_name}"
                                    )

                # Check imports in alias files
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in FORBIDDEN_ALIAS_TARGETS:
                            if forbidden in alias.name:
                                violations.append(
                                    f"{py_file}:{node.lineno}: "
                                    f"forbidden import in alias file: {alias.name}"
                                )

                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for forbidden in FORBIDDEN_ALIAS_TARGETS:
                        if forbidden in module:
                            violations.append(
                                f"{py_file}:{node.lineno}: "
                                f"forbidden import from in alias file: {module}"
                            )

    passed = len(violations) == 0
    return passed, violations


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for CI gate."""
    import argparse

    parser = argparse.ArgumentParser(
        description="alias bypass scanner"
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        help="Path to repository root",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args(argv)

    passed, violations = scan_for_alias_bypass(args.repo_path)

    if args.output_format == "json":
        import json
        result = {
            "passed": passed,
            "violations": violations,
            "scanner": "alias_bypass_scanner",
            "version": "W8.0",
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Alias Bypass Scanner W8.0")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print(f"Violations: {len(violations)}")
        if violations:
            print("\nViolations:")
            for v in violations:
                print(f"  - {v}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
