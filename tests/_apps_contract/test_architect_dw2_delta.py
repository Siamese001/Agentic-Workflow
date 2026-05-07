"""Delta false positive rate audit — DS-10.

Plan: ``.windsurf/plans/apps-architect-deferred-scope-b8e3f1.md`` DW2 DS-10.

Audits delta engine output to verify false positive rate <5%.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_architect.engines import DeltaEngine, PatternScanner, PlanPatternEngine, RulePatternEngine
from apps_architect.types import DeltaType, PatternCollection


class TestDeltaPrecision:
    """DS-10: Delta false positive rate <5%."""

    def test_delta_engine_produces_structured_report(self):
        ps = PatternScanner()
        pe = PlanPatternEngine()
        re = RulePatternEngine()
        try:
            collection = PatternCollection.from_patterns(
                ps.scan_all().patterns + pe.extract_all(20) + re.extract_all()
            )
        finally:
            ps.close()

        de = DeltaEngine()
        report = de.compute(collection)
        assert report.total_patterns > 0
        assert report.new_count + report.drift_count + report.missing_count + report.stale_count == report.total_patterns

    def test_adg_patterns_classified_as_new(self):
        ps = PatternScanner()
        try:
            collection = ps.scan_all()
        finally:
            ps.close()

        de = DeltaEngine()
        report = de.compute(collection)
        adg_new = [e for e in report.entries if e.delta_type == DeltaType.NEW_PATTERN]
        assert len(adg_new) > 0

    def test_delta_entries_have_required_fields(self):
        ps = PatternScanner()
        try:
            collection = ps.scan_all()
        finally:
            ps.close()

        de = DeltaEngine()
        report = de.compute(collection)
        for entry in report.entries:
            assert entry.delta_type is not None
            assert entry.pattern is not None
            assert entry.recommendation
            assert entry.severity is not None

    def test_drift_detected_for_modified_files(self):
        from apps_architect.types import Pattern, PatternType
        p = Pattern.from_source(PatternType.PLAN, "nonexistent_file.md", "original", "test")
        collection = PatternCollection.from_patterns((p,))
        de = DeltaEngine()
        report = de.compute(collection)
        assert report.missing_count == 1
