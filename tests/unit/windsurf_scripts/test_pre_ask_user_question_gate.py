"""Tests for pre_ask_user_question_gate.py.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W4.
"""

import json
import sys
from pathlib import Path

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import importlib.util

# Load module directly from .claude/governance/scripts
gate_spec = importlib.util.spec_from_file_location(
    "pre_ask_user_question_gate",
    REPO_ROOT / ".claude" / "governance/scripts" / "pre_ask_user_question_gate.py"
)
gate_module = importlib.util.module_from_spec(gate_spec)
sys.modules["pre_ask_user_question_gate"] = gate_module
gate_spec.loader.exec_module(gate_module)

classify_decision_type = gate_module.classify_decision_type
route_to_author_gate = gate_module.route_to_author_gate
route_to_enriched_choice = gate_module.route_to_enriched_choice
pre_ask_user_question_gate = gate_module.pre_ask_user_question_gate


class TestClassifyDecisionType:
    """Test decision classification."""
    
    def test_author_gate_refactor_keyword(self):
        """Single keyword should classify as ENRICHED (threshold=2)."""
        result = classify_decision_type(
            question="Which approach for the refactor?",
            options=[
                {"id": "A", "label": "Extract", "description": "..."},
                {"id": "B", "label": "Inline", "description": "..."},
            ],
        )
        assert result == "ENRICHED_CHOICE"  # Only 1 keyword
    
    def test_author_gate_multiple_keywords(self):
        """Multiple governance keywords classify as AUTHOR_GATE."""
        result = classify_decision_type(
            question="Cross-layer migration with breaking change?",
            options=[
                {"id": "A", "label": "Extract", "description": "..."},
                {"id": "B", "label": "Inline", "description": "..."},
            ],
        )
        assert result == "AUTHOR_GATE"  # cross-layer, migration, breaking change
    
    def test_author_gate_structured_options(self):
        """Options with confidence field classify as AUTHOR_GATE."""
        result = classify_decision_type(
            question="Which approach?",
            options=[
                {
                    "id": "A",
                    "label": "Plan A",
                    "description": "...",
                    "confidence": 0.88,
                },
                {"id": "B", "label": "Plan B", "description": "..."},
            ],
        )
        assert result == "AUTHOR_GATE"
    
    def test_enriched_choice_simple(self):
        """Simple choice with no governance keywords."""
        result = classify_decision_type(
            question="What color should the button be?",
            options=[
                {"id": "A", "label": "Blue", "description": "..."},
                {"id": "B", "label": "Green", "description": "..."},
            ],
        )
        assert result == "ENRICHED_CHOICE"


class TestRouting:
    """Test routing functions."""
    
    def test_route_to_author_gate(self):
        """AUTHOR_GATE routing produces correct payload."""
        payload = route_to_author_gate(
            question="Test question?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Desc A",
                    "tradeoff": "Tradeoff A",
                },
            ],
            recommended_id="A",
        )
        
        assert payload["_routing"] == "AUTHOR_GATE"
        assert payload["telemetry_packet"]["packet_type"] == "AUTHOR_GATE_ROUTED"
        assert "confidence_prefix" in payload["telemetry_packet"]["invariants"]
    
    def test_route_to_enriched_choice(self):
        """ENRICHED_CHOICE routing produces correct payload."""
        payload = route_to_enriched_choice(
            question="Test question?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Desc A",
                    "tradeoff": "Tradeoff A",
                },
            ],
            recommended_id="A",
        )
        
        assert payload["_routing"] == "ENRICHED_CHOICE"
        assert payload["telemetry_packet"]["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert "confidence_prefix" in payload["telemetry_packet"]["invariants"]
    
    def test_pre_hook_routing_author_gate(self):
        """Pre-hook correctly routes AUTHOR_GATE decisions."""
        payload = pre_ask_user_question_gate(
            question="Cross-layer refactor with blast radius?",
            options=[
                {
                    "id": "A",
                    "label": "Extract",
                    "description": "Extract module",
                    "tradeoff": "Cleaner but more files",
                },
                {
                    "id": "B",
                    "label": "Inline",
                    "description": "Keep as-is",
                    "tradeoff": "Simpler but larger",
                },
            ],
            recommended_id="A",
        )
        
        assert payload["_routing"] == "AUTHOR_GATE"
        assert payload["telemetry_packet"]["packet_type"] == "AUTHOR_GATE_ROUTED"
        # Check UI invariants present
        assert "⭐ A" in payload["options"][0]["label"]
        assert "[confidence=" in payload["options"][0]["description"]
        assert "· trade-off:" in payload["options"][0]["description"]
    
    def test_pre_hook_routing_enriched_choice(self):
        """Pre-hook correctly routes ENRICHED_CHOICE decisions."""
        payload = pre_ask_user_question_gate(
            question="Which color for the button?",
            options=[
                {
                    "id": "A",
                    "label": "Blue",
                    "description": "Blue button",
                    "tradeoff": "Professional but common",
                },
                {
                    "id": "B",
                    "label": "Green",
                    "description": "Green button",
                    "tradeoff": "Fresh but unconventional",
                },
            ],
            recommended_id="A",
        )
        
        assert payload["_routing"] == "ENRICHED_CHOICE"
        assert payload["telemetry_packet"]["packet_type"] == "ASK_USER_QUESTION_PACKET"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
