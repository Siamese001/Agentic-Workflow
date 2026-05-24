#!/usr/bin/env python3
"""GOV-JPH: agentic_core/runtime/judges/panel must remain app-agnostic."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PANEL_DIR = REPO_ROOT / "agentic_core" / "runtime" / "judges" / "panel"

FORBIDDEN_IMPORT = re.compile(r"^\s*(?:from|import)\s+apps_", re.MULTILINE)
FORBIDDEN_LITERAL = re.compile(r"""["']apps_(?:rg|lic|qna|research|architect)["']""")


def scan_panel_boundary() -> list[str]:
    violations: list[str] = []
    if not PANEL_DIR.is_dir():
        return [f"missing panel package: {PANEL_DIR}"]

    for path in sorted(PANEL_DIR.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN_IMPORT.search(text):
            violations.append(f"{rel}: imports apps_* package")
        for i, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("#"):
                continue
            if FORBIDDEN_LITERAL.search(line):
                violations.append(f"{rel}:{i}: apps_* literal in code")
    return violations


def test_panel_package_importable() -> None:
    from agentic_core.runtime.judges.panel import JudgePanelRunner

    assert JudgePanelRunner is not None


def main() -> int:
    violations = scan_panel_boundary()
    if violations:
        print("FAIL — judge panel harness boundary violations:")
        for v in violations:
            print(f"  {v}")
        return 2
    print("PASS — agentic_core/runtime/judges/panel has no apps_* leakage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
