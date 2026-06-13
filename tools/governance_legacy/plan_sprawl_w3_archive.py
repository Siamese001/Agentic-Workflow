#!/usr/bin/env python3
"""W3 plan sprawl inventory + archive for governance-dedup-closeout-e8a4c2."""
from __future__ import annotations

import csv
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / ".claude" / "plans"
ARCHIVE_DIR = PLANS / "_archive" / "2026-05"
CSV_OUT = REPO / "docs/reports/cursor/plan_sprawl_inventory_20260526.csv"

ARCHIVE_STATUSES = frozenset(
    {
        "completed",
        "complete",
        "done",
        "superseded",
        "retired",
        "archived",
        "closed",
        "cancelled",
        "canceled",
    }
)
ACTIVE_STATUSES = frozenset(
    {
        "todo",
        "in progress",
        "in_progress",
        "not started",
        "waiting",
        "lower priority",
        "blocked",
        "active",
    }
)
KEEP_TOP_LEVEL = frozenset({"README.md", "CURSOR_RUNTIME_SEAM_TEMPLATE.md"})
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-[0-9a-f]{6}\.md$", re.I)


def _parse_status(text: str) -> tuple[str, str]:
    status = ""
    wave = ""
    for line in text.splitlines()[:120]:
        if line.startswith("PLAN_STATUS:"):
            status = line.split(":", 1)[1].strip()
        elif line.startswith("CURRENT_WAVE:"):
            wave = line.split(":", 1)[1].strip()
        elif not status and line.startswith("**Status:**"):
            status = line.split(":", 1)[1].strip()
    return status, wave


def classify(name: str, status: str, text: str) -> str:
    if name in KEEP_TOP_LEVEL:
        return "KEEP"
    norm = status.lower().replace("_", " ")
    if norm in ACTIVE_STATUSES:
        return "ACTIVE"
    if norm in ARCHIVE_STATUSES:
        return "ARCHIVE"
    if re.search(r"PLAN_STATUS:\s*(COMPLETED?|DONE|SUPERSEDED)\b", text, re.I):
        return "ARCHIVE"
    if re.search(r"\*\*Status:\*\*\s*(Completed|Complete|Done)\b", text, re.I):
        return "ARCHIVE"
    if SLUG_RE.match(name) and not status:
        return "ARCHIVE"
    return "REVIEW"


def main() -> int:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    moved: list[str] = []

    for path in sorted(PLANS.iterdir()):
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        status, wave = _parse_status(text)
        disposition = classify(path.name, status, text)
        rows.append(
            {
                "filename": path.name,
                "plan_status": status,
                "current_wave": wave,
                "disposition": disposition,
                "is_slug_plan": "yes" if SLUG_RE.match(path.name) else "no",
            }
        )
        if disposition == "ARCHIVE":
            dest = ARCHIVE_DIR / path.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(path), str(dest))
            moved.append(path.name)

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["filename", "plan_status", "current_wave", "disposition", "is_slug_plan"],
        )
        writer.writeheader()
        writer.writerows(rows)

    remaining = [p.name for p in PLANS.iterdir() if p.is_file()]
    print(
        {
            "ok": True,
            "archived_count": len(moved),
            "remaining_top_level_count": len(remaining),
            "remaining": sorted(remaining),
            "csv": str(CSV_OUT.relative_to(REPO)).replace("\\", "/"),
            "archive_dir": str(ARCHIVE_DIR.relative_to(REPO)).replace("\\", "/"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return 0 if len(remaining) <= 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
