"""G-THREE-BUCKET-GAP — three-bucket gap report threshold gate (W5).

Plan: ``.claude/plans/three-bucket-gap-remediation-069806.md`` (W5).

This gate consumes ``docs/reports/adg/THREE_BUCKET_GAP_REPORT.json``
(produced by ``tools/adg/three_bucket_gap_report.py``) and enforces
per-class thresholds on the seven gap classes defined in the
three-bucket authority model:

    ├── TRIPLET_ATTESTED  (—  : passing — counts as health)
    ├── REGISTRY_DRIFT    (P2: undocumented coupling / accidental API)
    ├── DEAD_PATH         (P3: declared + wired but never traced)
    ├── UNOBSERVED_CODE   (P3: static-only orphan)
    ├── DYNAMIC_DISPATCH  (P5: runtime-only — observed but not in code)
    ├── SHADOW_CHANNEL    (P1: registry-only — declared but unused)
    └── CONFIG_BLOAT      (P4: runtime-only declared)

Per-class thresholds (defaults — override with --config):

    SHADOW_CHANNEL   == 0     (P1: critical, never tolerated)
    REGISTRY_DRIFT   <= 5%    (P2: warn band)
    DEAD_PATH        <= 10%   (P3: tolerated band)
    UNOBSERVED_CODE  no max   (P3: aspirational target only — drives W3.future)
    DYNAMIC_DISPATCH <= 20%   (P5: dynamic call-site allowance)
    CONFIG_BLOAT     <= 1%    (P4: declared registry rows that aren't yet used)

Modes
-----
* ``advisory`` (env ``THREE_BUCKET_GAP_STRICT=0``): always exit 0,
  surface violations in stdout + report.
* ``strict`` (default, env ``THREE_BUCKET_GAP_STRICT=1``): exit 1 on any
  violation. ``--strict`` CLI flag forces strict regardless of env.

Bypass: ``THREE_BUCKET_GAP_BYPASS=1`` — short-circuit to exit 0.

Constitutional ties: §22 graph-layer evidence; §28 SQLite-direct fallback;
W1+W2+W3 of plan three-bucket-gap-remediation-069806.
"""

from __future__ import annotations

# This gate consumes a pre-built JSON report; it does not query ADG views.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "THREE_BUCKET_GAP_REPORT.json"
)
GATE_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "three_bucket_gap_gate_report.json"
)


# Per-class thresholds. Each entry is (max_count, max_pct).
# - max_count is None means "no count threshold"
# - max_pct  is None means "no percentage threshold"
# When BOTH are None, the class is exempt from any threshold check.
DEFAULT_THRESHOLDS: Final[dict[str, tuple[int | None, float | None]]] = {
    "SHADOW_CHANNEL":   (0,    None),  # P1 — must be zero
    "REGISTRY_DRIFT":   (None, 5.0),   # P2 — <= 5%
    "DEAD_PATH":        (None, 10.0),  # P3 — <= 10%
    "UNOBSERVED_CODE":  (None, None),  # P3 — aspirational only
    "DYNAMIC_DISPATCH": (None, 20.0),  # P5 — <= 20%
    "CONFIG_BLOAT":     (None, 1.0),   # P4 — <= 1%
    # TRIPLET_ATTESTED is the healthy bucket; no upper threshold.
}


@dataclass
class ClassResult:
    defect_class: str
    severity: str
    edge_count: int
    edge_pct: float
    threshold_count: int | None
    threshold_pct: float | None
    violation: bool
    violation_reason: str = ""


@dataclass
class GateResult:
    gate: str = "G-THREE-BUCKET-GAP"
    tier: str = "B"
    timestamp: str = ""
    report_path: str = ""
    snapshot: str = ""
    strict_mode: bool = True
    runtime_view_present: bool = False
    health_score_pct_triplet_attested: float = 0.0
    classes: list[dict] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    status: str = "ok"


def _classify(
    cls_row: dict, thresholds: dict[str, tuple[int | None, float | None]]
) -> ClassResult:
    name = str(cls_row.get("defect_class", ""))
    severity = str(cls_row.get("severity", ""))
    count = int(cls_row.get("edge_count", 0))
    pct = float(cls_row.get("edge_pct", 0.0))

    max_count, max_pct = thresholds.get(name, (None, None))
    violation = False
    reason_parts: list[str] = []

    if max_count is not None and count > max_count:
        violation = True
        reason_parts.append(f"count={count} exceeds threshold={max_count}")
    if max_pct is not None and pct > max_pct:
        violation = True
        reason_parts.append(f"pct={pct:.2f}% exceeds threshold={max_pct:.2f}%")

    return ClassResult(
        defect_class=name,
        severity=severity,
        edge_count=count,
        edge_pct=pct,
        threshold_count=max_count,
        threshold_pct=max_pct,
        violation=violation,
        violation_reason="; ".join(reason_parts),
    )


def _load_thresholds_override(path: Path | None) -> dict[str, tuple[int | None, float | None]]:
    """Optional JSON override file. Shape: {"CLASS": {"max_count": int|null, "max_pct": float|null}}."""
    if path is None:
        return DEFAULT_THRESHOLDS
    if not path.exists():
        raise FileNotFoundError(f"thresholds config not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = dict(DEFAULT_THRESHOLDS)
    for cls_name, vals in raw.items():
        if not isinstance(vals, dict):
            continue
        out[cls_name] = (vals.get("max_count"), vals.get("max_pct"))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Path to gap report JSON (default {DEFAULT_REPORT_PATH})",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON file overriding per-class thresholds",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override THREE_BUCKET_GAP_STRICT env var)",
    )
    parser.add_argument(
        "--min-health-score",
        type=float,
        default=None,
        help=(
            "W5 P5.2: minimum health_score_pct_triplet_attested (0.0-100.0). "
            "Overrides THREE_BUCKET_GAP_MIN_HEALTH_SCORE env var. Default "
            "threshold is 0.0 (reporting only) until the three-bucket soak "
            "window (P5.5) establishes a calibrated floor."
        ),
    )
    args = parser.parse_args(argv)

    if os.environ.get("THREE_BUCKET_GAP_BYPASS") == "1":
        print("[three_bucket_gap] bypass active (THREE_BUCKET_GAP_BYPASS=1)")
        return 0

    # W5 of plan three-bucket-gap-remediation-069806: strict mode is the
    # default. Set THREE_BUCKET_GAP_STRICT=0 to revert to advisory.
    _env = os.environ.get("THREE_BUCKET_GAP_STRICT", "1")
    strict = args.strict or _env == "1"

    if not args.report.exists():
        print(
            f"[three_bucket_gap] FAIL: report not found at {args.report}\n"
            f"  Run: ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py\n"
            f"  Or: python tools/adg/three_bucket_gap_report.py"
        )
        return 1 if strict else 0

    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[three_bucket_gap] FAIL: cannot parse report: {exc}")
        return 1 if strict else 0

    thresholds = _load_thresholds_override(args.config)

    classes_in_report = report.get("summary_by_class") or []
    cls_results: list[ClassResult] = [
        _classify(c, thresholds) for c in classes_in_report
    ]
    violations = [r for r in cls_results if r.violation]

    # W5 P5.2: optional health-score floor. Resolved from CLI flag → env var →
    # default 0.0 (reporting only). Emits a synthetic violation when the
    # observed triplet-attested percentage falls below the floor.
    health_score_value = float(report.get("health_score_pct_triplet_attested", 0.0))
    health_floor_raw = args.min_health_score
    if health_floor_raw is None:
        _env_floor = os.environ.get("THREE_BUCKET_GAP_MIN_HEALTH_SCORE", "0.0")
        try:
            health_floor_raw = float(_env_floor)
        except ValueError:
            print(
                f"[three_bucket_gap] WARN: invalid THREE_BUCKET_GAP_MIN_HEALTH_SCORE="
                f"{_env_floor!r}; treating as 0.0"
            )
            health_floor_raw = 0.0
    health_floor: float = max(0.0, min(100.0, health_floor_raw))
    health_violation_msg = ""
    if health_floor > 0.0 and health_score_value < health_floor:
        health_violation_msg = (
            f"health_score {health_score_value:.2f}% < floor {health_floor:.2f}%"
        )

    violation_strings = [
        f"{r.defect_class} ({r.severity}): {r.violation_reason}" for r in violations
    ]
    if health_violation_msg:
        violation_strings.append(f"HEALTH_SCORE (P1): {health_violation_msg}")
    total_violations = len(violations) + (1 if health_violation_msg else 0)

    result = GateResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        report_path=str(args.report.relative_to(REPO_ROOT))
        if args.report.is_absolute() and args.report.is_relative_to(REPO_ROOT)
        else str(args.report),
        snapshot=str(report.get("snapshot", "")),
        strict_mode=strict,
        runtime_view_present=bool(report.get("runtime_view_present", False)),
        health_score_pct_triplet_attested=health_score_value,
        classes=[asdict(r) for r in cls_results],
        violations=violation_strings,
        status="ok" if total_violations == 0 else "violations",
    )

    GATE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_REPORT_PATH.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    print(
        f"READ_EXISTING_REPORT: path={result.report_path} "
        f"snapshot={report.get('snapshot', '')} "
        f"snapshot_sha256={report.get('source_snapshot_sha256', 'MISSING')} "
        f"generated_at={report.get('generated_at', 'MISSING')} "
        f"runtime_proof={report.get('runtime_proof_status', '')}"
    )
    print(
        f"[three_bucket_gap] classes={len(cls_results)} violations={total_violations} "
        f"runtime_view_present={result.runtime_view_present} "
        f"health_score={result.health_score_pct_triplet_attested:.1f}% "
        f"health_floor={health_floor:.1f}% strict={strict}"
    )
    if total_violations:
        print(f"[three_bucket_gap] details written to {GATE_REPORT_PATH}")
        for v in violation_strings:
            print(f"  - {v}")

    if total_violations and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
