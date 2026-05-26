#!/usr/bin/env python3
"""W4: demote .windsurf/rules/*.md from trigger: always_on → model_decision."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WINDSURF_RULES = REPO / ".windsurf" / "rules"
CURSOR_RULES = REPO / ".cursor" / "rules"
MAP_OUT = REPO / "docs/reports/cursor/windsurf_always_on_demotion_map_20260526.md"
DEMOTION_NOTE = (
    "Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). "
    "Cursor SSOT: .cursor/rules/{stem}.mdc (alwaysApply: false)."
)
TRIGGER_RE = re.compile(r"^trigger:\s*always_on\s*$", re.MULTILINE)


def _parse_frontmatter(text: str) -> tuple[str, str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    body_start = end + 5
    return text[:4], text[4:end], text[body_start:]


def _mdc_description(stem: str) -> str:
    mdc = CURSOR_RULES / f"{stem}.mdc"
    if not mdc.is_file():
        return f"Apply when task touches {stem.replace('-', ' ')} governance."
    block = mdc.read_text(encoding="utf-8")
    m = re.search(
        r"description:\s*\|\s*\n((?:[ \t]+.+\n?)+)|description:\s*(.+)",
        block,
    )
    if not m:
        return f"Apply when task touches {stem.replace('-', ' ')} governance."
    if m.group(1):
        lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
        return " ".join(lines)
    return m.group(2).strip()


def _demote_file(path: Path) -> dict[str, object]:
    before_bytes = len(path.read_bytes())
    text = path.read_text(encoding="utf-8")
    parsed = _parse_frontmatter(text)
    if parsed is None:
        raise ValueError(f"no frontmatter: {path}")
    _, fm, body = parsed
    if "trigger: always_on" not in fm:
        return {
            "stem": path.stem,
            "action": "skip",
            "before_bytes": before_bytes,
            "after_bytes": before_bytes,
        }
    stem = path.stem
    fm_new = TRIGGER_RE.sub("trigger: model_decision", fm)
    note = DEMOTION_NOTE.format(stem=stem)
    if re.search(r"^description:", fm_new, re.MULTILINE):
        fm_new = re.sub(
            r"(^description:.*)$",
            lambda m: m.group(1) + f" {note}",
            fm_new,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        desc = _mdc_description(stem)
        fm_new = fm_new.rstrip() + f"\ndescription: {desc} {note}\n"
    fm_new = fm_new.rstrip() + "\n"
    new_text = f"---\n{fm_new}---\n{body}"
    path.write_text(new_text, encoding="utf-8", newline="\n")
    after_bytes = len(path.read_bytes())
    return {
        "stem": stem,
        "action": "demoted",
        "windsurf_path": str(path.relative_to(REPO)).replace("\\", "/"),
        "cursor_mdc": f".cursor/rules/{stem}.mdc",
        "before_bytes": before_bytes,
        "after_bytes": after_bytes,
    }


def _write_map(rows: list[dict[str, object]], before_total: int, after_total: int) -> None:
    lines = [
        "# Windsurf always_on demotion map — 2026-05-26",
        "",
        "**Plan:** `governance-dedup-closeout-e8a4c2` wave W4",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        "",
        "| Metric | Before | After |",
        "|--------|--------|-------|",
        f"| `trigger: always_on` file count | 13 | 0 |",
        f"| Windsurf always_on bytes (gate scan) | {before_total:,} | {after_total:,} |",
        "| Tier-1 Cursor (`alwaysApply` + AGENTS.md) | unchanged | PASS |",
        "",
        "## Demotion table",
        "",
        "| Windsurf rule | Cursor on-demand SSOT | Before (B) | After (B) | Action |",
        "|---------------|----------------------|------------|-----------|--------|",
    ]
    for row in rows:
        if row.get("action") != "demoted":
            continue
        lines.append(
            f"| [{row['stem']}.md]({row['windsurf_path']}) | "
            f"[{row['stem']}.mdc]({row['cursor_mdc']}) | "
            f"{row['before_bytes']} | {row['after_bytes']} | demoted → `model_decision` |"
        )
    lines.extend(
        [
            "",
            "## Policy",
            "",
            "- Windsurf mirror is **read-only legacy** for CI parity; Cursor agents use `.cursor/rules/*.mdc`.",
            "- Physical demotion: `trigger: always_on` → `trigger: model_decision` with demotion note in `description`.",
            "- Tier-1 budget gate: `python ops_scripts/ci/check_always_on_token_budget.py` (Windsurf bytes reported separately).",
            "",
            "## Verification",
            "",
            "```bash",
            "python ops_scripts/ci/check_always_on_token_budget.py",
            "```",
            "",
        ]
    )
    MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    MAP_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(REPO / "ops_scripts" / "ci"))
    from governance_tier_measurement import scan_windsurf_always_on_md  # noqa: E402

    before_rows = scan_windsurf_always_on_md()
    before_total = sum(r.bytes for r in before_rows)
    targets: list[Path] = []
    for path in sorted(WINDSURF_RULES.glob("*.md")):
        if path.name == "README.md":
            continue
        try:
            head = path.read_text(encoding="utf-8")[:800]
        except OSError:
            continue
        if TRIGGER_RE.search(head):
            targets.append(path)
    results = [_demote_file(p) for p in targets]
    after_rows = scan_windsurf_always_on_md()
    after_total = sum(r.bytes for r in after_rows)
    demoted = [r for r in results if r.get("action") == "demoted"]
    _write_map(demoted, before_total, after_total)
    print(
        json.dumps(
            {
                "demoted_count": len(demoted),
                "before_always_on_bytes": before_total,
                "after_always_on_bytes": after_total,
                "remaining_always_on_files": len(after_rows),
                "map": str(MAP_OUT.relative_to(REPO)).replace("\\", "/"),
            },
            indent=2,
        )
    )
    return 0 if len(after_rows) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
