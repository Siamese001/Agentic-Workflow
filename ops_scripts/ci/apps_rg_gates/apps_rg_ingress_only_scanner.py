"""apps_rg Ingress-Only Scanner — AG-RGGOV-W8 CI Gate

Static scanner verifying apps_rg contains only ingress, profiles, fixtures,
docs, tests, and inert helpers.

FORBIDDEN in live apps_rg:
- planners, routers, orchestrators, executors
- agents, judges
- gateways, providers
- prompt assemblers
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


# Forbidden runtime components in apps_rg
FORBIDDEN_COMPONENTS: tuple[str, ...] = (
    # Core runtime authority
    "planner", "planners",
    "router", "routers",
    "orchestrator", "orchestrators",
    "executor", "executors",
    "agent", "agents",
    "judge", "judges",
    "gateway", "gateways",
    "provider", "providers",
    "prompt_assembler", "prompt_assemblers",
    # L3/L4/L5 components
    "workflow", "workflows",
    "coordinator", "coordinators",
    "scheduler", "schedulers",
    # Provider integrations
    "openai", "anthropic", "google.generativeai",
    "vllm", "qwen",
)

# Allowed patterns (inert helpers, not runtime authority)
ALLOWED_PATTERNS: tuple[str, ...] = (
    # Documentation
    "README", "RUNBOOK", "SLO", "AGENTIC_SPINE", "PROMPT_BOUNDARY_CONTRACT",
    # Configuration
    "config", "yaml", "json",
    # Profile handling (ingress-only)
    "profile", "profiles",
    # Test fixtures
    "fixture", "fixtures",
    # Inert helpers
    "utils", "helpers", "format",
)

# Allowed directories in apps_rg
ALLOWED_DIRS: tuple[str, ...] = (
    "L1_cognition",  # Only profile planning, not runtime planning
    "cache",
    "cert",
    "airlocks",
    "config",
    "scripts",  # Ops scripts only
    "tests",
    "fixtures",
)


def scan_apps_rg_for_forbidden_components(
    apps_rg_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Scan apps_rg for forbidden runtime components.

    Args:
        apps_rg_path: Path to apps_rg directory (default: repo-root/apps_rg)

    Returns:
        Tuple of (passed, violations)
    """
    if apps_rg_path is None:
        apps_rg_path = Path(__file__).parent.parent.parent.parent.parent / "apps_rg"

    violations: list[str] = []

    for py_file in apps_rg_path.rglob("*.py"):
        # Skip tests directory (tests are allowed to reference runtime)
        if "tests" in py_file.parts or "_test" in py_file.name:
            continue

        # Skip __pycache__
        if "__pycache__" in py_file.parts:
            continue

        # Skip quarantine directories (quarantined code is allowed to have forbidden patterns)
        if "_quarantine" in py_file.parts or "quarantine" in py_file.parts:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError) as e:
            violations.append(f"{py_file}: parse error: {e}")
            continue

        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    for forbidden in FORBIDDEN_COMPONENTS:
                        if forbidden in name.lower():
                            violations.append(
                                f"{py_file}:{node.lineno}: forbidden import: {name}"
                            )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for forbidden in FORBIDDEN_COMPONENTS:
                    if forbidden in module.lower():
                        # Exception: agentic_core is the core runtime, not an apps_rg agent
                        if forbidden == "agent" and "agentic_core" in module.lower():
                            continue
                        # Exception: AppIngressRunner import is allowed (canonical entry point)
                        if "app_ingress_runner" in module.lower():
                            continue
                        violations.append(
                            f"{py_file}:{node.lineno}: forbidden import from: {module}"
                        )

        # Check class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()
                for forbidden in FORBIDDEN_COMPONENTS:
                    if forbidden in class_name:
                        # Check if it's an allowed pattern
                        allowed = any(a.lower() in class_name for a in ALLOWED_PATTERNS)
                        if not allowed:
                            violations.append(
                                f"{py_file}:{node.lineno}: forbidden class: {node.name}"
                            )

        # Check function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name.lower()
                for forbidden in FORBIDDEN_COMPONENTS:
                    if forbidden in func_name:
                        allowed = any(a.lower() in func_name for a in ALLOWED_PATTERNS)
                        if not allowed:
                            violations.append(
                                f"{py_file}:{node.lineno}: forbidden function: {node.name}"
                            )

    passed = len(violations) == 0
    return passed, violations


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for CI gate."""
    import argparse

    parser = argparse.ArgumentParser(
        description="apps_rg ingress-only static scanner"
    )
    parser.add_argument(
        "--apps-rg-path",
        type=Path,
        help="Path to apps_rg directory",
    )
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        default=True,
        help="Exit with non-zero code if violations found",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args(argv)

    passed, violations = scan_apps_rg_for_forbidden_components(args.apps_rg_path)

    if args.output_format == "json":
        import json
        result = {
            "passed": passed,
            "violations": violations,
            "scanner": "apps_rg_ingress_only_scanner",
            "version": "W8.0",
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"apps_rg Ingress-Only Scanner W8.0")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print(f"Violations: {len(violations)}")
        if violations:
            print("\nViolations:")
            for v in violations:
                print(f"  - {v}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
