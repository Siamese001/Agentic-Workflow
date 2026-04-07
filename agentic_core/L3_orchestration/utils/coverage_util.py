"""Coverage Utility - Deterministic layer coverage calculations.

This module provides deterministic coverage metric functionality previously
implemented in CoverageAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 6 Micro-Wave 2).

Usage:
    from agentic_core.L3_orchestration.utils.coverage_util import (
        calculate_coverage_metrics, compute_proportions, shannon_entropy
    )

    # Calculate coverage
    metrics = calculate_coverage_metrics(layer_counts, threshold_entropy=2.2)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

import numpy as np

Logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage analysis results."""

    total_layers: int
    active_layers: int
    entropy: float
    max_entropy: float
    entropy_ratio: float
    proportions: dict[str, float]
    underrepresented_layer: str | None
    is_balanced: bool
    threshold: float


def compute_proportions(counts: dict[str, int]) -> dict[str, float]:
    """Compute layer activation proportions.

    Args:
        counts: Dictionary mapping layer names to activation counts

    Returns:
        Dictionary mapping layer names to proportion (0.0-1.0)
    """
    total = sum(counts.values())
    if total == 0:
        return dict.fromkeys(counts, 0.0)
    return {layer: count / total for layer, count in counts.items()}


def shannon_entropy(proportions: dict[str, float]) -> float:
    """Calculate Shannon entropy of layer distribution.

    Args:
        proportions: Dictionary of layer proportions

    Returns:
        Shannon entropy value (0 to log2(n))
    """
    props = np.array([p for p in proportions.values() if p > 0])
    if len(props) == 0:
        return 0.0
    return float(-np.sum(props * np.log2(props)))


def find_underrepresented_layer(
    proportions: dict[str, float],
    priority_boost_layers: list[str] | None = None,
) -> str | None:
    """Find the most underrepresented layer.

    Args:
        proportions: Layer activation proportions
        priority_boost_layers: Ordered list of layers to prioritize

    Returns:
        Name of underrepresented layer or None if balanced
    """
    if not proportions:
        return None

    priority_boost_layers = priority_boost_layers or []

    def sort_key(layer: str) -> tuple[float, int]:
        prop = proportions.get(layer, 0.0)
        if layer in priority_boost_layers:
            priority = -priority_boost_layers.index(layer)
        else:
            priority = 99
        return (prop, priority)

    return min(proportions.keys(), key=sort_key)


def calculate_coverage_metrics(
    layer_counts: dict[str, int],
    threshold_entropy: float = 2.2,
    priority_boost_layers: list[str] | None = None,
    default_layers: list[str] | None = None,
) -> CoverageMetrics:
    """Calculate comprehensive coverage metrics.

    Args:
        layer_counts: Dictionary of layer activation counts
        threshold_entropy: Entropy threshold for balance detection
        priority_boost_layers: Layers to prioritize in underrepresented detection
        default_layers: Default layer list if counts empty

    Returns:
        CoverageMetrics with analysis results
    """
    default_layers = default_layers or [
        "L0_routing", "L1_cognition", "L2_execution",
        "L3_orchestration", "L4_state", "L5_safety",
    ]

    # Ensure all layers have counts
    all_layers = set(layer_counts.keys()) | set(default_layers)
    full_counts = {layer: layer_counts.get(layer, 0) for layer in all_layers}

    # Calculate proportions
    proportions = compute_proportions(full_counts)

    # Calculate entropy
    entropy = shannon_entropy(proportions)
    max_entropy = math.log2(len(all_layers)) if all_layers else 1.0
    entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0.0

    # Determine balance
    is_balanced = entropy >= threshold_entropy

    # Find underrepresented layer
    underrepresented = None if is_balanced else find_underrepresented_layer(
        proportions, priority_boost_layers,
    )

    return CoverageMetrics(
        total_layers=len(all_layers),
        active_layers=sum(1 for c in full_counts.values() if c > 0),
        entropy=entropy,
        max_entropy=max_entropy,
        entropy_ratio=entropy_ratio,
        proportions=proportions,
        underrepresented_layer=underrepresented,
        is_balanced=is_balanced,
        threshold=threshold_entropy,
    )


def generate_coverage_report(metrics: CoverageMetrics) -> str:
    """Generate human-readable coverage report.

    Args:
        metrics: CoverageMetrics from calculate_coverage_metrics

    Returns:
        Formatted report string
    """
    report = (
        f"Coverage: Entropy={metrics.entropy:.2f}/{metrics.max_entropy:.2f} "
        f"({metrics.entropy_ratio * 100:.1f}% max). "
    )

    if metrics.is_balanced:
        report += "Coverage balanced."
    else:
        under = metrics.underrepresented_layer
        prop = metrics.proportions.get(under, 0.0) if under else 0.0
        report += (
            f"IMBALANCE DETECTED — Underrepresented: {under} "
            f"({prop:.1%}). Triggering active correction."
        )

    return report


def get_layer_bias_weight(
    layer: str,
    priority_boost_layers: list[str],
    base_weight: float = 4.0,
) -> float:
    """Calculate effective bias weight for a layer.

    Args:
        layer: Target layer name
        priority_boost_layers: Ordered list of prioritized layers
        base_weight: Base selection weight multiplier

    Returns:
        Effective weight for routing bias
    """
    if layer in priority_boost_layers:
        priority_index = priority_boost_layers.index(layer)
    else:
        priority_index = 99

    return base_weight + (5 - priority_index)


def heal_repository(
    layers: list[str] | None = None,
    threshold_entropy: float = 2.2,
    bias_weight: float = 4.0,
    priority_boost_layers: list[str] | None = None,
) -> dict[str, Any]:
    """Validate coverage configuration (autonomous healing interface).

    Args:
        layers: Layer list to validate
        threshold_entropy: Entropy threshold
        bias_weight: Selection weight multiplier
        priority_boost_layers: Priority layer list

    Returns:
        Healing results dict per standard_heal format
    """
    violations_found = 0

    if not layers or len(layers) == 0:
        violations_found += 1
        Logger.warning("[Coverage] No layers configured")

    if threshold_entropy <= 0 or threshold_entropy > 5:
        violations_found += 1
        Logger.warning(f"[Coverage] Invalid threshold: {threshold_entropy}")

    if bias_weight <= 0:
        violations_found += 1
        Logger.warning(f"[Coverage] Invalid bias_weight: {bias_weight}")

    if not priority_boost_layers:
        violations_found += 1
        Logger.warning("[Coverage] No priority_boost_layers configured")

    return {
        "violations_found": violations_found,
        "violations_fixed": 1 if violations_found == 0 else 0,
        "errors": 0,
        "skipped": 0,
    }


def main():
    """Main entry point for Coverage Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="Coverage Utility")
    parser.add_argument(
        "--layer-counts",
        type=str,
        help="JSON string of layer counts",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=2.2,
        help="Entropy threshold",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Parse layer counts
    import json
    layer_counts = json.loads(args.layer_counts) if args.layer_counts else {}

    # Calculate metrics
    metrics = calculate_coverage_metrics(layer_counts, args.threshold)

    # Generate report
    report = generate_coverage_report(metrics)
    print(report)

    return {
        "entropy": metrics.entropy,
        "max_entropy": metrics.max_entropy,
        "is_balanced": metrics.is_balanced,
        "underrepresented": metrics.underrepresented_layer,
    }


if __name__ == "__main__":
    main()
