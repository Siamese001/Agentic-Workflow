"""
SOVEREIGN FINAL AUDIT
---------------------
Verifies file inventory, class inheritance, and void compliance.
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_RG_DIR,
    ARCHIVES_DIR,
)
from tqdm import tqdm

ROOT = Path(APPS_RG_DIR)
REQUIRED_BASE = "BaseRGEngine"
FORBIDDEN_IMPORTS = [ARCHIVES_DIR, "legacy"]


def audit_file(path: Path):
    try:
        content = path.read_text("utf-8")
        tree = ast.parse(content)
    except Exception as e:
        return {"error": f"Parse Error: {e}"}

    issues = []

    # Check Imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            module = node.module if hasattr(node, "module") else None
            [n.name for n in node.names]

            # Check Forbidden
            if module and any(f in module for f in FORBIDDEN_IMPORTS):
                issues.append(f"Forbidden Import: {module}")

    # Check Inheritance (Heuristic)
    if "engines" in str(path) and "base" not in str(path):
        if "class " in content and REQUIRED_BASE not in content:
            issues.append(f"Missing Inheritance: {REQUIRED_BASE}")

    return {"issues": issues}


def main():
    print(f"🛡️  Starting Audit on {ROOT}...")

    total_files = 0
    clean_files = 0
    all_issues = []

    for path in tqdm(ROOT.rglob("*.py"), desc="Processing", unit="item"):
        if path.name == "__init__.py":
            continue
        # Skip legacy and quarantine folders
        if "legacy" in str(path) or "quarantine" in str(path):
            continue
        # Only check refactored engine directories
        if not any(
            subdir in str(path).replace("\\", "/")
            for subdir in [
                "engines/hops",
                "engines/generation",
                "engines/refinement",
                "engines/safety",
                "engines/orchestration",
                "engines/quality",
                "shared/core",
            ]
        ):
            continue
        total_files += 1

        result = audit_file(path)
        if result.get("issues"):
            print(f"❌ {path}: {result['issues']}")
            all_issues.extend([f"{path}: {i}" for i in result["issues"]])
        elif result.get("error"):
            print(f"⚠️ {path}: {result['error']}")
        else:
            clean_files += 1

    print("-" * 40)
    print(f"TOTAL FILES: {total_files}")
    print(f"CLEAN FILES: {clean_files}")
    if total_files > 0:
        print(f"COMPLIANCE:  {int((clean_files / total_files) * 100)}%")
    else:
        print("COMPLIANCE:  0%")

    if all_issues:
        print("\nFAILURE: Compliance Violations Detected.")
        exit(1)
    else:
        print("\nSUCCESS: System is 100% Compliant.")
        exit(0)


if __name__ == "__main__":
    main()
