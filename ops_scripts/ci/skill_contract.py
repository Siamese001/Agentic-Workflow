#!/usr/bin/env python3
"""Shared parsing and validation helpers for repository-owned Agent Skills."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ALLOWED_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
BODY_MAX_LINES = 500
_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class SkillDocument:
    """Parsed representation of one ``SKILL.md`` document."""

    path: Path
    frontmatter: dict[str, Any]
    body: str
    text: str

    @property
    def name(self) -> str:
        value = self.frontmatter.get("name", "")
        return value if isinstance(value, str) else ""

    @property
    def description(self) -> str:
        value = self.frontmatter.get("description", "")
        return value if isinstance(value, str) else ""


def parse_skill_document(skill_md: Path) -> tuple[SkillDocument | None, list[str]]:
    """Parse one skill document and return structural errors without raising."""

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"could not read: {exc}"]

    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return None, [
            "missing or malformed YAML frontmatter "
            "(SKILL.md must start with '---' and include a closing '---')"
        ]

    raw_frontmatter = match.group(1)
    try:
        payload = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        return None, [f"invalid YAML frontmatter: {exc}"]

    if not isinstance(payload, dict):
        return None, ["frontmatter must be a YAML mapping"]

    frontmatter = dict(payload)
    body = text[match.end() :]
    return SkillDocument(skill_md, frontmatter, body, text), []


def validate_skill_document(document: SkillDocument) -> list[str]:
    """Validate the Agent Skills specification plus repository line budget."""

    issues: list[str] = []
    frontmatter = document.frontmatter

    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_FIELDS)
    if unexpected:
        issues.append(
            "unsupported frontmatter field(s): "
            + ", ".join(unexpected)
            + "; allowed fields are "
            + ", ".join(sorted(ALLOWED_FRONTMATTER_FIELDS))
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        issues.append("frontmatter field 'name' must be a non-empty string")
    else:
        name = name.strip()
        if len(name) > NAME_MAX:
            issues.append(f"name is {len(name)} characters; maximum is {NAME_MAX}")
        if _NAME_RE.fullmatch(name) is None:
            issues.append(
                "name must contain lowercase letters, digits, and single hyphens only; "
                "it cannot start/end with a hyphen or contain consecutive hyphens"
            )
        parent_name = document.path.parent.name
        if name != parent_name:
            issues.append(f"name '{name}' must match parent directory '{parent_name}'")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        issues.append("frontmatter field 'description' must be a non-empty string")
    elif len(description.strip()) > DESCRIPTION_MAX:
        issues.append(
            f"description is {len(description.strip())} characters; maximum is {DESCRIPTION_MAX}"
        )

    for field in ("license", "allowed-tools"):
        value = frontmatter.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            issues.append(f"frontmatter field '{field}' must be a non-empty string when present")

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str) or not compatibility.strip():
            issues.append("frontmatter field 'compatibility' must be a non-empty string when present")
        elif len(compatibility.strip()) > COMPATIBILITY_MAX:
            issues.append(
                f"compatibility is {len(compatibility.strip())} characters; "
                f"maximum is {COMPATIBILITY_MAX}"
            )

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            issues.append("frontmatter field 'metadata' must be a string-to-string mapping")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not key.strip():
                    issues.append("metadata keys must be non-empty strings")
                if not isinstance(value, str):
                    issues.append(f"metadata value for '{key}' must be a string")

    total_lines = document.text.count("\n") + 1
    if total_lines > BODY_MAX_LINES:
        issues.append(
            f"SKILL.md is {total_lines} lines; keep it at or below {BODY_MAX_LINES} "
            "and move detail into references/"
        )

    return issues


def validate_skill_path(skill_md: Path) -> list[str]:
    """Parse and validate one skill path."""

    document, issues = parse_skill_document(skill_md)
    if document is None:
        return issues
    return [*issues, *validate_skill_document(document)]


def iter_skill_directories(skills_root: Path) -> list[Path]:
    """Return deterministic top-level skill directories containing ``SKILL.md``."""

    if not skills_root.is_dir():
        return []
    return sorted(
        directory
        for directory in skills_root.iterdir()
        if directory.is_dir() and (directory / "SKILL.md").is_file()
    )
