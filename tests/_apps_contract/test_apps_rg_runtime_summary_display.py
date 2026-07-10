"""apps-test-model: MIGRATION.

S5 contract tests: Runtime Executive Summary Display Fix.

Verifies that the runtime summary display for apps_rg correctly reflects the
live resume-generation path and accurately labels inactive/future components.

S5 Display Truth Table (per apps_rg_resume_shipping_s5_runtime_summary_display_fix.md):
1. Live path must be shown as: U0 -> L1 -> L0 -> C0 -> PA -> L2 -> Exit
2. L6 must be displayed as: POST_RUNTIME / FUTURE_RUN_ONLY / NOT_IN_LIVE_GENERATION_PATH
3. Semantic cache write status must contain: DISABLED_OR_PROPOSAL_ONLY_FOR_RESUME_SHIPPING
4. apps_rg_dispatch_section_pipeline must not be displayed as active.
5. section_agentic_pipeline must not be displayed as active.
6. l6_shadow_learning must not be displayed as active.
7. Runtime summary must NOT claim L6 is live, cache writes are durable,
   section_pipeline is active, or L5 governed-production is complete.
8. Runtime summary MAY say: Resume Shipping Critical Path active, S0.5 cache guard enforced,
   S4 structured resume metadata available, governed-production track not complete.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


class TestRuntimeSummaryModuleImport(unittest.TestCase):
    """Smoke: module and key symbols import without error."""

    def test_module_importable(self) -> None:
        import apps_rg.runtime.runtime_executive_summary  # noqa: F401

    def test_key_symbols_present(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import (
            RESUME_SHIPPING_LIVE_PATH,
            RuntimeExecutiveSummary,
            build_resume_shipping_status,
            display_runtime_summary_inline,
            format_executive_summary_markdown,
            generate_runtime_executive_summary,
            write_runtime_summary_to_runs,
        )
        self.assertIsNotNone(RuntimeExecutiveSummary)
        self.assertIsNotNone(generate_runtime_executive_summary)
        self.assertIsNotNone(format_executive_summary_markdown)
        self.assertIsNotNone(display_runtime_summary_inline)
        self.assertIsNotNone(write_runtime_summary_to_runs)
        self.assertIsNotNone(build_resume_shipping_status)
        self.assertIsNotNone(RESUME_SHIPPING_LIVE_PATH)


class TestResumeLivePathConstant(unittest.TestCase):
    """RESUME_SHIPPING_LIVE_PATH must exactly state the live path."""

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import RESUME_SHIPPING_LIVE_PATH
        self.live_path = RESUME_SHIPPING_LIVE_PATH

    def test_live_path_contains_u0(self) -> None:
        self.assertIn("U0", self.live_path)

    def test_live_path_contains_l1(self) -> None:
        self.assertIn("L1", self.live_path)

    def test_live_path_contains_l0(self) -> None:
        self.assertIn("L0", self.live_path)

    def test_live_path_contains_c0(self) -> None:
        self.assertIn("C0", self.live_path)

    def test_live_path_contains_pa(self) -> None:
        self.assertIn("PA", self.live_path)

    def test_live_path_contains_l2(self) -> None:
        self.assertIn("L2", self.live_path)

    def test_live_path_contains_exit(self) -> None:
        self.assertIn("Exit", self.live_path)

    def test_live_path_does_not_contain_l6(self) -> None:
        self.assertNotIn("L6", self.live_path)

    def test_live_path_does_not_contain_cache(self) -> None:
        self.assertNotIn("Cache", self.live_path.replace("U0 -> L1 -> L0 -> C0", ""))


class TestBuildResumeshippingStatus(unittest.TestCase):
    """build_resume_shipping_status() truth table assertions."""

    def setUp(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        self.status = build_resume_shipping_status()

    # --- live_path ---
    def test_live_path_key_present(self) -> None:
        self.assertIn("live_path", self.status)

    def test_live_path_has_u0_l1_l0_c0_pa_l2_exit(self) -> None:
        lp = str(self.status["live_path"])
        for stage in ("U0", "L1", "L0", "C0", "PA", "L2", "Exit"):
            self.assertIn(stage, lp, f"live_path missing stage: {stage}")

    def test_live_path_no_l6(self) -> None:
        self.assertNotIn("L6", str(self.status["live_path"]))

    # --- l6_status ---
    def test_l6_status_post_runtime(self) -> None:
        self.assertIn("POST_RUNTIME", str(self.status["l6_status"]))

    def test_l6_status_future_run_only(self) -> None:
        self.assertIn("FUTURE_RUN_ONLY", str(self.status["l6_status"]))

    def test_l6_status_not_in_live_path(self) -> None:
        self.assertIn("NOT_IN_LIVE_GENERATION_PATH", str(self.status["l6_status"]))

    # --- cache_write_status ---
    def test_cache_write_status_disabled(self) -> None:
        self.assertIn(
            "DISABLED_OR_PROPOSAL_ONLY_FOR_RESUME_SHIPPING",
            str(self.status["cache_write_status"]),
        )

    # --- section pipeline statuses ---
    def test_section_pipeline_not_active(self) -> None:
        self.assertEqual(self.status["section_pipeline_status"], "NOT_ACTIVE")

    def test_section_dispatch_not_active(self) -> None:
        self.assertEqual(self.status["section_dispatch_status"], "NOT_ACTIVE")

    def test_l6_shadow_learning_not_active(self) -> None:
        self.assertEqual(self.status["l6_shadow_learning_status"], "NOT_ACTIVE")

    # --- L5-governed production ---
    def test_l5_governed_not_claimed(self) -> None:
        self.assertIs(self.status["l5_governed_production_claimed"], False)

    # --- S0.5 and S4 ---
    def test_s05_cache_guard_enforced(self) -> None:
        self.assertIn("ENFORCED", str(self.status["s05_cache_guard"]))

    def test_s4_structured_resume_available(self) -> None:
        self.assertIn("AVAILABLE", str(self.status["s4_structured_resume_metadata"]))

    def test_governed_production_not_complete(self) -> None:
        self.assertIn("NOT_COMPLETE", str(self.status["governed_production_track"]))


class TestRuntimeExecutiveSummaryDefaults(unittest.TestCase):
    """RuntimeExecutiveSummary dataclass defaults reflect S5 truths."""

    def _make_summary(self, **kwargs: Any):
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        defaults = {
            "run_id": "test-run",
            "trace_id": "test-trace",
            "target_company": "ACME",
            "target_role": "Director",
            "generation_mode": "strategic_tailor",
            "start_timestamp": "2026-01-01T00:00:00+00:00",
            "end_timestamp": "2026-01-01T00:00:01+00:00",
            "total_duration_ms": 1000,
            "sections": [],
        }
        defaults.update(kwargs)
        return RuntimeExecutiveSummary(**defaults)

    def test_pipeline_depth_no_l6(self) -> None:
        s = self._make_summary()
        self.assertNotIn("L6", s.pipeline_depth)

    def test_pipeline_depth_contains_live_stages(self) -> None:
        s = self._make_summary()
        for stage in ("U0", "L1", "L0", "C0", "PA", "L2", "Exit"):
            self.assertIn(stage, s.pipeline_depth)

    def test_pipeline_depth_contains_resume_shipping_label(self) -> None:
        s = self._make_summary()
        self.assertIn("Resume Shipping Critical Path", s.pipeline_depth)

    def test_l6_status_post_runtime(self) -> None:
        s = self._make_summary()
        self.assertIn("POST_RUNTIME", s.l6_status)

    def test_cache_write_status_disabled(self) -> None:
        s = self._make_summary()
        self.assertIn("DISABLED_OR_PROPOSAL_ONLY", s.cache_write_status)

    def test_section_pipeline_not_active(self) -> None:
        s = self._make_summary()
        self.assertEqual(s.section_pipeline_status, "NOT_ACTIVE")

    def test_section_dispatch_not_active(self) -> None:
        s = self._make_summary()
        self.assertEqual(s.section_dispatch_status, "NOT_ACTIVE")

    def test_l6_shadow_learning_not_active(self) -> None:
        s = self._make_summary()
        self.assertEqual(s.l6_shadow_learning_status, "NOT_ACTIVE")

    def test_l5_governed_not_claimed(self) -> None:
        s = self._make_summary()
        self.assertIs(s.l5_governed_production_claimed, False)

    def test_cache_writes_zero_by_default(self) -> None:
        s = self._make_summary()
        self.assertEqual(s.cache_writes, 0)

    def test_stages_executed_live_path_only(self) -> None:
        s = self._make_summary()
        # Default is empty list; when populated by generate_ it should have no L6/Cache
        for stage in s.stages_executed:
            self.assertNotIn("L6", stage, f"L6 must not appear in stages_executed: {stage}")
            self.assertNotIn("Shadow", stage, f"Shadow must not appear in stages_executed: {stage}")
            self.assertNotIn("Cache: Writeback", stage, f"Cache: Writeback must not appear in stages_executed: {stage}")


class TestGeneratedSummaryStagesExecuted(unittest.TestCase):
    """generate_runtime_executive_summary stages_executed list must be L6/cache-free."""

    def _make_mock_result(self, exit_status: str = "success") -> MagicMock:
        disp = MagicMock()
        disp.exit_status = exit_status
        result = MagicMock()
        result.disposition = disp
        result.artifact = None
        result.section_id = "headline"
        result.writeback_key = None
        return result

    def test_stages_executed_no_l6(self) -> None:
        import tempfile

        from apps_rg.runtime.runtime_executive_summary import generate_runtime_executive_summary
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

    def test_stages_executed_no_cache_writeback(self) -> None:
        import tempfile

        from apps_rg.runtime.runtime_executive_summary import generate_runtime_executive_summary
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = generate_runtime_executive_summary(
                section_results=[self._make_mock_result()],
                shared_context={"target_company": "ACME", "target_role": "Director"},
                parent_trace_id="test-trace",
                run_dir=Path(tmpdir),
            )
        for stage in summary.stages_executed:
            self.assertNotIn("Cache: Writeback", stage)
            self.assertNotIn("Writeback", stage)

    def test_cache_writes_always_zero(self) -> None:
        import tempfile

        from apps_rg.runtime.runtime_executive_summary import generate_runtime_executive_summary
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = generate_runtime_executive_summary(
                section_results=[self._make_mock_result("success"), self._make_mock_result("success")],
                shared_context={"target_company": "ACME", "target_role": "Director"},
                parent_trace_id="test-trace",
                run_dir=Path(tmpdir),
            )
        self.assertEqual(summary.cache_writes, 0)

    def test_per_section_stages_no_l6_shadow_cache(self) -> None:
        import tempfile

        from apps_rg.runtime.runtime_executive_summary import (
            generate_runtime_executive_summary,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = generate_runtime_executive_summary(
                section_results=[self._make_mock_result("success")],
                shared_context={"target_company": "ACME", "target_role": "Director"},
                parent_trace_id="test-trace",
                run_dir=Path(tmpdir),
            )
        forbidden_stage_names = {"L6_shadow_learning", "Cache_writeback"}
        for sec in summary.sections:
            for stage in sec.stages:
                self.assertNotIn(stage.stage_name, forbidden_stage_names,
                    f"Forbidden stage '{stage.stage_name}' found in section '{sec.section_id}'")


class TestFormatMarkdownDisplayTruths(unittest.TestCase):
    """format_executive_summary_markdown output must assert S5 truths."""

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
        self.md = format_executive_summary_markdown(self._make_summary())

    def test_markdown_shows_live_path_label(self) -> None:
        self.assertIn("Resume Shipping Critical Path", self.md)

    def test_markdown_shows_l6_post_runtime(self) -> None:
        self.assertIn("POST_RUNTIME", self.md)

    def test_markdown_shows_cache_disabled(self) -> None:
        self.assertIn("DISABLED_OR_PROPOSAL_ONLY_FOR_RESUME_SHIPPING", self.md)

    def test_markdown_shows_section_pipeline_not_active(self) -> None:
        self.assertIn("section_agentic_pipeline", self.md)
        # value must be NOT_ACTIVE
        self.assertIn("NOT_ACTIVE", self.md)

    def test_markdown_shows_section_dispatch_not_active(self) -> None:
        self.assertIn("apps_rg_dispatch_section_pipeline", self.md)

    def test_markdown_shows_l6_shadow_learning_not_active(self) -> None:
        self.assertIn("l6_shadow_learning", self.md)

    def test_markdown_l5_governed_false(self) -> None:
        self.assertIn("L5-Governed Production Claimed", self.md)
        self.assertIn("False", self.md)

    def test_markdown_no_l6_in_stages_list(self) -> None:
        # The numbered live-stages list must not contain L6
        for line in self.md.split("\n"):
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                self.assertNotIn("L6", line, f"L6 found in numbered stages list: {line}")

    def test_markdown_shows_s05_cache_guard_enforced(self) -> None:
        self.assertIn("S0.5 Cache Guard", self.md)
        self.assertIn("ENFORCED", self.md)

    def test_markdown_shows_s4_metadata_available(self) -> None:
        self.assertIn("S4 Structured Resume Metadata", self.md)
        self.assertIn("AVAILABLE", self.md)

    def test_markdown_shows_governed_production_not_complete(self) -> None:
        self.assertIn("NOT_COMPLETE", self.md)

    def test_markdown_no_claim_l5_governed_production_release(self) -> None:
        # Must NOT positively claim L5-governed production is complete
        lower = self.md.lower()
        self.assertNotIn("l5-governed production release complete", lower)
        self.assertNotIn("governed-production: complete", lower)

    def test_markdown_cache_writes_zero_with_disabled_label(self) -> None:
        self.assertIn("DISABLED", self.md)


class TestInlineDisplayTruths(unittest.TestCase):
    """display_runtime_summary_inline output must assert S5 truths."""

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

    def test_inline_shows_live_path_u0_l1_l0_c0_pa_l2_exit(self) -> None:
        for stage in ("U0", "L1", "L0", "C0", "PA", "L2", "Exit"):
            self.assertIn(stage, self.inline)

    def test_inline_shows_l6_post_runtime(self) -> None:
        self.assertIn("POST_RUNTIME", self.inline)

    def test_inline_shows_cache_disabled(self) -> None:
        self.assertIn("DISABLED", self.inline)

    def test_inline_shows_s05_cache_guard_enforced(self) -> None:
        self.assertIn("S0.5 cache guard", self.inline)
        self.assertIn("ENFORCED", self.inline)

    def test_inline_no_l6_live_claim(self) -> None:
        # L6 must not appear as an active live stage in the pipeline row
        self.assertNotIn("-> L6", self.inline)

    def test_inline_no_cache_writeback_count(self) -> None:
        # Old pattern "N cache writebacks" must be gone
        import re
        pattern = re.compile(r"\d+\s+cache\s+writebacks", re.IGNORECASE)
        self.assertIsNone(pattern.search(self.inline))

    def test_inline_no_shadow_spans_count(self) -> None:
        # Old pattern "N shadow spans" must be gone
        import re
        pattern = re.compile(r"\d+\s+shadow\s+spans", re.IGNORECASE)
        self.assertIsNone(pattern.search(self.inline))

    def test_inline_l5_not_claimed(self) -> None:
        self.assertIn("NOT_CLAIMED", self.inline)


class TestForbiddenReactivationGuard(unittest.TestCase):
    """Reactivation guard: forbidden symbols must not be importable from dispatch paths."""

    def test_section_pipeline_availability_flag_is_removed(self) -> None:
        from apps_rg.runtime.dispatch import apps_rg_dispatch as mod
        self.assertFalse(hasattr(mod, "SECTION_PIPELINE_AVAILABLE"))

    def test_apps_rg_dispatch_section_pipeline_not_in_all(self) -> None:
        from apps_rg.runtime.dispatch import apps_rg_dispatch as mod
        self.assertNotIn("apps_rg_dispatch_section_pipeline", getattr(mod, "__all__", []))

    def test_dispatch_section_pipeline_symbol_is_removed(self) -> None:
        from apps_rg.runtime.dispatch import apps_rg_dispatch as mod
        self.assertFalse(hasattr(mod, "apps_rg_dispatch_section_pipeline"))

    def test_l6_shadow_learning_not_imported_in_dispatch(self) -> None:
        import inspect

        from apps_rg.runtime.dispatch import apps_rg_dispatch as mod
        source = inspect.getsource(mod)
        # Must not import l6_shadow_learning
        self.assertNotIn("l6_shadow_learning", source.replace("# ", "# COMMENT:"))

    def test_section_agentic_pipeline_not_active_in_dispatch(self) -> None:
        import inspect

        from apps_rg.runtime.dispatch import apps_rg_dispatch as mod
        source = inspect.getsource(mod)
        # section_agentic_pipeline imports must be absent (not just commented)
        import ast
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in getattr(node, "names", []):
                    self.assertNotEqual(
                        alias.name, "section_agentic_pipeline",
                        "section_agentic_pipeline must not be imported in dispatch module",
                    )


class TestS5RegressionAgainstS1S4(unittest.TestCase):
    """Regression: S1-S4 targeted tests still importable after S5 changes."""

    def test_source_resume_schema_importable(self) -> None:
        import apps_rg.runtime.schemas.source_resume_schema  # noqa: F401

    def test_section_treatment_profile_importable(self) -> None:
        import apps_rg.runtime.schemas.section_treatment_profile  # noqa: F401

    def test_structured_resume_classifier_importable(self) -> None:
        import apps_rg.runtime.u0.structured_resume_classifier  # noqa: F401

    def test_u0_binding_importable(self) -> None:
        import apps_rg.runtime.bindings.u0_binding  # noqa: F401

    def test_runtime_summary_importable_after_s5(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import (
            build_resume_shipping_status,
        )
        status = build_resume_shipping_status()
        self.assertFalse(status["l5_governed_production_claimed"])


if __name__ == "__main__":
    unittest.main()
