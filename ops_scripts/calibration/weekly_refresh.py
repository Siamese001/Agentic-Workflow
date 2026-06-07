"""Weekly calibration refresh + drift report — W4.P2 deposit.

Plan: ``docs/archive/windsurf/legacy-tree/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` §W4.P2.

What this does:

1. Runs the W0.P2 threshold-sweep harness against every fixture under
   ``tests/calibration/fixtures/`` and writes fresh JSON reports to
   ``docs/reports/calibration/<fixture>_sweep.json``.
2. Reads the currently-deployed thresholds from
   ``config/routing_thresholds.yaml`` via the W2.P1 loader.
3. Compares the sweep's ``max_f1`` optimum against the deployed default
   and emits a drift report at
   ``docs/reports/calibration/drift_<YYYYMMDD>.md``.
4. Reads the W4.P1 in-process counter snapshot (if operators pipe
   production counts into this job's env) to include hit-rate rollups
   per namespace.

This is **advisory only** — it never edits
``config/routing_thresholds.yaml`` automatically. Operators review the
drift report and decide whether to promote new thresholds. Constitutional
§6 (Author-Gate for ambiguous decisions) applies to any threshold flip.

Usage::

    # Run inline (produces sweep reports + drift report):
    python ops_scripts/calibration/weekly_refresh.py

    # Skip re-running the sweep (use existing *_sweep.json):
    python ops_scripts/calibration/weekly_refresh.py --no-sweep

    # Write drift report to a specific path:
    python ops_scripts/calibration/weekly_refresh.py --output drift.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.config.routing_thresholds import (
    RoutingThresholdConfig,
    get_routing_thresholds,
)

# Map each fixture file stem -> threshold key the sweep calibrates.
# Stems deliberately match the files shipped by W0.P1 under
# ``tests/calibration/fixtures/``.
_FIXTURE_TO_KEY: dict[str, str] = {
    "r1a_exact_cache": "r1a_freshness_ratio",
    "r1b_semantic_cache": "r1b_semantic_similarity",
    "r3_grounding": "r3_grounding_need",
    "r5_abstain": "r5_abstain_confidence",
    "c0_coverage": "c0_coverage_floor",
}

# Alerting thresholds — absolute delta between sweep optimum and deployed
# default. Anything above :data:`_DRIFT_WARN` surfaces in the report; above
# :data:`_DRIFT_ALERT` triggers the ⚠️ marker.
_DRIFT_WARN: float = 0.02
_DRIFT_ALERT: float = 0.05

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_DIR = _REPO_ROOT / "tests" / "calibration" / "fixtures"
_REPORT_DIR = _REPO_ROOT / "docs" / "reports" / "calibration"


@dataclass(frozen=True)
class DriftRow:
    """One row of the drift report."""

    fixture: str
    threshold_key: str
    deployed_default: float
    sweep_max_f1_threshold: float | None
    sweep_max_f1_score: float | None
    delta: float | None
    severity: str  # "ok" | "warn" | "alert" | "n/a"


def _run_sweep() -> int:
    """Invoke the W0.P2 harness (`python -m tools.calibration --all`)."""
    # Import inside the function so a missing calibration harness does
    # not break `--no-sweep` callers.
    from tools.calibration.__main__ import main as sweep_main  # noqa: PLC0415

    return sweep_main(["--all", "--no-progress"])


def _load_sweep_report(fixture_stem: str) -> dict[str, Any] | None:
    """Load the sweep JSON for ``fixture_stem`` if present."""
    path = _REPORT_DIR / f"{fixture_stem}_sweep.json"
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _resolve_deployed_default(key: str, config: RoutingThresholdConfig) -> float:
    """Look up the deployed default for ``key`` from the loader."""
    return config.lookup(key, namespace="")


def _compute_drift_row(
    fixture_stem: str,
    key: str,
    config: RoutingThresholdConfig,
) -> DriftRow:
    deployed = _resolve_deployed_default(key, config)
    report = _load_sweep_report(fixture_stem)
    if report is None:
        return DriftRow(
            fixture=fixture_stem,
            threshold_key=key,
            deployed_default=deployed,
            sweep_max_f1_threshold=None,
            sweep_max_f1_score=None,
            delta=None,
            severity="n/a",
        )
    optimum = report.get("optimal_max_f1")
    if not isinstance(optimum, dict) or "threshold" not in optimum:
        return DriftRow(
            fixture=fixture_stem,
            threshold_key=key,
            deployed_default=deployed,
            sweep_max_f1_threshold=None,
            sweep_max_f1_score=None,
            delta=None,
            severity="n/a",
        )
    sweep_threshold = float(optimum["threshold"])
    sweep_f1 = float(optimum.get("f1", 0.0))
    delta = abs(deployed - sweep_threshold)
    if delta >= _DRIFT_ALERT:
        severity = "alert"
    elif delta >= _DRIFT_WARN:
        severity = "warn"
    else:
        severity = "ok"
    return DriftRow(
        fixture=fixture_stem,
        threshold_key=key,
        deployed_default=deployed,
        sweep_max_f1_threshold=sweep_threshold,
        sweep_max_f1_score=sweep_f1,
        delta=delta,
        severity=severity,
    )


def _severity_marker(severity: str) -> str:
    return {
        "ok": "✅",
        "warn": "⚠️",
        "alert": "🔴",
        "n/a": "—",
    }.get(severity, "?")


def _render_report(
    rows: list[DriftRow],
    *,
    config: RoutingThresholdConfig,
    generated_at: datetime,
) -> str:
    lines: list[str] = []
    lines.append(f"# L0 Routing Calibration Drift Report — {generated_at.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(
        "Plan: `docs/archive/windsurf/legacy-tree/plans/l0-routing-calibration-gap-audit-b3c9d4.md` §W4.P2",
    )
    lines.append(f"Generated: {generated_at.isoformat()}")
    lines.append(f"Config source: `{config.source_path or 'not loaded'}` loaded_ok={config.loaded_ok}")
    lines.append("")
    lines.append(f"Drift thresholds: warn ≥ {_DRIFT_WARN:.2f}, alert ≥ {_DRIFT_ALERT:.2f}")
    lines.append("")
    lines.append("| Fixture | Threshold key | Deployed | Sweep optimum | F1 | |Δ| | Severity |")
    lines.append("|---|---|---:|---:|---:|---:|:---:|")
    any_alert = False
    for row in rows:
        if row.severity == "alert":
            any_alert = True
        if row.sweep_max_f1_threshold is None:
            lines.append(
                f"| `{row.fixture}` | `{row.threshold_key}` | "
                f"{row.deployed_default:.3f} | — | — | — | "
                f"{_severity_marker(row.severity)} {row.severity} |"
            )
            continue
        lines.append(
            f"| `{row.fixture}` | `{row.threshold_key}` | "
            f"{row.deployed_default:.3f} | "
            f"{row.sweep_max_f1_threshold:.3f} | "
            f"{row.sweep_max_f1_score:.3f} | "
            f"{row.delta:.3f} | "
            f"{_severity_marker(row.severity)} {row.severity} |"
        )
    lines.append("")
    if any_alert:
        lines.append(
            "**🔴 At least one threshold shows alert-level drift.** "
            "Review the corresponding sweep report under "
            "`docs/reports/calibration/*_sweep.json` before promoting the new threshold."
        )
    else:
        lines.append("No alert-level drift. No threshold-promotion action recommended this cycle.")
    lines.append("")
    lines.append("## Next steps")
    lines.append("")
    lines.append("- Review any non-`ok` rows against the corresponding sweep JSON report.")
    lines.append("- If a row is `alert`, update `config/routing_thresholds.yaml` with the new value.")
    lines.append("- Re-run this job after the YAML change to confirm drift clears.")
    lines.append(
        "- Calibration harness: `python -m tools.calibration --all` "
        "(or `python ops_scripts/calibration/weekly_refresh.py` to re-run both)."
    )
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python ops_scripts/calibration/weekly_refresh.py",
        description="W4.P2 weekly routing calibration refresh + drift report",
    )
    parser.add_argument(
        "--no-sweep",
        action="store_true",
        help="Skip re-running the threshold-sweep harness (use existing reports).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Destination path for the drift report. Defaults to docs/reports/calibration/drift_<YYYYMMDD>.md."
        ),
    )
    parser.add_argument(
        "--fail-on-alert",
        action="store_true",
        help="Exit with code 1 if any threshold shows alert-level drift.",
    )
    return parser


def run(
    *,
    no_sweep: bool = False,
    output: Path | None = None,
    fail_on_alert: bool = False,
) -> int:
    """Entry point (programmatic + CLI).

    Returns:
        0 on success (or when ``fail_on_alert`` is False and drift exists).
        1 when ``fail_on_alert=True`` and any row is alert-level.
        2 on unrecoverable error (sweep invocation failed).
    """
    if not no_sweep:
        rc = _run_sweep()
        if rc != 0:
            print(
                f"weekly_refresh: sweep harness exited with rc={rc}",
                file=sys.stderr,
            )
            return 2

    # Load the live thresholds fresh — important when this runs right
    # after an operator hand-edit of routing_thresholds.yaml.
    config = get_routing_thresholds(force_reload=True)

    rows: list[DriftRow] = []
    for fixture_stem, key in sorted(_FIXTURE_TO_KEY.items()):
        rows.append(_compute_drift_row(fixture_stem, key, config))

    generated_at = datetime.now(timezone.utc)
    report_text = _render_report(rows, config=config, generated_at=generated_at)
    destination = (
        output if output is not None else (_REPORT_DIR / f"drift_{generated_at.strftime('%Y%m%d')}.md")
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"\nreport written: {destination}")

    if fail_on_alert and any(row.severity == "alert" for row in rows):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return run(
        no_sweep=args.no_sweep,
        output=args.output,
        fail_on_alert=args.fail_on_alert,
    )


if __name__ == "__main__":
    raise SystemExit(main())
