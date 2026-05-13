"""W4 contract test: L6 must not appear in live generation pipeline display.

Verifies that:
1. No "L6" appears inside the live pipeline display sections
2. The live pipeline shows only U0->L1->L0->C0->PA->L2->Exit
3. L6 is relegated to POST-RUNTIME section only
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock


class TestNoL6InLivePathMarkdown(unittest.TestCase):
    """Markdown output must not show L6 in live pipeline."""

    def _make_summary(self):
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
            stages_executed=[
                "U0: Intake & Validation",
                "L1: Planning & Cognition",
                "L0: Routing & Dispatch",
                "C0: Evidence Retrieval",
                "PA: Prompt Assembly",
                "L2: Generation & Inference",
                "Exit: Finalization & Gates",
            ],
        )

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import format_executive_summary_markdown
        self.summary = self._make_summary()
        self.md = format_executive_summary_markdown(self.summary)

    def test_live_generation_pipeline_section_has_no_l6(self) -> None:
        """LIVE GENERATION PIPELINE section must not contain L6."""
        lines = self.md.split("\n")
        in_live_section = False
        for line in lines:
            if line.startswith("## LIVE GENERATION PIPELINE"):
                in_live_section = True
                continue
            if in_live_section and line.startswith("##"):
                break
            if in_live_section:
                self.assertNotIn("L6", line, f"L6 found in LIVE GENERATION PIPELINE: {line}")

    def test_arrow_pipeline_has_no_l6(self) -> None:
        """The arrow-format pipeline must not contain L6."""
        for line in self.md.split("\n"):
            if "->" in line and "U0" in line:
                self.assertNotIn("L6", line, f"L6 found in pipeline arrows: {line}")

    def test_post_runtime_section_exists(self) -> None:
        """POST-RUNTIME section must exist and contain L6 references."""
        self.assertIn("## POST-RUNTIME", self.md)

    def test_l6_in_post_runtime_only(self) -> None:
        """L6 Shadow Handoff must appear only in POST-RUNTIME section."""
        lines = self.md.split("\n")
        in_post_runtime = False
        l6_found_in_post_runtime = False
        for line in lines:
            if line.startswith("## POST-RUNTIME"):
                in_post_runtime = True
                continue
            if in_post_runtime and line.startswith("##"):
                in_post_runtime = False
                continue
            if in_post_runtime and "L6" in line:
                l6_found_in_post_runtime = True
        self.assertTrue(l6_found_in_post_runtime, "L6 Shadow Handoff not found in POST-RUNTIME")


class TestNoL6InLivePathInline(unittest.TestCase):
    """Inline display must not show L6 in live pipeline."""

    def _make_summary(self):
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
        )

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import display_runtime_summary_inline
        self.inline = display_runtime_summary_inline(self._make_summary())

    def test_inline_live_path_no_l6(self) -> None:
        """Inline LIVE GENERATION PIPELINE must not contain L6."""
        lines = self.inline.split("\n")
        in_live_path = False
        for line in lines:
            if "LIVE GENERATION PIPELINE" in line:
                in_live_path = True
                continue
            if in_live_path and "POST-RUNTIME" in line:
                break
            if in_live_path:
                self.assertNotIn("L6", line, f"L6 found in inline live path: {line}")

    def test_inline_post_runtime_has_l6(self) -> None:
        """Inline POST-RUNTIME must show L6-Handoff."""
        self.assertIn("L6-Handoff", self.inline)


class TestNoL6InConstant(unittest.TestCase):
    """RESUME_SHIPPING_LIVE_PATH constant must not contain L6."""

    def test_constant_has_no_l6(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import RESUME_SHIPPING_LIVE_PATH
        self.assertNotIn("L6", RESUME_SHIPPING_LIVE_PATH)

    def test_constant_has_all_live_stages(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import RESUME_SHIPPING_LIVE_PATH
        for stage in ("U0", "L1", "L0", "C0", "PA", "L2", "Exit"):
            self.assertIn(stage, RESUME_SHIPPING_LIVE_PATH)


class TestBuildStatusNoL6InLivePath(unittest.TestCase):
    """build_resume_shipping_status live_path must not contain L6."""

    def test_status_live_path_no_l6(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status()
        self.assertNotIn("L6", status["live_path"])

    def test_status_l6_is_post_runtime(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status()
        self.assertIn("POST_RUNTIME", status["l6_status"])


class TestGenerateSummaryStagesNoL6(unittest.TestCase):
    """Generated summary stages must not include L6."""

    def _make_mock_result(self, exit_status: str = "success") -> MagicMock:
        disp = MagicMock()
        disp.exit_status = exit_status
        result = MagicMock()
        result.disposition = disp
        result.artifact = None
        result.section_id = "headline"
        result.writeback_key = None
        return result

    def test_generated_stages_executed_no_l6(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import generate_runtime_executive_summary
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = generate_runtime_executive_summary(
                section_results=[self._make_mock_result()],
                shared_context={"target_company": "ACME", "target_role": "Director"},
                parent_trace_id="test-trace",
                run_dir=Path(tmpdir),
            )
        for stage in summary.stages_executed:
            self.assertNotIn("L6", stage)
            self.assertNotIn("Shadow", stage)


if __name__ == "__main__":
    unittest.main()
