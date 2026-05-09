"""apps_rg Forbidden Contract Emission Scanner — AG-RGGOV-W8 CI Gate

Static scanner verifying apps_rg does not define, import for emission,
or instantiate forbidden runtime contracts.

FORBIDDEN in apps_rg:
- L1PlanContract definition or instantiation
- RouteContract definition or instantiation
- FinalEvidenceContract definition or instantiation
- CompiledPromptArtifact definition or instantiation
- SealedL2Artifact definition or instantiation
- X3Disposition definition or instantiation
- GateVerdict definition or instantiation
- CommitRequest definition or instantiation
- LearningProposal definition or instantiation
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Sequence


# Forbidden contracts — apps_rg must not emit these
FORBIDDEN_CONTRACTS: tuple[str, ...] = (
    # Core runtime contracts (only core may emit)
    "L1PlanContract",
    "RouteContract",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "SealedL2Artifact",
    "SealedL2Artifact_v1",
    "X3Disposition",
    "X3Disposition_v1",
    # Control/learning contracts
    "GateVerdict",
    "CommitRequest",
    "LearningProposal",
    # Internal runtime types
    "ValidatedRequest",  # Only U0 creates this
    "AuthorityValidationReceipt",  # Only U0 creates this
)

# Allowed: apps_rg may reference these for type hints only
# (must not instantiate)
ALLOWED_TYPE_HINTS: tuple[str, ...] = (
    # Ingress contracts
    "AppsRgIngressPayload",
    "AppsRgProfileManifest",
    "RequestEnvelope",
    # L7 audit (read-only observation)
    "L7RuntimeAuditTrace",
)


def scan_apps_rg_for_forbidden_contracts(
    apps_rg_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Scan apps_rg for forbidden contract definitions or instantiation.

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
            # Check class definitions (contract definitions)
            if isinstance(node, ast.ClassDef):
                if node.name in FORBIDDEN_CONTRACTS:
                    violations.append(
                        f"{py_file}:{node.lineno}: forbidden contract definition: {node.name}"
                    )

            # Check function calls (contract instantiation)
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    if func.id in FORBIDDEN_CONTRACTS:
                        violations.append(
                            f"{py_file}:{node.lineno}: forbidden contract instantiation: {func.id}"
                        )
                elif isinstance(func, ast.Attribute):
                    if func.attr in FORBIDDEN_CONTRACTS:
                        violations.append(
                            f"{py_file}:{node.lineno}: forbidden contract instantiation: {func.attr}"
                        )

            # Check imports
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in FORBIDDEN_CONTRACTS:
                        # Check if it's just a type hint import
                        # (we still flag it for review)
                        violations.append(
                            f"{py_file}:{node.lineno}: forbidden contract import: {alias.name}"
                        )

    passed = len(violations) == 0
    return passed, violations


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for CI gate."""
    import argparse

    parser = argparse.ArgumentParser(
        description="apps_rg forbidden contract emission scanner"
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

    passed, violations = scan_apps_rg_for_forbidden_contracts(args.apps_rg_path)

    if args.output_format == "json":
        import json
        result = {
            "passed": passed,
            "violations": violations,
            "scanner": "apps_rg_forbidden_contract_scanner",
            "version": "W8.0",
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"apps_rg Forbidden Contract Scanner W8.0")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print(f"Violations: {len(violations)}")
        if violations:
            print("\nViolations:")
            for v in violations:
                print(f"  - {v}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
