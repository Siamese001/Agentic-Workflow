#!/usr/bin/env python3
"""
open_scope_inventory.py — extract open-scope items from plan files and ADRs.

Scans:
  .windsurf/plans/*.md
  docs/architecture/adr/ADR-*.md

Extracts sections matching a set of canonical open-scope headings:
  ## Gap Register
  ## Next Steps
  ## Open Questions
  ## Out of Scope
  ## Future Improvement Opportunities
  ## Deferred
  ## Follow-up

Emits JSON (default) or markdown (--format md).

Each item carries:
  source_file, source_path, section, item_id (e.g. GAP-1), title,
  blurb, source_hints (deferred/blocked/todo).

Used by Cascade to drive Memory/Notion writeback for open scope.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = [
    REPO_ROOT / ".windsurf" / "plans",
    REPO_ROOT / "docs" / "architecture" / "adr",
]

SECTION_HEADINGS = {
    "gap_register": re.compile(r"^#{2,3}\s+Gap Register", re.IGNORECASE),
    "next_steps": re.compile(r"^#{2,3}\s+Next Steps?", re.IGNORECASE),
    "open_questions": re.compile(r"^#{2,3}\s+Open Questions?", re.IGNORECASE),
    "out_of_scope": re.compile(r"^#{2,3}\s+Out of Scope", re.IGNORECASE),
    "future_opportunities": re.compile(r"^#{2,3}\s+Future\s+(Improvement\s+)?Opportunities?", re.IGNORECASE),
    "deferred": re.compile(r"^#{2,3}\s+Deferred", re.IGNORECASE),
    "followup": re.compile(r"^#{2,3}\s+Follow[-\s]?ups?", re.IGNORECASE),
}

# Any H2/H3 marks end of section
SECTION_TERMINATOR = re.compile(r"^#{2,3}\s+")

# Item markers inside a section
GAP_ID_RE = re.compile(
    r"^\*\*(GAP-\d+[a-z]?|OQ-?\d+|H\d+|F\d+\.\d+|W\d+[-.]P?\d+|[A-Z]+-\d+)[:\s]",
    re.MULTILINE,
)
BULLET_RE = re.compile(r"^\s*[-*]\s+\*\*([^*]+?)\*\*:?\s*(.*)$", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)

STATUS_HINTS = {
    "deferred": re.compile(r"\bdeferred\b", re.IGNORECASE),
    "blocked": re.compile(r"\bblock(ed|er|ing)\b", re.IGNORECASE),
    "todo": re.compile(r"\b(todo|pending|open|not\s+started)\b", re.IGNORECASE),
    "in_progress": re.compile(r"\b(in\s+progress|wip|underway)\b", re.IGNORECASE),
    "done": re.compile(r"\b(done|complete|shipped|resolved)\b", re.IGNORECASE),
    "descoped": re.compile(r"\bdesc(o|ro)ped\b", re.IGNORECASE),
}


@dataclass
class OpenScopeItem:
    source_file: str
    source_path: str
    section: str
    item_id: Optional[str]
    title: str
    blurb: str
    status_hints: list[str]


def _extract_sections(content: str) -> list[tuple[str, str]]:
    """Return list of (section_name, body) tuples."""
    lines = content.splitlines(keepends=True)
    sections: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched_name: Optional[str] = None
        for name, pattern in SECTION_HEADINGS.items():
            if pattern.match(line.strip()):
                matched_name = name
                break
        if matched_name is None:
            i += 1
            continue
        body_start = i + 1
        j = body_start
        while j < len(lines) and not SECTION_TERMINATOR.match(lines[j].strip()):
            j += 1
        body = "".join(lines[body_start:j])
        sections.append((matched_name, body))
        i = j
    return sections


def _status_hints_for(text: str) -> list[str]:
    return [name for name, pat in STATUS_HINTS.items() if pat.search(text)]


def _parse_items(section_name: str, body: str, source_path: Path) -> list[OpenScopeItem]:
    items: list[OpenScopeItem] = []
    source_file = source_path.name
    rel = source_path.relative_to(REPO_ROOT).as_posix()

    # Strategy 1: bold-IDd paragraphs e.g. **GAP-1: Title**
    gap_matches = list(GAP_ID_RE.finditer(body))
    if gap_matches:
        for k, m in enumerate(gap_matches):
            start = m.start()
            end = gap_matches[k + 1].start() if k + 1 < len(gap_matches) else len(body)
            chunk = body[start:end]
            header_line = chunk.splitlines()[0] if chunk else ""
            # Title = everything on header line after the bold ID
            title = header_line
            id_match = re.match(r"^\*\*([^:*]+)[:\s*]*\*?\*?\s*(.*)$", header_line)
            item_id = id_match.group(1).strip() if id_match else None
            title_rest = id_match.group(2).strip() if id_match else header_line
            blurb = chunk[:500]
            items.append(
                OpenScopeItem(
                    source_file=source_file,
                    source_path=rel,
                    section=section_name,
                    item_id=item_id,
                    title=(title_rest or item_id or source_file)[:120],
                    blurb=blurb.strip(),
                    status_hints=_status_hints_for(chunk),
                )
            )
        return items

    # Strategy 2: bullet list entries e.g. - **Title**: blurb
    bullet_matches = list(BULLET_RE.finditer(body))
    if bullet_matches:
        for m in bullet_matches:
            title = m.group(1).strip()
            blurb_after = m.group(2).strip()
            items.append(
                OpenScopeItem(
                    source_file=source_file,
                    source_path=rel,
                    section=section_name,
                    item_id=None,
                    title=title[:120],
                    blurb=f"{title}: {blurb_after}"[:500],
                    status_hints=_status_hints_for(f"{title} {blurb_after}"),
                )
            )
        return items

    # Strategy 3: table rows (skip header + separator)
    table_rows = list(TABLE_ROW_RE.finditer(body))
    if len(table_rows) > 2:
        for m in table_rows[2:]:
            col1 = m.group(1).strip()
            col2 = m.group(2).strip()
            col3 = m.group(3).strip()
            if col1.startswith("-") or col1.startswith(":") or not col1:
                continue
            items.append(
                OpenScopeItem(
                    source_file=source_file,
                    source_path=rel,
                    section=section_name,
                    item_id=col1 if re.match(r"^[A-Z0-9\-\.]+$", col1) else None,
                    title=(col2 or col1)[:120],
                    blurb=f"{col1} | {col2} | {col3}"[:500],
                    status_hints=_status_hints_for(f"{col1} {col2} {col3}"),
                )
            )
        return items

    # Strategy 4: free-text fallback — emit a single item for the whole section
    body_trim = body.strip()
    if body_trim:
        items.append(
            OpenScopeItem(
                source_file=source_file,
                source_path=rel,
                section=section_name,
                item_id=None,
                title=f"[section: {section_name}]"[:120],
                blurb=body_trim[:500],
                status_hints=_status_hints_for(body_trim),
            )
        )
    return items


def scan() -> list[OpenScopeItem]:
    all_items: list[OpenScopeItem] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for md_path in sorted(root.glob("*.md")):
            try:
                content = md_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            sections = _extract_sections(content)
            for section_name, body in sections:
                all_items.extend(_parse_items(section_name, body, md_path))
    return all_items


def _as_markdown(items: list[OpenScopeItem]) -> str:
    out: list[str] = [
        "# Open Scope Inventory",
        "",
        f"Total items: **{len(items)}**",
        "",
        "| Source | Section | ID | Title | Hints |",
        "|---|---|---|---|---|",
    ]
    for it in items:
        hints = ",".join(it.status_hints) or "-"
        title = it.title.replace("|", "\\|")
        out.append(f"| `{it.source_file}` | {it.section} | {it.item_id or '-'} | {title} | {hints} |")
    return "\n".join(out) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--format", choices=["json", "md"], default="json")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    items = scan()
    payload = [asdict(i) for i in items]
    if args.format == "json":
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        text = _as_markdown(items)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {len(items)} items -> {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
