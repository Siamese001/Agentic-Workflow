#!/usr/bin/env python3
"""Rename Windsurf-agent 'cascade' hooks/strings to Cursor Agent equivalents.

Cursor Agent (Windsurf agent) -> Cursor Agent
post_cursor_agent_* -> post_cursor_agent_*

Does NOT rewrite:
  - SQL CASCADE / FOREIGN KEY ... CASCADE
  - lowercase 'cascading' (adjective)
  - L2 router id 'cascade' / router=cascade / L2/cascade
  - Cost-tier / route-selection 'cascade' in agentic_core L0
  - import-cascade, full-cascade, qwen cascade fallback (execution cascade)

Usage:
  python ops_scripts/maintenance/rewrite_cascade_to_cursor.py --dry-run
  python ops_scripts/maintenance/rewrite_cascade_to_cursor.py
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
    "historical_plans_20260515",
    "__pycache__",
    ".git",
    "node_modules",
)

TEXT_SUFFIXES = {".md", ".mdc", ".py", ".yaml", ".yml", ".json", ".sql"}

# Longest-first identifier / path replacements.
IDENT_REPLACEMENTS: list[tuple[str, str]] = [
    ("post_cursor_agent_response", "post_cursor_agent_response"),
    ("post_cursor_agent_", "post_cursor_agent_"),
    ("POST_CURSOR_AGENT_", "POST_CURSOR_AGENT_"),
    ("manual_post_cursor_agent", "manual_post_cursor_agent"),
    ("_post_cursor_agent_payload", "_post_cursor_agent_payload"),
    ("check_post_cursor_agent_alive", "check_post_cursor_agent_alive"),
    ("post-cursor-agent", "post-cursor-agent"),
    ("Post-Cursor-Agent", "Post-Cursor-Agent"),
    ("Post-cursor-agent", "Post-cursor-agent"),
    ("--cursor-prompts", "--cursor-prompts"),
    ("cursor_prompts", "cursor_prompts"),
    ("cursor-prompts", "cursor-prompts"),
]

PROSE_REPLACEMENTS: list[tuple[str, str]] = [
    ("Cursor Agent", "Cursor Agent"),
    ("Cursor Agent's", "Cursor Agent's"),
    ("Cursor Agent MUST", "Cursor Agent MUST"),
    ("Cursor Agent makes", "Cursor Agent makes"),
    ("Cursor Agent response", "Cursor Agent response"),
    ("cursor agent response", "cursor agent response"),
    ("Cursor Agent tool-call", "Cursor Agent tool-call"),
    ("Cursor Agent composed", "Cursor Agent composed"),
    ("Event in Cursor Agent", "Event in Cursor Agent"),
    ("by Cursor Agent", "by Cursor Agent"),
    ("when Cursor Agent", "when Cursor Agent"),
    ("if Cursor Agent", "if Cursor Agent"),
    ("that Cursor Agent", "that Cursor Agent"),
    ("Cursor Agent can", "Cursor Agent can"),
    ("Cursor Agent is", "Cursor Agent is"),
    ("Cursor Agent has", "Cursor Agent has"),
    ("Cursor Agent executed", "Cursor Agent executed"),
    ("Cursor Agent edited", "Cursor Agent edited"),
    ("Cursor Agent closes", "Cursor Agent closes"),
    ("Cursor Agent turn", "Cursor Agent turn"),
    ("Cursor Agent session", "Cursor Agent session"),
    ("Cursor Agent violations", "Cursor Agent violations"),
    ("Cursor Agent violation", "Cursor Agent violation"),
    ("Cursor Agent at", "Cursor Agent at"),
    ("Cursor Agent post-", "Cursor Agent post-"),
    ("Cursor Agent would", "Cursor Agent would"),
    ("Cursor Agent self-", "Cursor Agent self-"),
    ("Cursor Agent discussing", "Cursor Agent discussing"),
    ("Cursor Agent touched", "Cursor Agent touched"),
    ("Cursor Agent list", "Cursor Agent list"),
    ("Cursor Agent mis-", "Cursor Agent mis-"),
    ("Cursor Agent cannot", "Cursor Agent cannot"),
    ("Cursor-Agent-authorable", "Cursor-Agent-authorable"),
    ("Cursor Agent responses", "Cursor Agent responses"),
    ("Cursor Agent response", "Cursor Agent response"),
    ("block Cursor Agent", "block Cursor Agent"),
    ("never block Cursor Agent", "never block Cursor Agent"),
    ("help Cursor Agent", "help Cursor Agent"),
    ("signals Cursor Agent", "signals Cursor Agent"),
    ("Detects Cursor Agent", "Detects Cursor Agent"),
    ("Scans Cursor Agent", "Scans Cursor Agent"),
    ("Reads Cursor Agent", "Reads Cursor Agent"),
    ("Fires on every Cursor Agent", "Fires on every Cursor Agent"),
    ("emitted by Cursor Agent", "emitted by Cursor Agent"),
    ("native Cursor Agent tools", "native Cursor Agent tools"),
    ("Windsurf/Cursor Agent", "Windsurf/Cursor Agent"),
    ("Restart Windsurf/Cursor Agent", "Restart Windsurf/Cursor Agent"),
    ("hang Cursor Agent's", "hang Cursor Agent's"),
    ("Author: Cursor", "Author: Cursor"),
    ("agent_identity=\"Cursor Agent\"", "agent_identity=\"Cursor Agent\""),
    ("Cursor Agent hook", "Cursor Agent hook"),
    ("Cursor Agent hooks", "Cursor Agent hooks"),
    ("Cursor Agent turn,", "Cursor Agent turn,"),
    ("Cursor Agent per", "Cursor Agent per"),
    ("from Cursor Agent", "from Cursor Agent"),
    ("to Cursor Agent", "to Cursor Agent"),
    ("Cursor Agent regression", "Cursor Agent regression"),
    ("Cursor Agent is regressing", "Cursor Agent is regressing"),
    ("did Cursor Agent's", "did Cursor Agent's"),
    ("Cursor Agent wrote", "Cursor Agent wrote"),
    ("what Cursor Agent wrote", "what Cursor Agent wrote"),
    ("Cursor Agent executed waves", "Cursor Agent executed waves"),
    ("Cursor Agent tool-schema", "Cursor Agent tool-schema"),
]

# Filenames to rename (basename patterns).
RENAME_GLOBS = [
    "**/post_cursor_agent_*.py",
    "**/manual_post_cursor_agent_replay.py",
    "**/check_post_cursor_agent_alive.py",
    "**/_post_cursor_agent_payload.py",
    "**/test_post_cursor_agent_*.py",
]

_REMAINING_CASCADE = re.compile(
    r"\bCascade\b(?![/\w])"  # word Cursor Agent not followed by / (L2/cascade)
)


def _should_skip(path: Path) -> bool:
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return True
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    return False


def _rewrite_text(text: str) -> str:
    updated = text
    for old, new in IDENT_REPLACEMENTS:
        updated = updated.replace(old, new)
    for old, new in PROSE_REPLACEMENTS:
        updated = updated.replace(old, new)
    # Residual standalone Cursor Agent -> Cursor Agent (skip L2/cascade paths).
    updated = _REMAINING_CASCADE.sub("Cursor Agent", updated)
    return updated


def _rename_targets() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    seen: set[Path] = set()
    roots = [
        REPO_ROOT / ".cursor",
        REPO_ROOT / "ops_scripts",
        REPO_ROOT / "tests",
        REPO_ROOT / "tools",
        REPO_ROOT / "apps_rg",
        REPO_ROOT / "apps_qna",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".pre-commit-config.yaml",
        REPO_ROOT / ".github",
    ]
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = list(root.rglob("*"))
        for path in candidates:
            if not path.is_file() or _should_skip(path):
                continue
            name = path.name
            new_name = name
            for old, new in IDENT_REPLACEMENTS:
                if old in new_name:
                    new_name = new_name.replace(old, new)
            if new_name != name:
                dest = path.with_name(new_name)
                if dest not in seen and path not in seen:
                    pairs.append((path, dest))
                    seen.add(path)
                    seen.add(dest)
    # Deepest paths first so parent renames do not break children.
    pairs.sort(key=lambda p: len(p[0].parts), reverse=True)
    return pairs


def _iter_content_files() -> list[Path]:
    roots = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".pre-commit-config.yaml",
        REPO_ROOT / ".cursor" / "rules",
        REPO_ROOT / ".cursor" / "plans",
        REPO_ROOT / ".cursor" / "scripts",
        REPO_ROOT / ".cursor" / "skills",
        REPO_ROOT / ".cursor" / "hooks",
        REPO_ROOT / ".cursor" / "schemas",
        REPO_ROOT / "ops_scripts",
        REPO_ROOT / "tests",
        REPO_ROOT / "tools",
        REPO_ROOT / "apps_rg",
        REPO_ROOT / "apps_qna",
        REPO_ROOT / "docs",
        REPO_ROOT / ".github",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if not _should_skip(root):
                files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and not _should_skip(path):
                files.append(path)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    renamed = 0
    for src, dest in _rename_targets():
        if dest.exists() and src.resolve() != dest.resolve():
            print(f"SKIP rename (dest exists): {dest.relative_to(REPO_ROOT)}")
            continue
        print(f"{'DRY-RUN RENAME' if args.dry_run else 'RENAME'}: {src.relative_to(REPO_ROOT)} -> {dest.name}")
        if not args.dry_run:
            src.rename(dest)
        renamed += 1

    changed = 0
    for path in _iter_content_files():
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        updated = _rewrite_text(original)
        if updated == original:
            continue
        changed += 1
        rel = path.relative_to(REPO_ROOT)
        print(f"{'DRY-RUN' if args.dry_run else 'UPDATE'}: {rel}")
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    print(
        f"{'Would rename' if args.dry_run else 'Renamed'} {renamed} file(s); "
        f"{'would update' if args.dry_run else 'updated'} {changed} file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
