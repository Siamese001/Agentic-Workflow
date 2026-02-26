"""CI guard G10: direct .execute() calls outside BaseRGEngine are forbidden.

Callers MUST use .execute_contracted() to ensure AgentOutputContract is emitted.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_PATHS = {
    "apps_rg/engines/base_rg_engine.py",
    "apps_lic/engines/base_lic_engine.py",  # if it exists
}
SCAN_ROOTS = ["apps_lic", "apps_rg", "apps_shared", "agentic_core"]


def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        for path in (REPO_ROOT / root).rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in ALLOWED_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "execute"
                ):
                    # Heuristic: receiver name ends with Engine/Agent
                    recv = ""
                    if isinstance(node.func.value, ast.Name):
                        recv = node.func.value.id
                    if any(kw in recv for kw in ("engine", "agent", "Engine", "Agent")):
                        violations.append(
                            f"{rel}:{node.lineno}: direct .execute() call on '{recv}' — use .execute_contracted()"
                        )
    if violations:
        print(f"FAIL: {len(violations)} direct .execute() call(s) found:")
        for v in violations:
            print(f"  {v}")
        return 1
    print("OK: no direct .execute() calls outside base")
    return 0


if __name__ == "__main__":
    sys.exit(main())
