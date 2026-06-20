#!/usr/bin/env python3
"""
check_ag_queue_seed_markers.py — Pre-commit gate: plan-prose ↔ AG_QUEUE_SEED parity.

For each staged `.codex/plans/*.md` file, count:
  - Prose lines mentioning future Author-Gate decisions
    (patterns: "Author-Gate required for", "Author-Gate pending for",
               "Author-Gate needed for")
  - `AG_QUEUE_SEED:` markers

Rule: prose_count MUST be ≤ marker_count. If a plan names future
AG decisions in prose but has fewer markers, the gate fails with
remediation instructions.

CLI::

    python ops_scripts/ci/check_ag_queue_seed_markers.py            # all tracked plans
    python ops_scripts/ci/check_ag_queue_seed_markers.py PATH...    # specific files

Exit codes:
    0 — all plans compliant (or no plans changed)
    1 — at least one plan missing markers

Bypass: AG_QUEUE_SEED_MARKERS_BYPASS=1.

Constitutional tie-in: §35.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".codex" / "plans"
# Forward-only relocation (plan relocate-plans-ssot-outside-claude-c1a17d):
# canonical NEW plans live in repo-root plans/; .codex/plans/ stays legacy-valid.
PLAN_DIRS = [REPO_ROOT / "plans", PLANS_DIR]

# Prose patterns that signal a future Author-Gate decision in the plan text.
# Skip occurrences surrounded by quotes, backticks, or parentheses (examples).
_PROSE_PATTERNS = (
    re.compile(r"Author-Gate\s+required\s+for\b", re.IGNORECASE),
    re.compile(r"Author-Gate\s+pending\s+for\b", re.IGNORECASE),
    re.compile(r"Author-Gate\s+needed\s+for\b", re.IGNORECASE),
)

# Wrapper chars that indicate an example/quoted mention (not a real declaration).
_QUOTE_WRAP_RE = re.compile(r"""["'`]""")

# Marker pattern
_MARKER_RE = re.compile(r"^\s*AG_QUEUE_SEED\s*:", re.MULTILINE)


def _staged_plans() -> list[Path]:
    """Return staged plan files via git diff --cached."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
            cwd=REPO_ROOT,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    out = []
    for line in result.stdout.splitlines():
        p = line.strip()
        if not p:
            continue
        if (p.startswith("plans/") or p.startswith(".codex/plans/")) and p.endswith(".md"):
            full = REPO_ROOT / p
            if full.exists():
                out.append(full)
    return out


def _count_prose_hits(text: str) -> int:
    """Count prose mentions of future Author-Gate decisions.

    Excludes occurrences wrapped in quotes, backticks, or parentheses —
    those are example citations, not declarations of scheduled work.
    """
    total = 0
    for pat in _PROSE_PATTERNS:
        for m in pat.finditer(text):
            start, end = m.start(), m.end()
            # Inspect up to 2 characters before and after
            before = text[max(0, start - 2):start]
            after = text[end:end + 2]
            # Skip if wrapped in quotes/backticks or parenthesized
            if _QUOTE_WRAP_RE.search(before) or _QUOTE_WRAP_RE.search(after):
                continue
            if before.endswith("(") or after.startswith(")"):
                continue
            total += 1
    return total


def _count_markers(text: str) -> int:
    return len(_MARKER_RE.findall(text))


def _check_one(path: Path) -> tuple[bool, int, int]:
    """Return (compliant, prose_count, marker_count)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return True, 0, 0
    prose = _count_prose_hits(text)
    markers = _count_markers(text)
    return prose <= markers, prose, markers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path, help="Plan files to check (default: git-staged)")
    args = parser.parse_args()

    if os.environ.get("AG_QUEUE_SEED_MARKERS_BYPASS") == "1":
        print("[ag_queue_seed_markers] BYPASS active — skipping.", file=sys.stderr)
        return 0

    if args.paths:
        plans = [p if p.is_absolute() else REPO_ROOT / p for p in args.paths]
    else:
        plans = _staged_plans()

    if not plans:
        return 0

    violations: list[tuple[Path, int, int]] = []
    for p in plans:
        if not p.exists() or not str(p).endswith(".md"):
            continue
        ok, prose, markers = _check_one(p)
        if not ok:
            violations.append((p, prose, markers))

    if not violations:
        return 0

    print("[ag_queue_seed_markers] PLAN PROSE ↔ MARKER PARITY VIOLATION", file=sys.stderr)
    for p, prose, markers in violations:
        rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
        print(
            f"  {rel}: {prose} prose mention(s), {markers} AG_QUEUE_SEED marker(s) — "
            f"missing {prose - markers}",
            file=sys.stderr,
        )
    print(
        "\nRemediation: for every 'Author-Gate required for X' prose mention in the plan,\n"
        "add a matching marker line like:\n"
        "  AG_QUEUE_SEED: plan=<slug-6hex> id=<packet_id> depends_on=<id1,id2> title=<short>\n"
        "Constitutional §35; rule .codex/rules/author-gate-queue-drain.md.\n"
        "Bypass (rare): AG_QUEUE_SEED_MARKERS_BYPASS=1",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
