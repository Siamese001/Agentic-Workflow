#!/usr/bin/env python3
"""
pre_user_prompt_reminder_check.py — scan .cursor/reminders/ for due items.

Runs on every user prompt. Parses YAML frontmatter `due_date: YYYY-MM-DD` from
each `.cursor/reminders/*.md` file. If today >= due_date, prints a one-line
reminder to stderr so Cursor Agent sees it in the session context.

Silent when:
- No reminders directory exists
- All reminders are future-dated
- Frontmatter malformed (per-file fail-open)

Move resolved reminders to .cursor/reminders/archived/ to stop surfacing.

Fail policy: OPEN — any error → exit 0 silently.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REMINDERS_DIR = REPO_ROOT / "docs" / "archive" / "cursor" / "reminders"

DUE_DATE_RE = re.compile(
    r"^due_date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE
)
PRIORITY_RE = re.compile(
    r"^priority:\s*(high|medium|low)\s*$", re.MULTILINE | re.IGNORECASE
)


def _iter_reminders() -> list[tuple[Path, date, str]]:
    if not REMINDERS_DIR.is_dir():
        return []
    hits: list[tuple[Path, date, str]] = []
    today = date.today()
    for path in REMINDERS_DIR.glob("*.md"):
        try:
            # Only read the frontmatter — first ~500 chars is enough
            head = path.read_text(encoding="utf-8", errors="replace")[:500]
        except OSError:
            continue
        m = DUE_DATE_RE.search(head)
        if not m:
            continue
        try:
            due = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if today < due:
            continue
        pm = PRIORITY_RE.search(head)
        priority = pm.group(1).lower() if pm else "medium"
        hits.append((path, due, priority))
    # Sort overdue-first, then priority
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    hits.sort(key=lambda t: (t[1], priority_rank.get(t[2], 1)))
    return hits


def main() -> int:
    try:
        reminders = _iter_reminders()
    except (OSError, ValueError):
        return 0
    if not reminders:
        return 0
    today = date.today()
    for path, due, priority in reminders:
        days_overdue = (today - due).days
        tag = "DUE TODAY" if days_overdue == 0 else f"OVERDUE {days_overdue}d"
        rel = path.relative_to(REPO_ROOT).as_posix()
        print(
            f"[REMINDER {tag}, priority={priority}] {due.isoformat()}: {rel}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[reminder_check] fail-open: {exc}", file=sys.stderr)
        sys.exit(0)
