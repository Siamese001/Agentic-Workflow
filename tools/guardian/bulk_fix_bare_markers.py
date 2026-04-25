"""Bulk-fix CLI for W17.b-tail — guardian marker hygiene.

Option B (selected via Author-Gate 2026-04-24):
- Accepts short-form `# guardian: allow-X` and long-form
  `# guardian: allow-X -- justification` as canonical (rule doc updated).
- Renames bare `# guardian: <prose>` (where <prose> does NOT start with `allow-`)
  to `# review: <prose>` because those are review-notes, not exemption directives.
- Excludes `tools/silent_swallower_report.json` from scan (report artifact,
  not source).

Usage::

    python tools/guardian/bulk_fix_bare_markers.py --dry-run       # preview
    python tools/guardian/bulk_fix_bare_markers.py --apply         # execute
    python tools/guardian/bulk_fix_bare_markers.py --verify        # post-check

Rollback: git revert the apply commit. All edits are comment-prefix-only; no
code behavior changes.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


# Matches any `# guardian: <rest>` comment. Bare vs. exemption is classified
# in Python (not via regex lookahead) to avoid the backtracking trap where
# `\s*` gives back zero characters to satisfy a negative lookahead against a
# non-space character. See dev note in module docstring / W17.b-tail 2026-04-24.
_ANY_GUARDIAN_RE = re.compile(r"(?P<prefix>#[ \t]*)guardian:(?P<body>.*)$")

EXCLUDE_PATH_SEGMENTS: tuple[str, ...] = (
    "archives/",
    "docs/",
    "tools/archive/",
    "tools/silent_swallower_report.json",  # W17.b-tail: report artifact
    ".backup/",
    "_backup",
)


@dataclass
class FileEdit:
    """Represents a single file's bare→review rewrite."""

    path: Path
    count: int
    preview: list[str]


def _is_prod_path(path: str) -> bool:
    """Return True if ``path`` is production source (not a report/archive)."""
    lowered = path.replace("\\", "/").lower()
    return not any(token in lowered for token in EXCLUDE_PATH_SEGMENTS)


def _discover_candidates() -> list[Path]:
    """Return the list of .py files containing bare `# guardian:` markers."""
    result = subprocess.run(
        ["git", "grep", "-lE", "# guardian:"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    candidates: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.endswith(".py"):
            continue
        if not _is_prod_path(line):
            continue
        candidates.append(Path(line))
    return candidates


def _is_bare_marker(body: str) -> bool:
    """Return True iff ``body`` (text after ``# guardian:``) is a review-note.

    A review-note body does NOT start with ``allow-`` (after stripping leading
    whitespace). Exemption directives use ``allow-<token>`` with optional
    ``-- <justification>`` suffix.
    """
    stripped = body.lstrip()
    return not stripped.startswith("allow-")


def _rewrite_file(path: Path, apply: bool) -> FileEdit:
    """Rewrite bare `# guardian:` to `# review:` in ``path``.

    Classifies per-line via :func:`_is_bare_marker`. Long-form and short-form
    exemption directives (``allow-*``) are left untouched. Review-notes
    (anything else after ``# guardian:``) are rewritten to ``# review:`` with
    the body preserved verbatim.

    Returns a :class:`FileEdit` with count and up to 3 preview lines. When
    ``apply`` is False, the file is not modified.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return FileEdit(path=path, count=0, preview=[])
    preview: list[str] = []
    count = 0
    new_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        match = _ANY_GUARDIAN_RE.search(line.rstrip("\r\n"))
        if match is None or not _is_bare_marker(match.group("body")):
            new_lines.append(line)
            continue
        # Rewrite the guardian: prefix of this line to review:
        prefix = match.group("prefix")
        body = match.group("body")
        old_segment = f"{prefix}guardian:{body}"
        new_segment = f"{prefix}review:{body}"
        new_line = line.replace(old_segment, new_segment, 1)
        count += 1
        if len(preview) < 3:
            preview.append(f"{old_segment.strip()}  ->  {new_segment.strip()}")
        new_lines.append(new_line)
    new_text = "".join(new_lines)
    if count > 0 and apply and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return FileEdit(path=path, count=count, preview=preview)


def run(apply: bool) -> int:
    candidates = _discover_candidates()
    edits: list[FileEdit] = []
    for path in candidates:
        edit = _rewrite_file(path, apply=apply)
        if edit.count > 0:
            edits.append(edit)
    total_sites = sum(e.count for e in edits)
    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[{mode}] bare `# guardian:` -> `# review:` rewrites")
    print(f"[{mode}] files with edits: {len(edits)}   total sites: {total_sites}")
    print(f"[{mode}] excluded segments: {', '.join(EXCLUDE_PATH_SEGMENTS)}")
    print()
    for edit in edits[:20]:
        print(f"  {edit.count:4d}  {edit.path}")
        for preview_line in edit.preview:
            print(f"         {preview_line[:180]}")
    if len(edits) > 20:
        print(f"  ...  ({len(edits) - 20} more files)")
    return 0 if total_sites >= 0 else 1


def verify() -> int:
    """Post-apply: confirm zero remaining bare `# guardian:` in prod."""
    result = subprocess.run(
        ["git", "grep", "-En", "# guardian:"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    bare = 0
    for line in result.stdout.splitlines():
        path = line.split(":", 1)[0]
        if not path.endswith(".py"):
            continue
        if not _is_prod_path(path):
            continue
        match = re.search(r"# guardian:\s*(.*)", line)
        if match and not match.group(1).strip().startswith("allow-"):
            bare += 1
    print(f"[VERIFY] remaining bare `# guardian:` in prod .py files: {bare}")
    return 0 if bare == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="preview changes, write nothing")
    mode.add_argument("--apply", action="store_true", help="execute rewrites")
    mode.add_argument("--verify", action="store_true", help="post-apply count check")
    args = parser.parse_args(argv)
    if args.verify:
        return verify()
    return run(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
