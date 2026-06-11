---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase_01b_ci_spine_guard.md'
original_relative_path: 'phase_01b_ci_spine_guard.md'
source_sha256: 1ce59192a390b36d1deb0287d2e4f5f609d73d6349c67dd6521303d309ac34fe
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 1B: AST Spine Bypass + Randomness CI Guard — Evidence

AST-based CI guard preventing spine bypass and randomness usage in deterministic paths.
Baseline captures 286 pre-existing violations; only NEW violations fail the build.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Commit Hash

d629080f31c77f816658f1892d7471d2945ce949

## Files Changed

- `ops_scripts/ci/check_spine_bypass.py` (created)
- `ops_scripts/hooks/spine_bypass_baseline.txt` (created)
- `.github/workflows/spine-determinism-guard.yml` (created)
- `tools/evidence/phase01b_spine_guard_evidence_runner.py` (created)
- `docs/reports/plans/phase_01b_ci_spine_guard.md` (created)

## Command: python ops_scripts/ci/check_spine_bypass.py

```
Exit code: 0

[OK] Spine bypass + randomness guard: 0 new violations (1183 files scanned, 286 baselined)
```


## Command: git diff --stat

```
Exit code: 0
```


## Command: git diff

```
Exit code: 0
```


## ops_scripts/ci/check_spine_bypass.py (verbatim)

```python
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_FILE = PROJECT_ROOT / "ops_scripts" / "hooks" / "spine_bypass_baseline.txt"

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
    PROJECT_ROOT / "apps_lic" / "engines" / "lic_spine_adapter.py",
    PROJECT_ROOT / "apps_rg" / "engines" / "rg_spine_adapter.py",
}

# ---------------------------------------------------------------------------
# B) Randomness ban
# ---------------------------------------------------------------------------

# Directories where randomness is banned.
RANDOMNESS_BANNED_DIRS = [
    PROJECT_ROOT / "apps_lic" / "reasoning",
    PROJECT_ROOT / "apps_lic" / "engines",
    PROJECT_ROOT / "apps_rg" / "reasoning",
    PROJECT_ROOT / "apps_rg" / "engines",
    PROJECT_ROOT / "agentic_core",
]

# Scan roots for the full guard.
SCAN_ROOTS = [
    PROJECT_ROOT / "apps_lic",
    PROJECT_ROOT / "apps_rg",
    PROJECT_ROOT / "agentic_core",
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
            self.violations.append(
                f"{rel}:{node.lineno}:randomness:banned randomness call '{chain[0]}()'"
            )
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
            line.strip()
            for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
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

```

## .github/workflows/spine-determinism-guard.yml (verbatim)

```yaml
name: Spine Determinism Guard

on:
  push:
  pull_request:

jobs:
  spine-bypass-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run AST spine bypass + randomness guard
        run: python ops_scripts/ci/check_spine_bypass.py

```

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

