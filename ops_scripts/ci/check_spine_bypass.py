"""
AST-based CI guard: spine bypass + randomness detection.

Scans apps_lic/, apps_rg/, agentic_core/ for:
  A) Banned direct instantiation of spine classes outside allowed adapters.
  B) Randomness usage in deterministic paths.

Uses a baseline file to track pre-existing violations so only NEW violations
fail the build.

Exit codes:
  0 — no new violations
  1 — new violations found
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "spine_bypass_baseline.txt"

# ---------------------------------------------------------------------------
# A) Banned direct instantiation
# ---------------------------------------------------------------------------

BANNED_INSTANTIATION = {
    "HOPPipelineExecutor",
    "ResumeOrchestratorEngine",
    "CIDRegistry",
}

# Files where banned instantiation IS allowed.
INSTANTIATION_ALLOWLIST = {
    PROJECT_ROOT / APPS_LIC_DIR / "engines" / "lic_spine_adapter.py",
    PROJECT_ROOT / APPS_RG_DIR / "engines" / "rg_spine_adapter.py",
}

# ---------------------------------------------------------------------------
# B) Randomness ban
# ---------------------------------------------------------------------------

# Directories where randomness is banned.
RANDOMNESS_BANNED_DIRS = [
    PROJECT_ROOT / APPS_LIC_DIR / "reasoning",
    PROJECT_ROOT / APPS_LIC_DIR / "engines",
    PROJECT_ROOT / APPS_RG_DIR / "reasoning",
    PROJECT_ROOT / APPS_RG_DIR / "engines",
    PROJECT_ROOT / AGENTIC_CORE_DIR,
]

# Scan roots for the full guard.
SCAN_ROOTS = [
    PROJECT_ROOT / APPS_LIC_DIR,
    PROJECT_ROOT / APPS_RG_DIR,
    PROJECT_ROOT / AGENTIC_CORE_DIR,
]

# Directory name segments to exclude from scanning.
EXCLUDE_DIRS = {
    "tests",
    "tools",
    "scripts",
    "artifacts",
    "backups",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def _is_excluded(path: Path) -> bool:
    """Return True if any part of the path is in the exclude set."""
    return bool(set(path.parts) & EXCLUDE_DIRS)


def _in_randomness_banned_dir(path: Path) -> bool:
    """Return True if path is under one of the randomness-banned directories."""
    for banned in RANDOMNESS_BANNED_DIRS:
        try:
            path.relative_to(banned)
            return True
        except ValueError:
            continue
    return False


def collect_python_files() -> list[Path]:
    """Collect all .py files under SCAN_ROOTS, excluding excluded dirs."""
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if not _is_excluded(py_file):
                files.append(py_file)
    return files


# ---------------------------------------------------------------------------
# AST visitors
# ---------------------------------------------------------------------------


class SpineBypassVisitor(ast.NodeVisitor):
    """Detect banned direct instantiation of spine classes (Call nodes only)."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        name = self._resolve_name(node.func)
        if name in BANNED_INSTANTIATION:
            rel = self.file_path.relative_to(PROJECT_ROOT).as_posix()
            self.violations.append(
                f"{rel}:{node.lineno}:spine_bypass:banned direct instantiation of '{name}'"
            )
        self.generic_visit(node)

    @staticmethod
    def _resolve_name(node: ast.expr) -> str:
        """Extract the callable name from Name or Attribute nodes."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""


class RandomnessVisitor(ast.NodeVisitor):
    """Detect randomness usage in deterministic paths (Call nodes only to avoid double-reporting)."""

    # (module, attr) pairs for attribute-chain bans.
    BANNED_ATTR_CHAINS: frozenset[tuple[str, str]] = frozenset(
        {
            ("numpy", "random"),
            ("np", "random"),
            ("uuid", "uuid4"),
            ("datetime", "now"),
            ("datetime", "utcnow"),
            ("random", "random"),
            ("random", "choice"),
            ("random", "randint"),
            ("random", "shuffle"),
            ("random", "sample"),
            ("random", "seed"),
        }
    )

    # Banned bare module names used as callables.
    BANNED_BARE_CALLS = {"random"}

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Only inspect Call nodes to avoid double-reporting attribute accesses."""
        chain = self._resolve_chain(node.func)
        rel = self.file_path.relative_to(PROJECT_ROOT).as_posix()

        if len(chain) == 1 and chain[0] in self.BANNED_BARE_CALLS:
            self.violations.append(f"{rel}:{node.lineno}:randomness:banned randomness call '{chain[0]}()'")
        elif len(chain) >= 2:
            pair = (chain[0], chain[1])
            if pair in self.BANNED_ATTR_CHAINS:
                self.violations.append(
                    f"{rel}:{node.lineno}:randomness:banned randomness call '{'.'.join(chain[:2])}'"
                )
        self.generic_visit(node)

    @staticmethod
    def _resolve_chain(node: ast.expr) -> list[str]:
        """Resolve an Attribute chain or Name to a list of name parts."""
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        parts.reverse()
        return parts


# ---------------------------------------------------------------------------
# Baseline helpers
# ---------------------------------------------------------------------------


def load_baseline() -> set[str]:
    """Load pre-existing violation signatures from baseline file."""
    if not BASELINE_FILE.exists():
        return set()
    try:
        return {
            line.strip() for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()
        }
    except OSError:
        return set()


def write_baseline(violations: list[str]) -> None:
    """Write current violations to baseline (requires env var guard)."""
    if os.environ.get("ALLOW_SPINE_BASELINE_WRITE") != "1":
        print(
            "[ERROR] --write-baseline requires ALLOW_SPINE_BASELINE_WRITE=1 env var",
            file=sys.stderr,
        )
        sys.exit(1)
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(sorted(set(violations))) + "\n"
    BASELINE_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {len(set(violations))} violations to {BASELINE_FILE.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Main scanning logic
# ---------------------------------------------------------------------------


def check_file_instantiation(path: Path) -> list[str]:
    """Check a file for banned spine class instantiation."""
    if path in INSTANTIATION_ALLOWLIST:
        return []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        return [f"{rel}:{exc.lineno}:syntax:SyntaxError: {exc.msg}"]
    visitor = SpineBypassVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def check_file_randomness(path: Path) -> list[str]:
    """Check a file for banned randomness usage."""
    if not _in_randomness_banned_dir(path):
        return []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        return [f"{rel}:{exc.lineno}:syntax:SyntaxError: {exc.msg}"]
    visitor = RandomnessVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    parser = argparse.ArgumentParser(description="AST spine bypass + randomness guard")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current violations to baseline (requires ALLOW_SPINE_BASELINE_WRITE=1)",
    )
    args = parser.parse_args()

    files = collect_python_files()
    all_violations: list[str] = []

    for path in files:
        all_violations.extend(check_file_instantiation(path))
        all_violations.extend(check_file_randomness(path))

    if args.write_baseline:
        write_baseline(all_violations)
        return 0

    baseline = load_baseline()
    current_set = set(all_violations)
    new_violations = sorted(current_set - baseline)

    if not new_violations:
        existing = len(current_set & baseline)
        print(
            f"[OK] Spine bypass + randomness guard: 0 new violations "
            f"({len(files)} files scanned, {existing} baselined)"
        )
        return 0

    print(
        f"[FAIL] Spine bypass + randomness guard: {len(new_violations)} NEW violation(s) "
        f"(out of {len(current_set)} total)\n"
    )
    for v in new_violations:
        print(f"  {v}")
    print(
        "\n[ACTION] Fix violations or run with ALLOW_SPINE_BASELINE_WRITE=1 "
        "--write-baseline to baseline pre-existing debt."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
