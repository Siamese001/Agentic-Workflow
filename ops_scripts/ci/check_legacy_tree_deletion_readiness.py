#!/usr/bin/env python3
"""Assess whether full ``.windsurf/`` tree deletion is CI-safe.

Does NOT delete anything. Emits a JSON report of required mirror paths and exits:
  0 — readiness assessment complete (deletion may still be blocked)
  1 — fail-closed and blockers present

Report: artifacts/governance/windsurf_deletion_readiness.json
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "artifacts" / "governance" / "windsurf_deletion_readiness.json"

TEXT_EXTS = {
    ".md",
    ".mdc",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".txt",
    ".sql",
}
SCAN_ROOTS = (
    "AGENTS.md",
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
ALLOW_PREFIXES = (
    ".claude/plans/_archive/",
    ".cursor/windsurf_compat/",
    ".windsurf/",
    "docs/archive/windsurf/",
)
ALLOW_FILES = {
    "ops_scripts/ci/check_no_active_legacy_surface_changes.py",
    "ops_scripts/ci/check_legacy_tree_deletion_readiness.py",
    "tools/migration/deprecate_legacy_refs.py",
}
LOCAL_WINDSURF_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])\.windsurf(?=[$/\\\"' )},\]])")


def _iter_scan_files() -> list[Path]:
    out: list[Path] = []
    for rel in SCAN_ROOTS:
        root = REPO_ROOT / rel
        if root.is_file():
            out.append(root)
        elif root.is_dir():
            out.extend(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_EXTS)
    return out


def _is_allowed_rel(rel: str) -> bool:
    if rel in ALLOW_FILES:
        return True
    return rel.startswith(ALLOW_PREFIXES)


def _active_windsurf_references() -> list[str]:
    refs: list[str] = []
    for path in _iter_scan_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if _is_allowed_rel(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if LOCAL_WINDSURF_PATH_RE.search(text) or "artifacts/governance" in text:
            refs.append(rel)
    return sorted(set(refs))


def main() -> int:
    active_refs = _active_windsurf_references()
    blockers = [f"active .windsurf reference: {rel}" for rel in active_refs]

    report = {
        "deletion_safe": not blockers,
        "blockers": blockers,
        "recommendation": (
            "Full .windsurf deletion is safe after blockers are empty and any remaining "
            "references are archive/compatibility-only."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if os.environ.get("WINDSURF_DELETION_READINESS_FAIL_CLOSED") == "1" and blockers:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
