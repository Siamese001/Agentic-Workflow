#!/usr/bin/env python3
"""W4 gate: assert compiled prompt/rubric constraint numbers == SECTION_CONSTRAINTS values.

Fail CI when any number stated in a judge rubric or template drifts from the SSOT.

Checks
------
1. X1D rubric module constants (rendered f-strings) — narrative word/char budgets.
2. YAML bullet templates — sc_paths and final_bullet_count fields.
3. PA source text scan — detect bare literals in narrative PA .py sources where
   a pattern matches but the found number does not equal the SSOT value.

Exit codes: 0 = all pass, 1 = one or more drift violations found.
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None  # type: ignore[assignment]

from apps_rg.runtime.sections.section_product_shape_ssot import SECTION_CONSTRAINTS

FAILURES: list[str] = []
CHECKS_RUN: int = 0


def fail(label: str, found: Any, expected: Any) -> None:
    FAILURES.append(f"DRIFT [{label}]: found {found!r}, expected {expected!r}")


def run_check() -> None:
    global CHECKS_RUN
    CHECKS_RUN += 1


# ─── 1. X1D rubric module constants ────────────────────────────────────────────

_WORD_BUDGET_RE = re.compile(r"max\s+(\d+)\s+words", re.I)
_CHAR_BUDGET_RE = re.compile(r"(\d+)\s+(?:chars|characters)", re.I)
# "no more than N words and N characters" form used in role_episode_x1d
_NO_MORE_THAN_RE = re.compile(r"no\s+more\s+than\s+(\d+)\s+words\s+and\s+(\d+)\s+characters", re.I)


def check_narrative_rubric(module_dotpath: str, rubric_attr: str, lane: str) -> None:
    """Import module, access rendered rubric string, verify word/char constraints."""
    run_check()
    c = SECTION_CONSTRAINTS[lane]
    try:
        mod = importlib.import_module(module_dotpath)
    except ImportError as exc:
        fail(f"{module_dotpath} import", str(exc), "importable")
        return

    rubric: str = getattr(mod, rubric_attr, "")
    if not rubric:
        fail(f"{module_dotpath}.{rubric_attr}", "missing or empty", "non-empty rubric string")
        return

    # "max N words" pattern
    for m in _WORD_BUDGET_RE.finditer(rubric):
        run_check()
        found = int(m.group(1))
        if found != c["max_words"]:
            fail(f"{module_dotpath}.{rubric_attr} max_words", found, c["max_words"])

    # "N characters" pattern (covers "max 58 words and 360 characters")
    for m in _CHAR_BUDGET_RE.finditer(rubric):
        run_check()
        found = int(m.group(1))
        if found != c["max_chars"]:
            fail(f"{module_dotpath}.{rubric_attr} max_chars", found, c["max_chars"])

    # "no more than N words and N characters" form
    for m in _NO_MORE_THAN_RE.finditer(rubric):
        run_check()
        found_words = int(m.group(1))
        found_chars = int(m.group(2))
        if found_words != c["max_words"]:
            fail(f"{module_dotpath}.{rubric_attr} no-more-than max_words", found_words, c["max_words"])
        if found_chars != c["max_chars"]:
            fail(f"{module_dotpath}.{rubric_attr} no-more-than max_chars", found_chars, c["max_chars"])


# ─── 2. YAML bullet template fields ────────────────────────────────────────────

def check_yaml_template(template_path: Path, lane: str) -> None:
    """Verify pool_selection.sc_paths and final_bullet_count in bullet YAML templates."""
    run_check()
    if yaml is None:
        fail(f"{template_path.name} yaml", "PyYAML not installed", "installed")
        return
    if not template_path.exists():
        fail(f"{template_path.name}", "file not found", "exists")
        return

    c = SECTION_CONSTRAINTS[lane]
    try:
        doc = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{template_path.name} yaml.safe_load", str(exc), "valid YAML")
        return

    pool_sel: dict[str, Any] = (
        (doc.get("rewrite_rules") or {}).get("pool_selection") or {}
    )

    if "sc_paths" in pool_sel:
        run_check()
        actual = pool_sel["sc_paths"]
        expected = c["sc_pool_paths"]
        if actual != expected:
            fail(f"{template_path.name} pool_selection.sc_paths", actual, expected)

    if "final_bullet_count" in pool_sel:
        run_check()
        actual = pool_sel["final_bullet_count"]
        expected = c["final_count"]
        if actual != expected:
            fail(f"{template_path.name} pool_selection.final_bullet_count", actual, expected)


# ─── 3. PA source text scan — bare literals that don't match SSOT ──────────────

# Patterns that, when found as bare literals in PA source, should equal the SSOT value.
_PA_SCAN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("max_words literal (max N words)", re.compile(r"max\s+(\d+)\s+words", re.I)),
    ("max_chars literal (max N chars/characters)", re.compile(r"max\s+(\d+)\s+(?:chars|characters)", re.I)),
    ("hard_max_words literal (hard max N words)", re.compile(r"hard\s+max\s+(\d+)\s+words", re.I)),
]

_PA_SOURCES = [
    "apps_rg/runtime/sections/unify_narrative_pa.py",
    "apps_rg/runtime/sections/ibm_narrative_pa.py",
    "apps_rg/runtime/sections/unify_narrative_lane.py",
    "apps_rg/runtime/sections/ibm_narrative_lane.py",
]

# All narrative lanes share the same max_words / max_chars values; use unify as reference.
_NARRATIVE_CONSTRAINT = SECTION_CONSTRAINTS["unify_narrative"]


def scan_pa_source_for_stale_literals(src: Path) -> None:
    """Find any bare constraint literal in src that doesn't match the SSOT value."""
    if not src.exists():
        return  # optional sources; skip gracefully
    text = src.read_text(encoding="utf-8")
    for desc, pattern in _PA_SCAN_PATTERNS:
        for m in pattern.finditer(text):
            found = int(m.group(1))
            # Determine expected value by pattern description
            if "max_words" in desc or "hard_max_words" in desc:
                expected = _NARRATIVE_CONSTRAINT["max_words"]
            else:
                expected = _NARRATIVE_CONSTRAINT["max_chars"]
            run_check()
            if found != expected:
                # A literal that doesn't match SSOT is an active drift violation.
                fail(f"{src.name} {desc}", found, expected)


# ─── main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    templates = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates"

    # 1. X1D rubric module constants
    check_narrative_rubric(
        "apps_rg.runtime.judges.unify_narrative_x1d",
        "NARRATIVE_RUBRIC",
        "unify_narrative",
    )
    check_narrative_rubric(
        "apps_rg.runtime.judges.ibm_narrative_x1d",
        "NARRATIVE_RUBRIC",
        "ibm_narrative",
    )
    # role_episode covers insurtech/ey — same max_words/max_chars as unify_narrative
    check_narrative_rubric(
        "apps_rg.runtime.judges.role_episode_x1d",
        "ROLE_EPISODE_RUBRIC",
        "insurtech_narrative",
    )

    # 2. YAML bullet template fields
    check_yaml_template(templates / "unify_bullet_tailor_v1.yaml", "unify_bullets")
    check_yaml_template(templates / "ibm_bullet_tailor_v1.yaml", "ibm_bullets")

    # 3. PA source scan for bare literals that don't match SSOT
    for rel in _PA_SOURCES:
        scan_pa_source_for_stale_literals(REPO_ROOT / rel)

    if FAILURES:
        print(f"FAIL: {len(FAILURES)} numeric parity violation(s) (ran {CHECKS_RUN} checks):")
        for msg in FAILURES:
            print(f"  {msg}")
        return 1

    print(
        f"PASS: all {CHECKS_RUN} numeric parity checks match SSOT "
        f"(3 rubric modules, 2 YAML templates, {len(_PA_SOURCES)} PA source scans)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
