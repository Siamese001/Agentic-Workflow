#!/usr/bin/env python3
"""legacy editor-decommission reference reporter (read-only).

Scans live repo trees for `.cursor/` references and classifies each line into:

  * runtime_read      — actual filesystem access (open/Path/glob/sqlite/args).
  * literal_path_ref  — a quoted ".cursor/<x>" path literal in CODE/CONFIG
                        (sets, dicts, registries, ingestion manifests, error
                        strings). These do NOT match open()/Path() idioms but a
                        consumer still depends on the path string, so the
                        surface cannot be deleted until they are repointed.
  * mention           — comments, prose, markdown citations (cosmetic; W6).

The first two categories are the ACTIONABLE consumer set for a wave: every
runtime_read + literal_path_ref must be repointed before the corresponding
`.cursor` surface can be git-rm'd. (v1 of this reporter only had runtime_read
and undercounted the rules/skills consumer set by ~7x — literal_path_ref closes
that gap.)

This is a REPORTER, not a codemod — it never edits files. Rewriting is done by
tools/migration/ssot_path_literal_migrator.py (exact) and ssot_prefix_path_migrator.py
(prefix) against the CURSOR_*/CLAUDE_* constants in
agentic_core/L0_routing/config/path_constants.py.

Usage:
    python tools/migration/cursor_reference_map.py
    python tools/migration/cursor_reference_map.py --out artifacts/migration/cursor_reference_map.json
    python tools/migration/cursor_reference_map.py --surface rules,skills,workflows,agents
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = [
    "tools", "ops_scripts", "agentic_core", "tests", "config", "scripts", ".claude",
]
SCAN_ROOT_GLOBS = ["apps_*"]
SCAN_FILES = [".pre-commit-config.yaml", "CLAUDE.md", "AGENTS.md"]

EXCLUDE_PARTS = {".cursor", ".git", "__pycache__", "node_modules", ".windsurf"}
EXCLUDE_PREFIXES = ("docs/archive/", "archives/")
TEXT_EXTS = {".py", ".md", ".mdc", ".txt", ".json", ".yaml", ".yml", ".toml",
             ".ini", ".sql", ".marker", ".cfg"}
# literal_path_ref only makes sense in code/config — markdown/txt = doc mention.
CODE_EXTS = {".py", ".json", ".yaml", ".yml", ".toml", ".ini", ".sql", ".cfg"}

CURSOR_RE = re.compile(r"\.cursor/")
RUNTIME_RE = re.compile(
    r"open\(|Path\(|read_text|read_bytes|write_text|write_bytes|\.glob\(|"
    r"iterdir|scandir|\.exists\(|is_file|is_dir|sqlite3\.connect|joinpath|"
    r"os\.path\.join|json\.load|json\.dump|\.mkdir|makedirs|shutil\.|"
    r"REPO_ROOT|PROJECT|/ ?\"\.cursor|/ ?'\.cursor"
)
COMMENT_RE = re.compile(r"^\s*#")
# A quoted ".cursor/..." path literal: '...', "...", or `...` enclosing a path.
QUOTED_CURSOR_RE = re.compile(r"""['"`][^'"`]*\.cursor/[^'"`]*['"`]""")
# Prose markers — a quoted ".cursor/x" inside an error/help string, not a config path.
PROSE_RE = re.compile(r"\b(See|Rule|Policy|Advisory|per|See:|remediation|details|invariant)\b",
                      re.IGNORECASE)


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def _excluded(rel: str) -> bool:
    if set(rel.split("/")) & EXCLUDE_PARTS:
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
            if _excluded(_rel(p)):
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
    ap.add_argument("--surface", default="",
                    help="comma-separated surfaces (rules,skills,...) to list consumer files for")
    args = ap.parse_args()
    surfaces = {f".cursor/{s.strip()}" for s in args.surface.split(",") if s.strip()}

    files = _iter_files()
    total = len(files)
    runtime_reads: list[dict] = []
    literal_refs: list[dict] = []
    by_subpath: dict[str, dict[str, int]] = {}
    consumer_files: dict[str, set[str]] = {}
    mention_count = 0
    files_with_refs: set[str] = set()

    for idx, p in enumerate(files, 1):
        if idx % 500 == 0 or idx == total:
            pct = int(idx * 100 / total) if total else 100
            print(f"  progress: {pct:3d}% ({idx}/{total})", file=sys.stderr)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if ".cursor/" not in text:
            continue
        rel = _rel(p)
        is_code = p.suffix.lower() in CODE_EXTS
        for lineno, line in enumerate(text.splitlines(), 1):
            if not CURSOR_RE.search(line):
                continue
            files_with_refs.add(rel)
            sub = _subpath(line)
            bucket = by_subpath.setdefault(
                sub, {"runtime_read": 0, "literal_path_ref": 0, "mention": 0})
            is_comment = bool(COMMENT_RE.match(line))
            is_runtime = bool(RUNTIME_RE.search(line)) and not is_comment
            row = {"file": rel, "line": lineno, "subpath": sub, "text": line.strip()[:160]}
            if is_runtime:
                bucket["runtime_read"] += 1
                runtime_reads.append(row)
                consumer_files.setdefault(sub, set()).add(rel)
            elif (is_code and not is_comment and QUOTED_CURSOR_RE.search(line)
                  and not PROSE_RE.search(line)):
                bucket["literal_path_ref"] += 1
                literal_refs.append(row)
                consumer_files.setdefault(sub, set()).add(rel)
            else:
                bucket["mention"] += 1
                mention_count += 1

    actionable = len(runtime_reads) + len(literal_refs)
    report = {
        "generated_for": "cursor-decommission-a1f7c3",
        "scanned_files": total,
        "files_with_cursor_refs": len(files_with_refs),
        "actionable_count": actionable,
        "runtime_read_count": len(runtime_reads),
        "literal_path_ref_count": len(literal_refs),
        "mention_count": mention_count,
        "by_subpath": dict(sorted(
            by_subpath.items(),
            key=lambda kv: -(kv[1]["runtime_read"] + kv[1]["literal_path_ref"]))),
        "consumer_files_by_subpath": {
            k: sorted(v) for k, v in sorted(consumer_files.items())},
        "runtime_reads": sorted(runtime_reads, key=lambda r: (r["subpath"], r["file"], r["line"])),
        "literal_path_refs": sorted(literal_refs, key=lambda r: (r["subpath"], r["file"], r["line"])),
    }

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"scanned_files={total} files_with_refs={len(files_with_refs)} "
          f"actionable={actionable} (runtime={len(runtime_reads)} literal={len(literal_refs)}) "
          f"mentions={mention_count}")
    print("subpath: runtime / literal / mention")
    for sub, c in list(report["by_subpath"].items())[:14]:
        print(f"  {sub:30s} {c['runtime_read']:4d} / {c['literal_path_ref']:4d} / {c['mention']}")
    if surfaces:
        print("\nconsumer files for requested surfaces:")
        for sub in sorted(surfaces):
            cf = report["consumer_files_by_subpath"].get(sub, [])
            print(f"  {sub} -> {len(cf)} files")
            for f in cf:
                print(f"      {f}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
