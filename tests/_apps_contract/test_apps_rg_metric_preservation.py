"""W6 tests: AppsRgMetricPreservationEnvelope — no invented metrics.
"""
from __future__ import annotations

import unittest

from apps_rg.runtime.bindings.exit_evidence_receipts import (
    AppsRgMetricPreservationEnvelope,
)


class TestAppsRgMetricPreservationEnvelope(unittest.TestCase):
    """Test metric preservation envelope for G22 evidence."""

    def test_metric_preservation_happy_path(self) -> None:
        """All source metrics preserved in output."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={
                "years_experience": 20,
                "team_size_led": 50,
                "budget_managed": 10000000,
            },
            output_metrics={
                "years_experience": 20,
                "team_size_led": 50,
                "budget_managed": 10000000,
            },
            preserved_metrics=["years_experience", "team_size_led", "budget_managed"],
            invented_metrics=[],  # No invention!
            omitted_metrics=[],   # Nothing omitted
            source_resume_hash="sha256:source123",
        )
        
        self.assertFalse(envelope.has_invention)
        self.assertEqual(envelope.preservation_rate, 1.0)

    def test_metric_invention_detected(self) -> None:
        """Invented metrics (not in source) are flagged."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={
                "years_experience": 20,
                "team_size_led": 50,
            },
            output_metrics={
                "years_experience": 20,
                "team_size_led": 50,
                "budget_managed": 10000000,  # INVENTED! Not in source
            },
            preserved_metrics=["years_experience", "team_size_led"],
            invented_metrics=["budget_managed"],  # Flagged as invented
            omitted_metrics=[],
            source_resume_hash="sha256:bad123",
        )
        
        self.assertTrue(envelope.has_invention)
        self.assertEqual(len(envelope.invented_metrics), 1)
        self.assertEqual(envelope.invented_metrics[0], "budget_managed")

    def test_metric_omission_allowed(self) -> None:
        """Omitting metrics is OK (not all source metrics are relevant)."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={
                "years_experience": 20,
                "team_size_led": 50,
                "old_metric": 100,  # Not relevant for this role
            },
            output_metrics={
                "years_experience": 20,
                "team_size_led": 50,
                # old_metric omitted intentionally
            },
            preserved_metrics=["years_experience", "team_size_led"],
            invented_metrics=[],  # No invention
            omitted_metrics=["old_metric"],  # Omitted is OK
            source_resume_hash="sha256:omit123",
        )
        
        # Omission does not trigger invention flag
        self.assertFalse(envelope.has_invention)
        # Preservation rate is 2/3 (not all source metrics used)
        self.assertEqual(envelope.preservation_rate, 2.0 / 3.0)

    def test_partial_preservation(self) -> None:
        """Partial preservation when some metrics changed."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={
                "years_experience": 20,
                "team_size": 50,
            },
            output_metrics={
                "years_experience": 20,  # Preserved
                "team_size": 75,  # Changed (not invention, but mutation)
            },
            preserved_metrics=["years_experience"],
            invented_metrics=[],
            omitted_metrics=[],
            source_resume_hash="sha256:partial",
        )
        
        # Only 1 of 2 preserved
        self.assertEqual(envelope.preservation_rate, 0.5)

    def test_empty_source_metrics(self) -> None:
        """Empty source metrics edge case."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={},  # No metrics in source
            output_metrics={},
            preserved_metrics=[],
            invented_metrics=[],
            omitted_metrics=[],
            source_resume_hash="sha256:empty",
        )
        
        # Preservation rate is 1.0 (nothing to preserve)
        self.assertEqual(envelope.preservation_rate, 1.0)
        self.assertFalse(envelope.has_invention)

    def test_no_invention_is_critical(self) -> None:
        """Critical test: invention must be detected for G22 compliance."""
        # Scenario: LLM "hallucinates" a metric
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={
                "years_experience": 20,
            },
            output_metrics={
                "years_experience": 20,
                "revenue_growth": 200,  # Hallucinated!
                "headcount_reduction": 30,  # Hallucinated!
            },
            preserved_metrics=["years_experience"],
            invented_metrics=["revenue_growth", "headcount_reduction"],
            omitted_metrics=[],
            source_resume_hash="sha256:hallucinate",
        )
        
        # This MUST be flagged as invention
        self.assertTrue(envelope.has_invention)
        self.assertEqual(len(envelope.invented_metrics), 2)


class TestMetricPreservationEvidencePath(unittest.TestCase):
    """Test that metric preservation feeds into Exit evidence path."""

    def test_envelope_is_evidence_for_exit(self) -> None:
        """Metric envelope is G22 evidence consumed by Exit."""
        envelope = AppsRgMetricPreservationEnvelope(
            source_metrics={"years": 20},
            output_metrics={"years": 20},
            preserved_metrics=["years"],
            invented_metrics=[],
            omitted_metrics=[],
            source_resume_hash="sha256:evidence",
        )
        
        # Envelope can be used as evidence
        self.assertTrue(hasattr(envelope, 'source_resume_hash'))
        self.assertFalse(envelope.has_invention)  # Clean


if __name__ == "__main__":
    unittest.main()
