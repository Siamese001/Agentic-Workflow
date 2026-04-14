"""
Enforce layer-separation constraints for a target Python file.

Validates that the Sovereign Root does not import forbidden downstream
modules or symbols that would violate architecture boundaries.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from tqdm import tqdm


DEFAULT_TARGET = Path("agentic_core/base_agents/SovereignBaseAgent.py")
FORBIDDEN_IMPORTS = (
    "CanonBaseAgent",
    "SovereignObservabilityAgent",
    "NamingAgent",
    "StructuralEngineerAgent",
    "agentic_core.canon",
    "agentic_core.L6_observability",
    "archives.void_violations",
)


def _matches_forbidden(candidate: str, forbidden: str) -> bool:
    return candidate == forbidden or candidate.startswith(f"{forbidden}.")


def check_imports(file_path: Path) -> list[str]:
    if not file_path.exists():
        return [f"CRITICAL: target file not found: {file_path}"]

    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"CRITICAL: could not read {file_path}: {exc}"]

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return [f"Syntax error in {file_path}: line {exc.lineno}: {exc.msg}"]

    violations: list[str] = []
    for node in tqdm(list(ast.walk(tree)), desc="Checking imports", unit="node", leave=False):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in FORBIDDEN_IMPORTS:
                    if _matches_forbidden(alias.name, forbidden):
                        violations.append(f"Line {node.lineno}: forbidden import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in FORBIDDEN_IMPORTS:
                if _matches_forbidden(module, forbidden):
                    violations.append(f"Line {node.lineno}: forbidden import source '{module}'")
            for alias in node.names:
                full_name = f"{module}.{alias.name}" if module else alias.name
                for forbidden in FORBIDDEN_IMPORTS:
                    if _matches_forbidden(alias.name, forbidden) or _matches_forbidden(full_name, forbidden):
                        violations.append(
                            f"Line {node.lineno}: forbidden import '{alias.name}' from '{module}'"
                        )
    return violations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Python file to validate for forbidden imports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = args.target.resolve()

    print(f"Checking layer separation for: {target}")
    violations = check_imports(target)
    if violations:
        print("\n[FAILED] Architecture violation detected")
        print("SovereignBaseAgent must not depend on downstream layers.")
        print("-" * 72)
        for violation in violations:
            print(f"  - {violation}")
        print("-" * 72)
        return 1

    print("[PASSED] Layer separation verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
