#!/usr/bin/env python3
"""Cursor-decommission reference reporter (read-only).

Scans live repo trees for `.cursor/` references and classifies each as either a
RUNTIME PATH READ/WRITE (must be rewritten before the corresponding `.cursor`
surface can move) or a MENTION (comment/docstring/string that is cosmetic and can
be bulk-rewritten in W6). Emits a JSON map consumed by the cursor-decommission
plan (.claude/plans/cursor-decommission-a1f7c3.md) and re-run in W6 to prove the
sweep reached zero runtime reads.

This is a REPORTER, not a codemod — it never edits files. The actual rewriting is
done by tools/migration/ssot_path_literal_migrator.py (exact) and
ssot_prefix_path_migrator.py (prefix), whose literal->symbol tables the waves
extend with the CURSOR_* constants now defined in
agentic_core/L0_routing/config/path_constants.py.

Usage:
    python tools/migration/cursor_reference_map.py
    python tools/migration/cursor_reference_map.py --out artifacts/migration/cursor_reference_map.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Live trees to scan. `.cursor/` itself, archives, caches, and the windsurf
# archive are excluded — we only care about LIVE references that bind the repo
# to the legacy tree.
SCAN_ROOTS = [
    "tools", "ops_scripts", "agentic_core", "tests", "config", "scripts", ".claude",
]
SCAN_ROOT_GLOBS = ["apps_*"]
SCAN_FILES = [".pre-commit-config.yaml", "CLAUDE.md", "AGENTS.md"]

EXCLUDE_PARTS = {".cursor", ".git", "__pycache__", "node_modules", ".windsurf"}
EXCLUDE_PREFIXES = ("docs/archive/", "archives/")
TEXT_EXTS = {".py", ".md", ".mdc", ".txt", ".json", ".yaml", ".yml", ".toml",
             ".ini", ".sql", ".marker", ".cfg"}

CURSOR_RE = re.compile(r"\.cursor/")
# Idioms that indicate an actual filesystem path read/write at runtime.
RUNTIME_RE = re.compile(
    r"open\(|Path\(|read_text|read_bytes|write_text|write_bytes|\.glob\(|"
    r"iterdir|scandir|\.exists\(|is_file|is_dir|sqlite3\.connect|joinpath|"
    r"os\.path\.join|json\.load|json\.dump|\.mkdir|makedirs|shutil\.|"
    r"REPO_ROOT|PROJECT|/ ?\"\.cursor|/ ?'\.cursor"
)
# Lines that are unambiguously comments/docstring text.
COMMENT_RE = re.compile(r"^\s*#")


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def _excluded(rel: str) -> bool:
    parts = set(rel.split("/"))
    if parts & EXCLUDE_PARTS:
        return True
    return rel.startswith(EXCLUDE_PREFIXES)


def _iter_files() -> list[Path]:
    out: list[Path] = []
    roots = [REPO_ROOT / r for r in SCAN_ROOTS]
    for g in SCAN_ROOT_GLOBS:
        roots.extend(sorted(REPO_ROOT.glob(g)))
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
                continue
            rel = _rel(p)
            if _excluded(rel):
                continue
            out.append(p)
    for f in SCAN_FILES:
        p = REPO_ROOT / f
        if p.is_file():
            out.append(p)
    return out


def _subpath(line: str) -> str:
    m = re.search(r"\.cursor/([a-z_]+)", line)
    return f".cursor/{m.group(1)}" if m else ".cursor/<other>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/migration/cursor_reference_map.json")
    args = ap.parse_args()

    files = _iter_files()
    total = len(files)
    runtime_reads: list[dict] = []
    by_subpath: dict[str, dict[str, int]] = {}
    mention_count = 0
    files_with_refs: set[str] = set()

    for idx, p in enumerate(files, 1):
        if idx % 500 == 0 or idx == total:
            # progress reporting for the long scan loop (constitutional §16)
            pct = int(idx * 100 / total) if total else 100
            print(f"  progress: {pct:3d}% ({idx}/{total})", file=sys.stderr)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if ".cursor/" not in text:
            continue
        rel = _rel(p)
        for lineno, line in enumerate(text.splitlines(), 1):
            if not CURSOR_RE.search(line):
                continue
            files_with_refs.add(rel)
            sub = _subpath(line)
            bucket = by_subpath.setdefault(sub, {"runtime_read": 0, "mention": 0})
            is_runtime = bool(RUNTIME_RE.search(line)) and not COMMENT_RE.match(line)
            if is_runtime:
                bucket["runtime_read"] += 1
                runtime_reads.append({"file": rel, "line": lineno,
                                      "subpath": sub, "text": line.strip()[:160]})
            else:
                bucket["mention"] += 1
                mention_count += 1

    report = {
        "generated_for": "cursor-decommission-a1f7c3",
        "scanned_files": total,
        "files_with_cursor_refs": len(files_with_refs),
        "runtime_read_count": len(runtime_reads),
        "mention_count": mention_count,
        "by_subpath": dict(sorted(by_subpath.items(),
                                  key=lambda kv: -(kv[1]["runtime_read"] + kv[1]["mention"]))),
        "runtime_reads": sorted(runtime_reads, key=lambda r: (r["subpath"], r["file"], r["line"])),
    }

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"scanned_files={total} files_with_refs={len(files_with_refs)} "
          f"runtime_reads={len(runtime_reads)} mentions={mention_count}")
    print("top subpaths (runtime_read / mention):")
    for sub, c in list(report["by_subpath"].items())[:12]:
        print(f"  {sub:32s} {c['runtime_read']:5d} / {c['mention']}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
