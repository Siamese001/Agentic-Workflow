"""Wave 2 — replace duplicate magic-constant definitions with imports from SSOT.

SSOT: apps_shared/config/pipeline_constants_config.py
Targets: BATCH_SIZE, BUFFER_SIZE, THRESHOLD, MAX_RETRIES, DEFAULT_SLEEP,
         MAX_DEPTH, MAX_FILES, DEFAULT_TIMEOUT

For each Python file with a top-level literal assignment matching the canonical
value, this script:
  1. Removes the literal assignment line
  2. Inserts an import from the SSOT (if not already present)

Files with outlier values are SKIPPED — those need rename-to-disambiguate
(separate manual pass).

Run with --dry-run to preview; --apply to write changes.
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(".")
SSOT_MODULE = "apps_shared.config.pipeline_constants_config"

# Canonical values — only replace when the file's value matches
CANONICAL = {
    "BATCH_SIZE": "32",
    "BUFFER_SIZE": "8192",
    "THRESHOLD": "0.95",
    "MAX_RETRIES": "3",
    "DEFAULT_SLEEP": "1.0",
    "MAX_DEPTH": "6",
    "MAX_FILES": "1000",
    "DEFAULT_TIMEOUT": "300",
}

# Don't touch the SSOT itself or files that already use it
SKIP_FILES = {
    Path("apps_shared/config/pipeline_constants_config.py"),
    Path("apps_shared/utils/open_telemetry_tracing_adapter_util.py"),
}

# Skip these directories entirely
SKIP_DIRS = ("archives", "tools/archive", "tests", "tools/analysis", "_smoke_v1_coerce_e9aa09")

ROOTS = ["agentic_core", "apps_eval", "apps_exec", "apps_lic", "apps_research",
         "system_learning"]


def find_target_files() -> list[tuple[Path, list[str]]]:
    """Return list of (path, constants_in_file_with_canonical_value)."""
    out: list[tuple[Path, list[str]]] = []
    for root in ROOTS:
        rp = REPO / root
        if not rp.exists():
            continue
        for py in rp.rglob("*.py"):
            try:
                # Use forward-slash repo-relative path for SKIP_DIRS check
                rel = py.relative_to(REPO).as_posix()
            except ValueError:
                continue
            if any(rel.startswith(d) for d in SKIP_DIRS):
                continue
            rel_path = py.relative_to(REPO)
            if rel_path in SKIP_FILES:
                continue
            try:
                text = py.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            matched = []
            for c, val in CANONICAL.items():
                # Top-level assignment, possibly with type annotation: NAME[: type] = value
                pat = rf"^{c}\s*(?::\s*[A-Za-z_][\w\[\], ]*)?\s*=\s*{re.escape(val)}\s*(?:#[^\n]*)?$"
                if re.search(pat, text, re.MULTILINE):
                    matched.append(c)
            if matched:
                out.append((py, matched))
    return out


def transform_file(path: Path, constants: list[str]) -> tuple[str, str]:
    """Return (old_text, new_text). Does not write."""
    text = path.read_text(encoding="utf-8")
    new_text = text

    # Step 1: remove literal assignment lines (top-level only)
    for c in constants:
        val = CANONICAL[c]
        pat = rf"^{c}\s*(?::\s*[A-Za-z_][\w\[\], ]*)?\s*=\s*{re.escape(val)}\s*(?:#[^\n]*)?\n"
        new_text = re.sub(pat, "", new_text, flags=re.MULTILINE)

    # Step 2: add import. Use single import line for all constants.
    # If a similar import exists, augment it; otherwise insert near other imports.
    needed = list(constants)
    # Check existing import line
    existing_import = re.search(
        rf"^from {re.escape(SSOT_MODULE)} import (.+)$",
        new_text, re.MULTILINE,
    )
    if existing_import:
        already = [s.strip() for s in existing_import.group(1).split(",")]
        merged = sorted(set(already) | set(needed))
        new_line = f"from {SSOT_MODULE} import " + ", ".join(merged)
        new_text = (new_text[:existing_import.start()] + new_line +
                    new_text[existing_import.end():])
    else:
        import_line = f"from {SSOT_MODULE} import " + ", ".join(sorted(needed))
        # Insert after the last top-level import block.
        # Tracks: docstring presence, multi-line `from X import (...)` paren depth.
        lines = new_text.splitlines(keepends=True)
        insert_idx = 0
        in_docstring = False
        docstring_quote = None
        paren_depth = 0
        for i, line in enumerate(lines):
            stripped = line.strip()

            # If we're mid-paren, just keep advancing insert_idx and updating depth
            if paren_depth > 0:
                paren_depth += line.count("(") - line.count(")")
                if paren_depth <= 0:
                    paren_depth = 0
                    insert_idx = i + 1
                continue

            # Module docstring tracking
            if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                quote = stripped[:3]
                if stripped.count(quote) >= 2 and len(stripped) > 3:
                    insert_idx = i + 1
                    continue
                in_docstring = True
                docstring_quote = quote
                continue
            if in_docstring:
                if docstring_quote in stripped:
                    in_docstring = False
                    insert_idx = i + 1
                continue

            if stripped.startswith("from __future__"):
                insert_idx = i + 1
                continue
            if stripped.startswith("import ") or stripped.startswith("from "):
                # Could open a multi-line `from X import (`
                opens = line.count("(") - line.count(")")
                if opens > 0:
                    paren_depth = opens
                    # don't bump insert_idx yet — wait for matching close
                    continue
                insert_idx = i + 1
                continue
            if not stripped or stripped.startswith("#"):
                continue
            break
        lines.insert(insert_idx, import_line + "\n")
        new_text = "".join(lines)

    return text, new_text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes")
    ap.add_argument("--limit", type=int, default=0, help="limit files processed")
    ap.add_argument("--verify", action="store_true", help="run py_compile on changed files")
    args = ap.parse_args()

    targets = find_target_files()
    if args.limit:
        targets = targets[:args.limit]

    print(f"Found {len(targets)} target files")
    total_const_removals = sum(len(c) for _, c in targets)
    print(f"Total constant-line removals planned: {total_const_removals}")

    if not args.apply:
        print("\nSample targets:")
        for path, consts in targets[:15]:
            print(f"  {path}  remove={consts}")
        if len(targets) > 15:
            print(f"  ... and {len(targets) - 15} more")
        print("\nDRY RUN — pass --apply to write changes")
        return 0

    changed: list[Path] = []
    failed: list[tuple[Path, str]] = []
    for path, consts in targets:
        try:
            old, new = transform_file(path, consts)
            if old == new:
                continue
            path.write_text(new, encoding="utf-8")
            changed.append(path)
        except (OSError, ValueError) as e:
            failed.append((path, str(e)))

    print(f"\nWrote {len(changed)} files")
    print(f"Failed: {len(failed)}")
    for p, e in failed[:5]:
        print(f"  FAIL {p}: {e}")

    if args.verify and changed:
        print(f"\nRunning py_compile on {len(changed)} changed files...")
        compile_failed = []
        for path in changed:
            r = subprocess.run(
                [sys.executable, "-m", "py_compile", str(path)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                compile_failed.append((path, r.stderr.strip()))
        print(f"py_compile failures: {len(compile_failed)}")
        for p, e in compile_failed[:10]:
            print(f"  FAIL {p}: {e[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
