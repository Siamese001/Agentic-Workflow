#!/usr/bin/env python3
"""GOV-SAR: agentic_core/L2_execution/regen must remain app-agnostic."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGEN_DIR = REPO_ROOT / "agentic_core" / "L2_execution" / "regen"

FORBIDDEN_IMPORT = re.compile(r"^\s*(?:from|import)\s+apps_", re.MULTILINE)
FORBIDDEN_IN_STRINGS = re.compile(
    r"(apps_rg|executive_summary|GRAPH_ONLY_GRADE_ONLY_RUBRIC|"
    r"x2_exec_summary_|Brown & Brown|resume_display_text)",
    re.IGNORECASE,
)
_STRING_LITERAL = re.compile(r"""['"]([^'"]{3,})['"]""")


def scan_regen_boundary() -> list[str]:
    violations: list[str] = []
    if not REGEN_DIR.is_dir():
        return [f"missing regen package: {REGEN_DIR}"]

    for path in sorted(REGEN_DIR.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN_IMPORT.search(text):
            violations.append(f"{rel}: imports apps_* package")
        for i, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("#"):
                continue
            for match in _STRING_LITERAL.finditer(line):
                if FORBIDDEN_IN_STRINGS.search(match.group(1)):
                    violations.append(
                        f"{rel}:{i}: forbidden app literal in string",
                    )
    return violations


def test_regen_package_importable() -> None:
    from agentic_core.L2_execution.regen import SameAuthorityRegenRunner

    assert SameAuthorityRegenRunner is not None


def main() -> int:
    violations = scan_regen_boundary()
    if violations:
        print("FAIL — same-authority regen boundary violations:")
        for v in violations:
            print(f"  {v}")
        return 2
    print("PASS — agentic_core/L2_execution/regen has no apps_* leakage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
