#!/usr/bin/env python3
"""check_router_calibration_evidence.py — Closed-loop router CI gate (§28).

Refuses to pass if any router-implementing file changed in the last
``WINDOW_DAYS`` (default 7) and the corresponding per-router calibration report
is missing or stale.

Modes (controlled by ``ROUTER_CI_GATE_MODE`` env var):
    advisory   (default): always exit 0; emit a banner with violations.
    strict              : exit 1 on any violation.

Bypass:
    ROUTER_ENFORCEMENT_BYPASS=1 → exit 0 unconditionally with a bypass banner.

Calibration report path:
    docs/reports/calibration/routers/<layer>_<router>/<YYYY-Www>.md

The 10 routers are the SSOT defined in §28 / closed-loop-router-enforcement.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CALIBRATION_DIR = REPO_ROOT / "docs" / "reports" / "calibration" / "routers"
DEFAULT_WINDOW_DAYS = 7
DEFAULT_REPORT_FRESH_DAYS = 14  # report counts if regenerated within 14 days


@dataclass(frozen=True)
class RouterSpec:
    layer: str  # L0..L6
    name: str  # bandit, r5, c0, cascade, shape, reroute, uwg, hitl, promo, regret
    file_globs: tuple[str, ...]  # glob patterns (POSIX-style, repo-relative)

    @property
    def key(self) -> str:
        return f"{self.layer}_{self.name}"


# SSOT — keep aligned with §28 and closed-loop-router-enforcement.md.
ROUTERS: tuple[RouterSpec, ...] = (
    RouterSpec(
        "L0",
        "bandit",
        (
            "agentic_core/L0_routing/**/*bandit*.py",
            "agentic_core/L0_routing/**/*router*.py",
        ),
    ),
    RouterSpec(
        "L0",
        "r5",
        (
            "agentic_core/L0_routing/**/r5*.py",
            "agentic_core/L0_routing/**/*reason_router*.py",
        ),
    ),
    RouterSpec(
        "L1",
        "c0",
        (
            "agentic_core/L1_cognition/**/c0*.py",
            "agentic_core/L1_cognition/**/*context_router*.py",
        ),
    ),
    RouterSpec(
        "L2",
        "cascade",
        (
            "agentic_core/L2_execution/**/*cascade*.py",
            "agentic_core/L6_observability/heal_router_otel.py",
        ),
    ),
    RouterSpec("L3", "shape", ("agentic_core/L3_orchestration/**/*shape*.py",)),
    RouterSpec("L3", "reroute", ("agentic_core/L3_orchestration/**/*reroute*.py",)),
    RouterSpec(
        "L4",
        "uwg",
        (
            "agentic_core/L4_state/**/*uwg*.py",
            "agentic_core/L4_state/**/*write_gateway*.py",
        ),
    ),
    RouterSpec(
        "L5",
        "hitl",
        (
            "agentic_core/L5_safety/**/*hitl*.py",
            "agentic_core/L5_safety/**/exit_control*.py",
        ),
    ),
    RouterSpec(
        "L6",
        "promo",
        (
            "agentic_core/L6_observability/flywheel_promoter.py",
            "agentic_core/L6_observability/promotion_gates.py",
        ),
    ),
    RouterSpec("L6", "regret", ("agentic_core/L6_observability/regret_accounting.py",)),
)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_changed_files(window_days: int) -> set[str]:
    """Return repo-relative paths changed in the last `window_days`.

    Includes both committed changes (via ``git log``) and unstaged/untracked
    working-tree changes (via ``git status``). Returns POSIX-style paths.
    """
    paths: set[str] = set()
    since = (datetime.now(timezone.utc) - timedelta(days=window_days)).strftime("%Y-%m-%d")
    try:
        r = subprocess.run(
            ["git", "log", f"--since={since}", "--name-only", "--pretty=format:"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
            check=False,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                line = line.strip()
                if line:
                    paths.add(line.replace("\\", "/"))
    except (OSError, subprocess.TimeoutExpired):
        # guardian: allow-silent-swallow -- git probe: fail-open, return what we have
        pass
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            shell=False,
            timeout=10,
            check=False,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                # Format: "XY path" — skip the 3-char status prefix.
                if len(line) > 3:
                    paths.add(line[3:].strip().replace("\\", "/"))
    except (OSError, subprocess.TimeoutExpired):
        # guardian: allow-silent-swallow -- git probe: fail-open
        pass
    return paths


# ---------------------------------------------------------------------------
# Glob → matched-files
# ---------------------------------------------------------------------------


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    """Translate a POSIX-style glob with ``**`` to a regex.

    ``**`` matches zero or more path segments; ``*`` matches within one segment;
    ``?`` matches a single non-slash char.
    """
    out = ["^"]
    i = 0
    while i < len(glob):
        c = glob[i]
        if c == "*":
            if i + 1 < len(glob) and glob[i + 1] == "*":
                # ``**`` — zero or more path segments. Tolerate the optional
                # trailing slash (``**/foo``) by consuming it greedily.
                out.append(".*")
                i += 2
                if i < len(glob) and glob[i] == "/":
                    i += 1
            else:
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c in ".+()[]|^$\\":
            out.append("\\" + c)
            i += 1
        else:
            out.append(c)
            i += 1
    out.append("$")
    return re.compile("".join(out))


def _matches_any_glob(path: str, globs: tuple[str, ...]) -> bool:
    return any(_glob_to_regex(g).match(path) for g in globs)


# ---------------------------------------------------------------------------
# Calibration report freshness
# ---------------------------------------------------------------------------


def _has_fresh_calibration_report(router: RouterSpec, fresh_days: int) -> tuple[bool, str | None]:
    """Return (is_fresh, latest_report_path_or_None).

    Looks under ``docs/reports/calibration/routers/<layer>_<router>/`` for any
    ``*.md`` modified in the last ``fresh_days`` days.
    """
    dir_path = CALIBRATION_DIR / router.key
    if not dir_path.is_dir():
        return False, None
    cutoff = datetime.now(timezone.utc) - timedelta(days=fresh_days)
    latest_mtime: float = -1.0
    latest_path: Path | None = None
    for p in dir_path.glob("*.md"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime > latest_mtime:
            latest_mtime = mtime
            latest_path = p
    if latest_path is None:
        return False, None
    is_fresh = datetime.fromtimestamp(latest_mtime, tz=timezone.utc) >= cutoff
    rel = latest_path.relative_to(REPO_ROOT).as_posix()
    return is_fresh, rel


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouterViolation:
    router_key: str
    changed_files: tuple[str, ...]
    latest_report: str | None
    reason: str


def audit(window_days: int, fresh_days: int) -> list[RouterViolation]:
    changed = _git_changed_files(window_days)
    violations: list[RouterViolation] = []
    for r in ROUTERS:
        hits = sorted(p for p in changed if _matches_any_glob(p, r.file_globs))
        if not hits:
            continue
        is_fresh, latest = _has_fresh_calibration_report(r, fresh_days)
        if is_fresh:
            continue
        if latest is None:
            reason = f"no calibration report under docs/reports/calibration/routers/{r.key}/"
        else:
            reason = f"latest report {latest} is older than {fresh_days} days"
        violations.append(
            RouterViolation(
                router_key=r.key,
                changed_files=tuple(hits),
                latest_report=latest,
                reason=reason,
            )
        )
    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_banner(violations: list[RouterViolation], mode: str) -> None:
    if not violations:
        print("[router-calibration] OK — no router-touching changes without recent calibration evidence.")
        return
    print(f"[router-calibration] {len(violations)} router(s) changed without fresh calibration evidence:")
    for v in violations:
        print(f"  - {v.router_key}: {v.reason}")
        for f in v.changed_files[:5]:
            print(f"      changed: {f}")
        if len(v.changed_files) > 5:
            print(f"      ... and {len(v.changed_files) - 5} more")
    print(f"[router-calibration] mode={mode}")
    print("[router-calibration] To bypass: ROUTER_ENFORCEMENT_BYPASS=1")
    print("[router-calibration] To switch to strict: ROUTER_CI_GATE_MODE=strict")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--window-days",
        type=int,
        default=DEFAULT_WINDOW_DAYS,
        help="git history window for change detection (default: 7)",
    )
    p.add_argument(
        "--fresh-days",
        type=int,
        default=DEFAULT_REPORT_FRESH_DAYS,
        help="max age of a calibration report to count as fresh (default: 14)",
    )
    args = p.parse_args(argv)

    if os.environ.get("ROUTER_ENFORCEMENT_BYPASS") == "1":
        print("[router-calibration] BYPASS active (ROUTER_ENFORCEMENT_BYPASS=1) — gate skipped.")
        return 0

    mode = os.environ.get("ROUTER_CI_GATE_MODE", "advisory").strip().lower()
    if mode not in ("advisory", "strict"):
        mode = "advisory"

    violations = audit(args.window_days, args.fresh_days)
    _print_banner(violations, mode)

    if mode == "strict" and violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
