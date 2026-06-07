"""Integration tests for Author-Gate / ask_user_question harmonization.

Plan: author-gate-ask-ui-deferred-scope-a2e3f8 D1.

Tests full pipeline: context detection → routing → enrichment → telemetry → ledger.
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.decisions.heuristic_scorer import compute_heuristic_confidence
from tools.ledgers.ask_user_question_ledger import write_decision, get_decision, list_recent_decisions


class TestFullPipeline:
    """End-to-end pipeline tests."""
    
    def test_author_gate_pipeline_full(self, tmp_path):
        """Full AUTHOR_GATE pipeline produces correct telemetry."""
        # Simulate a governance-class decision
        question = "Cross-layer refactor with breaking change — which approach?"
        options = [
            {
                "id": "A",
                "label": "Extract module",
                "description": "Extract to new file",
                "tradeoff": "Cleaner but more files",
            },
            {
                "id": "B",
                "label": "Inline code",
                "description": "Keep as-is",
                "tradeoff": "Simpler but larger file",
            },
        ]
        
        # Classify (keywords: cross-layer, refactor, breaking change)
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question=question,
            options=options,
            recommended_id="A",
            telemetry_context="author_gate_routed",
        )
        
        # Verify UI invariants (id is lowercased in label)
        assert "⭐ a" in payload["options"][0]["label"].lower()
        assert "[confidence=" in payload["options"][0]["description"]
        assert "· trade-off:" in payload["options"][0]["description"]
        
        # Verify telemetry
        assert payload["telemetry_packet"]["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert "confidence_prefix" in payload["telemetry_packet"]["invariants"]
        assert "tradeoff_segment" in payload["telemetry_packet"]["invariants"]
        assert "star_marker" in payload["telemetry_packet"]["invariants"]
    
    def test_enriched_choice_pipeline_full(self, tmp_path):
        """Full ENRICHED_CHOICE pipeline produces correct telemetry."""
        question = "Which color for the button?"
        options = [
            {
                "id": "blue",
                "label": "Blue",
                "description": "Professional look",
                "tradeoff": "Common but safe",
            },
            {
                "id": "green",
                "label": "Green",
                "description": "Fresh look",
                "tradeoff": "Unconventional",
            },
        ]
        
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question=question,
            options=options,
            recommended_id="blue",
            telemetry_context="ui_choice",
        )
        
        # Verify UI invariants present (id is lowercased)
        assert "⭐ blue" in payload["options"][0]["label"].lower()
        assert "[confidence=" in payload["options"][0]["description"]
    
    def test_heuristic_to_ledger_pipeline(self, tmp_path):
        """Heuristic scorer → decision → ledger writeback."""
        # Override ledger path
        import tools.ledgers.ask_user_question_ledger as ledger_module
        original_path = ledger_module.LEDGER_PATH
        ledger_module.LEDGER_PATH = tmp_path / "test_ledger.sqlite"
        
        try:
            # Compute heuristic confidence for some files
            files = [
                "agentic_core/L2_execution/capability/foo.py",
                "tests/unit/test_foo.py",
            ]
            score = compute_heuristic_confidence(files)
            
            # Build packet with computed confidence
            packet = {
                "packet_type": "ASK_USER_QUESTION_PACKET",
                "context": "integration_test",
                "timestamp": "2026-05-10T10:00:00+00:00",
                "option_count": 2,
                "recommended_index": 0,
                "confidence_source": "heuristic_computed",
                "confidence_score": score.total_score,
                "invariants": ["confidence_prefix", "tradeoff_segment"],
            }
            
            # Write to ledger
            decision_id = write_decision(packet, selected_index=0)
            
            # Read back
            decision = get_decision(decision_id)
            assert decision is not None
            assert decision["confidence_score"] == pytest.approx(score.total_score, 0.01)
            assert decision["context"] == "integration_test"
        finally:
            ledger_module.LEDGER_PATH = original_path


class TestEdgeCases:
    """Edge case handling."""
    
    def test_single_option(self):
        """Single option should still work."""
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question="Proceed?",
            options=[
                {
                    "id": "yes",
                    "label": "Yes",
                    "description": "Continue",
                    "tradeoff": "Moves forward",
                },
            ],
            recommended_id="yes",
        )
        
        assert len(payload["options"]) == 1
        assert "⭐ yes" in payload["options"][0]["label"].lower()
    
    def test_many_options(self):
        """Four options (max allowed) should work."""
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        options = [
            {"id": f"opt{i}", "label": f"Option {i}", "description": f"Desc {i}", "tradeoff": f"Trade {i}"}
            for i in range(4)
        ]
        
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=options,
            recommended_id="opt2",
        )
        
        assert len(payload["options"]) == 4
        # Only recommended has star
        assert payload["options"][2]["label"].startswith("⭐")
    
    def test_no_recommended(self):
        """No recommended option should work."""
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question="Which color?",
            options=[
                {"id": "red", "label": "Red", "description": "Bold", "tradeoff": "Attention-grabbing"},
                {"id": "blue", "label": "Blue", "description": "Calm", "tradeoff": "Safe"},
            ],
        )
        
        # No star on any option
        for opt in payload["options"]:
            assert "⭐" not in opt["label"]
        
        assert payload["telemetry_packet"]["recommended_index"] is None


class TestHookCLI:
    """CLI and hook mode tests."""
    
    def test_hook_mode_returns_zero(self):
        """Hook mode should always return 0."""
        import subprocess
        
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf" / "pre_ask_user_question_gate.py"), "--hook-mode"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
    
    def test_test_mode_returns_zero(self):
        """Test mode should return 0."""
        import subprocess
        
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf" / "pre_ask_user_question_gate.py"), "--test"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "OK" in result.stdout
    
    def test_stdin_mode_valid_input(self):
        """Stdin mode with valid input."""
        import subprocess
        
        input_data = {
            "question": "Cross-layer migration?",
            "options": [
                {"id": "A", "label": "Extract", "description": "...", "tradeoff": "..."},
            ],
            "recommended_id": "A",
        }
        
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf" / "pre_ask_user_question_gate.py")],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "telemetry_packet" in output


class TestHeuristicWithRealADG:
    """Heuristic scorer with ADG integration."""
    
    def test_adg_lookup_returns_valid_score(self):
        """Scorer should return valid score even if ADG unavailable."""
        score = compute_heuristic_confidence([
            "agentic_core/L0_routing/c0_retrieval/foo.py",
        ])
        
        assert 0.60 <= score.total_score <= 1.0
        assert score.components["layer_criticality"] < 1.0  # L0 is critical
    
    def test_l6_has_higher_layer_score(self):
        """L6 should have higher layer score (less critical)."""
        score_l0 = compute_heuristic_confidence([
            "agentic_core/L0_routing/c0_retrieval/foo.py",
        ])
        score_l6 = compute_heuristic_confidence([
            "apps_architect/L6_observability/span_emitters.py",
        ])
        
        # L6 should be less critical than L0
        assert score_l6.components["layer_criticality"] > score_l0.components["layer_criticality"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
