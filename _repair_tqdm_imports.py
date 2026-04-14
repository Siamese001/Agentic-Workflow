"""
Repair misplaced 'from tqdm import tqdm' lines.

The _fix_progress.py script inserted tqdm imports after the last line
starting with 'from ' / 'import ', which could be inside functions, try
blocks, or continuation lines of multi-line imports. This script moves
them to the correct top-level position.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_SCAN_CMD = """
import ast, sys
from pathlib import Path
root = Path('.')
errors = []
for f in sorted(root.rglob('*.py')):
    if any(p in f.parts for p in ('__pycache__', '.git', 'archives')):
        continue
    try:
        src = f.read_text(encoding='utf-8', errors='ignore')
        ast.parse(src)
    except SyntaxError:
        print(f)
"""

_CHECK_CMD = """
import ast, sys
from pathlib import Path
root = Path('.')
errors = []
for f in sorted(root.rglob('*.py')):
    if any(p in f.parts for p in ('__pycache__', '.git', 'archives')):
        continue
    try:
        src = f.read_text(encoding='utf-8', errors='ignore')
        ast.parse(src)
    except SyntaxError as e:
        errors.append(f'{f}: {e}')
if errors:
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)
else:
    print(f'All {len(list(Path(".").rglob("*.py")))} files OK')
"""


def has_syntax_error(source: str) -> bool:
    try:
        ast.parse(source)
        return False
    except SyntaxError:
        return True


def find_top_level_import_end_line(source: str) -> int:
    """Return 1-indexed line number of the end of the last top-level import."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _fallback_import_end(source)

    last_end = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            end = getattr(node, "end_lineno", node.lineno)
            if end > last_end:
                last_end = end
    return last_end


def _fallback_import_end(source: str) -> int:
    last = 0
    for i, line in enumerate(source.splitlines(), 1):
        if line[0:1] not in (" ", "\t") and line.lstrip().startswith(("from ", "import ", "from __future__")):
            last = i
    return last


def repair_file(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")

    if "from tqdm import tqdm" not in source:
        return False

    lines = source.splitlines(keepends=True)
    misplaced = any(line.lstrip() == "from tqdm import tqdm\n" and line[0:1] in (" ", "\t") for line in lines)
    broken = has_syntax_error(source)

    if not misplaced and not broken:
        return False

    # Remove ALL tqdm import lines
    cleaned_lines = [l for l in lines if l.strip() != "from tqdm import tqdm"]
    cleaned_source = "".join(cleaned_lines)

    # Find correct insert position on cleaned source
    insert_after = find_top_level_import_end_line(cleaned_source)
    if insert_after == 0:
        # No top-level imports — insert before first non-blank non-docstring line
        for i, line in enumerate(cleaned_lines):
            s = line.strip()
            if s and not s.startswith(('"""', "'''", "#")):
                insert_after = i
                break
        else:
            insert_after = len(cleaned_lines)

    new_lines = list(cleaned_lines)
    new_lines.insert(insert_after, "from tqdm import tqdm\n")
    new_source = "".join(new_lines)

    if has_syntax_error(new_source):
        # Fallback: insert right after __future__ import
        fallback_lines = list(cleaned_lines)
        fallback_insert = 0
        for i, line in enumerate(fallback_lines):
            if line.strip().startswith("from __future__"):
                fallback_insert = i + 1
                break
        fallback_lines.insert(fallback_insert, "from tqdm import tqdm\n")
        fallback_source = "".join(fallback_lines)
        if not has_syntax_error(fallback_source):
            new_source = fallback_source
        else:
            print(f"  FAIL (could not repair): {path.relative_to(ROOT)}")
            return False

    path.write_text(new_source, encoding="utf-8")
    return True


def main() -> None:
    print("Scanning for broken files...")
    result = subprocess.run(
        [sys.executable, "-c", _SCAN_CMD],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )

    broken = [Path(p.strip()) for p in result.stdout.splitlines() if p.strip()]
    print(f"Found {len(broken)} broken files\n")

    repaired = 0
    failed: list[str] = []
    for path in broken:
        full = ROOT / path
        if not full.exists():
            continue
        if repair_file(full):
            print(f"  REPAIRED: {path}")
            repaired += 1
        else:
            failed.append(str(path))

    print(f"\nRepaired: {repaired}  Failed: {len(failed)}")
    if failed:
        print("Still broken:")
        for f in failed:
            print(f"  {f}")

    print("\nFinal syntax check...")
    result2 = subprocess.run(
        [sys.executable, "-c", _CHECK_CMD],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # Show last 3000 chars (summaries / errors)
    tail = (result2.stdout + result2.stderr)[-3000:]
    print(tail)
    sys.exit(result2.returncode)


if __name__ == "__main__":
    main()
