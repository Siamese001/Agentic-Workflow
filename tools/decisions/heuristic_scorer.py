"""Heuristic confidence scorer for non-gated decisions.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W3.

Computes confidence scores using:
- ADG blast radius (files touched)
- Layer criticality (L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0)
- Reversibility (file type)
- Test surface delta
- Precedent match (if any)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Layer multipliers per constitutional §4
LAYER_MULTIPLIERS = {
    "L0": 2.0,
    "L1": 1.0,
    "L2": 1.0,
    "L3": 1.75,
    "L4": 1.75,
    "L5": 2.0,
    "L6": 0.75,
}

# File type reversibility scores (higher = more reversible)
REVERSIBILITY_SCORES = {
    ".md": 0.95,      # Docs - fully reversible
    ".yaml": 0.90,    # Config - highly reversible
    ".yml": 0.90,
    ".json": 0.85,    # Data - mostly reversible
    ".py": 0.70,      # Code - moderate reversibility
    ".pyi": 0.80,     # Stubs - more reversible
    ".sql": 0.75,     # Schema - moderate
    ".toml": 0.85,    # Config
}

DEFAULT_REVERSIBILITY = 0.60


def _extract_layer(path: str) -> str | None:
    """Extract layer from file path."""
    path_lower = path.lower()
    
    # Check for layer indicators in path
    layer_indicators = [
        ("L0_routing", "L0"),
        ("L1_cognition", "L1"),
        ("L2_execution", "L2"),
        ("L3_orchestration", "L3"),
        ("L4_state", "L4"),
        ("L5_safety", "L5"),
        ("L6_observability", "L6"),
        ("/L0/", "L0"),
        ("/L1/", "L1"),
        ("/L2/", "L2"),
        ("/L3/", "L3"),
        ("/L4/", "L4"),
        ("/L5/", "L5"),
        ("/L6/", "L6"),
    ]
    
    for indicator, layer in layer_indicators:
        if indicator in path:
            return layer
    
    # Check for agentic_core layers
    if "agentic_core/L0" in path:
        return "L0"
    if "agentic_core/L1" in path:
        return "L1"
    if "agentic_core/L2" in path:
        return "L2"
    if "agentic_core/L3" in path:
        return "L3"
    if "agentic_core/L4" in path:
        return "L4"
    if "agentic_core/L5" in path:
        return "L5"
    if "agentic_core/L6" in path or "apps_architect/L6" in path:
        return "L6"
    
    return None


def _get_reversibility_score(file_path: str) -> float:
    """Get reversibility score based on file extension."""
    ext = Path(file_path).suffix.lower()
    return REVERSIBILITY_SCORES.get(ext, DEFAULT_REVERSIBILITY)


def _query_adg_blast_radius(files: list[str]) -> dict[str, Any]:
    """Query ADG for blast radius of files.
    
    Returns dict with fan_in, fan_out, centrality metrics.
    Fail-soft: returns defaults if ADG unavailable.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.adg.core.sqlite_adg import get_blast_radius
        
        total_fan_in = 0
        total_fan_out = 0
        
        for file_path in files:
            try:
                radius = get_blast_radius(file_path)
                total_fan_in += radius.get("fan_in", 0)
                total_fan_out += radius.get("fan_out", 0)
            except Exception:
                continue
        
        return {
            "fan_in": total_fan_in,
            "fan_out": total_fan_out,
            "centrality": (total_fan_in + total_fan_out) / 2 if files else 0,
        }
    except ImportError:
        # ADG not available - fail soft
        return {"fan_in": 0, "fan_out": 0, "centrality": 0, "fallback": True}
    finally:
        if REPO_ROOT in sys.path:
            sys.path.remove(str(REPO_ROOT))


def _count_test_files(scope_files: list[str]) -> int:
    """Count test files in scope."""
    return sum(1 for f in scope_files if "test" in f.lower() or "_test" in f.lower())


@dataclass
class HeuristicScore:
    """Score result with component breakdown."""
    
    total_score: float
    blast_radius_weight: float
    layer_criticality_weight: float
    reversibility_weight: float
    test_surface_weight: float
    components: dict[str, float]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": round(self.total_score, 2),
            "blast_radius": round(self.components["blast_radius"], 2),
            "layer_criticality": round(self.components["layer_criticality"], 2),
            "reversibility": round(self.components["reversibility"], 2),
            "test_surface": round(self.components["test_surface"], 2),
            "weights": {
                "blast_radius": self.blast_radius_weight,
                "layer_criticality": self.layer_criticality_weight,
                "reversibility": self.reversibility_weight,
                "test_surface": self.test_surface_weight,
            },
        }


def compute_heuristic_confidence(
    scope_files: list[str],
    weights: dict[str, float] | None = None,
) -> HeuristicScore:
    """Compute confidence score for non-gated decisions.
    
    Args:
        scope_files: List of file paths that would be touched
        weights: Optional custom weights (must sum to ~1.0)
    
    Returns:
        HeuristicScore with total score (0.0-1.0) and component breakdown
    
    Example:
        >>> score = compute_heuristic_confidence([
        ...     "agentic_core/L2_execution/capability/foo.py",
        ...     "tests/unit/test_foo.py",
        ... ])
        >>> print(score.total_score)  # e.g., 0.74
    """
    # Default weights per plan b8c3e1
    default_weights = {
        "blast_radius": 0.25,
        "layer_criticality": 0.20,
        "reversibility": 0.20,
        "test_surface": 0.20,
        "precedent": 0.15,  # Reserved for future precedent lookup
    }
    w = weights or default_weights
    
    # Normalize weights to sum to 1.0
    total_weight = sum(w.values())
    if total_weight > 0:
        w = {k: v / total_weight for k, v in w.items()}
    
    # 1. Blast radius (ADG query)
    blast_data = _query_adg_blast_radius(scope_files)
    centrality = blast_data.get("centrality", 0)
    # Higher centrality = more impact = lower confidence
    # Normalize: 0-50 centrality maps to 0.6-1.0 score
    blast_score = max(0.6, 1.0 - (centrality / 100))
    
    # 2. Layer criticality
    layer_scores = []
    for file_path in scope_files:
        layer = _extract_layer(file_path)
        if layer:
            multiplier = LAYER_MULTIPLIERS.get(layer, 1.0)
            # Lower multiplier = less critical = higher confidence
            layer_scores.append(2.0 - multiplier)  # Invert: L0 (2.0) → 0.0, L6 (0.75) → 1.25
    
    if layer_scores:
        avg_layer_score = sum(layer_scores) / len(layer_scores)
        # Normalize to 0.5-1.0 range
        layer_score = min(1.0, max(0.5, 0.5 + (avg_layer_score / 2)))
    else:
        layer_score = 0.75  # Default if no layer detected
    
    # 3. Reversibility
    revers_scores = [_get_reversibility_score(f) for f in scope_files]
    reversibility_score = sum(revers_scores) / len(revers_scores) if revers_scores else DEFAULT_REVERSIBILITY
    
    # 4. Test surface
    test_count = _count_test_files(scope_files)
    # More tests = higher confidence
    if test_count >= 3:
        test_score = 1.0
    elif test_count >= 1:
        test_score = 0.85
    else:
        test_score = 0.70
    
    # Compute weighted total
    total = (
        w["blast_radius"] * blast_score +
        w["layer_criticality"] * layer_score +
        w["reversibility"] * reversibility_score +
        w["test_surface"] * test_score +
        w.get("precedent", 0.0) * 0.72  # Default precedent score
    )
    
    # Clamp to valid range
    total = max(0.60, min(1.0, total))  # Floor at 0.60 per surface threshold
    
    return HeuristicScore(
        total_score=total,
        blast_radius_weight=w["blast_radius"],
        layer_criticality_weight=w["layer_criticality"],
        reversibility_weight=w["reversibility"],
        test_surface_weight=w["test_surface"],
        components={
            "blast_radius": blast_score,
            "layer_criticality": layer_score,
            "reversibility": reversibility_score,
            "test_surface": test_score,
        },
    )


def main() -> int:
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute heuristic confidence score")
    parser.add_argument("files", nargs="+", help="Files in scope")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    score = compute_heuristic_confidence(args.files)
    
    if args.json:
        print(json.dumps(score.to_dict(), indent=2))
    else:
        print(f"Confidence: {score.total_score:.2f}")
        print(f"  Blast radius: {score.components['blast_radius']:.2f}")
        print(f"  Layer criticality: {score.components['layer_criticality']:.2f}")
        print(f"  Reversibility: {score.components['reversibility']:.2f}")
        print(f"  Test surface: {score.components['test_surface']:.2f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
