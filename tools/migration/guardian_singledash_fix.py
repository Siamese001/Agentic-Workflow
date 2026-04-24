"""Codemod: convert `# guardian: allow-X - reason` (single dash) to canonical
`# guardian: allow-X -- reason` (double dash).

The strict guardian extractor in agentic_core.adg.artifact.multi_writer
requires the `--` separator. 243 sites in production code use a single
`-` and are therefore silently dropped from approved-disposition matching
(sites still RAISE no anti-pattern, but never get auto-approved either).

This script does ONLY the separator fix — it does not invent justifications,
does not change the token, and does not touch lines without an existing
single-dash pattern. Idempotent: running twice is a no-op.

Usage::

    python tools/migration/guardian_singledash_fix.py --dry-run
    python tools/migration/guardian_singledash_fix.py --apply
"""
from __future__ import annotations

import argparse
import py_compile
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOTS = ("agentic_core", "apps_rg", "apps_shared", "apps_lic", "apps_eval",
         "apps_exec", "apps_research", "apps_rfp", "apps_underwriting_ai",
         "tools", "ops_scripts", "system_learning", "infrastructure")

EXCLUDE_PATTERNS = (
    r"(^|[/\\])__pycache__[/\\]",
    r"(^|[/\\])archives?[/\\]",
    r"(^|[/\\])tests[/\\]",
    r"(^|[/\\])tools[/\\]debug[/\\]",
    r"(^|[/\\])tools[/\\]migration[/\\]",
    # The strict extractor file itself — its docstring describes the
    # forbidden pattern; rewriting would falsify the doctrine.
    r"multi_writer\.py$",
)

# Match: '# guardian: allow-FOO - reason...' but NOT '-- reason' or '---'.
# We use a negative lookahead to avoid matching the canonical '--' form.
PATTERN = re.compile(
    r"(#\s*guardian:\s*allow-[A-Za-z0-9_-]+)"  # group 1: comment+token
    r"\s+-\s+"                                 # single ' - ' separator
    r"(?!-)"                                   # NOT followed by another '-'
    r"(\S)",                                   # group 2: first justification char
)

REPLACEMENT = r"\1 -- \2"


def _read_preserve_newlines(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    newline = "\r\n" if b"\r\n" in data else "\n"
    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return text, newline


def _write_preserve_newlines(path: Path, text: str, newline: str) -> None:
    out = text.replace("\n", newline) if newline != "\n" else text
    path.write_bytes(out.encode("utf-8"))


def _process_file(path: Path, dry_run: bool) -> tuple[int, str | None]:
    """Return (sites_fixed, error_message)."""
    text, newline = _read_preserve_newlines(path)
    new_text, n_subs = PATTERN.subn(REPLACEMENT, text)
    if n_subs == 0:
        return 0, None
    if dry_run:
        return n_subs, None

    original = path.read_bytes()
    tmp_dir = Path(tempfile.mkdtemp(prefix="_guardian_dash_"))
    try:
        _write_preserve_newlines(path, new_text, newline)
        cfile = tmp_dir / (path.stem + ".verify.pyc")
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)
    except (py_compile.PyCompileError, SyntaxError, OSError) as exc:
        path.write_bytes(original)
        return 0, f"compile failed, reverted: {exc}"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return n_subs, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        print("must pass --dry-run or --apply", file=sys.stderr)
        return 2

    files_with_hits = 0
    total_sites = 0
    failures: list[tuple[Path, str]] = []
    written: list[Path] = []

    for root in ROOTS:
        rp = Path(root)
        if not rp.exists():
            continue
        for py in rp.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE_PATTERNS):
                continue
            n, err = _process_file(py, args.dry_run)
            if err:
                failures.append((py, err))
                continue
            if n > 0:
                files_with_hits += 1
                total_sites += n
                if args.dry_run:
                    print(f"  (dry-run) would fix {n} site(s) in {py}")
                else:
                    written.append(py)
                    print(f"  WROTE {py}  ({n} site(s))")

    print(
        f"\nresult: files={files_with_hits}, sites={total_sites}, "
        f"written={len(written)}, failures={len(failures)}"
    )
    if failures:
        for fp, err in failures:
            print(f"  FAIL: {fp}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
