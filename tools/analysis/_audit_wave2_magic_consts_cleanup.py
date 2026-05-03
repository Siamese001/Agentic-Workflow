"""Wave 2 — delete dead magic-constants boilerplate block.

Pattern (8 consecutive lines, each matched exactly):

    MAX_RETRIES = 3
    DEFAULT_SLEEP = 1.0
    THRESHOLD = 0.95
    BUFFER_SIZE = 8192
    BATCH_SIZE = 32
    MAX_DEPTH = 6
    MAX_FILES = 1000
    DEFAULT_TIMEOUT = 300[...]

These constants are NEVER read anywhere (verified via grep for external imports).
Their only effect is to pollute the `mv_hotspot_centrality` short-name layer
buckets that drive `check_ssot_magic_constants.py`. Deleting the block reduces
SSOT violations without changing behavior.

Safety invariant: we ONLY rewrite files where the 8 identifiers (`MAX_RETRIES`,
`DEFAULT_SLEEP`, `THRESHOLD`, `BUFFER_SIZE`, `BATCH_SIZE`, `MAX_DEPTH`,
`MAX_FILES`, `DEFAULT_TIMEOUT`) appear EXACTLY once in the file — the block
itself. Any file that references these names elsewhere is skipped.

Separate exclusion list prevents rewriting legitimate BATCH_SIZE usage in
`tools/generate/ingestion/*.py` (per-collection tuning), `tests/_config/common.py`
(real test-wide constant), and archived/tombstoned folders.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BLOCK_NAMES = (
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
)

# The 8-line boilerplate. The trailing DEFAULT_TIMEOUT line varies between
# "300" and "300  # 5 minutes", and some files have a following "# Configuration
# constants" comment. We match flexibly by anchoring on the first 7 lines
# (exact) and allowing the 8th to be either form, optionally followed by
# the trailing comment line.
BLOCK_RE = re.compile(
    r"""
    ^MAX_RETRIES\s*=\s*3\s*\n
    DEFAULT_SLEEP\s*=\s*1\.0\s*\n
    THRESHOLD\s*=\s*0\.95\s*\n
    BUFFER_SIZE\s*=\s*8192\s*\n
    BATCH_SIZE\s*=\s*32\s*\n
    MAX_DEPTH\s*=\s*6\s*\n
    MAX_FILES\s*=\s*1000\s*\n
    DEFAULT_TIMEOUT\s*=\s*300(\s*\#\s*5\s*minutes)?\s*\n
    (\#\s*Configuration\s+constants\s*\n)?
    """,
    re.MULTILINE | re.VERBOSE,
)

EXCLUDE_DIRS = {
    "archives",
    "tools/archive",
    "tools/generate/ingestion",  # legitimate per-collection BATCH_SIZE
    "tools/analysis",  # self-exclusion (this script + siblings)
    ".git",
    ".venv",
    "node_modules",
}

EXCLUDE_FILES = {
    Path("tests/_config/common.py"),  # legitimate BATCH_SIZE = 32
}


def _is_excluded(path: Path) -> bool:
    rel_posix = path.relative_to(REPO_ROOT).as_posix()
    for ex in EXCLUDE_DIRS:
        if rel_posix.startswith(ex + "/") or rel_posix == ex:
            return True
    for ex_file in EXCLUDE_FILES:
        if path.relative_to(REPO_ROOT) == ex_file:
            return True
    return False


def _external_usage_count(text: str, name: str) -> int:
    """Count occurrences of NAME as a standalone identifier, minus the
    single assignment inside the boilerplate block (captured via BLOCK_RE).

    A file where each BLOCK_NAME appears EXACTLY once is safe to trim.
    """
    return len(re.findall(rf"\b{name}\b", text))


def transform(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    if not BLOCK_RE.search(text):
        return None
    # Every block identifier must appear exactly once in the file.
    for name in BLOCK_NAMES:
        if _external_usage_count(text, name) != 1:
            return None
    new_text = BLOCK_RE.sub("", text, count=1)
    return text, new_text


def main() -> int:
    candidates = []
    for path in REPO_ROOT.rglob("*.py"):
        if _is_excluded(path):
            continue
        candidates.append(path)

    changed: list[Path] = []
    skipped_has_external: list[Path] = []
    no_block: list[Path] = []
    for path in candidates:
        result = transform(path)
        if result is None:
            # Either no block or external usage; only report on "has block
            # but external usage" to keep output short.
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if BLOCK_RE.search(text):
                skipped_has_external.append(path)
            else:
                no_block.append(path)
            continue
        _old, new = result
        path.write_text(new, encoding="utf-8")
        changed.append(path)

    print(f"Changed: {len(changed)} files")
    for p in changed:
        print(f"  WROTE {p.relative_to(REPO_ROOT).as_posix()}")
    print()
    print(f"Skipped (block present but external usage): {len(skipped_has_external)}")
    for p in skipped_has_external:
        print(f"  SKIP-EXTERNAL {p.relative_to(REPO_ROOT).as_posix()}")

    # Compile-check every changed file.
    print()
    print(f"Verifying py_compile on {len(changed)} files...")
    fails = 0
    for path in changed:
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            fails += 1
            print(f"  FAIL {path.relative_to(REPO_ROOT).as_posix()}")
            for line in r.stderr.splitlines()[:5]:
                print(f"     {line}")
    print(f"Compile failures: {fails}/{len(changed)}")
    return fails


if __name__ == "__main__":
    sys.exit(main())
