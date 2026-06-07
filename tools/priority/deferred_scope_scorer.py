#!/usr/bin/env python3
"""
deferred_scope_scorer.py — SSOT for deferred-scope priority banding.

Computes a deterministic P1..P5 priority band from ADG-observable features:
coverage starvation, layer criticality multiplier, structural fan-in, and
ADG-surface intersection. This is the single source of truth invoked by
`.cursor/scripts/_legacy_windsurf/post_cursor_agent_deferred_scope_capture.py` and any manual
CLI/review tooling.

Policy SSOT: .cursor/rules/deferred-scope-capture.md
ADG layer multipliers SSOT: .cursor/rules/adg-canonical-invariants.md §6
Operational signals SSOT: docs/architecture/adr/ADR-031-priority-scoring-operational-signals.md

Formula (v2 — ADR-031):

    impact = coverage_gap_pct
           * layer_multiplier
           * (1 + log10(1 + fan_in))            # structural blast radius (ADG)
           * surface_boost                       # 5-surface safety intersection (ADG)
           * (1 + log10(1 + prod_invocations))   # operational — production frequency
           * (1 + trajectory_defect_rate)        # operational — OTel-observed failure rate
           * reversibility_boost                 # operational — write > action > read
           * item_class_multiplier               # regression > capability
           * complexity_penalty                  # 0.8 if the item adds agentic surface area

All new inputs default to neutral (factor = 1.0) so callers that only supply
the four ADG inputs receive identical v1 scoring. This is a strict superset.

Usage:
    from tools.priority.deferred_scope_scorer import score_deferred_scope

    # Back-compat call (v1 parity):
    r = score_deferred_scope(layer="L5", fan_in=12, surface="Security",
                             coverage_gap_pct=85.4)
    # band="P1", impact=334.7

    # Full v2 call with operational signals:
    r = score_deferred_scope(
        layer="L5", fan_in=12, surface="Security", coverage_gap_pct=85.4,
        prod_invocations=5000, trajectory_defect_rate=0.12,
        reversibility="write", item_class="regression", adds_complexity=False,
    )

    # CLI:
    python -m tools.priority.deferred_scope_scorer \\
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

# ADR-031 operational-signal constants (neutral defaults preserve v1 parity)
REVERSIBILITY_BOOSTS: dict[str, float] = {
    "write": 1.5,  # irreversible durable-state mutation
    "action": 1.3,  # external side-effect (HTTP, subprocess, notification)
    "read": 1.0,  # reversible / idempotent
}

ITEM_CLASS_MULTIPLIERS: dict[str, float] = {
    "regression": 1.5,  # known-good behavior broke — trumps new capability
    "capability": 1.0,  # new feature / unmet capability
}

# Anthropic "Building Effective Agents" — add complexity only when it
# demonstrably improves outcomes. Items that ADD agentic surface area
# (new tool, orchestrator, exemption) pay a structural penalty.
COMPLEXITY_PENALTY: float = 0.8

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


Reversibility = Literal["write", "action", "read"]
ItemClass = Literal["regression", "capability"]


@dataclass(frozen=True)
class ScoreResult:
    band: Band
    impact_score: float
    layer_multiplier: float
    surface_boost: float
    fan_in_factor: float
    # v2 — ADR-031 operational signals. All default-neutral so pre-v2
    # ScoreResult consumers see identical fields plus these additions.
    prod_factor: float = 1.0
    trajectory_factor: float = 1.0
    reversibility_boost: float = 1.0
    item_class_multiplier: float = 1.0
    complexity_penalty: float = 1.0


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


def _normalize_reversibility(value: str) -> float:
    return REVERSIBILITY_BOOSTS.get(value.strip().lower(), 1.0)


def _normalize_item_class(value: str) -> float:
    return ITEM_CLASS_MULTIPLIERS.get(value.strip().lower(), 1.0)


def score_deferred_scope(
    *,
    layer: str,
    fan_in: int,
    surface: str,
    coverage_gap_pct: float,
    # v2 operational signals (ADR-031) — all default-neutral.
    prod_invocations: int = 0,
    trajectory_defect_rate: float = 0.0,
    reversibility: str = "read",
    item_class: str = "capability",
    adds_complexity: bool = False,
) -> ScoreResult:
    """Compute priority band P1..P5 for a deferred scope item.

    v2 formula (ADR-031):
        impact = coverage_gap_pct * layer_multiplier
               * (1 + log10(1 + fan_in))          # ADG structural
               * surface_boost                     # ADG 5-surface
               * (1 + log10(1 + prod_invocations)) # operational frequency
               * (1 + trajectory_defect_rate)      # operational quality
               * reversibility_boost               # blast-radius modifier
               * item_class_multiplier             # regression > capability
               * complexity_penalty                # 0.8 if adds_complexity

    Back-compat invariant: all v2 inputs at their defaults produce identical
    results to v1. Test suite pins this.

    Input normalization:
    - layer: unknown layers default to multiplier 1.0
    - fan_in: negative values clamped to 0
    - surface: unknown values default to boost 1.0
    - coverage_gap_pct: clamped to [0, 100]
    - prod_invocations: negative values clamped to 0
    - trajectory_defect_rate: clamped to [0, 1]
    - reversibility: unknown values default to 1.0 ("read"-equivalent)
    - item_class: unknown values default to 1.0 ("capability"-equivalent)
    """
    layer_multiplier = _normalize_layer(layer)
    surface_boost = _normalize_surface(surface)
    fan_in_clamped = max(0, int(fan_in))
    gap_clamped = max(0.0, min(100.0, float(coverage_gap_pct)))

    fan_in_factor = 1.0 + math.log10(1.0 + fan_in_clamped)

    prod_clamped = max(0, int(prod_invocations))
    prod_factor = 1.0 + math.log10(1.0 + prod_clamped)

    traj_clamped = max(0.0, min(1.0, float(trajectory_defect_rate)))
    trajectory_factor = 1.0 + traj_clamped

    reversibility_boost = _normalize_reversibility(reversibility)
    item_class_multiplier = _normalize_item_class(item_class)
    complexity_penalty = COMPLEXITY_PENALTY if adds_complexity else 1.0

    impact = (
        gap_clamped
        * layer_multiplier
        * fan_in_factor
        * surface_boost
        * prod_factor
        * trajectory_factor
        * reversibility_boost
        * item_class_multiplier
        * complexity_penalty
    )
    band = _classify_band(impact)

    return ScoreResult(
        band=band,
        impact_score=round(impact, 2),
        layer_multiplier=layer_multiplier,
        surface_boost=surface_boost,
        fan_in_factor=round(fan_in_factor, 3),
        prod_factor=round(prod_factor, 3),
        trajectory_factor=round(trajectory_factor, 3),
        reversibility_boost=reversibility_boost,
        item_class_multiplier=item_class_multiplier,
        complexity_penalty=complexity_penalty,
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
    # v2 operational signals (ADR-031) — all optional, default-neutral.
    parser.add_argument(
        "--prod-invocations",
        type=int,
        default=0,
        help="Production invocation count (30d rolling) from otel_mcp",
    )
    parser.add_argument(
        "--trajectory-defect-rate",
        type=float,
        default=0.0,
        help="OTel-observed trajectory defect rate in [0, 1]",
    )
    parser.add_argument(
        "--reversibility",
        default="read",
        choices=list(REVERSIBILITY_BOOSTS.keys()),
        help="Side-effect class of the affected path",
    )
    parser.add_argument(
        "--item-class",
        default="capability",
        choices=list(ITEM_CLASS_MULTIPLIERS.keys()),
        help="Regression (known-good broke) vs capability (new)",
    )
    parser.add_argument(
        "--adds-complexity",
        action="store_true",
        help="Item adds agentic surface area (tool/orchestrator/exemption)",
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
        prod_invocations=args.prod_invocations,
        trajectory_defect_rate=args.trajectory_defect_rate,
        reversibility=args.reversibility,
        item_class=args.item_class,
        adds_complexity=args.adds_complexity,
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
                    "prod_factor": result.prod_factor,
                    "trajectory_factor": result.trajectory_factor,
                    "reversibility_boost": result.reversibility_boost,
                    "item_class_multiplier": result.item_class_multiplier,
                    "complexity_penalty": result.complexity_penalty,
                },
                indent=2,
            )
        )
    else:
        print(f"Priority band:        {result.band}")
        print(f"Impact score:         {result.impact_score}")
        print(f"Layer multiplier:     {result.layer_multiplier} (layer={args.layer})")
        print(f"Fan-in factor:        {result.fan_in_factor} (fan_in={args.fan_in})")
        print(f"Surface boost:        {result.surface_boost} (surface={args.surface})")
        print(f"Coverage gap pct:     {args.coverage_gap_pct}")
        print(f"Prod factor:          {result.prod_factor} (prod_invocations={args.prod_invocations})")
        print(f"Trajectory factor:    {result.trajectory_factor} (defect_rate={args.trajectory_defect_rate})")
        print(f"Reversibility boost:  {result.reversibility_boost} ({args.reversibility})")
        print(f"Item class mult:      {result.item_class_multiplier} ({args.item_class})")
        print(f"Complexity penalty:   {result.complexity_penalty} (adds_complexity={args.adds_complexity})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
