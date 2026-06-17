#!/usr/bin/env python3
"""Rename legacy editor-agent 'cascade' hooks/strings to Codex equivalents.

Codex (legacy editor agent) -> Codex
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
    ("Post-legacy editor-Agent", "Post-legacy editor-Agent"),
    ("Post-cursor-agent", "Post-cursor-agent"),
    ("--cursor-prompts", "--cursor-prompts"),
    ("cursor_prompts", "cursor_prompts"),
    ("cursor-prompts", "cursor-prompts"),
]

PROSE_REPLACEMENTS: list[tuple[str, str]] = [
    ("Codex", "Codex"),
    ("Codex's", "Codex's"),
    ("Codex MUST", "Codex MUST"),
    ("Codex makes", "Codex makes"),
    ("Codex response", "Codex response"),
    ("cursor agent response", "cursor agent response"),
    ("Codex tool-call", "Codex tool-call"),
    ("Codex composed", "Codex composed"),
    ("Event in Codex", "Event in Codex"),
    ("by Codex", "by Codex"),
    ("when Codex", "when Codex"),
    ("if Codex", "if Codex"),
    ("that Codex", "that Codex"),
    ("Codex can", "Codex can"),
    ("Codex is", "Codex is"),
    ("Codex has", "Codex has"),
    ("Codex executed", "Codex executed"),
    ("Codex edited", "Codex edited"),
    ("Codex closes", "Codex closes"),
    ("Codex turn", "Codex turn"),
    ("Codex session", "Codex session"),
    ("Codex violations", "Codex violations"),
    ("Codex violation", "Codex violation"),
    ("Codex at", "Codex at"),
    ("Codex post-", "Codex post-"),
    ("Codex would", "Codex would"),
    ("Codex self-", "Codex self-"),
    ("Codex discussing", "Codex discussing"),
    ("Codex touched", "Codex touched"),
    ("Codex list", "Codex list"),
    ("Codex mis-", "Codex mis-"),
    ("Codex cannot", "Codex cannot"),
    ("legacy editor-Agent-authorable", "legacy editor-Agent-authorable"),
    ("Codex responses", "Codex responses"),
    ("Codex response", "Codex response"),
    ("block Codex", "block Codex"),
    ("never block Codex", "never block Codex"),
    ("help Codex", "help Codex"),
    ("signals Codex", "signals Codex"),
    ("Detects Codex", "Detects Codex"),
    ("Scans Codex", "Scans Codex"),
    ("Reads Codex", "Reads Codex"),
    ("Fires on every Codex", "Fires on every Codex"),
    ("emitted by Codex", "emitted by Codex"),
    ("native Codex tools", "native Codex tools"),
    ("legacy editor/Codex", "legacy editor/Codex"),
    ("Restart legacy editor/Codex", "Restart legacy editor/Codex"),
    ("hang Codex's", "hang Codex's"),
    ("Author: legacy editor", "Author: legacy editor"),
    ("agent_identity=\"Codex\"", "agent_identity=\"Codex\""),
    ("Codex hook", "Codex hook"),
    ("Codex hooks", "Codex hooks"),
    ("Codex turn,", "Codex turn,"),
    ("Codex per", "Codex per"),
    ("from Codex", "from Codex"),
    ("to Codex", "to Codex"),
    ("Codex regression", "Codex regression"),
    ("Codex is regressing", "Codex is regressing"),
    ("did Codex's", "did Codex's"),
    ("Codex wrote", "Codex wrote"),
    ("what Codex wrote", "what Codex wrote"),
    ("Codex executed waves", "Codex executed waves"),
    ("Codex tool-schema", "Codex tool-schema"),
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
    r"\bCascade\b(?![/\w])"  # word Codex not followed by / (L2/cascade)
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
    # Residual standalone Codex -> Codex (skip L2/cascade paths).
    updated = _REMAINING_CASCADE.sub("Codex", updated)
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
