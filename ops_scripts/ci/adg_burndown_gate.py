"""
ADG Intelligent Burndown Gate — Pre-Commit Anti-Pattern Ratchet

Enforces a one-way ratchet on anti-pattern counts:
  - Tracks a BUDGET: {file: {category: max_allowed_count}} in a JSON file.
  - On every commit the live scan is compared against the budget.
  - A file+category pair may NEVER exceed its budgeted count.
  - When violations are fixed the budget automatically shrinks to lock in
    progress (count can only go down, never up).
  - Uses ADG dependency graph to surface the highest-ROI files to tackle next.

Ratchet stability: counts per file+category are immune to line-number shifts
that occur when other lines in the same file are edited.

Exit codes:
  0  — budget held or improved (commit allowed)
  1  — budget exceeded (new anti-patterns introduced; commit blocked)

Environment overrides:
  ADG_BURNDOWN_BYPASS=1   — skip gate entirely (emergency; logged to stderr)
  ADG_BURNDOWN_DRY_RUN=1  — report without updating budget file
  ADG_BURNDOWN_INIT=1     — (re)initialise budget from current scan, then exit 0
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap — works as pre-commit hook or direct invocation from repo root.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
)
from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel

PROJECT_ROOT = get_validated_project_root()

# Budget file: {rel_path: {category: max_allowed_count}}
# Stored separately from landmine_baseline.txt — immune to line-number churn.
BUDGET_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "burndown_budget.json"

_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES | {".nox"}
_EXCLUDE_FILE_PATTERNS = ["__dbg_*.py", "**/activate_this.py"]

# ADG artifact — graceful degradation when absent
_ADG_FILE_GRAPH = PROJECT_ROOT / "artifacts" / "adg" / "adg_file_graph_03122026.json"

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Budget = dict[str, dict[str, int]]  # {rel_path: {category: count}}

# ---------------------------------------------------------------------------
# Budget I/O
# ---------------------------------------------------------------------------


def _load_budget() -> Budget:
    if not BUDGET_FILE.exists():
        return {}
    try:
        return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_budget(budget: Budget) -> None:
    """Atomically persist the budget (never called in dry-run mode)."""
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(budget, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(
        dir=str(BUDGET_FILE.parent),
        prefix=".burndown_budget_",
        suffix=".tmp",
    )
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and BUDGET_FILE.exists():
            BUDGET_FILE.unlink()
        Path(tmp).replace(BUDGET_FILE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _budget_total(budget: Budget) -> int:
    return sum(c for cats in budget.values() for c in cats.values())


# ---------------------------------------------------------------------------
# Scan helpers
# ---------------------------------------------------------------------------


def _collect_all_python_files() -> list[Path]:
    return [
        f
        for f in sorted(PROJECT_ROOT.rglob("*.py"))
        if not (set(f.relative_to(PROJECT_ROOT).parts) & _EXCLUDE_DIRS)
        and not any(f.match(pat) for pat in _EXCLUDE_FILE_PATTERNS)
    ]


def _rel(fp) -> str:
    p = Path(fp)
    return p.relative_to(PROJECT_ROOT).as_posix() if p.is_absolute() else p.as_posix()


def _scan_to_counts(violations) -> Budget:
    """Convert violation list → {rel_path: {category: count}}."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for v in violations:
        counts[_rel(v.file_path)][v.category.value] += 1
    return {f: dict(cats) for f, cats in counts.items()}


# ---------------------------------------------------------------------------
# ADG helpers
# ---------------------------------------------------------------------------


def _load_adg_importer_counts() -> dict[str, int]:
    """Returns {rel_path: importer_count} from ADG edges."""
    if not _ADG_FILE_GRAPH.exists():
        return {}
    try:
        adg = json.loads(_ADG_FILE_GRAPH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    counts: dict[str, int] = defaultdict(int)
    for edge in adg.get("edges", []):
        sym = edge.get("sym", "")
        if sym and "." in sym:
            target = "/".join(sym.split(".")[:-1]) + ".py"
            counts[target] += 1
    return dict(counts)


def _adg_fix_priority(
    current: Budget,
    importer_counts: dict[str, int],
) -> list[tuple[str, int, int]]:
    """
    Sort files by (total_violations * importer_count) desc — highest-ROI first.
    Returns [(rel_path, total_violations, importer_count), ...].
    """
    scored = [
        (rel_path, sum(cats.values()), importer_counts.get(rel_path, 0)) for rel_path, cats in current.items()
    ]
    scored.sort(key=lambda x: x[1] * max(x[2], 1), reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def _compute_regressions(budget: Budget, current: Budget) -> list[tuple[str, str, int, int]]:
    """
    Return (rel_path, category, budget_count, actual_count) tuples where
    actual_count > budget_count.
    """
    out = []
    for rel_path, cats in current.items():
        budgeted_file = budget.get(rel_path, {})
        for cat, actual in cats.items():
            allowed = budgeted_file.get(cat, 0)
            if actual > allowed:
                out.append((rel_path, cat, allowed, actual))
    return sorted(out)


def _shrink_budget(budget: Budget, current: Budget) -> tuple[Budget, int]:
    """
    Return (new_budget, reduced_slot_count) where new_budget = min(budget, current)
    for every file+category pair, with zero-count entries removed.
    """
    new_budget: Budget = {}
    reduced = 0
    for rel_path, cats in budget.items():
        current_cats = current.get(rel_path, {})
        new_cats: dict[str, int] = {}
        for cat, budgeted in cats.items():
            actual = current_cats.get(cat, 0)
            new_val = min(budgeted, actual)
            if new_val > 0:
                new_cats[cat] = new_val
            if actual < budgeted:
                reduced += 1
        if new_cats:
            new_budget[rel_path] = new_cats
    return new_budget, reduced


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def _banner(title: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}")


def _show_burndown_status(current: Budget, importer_counts: dict[str, int]) -> None:
    total = sum(c for cats in current.values() for c in cats.values())
    cat_totals: dict[str, int] = defaultdict(int)
    for cats in current.values():
        for cat, cnt in cats.items():
            cat_totals[cat] += cnt

    print(f"\n[BURNDOWN STATUS] {total} violation(s) remaining")
    for cat, cnt in sorted(cat_totals.items(), key=lambda x: -x[1]):
        print(f"  {cnt:4d}  {cat}")

    priority = _adg_fix_priority(current, importer_counts)
    if priority:
        print("\n[ADG-GUIDED] Top 10 highest-ROI files to fix next:")
        print(f"  {'violations':>10}  {'importers':>9}  file")
        for rel_path, vcount, importers in priority[:10]:
            print(f"  {vcount:>10d}  {importers:>9d}  {rel_path}")
    else:
        top = sorted(
            [(f, sum(c.values())) for f, c in current.items()],
            key=lambda x: -x[1],
        )[:10]
        print("\n[NEXT TARGETS] Top 10 files (ADG graph not available):")
        for rel_path, cnt in top:
            print(f"  {cnt:>4d}  {rel_path}")
    print()


# ---------------------------------------------------------------------------
# Main gate
# ---------------------------------------------------------------------------


def run_gate() -> int:
    if os.environ.get("ADG_BURNDOWN_BYPASS") == "1":
        print(
            "[ADG-BURNDOWN] BYPASS active (ADG_BURNDOWN_BYPASS=1) — gate skipped.",
            file=sys.stderr,
        )
        return 0

    dry_run = os.environ.get("ADG_BURNDOWN_DRY_RUN") == "1"
    init_mode = os.environ.get("ADG_BURNDOWN_INIT") == "1"

    # Scan repo
    python_files = _collect_all_python_files()
    scanner = AntiPatternScanner(project_root=PROJECT_ROOT, enforcement_level=EnforcementLevel.WARNING)
    report = scanner.scan_changed_files(python_files)
    current = _scan_to_counts(report.all_violations)
    current_total = sum(c for cats in current.values() for c in cats.values())

    # Init mode: write budget from current state and exit cleanly
    if init_mode:
        if not dry_run:
            _write_budget(current)
        print(f"[ADG-BURNDOWN] Budget initialised: {current_total} violations across {len(current)} files")
        print(f"  Saved to: {BUDGET_FILE.relative_to(PROJECT_ROOT)}")
        return 0

    # Load budget
    budget = _load_budget()
    if not budget:
        # First-ever run — bootstrap silently from current state
        if not dry_run:
            _write_budget(current)
        _banner("ADG INTELLIGENT BURNDOWN GATE")
        print(f"  Budget bootstrapped: {current_total} violations across {len(current)} files.")
        print(f"  Saved to: {BUDGET_FILE.relative_to(PROJECT_ROOT)}")
        print("  Subsequent commits may only reduce this count.\n")
        _show_burndown_status(current, _load_adg_importer_counts())
        return 0

    budget_total = _budget_total(budget)

    # Detect regressions
    regressions = _compute_regressions(budget, current)

    # Compute shrunken budget (locks in any improvements)
    new_budget, reduced_slots = _shrink_budget(budget, current)
    new_budget_total = _budget_total(new_budget)

    # Only persist budget shrinkage on clean (non-regressed) commits
    if not dry_run and not regressions and reduced_slots > 0:
        _write_budget(new_budget)

    # Report
    _banner("ADG INTELLIGENT BURNDOWN GATE")
    print(f"  Budget (allowed) : {budget_total:>5d}")
    print(f"  Actual (current) : {current_total:>5d}")
    print(f"  Net vs budget    : {current_total - budget_total:>+5d}")
    if dry_run:
        print("  Mode             :  DRY RUN (budget NOT updated)")

    if regressions:
        reg_excess = sum(actual - allowed for _, _, allowed, actual in regressions)
        print(
            f"\n[BLOCK] {len(regressions)} file+category pair(s) exceed budget "
            f"({reg_excess} excess violation(s)):\n"
        )
        by_cat: dict[str, int] = defaultdict(int)
        for _, cat, allowed, actual in regressions:
            by_cat[cat] += actual - allowed
        for cat, excess in sorted(by_cat.items()):
            print(f"  • {cat}: +{excess}")
        print()
        for rel_path, cat, allowed, actual in regressions[:25]:
            print(
                f"  [FAIL] {rel_path}  [{cat}]  budget={allowed}  actual={actual}  excess=+{actual - allowed}"
            )

    if reduced_slots > 0:
        locked = budget_total - new_budget_total
        print(f"\n[PROGRESS] {reduced_slots} slot(s) improved — budget tightened by {locked} violation(s).")
        cats_improved: dict[str, int] = defaultdict(int)
        for rel_path, cats in budget.items():
            new_cats = new_budget.get(rel_path, {})
            for cat, old_val in cats.items():
                new_val = new_cats.get(cat, 0)
                if new_val < old_val:
                    cats_improved[cat] += old_val - new_val
        for cat, delta in sorted(cats_improved.items(), key=lambda x: -x[1]):
            print(f"  ✓ {cat}: -{delta}")

    _show_burndown_status(current, _load_adg_importer_counts())

    if regressions:
        print(
            "[ACTION] Fix the violations above OR add "
            "'# guardian: allow-<pattern>' to whitelist intentional exceptions."
        )
        print("         Each file+category budget may only decrease between commits.\n")
        return 1

    return 0


def main() -> int:
    return run_gate()


if __name__ == "__main__":
    sys.exit(main())
