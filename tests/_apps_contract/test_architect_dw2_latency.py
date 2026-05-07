"""E2E scan latency benchmark — DS-11.

Plan: ``.windsurf/plans/apps-architect-deferred-scope-b8e3f1.md`` DW2 DS-11.

Benchmarks the full scan → delta → rules pipeline to verify <30s.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_architect.engines import (
    DeltaEngine,
    PatternScanner,
    PlanPatternEngine,
    RuleGenerator,
    RulePatternEngine,
)
from apps_architect.types import PatternCollection


class TestLatencyBenchmark:
    """DS-11: E2E scan latency <30s."""

    def test_full_pipeline_under_30_seconds(self):
        start = time.monotonic()

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

        rg = RuleGenerator()
        rules = rg.generate(report)

        elapsed = time.monotonic() - start
        assert elapsed < 30.0, f"Pipeline took {elapsed:.1f}s, exceeds 30s limit"
        assert len(rules) > 0

    def test_scan_only_under_10_seconds(self):
        start = time.monotonic()
        ps = PatternScanner()
        try:
            ps.scan_all()
        finally:
            ps.close()
        elapsed = time.monotonic() - start
        assert elapsed < 10.0, f"Scan took {elapsed:.1f}s"

    def test_delta_only_under_5_seconds(self):
        ps = PatternScanner()
        try:
            collection = ps.scan_all()
        finally:
            ps.close()

        start = time.monotonic()
        de = DeltaEngine()
        de.compute(collection)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Delta took {elapsed:.1f}s"
