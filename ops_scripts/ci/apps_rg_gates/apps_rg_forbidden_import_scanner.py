"""apps_rg Forbidden Import Scanner — AG-RGGOV-W8 CI Gate

Static scanner verifying apps_rg does not import forbidden providers,
gateways, or runtime authority symbols.

FORBIDDEN imports in live apps_rg:
- openai
- anthropic
- google.generativeai
- vllm, qwen direct client
- get_llm_gateway
- SovereignLLMGateway
- lifecycle_trace_contract
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


# Forbidden imports — absolute ban
FORBIDDEN_MODULES: tuple[str, ...] = (
    # Provider SDKs
    "openai",
    "anthropic",
    "google.generativeai",
    "vllm",
    "qwen",
    # Runtime authority
    "get_llm_gateway",
    "SovereignLLMGateway",
    "lifecycle_trace_contract",
    # Specific agentic_core paths
    "agentic_core.L1_cognition",  # Runtime planners
    "agentic_core.L0_routing",  # Runtime routers
    "agentic_core.L3_orchestration",  # Runtime orchestrators
    "agentic_core.L2_execution",  # Runtime executors (except via public API)
    "agentic_core.L5_safety",  # L5 authority (except RequestEnvelope)
    "agentic_core.L6_observability",  # L6 (except span emission)
)

# Allowed imports from agentic_core
ALLOWED_AGENTIC_CORE_IMPORTS: tuple[str, ...] = (
    # Contracts only
    "agentic_core.runtime.contracts",
    "agentic_core.runtime.entrypoints.AppIngressRunner",
    # L7 audit (read-only)
    "agentic_core.runtime.audit",
)

# Explicitly allowed symbols (exceptions to the rules)
ALLOWED_SYMBOLS: tuple[str, ...] = (
    "RequestEnvelope",  # From L5 authority
    "L7RuntimeAuditTrace",  # From L7 (read-only audit)
)


def scan_apps_rg_for_forbidden_imports(
    apps_rg_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Scan apps_rg for forbidden imports.

    Args:
        apps_rg_path: Path to apps_rg directory

    Returns:
        Tuple of (passed, violations)
    """
    if apps_rg_path is None:
        apps_rg_path = Path(__file__).parent.parent.parent.parent.parent / "apps_rg"

    violations: list[str] = []

    for py_file in apps_rg_path.rglob("*.py"):
        # Skip tests
        if "tests" in py_file.parts or "_test" in py_file.name:
            continue
        if "__pycache__" in py_file.parts:
            continue
        # Skip quarantine directories
        if "_quarantine" in py_file.parts or "quarantine" in py_file.parts:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError) as e:
            violations.append(f"{py_file}: parse error: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    for forbidden in FORBIDDEN_MODULES:
                        if name == forbidden or name.startswith(forbidden + "."):
                            # Check if in allowed exceptions
                            if name not in ALLOWED_SYMBOLS:
                                violations.append(
                                    f"{py_file}:{node.lineno}: forbidden import: {name}"
                                )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Check if the module itself is forbidden
                for forbidden in FORBIDDEN_MODULES:
                    if module == forbidden or module.startswith(forbidden + "."):
                        # Check allowed exceptions
                        is_allowed = False
                        for allowed in ALLOWED_AGENTIC_CORE_IMPORTS:
                            if module.startswith(allowed):
                                is_allowed = True
                                break
                        # Check if importing allowed symbols only
                        if is_allowed:
                            imported_names = [a.name for a in node.names]
                            if all(n in ALLOWED_SYMBOLS for n in imported_names):
                                continue

                        if not is_allowed:
                            violations.append(
                                f"{py_file}:{node.lineno}: forbidden import from: {module}"
                            )

    passed = len(violations) == 0
    return passed, violations


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for CI gate."""
    import argparse

    parser = argparse.ArgumentParser(
        description="apps_rg forbidden import scanner"
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

    passed, violations = scan_apps_rg_for_forbidden_imports(args.apps_rg_path)

    if args.output_format == "json":
        import json
        result = {
            "passed": passed,
            "violations": violations,
            "scanner": "apps_rg_forbidden_import_scanner",
            "version": "W8.0",
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"apps_rg Forbidden Import Scanner W8.0")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print(f"Violations: {len(violations)}")
        if violations:
            print("\nViolations:")
            for v in violations:
                print(f"  - {v}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
