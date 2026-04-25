"""
Tests for ConstitutionalRulesEngine - governance rule validation and enforcement.

Coverage:
- Rule loading and parsing
- Rule evaluation against context
- Rule conflict detection
- Rule priority ordering
- Exception handling for malformed rules
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L1_cognition.reasoning.constitutional_rules_engine import ConstitutionalRulesEngine


class TestConstitutionalRulesEngine:
    """Test suite for ConstitutionalRulesEngine."""

    def test_init_with_valid_rules_path(self, tmp_path):
        """Test initialization with valid rules directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test_rule.md").write_text("# Test Rule\n\nContent")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        assert engine is not None
        assert engine.rules_path == str(rules_dir)

    def test_init_with_missing_rules_path(self):
        """Test initialization with missing rules directory."""
        with pytest.raises(FileNotFoundError):
            ConstitutionalRulesEngine(rules_path="/nonexistent/path")

    def test_load_rules_from_directory(self, tmp_path):
        """Test loading rules from directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "rule1.md").write_text("# Rule 1")
        (rules_dir / "rule2.md").write_text("# Rule 2")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        rules = engine.load_rules()
        
        assert len(rules) == 2
        assert "rule1" in [r.get("name", "") for r in rules]

    def test_evaluate_context_against_rules(self, tmp_path):
        """Test rule evaluation against context."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test_rule.md").write_text("""
# Test Rule

## Trigger
action: "write_file"

## Constraint
path must not contain "archive"
""")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        context = {"action": "write_file", "path": "src/main.py"}
        result = engine.evaluate(context)
        
        assert result.compliant is True

    def test_evaluate_context_violation(self, tmp_path):
        """Test rule evaluation detects violations."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test_rule.md").write_text("""
# Test Rule

## Trigger
action: "write_file"

## Constraint
path must not contain "archive"
""")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        context = {"action": "write_file", "path": "archive/old.py"}
        result = engine.evaluate(context)
        
        assert result.compliant is False
        assert "archive" in result.violation_message.lower()

    def test_rule_priority_ordering(self, tmp_path):
        """Test rules are evaluated in priority order."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "p1_rule.md").write_text("# P1 Rule\n\nPriority: 1")
        (rules_dir / "p2_rule.md").write_text("# P2 Rule\n\nPriority: 2")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        rules = engine.load_rules()
        
        # Rules should be sorted by priority
        priorities = [r.get("priority", 999) for r in rules]
        assert priorities == sorted(priorities)

    def test_malformed_rule_handling(self, tmp_path):
        """Test handling of malformed rule files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "bad_rule.md").write_text("Not a valid rule format")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        rules = engine.load_rules()
        
        # Should skip or handle malformed rules gracefully
        assert isinstance(rules, list)

    def test_rule_conflict_detection(self, tmp_path):
        """Test detection of conflicting rules."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "rule_a.md").write_text("# Rule A\n\nRequire: X")
        (rules_dir / "rule_b.md").write_text("# Rule B\n\nForbid: X")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        conflicts = engine.detect_conflicts()
        
        assert len(conflicts) > 0

    def test_get_rule_by_id(self, tmp_path):
        """Test retrieving specific rule by ID."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test_rule.md").write_text("# Test Rule\n\nID: rule-123")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        rule = engine.get_rule("rule-123")
        
        assert rule is not None
        assert rule.get("id") == "rule-123"

    def test_reload_rules(self, tmp_path):
        """Test reloading rules from disk."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "rule1.md").write_text("# Rule 1")
        
        engine = ConstitutionalRulesEngine(rules_path=str(rules_dir))
        initial_count = len(engine.load_rules())
        
        # Add new rule
        (rules_dir / "rule2.md").write_text("# Rule 2")
        engine.reload_rules()
        
        new_count = len(engine.load_rules())
        assert new_count == initial_count + 1
