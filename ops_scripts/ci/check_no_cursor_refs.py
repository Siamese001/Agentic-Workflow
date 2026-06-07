#!/usr/bin/env python3
"""Anti-regression gate (cursor-decommission W7): keep `.cursor/` decommissioned.

Two checks:
  1. DIRECTORY: no tracked files may live under `.cursor/`. The legacy Cursor tree
     was relocated to `.claude/` (engine -> .claude/governance/scripts, plans ->
     .claude/plans, state/schemas/templates -> .claude/, rules/skills/commands/agents
     are the .claude SSOT). Historical copies live read-only under docs/archive/cursor/.
  2. ACTIVE PATH USE: no live code may CONSTRUCT a `.cursor/` filesystem path
     (Path(".cursor/..."), open(".cursor/..."), `/ ".cursor"`, endswith(".cursor...")).
     Cosmetic mentions in comments/docstrings/markdown/SQL-comments are allowed
     (they reference history; rewriting archived prose adds churn without value).

Exit 0 = clean. Exit 1 = regression (fail-closed by default; this is a ratchet).
Bypass: CHECK_NO_CURSOR_REFS_BYPASS=1.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Active code roots scanned for path-construction. Excludes archives, legacy
# mirrors, plans (historical), and the migration tooling itself.
ACTIVE_GLOBS = ("ops_scripts", "tools", "agentic_core", ".claude/governance",
                ".claude/hooks")
ACTIVE_APP_GLOB = "apps_*"
EXCLUDE_SUBSTR = ("/_legacy_", "/_archive/", "/__pycache__/", "/docs/archive/",
                  "tools/migration/", "tools/cursor/")
# Legacy/self/historical-purpose files that intentionally retain .cursor references
# (one-shot migration tools, the cursor-era RULES_INDEX generator, this gate itself).
DENYLIST_FILES = {
    "ops_scripts/ci/check_no_cursor_refs.py",
    "ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py",
    "ops_scripts/maintenance/rewrite_cascade_to_cursor.py",
    ".claude/governance/scripts/generate_rules_index.py",
    ".claude/governance/scripts/sync_mcp_config.py",  # obsolete MCP-mirror sync (mirror retired)
    "tools/cursor/verify_cursor_author_gate_wiring.py",
}

# A real .cursor/ filesystem path construction (not a comment/docstring mention).
PATH_USE_RE = re.compile(
    r"""(Path\(\s*['"]\.cursor/|"""           # Path(".cursor/...
    r"""open\(\s*['"]\.cursor/|"""             # open(".cursor/...
    r"""/\s*['"]\.cursor['"]|"""               # / ".cursor"
    r"""endswith\(\s*['"]\.cursor/|"""         # endswith(".cursor/...
    r"""\.glob\(\s*['"][^'"]*\.cursor/)"""     # glob("...cursor/...
)
COMMENT_RE = re.compile(r"^\s*(#|--|//|\*)")


def _tracked_cursor_files() -> list[str]:
    # Index (staged) state — reflects the commit being made, so the gate is
    # green on the very commit that removes .cursor (HEAD would still show it).
    out = subprocess.run(
        ["git", "ls-files", ".cursor"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, check=False,
    )
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def _active_path_uses() -> list[str]:
    hits: list[str] = []
    roots = [REPO_ROOT / g for g in ACTIVE_GLOBS]
    roots.extend(sorted(REPO_ROOT.glob(ACTIVE_APP_GLOB)))
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*.py"):
            rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel in DENYLIST_FILES:
                continue
            if any(s.strip("/") in f"/{rel}/" or rel.startswith(s.lstrip("/")) for s in EXCLUDE_SUBSTR):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if ".cursor/" not in text:
                continue
            for n, line in enumerate(text.splitlines(), 1):
                if COMMENT_RE.match(line):
                    continue
                if PATH_USE_RE.search(line):
                    hits.append(f"{rel}:{n}: {line.strip()[:120]}")
    return hits


def main() -> int:
    if os.environ.get("CHECK_NO_CURSOR_REFS_BYPASS") == "1":
        print("[no-cursor-refs] bypassed", file=sys.stderr)
        return 0
    tracked = _tracked_cursor_files()
    active = _active_path_uses()
    if not tracked and not active:
        print("[no-cursor-refs] OK — .cursor/ decommissioned; no active path use")
        return 0
    if tracked:
        print(f"[no-cursor-refs] FAIL — {len(tracked)} tracked file(s) under .cursor/:", file=sys.stderr)
        for f in tracked[:20]:
            print(f"  {f}", file=sys.stderr)
    if active:
        print(f"[no-cursor-refs] FAIL — {len(active)} active .cursor/ path construction(s):", file=sys.stderr)
        for h in active[:20]:
            print(f"  {h}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
