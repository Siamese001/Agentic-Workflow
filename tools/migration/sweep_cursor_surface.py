#!/usr/bin/env python3
"""Scan-based .cursor/<surface> -> .claude/<target> sweeper (both path forms).

More thorough than repoint_cursor_surface.py (which only edits map-listed
consumer files): this walks the live trees and rewrites BOTH the literal
``.cursor/<surface>`` form AND the segmented ``".cursor" / "<surface>"`` Python
form (which the literal tool/map miss), across code AND docs (.md/.mdc).

Excludes: .cursor, .claude/plans (the moved content itself), archives, caches,
and a denylist of files that intentionally keep .cursor references.

.py files are py_compile-verified after rewrite; any that fail to compile are
auto-reverted and reported (non-zero exit).

Usage:
    python tools/migration/sweep_cursor_surface.py --surface plans --target plans --dry-run
    python tools/migration/sweep_cursor_surface.py --surface plans --target plans --apply
"""
from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = ["ops_scripts", "tools", "agentic_core", "tests", "config",
              ".claude/rules", ".claude/skills", ".claude/hooks", ".claude/commands"]
SCAN_ROOT_GLOBS = ["apps_*"]
SCAN_FILES = ["CLAUDE.md", "AGENTS.md", ".pre-commit-config.yaml"]

EXCLUDE_PARTS = {".cursor", ".git", "__pycache__", "node_modules", ".windsurf"}
EXCLUDE_PREFIXES = ("docs/archive/", "archives/", ".claude/plans/")
TEXT_EXTS = {".py", ".md", ".mdc", ".json", ".yaml", ".yml", ".toml",
             ".ini", ".sql", ".cfg", ".txt"}

DENYLIST = {
    "agentic_core/L0_routing/config/path_constants.py",
    "tools/migration/cursor_reference_map.py",
    "tools/migration/repoint_cursor_surface.py",
    "tools/migration/sweep_cursor_surface.py",
    "tools/migration/deprecate_windsurf_refs.py",
    "ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py",
    "ops_scripts/maintenance/rewrite_cascade_to_cursor.py",
    "ops_scripts/ci/governance_w2_dedupe_report.py",
    "scripts/governance/verify_codex_backup.py",
    "ops_scripts/ci/check_no_active_windsurf_changes.py",
    "ops_scripts/ci/check_windsurf_deletion_readiness.py",
    "ops_scripts/ci/check_mcp_config_sovereignty.py",
}


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def _excluded(rel: str) -> bool:
    if set(rel.split("/")) & EXCLUDE_PARTS:
        return True
    return rel.startswith(EXCLUDE_PREFIXES)


def _iter_files():
    roots = [REPO_ROOT / r for r in SCAN_ROOTS]
    for g in SCAN_ROOT_GLOBS:
        roots.extend(sorted(REPO_ROOT.glob(g)))
    seen = set()
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in TEXT_EXTS and not _excluded(_rel(p)):
                if p not in seen:
                    seen.add(p)
                    yield p
    for f in SCAN_FILES:
        p = REPO_ROOT / f
        if p.is_file() and p not in seen:
            yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True)
    ap.add_argument("--target", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    literal_old, literal_new = f".cursor/{args.surface}", f".claude/{args.target}"
    seg_old, seg_new = f'".cursor" / "{args.surface}"', f'".claude" / "{args.target}"'

    changed, reverted = [], []
    for p in _iter_files():
        rel = _rel(p)
        if rel in DENYLIST:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if literal_old not in text and seg_old not in text:
            continue
        n = text.count(literal_old) + text.count(seg_old)
        new_text = text.replace(literal_old, literal_new).replace(seg_old, seg_new)
        if args.dry_run:
            changed.append(f"{rel} ({n})")
            continue
        p.write_text(new_text, encoding="utf-8")
        if p.suffix == ".py":
            try:
                py_compile.compile(str(p), doraise=True)
            except py_compile.PyCompileError as exc:
                p.write_text(text, encoding="utf-8")
                reverted.append(f"{rel}: {exc}")
                continue
        changed.append(f"{rel} ({n})")

    verb = "WOULD CHANGE" if args.dry_run else "CHANGED"
    print(f"{literal_old} | {seg_old}  ->  {literal_new} | {seg_new}")
    print(f"{verb}: {len(changed)}  reverted: {len(reverted)}")
    for c in changed:
        print(f"  ~ {c}")
    for r in reverted:
        print(f"  ! {r}")
    return 1 if reverted else 0


if __name__ == "__main__":
    raise SystemExit(main())
