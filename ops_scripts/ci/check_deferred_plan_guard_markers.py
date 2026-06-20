#!/usr/bin/env python3
"""
check_deferred_plan_guard_markers.py — CI gate: deferred-scope plan guard parity.

Every .codex/plans/*.md file that contains "do not implement without"
prose MUST also contain a matching DO_NOT_IMPLEMENT_GUARD: marker line.

The marker is machine-readable and picked up by
pre_user_prompt_deferred_plan_gate.py at the start of every Codex turn,
making the execution block visible to the model rather than relying on prose
Codex can silently bypass.

Root-cause closed: RCA 2026-05-10 — notion-test-hardening-deferred-scope-a7b4c9
executed without Author-Gate because prose guard was invisible to hook chain.

CLI::

    python ops_scripts/ci/check_deferred_plan_guard_markers.py            # all plans
    python ops_scripts/ci/check_deferred_plan_guard_markers.py PATH...    # specific files

Exit codes:
    0 — all plans compliant (or no plans present)
    1 — at least one plan has prose guard but missing DO_NOT_IMPLEMENT_GUARD: marker

Bypass: DEFERRED_PLAN_GUARD_BYPASS=1.
Constitutional tie-in: §6 (Author-Gate), §35 (queue drain).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".codex" / "plans"

# Machine-readable guard marker
_MARKER_RE = re.compile(r"^\s*DO_NOT_IMPLEMENT_GUARD\s*:", re.MULTILINE)

# Prose patterns that signal "do not implement without <gate>" intent
_PROSE_PATTERNS = (
    re.compile(r"nothing\s+here\s+should\s+be\s+implemented\s+without", re.IGNORECASE),
    re.compile(r"do\s+not\s+implement\s+without", re.IGNORECASE),
    re.compile(r"should\s+not\s+be\s+implemented\s+without", re.IGNORECASE),
    re.compile(r"must\s+not\s+be\s+implemented\s+without", re.IGNORECASE),
)

# Exclude quoted/code-block occurrences (heuristic: preceded by > or ` or ")
_QUOTE_PREFIX_RE = re.compile(r"""[>`"']""")


def _count_prose_guards(text: str) -> int:
    total = 0
    for pat in _PROSE_PATTERNS:
        for m in pat.finditer(text):
            start = m.start()
            before = text[max(0, start - 3):start]
            if _QUOTE_PREFIX_RE.search(before):
                continue
            total += 1
    return total


def _has_marker(text: str) -> bool:
    return bool(_MARKER_RE.search(text))


def _check_one(path: Path) -> tuple[bool, int, bool]:
    """Return (compliant, prose_count, has_marker)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return True, 0, False
    prose = _count_prose_guards(text)
    marker = _has_marker(text)
    # Compliant if either: no prose guard, or prose guard + marker present
    compliant = (prose == 0) or marker
    return compliant, prose, marker


def _all_plans() -> list[Path]:
    if not PLANS_DIR.exists():
        return []
    try:
        return sorted(
            p for p in PLANS_DIR.glob("*.md")
            if not p.name.startswith("_")
        )
    except OSError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deferred-scope plan guard marker parity."
    )
    parser.add_argument(
        "paths", nargs="*", type=Path,
        help="Plan files to check (default: all .codex/plans/*.md)"
    )
    args = parser.parse_args()

    if os.environ.get("DEFERRED_PLAN_GUARD_BYPASS") == "1":
        print("[deferred_plan_guard] BYPASS active — skipping.", file=sys.stderr)
        return 0

    plans = args.paths if args.paths else _all_plans()
    if not plans:
        return 0

    violations: list[tuple[Path, int]] = []
    for p in plans:
        p = Path(p)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists() or not str(p).endswith(".md"):
            continue
        ok, prose, marker = _check_one(p)
        if not ok:
            violations.append((p, prose))

    if not violations:
        return 0

    print(
        "[deferred_plan_guard] DEFERRED-SCOPE PLAN GUARD MARKER MISSING",
        file=sys.stderr,
    )
    for p, prose in violations:
        try:
            rel = p.relative_to(REPO_ROOT)
        except ValueError:
            rel = p
        print(
            f"  {rel}: {prose} prose guard mention(s) but no DO_NOT_IMPLEMENT_GUARD: marker",
            file=sys.stderr,
        )
    print(
        "\nRemediation: add a marker line to the plan file, e.g.:\n"
        "  DO_NOT_IMPLEMENT_GUARD: plan=<slug-6hex> reason=requires Author-Gate decision before execution\n\n"
        "This marker is picked up by pre_user_prompt_deferred_plan_gate.py at every\n"
        "Codex turn, making the block visible to the model.\n"
        "Bypass (rare): DEFERRED_PLAN_GUARD_BYPASS=1\n"
        "RCA: 2026-05-10 notion-test-hardening-deferred-scope-a7b4c9 executed without gate.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
