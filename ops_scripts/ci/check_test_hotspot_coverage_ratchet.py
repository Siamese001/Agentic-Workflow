#!/usr/bin/env python3
"""Test-hotspot coverage ratchet gate (W6.2).

Plan: ``adg-testing-hotspots-wave-plan-a7f3c1`` Wave 6.

Locks in the testing-hotspot burn-down so coverage can only go UP. Computes
basename test coverage (does a ``test_<leaf>.py`` exist anywhere under
``tests/`` for each source module?) for ``agentic_core`` and the ``apps_*``
surface, then compares the *tested* counts against a committed baseline.

Modes
-----
- (default)            advisory — print status; exit 0 even on regression.
- ``--strict`` / env  fail-closed — exit 1 when tested count drops below baseline.
- ``--init``          (re)write the baseline from the current tree.

Env: ``TEST_HOTSPOT_RATCHET_FAIL_CLOSED=1`` ⇒ same as ``--strict``.
     ``TEST_HOTSPOT_RATCHET_BYPASS=1``      ⇒ skip (exit 0, warn).

Basename match mirrors ``tools/analysis/test_hotspot_gaps_report.py`` — it does
NOT require the ADG snapshot, so it runs anywhere (CI, fresh clone).

SSOT folder: ``ops_scripts/ci/`` (constitutional §31, ``check_*`` archetype).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO / "tests"
# Baseline lives next to the gate (tracked) — artifacts/ is gitignored, so a
# baseline there would never reach CI and the ratchet would no-op.
BASELINE = Path(__file__).resolve().parent / "coverage_ratchet_baseline.json"

_CORE_ROOT = REPO / "agentic_core"


def _test_basenames() -> set[str]:
    """Every ``<leaf>`` for which a ``tests/**/test_<leaf>.py`` exists."""
    out: set[str] = set()
    for p in TESTS_DIR.rglob("test_*.py"):
        out.add(p.stem[len("test_"):])
    return out


def _module_leaves(root: Path) -> list[str]:
    """Source module leaves under ``root`` (excludes ``__init__`` and tests/)."""
    leaves: list[str] = []
    for p in root.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        if "/tests/" in p.as_posix():
            continue
        leaves.append(p.stem)
    return leaves


def _coverage(root: Path, tested: set[str]) -> tuple[int, int]:
    leaves = _module_leaves(root)
    covered = sum(1 for leaf in leaves if leaf in tested)
    return covered, len(leaves)


def _measure() -> dict[str, int]:
    tested = _test_basenames()
    core_cov, core_total = _coverage(_CORE_ROOT, tested)
    apps_cov = apps_total = 0
    for app_dir in sorted(REPO.glob("apps_*")):
        if not app_dir.is_dir():
            continue
        c, t = _coverage(app_dir, tested)
        apps_cov += c
        apps_total += t
    return {
        "core_tested": core_cov,
        "core_total": core_total,
        "apps_tested": apps_cov,
        "apps_total": apps_total,
    }


def _load_baseline() -> dict[str, int] | None:
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.1f}%" if d else "n/a"


def _rel(p: Path) -> str:
    """Repo-relative display, falling back to the absolute path off-tree."""
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--init", action="store_true", help="(re)write the baseline")
    ap.add_argument("--strict", action="store_true", help="fail-closed on regression")
    args = ap.parse_args(argv)

    if os.environ.get("TEST_HOTSPOT_RATCHET_BYPASS") == "1":
        print("WARNING: TEST_HOTSPOT_RATCHET_BYPASS=1 — ratchet skipped")
        return 0

    cur = _measure()
    print(
        f"[test-hotspot-ratchet] core {cur['core_tested']}/{cur['core_total']} "
        f"({_pct(cur['core_tested'], cur['core_total'])}) · "
        f"apps {cur['apps_tested']}/{cur['apps_total']} "
        f"({_pct(cur['apps_tested'], cur['apps_total'])})"
    )

    if args.init:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(cur, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[test-hotspot-ratchet] baseline written → {_rel(BASELINE)}")
        return 0

    base = _load_baseline()
    if base is None:
        print(
            "[test-hotspot-ratchet] no baseline found "
            f"({_rel(BASELINE)}); run with --init. (advisory pass)"
        )
        return 0

    strict = args.strict or os.environ.get("TEST_HOTSPOT_RATCHET_FAIL_CLOSED") == "1"
    regressions: list[str] = []
    for key in ("core_tested", "apps_tested"):
        if cur[key] < base.get(key, 0):
            regressions.append(f"{key}: {cur[key]} < baseline {base.get(key, 0)}")

    if regressions:
        print("[test-hotspot-ratchet] ❌ coverage REGRESSED:")
        for r in regressions:
            print(f"  - {r}")
        if strict:
            print("[test-hotspot-ratchet] fail-closed (strict) → exit 1")
            return 1
        print("[test-hotspot-ratchet] advisory mode → exit 0 (set --strict to enforce)")
        return 0

    print("[test-hotspot-ratchet] ✅ coverage is monotonic (≥ baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
