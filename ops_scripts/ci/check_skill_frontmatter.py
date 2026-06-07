#!/usr/bin/env python3
"""check_skill_frontmatter.py — CI gate: every ``.cursor/skills/<name>/SKILL.md``
must conform to Anthropic's Agent Skills authoring spec.

Reference: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Enforced invariants
-------------------
1. YAML frontmatter exists (starts with ``---`` on line 1).
2. ``name`` field present, non-empty, length <= 64, matches ``^[a-z0-9-]+$``,
   contains no reserved words (``anthropic``, ``claude``).
3. ``description`` field present, non-empty, length <= 1024 chars.
4. Description uses third person (no first-person leaks like ``"I can"``,
   ``"I will"``, ``"I help"``, ``"you can use this"``, ``"this helps you"``).
5. Description contains a when-trigger (one of: ``use when``, ``when ``,
   ``before ``, ``after ``, ``during ``).
6. SKILL.md body (including frontmatter) <= 500 lines.
7. No Windows-style path separators in SKILL.md content
   (``scripts\\helper``, ``docs/archive/windsurf/legacy-tree\\skills``, etc.).

Exit 0: every skill conforms.
Exit 1: one or more violations.

Usage
-----
    python ops_scripts/ci/check_skill_frontmatter.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".cursor" / "skills"

NAME_MAX = 64
DESC_MAX = 1024
BODY_MAX_LINES = 500
RESERVED_WORDS = ("anthropic", "claude")
FIRST_PERSON_PATTERNS = (
    re.compile(r"\bI (?:can|will|help|am|have|provide)\b", re.IGNORECASE),
    re.compile(r"\byou can use this\b", re.IGNORECASE),
    re.compile(r"\bthis helps you\b", re.IGNORECASE),
    re.compile(r"\bteaches cascade\b", re.IGNORECASE),
)
WHEN_TRIGGER_PATTERNS = (
    re.compile(r"\bwhen \w+\b", re.IGNORECASE),
    re.compile(r"\bbefore \w+\b", re.IGNORECASE),
    re.compile(r"\bafter \w+\b", re.IGNORECASE),
    re.compile(r"\bduring \w+\b", re.IGNORECASE),
    re.compile(r"\binvoke\b", re.IGNORECASE),
)
# Detect Windows-style separators used as real path dividers in the body.
# Exempt inline-code (``...``) and fenced code blocks — documentation often
# *cites* forbidden path patterns as examples (e.g. noting ``C:\Users\...``
# as a thing to detect), and those cites are not violations.
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\[A-Za-z]|\docs/archive/windsurf/legacy-tree\\|scripts\\|ops_scripts\\")
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """Extract ``{key: value}`` frontmatter and the body after it.

    Returns ``None`` if no valid frontmatter exists (missing opening ``---`` or
    missing closing ``---`` before content).
    """
    if not text.startswith("---\n"):
        return None
    end_marker = text.find("\n---\n", 4)
    if end_marker < 0:
        return None
    block = text[4:end_marker]
    body = text[end_marker + 5 :]
    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        if raw.startswith(" ") and current_key is not None:
            fields[current_key] = fields[current_key] + " " + raw.strip()
            continue
        m = re.match(r"^([a-z_][a-z0-9_]*)\s*:\s*(.*)$", raw)
        if not m:
            continue
        current_key = m.group(1)
        fields[current_key] = m.group(2).strip()
    return fields, body


def _check_skill(skill_md: Path) -> list[str]:
    """Return a list of violation messages for this SKILL.md."""
    violations: list[str] = []
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"could not read: {exc}"]

    # Rule 6: body <= 500 lines
    total_lines = text.count("\n") + 1
    if total_lines > BODY_MAX_LINES:
        violations.append(
            f"SKILL.md is {total_lines} lines (Anthropic budget: {BODY_MAX_LINES}). "
            f"Split supporting content into separate files under the skill directory."
        )

    parsed = _parse_frontmatter(text)
    if parsed is None:
        violations.append("missing YAML frontmatter (file must start with '---' and close with '---')")
        return violations
    fields, _body = parsed

    # Rule 2: name
    name = fields.get("name", "")
    if not name:
        violations.append("frontmatter missing required field: name")
    else:
        if len(name) > NAME_MAX:
            violations.append(f"name '{name}' is {len(name)} chars (max {NAME_MAX})")
        if not re.match(r"^[a-z0-9-]+$", name):
            violations.append(
                f"name '{name}' must match ^[a-z0-9-]+$ (lowercase letters, numbers, hyphens only)"
            )
        for reserved in RESERVED_WORDS:
            if reserved in name.lower():
                violations.append(f"name '{name}' contains reserved word '{reserved}'")

    # Rule 3 + 4 + 5: description
    desc = fields.get("description", "")
    if not desc:
        violations.append("frontmatter missing required field: description")
    else:
        if len(desc) > DESC_MAX:
            violations.append(f"description is {len(desc)} chars (max {DESC_MAX})")
        for pat in FIRST_PERSON_PATTERNS:
            if pat.search(desc):
                violations.append(
                    f"description contains first/second-person leak: '{pat.pattern}' "
                    f"(Anthropic requires third person)"
                )
        if not any(pat.search(desc) for pat in WHEN_TRIGGER_PATTERNS):
            violations.append(
                "description missing when-trigger "
                "(Anthropic requires both what + when; include phrases like "
                "'Use when ...', 'Before ...', 'After ...', 'During ...')"
            )

    # Rule 7: Windows-style paths (strip code spans first — docs often cite
    # forbidden patterns as examples, and those cites aren't violations).
    stripped = _FENCED_CODE_RE.sub("", text)
    stripped = _INLINE_CODE_RE.sub("", stripped)
    m = WINDOWS_PATH_RE.search(stripped)
    if m is not None:
        violations.append(
            f"contains Windows-style path separator near '{m.group(0)}' — "
            "use forward slashes (outside of code spans)"
        )

    return violations


def main() -> int:
    if not SKILLS_ROOT.exists():
        print(f"[skill_frontmatter] SKIP: {SKILLS_ROOT} not found", flush=True)
        return 0

    failures: dict[str, list[str]] = {}
    skill_dirs = sorted(d for d in SKILLS_ROOT.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"[skill_frontmatter] SKIP: no skills under {SKILLS_ROOT}", flush=True)
        return 0

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            failures[skill_dir.name] = ["SKILL.md not found"]
            continue
        issues = _check_skill(skill_md)
        if issues:
            failures[skill_dir.name] = issues

    if failures:
        print("[skill_frontmatter] FAIL: the following skills violate Anthropic's authoring spec:\n")
        for name, issues in failures.items():
            print(f"  .cursor/skills/{name}/SKILL.md")
            for issue in issues:
                print(f"    - {issue}")
            print()
        print(
            "Reference: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices",
        )
        return 1

    print(
        f"[skill_frontmatter] OK: all {len(skill_dirs)} skills conform to Anthropic's "
        "authoring spec (name, description, <500 line body, third person, when-trigger).",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
