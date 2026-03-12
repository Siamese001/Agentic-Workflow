"""
ADG Intelligent Burndown Gate — Pre-Commit Anti-Pattern Ratchet

Enforces a one-way ratchet on the landmine baseline:
  - The baseline count may only decrease or stay the same; it CANNOT grow.
  - Every commit that touches files with existing violations MUST reduce or hold
    the baseline count for those files (no silent grandfathering of new lines).
  - On violation-count *reduction*: auto-shrinks the baseline file so progress
    is permanently locked in.
  - Uses ADG dependency graph to report blast-radius and suggest the highest-ROI
    files to fix next.

Exit codes:
  0  — baseline held or improved (commit allowed)
  1  — baseline regressed (new anti-patterns snuck in; commit blocked)

Environment overrides:
  ADG_BURNDOWN_BYPASS=1   — skip gate (emergency only; logged to stderr)
  ADG_BURNDOWN_DRY_RUN=1  — report without updating baseline file
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap path so the script works as both a pre-commit hook and a direct
# invocation from repo root.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation

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
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "landmine_baseline.txt"
_EXCLUDE_DIRS = (
    GLOBAL_EXCLUDED_DIRS
    | SOVEREIGN_EXCLUDED_FOLDERS
    | DISCOVERY_EXCLUDED_TERRITORIES
    | {".nox"}
)
_EXCLUDE_FILE_PATTERNS = ["__dbg_*.py", "**/activate_this.py"]

# ADG artifact — may not exist in all environments (graceful degradation)
_ADG_FILE_GRAPH = PROJECT_ROOT / "artifacts" / "adg" / "adg_file_graph_03122026.json"

# ---------------------------------------------------------------------------
# Baseline helpers (text format: "rel/path.py:lineno:category:message")
# ---------------------------------------------------------------------------

def _load_baseline_signatures() -> set[str]:
    if not BASELINE_FILE.exists():
        return set()
    return {
        line.strip()
        for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _count_by_category(signatures: set[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for sig in signatures:
        parts = sig.split(":")
        if len(parts) >= 3:
            counts[parts[2]] += 1
    return dict(counts)


def _write_baseline(signatures: set[str]) -> None:
    """Atomically shrink the baseline to *signatures* (never grows here)."""
    if os.environ.get("ADG_BURNDOWN_DRY_RUN") == "1":
        return
    lines = sorted(signatures)
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: temp file then rename
    import tempfile
    fd, tmp = tempfile.mkstemp(
        dir=str(BASELINE_FILE.parent),
        prefix=".landmine_baseline_",
        suffix=".tmp",
    )
    try:
        os.write(fd, ("\n".join(lines) + "\n").encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and BASELINE_FILE.exists():
            BASELINE_FILE.unlink()
        Path(tmp).replace(BASELINE_FILE)
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


# ---------------------------------------------------------------------------
# ADG helpers — provide fix-priority guidance (non-blocking if ADG absent)
# ---------------------------------------------------------------------------

def _load_adg_reverse_index() -> dict[str, list[str]]:
    """
    Returns {file_path_posix: [files_that_import_it, ...]} from ADG edges.
    Used to estimate blast-radius: fixing a heavily-imported file has high ROI.
    """
    if not _ADG_FILE_GRAPH.exists():
        return {}
    try:
        adg = json.loads(_ADG_FILE_GRAPH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    reverse: dict[str, list[str]] = defaultdict(list)
    for edge in adg.get("edges", []):
        src = edge.get("f", "")
        sym = edge.get("sym", "")
        if src and sym and "." in sym:
            # Reconstruct module path from dotted symbol
            target = "/".join(sym.split(".")[:-1]) + ".py"
            reverse[target].append(src)
    return dict(reverse)


def _adg_fix_priority(
    files_with_violations: list[tuple[str, int]],
    reverse_index: dict[str, list[str]],
) -> list[tuple[str, int, int]]:
    """
    Sort files by (violations × importers) descending — highest-ROI first.
    Returns list of (rel_path, violation_count, importer_count).
    """
    scored = []
    for rel_path, vcount in files_with_violations:
        importers = len(reverse_index.get(rel_path, []))
        scored.append((rel_path, vcount, importers))
    scored.sort(key=lambda x: (x[1] * max(x[2], 1)), reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Full-repo scan helpers
# ---------------------------------------------------------------------------

def _collect_all_python_files() -> list[Path]:
    return [
        f
        for f in sorted(PROJECT_ROOT.rglob("*.py"))
        if not (set(f.relative_to(PROJECT_ROOT).parts) & _EXCLUDE_DIRS)
        and not any(f.match(pat) for pat in _EXCLUDE_FILE_PATTERNS)
    ]


def _sig_for_violation(v) -> str:
    fp = v.file_path
    if isinstance(fp, Path):
        rel = fp.relative_to(PROJECT_ROOT).as_posix() if fp.is_absolute() else fp.as_posix()
    else:
        p = Path(fp)
        rel = p.relative_to(PROJECT_ROOT).as_posix() if p.is_absolute() else p.as_posix()
    return f"{rel}:{v.line_number}:{v.category.value}:{v.message}"


# ---------------------------------------------------------------------------
# Main gate logic
# ---------------------------------------------------------------------------

def run_gate() -> int:
    """
    Run the burndown ratchet gate.

    Returns 0 (pass) or 1 (block).
    """
    if os.environ.get("ADG_BURNDOWN_BYPASS") == "1":
        print(
            "[ADG-BURNDOWN] BYPASS active (ADG_BURNDOWN_BYPASS=1). "
            "Gate skipped — violations NOT checked.",
            file=sys.stderr,
        )
        return 0

    dry_run = os.environ.get("ADG_BURNDOWN_DRY_RUN") == "1"

    # 1. Load saved baseline
    baseline_sigs = _load_baseline_signatures()
    baseline_total = len(baseline_sigs)

    # 2. Full-repo scan (same scope as check_anti_patterns.py)
    python_files = _collect_all_python_files()
    scanner = AntiPatternScanner(
        project_root=PROJECT_ROOT, enforcement_level=EnforcementLevel.WARNING
    )
    report = scanner.scan_changed_files(python_files)
    current_sigs = {_sig_for_violation(v) for v in report.all_violations}
    current_total = len(current_sigs)

    # 3. Compute delta
    regressed_sigs = current_sigs - baseline_sigs  # new violations NOT in baseline
    resolved_sigs = baseline_sigs - current_sigs   # violations fixed since baseline

    regressed_count = len(regressed_sigs)
    resolved_count = len(resolved_sigs)
    net_change = current_total - baseline_total     # positive = regression

    # 4. Shrink baseline if violations were fixed (lock in progress)
    if resolved_count > 0 and not dry_run:
        updated = baseline_sigs - resolved_sigs
        _write_baseline(updated)

    # 5. Build ADG fix-priority report (best-ROI files to work on next)
    reverse_index = _load_adg_reverse_index()
    remaining_by_file: dict[str, int] = defaultdict(int)
    for sig in current_sigs:
        parts = sig.split(":")
        if parts:
            remaining_by_file[parts[0]] += 1
    priority_list = _adg_fix_priority(list(remaining_by_file.items()), reverse_index)

    # 6. Report
    _banner("ADG INTELLIGENT BURNDOWN GATE")
    print(f"  Baseline total  : {baseline_total:>5d}")
    print(f"  Current total   : {current_total:>5d}")
    print(f"  Resolved (fixed): {resolved_count:>5d}  [baseline shrunk]")
    print(f"  Regressed (NEW) : {regressed_count:>5d}")
    print(f"  Net change      : {net_change:>+5d}")
    if dry_run:
        print("  Mode            :  DRY RUN (baseline NOT updated)")

    # 7. Show regressions if any
    if regressed_sigs:
        print(f"\n[BLOCK] {regressed_count} NEW anti-pattern(s) introduced:")
        reg_by_cat: dict[str, int] = defaultdict(int)
        for sig in sorted(regressed_sigs):
            parts = sig.split(":")
            cat = parts[2] if len(parts) > 2 else "unknown"
            reg_by_cat[cat] += 1
        for cat, cnt in sorted(reg_by_cat.items()):
            print(f"  • {cat}: {cnt}")
        print()
        for sig in sorted(regressed_sigs)[:20]:
            parts = sig.split(":")
            print(f"  [FAIL] {':'.join(parts[:2])}  [{parts[2] if len(parts)>2 else '?'}]")
            if len(parts) > 3:
                print(f"         {':'.join(parts[3:])[:100]}")

    # 8. Show burndown progress
    if resolved_count > 0:
        print(f"\n[PROGRESS] Eliminated {resolved_count} violation(s) — baseline updated.")
        cats_fixed = _count_by_category(resolved_sigs)
        for cat, cnt in sorted(cats_fixed.items(), key=lambda x: -x[1]):
            print(f"  ✓ {cat}: -{cnt}")

    # 9. Show ADG-guided next targets (top 10 by ROI)
    remaining_cats = _count_by_category(current_sigs)
    print(f"\n[BURNDOWN STATUS] {current_total} violation(s) remaining")
    for cat, cnt in sorted(remaining_cats.items(), key=lambda x: -x[1]):
        print(f"  {cnt:4d}  {cat}")

    if priority_list:
        print(f"\n[ADG-GUIDED] Top 10 highest-ROI files to fix next:")
        print(f"  {'violations':>10}  {'importers':>9}  file")
        for rel_path, vcount, importers in priority_list[:10]:
            print(f"  {vcount:>10d}  {importers:>9d}  {rel_path}")
    else:
        # Fallback: show top violators without ADG
        print(f"\n[NEXT TARGETS] Top 10 files by violation count (ADG graph not available):")
        for rel_path, vcount, _ in sorted(
            [(p, c, 0) for p, c in remaining_by_file.items()],
            key=lambda x: -x[1],
        )[:10]:
            print(f"  {vcount:>4d}  {rel_path}")

    print()

    if regressed_count > 0:
        print(
            "[ACTION] Fix the NEW violations above OR add "
            "'# guardian: allow-<pattern>' to whitelist intentional exceptions."
        )
        print(
            "         The baseline count may only decrease. "
            "It cannot grow between commits."
        )
        return 1

    return 0


def _banner(title: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    return run_gate()


if __name__ == "__main__":
    sys.exit(main())
