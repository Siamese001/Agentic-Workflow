#!/usr/bin/env python3
"""
deferred_scope_scorer.py — SSOT for deferred-scope priority banding.

Computes a deterministic P1..P5 priority band from ADG-observable features:
coverage starvation, layer criticality multiplier, structural fan-in, and
ADG-surface intersection. This is the single source of truth invoked by
`.windsurf/scripts/post_cascade_deferred_scope_capture.py` and any manual
CLI/review tooling.

Policy SSOT: .windsurf/rules/deferred-scope-capture.md
ADG layer multipliers SSOT: .windsurf/rules/adg-canonical-invariants.md §6

Usage:
    from tools.priority.deferred_scope_scorer import score_deferred_scope

    band, impact = score_deferred_scope(
        layer="L5",
        fan_in=12,
        surface="Security",
        coverage_gap_pct=85.4,
    )
    # band="P1", impact=334.7

    # CLI:
    python -m tools.priority.deferred_scope_scorer \
        --layer L5 --fan-in 12 --surface Security --coverage-gap-pct 85.4
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Scoring constants — constitutional §22 / adg-canonical-invariants §6
# ---------------------------------------------------------------------------

LAYER_MULTIPLIERS: dict[str, float] = {
    "L0": 2.0,
    "L5": 2.0,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.0,
    "L2": 1.0,
    "L6": 0.75,
}

SURFACE_BOOSTS: dict[str, float] = {
    "Security": 1.5,
    "Write": 1.4,
    "Execution": 1.3,
    "State": 1.2,
    "Observability": 1.1,
    "None": 1.0,
}

# Priority band thresholds on the computed impact score.
BAND_THRESHOLDS: list[tuple[str, float]] = [
    ("P1", 300.0),
    ("P2", 150.0),
    ("P3", 75.0),
    ("P4", 30.0),
    ("P5", 0.0),
]

Band = Literal["P1", "P2", "P3", "P4", "P5"]
Surface = Literal["Execution", "Write", "Security", "State", "Observability", "None"]


@dataclass(frozen=True)
class ScoreResult:
    band: Band
    impact_score: float
    layer_multiplier: float
    surface_boost: float
    fan_in_factor: float


def _normalize_layer(layer: str) -> float:
    key = layer.strip().upper()
    return LAYER_MULTIPLIERS.get(key, 1.0)


def _normalize_surface(surface: str) -> float:
    key = surface.strip()
    key = key[0].upper() + key[1:].lower() if key else "None"
    return SURFACE_BOOSTS.get(key, 1.0)


def _classify_band(impact: float) -> Band:
    for band, threshold in BAND_THRESHOLDS:
        if impact >= threshold:
            return band  # type: ignore[return-value]
    return "P5"


def score_deferred_scope(
    *,
    layer: str,
    fan_in: int,
    surface: str,
    coverage_gap_pct: float,
) -> ScoreResult:
    """Compute priority band P1..P5 for a deferred scope item.

    Formula:
        impact = coverage_gap_pct * layer_multiplier
               * (1 + log10(1 + fan_in)) * surface_boost

    Inputs are validated and clamped:
    - layer: unknown layers default to multiplier 1.0
    - fan_in: negative values clamped to 0
    - surface: unknown values default to boost 1.0
    - coverage_gap_pct: clamped to [0, 100]
    """
    layer_multiplier = _normalize_layer(layer)
    surface_boost = _normalize_surface(surface)
    fan_in_clamped = max(0, int(fan_in))
    gap_clamped = max(0.0, min(100.0, float(coverage_gap_pct)))

    fan_in_factor = 1.0 + math.log10(1.0 + fan_in_clamped)
    impact = gap_clamped * layer_multiplier * fan_in_factor * surface_boost
    band = _classify_band(impact)

    return ScoreResult(
        band=band,
        impact_score=round(impact, 2),
        layer_multiplier=layer_multiplier,
        surface_boost=surface_boost,
        fan_in_factor=round(fan_in_factor, 3),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deferred_scope_scorer",
        description="Compute P1..P5 priority for a deferred scope item.",
    )
    parser.add_argument("--layer", required=True, help="ADG layer (L0..L6, L_APP, etc.)")
    parser.add_argument("--fan-in", type=int, required=True, help="Structural fan-in count")
    parser.add_argument(
        "--surface",
        required=True,
        choices=list(SURFACE_BOOSTS.keys()),
        help="ADG surface intersection (or None)",
    )
    parser.add_argument(
        "--coverage-gap-pct",
        type=float,
        required=True,
        help="Coverage gap percentage (0-100)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = score_deferred_scope(
        layer=args.layer,
        fan_in=args.fan_in,
        surface=args.surface,
        coverage_gap_pct=args.coverage_gap_pct,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "band": result.band,
                    "impact_score": result.impact_score,
                    "layer_multiplier": result.layer_multiplier,
                    "surface_boost": result.surface_boost,
                    "fan_in_factor": result.fan_in_factor,
                },
                indent=2,
            )
        )
    else:
        print(f"Priority band:     {result.band}")
        print(f"Impact score:      {result.impact_score}")
        print(f"Layer multiplier:  {result.layer_multiplier} (layer={args.layer})")
        print(f"Fan-in factor:     {result.fan_in_factor} (fan_in={args.fan_in})")
        print(f"Surface boost:     {result.surface_boost} (surface={args.surface})")
        print(f"Coverage gap pct:  {args.coverage_gap_pct}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
