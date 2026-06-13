#!/usr/bin/env python3
"""Anti-regression gate: no imports from archive namespaces in production code.

Constitutional §12 ("No imports from `archives/` in production"). Archived /
superseded code is retained for provenance (SVP §9 archival-over-deletion) but is
**reference-only** — it MUST NOT be imported back into the live product. This gate
scans production roots (``agentic_core/`` + ``apps_*/``) for Python ``import`` /
``from ... import`` statements whose dotted module path contains an archive segment.

Banned: any dotted-path segment equal to ``archive`` or ``archives``. Covers —
  - root ``archives/`` (gitignored, deprecated 2026-04-21 per path_constants.py)
  - ``ops_scripts/archives/`` (OPS_ARCHIVES_DIR)
  - ``tools/archive/``
  - ``apps_*/archives/`` (app-scoped)

Scope note: ``system_learning/`` (named in older doctrine) no longer exists, so the
production surface is ``agentic_core/`` + ``apps_*/``. Static import statements only
(``importlib``/``__import__`` dynamic loads are out of scope, matching the sibling
``check_no_cursor_refs.py``). Files INSIDE archive dirs, tests, ``__pycache__``,
``_legacy_`` and ``migration`` paths are excluded (archived code may import archived code).

Exit 0 = clean. Exit 1 = a production module imports archived code (fail-closed ratchet).
Bypass: ``CHECK_NO_ARCHIVES_IMPORTS_BYPASS=1``.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PROD_ROOTS = ("agentic_core",)
PROD_APP_GLOB = "apps_*"
EXCLUDE_SUBSTR = (
    "/__pycache__/", "/_legacy_", "/_archive/", "/archive/", "/archives/",
    "/tests/", "/migration/",
)
ARCHIVE_SEGMENTS = {"archive", "archives"}

# Matches `from <mod> import ...` (captures mod) or `import <mods>` (captures mods).
_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+(?P<from>[.\w]+)\s+import\b|import\s+(?P<imp>[.\w][.\w\s,]*))"
)
_COMMENT_RE = re.compile(r"^\s*(?:#|\"\"\"|''')")


def _module_has_archive_segment(dotted: str) -> bool:
    return any(seg in ARCHIVE_SEGMENTS for seg in dotted.strip().split("."))


def _imported_modules(line: str) -> list[str]:
    """Extract the module path(s) an import line pulls in (handles `as` + comma lists)."""
    m = _IMPORT_RE.match(line)
    if not m:
        return []
    if m.group("from"):
        return [m.group("from")]
    out: list[str] = []
    for tok in (m.group("imp") or "").split(","):
        tok = tok.strip()
        if tok:
            out.append(tok.split()[0])  # drop ` as alias`
    return out


def _archive_import_hits(root: Path = REPO_ROOT) -> list[str]:
    hits: list[str] = []
    roots = [root / r for r in PROD_ROOTS]
    roots.extend(sorted(root.glob(PROD_APP_GLOB)))
    for base in roots:
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            if any(s in f"/{rel}" for s in EXCLUDE_SUBSTR) or p.name.startswith("test_"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if "archive" not in text:  # fast reject
                continue
            for n, line in enumerate(text.splitlines(), 1):
                if _COMMENT_RE.match(line):
                    continue
                for mod in _imported_modules(line):
                    if _module_has_archive_segment(mod):
                        hits.append(f"{rel}:{n}: {line.strip()[:120]}")
                        break
    return hits


def main() -> int:
    if os.environ.get("CHECK_NO_ARCHIVES_IMPORTS_BYPASS") == "1":
        print("[no-archives-imports] bypassed", file=sys.stderr)
        return 0
    hits = _archive_import_hits()
    if not hits:
        print("[no-archives-imports] OK — no production imports from archive namespaces")
        return 0
    print(
        f"[no-archives-imports] FAIL — {len(hits)} production import(s) from archived code:",
        file=sys.stderr,
    )
    for h in hits[:30]:
        print(f"  {h}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
