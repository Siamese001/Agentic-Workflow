"""W4 contract test: Writeback candidates must be explicitly marked as inert.

Verifies that:
1. inert_writeback_candidates field exists and defaults to 0
2. uwg_committed_writes field exists and defaults to 0
3. Display shows "inert" prefix on writeback candidates
4. No claim of durable writes without UWG receipt
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock


class TestInertPrefixOnCandidatesDataclass(unittest.TestCase):
    """RuntimeExecutiveSummary dataclass must have inert prefix fields."""

    def _make_summary(self, **kwargs):
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        defaults = dict(
            run_id="test-run",
            trace_id="test-trace",
            target_company="ACME",
            target_role="Director",
            generation_mode="strategic_tailor",
            start_timestamp="2026-01-01T00:00:00+00:00",
            end_timestamp="2026-01-01T00:00:01+00:00",
            total_duration_ms=1000,
            sections=[],
        )
        defaults.update(kwargs)
        return RuntimeExecutiveSummary(**defaults)

    def test_inert_writeback_candidates_defaults_zero(self) -> None:
        """inert_writeback_candidates must default to 0."""
        s = self._make_summary()
        self.assertEqual(s.inert_writeback_candidates, 0)

    def test_uwg_committed_writes_defaults_zero(self) -> None:
        """uwg_committed_writes must default to 0."""
        s = self._make_summary()
        self.assertEqual(s.uwg_committed_writes, 0)

    def test_inert_candidates_can_be_set(self) -> None:
        """inert_writeback_candidates can be set to non-zero."""
        s = self._make_summary(inert_writeback_candidates=5)
        self.assertEqual(s.inert_writeback_candidates, 5)

    def test_uwg_committed_can_be_set(self) -> None:
        """uwg_committed_writes can be set to non-zero."""
        s = self._make_summary(uwg_committed_writes=3)
        self.assertEqual(s.uwg_committed_writes, 3)


class TestInertPrefixInMarkdown(unittest.TestCase):
    """Markdown output must show inert prefix on writeback status."""

    def _make_summary(self, candidates=0, committed=0):
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        return RuntimeExecutiveSummary(
            run_id="test-run",
            trace_id="test-trace",
            target_company="ACME",
            target_role="Director",
            generation_mode="strategic_tailor",
            start_timestamp="2026-01-01T00:00:00+00:00",
            end_timestamp="2026-01-01T00:00:01+00:00",
            total_duration_ms=1000,
            sections=[],
            inert_writeback_candidates=candidates,
            uwg_committed_writes=committed,
        )

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import format_executive_summary_markdown
        self.format_fn = format_executive_summary_markdown

    def test_markdown_has_write_back_status_section(self) -> None:
        """Markdown must have WRITE-BACK STATUS section."""
        md = self.format_fn(self._make_summary())
        self.assertIn("## WRITE-BACK STATUS", md)

    def test_markdown_shows_inert_candidates(self) -> None:
        """Markdown must show inert_writeback_candidates."""
        md = self.format_fn(self._make_summary(candidates=5))
        self.assertIn("inert_writeback_candidates", md)
        self.assertIn("5", md)

    def test_markdown_shows_uwg_committed(self) -> None:
        """Markdown must show uwg_committed_writes."""
        md = self.format_fn(self._make_summary(committed=2))
        self.assertIn("uwg_committed_writes", md)
        self.assertIn("2", md)

    def test_markdown_no_durable_claim_without_uwg(self) -> None:
        """Must not claim durable writes when uwg_committed_writes is 0."""
        md = self.format_fn(self._make_summary(candidates=5, committed=0))
        # Should not contain phrases implying committed writes
        self.assertNotIn("durable", md.lower())
        self.assertNotIn("persisted", md.lower())


class TestInertPrefixInInline(unittest.TestCase):
    """Inline display must show inert prefix on writeback status."""

    def _make_summary(self, candidates=0, committed=0):
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        return RuntimeExecutiveSummary(
            run_id="test-run",
            trace_id="test-trace",
            target_company="ACME",
            target_role="Director",
            generation_mode="strategic_tailor",
            start_timestamp="2026-01-01T00:00:00+00:00",
            end_timestamp="2026-01-01T00:00:01+00:00",
            total_duration_ms=1000,
            sections=[],
            inert_writeback_candidates=candidates,
            uwg_committed_writes=committed,
        )

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import display_runtime_summary_inline
        self.inline_fn = display_runtime_summary_inline

    def test_inline_has_write_back_section(self) -> None:
        """Inline must show WRITE-BACK line."""
        inline = self.inline_fn(self._make_summary())
        self.assertIn("WRITE-BACK", inline)

    def test_inline_shows_inert_candidates(self) -> None:
        """Inline must show inert_candidates."""
        inline = self.inline_fn(self._make_summary(candidates=3))
        self.assertIn("inert_candidates", inline)
        self.assertIn("3", inline)

    def test_inline_shows_uwg_committed(self) -> None:
        """Inline must show uwg_committed."""
        inline = self.inline_fn(self._make_summary(committed=1))
        self.assertIn("uwg_committed", inline)
        self.assertIn("1", inline)


class TestBuildStatusInertFields(unittest.TestCase):
    """build_resume_shipping_status must return inert writeback fields."""

    def test_status_has_inert_candidates(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status(inert_writeback_candidates=7)
        self.assertEqual(status["inert_writeback_candidates"], 7)

    def test_status_has_uwg_committed(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status(uwg_committed_writes=4)
        self.assertEqual(status["uwg_committed_writes"], 4)

    def test_status_defaults_zero(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status()
        self.assertEqual(status["inert_writeback_candidates"], 0)
        self.assertEqual(status["uwg_committed_writes"], 0)


class TestUWGClaimGuard(unittest.TestCase):
    """Guard against claiming durable writes without UWG receipt."""

    def test_no_claim_when_uwg_zero(self) -> None:
        """When uwg_committed_writes is 0, no claim of durable persistence."""
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary, format_executive_summary_markdown
        s = RuntimeExecutiveSummary(
            run_id="test",
            trace_id="test",
            target_company="ACME",
            target_role="Director",
            generation_mode="strategic_tailor",
            start_timestamp="2026-01-01T00:00:00+00:00",
            end_timestamp="2026-01-01T00:00:01+00:00",
            total_duration_ms=1000,
            sections=[],
            inert_writeback_candidates=5,
            uwg_committed_writes=0,
        )
        md = format_executive_summary_markdown(s)
        # Must show 0 committed, not imply persistence
        self.assertIn("uwg_committed_writes: 0", md)

    def test_can_show_nonzero_uwg(self) -> None:
        """When uwg_committed_writes is non-zero, display shows the count."""
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary, format_executive_summary_markdown
        s = RuntimeExecutiveSummary(
            run_id="test",
            trace_id="test",
            target_company="ACME",
            target_role="Director",
            generation_mode="strategic_tailor",
            start_timestamp="2026-01-01T00:00:00+00:00",
            end_timestamp="2026-01-01T00:00:01+00:00",
            total_duration_ms=1000,
            sections=[],
            inert_writeback_candidates=5,
            uwg_committed_writes=3,
        )
        md = format_executive_summary_markdown(s)
        self.assertIn("uwg_committed_writes: 3", md)


if __name__ == "__main__":
    unittest.main()
