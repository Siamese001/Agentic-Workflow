"""
Terminal/Subprocess Cleanup CI Gate — Constitutional Rule §11.

Enforces terminal process lifecycle management by catching static patterns
that commonly leak processes:

  1. `subprocess.Popen(...)` without `.wait()`, `.terminate()`, `.kill()`,
     or context manager (`with subprocess.Popen(...) as proc:`)
  2. `subprocess.run(...)` without `timeout=` kwarg (also enforced by §14)
  3. `os.system(...)` — always unbounded; never acceptable
  4. `os.popen(...)` — deprecated, leaks stdio pipes

Constitutional §11 references this gate. Before today it didn't exist;
the rule was making an implicit promise. This gate provides static enforcement
of the subset of terminal-lifecycle concerns that ARE observable at commit time.
Runtime concerns (zombie reaping, orphan process groups) remain the T2 rule's
responsibility — pre-commit can't enforce runtime behavior.

Exit codes:
    0  — all checks passed
    1  — violations found

Usage:
    python ops_scripts/ci/check_terminal_cleanup.py [--verbose] [--staged] [file ...]

Guardian exemption:
    # guardian: allow-popen-leak -- <specific justification>
    on the line where subprocess.Popen / os.system is called, to acknowledge
    a deliberate long-lived process (e.g., a daemon spawner).
"""

from __future__ import annotations

import argparse
import ast
import subprocess  # noqa: S404 -- this file audits subprocess usage, so import is required
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

_SCAN_DIRS = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_shared",
    "apps_underwriting_ai",
    "ops_scripts",
    "tools",
    "system_learning",
    ".windsurf/scripts",
]

_SKIP_PATTERNS = (
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "archives",
    "archive",
    ".git",
    "node_modules",
    "tests",  # test-side terminal patterns are acceptable; tests often spawn+kill
)

_GUARDIAN_MARKERS = (
    "guardian: allow-popen-leak",
    "guardian: allow-terminal-leak",
    "guardian: allow-unbounded-subprocess",
)

# Stdlib functions that spawn unbounded processes — always flagged
_BANNED_CALLS: dict[tuple[str, str], str] = {
    ("os", "system"): (
        "os.system() cannot be bounded or reaped; use subprocess.run(argv, "
        "shell=False, timeout=N)"
    ),
    ("os", "popen"): (
        "os.popen() is deprecated and leaks stdio pipes; use subprocess.run"
    ),
}

# subprocess.Popen requires .wait() / .terminate() / .kill() / context manager
# somewhere in the enclosing function. We check structural patterns, not data flow.
_POPEN_CLEANUP_METHODS = ("wait", "terminate", "kill", "communicate", "__exit__")


class Violation:
    """A detected terminal-cleanup compliance violation."""

    def __init__(self, path: Path, lineno: int, message: str) -> None:
        self.path = path
        self.lineno = lineno
        self.message = message

    def __str__(self) -> str:
        try:
            rel = self.path.relative_to(_ROOT)
        except ValueError:
            rel = self.path
        return f"{rel}:{self.lineno}: {self.message}"


def _should_skip(path: Path) -> bool:
    parts = path.parts
    return any(skip in parts for skip in _SKIP_PATTERNS)


def _line_has_guardian(source_lines: list[str], lineno: int) -> bool:
    """Check line itself plus the line above for a guardian marker."""
    for offset in (0, -1):
        idx = lineno - 1 + offset
        if 0 <= idx < len(source_lines):
            line = source_lines[idx].lower()
            if any(marker in line for marker in _GUARDIAN_MARKERS):
                return True
    return False


def _qualified_name(node: ast.Attribute | ast.Name) -> tuple[str, str] | None:
    """Return (module, attr) for patterns like os.system or subprocess.Popen."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return (node.value.id, node.attr)
    return None


def _is_subprocess_popen(call: ast.Call) -> bool:
    q = _qualified_name(call.func) if isinstance(call.func, ast.Attribute) else None
    return q == ("subprocess", "Popen")


def _is_subprocess_run(call: ast.Call) -> bool:
    q = _qualified_name(call.func) if isinstance(call.func, ast.Attribute) else None
    return q == ("subprocess", "run")


def _is_banned_call(call: ast.Call) -> tuple[str, str] | None:
    if isinstance(call.func, ast.Attribute):
        q = _qualified_name(call.func)
        if q in _BANNED_CALLS:
            return q
    return None


def _call_has_timeout_kwarg(call: ast.Call) -> bool:
    return any(kw.arg == "timeout" for kw in call.keywords)


def _popen_is_in_with_block(call: ast.Call, tree: ast.AST) -> bool:
    """Check if this Popen call is the context-manager target of a `with` block."""
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            for item in node.items:
                if item.context_expr is call:
                    return True
    return False


def _popen_has_cleanup_in_enclosing_function(call: ast.Call, tree: ast.AST) -> bool:
    """
    Heuristic: if .wait / .terminate / .kill / .communicate is called on ANY
    variable in the enclosing function body, treat it as cleaned up.

    This is intentionally permissive — we want to catch the obvious leaks
    (Popen assigned to a var that nobody calls wait on), not chase dataflow.
    """
    # Find enclosing function
    enclosing: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Is the call somewhere inside this function?
            for sub in ast.walk(node):
                if sub is call:
                    enclosing = node
                    break
        if enclosing is not None:
            break
    if enclosing is None:
        return False
    # Scan for cleanup method calls anywhere in the function
    for sub in ast.walk(enclosing):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr in _POPEN_CLEANUP_METHODS:
                return True
    return False


def check_file(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations
    source_lines = source.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # Check 1 & 2: banned os.system / os.popen
        banned = _is_banned_call(node)
        if banned is not None:
            if _line_has_guardian(source_lines, node.lineno):
                continue
            module, attr = banned
            violations.append(
                Violation(
                    path,
                    node.lineno,
                    f"{module}.{attr}(): {_BANNED_CALLS[banned]}",
                )
            )
            continue

        # Check 3: subprocess.Popen without cleanup
        if _is_subprocess_popen(node):
            if _line_has_guardian(source_lines, node.lineno):
                continue
            if _popen_is_in_with_block(node, tree):
                continue
            if _popen_has_cleanup_in_enclosing_function(node, tree):
                continue
            violations.append(
                Violation(
                    path,
                    node.lineno,
                    "subprocess.Popen without .wait/.terminate/.kill/"
                    ".communicate or `with` context — will leak process on error",
                )
            )
            continue

        # Check 4: subprocess.run without timeout (also enforced by §14 but
        # reiterating here since terminal cleanup requires bounded runtime)
        if _is_subprocess_run(node):
            if _line_has_guardian(source_lines, node.lineno):
                continue
            if _call_has_timeout_kwarg(node):
                continue
            violations.append(
                Violation(
                    path,
                    node.lineno,
                    "subprocess.run without timeout= kwarg — unbounded runtime "
                    "(constitutional §14)",
                )
            )

    return violations


def collect_repo_files() -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for rel in _SCAN_DIRS:
        root = _ROOT / rel
        if not root.is_dir():
            continue
        for py_file in root.rglob("*.py"):
            resolved = py_file.resolve()
            if resolved in seen or _should_skip(py_file):
                continue
            seen.add(resolved)
            files.append(py_file)
    return files


def collect_staged_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    files: list[Path] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.endswith(".py"):
            continue
        path = _ROOT / line
        if path.is_file() and not _should_skip(path):
            files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Static check: terminal/subprocess cleanup (Constitutional §11)"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Only scan files staged for commit (for pre-commit hook)",
    )
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.files:
        paths = [p for p in args.files if p.is_file()]
    elif args.staged:
        paths = collect_staged_files()
    else:
        paths = collect_repo_files()

    if not paths:
        if args.verbose:
            print("[check_terminal_cleanup] no Python files to scan")
        return 0

    all_violations: list[Violation] = []
    for path in paths:
        all_violations.extend(check_file(path))

    if all_violations:
        print(
            f"[check_terminal_cleanup] {len(all_violations)} violation(s) "
            f"across {len({v.path for v in all_violations})} file(s):"
        )
        for v in all_violations:
            print(f"  {v}")
        print()
        print(
            "Fix: use `with subprocess.Popen(...) as p:`, add "
            "`timeout=` to subprocess.run, or replace os.system with subprocess.run."
        )
        print(
            "Guardian exemption (rare): add `# guardian: allow-popen-leak -- "
            "<reason>` on the call line."
        )
        return 1

    if args.verbose:
        print(
            f"[check_terminal_cleanup] OK: scanned {len(paths)} files, "
            f"no violations"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
