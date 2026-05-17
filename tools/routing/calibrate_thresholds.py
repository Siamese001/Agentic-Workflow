"""Routing threshold calibration tool (Wave 6 P6.1).

Reads HealClassifierTelemetry events from a JSONL feed and produces:
  - Per-tier Brier scores (calibration quality)
  - Platt-scaled threshold recommendations for HIGH / MEDIUM cutoffs
  - A summary report written to `docs/reports/routing_calibration/`

The tool is pure-Python (no sklearn dependency) and is safe to run against
an empty feed — with no data it returns a no-op report. Callers should
regenerate thresholds by updating ``HEALING_CONFIDENCE_HIGH`` /
``HEALING_CONFIDENCE_MEDIUM`` env defaults via
``routing_thresholds_ssot.py`` (after SVP review)
via a manual PR after reviewing the recommendation.

Usage (via `python -m tools.routing.calibrate_thresholds`):

    python -m tools.routing.calibrate_thresholds \\
        --feed artifacts/telemetry/heal_classifier.jsonl \\
        --out  docs/reports/routing_calibration/2026-04-21.md

JSONL event shape (one per line) — subset of `HealClassifierTelemetry`:

    {
      "recommended_tier": "HIGH" | "MEDIUM" | "LOW" | "HITL",
      "heal_confidence": 0.0-1.0,
      "outcome_success": bool
    }

Plan reference: `.windsurf/plans/routing-unification-qwen-abe735.md` P6.1.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================================
# Pure math primitives (no sklearn / numpy dependency)
# ============================================================================


def brier_score(pairs: list[tuple[float, bool]]) -> float:
    """Mean squared error between predicted confidence and actual outcome.

    pairs: sequence of (predicted_confidence, outcome_success).
    Returns a value in [0.0, 1.0]. Lower is better; < 0.1 is well-calibrated.
    Returns 0.0 for empty input.
    """
    if not pairs:
        return 0.0
    total = 0.0
    for conf, success in pairs:
        target = 1.0 if success else 0.0
        total += (conf - target) ** 2
    return total / len(pairs)


def platt_recommend_threshold(
    pairs: list[tuple[float, bool]],
    target_success_rate: float = 0.85,
) -> float | None:
    """Recommend a confidence cutoff achieving `target_success_rate` on observed data.

    Uses a simple sliding-window heuristic — not a full Platt sigmoid fit,
    but produces a conservative threshold stable on small samples.

    Returns None when the feed has fewer than 10 events (insufficient data).
    """
    if len(pairs) < 10:
        return None

    # Sort by predicted confidence descending. Walk down until observed
    # success rate on the accumulated window drops below the target.
    sorted_pairs = sorted(pairs, key=lambda p: -p[0])
    successes = 0
    for idx, (conf, success) in enumerate(sorted_pairs, start=1):
        successes += 1 if success else 0
        rate = successes / idx
        if rate < target_success_rate and idx >= 5:
            # Walk back one step to the last good cutoff
            return round(conf, 3)
    # Never dropped below target — recommend the minimum observed confidence
    return round(sorted_pairs[-1][0], 3)


# ============================================================================
# Feed parsing
# ============================================================================


@dataclass
class CalibrationReport:
    total_events: int = 0
    per_tier_counts: dict[str, int] = field(default_factory=dict)
    per_tier_brier: dict[str, float] = field(default_factory=dict)
    per_tier_success_rate: dict[str, float] = field(default_factory=dict)
    recommended_high_threshold: float | None = None
    recommended_medium_threshold: float | None = None
    insufficient_data: bool = False
    feed_path: str = ""


def load_feed(path: Path) -> list[dict]:
    """Read a JSONL feed. Missing or empty file returns []."""
    if not path.exists():
        return []
    events: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"[calibrate_thresholds] WARN line {lineno}: malformed JSON: {exc}\n")
    return events


def compute_report(events: list[dict], feed_path: str = "") -> CalibrationReport:
    """Derive a calibration report from raw events."""
    report = CalibrationReport(total_events=len(events), feed_path=feed_path)
    if not events:
        report.insufficient_data = True
        return report

    by_tier: dict[str, list[tuple[float, bool]]] = {}
    try:
        from tqdm import tqdm  # noqa: PLC0415
    except ImportError:
        tqdm = lambda it, **_kw: it  # noqa: E731
    for ev in tqdm(events, desc="Aggregating events", unit="event"):
        # progress: wrap with tqdm for §16 compliance
        tier = str(ev.get("recommended_tier", ""))
        conf = ev.get("heal_confidence")
        outcome = ev.get("outcome_success")
        if not tier or conf is None or outcome is None:
            continue
        try:
            conf_f = float(conf)
        except (TypeError, ValueError):
            continue
        by_tier.setdefault(tier, []).append((conf_f, bool(outcome)))

    for tier, pairs in by_tier.items():
        report.per_tier_counts[tier] = len(pairs)
        report.per_tier_brier[tier] = round(brier_score(pairs), 4)
        successes = sum(1 for _, s in pairs if s)
        report.per_tier_success_rate[tier] = round(successes / len(pairs), 4)

    # Recommend HIGH threshold from the HIGH+MEDIUM pool (where deterministic
    # routing should route to HIGH if confidence is high enough).
    high_pool = by_tier.get("HIGH", []) + by_tier.get("MEDIUM", [])
    report.recommended_high_threshold = platt_recommend_threshold(high_pool, target_success_rate=0.85)
    # Recommend MEDIUM threshold from MEDIUM+LOW pool.
    medium_pool = by_tier.get("MEDIUM", []) + by_tier.get("LOW", [])
    report.recommended_medium_threshold = platt_recommend_threshold(medium_pool, target_success_rate=0.50)

    if report.total_events < 10:
        report.insufficient_data = True

    return report


def render_markdown(report: CalibrationReport) -> str:
    from datetime import datetime, timezone  # noqa: PLC0415

    lines = [
        "# Routing Threshold Calibration Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Feed:** `{report.feed_path or '(none)'}`",
        f"**Events:** {report.total_events}",
        "",
    ]

    if report.insufficient_data:
        lines.append(
            "> ⚠️ **Insufficient data** — need at least 10 events per tier to "
            "produce reliable threshold recommendations. Reporting no-op result."
        )
        lines.append("")

    lines.append("## Per-Tier Statistics")
    lines.append("")
    lines.append("| Tier | Events | Brier Score | Success Rate |")
    lines.append("|---|---:|---:|---:|")
    for tier in ("HIGH", "MEDIUM", "LOW", "HITL"):
        count = report.per_tier_counts.get(tier, 0)
        brier = report.per_tier_brier.get(tier, 0.0)
        rate = report.per_tier_success_rate.get(tier, 0.0)
        brier_marker = " ⚠️" if brier > 0.25 else ""
        lines.append(f"| {tier} | {count} | {brier:.4f}{brier_marker} | {rate:.4f} |")
    lines.append("")

    lines.append("## Recommended Thresholds")
    lines.append("")
    lines.append(
        f"- **HEALING_CONFIDENCE_HIGH** (HIGH cutoff, target success ≥ 0.85): "
        f"`{report.recommended_high_threshold}`"
    )
    lines.append(
        f"- **HEALING_CONFIDENCE_MEDIUM** (MEDIUM cutoff, target success ≥ 0.50): "
        f"`{report.recommended_medium_threshold}`"
    )
    lines.append("")
    lines.append(
        "To apply after review: set paired env knobs `HEALING_CONFIDENCE_HIGH` / "
        "`HEALING_CONFIDENCE_MEDIUM` (validated in "
        "`agentic_core/L2_execution/healers/routing_thresholds_ssot.py`)."
    )
    lines.append("")
    lines.append("## Alerts")
    lines.append("")
    alerts = []
    for tier, brier in report.per_tier_brier.items():
        if brier > 0.25:
            alerts.append(
                f"- ⚠️ Tier **{tier}** Brier score {brier:.4f} exceeds 0.25 — "
                "classifier is miscalibrated for this tier."
            )
    if not alerts:
        alerts.append("- No calibration alerts.")
    lines.extend(alerts)
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calibrate routing tier thresholds from HealClassifierTelemetry feed.",
    )
    parser.add_argument(
        "--feed",
        type=Path,
        required=True,
        help="Path to JSONL telemetry feed.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Path to write the markdown report.",
    )
    args = parser.parse_args(argv)

    events = load_feed(args.feed)
    report = compute_report(events, feed_path=str(args.feed))
    markdown = render_markdown(report)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")

    print(f"[calibrate_thresholds] wrote {len(markdown)} chars to {args.out}")
    print(f"[calibrate_thresholds] events: {report.total_events}")
    if report.insufficient_data:
        print("[calibrate_thresholds] insufficient_data=True — report is a no-op")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
