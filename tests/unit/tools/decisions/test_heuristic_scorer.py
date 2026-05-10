"""Tests for heuristic_scorer.py.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W4.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.decisions.heuristic_scorer import (
    compute_heuristic_confidence,
    _extract_layer,
    _get_reversibility_score,
    LAYER_MULTIPLIERS,
    REVERSIBILITY_SCORES,
    DEFAULT_REVERSIBILITY,
)


class TestExtractLayer:
    """Test layer extraction from file paths."""
    
    def test_l0_routing(self):
        assert _extract_layer("agentic_core/L0_routing/foo.py") == "L0"
    
    def test_l1_cognition(self):
        assert _extract_layer("agentic_core/L1_cognition/bar.py") == "L1"
    
    def test_l2_execution(self):
        assert _extract_layer("agentic_core/L2_execution/baz.py") == "L2"
    
    def test_l3_orchestration(self):
        assert _extract_layer("agentic_core/L3_orchestration/qux.py") == "L3"
    
    def test_l4_state(self):
        assert _extract_layer("agentic_core/L4_state/corge.py") == "L4"
    
    def test_l5_safety(self):
        assert _extract_layer("agentic_core/L5_safety/grault.py") == "L5"
    
    def test_l6_observability(self):
        assert _extract_layer("apps_architect/L6_observability/garply.py") == "L6"
    
    def test_no_layer(self):
        assert _extract_layer("tools/utils/helper.py") is None


class TestReversibilityScore:
    """Test reversibility score lookup."""
    
    def test_markdown(self):
        assert _get_reversibility_score("docs/readme.md") == REVERSIBILITY_SCORES[".md"]
    
    def test_yaml(self):
        assert _get_reversibility_score("config/settings.yaml") == REVERSIBILITY_SCORES[".yaml"]
    
    def test_python(self):
        assert _get_reversibility_score("src/module.py") == REVERSIBILITY_SCORES[".py"]
    
    def test_json(self):
        assert _get_reversibility_score("data/config.json") == REVERSIBILITY_SCORES[".json"]
    
    def test_unknown_extension(self):
        assert _get_reversibility_score("file.unknown") == DEFAULT_REVERSIBILITY


class TestComputeHeuristicConfidence:
    """Test confidence computation."""
    
    def test_score_range(self):
        """Score should be in valid range [0.60, 1.0]."""
        score = compute_heuristic_confidence([
            "agentic_core/L2_execution/capability/foo.py",
            "tests/unit/test_foo.py",
        ])
        
        assert 0.60 <= score.total_score <= 1.0
        assert score.total_score == pytest.approx(
            sum(score.components.values()) / len(score.components),
            abs=0.2,  # Weighted average, not exact mean
        )
    
    def test_empty_files(self):
        """Empty file list should still return valid score."""
        score = compute_heuristic_confidence([])
        
        assert 0.60 <= score.total_score <= 1.0
    
    def test_layer_criticality_l0(self):
        """L0 files should have lower layer score (higher criticality)."""
        score_l0 = compute_heuristic_confidence([
            "agentic_core/L0_routing/c0_retrieval/foo.py",
        ])
        
        score_l6 = compute_heuristic_confidence([
            "apps_architect/L6_observability/span_emitters.py",
        ])
        
        # L6 should have higher layer component score (less critical)
        assert score_l6.components["layer_criticality"] >= score_l0.components["layer_criticality"]
    
    def test_reversibility_docs_vs_code(self):
        """Docs should have higher reversibility than code."""
        score_doc = compute_heuristic_confidence([
            "docs/readme.md",
        ])
        
        score_code = compute_heuristic_confidence([
            "src/module.py",
        ])
        
        assert score_doc.components["reversibility"] > score_code.components["reversibility"]
    
    def test_test_surface_with_tests(self):
        """Files with test coverage should have higher test score."""
        score = compute_heuristic_confidence([
            "src/module.py",
            "tests/unit/test_module.py",
            "tests/integration/test_module.py",
            "tests/e2e/test_module.py",
        ])
        
        assert score.components["test_surface"] == 1.0  # 3+ tests
    
    def test_test_surface_without_tests(self):
        """Files without test coverage should have lower test score."""
        score = compute_heuristic_confidence([
            "src/module.py",
        ])
        
        assert score.components["test_surface"] == 0.70  # No tests
    
    def test_custom_weights(self):
        """Custom weights should be respected."""
        custom_weights = {
            "blast_radius": 0.5,
            "layer_criticality": 0.5,
            "reversibility": 0.0,
            "test_surface": 0.0,
        }
        
        score = compute_heuristic_confidence(
            ["src/module.py"],
            weights=custom_weights,
        )
        
        assert score.blast_radius_weight == 0.5
        assert score.layer_criticality_weight == 0.5
        assert score.reversibility_weight == 0.0
        assert score.test_surface_weight == 0.0
    
    def test_to_dict(self):
        """to_dict should produce serializable output."""
        score = compute_heuristic_confidence([
            "agentic_core/L2_execution/capability/foo.py",
        ])
        
        d = score.to_dict()
        
        assert "total_score" in d
        assert "blast_radius" in d
        assert "layer_criticality" in d
        assert "reversibility" in d
        assert "test_surface" in d
        assert "weights" in d
        
        # Values should be rounded
        assert isinstance(d["total_score"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
