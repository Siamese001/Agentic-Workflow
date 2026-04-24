"""W6.1-Tooling guardian stamper.

Adds the canonical guardian comment to tooling-layer bare/broad except
handlers that currently lack justification.

Default stamp:
    # guardian: allow-broad-exception -- offline tooling, reports failure

Design:
- AST walk locates ExceptHandler nodes with
  `type=None | Name('Exception') | Name('BaseException')`.
- For each, inspect the source line and adjacent lines for an existing
  `guardian: allow-` token (same regex as coverage check). Skip if present.
- Otherwise append a line-end comment to the `except` line, preserving
  original indentation and any existing trailing comment body.
- Dry-run mode prints per-file diff summary without writing.

Per constitutional §16, runs over 10 files get a progress bar.

Usage:
    python tools/migration/guardian_stamp_tooling.py --scope tools --dry-run
    python tools/migration/guardian_stamp_tooling.py --scope tools --apply
    python tools/migration/guardian_stamp_tooling.py --scope ops_scripts --apply
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

GUARDIAN_RE = re.compile(r"guardian\s*:\s*allow-\S+", re.IGNORECASE)

DEFAULT_STAMP = "guardian: allow-broad-exception -- offline tooling, reports failure"

EXCLUDE_DIR_MARKERS = (
    "__pycache__",
    "/archives/",
    "\\archives\\",
    "/_archive/",
    "\\_archive\\",
    "/tests/",
    "\\tests\\",
)


def _should_skip_dir(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(m.replace("\\", "/") in p for m in EXCLUDE_DIR_MARKERS)


def _iter_py_files(roots: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        rp = Path(root)
        if not rp.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(rp):
            if _should_skip_dir(dirpath):
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    out.append(Path(dirpath) / fn)
    return out


def _target_except_handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    out: list[ast.ExceptHandler] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        t = node.type
        if t is None:
            out.append(node)
        elif isinstance(t, ast.Name) and t.id in ("Exception", "BaseException"):
            out.append(node)
    return out


def _has_guardian_in_window(lines: list[str], ln: int) -> bool:
    start = max(0, ln - 2)
    end = min(len(lines), ln + 1)
    window = " ".join(lines[start:end])
    return bool(GUARDIAN_RE.search(window))


def _stamp_line(line: str, stamp: str) -> str:
    """Return the line with the guardian stamp appended as a comment.

    Preserves existing trailing content / comment by chaining with ' -- '
    when a `#` already exists, or adding a fresh `  # guardian: ...` tail.
    """
    stripped = line.rstrip()
    if not stripped:
        return line
    if "#" in stripped:
        # Append the guardian tail to the existing comment body
        return stripped + "  # " + stamp + "\n"
    return stripped + "  # " + stamp + "\n"


def process_file(
    path: Path, *, dry_run: bool, stamp: str
) -> tuple[int, int, list[str]]:
    """Return (stamped, skipped, diff_lines) for one file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return (0, 0, [])
    lines = text.splitlines(keepends=True)
    if not lines:
        return (0, 0, [])

    handlers = _target_except_handlers(tree)
    if not handlers:
        return (0, 0, [])

    # Work bottom-up so earlier linenos stay stable
    handlers.sort(key=lambda h: h.lineno, reverse=True)
    plain_lines = [ln.rstrip("\r\n") for ln in lines]
    diff_lines: list[str] = []
    stamped = 0
    skipped = 0

    for h in handlers:
        # Find the line that ends the `except` clause (ends with `:`).
        # Walk forward from h.lineno until we hit a line whose non-comment
        # content ends with `:`. This handles both:
        #   except Exception:                  (same line)
        #   except (                           (multi-line)
        #       Exception
        #   ) as e:
        # and the case where a comment sits between `except:` and body.
        target_ln = h.lineno
        end_search = min(len(lines), (h.body[0].lineno if h.body else h.lineno + 3))
        for probe in range(h.lineno - 1, end_search):
            content = plain_lines[probe]
            if "#" in content:
                content = content.split("#", 1)[0]
            if content.rstrip().endswith(":"):
                target_ln = probe + 1
                break
        ln = target_ln - 1  # 0-indexed
        if ln < 0 or ln >= len(lines):
            continue
        if _has_guardian_in_window(plain_lines, target_ln):
            skipped += 1
            continue
        # Extra safety: only stamp lines that end with `:` (the actual clause end).
        # Skip odd cases where we'd be editing mid-expression.
        stripped_check = plain_lines[ln].rstrip()
        # Allow `:` optionally followed by a comment
        if "#" in stripped_check:
            before_hash = stripped_check.split("#", 1)[0].rstrip()
        else:
            before_hash = stripped_check
        if not before_hash.endswith(":"):
            skipped += 1
            continue
        orig = lines[ln]
        new = _stamp_line(orig, stamp)
        if new == orig:
            skipped += 1
            continue
        diff_lines.append(f"  L{h.lineno}: {orig.rstrip()}")
        diff_lines.append(f"  L{h.lineno}+ {new.rstrip()}")
        lines[ln] = new
        # Sync plain_lines so sibling handlers on nearby lines see the update
        plain_lines[ln] = new.rstrip("\r\n")
        stamped += 1

    if stamped > 0 and not dry_run:
        path.write_text("".join(lines), encoding="utf-8")

    return (stamped, skipped, diff_lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument(
        "--scope",
        action="append",
        choices=["tools", "ops_scripts"],
        help="Root directories to scan (repeatable). Default: both.",
    )
    p.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    p.add_argument("--apply", action="store_true", help="Write changes to disk.")
    p.add_argument(
        "--stamp",
        default=DEFAULT_STAMP,
        help=f"Guardian comment body. Default: {DEFAULT_STAMP!r}",
    )
    p.add_argument(
        "--max-diff-lines",
        type=int,
        default=40,
        help="Print up to N per-file diff lines to stdout.",
    )
    args = p.parse_args(argv)

    if not args.dry_run and not args.apply:
        args.dry_run = True

    scopes = args.scope or ["tools", "ops_scripts"]
    files = _iter_py_files(scopes)
    total = len(files)
    print(f"Scanning {total} .py files in: {', '.join(scopes)}")
    if args.dry_run:
        print("Mode: DRY-RUN (no writes)")
    else:
        print("Mode: APPLY (writing changes)")
    print()

    by_layer: Counter[str] = Counter()
    files_touched = 0
    total_stamped = 0
    total_skipped = 0
    first_diff_printed = 0

    try:
        from tqdm import tqdm  # type: ignore[import-not-found]
        iterator = tqdm(files, desc="Stamping", unit="file")
    except ImportError:
        iterator = files

    for i, fp in enumerate(iterator, 1):
        stamped, skipped, diff = process_file(fp, dry_run=args.dry_run, stamp=args.stamp)
        if stamped:
            files_touched += 1
            total_stamped += stamped
            layer = "L_TOOLS" if str(fp).replace("\\", "/").startswith("tools/") else "L_OPS"
            by_layer[layer] += stamped
            if first_diff_printed < args.max_diff_lines and diff:
                for ln in diff[:8]:
                    print(ln)
                    first_diff_printed += 1
                print(f"  -- {fp.as_posix()}")
        total_skipped += skipped

    print()
    print(f"Files touched: {files_touched}/{total}")
    print(f"Total stamped: {total_stamped}")
    print(f"Total skipped (already covered): {total_skipped}")
    print()
    print("Stamped by layer:")
    for lay, n in by_layer.most_common():
        print(f"  {n:>5}  {lay}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
