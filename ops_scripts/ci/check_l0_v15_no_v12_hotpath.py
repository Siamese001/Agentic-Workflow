#!/usr/bin/env python3
"""Fail if v12 hot-path modules are imported outside _archive and tests."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_FORBIDDEN = (
    (r"from\s+agentic_core\.L0_routing\.reasoning\.v12_route_selector\b", "v12_route_selector"),
    (r"from\s+agentic_core\.L0_routing\.reasoning\.cold_start_safeguard\b", "cold_start_safeguard"),
    (r"from\s+agentic_core\.L0_routing\.config\.fallback_chains_loader\b(?!_v15)", "fallback_chains_loader"),
    (r"import\s+agentic_core\.L0_routing\.reasoning\.v12_route_selector\b", "v12_route_selector"),
)
_ALLOWED_PARTS = ("_archive", "tests", "test_")


def _scan_file(path: Path) -> list[str]:
    rel = path.relative_to(_repo).as_posix()
    if any(part in rel for part in ("_archive/v12/", "/tests/", "\\tests\\")):
        return []
    if "/test_" in rel or rel.startswith("tests/"):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits: list[str] = []
    for pat, name in _FORBIDDEN:
        if re.search(pat, text):
            hits.append(f"{rel}: forbidden import {name}")
    return hits


def main() -> int:
    global _repo
    _repo = _REPO
    violations: list[str] = []
    for py in (_REPO / "agentic_core").rglob("*.py"):
        if ".venv" in py.parts:
            continue
        violations.extend(_scan_file(py))
    for apps in _REPO.glob("apps_*"):
        if apps.is_dir():
            for py in apps.rglob("*.py"):
                violations.extend(_scan_file(py))
    if violations:
        print("FAIL v12 hot-path imports outside archive/tests:")
        for v in sorted(set(violations))[:40]:
            print(f"  {v}")
        print(f"  total={len(violations)}")
        return 1
    print("OK no v12 hot-path imports in production tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
