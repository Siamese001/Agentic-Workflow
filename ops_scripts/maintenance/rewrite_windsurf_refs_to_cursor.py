#!/usr/bin/env python3
"""Rewrite active Windsurf SSOT path references to Cursor equivalents.

Skips archive/legacy trees and preserves explicit Windsurf-mirror MCP paths.

Usage:
  python ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py --dry-run
  python ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIR_PARTS = (
    "_archive",
    "_legacy_windsurf",
    "_legacy_cursor",
    "_zero_loss_originals",
    "windsurf_compat",
    "windsurf_legacy_plans",
    "__pycache__",
    ".git",
)

TEXT_SUFFIXES = {".md", ".mdc", ".py", ".yaml", ".yml", ".json"}

REPLACEMENTS: list[tuple[str, str]] = [
    (".cursor/rules/", ".cursor/rules/"),
    ("docs/archive/windsurf/legacy-tree/plans/", ".cursor/plans/"),
    (".cursor/state/", ".cursor/state/"),
    (".claude/governance/scripts/", ".cursor/scripts/"),
    (".cursor/skills/", ".cursor/skills/"),
    ("docs/archive/windsurf/legacy-tree/config/", ".cursor/config/"),
    (' / "docs/archive/windsurf/legacy-tree" / "config" / ', ' / ".cursor" / "config" / '),
    (".cursor/hooks.json", ".cursor/hooks.json"),
    (".cursor/schemas/", ".cursor/schemas/"),
    ("docs/archive/windsurf/legacy-tree/workflows/", ".cursor/workflows/"),
    (".cursor/templates/", ".cursor/templates/"),
    ("docs/archive/windsurf/legacy-tree/commands/", ".cursor/commands/"),
    ("docs/archive/windsurf/legacy-tree/agents/", ".cursor/agents/"),
    (".cursor/RULES_INDEX.md", ".cursor/RULES_INDEX.md"),
    ("artifacts/cursor/", "artifacts/cursor/"),
    ('Path("artifacts/cursor")', 'Path("artifacts/cursor")'),
    ("Path('artifacts/cursor')", "Path('artifacts/cursor')"),
    (r"\.windsurf[/\\]mcp_config\.json", r".cursor[/\\]mcp\.json"),
    (r"\.windsurf[/\\]scripts[/\\]", r".cursor[/\\]scripts[/\\]"),
    (r"\.windsurf[/\\]plans[/\\]", r".cursor[/\\]plans[/\\]"),
    (r"\\\.windsurf[/\\]plans", r"\\\.cursor[/\\]plans"),
    ("@.cursor/rules/", "@.cursor/rules/"),
    ("tools/windsurf/wave_execution_state.py", "tools/plan_lifecycle/wave_execution_state.py"),
    ("python tools/windsurf/wave_execution_state.py", "python tools/plan_lifecycle/wave_execution_state.py"),
    ("docs/windsurf/", "docs/cursor/"),
    ("windsurf-config-lookup.md", "cursor-config-lookup.mdc"),
    ("windsurf-config-lookup", "cursor-config-lookup"),
    ("## Windsurf Configuration Docs", "## Cursor Configuration Docs"),
    ("Windsurf Configuration Docs", "Cursor Configuration Docs"),
]

# Whole-line / doc fixes (order matters — run after path swaps).
PHRASE_REPLACEMENTS: list[tuple[str, str]] = [
    (
        "invoke the `structured-reasoning` skill. Emit `SR_INTAKE`",
        "invoke the `structured-reasoning` skill. Emit `SR_INTAKE`",
    ),
    (
        "See `.cursor/rules/sequential-thinking-enforcement.md`",
        "See `.cursor/rules/sequential-thinking-enforcement.mdc`",
    ),
    (
        "See `.cursor/rules/sequential-thinking-enforcement.md`",
        "See `.cursor/rules/sequential-thinking-enforcement.mdc`",
    ),
    (
        "See `.cursor/rules/windsurf-config-lookup.md`",
        "See `.cursor/rules/cursor-config-lookup.mdc`",
    ),
    (
        "See `.cursor/rules/windsurf-config-lookup.md` for the full local-first lookup order. Local docs mirror: `docs/windsurf/`. Plans SSOT: `docs/archive/windsurf/legacy-tree/plans/<name>-<6hex>.md`",
        "See `.cursor/rules/cursor-config-lookup.mdc` for the full local-first lookup order. Plans SSOT: `.cursor/plans/<name>-<6hex>.md`",
    ),
    (
        "Full rules: `.cursor/rules/` and `.cursor/RULES_INDEX.md`",
        "Full rules: `.cursor/rules/` and `.cursor/RULES_INDEX.md`",
    ),
    (
        "2. **Windsurf Rules** — Static analysis and editing-time guidance",
        "2. **Cursor Rules** — Static analysis and editing-time guidance",
    ),
    (
        "Sync Windsurf mirror via `.claude/governance/scripts/post_write_mcp_config_sync.py` when using Windsurf",
        "Sync Windsurf mirror via `.claude/governance/scripts/post_write_mcp_config_sync.py` when using Windsurf (optional)",
    ),
    (
        "Change gate behavior in `.claude/governance/scripts/pre_mcp_gate.py`",
        "Change gate behavior in `.cursor/scripts/pre_mcp_gate.py`",
    ),
    (
        "python .claude/governance/scripts/sync_mcp_config.py",
        "python .cursor/scripts/sync_mcp_config.py",
    ),
    (
        "Filesystem SSOT: `.cursor/mcp.json`",
        "Filesystem SSOT (Windsurf mirror): `.cursor/mcp.json`",
    ),
    (
        "Filesystem SSOT: `.cursor/rules/*.md`",
        "Filesystem SSOT: `.cursor/rules/*.mdc`",
    ),
]


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if any(part in SKIP_DIR_PARTS for part in parts):
        return True
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    return False


def _rewrite_text(text: str) -> str:
    updated = text
    for old, new in REPLACEMENTS:
        updated = updated.replace(old, new)
    for old, new in PHRASE_REPLACEMENTS:
        updated = updated.replace(old, new)
    updated = updated.replace(".mdc.mdc", ".mdc")
    return updated


def iter_target_files() -> list[Path]:
    roots = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "agentic_core" / "AGENTS.md",
        REPO_ROOT / "apps_lic" / "AGENTS.md",
        REPO_ROOT / "apps_qna" / "AGENTS.md",
        REPO_ROOT / "apps_research" / "AGENTS.md",
        REPO_ROOT / "apps_rg" / "AGENTS.md",
        REPO_ROOT / ".cursor" / "rules",
        REPO_ROOT / ".cursor" / "plans",
        REPO_ROOT / ".cursor" / "scripts",
        REPO_ROOT / ".cursor" / "skills",
        REPO_ROOT / ".cursor" / "hooks",
        REPO_ROOT / "tools" / "windsurf",
        REPO_ROOT / "tools" / "plan_lifecycle",
        REPO_ROOT / "ops_scripts" / "ci",
        REPO_ROOT / ".pre-commit-config.yaml",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            if not _should_skip(root):
                files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not _should_skip(path):
                files.append(path)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed = 0
    for path in iter_target_files():
        original = path.read_text(encoding="utf-8")
        updated = _rewrite_text(original)
        if updated == original:
            continue
        changed += 1
        rel = path.relative_to(REPO_ROOT)
        print(f"{'DRY-RUN' if args.dry_run else 'UPDATE'}: {rel}")
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    print(f"{'Would update' if args.dry_run else 'Updated'} {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
