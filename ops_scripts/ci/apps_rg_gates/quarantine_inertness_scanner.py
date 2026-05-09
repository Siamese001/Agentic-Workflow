"""Quarantine Inertness Scanner — AG-RGGOV-W8 CI Gate

Scanner verifying quarantined modules raise RuntimeError immediately
and are not reachable from live apps_rg code.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


QUARANTINE_PATHS: tuple[str, ...] = (
    "quarantine",
    "_quarantine",
    "archives",
    "_archived",
)

REQUIRED_QUARANTINE_PATTERN: str = "RuntimeError"


def check_quarantine_inertness(
    quarantine_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Check quarantined modules raise RuntimeError immediately.

    Args:
        quarantine_path: Path to quarantine directory

    Returns:
        Tuple of (passed, violations)
    """
    violations: list[str] = []

    # Find all quarantine directories
    repo_root = Path(__file__).parent.parent.parent.parent.parent

    if quarantine_path is None:
        quarantine_dirs = [
            repo_root / p for p in QUARANTINE_PATHS if (repo_root / p).exists()
        ]
    else:
        quarantine_dirs = [quarantine_path]

    for q_dir in quarantine_dirs:
        if not q_dir.exists():
            continue

        for py_file in q_dir.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError) as e:
                violations.append(f"{py_file}: parse error: {e}")
                continue

            # Check for RuntimeError raise
            has_runtime_error = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise):
                    if isinstance(node.exc, ast.Call):
                        if isinstance(node.exc.func, ast.Name):
                            if node.exc.func.id == "RuntimeError":
                                has_runtime_error = True
                    elif isinstance(node.exc, ast.Name):
                        if node.exc.id == "RuntimeError":
                            has_runtime_error = True

            if not has_runtime_error:
                violations.append(
                    f"{py_file}: missing RuntimeError raise (quarantine inertness)"
                )

    passed = len(violations) == 0
    return passed, violations


def check_live_apps_rg_does_not_import_quarantine(
    apps_rg_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Check live apps_rg does not import from quarantine.

    Args:
        apps_rg_path: Path to apps_rg directory

    Returns:
        Tuple of (passed, violations)
    """
    if apps_rg_path is None:
        apps_rg_path = Path(__file__).parent.parent.parent.parent.parent / "apps_rg"

    violations: list[str] = []

    for py_file in apps_rg_path.rglob("*.py"):
        if "tests" in py_file.parts or "_test" in py_file.name:
            continue
        if "__pycache__" in py_file.parts:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError) as e:
            violations.append(f"{py_file}: parse error: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for q_path in QUARANTINE_PATHS:
                    if q_path in module:
                        violations.append(
                            f"{py_file}:{node.lineno}: live code imports quarantine: {module}"
                        )

    passed = len(violations) == 0
    return passed, violations


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for CI gate."""
    import argparse

    parser = argparse.ArgumentParser(
        description="quarantine inertness scanner"
    )
    parser.add_argument(
        "--quarantine-path",
        type=Path,
        help="Path to quarantine directory",
    )
    parser.add_argument(
        "--apps-rg-path",
        type=Path,
        help="Path to apps_rg directory",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args(argv)

    passed_inertness, violations_inertness = check_quarantine_inertness(
        args.quarantine_path
    )
    passed_imports, violations_imports = check_live_apps_rg_does_not_import_quarantine(
        args.apps_rg_path
    )

    all_violations = violations_inertness + violations_imports
    passed = passed_inertness and passed_imports

    if args.output_format == "json":
        import json
        result = {
            "passed": passed,
            "quarantine_inertness_passed": passed_inertness,
            "no_quarantine_imports_passed": passed_imports,
            "violations": all_violations,
            "scanner": "quarantine_inertness_scanner",
            "version": "W8.0",
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Quarantine Inertness Scanner W8.0")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print(f"Quarantine Inertness: {'PASS' if passed_inertness else 'FAIL'}")
        print(f"No Quarantine Imports: {'PASS' if passed_imports else 'FAIL'}")
        print(f"Violations: {len(all_violations)}")
        if all_violations:
            print("\nViolations:")
            for v in all_violations:
                print(f"  - {v}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
