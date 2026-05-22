"""Normalize targeting briefing files: fix pipe/tab tables and use .md extension."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGETING = REPO / "apps_rg" / "config" / "targeting"

_SECTION_HEAD = re.compile(r"^\d+\.\s")


def _md_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _md_separator(ncols: int) -> str:
    return "| " + " | ".join(["---"] * ncols) + " |"


def _is_pipe_table_row(line: str) -> bool:
    s = line.strip()
    if not s or "|" not in s:
        return False
    parts = [p.strip() for p in s.split("|")]
    return len([p for p in parts if p]) >= 2


def _already_md_table_row(line: str) -> bool:
    return line.strip().startswith("|")


def _normalize_md_separator(line: str) -> str:
    if not line.strip().startswith("|"):
        return line
    return re.sub(r":?----+:?", "---", line)


def _fix_inline_pipe_tables(text: str) -> str:
    """Rows like 'A | B | C' without a leading pipe -> GFM table."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _is_pipe_table_row(line) and not _already_md_table_row(line):
            block: list[str] = []
            while i < len(lines) and _is_pipe_table_row(lines[i]) and not _already_md_table_row(lines[i]):
                block.append(lines[i])
                i += 1
            md_rows = [_md_row([c.strip() for c in row.split("|")]) for row in block]
            ncols = md_rows[0].count("|") - 1
            if len(md_rows) > 1:
                out.append("")
                out.append(md_rows[0])
                out.append(_md_separator(ncols))
                out.extend(md_rows[1:])
                out.append("")
            else:
                out.extend(md_rows)
            continue
        if _already_md_table_row(line):
            out.append(_normalize_md_separator(line))
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _parse_vertical_tab_block(raw_lines: list[str]) -> list[list[str]] | None:
    rows: list[list[str]] = []
    row: list[str] = []
    ncols: int | None = None

    for line in raw_lines:
        if not line.strip():
            continue
        cell = line[1:].strip() if line.startswith("\t") else line.strip()
        if _SECTION_HEAD.match(cell):
            break
        if line.startswith("\t"):
            row.append(cell)
        else:
            if row:
                if ncols is None:
                    ncols = len(row)
                elif len(row) != ncols:
                    return None
                rows.append(row)
            row = [cell]
    if row:
        if ncols is None:
            ncols = len(row)
        elif len(row) == ncols:
            rows.append(row)
        else:
            return None
    if not rows or ncols is None or len(rows) < 2:
        return None
    if not all(len(r) == ncols for r in rows):
        return None
    return rows


def _fix_vertical_tab_tables(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() and not line.startswith("|") and (
            (line.startswith("\t") and i > 0 and lines[i - 1].strip() == "")
            or (not line.startswith("\t") and i + 1 < len(lines) and lines[i + 1].startswith("\t"))
        ):
            start = i
            if not line.startswith("\t"):
                probe = i
                chunk: list[str] = []
                while probe < len(lines):
                    if not lines[probe].strip():
                        break
                    chunk.append(lines[probe])
                    probe += 1
                    if len(chunk) >= 6:
                        break
                parsed = _parse_vertical_tab_block(chunk)
                if parsed:
                    md = [_md_row(parsed[0]), _md_separator(len(parsed[0]))] + [_md_row(r) for r in parsed[1:]]
                    out.append("")
                    out.extend(md)
                    out.append("")
                    i = start + len(chunk)
                    continue
        out.append(line)
        i += 1
    return "\n".join(out)


def normalize_briefing_text(text: str) -> str:
    text = _fix_vertical_tab_tables(text)
    text = _fix_inline_pipe_tables(text)
    return text


def process_file(path: Path, *, rename_md: bool = True) -> Path:
    text = path.read_text(encoding="utf-8")
    normalized = normalize_briefing_text(text)
    out_path = path.with_suffix(".md") if rename_md and path.suffix.lower() == ".txt" else path
    out_path.write_text(normalized, encoding="utf-8")
    if rename_md and out_path != path and path.exists():
        path.unlink()
    return out_path


def main(argv: list[str]) -> int:
    names = argv or [
        "truist_head_agentic_ai_engineering_briefing.md",
        "neo4j_vp_product_management_agentic_ai_briefing.txt",
        "invesco_global_head_advanced_engineering_briefing.txt",
        "brown_brown_svp_it_strategy_innovation_briefing.md",
        "brown_brown_svp_it_strategy_innovation_briefing_exec.md",
        "aig_vp_global_head_agentic_ai_briefing.txt",
        "openai_partner_ade_briefing.txt",
    ]
    for name in names:
        p = TARGETING / name
        if not p.exists() and name.endswith(".md"):
            p = TARGETING / name.replace(".md", ".txt")
        if not p.exists():
            print(f"skip missing: {name}", file=sys.stderr)
            continue
        out = process_file(p, rename_md=True)
        print(f"ok {out.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
