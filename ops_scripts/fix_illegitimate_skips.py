"""Automated fixer: convert all illegitimate pytest.skip() / importorskip to
pytest.fail() or delete dead stubs, as classified by classify_skips.py.

Strategy:
  - pytest.skip(msg) → pytest.fail(msg)  for all illegitimate sites
  - pytest.importorskip(pkg) for mandatory deps → raise ImportError assertion
  - "not yet implemented" stubs → comment body with pytest.fail()
  - Legitimate sites (Redis, Playwright, tamper env flag, platform, faiss-gpu)
    are left untouched.

Run from repo root:
    python ops_scripts/fix_illegitimate_skips.py
"""

import ast
import re
from pathlib import Path

ROOT = Path("c:/Git/Agentic-Workflow")
TESTS = ROOT / "tests"

# ── Legitimately optional — DO NOT change these lines ──────────────────────────
LEGITIMATE_REASONS_SUBSTRINGS = [
    # external services
    "redis not running",
    "redis not",
    "playwright not installed",
    "playwright visual tests should be run separately",
    # opt-in env flag negative control
    "ssot_orch_negctrl_tamper",
    "activate tamper",
    # platform
    "read-only directory",
    # conditional hardware (faiss-gpu installed → cpu path not applicable)
    "faiss-gpu",
]

# ── Dead stub reasons — delete the whole test function body ────────────────────
NOT_IMPLEMENTED_SUBSTRINGS = [
    "not yet implemented",
    "method not implemented yet",
]


def is_legitimate(reason: str) -> bool:
    r = reason.lower()
    return any(k in r for k in LEGITIMATE_REASONS_SUBSTRINGS)


def is_not_implemented(reason: str) -> bool:
    r = reason.lower()
    return any(k in r for k in NOT_IMPLEMENTED_SUBSTRINGS)


def fix_file(path: Path) -> tuple[bool, int]:
    """Return (changed, num_fixes) for a single file."""
    original = path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines(keepends=True)

    # Parse to find skip sites with exact line numbers and reasons
    try:
        tree = ast.parse(original)
    except SyntaxError:
        return False, 0

    # Collect (lineno, kind, reason) for illegitimate sites
    illegit_lines: dict[int, tuple[str, str]] = {}  # 1-based lineno → (kind, reason)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func

        # pytest.importorskip
        if isinstance(func, ast.Attribute) and func.attr == "importorskip":
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip("\"'") if rawargs else "missing import"
            illegit_lines[node.lineno] = ("importorskip", reason)

        # pytest.skip(...)
        elif (
            isinstance(func, ast.Attribute)
            and func.attr == "skip"
            and isinstance(func.value, ast.Name)
            and func.value.id == "pytest"
        ):
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip("\"'") if rawargs else ""
            if not is_legitimate(reason):
                kind = "not_implemented" if is_not_implemented(reason) else "skip"
                illegit_lines[node.lineno] = (kind, reason)

    if not illegit_lines:
        return False, 0

    changed = False
    fixes = 0
    new_lines = list(lines)

    for lineno, (kind, reason) in sorted(illegit_lines.items()):
        idx = lineno - 1  # 0-based
        line = new_lines[idx]

        if kind == "importorskip":
            # Replace importorskip with a hard assertion that the module is importable
            # Extract the module name from the line
            m = re.search(r'importorskip\s*\(\s*["\']([^"\']+)["\']', line)
            if m:
                pkg = m.group(1)
                indent = len(line) - len(line.lstrip())
                ind = " " * indent
                new_lines[idx] = (
                    f"{ind}try:\n"
                    f"{ind}    import {pkg}  # noqa: F401\n"
                    f"{ind}except ImportError:\n"
                    f'{ind}    pytest.fail("{pkg} is a mandatory dependency — install it")\n'
                )
                changed = True
                fixes += 1
            continue

        if kind == "not_implemented":
            # Replace the pytest.skip() with pytest.fail() to surface the gap
            new_line = line.replace("pytest.skip(", "pytest.fail(", 1)
            if new_line != line:
                new_lines[idx] = new_line
                changed = True
                fixes += 1
            continue

        # Regular illegitimate skip → fail
        new_line = line.replace("pytest.skip(", "pytest.fail(", 1)
        if new_line != line:
            new_lines[idx] = new_line
            changed = True
            fixes += 1

    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")

    return changed, fixes


def main() -> None:
    total_files = 0
    total_fixes = 0

    for path in sorted(TESTS.rglob("test_*.py")):
        changed, fixes = fix_file(path)
        if changed:
            rel = path.relative_to(ROOT)
            print(f"  FIXED {fixes:3d} site(s)  {rel}")
            total_files += 1
            total_fixes += fixes

    print(f"\nDONE: {total_fixes} fixes across {total_files} files")


if __name__ == "__main__":
    main()
