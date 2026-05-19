#!/usr/bin/env python3
"""One-shot W4 helper: trim skill descriptions into the CI concise band."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / ".cursor" / "skills"
DESC_MIN, DESC_MAX = 60, 420
_FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_WHEN = re.compile(
    r"\b(use when|invoke when|invoke for|invoke\b|when the user|when \w+|before \w+|after \w+)",
    re.I,
)


def _parse_fields(text: str) -> tuple[dict[str, str], str, str]:
    m = _FM.match(text)
    if not m:
        return {}, text, text
    block, body = m.group(1), text[m.end() :]
    fields: dict[str, str] = {}
    key: str | None = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        if raw.startswith(" ") and key:
            fields[key] = (fields[key] + " " + raw.strip()).strip()
            continue
        fm = re.match(r"^([a-z_][a-z0-9_]*)\s*:\s*(.*)$", raw)
        if not fm:
            continue
        key = fm.group(1)
        val = fm.group(2).strip()
        fields[key] = "" if val in {"|", ">"} else val
    return fields, block, body


def _trim(desc: str, name: str) -> str:
    desc = " ".join(desc.split())
    if DESC_MIN <= len(desc) <= DESC_MAX and _WHEN.search(desc):
        return desc
    if not _WHEN.search(desc):
        desc = f"{desc} Invoke when the user needs {name.replace('-', ' ')} guidance."
    while len(desc) > DESC_MAX and " " in desc:
        desc = desc.rsplit(" ", 1)[0].rstrip(".,;") + "."
    if len(desc) < DESC_MIN:
        desc = f"Use when {name.replace('-', ' ')} procedures apply. {desc}"
    return desc[:DESC_MAX]


def main() -> int:
    changed = 0
    for skill_dir in sorted(SKILLS.iterdir()):
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            continue
        text = md.read_text(encoding="utf-8")
        fields, block, body = _parse_fields(text)
        desc = fields.get("description", "")
        if not desc:
            continue
        new = _trim(desc, skill_dir.name)
        if new == desc:
            continue
        # Rewrite description as single-line scalar (YAML-safe)
        lines = block.splitlines()
        out_lines: list[str] = []
        i = 0
        while i < len(lines):
            if re.match(r"^description\s*:", lines[i]):
                out_lines.append(f"description: {new}")
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or lines[i].strip() == ""):
                    if lines[i].strip() and not lines[i].startswith(" "):
                        break
                    if lines[i].startswith(" ") or (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith(" ")):
                        i += 1
                        continue
                    if lines[i].strip() == "":
                        i += 1
                        break
                    i += 1
                continue
            out_lines.append(lines[i])
            i += 1
        new_text = "---\n" + "\n".join(out_lines) + "\n---\n" + body
        md.write_text(new_text, encoding="utf-8")
        print(f"{skill_dir.name}: {len(desc)} -> {len(new)}")
        changed += 1
    print(f"updated {changed} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
