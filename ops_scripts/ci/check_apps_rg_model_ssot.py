#!/usr/bin/env python3
"""CI gate: apps_rg generator model IDs have one SSOT.

The generator model is defined in ``apps_rg/config/provider_profiles.yaml``
(``external_claude_generator.default_model`` plus ``model_by_section``) and
resolved by
``apps_rg.runtime.section_model_limits.resolve_section_generation_model``.

This gate forbids hardcoded ``claude-*`` generator-model ID literals in
apps_rg generation paths so provider profile intent cannot be silently
overridden. Scope: ``apps_rg/runtime/sections``, ``apps_rg/l2_recipe``,
``apps_rg/prompt_assembly``, and ``apps_rg/runtime/providers``.

Exempt: ``section_model_limits.py`` (the sanctioned resolver fallback),
``judges/**`` (judge model tiers have a separate SSOT), and tests. Comment
lines are skipped.

Exit 1 on violation. Bypass: ``APPS_RG_MODEL_SSOT_GATE_BYPASS=1``.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCAN_DIRS = (
    REPO / "apps_rg" / "runtime" / "sections",
    REPO / "apps_rg" / "l2_recipe",
    REPO / "apps_rg" / "prompt_assembly",
    REPO / "apps_rg" / "runtime" / "providers",
)
EXEMPT_FILES = {REPO / "apps_rg" / "runtime" / "section_model_limits.py"}
_MODEL_LITERAL = re.compile(r"""['"]claude-(?:haiku|sonnet|opus)-[0-9][0-9a-z.\-]*['"]""")


def _is_exempt(path: Path) -> bool:
    if path in EXEMPT_FILES:
        return True
    parts = path.parts
    if "judges" in parts:
        return True
    return path.name.startswith("test_") or "tests" in parts


def scan() -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for py_file in sorted(scan_dir.rglob("*.py")):
            if _is_exempt(py_file):
                continue
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if line.strip().startswith("#"):
                    continue
                if _MODEL_LITERAL.search(line):
                    hits.append((py_file.relative_to(REPO).as_posix(), line_no, line.strip()[:120]))
    return hits


def main() -> int:
    if os.environ.get("APPS_RG_MODEL_SSOT_GATE_BYPASS") == "1":
        print("[apps_rg-model-ssot] BYPASS=1 - skipping")
        return 0

    hits = scan()
    if not hits:
        print("[apps_rg-model-ssot] PASS - no hardcoded claude-* generator-model literals in apps_rg generation paths")
        return 0

    print(
        "[apps_rg-model-ssot] FAIL - hardcoded generator-model literal(s) found. Use "
        "section_model_limits.resolve_section_generation_model(section_id); the SSOT is "
        "apps_rg/config/provider_profiles.yaml (external_claude_generator):"
    )
    for file_name, line_no, text in hits:
        print(f"  {file_name}:{line_no}: {text}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
