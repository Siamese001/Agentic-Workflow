"""ADG Drift Diff — structural regression detection between two ADG artifacts.

Compares a baseline artifact (e.g. main-branch) with a current artifact and
reports regressions, improvements, and structural changes.

Regression rules (any NEW occurrence is a failure):
  R1: unresolved_import_count increases
  R2: layer_violation_count increases
  R3: orphan_module_count increases beyond threshold
  R4: entities removed without a corresponding rename

Improvements are reported (not failures):
  I1: unresolved_import_count decreases
  I2: layer_violation_count decreases

CLI:
    python -m agentic_core.adg.applications.drift_diff \\
        --baseline artifacts/adg/baseline.json \\
        --current artifacts/adg/current.json
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RegressionFinding:
    """One regression finding from the diff."""

    rule: str
    severity: str
    description: str
    baseline_value: int | str
    current_value: int | str
    delta: int | str


@dataclass
class DriftDiffResult:
    """Full result of a drift diff between two artifacts."""

    baseline_path: str
    current_path: str
    baseline_commit: str
    current_commit: str
    baseline_digest: str
    current_digest: str
    regressions: list[RegressionFinding] = field(default_factory=list)
    improvements: list[dict] = field(default_factory=list)
    neutral_changes: list[dict] = field(default_factory=list)
    passed: bool = True
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "baseline_path": self.baseline_path,
            "current_path": self.current_path,
            "baseline_commit": self.baseline_commit,
            "current_commit": self.current_commit,
            "baseline_digest": self.baseline_digest,
            "current_digest": self.current_digest,
            "passed": self.passed,
            "summary": self.summary,
            "regressions": [
                {
                    "rule": r.rule,
                    "severity": r.severity,
                    "description": r.description,
                    "baseline": r.baseline_value,
                    "current": r.current_value,
                    "delta": r.delta,
                }
                for r in sorted(self.regressions, key=lambda x: x.rule)
            ],
            "improvements": sorted(self.improvements, key=lambda x: x.get("metric", "")),
            "neutral_changes": sorted(self.neutral_changes, key=lambda x: x.get("metric", "")),
        }


def run_drift_diff(
    baseline_path: Path | str,
    current_path: Path | str,
    strict: bool = False,
) -> DriftDiffResult:
    """Compare two ADG artifact JSON files and detect structural regressions.

    Parameters
    ----------
    baseline_path:
        Path to the baseline artifact JSON.
    current_path:
        Path to the current artifact JSON.
    strict:
        If True, any regression causes the result to fail.
        If False, only HIGH severity regressions cause failure.
    """
    from agentic_core.adg.artifact.serializer import diff_artifacts, load_artifact

    baseline_raw = load_artifact(baseline_path)
    current_raw = load_artifact(current_path)

    diff = diff_artifacts(baseline_path, current_path)

    result = DriftDiffResult(
        baseline_path=str(baseline_path),
        current_path=str(current_path),
        baseline_commit=diff["commit_shas"]["baseline"],
        current_commit=diff["commit_shas"]["current"],
        baseline_digest=baseline_raw.get("artifact_digest", ""),
        current_digest=current_raw.get("artifact_digest", ""),
    )

    # R1: unresolved imports regression
    uri = diff["unresolved_imports"]
    if uri["delta"] > 0:
        result.regressions.append(
            RegressionFinding(
                rule="R1",
                severity="HIGH",
                description=f"Unresolved imports increased by {uri['delta']}",
                baseline_value=uri["baseline_count"],
                current_value=uri["current_count"],
                delta=uri["delta"],
            )
        )
    elif uri["delta"] < 0:
        result.improvements.append(
            {
                "metric": "unresolved_imports",
                "description": f"Unresolved imports decreased by {abs(uri['delta'])}",
                "baseline": uri["baseline_count"],
                "current": uri["current_count"],
            }
        )

    # R2: layer violations regression
    lv = diff["layer_violations"]
    if lv["delta"] > 0:
        result.regressions.append(
            RegressionFinding(
                rule="R2",
                severity="HIGH",
                description=f"Layer violations increased by {lv['delta']}",
                baseline_value=lv["baseline_count"],
                current_value=lv["current_count"],
                delta=lv["delta"],
            )
        )
    elif lv["delta"] < 0:
        result.improvements.append(
            {
                "metric": "layer_violations",
                "description": f"Layer violations decreased by {abs(lv['delta'])}",
                "baseline": lv["baseline_count"],
                "current": lv["current_count"],
            }
        )

    # R3: orphan modules regression (allow +5 tolerance)
    om = diff["orphan_modules"]
    _ORPHAN_TOLERANCE = 5
    if om["delta"] > _ORPHAN_TOLERANCE:
        result.regressions.append(
            RegressionFinding(
                rule="R3",
                severity="MEDIUM",
                description=f"Orphan module count increased by {om['delta']} (tolerance={_ORPHAN_TOLERANCE})",
                baseline_value=om["baseline_count"],
                current_value=om["current_count"],
                delta=om["delta"],
            )
        )
    elif om["delta"] < 0:
        result.improvements.append(
            {
                "metric": "orphan_modules",
                "description": f"Orphan modules decreased by {abs(om['delta'])}",
                "baseline": om["baseline_count"],
                "current": om["current_count"],
            }
        )

    # R4: significant entity removal (more than 10 entities removed without additions)
    ent = diff["entities"]
    if ent["removed_count"] > 10 and ent["added_count"] == 0:
        result.regressions.append(
            RegressionFinding(
                rule="R4",
                severity="MEDIUM",
                description=f"{ent['removed_count']} entities removed with no new entities added",
                baseline_value=ent["baseline_count"],
                current_value=ent["current_count"],
                delta=ent["current_count"] - ent["baseline_count"],
            )
        )

    # Neutral: entity count change within tolerance
    if ent["added_count"] > 0 or ent["removed_count"] > 0:
        result.neutral_changes.append(
            {
                "metric": "entities",
                "added": ent["added_count"],
                "removed": ent["removed_count"],
                "added_sample": ent["added"][:5],
                "removed_sample": ent["removed"][:5],
            }
        )

    # Identity health delta
    ihd = diff["identity_health_delta"]
    unresolved_delta = ihd.get("unresolved_import", 0)
    if unresolved_delta != 0:
        result.neutral_changes.append(
            {
                "metric": "identity_health.unresolved_import",
                "delta": unresolved_delta,
            }
        )

    # Determine pass/fail
    high_regressions = [r for r in result.regressions if r.severity == "HIGH"]
    medium_regressions = [r for r in result.regressions if r.severity == "MEDIUM"]
    any_regressions = bool(result.regressions)

    if strict:
        result.passed = not any_regressions
    else:
        result.passed = not bool(high_regressions)

    reg_count = len(result.regressions)
    imp_count = len(result.improvements)
    if result.passed:
        result.summary = (
            f"PASS: {reg_count} regressions ({len(high_regressions)} HIGH), {imp_count} improvements"
        )
    else:
        result.summary = (
            f"FAIL: {len(high_regressions)} HIGH regressions, "
            f"{len(medium_regressions)} MEDIUM, "
            f"{imp_count} improvements"
        )

    logger.info("Drift diff complete: %s", result.summary)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ADG Drift Diff — structural regression check")
    parser.add_argument("--baseline", required=True, help="Path to baseline artifact JSON")
    parser.add_argument("--current", required=True, help="Path to current artifact JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on any regression (not just HIGH)")
    parser.add_argument("--output-json", default=None, help="Write result to JSON file")
    args = parser.parse_args(argv)

    result = run_drift_diff(
        baseline_path=Path(args.baseline),
        current_path=Path(args.current),
        strict=args.strict,
    )

    output = json.dumps(result.to_dict(), indent=2)
    print(output)

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"\nResult written: {out_path}", file=sys.stderr)

    return 0 if result.passed else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
