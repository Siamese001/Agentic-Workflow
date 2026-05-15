"""Evidence-freshness gate for APPS-DOM runtime harness fixtures.

Plan: .cursor/plans/apps-dom-real-evidence-enhancement-c7f4d8.md W4.P1.

Guards against stale fixtures masking regressions. The APPS-DOM runtime
evidence chain (harness -> emitter -> merger -> compiler) depends on
harness fixtures under:

  - artifacts/apps_otel_traces/                  (pass-path)
  - artifacts/apps_negative_controls_runtime/    (X3A DENY)
  - artifacts/apps_safe_abstain_runtime/         (X3E SAFE_ABSTAIN)

If any of those directories contain a fixture older than the freshness
window (default 168h = 1 week), the gate reports drift. This catches the case
where a plan landed runtime changes but nobody regenerated the fixtures,
so the compiler still sees stale PASS assertions.

Tolerance modes:
  - Absent fixture directory -> SKIP (first-run tolerant).
  - Fixtures present but all fresh -> PASS.
  - Any fixture stale -> stderr report; exit 0 (advisory) unless
    ``APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED=1`` (exit 1) or
    ``APPS_DOM_FIXTURE_FRESHNESS_BYPASS=1`` (exit 0 with bypass banner).

Configuration:
  - APPS_DOM_FIXTURE_FRESHNESS_HOURS  (default 168)
  - APPS_DOM_FIXTURE_FRESHNESS_BYPASS (1 to force PASS with WARNING)
  - APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED (1 to exit 1 on stale fixtures; default advisory exit 0)

Exit codes:
  0  all fresh, SKIP (absent dirs), stale with advisory default, or BYPASS
  1  stale fixtures when ``APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED=1``
  2  fatal error
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_FIXTURE_DIRS: tuple[tuple[str, str], ...] = (
    ("pass-path", "artifacts/apps_otel_traces"),
    ("negative-control", "artifacts/apps_negative_controls_runtime"),
    ("safe-abstain", "artifacts/apps_safe_abstain_runtime"),
)

_DEFAULT_FRESHNESS_HOURS = 168


def _parse_iso_utc(s: str) -> datetime | None:
    """Parse an ISO-8601 UTC timestamp; return None on any error."""
    if not isinstance(s, str):
        return None
    try:
        # Accept both "+00:00" and "Z" suffixes.
        s = s.replace("Z", "+00:00") if s.endswith("Z") else s
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _fixture_age_hours(fixture_path: Path, now: datetime) -> float | None:
    """Return age in hours from a fixture's generated_at_utc, or None if unknown."""
    try:
        doc = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    ts_str = doc.get("generated_at_utc") if isinstance(doc, dict) else None
    ts = _parse_iso_utc(str(ts_str or ""))
    if ts is None:
        # Fallback to filesystem mtime
        try:
            mtime = datetime.fromtimestamp(fixture_path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            return None
        return (now - mtime).total_seconds() / 3600.0
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return (now - ts).total_seconds() / 3600.0


def _scan_directory(dir_rel: str, now: datetime) -> dict[str, object]:
    """Return {exists, fixtures_total, fixtures_stale, oldest_age_hours, paths_stale}."""
    dir_abs = REPO_ROOT / dir_rel
    report: dict[str, object] = {
        "directory": dir_rel,
        "exists": dir_abs.exists(),
        "fixtures_total": 0,
        "fixtures_stale": 0,
        "oldest_age_hours": None,
        "paths_stale": [],
    }
    if not dir_abs.exists():
        return report
    fixtures = sorted(p for p in dir_abs.iterdir()
                      if p.is_file() and p.suffix == ".json" and not p.name.startswith("_"))
    report["fixtures_total"] = len(fixtures)
    stale_paths: list[str] = []
    oldest = 0.0
    freshness_hours = _get_freshness_hours()
    for fx in fixtures:
        age = _fixture_age_hours(fx, now)
        if age is None:
            continue
        if age > oldest:
            oldest = age
        if age > freshness_hours:
            stale_paths.append(fx.relative_to(REPO_ROOT).as_posix())
    report["oldest_age_hours"] = round(oldest, 2) if fixtures else None
    report["fixtures_stale"] = len(stale_paths)
    report["paths_stale"] = stale_paths
    return report


def _get_freshness_hours() -> int:
    """Return the freshness window in hours, honoring env override."""
    raw = os.environ.get("APPS_DOM_FIXTURE_FRESHNESS_HOURS", "").strip()
    if not raw:
        return _DEFAULT_FRESHNESS_HOURS
    try:
        hours = int(raw)
        if hours > 0:
            return hours
    except ValueError:
        pass
    return _DEFAULT_FRESHNESS_HOURS


def main() -> int:
    bypass = os.environ.get("APPS_DOM_FIXTURE_FRESHNESS_BYPASS", "").strip() in {"1", "true", "TRUE"}
    freshness_hours = _get_freshness_hours()
    now = datetime.now(timezone.utc)

    print("[check_apps_dom_fixture_freshness] checking harness fixture freshness")
    print(f"  freshness window: {freshness_hours}h")
    if bypass:
        print("  BYPASS flag set — violations logged, exit 0 forced")

    reports = [_scan_directory(rel, now) for _label, rel in _FIXTURE_DIRS]

    all_absent = True
    total_stale = 0
    total_fixtures = 0
    for (label, _rel), rep in zip(_FIXTURE_DIRS, reports):
        if rep["exists"]:
            all_absent = False
        total_fixtures += int(rep["fixtures_total"])
        total_stale += int(rep["fixtures_stale"])
        status = "OK  " if rep["fixtures_stale"] == 0 and rep["exists"] else "    "
        age = rep["oldest_age_hours"]
        age_repr = f"{age}h" if age is not None else "n/a"
        print(
            f"  {status}{label:18s}  dir={rep['directory']:50s}  "
            f"total={rep['fixtures_total']:2d}  stale={rep['fixtures_stale']:2d}  "
            f"oldest={age_repr}  exists={rep['exists']}"
        )
        for p in rep["paths_stale"][:3]:
            print(f"        stale: {p}")

    if all_absent:
        print("[check_apps_dom_fixture_freshness] SKIP — no fixture directories present (first-run tolerant)")
        return 0

    if total_stale == 0:
        print(f"[check_apps_dom_fixture_freshness] OK — {total_fixtures} fixtures fresh")
        return 0

    # Persist drift report for audit
    artifacts_dir = REPO_ROOT / "artifacts" / "ci"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    drift = {
        "checked_at_utc": now.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "freshness_hours": freshness_hours,
        "total_fixtures": total_fixtures,
        "total_stale": total_stale,
        "per_directory": reports,
    }
    drift_path = artifacts_dir / "apps_dom_fixture_freshness.json"
    drift_path.write_text(json.dumps(drift, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[check_apps_dom_fixture_freshness] drift report: {drift_path.relative_to(REPO_ROOT).as_posix()}")

    if bypass:
        print(
            f"[check_apps_dom_fixture_freshness] BYPASS — {total_stale} stale fixture(s) "
            f"logged; exit 0 forced. Re-run the harnesses to refresh."
        )
        return 0

    fail_closed = os.environ.get("APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED", "").strip() == "1"
    if fail_closed:
        print(
            f"[check_apps_dom_fixture_freshness] FAIL-CLOSED — {total_stale} fixture(s) older than "
            f"{freshness_hours}h. Re-run:\n"
            f"  python tools/cert/apps_e2e/run_app_cert_with_otel_capture.py\n"
            f"  python tools/cert/apps_e2e/run_app_negative_control_with_otel.py\n"
            f"  python tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py"
        )
        return 1

    print(
        f"[check_apps_dom_fixture_freshness] Advisory — {total_stale} stale fixture(s) "
        f"older than {freshness_hours}h (set APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED=1 to fail). Re-run:\n"
        f"  python tools/cert/apps_e2e/run_app_cert_with_otel_capture.py\n"
        f"  python tools/cert/apps_e2e/run_app_negative_control_with_otel.py\n"
        f"  python tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CI gate must never crash the suite;
        # a fatal error is reported as exit 2, operator investigates.
        print(f"[check_apps_dom_fixture_freshness] FATAL {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
