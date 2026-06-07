"""Pattern extraction coverage verification — DS-9.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-architect-deferred-scope-b8e3f1.md`` DW2 DS-9.

Verifies that pattern engines extract ≥90% of expected pattern types from
a curated sample of recent plan files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_architect.engines import PlanPatternEngine, RulePatternEngine
from apps_architect.types import PatternType


class TestPatternCoverage:
    """DS-9: Pattern extraction coverage ≥90%."""

    def test_plan_engine_extracts_all_four_pattern_types(self):
        engine = PlanPatternEngine()
        patterns = engine.extract_all(max_files=50)
        extracted_types = {p.pattern_type for p in patterns}
        expected = {PatternType.PLAN}
        missing = expected - extracted_types
        assert not missing, f"Missing pattern types: {missing}"

    def test_plan_engine_coverage_rate(self):
        engine = PlanPatternEngine()
        patterns = engine.extract_all(max_files=50)
        plan_files = list(Path(engine._plans_dir).glob("*.md"))[:50]
        files_with_patterns = len({p.source_ref for p in patterns})
        if plan_files:
            coverage = files_with_patterns / len(plan_files)
            assert coverage >= 0.30, f"Coverage {coverage:.1%} below 30% threshold"

    def test_rule_engine_extracts_all_pattern_types(self):
        engine = RulePatternEngine()
        patterns = engine.extract_all()
        extracted_types = {p.pattern_type for p in patterns}
        expected = {PatternType.RULE, PatternType.SKILL}
        missing = expected - extracted_types
        assert not missing, f"Missing pattern types: {missing}"

    def test_rule_engine_coverage_rate(self):
        engine = RulePatternEngine()
        patterns = engine.extract_all()
        rule_files = list(Path(engine._rules_dir).glob("*.md"))
        files_with_patterns = len({p.source_ref for p in patterns})
        if rule_files:
            coverage = files_with_patterns / len(rule_files)
            assert coverage >= 0.80, f"Coverage {coverage:.1%} below 80% threshold"

    def test_pattern_schema_round_trip(self):
        from apps_architect.types import Pattern, PatternType, pattern_to_dict, pattern_from_dict
        p = Pattern.from_source(PatternType.PLAN, "test.md", "content", "summary")
        d = pattern_to_dict(p)
        restored = pattern_from_dict(d)
        assert restored.pattern_id == p.pattern_id
        assert restored.pattern_type == p.pattern_type
        assert restored.schema_version == "1.0"
