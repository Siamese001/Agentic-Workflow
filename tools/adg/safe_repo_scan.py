"""Windows-safe repo file scan for registry consumer resolvers.

``Path.rglob`` can raise ``OSError`` (WinError 1920) on broken junctions such as
``.venv/lib64`` or repo-root ``lib64``. Consumer resolvers in ``agentic_core``
use ``_scan_files``; ``registry_bucket_lift`` patches it to this implementation
before calling ``resolve_all_consumer_edges()``.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        "tests",
        "archives",
        "_archived",
        "venv",
        ".venv",
        "site-packages",
        "lib64",
        "lib",
        "__pycache__",
        ".git",
        "node_modules",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)


def _on_walk_error(_err: OSError) -> None:
    """Ignore directories/files that cannot be accessed (junctions, permissions)."""


def _should_prune_dir(name: str) -> bool:
    if name in _SKIP_DIR_NAMES:
        return True
    if name.startswith(".") and name not in {".codex"}:
        return True
    return False


def safe_scan_files(
    root: Path,
    pattern: str,
    exts: tuple[str, ...] = (".py",),
) -> dict[str, list[int]]:
    """Mirror ``registry_consumer_resolver._scan_files`` without fragile ``rglob``."""
    rx = re.compile(pattern)
    results: dict[str, list[int]] = {}
    root = root.resolve()

    for dirpath, dirnames, filenames in os.walk(
        root, topdown=True, onerror=_on_walk_error
    ):
        dirnames[:] = [d for d in dirnames if not _should_prune_dir(d)]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix not in exts:
                continue
            try:
                rel_parts = p.relative_to(REPO_ROOT).parts
            except ValueError:
                continue
            if any(part in _SKIP_DIR_NAMES for part in rel_parts):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits: list[int] = []
            for line_no, line in enumerate(text.splitlines(), start=1):
                if rx.search(line):
                    hits.append(line_no)
            if hits:
                rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                results[rel] = hits
    return results
