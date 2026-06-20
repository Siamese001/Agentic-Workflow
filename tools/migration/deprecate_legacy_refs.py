#!/usr/bin/env python3
"""Rewrite active `.windsurf` references to legacy editor/archive locations."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TEXT_EXTS = {
    ".cfg",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".mdc",
    ".ps1",
    ".py",
    ".sql",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SCAN_ROOTS = (
    "AGENTS.md",
    ".pre-commit-config.yaml",
    ".cursor/scripts",
    ".cursor/rules",
    ".cursor/skills",
    "agentic_core",
    "apps_lic",
    "apps_qna",
    "apps_research",
    "apps_rg",
    "apps_underwriting_ai",
    "config",
    "ops_scripts",
    "tests",
    "tools",
)

SKIP_PREFIXES = (
    ".git/",
    ".windsurf/",
    ".codex/plans/_archive/",
    ".cursor/scripts/_legacy_windsurf/",
    "docs/archive/windsurf/legacy-tree/",
)

SKIP_FILES = {
    "ops_scripts/ci/check_no_active_windsurf_changes.py",
    "ops_scripts/ci/check_windsurf_deletion_readiness.py",
    "tools/migration/deprecate_windsurf_refs.py",
}

REPLACEMENTS = (
    (".codex/plans/", "docs/archive/windsurf/legacy-tree/plans/"),
    (".windsurf\\plans\\", "docs\\archive\\windsurf\\legacy-tree\\plans\\"),
    (".windsurf/plans", "docs/archive/windsurf/legacy-tree/plans"),
    (".windsurf\\plans", "docs\\archive\\windsurf\\legacy-tree\\plans"),
    (".windsurf/schemas/", ".cursor/schemas/"),
    (".windsurf\\schemas\\", ".cursor\\schemas\\"),
    (".windsurf/schemas", ".cursor/schemas"),
    (".windsurf\\schemas", ".cursor\\schemas"),
    (".codex/governance/scripts/", ".cursor/scripts/_legacy_windsurf/"),
    (".windsurf\\scripts\\", ".cursor\\scripts\\_legacy_windsurf\\"),
    (".windsurf/scripts", ".cursor/scripts/_legacy_windsurf"),
    (".windsurf\\scripts", ".cursor\\scripts\\_legacy_windsurf"),
    (".codex/skills/", ".codex/skills/"),
    (".windsurf\\skills\\", ".cursor\\skills\\"),
    (".windsurf/skills", ".cursor/skills"),
    (".windsurf\\skills", ".cursor\\skills"),
    (".codex/rules/", ".codex/rules/"),
    (".windsurf\\rules\\", ".cursor\\rules\\"),
    (".windsurf/rules", ".cursor/rules"),
    (".windsurf\\rules", ".cursor\\rules"),
    ("docs/archive/windsurf/legacy-tree/workflows/", "docs/archive/windsurf/legacy-tree/workflows/"),
    (".windsurf\\workflows\\", "docs\\archive\\windsurf\\legacy-tree\\workflows\\"),
    (".windsurf/workflows", "docs/archive/windsurf/legacy-tree/workflows"),
    (".windsurf\\workflows", "docs\\archive\\windsurf\\legacy-tree\\workflows"),
    (".windsurf/state/", ".cursor/state/"),
    (".windsurf\\state\\", ".cursor\\state\\"),
    (".windsurf/state", ".cursor/state"),
    (".windsurf\\state", ".cursor\\state"),
    (".codex/templates/", ".codex/templates/"),
    (".windsurf\\templates\\", ".cursor\\templates\\"),
    (".windsurf/templates", ".cursor/templates"),
    (".windsurf\\templates", ".cursor\\templates"),
    (".windsurf/reminders/", "docs/archive/windsurf/legacy-tree/reminders/"),
    (".windsurf\\reminders\\", "docs\\archive\\windsurf\\legacy-tree\\reminders\\"),
    (".windsurf/reminders", "docs/archive/windsurf/legacy-tree/reminders"),
    (".windsurf\\reminders", "docs\\archive\\windsurf\\legacy-tree\\reminders"),
    (".codex/hooks.json", ".codex/hooks.json"),
    (".windsurf\\hooks.json", ".cursor\\hooks.json"),
    (".mcp.json", ".mcp.json"),
    (".windsurf\\mcp_config.json", ".cursor\\mcp.json"),
    (".windsurf/RULES_INDEX.md", ".cursor/RULES_INDEX.md"),
    (".windsurf\\RULES_INDEX.md", ".cursor\\RULES_INDEX.md"),
    (".windsurfrules", ".cursor/rules"),
    ("artifacts/governance/", "artifacts/governance/"),
    ("artifacts\\windsurf\\", "artifacts\\cursor\\"),
    ("artifacts/governance", "artifacts/governance"),
    ("artifacts\\windsurf", "artifacts\\cursor"),
)

PATH_DIVISION_REPLACEMENTS = (
    ('/ ".windsurf" / "schemas"', '/ ".cursor" / "schemas"'),
    ("/ '.windsurf' / 'schemas'", "/ '.cursor' / 'schemas'"),
    ('/ ".windsurf" / "scripts"', '/ ".cursor" / "scripts" / "_legacy_windsurf"'),
    ("/ '.windsurf' / 'scripts'", "/ '.cursor' / 'scripts' / '_legacy_windsurf'"),
    ('/ ".windsurf" / "skills"', '/ ".cursor" / "skills"'),
    ("/ '.windsurf' / 'skills'", "/ '.cursor' / 'skills'"),
    ('/ ".windsurf" / "rules"', '/ ".cursor" / "rules"'),
    ("/ '.windsurf' / 'rules'", "/ '.cursor' / 'rules'"),
    ('/ ".windsurf" / "state"', '/ ".cursor" / "state"'),
    ("/ '.windsurf' / 'state'", "/ '.cursor' / 'state'"),
    (
        '/ ".windsurf" / "plans"',
        '/ "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"',
    ),
    (
        "/ '.windsurf' / 'plans'",
        "/ 'docs' / 'archive' / 'windsurf' / 'legacy-tree' / 'plans'",
    ),
)

LOCAL_WINDSURF_DIR_RE = re.compile(r"(?<![A-Za-z0-9_])\.windsurf(?=[$/\\\"' )},\]])")


def iter_files() -> list[Path]:
    files: list[Path] = []
    for item in SCAN_ROOTS:
        path = ROOT / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
    return files


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return (
        rel in SKIP_FILES
        or any(rel.startswith(prefix) for prefix in SKIP_PREFIXES)
        or path.suffix.lower() not in TEXT_EXTS
    )


def rewrite_text(text: str) -> str:
    new = text
    for old, replacement in REPLACEMENTS:
        new = new.replace(old, replacement)
    for old, replacement in PATH_DIVISION_REPLACEMENTS:
        new = new.replace(old, replacement)
    return LOCAL_WINDSURF_DIR_RE.sub("docs/archive/windsurf/legacy-tree", new)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    changed: list[str] = []
    for path in iter_files():
        if should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new = rewrite_text(text)
        if new == text:
            continue
        changed.append(path.relative_to(ROOT).as_posix())
        if args.write:
            path.write_text(new, encoding="utf-8")

    print(f"changed={len(changed)} write={args.write}")
    for rel in changed:
        print(rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

