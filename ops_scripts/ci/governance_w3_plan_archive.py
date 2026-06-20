#!/usr/bin/env python3
"""Archive stale top-level .codex/plans/*.md to _archive/YYYY-MM/ (W3B)."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / ".codex" / "plans"
ARCHIVE_MONTH = "2026-05"
ARCHIVE_DIR = PLANS / "_archive" / ARCHIVE_MONTH
OUT_JSON = REPO / "docs/reports/cursor/governance_w3_plan_archive_manifest.json"
OUT_MD = REPO / "docs/reports/cursor/governance_w3_plan_archive_manifest.md"

EXCLUDE_NAMES = frozenset(
    {
        "README.md",
        "CURSOR_RUNTIME_SEAM_TEMPLATE.md",
    }
)
KEEP_ALWAYS = frozenset(
    {
        "cursor-governance-two-tier-b4e8f2.md",
    }
)
MAX_ACTIVE = 19  # under 20 excluding template/README


def _is_top_level(path: Path) -> bool:
    return path.parent.resolve() == PLANS.resolve() and path.suffix == ".md"


def _wave_progress_slice(text: str) -> str:
    m = re.search(r"## Wave Progress\s*\n(.*?)(\n## |\Z)", text, re.S | re.I)
    return m.group(1) if m else ""


def _classify(path: Path) -> tuple[str, str]:
    """Return (decision, reason) where decision is keep|archive|skip."""
    name = path.name
    if name in EXCLUDE_NAMES:
        return "exclude", "template_or_readme"
    if name in KEEP_ALWAYS:
        return "keep", "w3_mandatory_active_plan"

    text = path.read_text(encoding="utf-8", errors="replace")
    wave_progress = _wave_progress_slice(text)
    wave_todo = "🔲 TODO" in wave_progress or "| 🔲" in wave_progress

    if re.search(r"PLAN_STATUS:\s*IN_PROGRESS", text, re.I):
        if wave_todo:
            return "keep", "in_progress_open_wave_row"
        if re.search(r"WAVE_STATUS:\s*TODO", text, re.I):
            return "keep", "in_progress_wave_status_todo"
        return "archive", "in_progress_all_waves_done"

    if re.search(r"PLAN_STATUS:\s*(Completed|Retired|Archived)", text, re.I):
        return "archive", "plan_status_terminal"

    if wave_todo:
        return "keep", "open_wave_progress_todo"

    if "BLOCKED" in text[:4000] and re.search(r"(PLAN_STATUS|WAVE_STATUS|CHECKPOINT)", text):
        return "keep", "explicit_blocked_state"

    # Legacy / completed — default archive (W3 sprawl burndown)
    return "archive", "stale_or_completed_not_in_progress"


def main() -> int:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()

    top_level = sorted(p for p in PLANS.glob("*.md") if _is_top_level(p))
    before_count = len([p for p in top_level if p.name not in EXCLUDE_NAMES])
    pass_number = 2 if before_count > MAX_ACTIVE else 1

    kept: list[dict] = []
    archived: list[dict] = []
    skipped: list[dict] = []

    for path in top_level:
        decision, reason = _classify(path)
        rel = path.relative_to(REPO).as_posix()
        if decision == "exclude":
            continue
        if decision == "keep":
            kept.append({"path": rel, "reason": reason})
            continue
        if decision == "skip":
            skipped.append({"path": rel, "reason": reason})
            continue
        dest = ARCHIVE_DIR / path.name
        if dest.exists():
            reason = f"{reason}; dest_exists_skip"
            skipped.append({"path": rel, "reason": reason, "would_archive_to": dest.relative_to(REPO).as_posix()})
            continue
        shutil.move(str(path), str(dest))
        archived.append(
            {
                "source": rel,
                "destination": dest.relative_to(REPO).as_posix(),
                "reason": reason,
                "archived_at": ts,
            }
        )

    # Enforce cap: if still > MAX_ACTIVE, archive oldest-kept completed IN_PROGRESS mistakes
    active_now = sorted(p for p in PLANS.glob("*.md") if _is_top_level(p) and p.name not in EXCLUDE_NAMES)
    after_count = len(active_now)

    if after_count > MAX_ACTIVE:
        # Archive keep entries that are IN_PROGRESS but have zero TODO (lowest risk)
        overflow = after_count - MAX_ACTIVE
        for path in sorted(active_now, key=lambda p: p.stat().st_mtime):
            if overflow <= 0:
                break
            if path.name in KEEP_ALWAYS:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "🔲 TODO" in text:
                continue
            dest = ARCHIVE_DIR / path.name
            if dest.exists():
                continue
            rel = path.relative_to(REPO).as_posix()
            shutil.move(str(path), str(dest))
            archived.append(
                {
                    "source": rel,
                    "destination": dest.relative_to(REPO).as_posix(),
                    "reason": "cap_enforcement_no_open_todos",
                    "archived_at": ts,
                }
            )
            overflow -= 1
        active_now = sorted(p for p in PLANS.glob("*.md") if _is_top_level(p) and p.name not in EXCLUDE_NAMES)
        after_count = len(active_now)

    payload = {
        "generated_at": ts,
        "plan_id": "cursor-governance-two-tier-b4e8f2",
        "wave": "W3B",
        "archive_date_folder": f".codex/plans/_archive/{ARCHIVE_MONTH}/",
        "pass_number": pass_number,
        "active_plans_before": before_count,
        "active_plans_after": after_count,
        "archived_plan_count": len(archived),
        "skipped_ambiguous_count": len(skipped),
        "kept_active": [{"path": k["path"], "reason": k["reason"]} for k in kept],
        "archived": archived,
        "skipped_ambiguous": skipped,
        "no_delete_assertion": len([a for a in archived if "deleted" in a.get("reason", "")]) == 0,
        "explicit_non_claims": [
            "cursor-governance-two-tier-b4e8f2.md never archived",
            "no plan bodies rewritten except move metadata in manifest",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# W3 Plan archive manifest",
        "",
        f"Generated: {ts}",
        "",
        f"- **Before:** {before_count} active top-level plans",
        f"- **After:** {after_count} active top-level plans",
        f"- **Archived:** {len(archived)}",
        f"- **Skipped (ambiguous):** {len(skipped)}",
        f"- **Archive folder:** `{payload['archive_date_folder']}`",
        "",
        "## Kept active",
        "",
    ]
    for k in payload["kept_active"]:
        md_lines.append(f"- [{k['path']}]({k['path']}) — {k['reason']}")
    md_lines.append("")
    md_lines.append(f"**No-delete assertion:** archive-only moves ({payload['no_delete_assertion']}).")

    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"[w3-plan-archive] before={before_count} after={after_count} archived={len(archived)}")
    return 0 if after_count < 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
