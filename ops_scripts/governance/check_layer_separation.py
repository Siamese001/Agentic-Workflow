"""
check_layer_separation.py - Enforce 3-Layer Architecture Constraints.

Validates that the Sovereign Root (Layer 0) does not import:
1. Canon Domains (Layer 1 Validation)
2. Concrete Implementations (L6 Observability, L2 Tools)

This prevents the 'God Object' Anti-Pattern.
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

TARGET_FILE = Path("agentic_core/base_agents/SovereignBaseAgent.py")
FORBIDDEN_IMPORTS = [
    "CanonBaseAgent",
    "SovereignObservabilityAgent",
    "NamingAgent",
    "StructuralEngineerAgent",
    "agentic_core.canon",
    "agentic_core.L6_observability",
    "archives.void_violations",
]


def check_imports(file_path: Path) -> list[str]:
    if not file_path.exists():
        return [f"CRITICAL: Target file {file_path} not found."]
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"Syntax Error in {file_path}: {e}"]
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in FORBIDDEN_IMPORTS:
                    if forbidden in alias.name:
                        violations.append(f"Line {node.lineno}: Forbidden import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in FORBIDDEN_IMPORTS:
                if forbidden in module:
                    violations.append(f"Line {node.lineno}: Forbidden import source '{module}'")
            for alias in node.names:
                for forbidden in FORBIDDEN_IMPORTS:
                    if forbidden in alias.name:
                        violations.append(
                            f"Line {node.lineno}: Forbidden import '{alias.name}' from '{module}'"
                        )
    return violations


def main():
    print(f"Checking Layer Separation for: {TARGET_FILE}")
    violations = check_imports(TARGET_FILE)
    if violations:
        print("\n[!] ARCHITECTURE VIOLATION DETECTED")
        print("    SovereignBaseAgent must NOT depend on downstream layers.")
        print("-" * 50)
        for v in violations:
            print(f"    - {v}")
        print("-" * 50)
        sys.exit(1)
    print("[OK] Layer Separation Verified. SovereignBaseAgent is pure.")
    sys.exit(0)


if __name__ == "__main__":
    main()
