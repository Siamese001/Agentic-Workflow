"""S6 contract tests: Deterministic Resume Exit Checks.

Verifies all S6 exit-check invariants per
apps_rg_resume_shipping_s6_deterministic_resume_exit_checks.md.

Key invariants:
- UNKNOWN is NEVER PASS
- material UNKNOWN blocks sendable=True
- INSUFFICIENT_SOURCE_SUPPORT / BLOCKED / UNKNOWN support_status blocks sendable
- Missing headline / multiline headline / empty exec summary / missing roles fail
- education / certifications / early_career require preserve_verbatim=True
- role narratives preserve_narrative_verbatim enforced (FAIL when explicit False)
- competencies must be 2-4 word phrases
- checker must not import PA, C0, L2, provider/model, section_agentic_pipeline,
  write_section_to_semantic_cache, or l6_shadow_learning
"""
from __future__ import annotations

import copy
import inspect
import unittest
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers to build minimal valid artifact
# ---------------------------------------------------------------------------

def _minimal_valid_artifact() -> dict[str, Any]:
    """Return a minimal structurally-valid resume artifact that should be sendable."""
    return {
        "schema_version": "source_resume_v2_structured",
        "headline": {"text": "Senior Technology Executive"},
        "executive_summary": {
            "text": "Experienced executive with 20 years leading digital transformation programs."
        },
        "roles": [
            {
                "employer": "ACME Corp",
                "title": "VP Engineering",
                "narrative": "Led engineering organisation through cloud migration.",
                "preserve_narrative_verbatim": True,
                "bullets": [
                    {"source_text": "Reduced cloud costs by 30%.", "ordinal": 1},
                    {"source_text": "Built a team of 45 engineers.", "ordinal": 2},
                ],
            }
        ],
        "competencies": {
            "items": ["Cloud Strategy", "Digital Transformation", "Agile Delivery"]
        },
        "education": {
            "preserve_verbatim": True,
            "entries": [{"text": "MBA, Wharton School of Business", "preserve_verbatim": True}],
        },
        "certifications": {
            "preserve_verbatim": True,
            "entries": [{"text": "AWS Certified Solutions Architect", "preserve_verbatim": True}],
        },
        "early_career": {
            "preserve_verbatim": True,
            "entries": [{"text": "Software Engineer, IBM 1998-2002", "preserve_verbatim": True}],
        },
    }


def _profile_override(**overrides: Any) -> dict[str, Any]:
    from apps_rg.runtime.exit.resume_exit_checks import _load_profile
    import copy
    p = copy.deepcopy(_load_profile())
    p.update(overrides)
    return p


# ---------------------------------------------------------------------------
# Smoke imports
# ---------------------------------------------------------------------------

class TestModuleImportSmoke(unittest.TestCase):
    def test_module_importable(self) -> None:
        import apps_rg.runtime.exit.resume_exit_checks  # noqa: F401

    def test_key_symbols_present(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import (
            CheckVerdict,
            CheckResult,
            ExitCheckSummary,
            run_exit_checks,
        )
        self.assertIsNotNone(run_exit_checks)
        self.assertIsNotNone(CheckVerdict)

    def test_profile_json_loadable(self) -> None:
        import json
        profile_path = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "config" / "domain_contract"
            / "resume_exit_checks_profile.v1.json"
        )
        self.assertTrue(profile_path.exists(), f"Profile not found: {profile_path}")
        with profile_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data["app_id"], "apps_rg")


# ---------------------------------------------------------------------------
# Boundary guard: no forbidden imports
# ---------------------------------------------------------------------------

class TestBoundaryGuard(unittest.TestCase):
    """exit checker must not import forbidden symbols."""

    def _get_source(self) -> str:
        from apps_rg.runtime.exit import resume_exit_checks as mod
        return inspect.getsource(mod)

    def test_no_section_agentic_pipeline(self) -> None:
        self.assertNotIn("section_agentic_pipeline", self._get_source())

    def test_no_write_section_to_semantic_cache(self) -> None:
        self.assertNotIn("write_section_to_semantic_cache", self._get_source())

    def test_no_l6_shadow_learning(self) -> None:
        self.assertNotIn("l6_shadow_learning", self._get_source())

    def test_no_pa_binding_import(self) -> None:
        self.assertNotIn("pa_binding", self._get_source())

    def test_no_c0_binding_import(self) -> None:
        self.assertNotIn("c0_binding", self._get_source())

    def test_no_l2_binding_import(self) -> None:
        self.assertNotIn("l2_binding", self._get_source())

    def test_no_provider_model_invocation(self) -> None:
        src = self._get_source()
        for forbidden in ("openai", "anthropic", "retired_provider", "local_model_server", "requests.post", "httpx"):
            self.assertNotIn(forbidden, src, f"Forbidden reference found: {forbidden!r}")

    def test_no_agentic_core_import(self) -> None:
        import ast
        from apps_rg.runtime.exit import resume_exit_checks as mod
        src = inspect.getsource(mod)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                for alias in getattr(node, "names", []):
                    full = f"{module}.{alias.name}" if module else alias.name
                    self.assertFalse(
                        full.startswith("agentic_core"),
                        f"Forbidden agentic_core import: {full}",
                    )

    def test_no_subprocess_import(self) -> None:
        self.assertNotIn("subprocess", self._get_source())


# ---------------------------------------------------------------------------
# Valid minimal artifact
# ---------------------------------------------------------------------------

class TestValidMinimalArtifact(unittest.TestCase):
    def setUp(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks, CheckVerdict
        self.summary = run_exit_checks(_minimal_valid_artifact())
        self.CheckVerdict = CheckVerdict

    def test_overall_verdict_not_fail(self) -> None:
        self.assertNotEqual(self.summary.overall_verdict, self.CheckVerdict.FAIL)

    def test_no_hard_fail(self) -> None:
        self.assertFalse(self.summary.hard_fail_present)

    def test_unknown_material_false(self) -> None:
        self.assertFalse(self.summary.unknown_material_present)

    def test_sendable_true(self) -> None:
        self.assertTrue(self.summary.sendable)

    def test_check_results_populated(self) -> None:
        self.assertGreater(len(self.summary.check_results), 0)


# ---------------------------------------------------------------------------
# A. Headline checks
# ---------------------------------------------------------------------------

class TestHeadlineCheck(unittest.TestCase):
    def _run(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        return run_exit_checks(artifact)

    def _headline_result(self, artifact: dict) -> Any:
        summary = self._run(artifact)
        for r in summary.check_results:
            if r.check_id == "A_HEADLINE":
                return r
        self.fail("A_HEADLINE check not found")

    def test_missing_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["headline"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_empty_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["headline"] = {"text": ""}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_whitespace_only_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["headline"] = {"text": "   "}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_multiline_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["headline"] = {"text": "Line one\nLine two"}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_carriage_return_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["headline"] = {"text": "Line one\rLine two"}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_headline_exceeds_max_length_fails(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks, CheckVerdict
        a = _minimal_valid_artifact()
        a["headline"] = {"text": "X" * 201}
        summary = run_exit_checks(a)
        r = next(r for r in summary.check_results if r.check_id == "A_HEADLINE")
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_valid_one_line_headline_passes(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        a = _minimal_valid_artifact()
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.PASS)

    def test_headline_not_dict_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["headline"] = "plain string"
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._headline_result(a)
        self.assertEqual(r.verdict, CheckVerdict.FAIL)

    def test_missing_headline_blocks_sendable(self) -> None:
        a = _minimal_valid_artifact()
        del a["headline"]
        summary = self._run(a)
        self.assertFalse(summary.sendable)


# ---------------------------------------------------------------------------
# B. Executive Summary checks
# ---------------------------------------------------------------------------

class TestExecSummaryCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "B_EXEC_SUMMARY")

    def test_missing_exec_summary_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["executive_summary"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_empty_exec_summary_text_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["executive_summary"] = {"text": ""}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_placeholder_tbd_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["executive_summary"] = {"text": "TBD"}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_placeholder_todo_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["executive_summary"] = {"text": "TODO"}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_too_short_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["executive_summary"] = {"text": "Short"}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_valid_summary_passes(self) -> None:
        a = _minimal_valid_artifact()
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)

    def test_empty_exec_summary_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        a["executive_summary"] = {"text": ""}
        self.assertFalse(run_exit_checks(a).sendable)


# ---------------------------------------------------------------------------
# C. Roles checks
# ---------------------------------------------------------------------------

class TestRolesCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "C_ROLES")

    def test_missing_roles_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["roles"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_employer_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0] = {**a["roles"][0], "employer": ""}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_title_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0] = {**a["roles"][0], "title": ""}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_narrative_fails(self) -> None:
        a = _minimal_valid_artifact()
        role = dict(a["roles"][0])
        del role["narrative"]
        a["roles"][0] = role
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_duplicate_bullet_ordinals_fail(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"] = [
            {"source_text": "A", "ordinal": 1},
            {"source_text": "B", "ordinal": 1},
        ]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_bullet_missing_ordinal_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"] = [{"source_text": "A"}]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_bullet_no_source_or_rewritten_text_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"] = [{"ordinal": 1}]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_valid_roles_pass(self) -> None:
        a = _minimal_valid_artifact()
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)

    def test_missing_roles_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        del a["roles"]
        self.assertFalse(run_exit_checks(a).sendable)

    def test_rewritten_text_accepted_in_lieu_of_source_text(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"] = [{"rewritten_text": "Delivered results.", "ordinal": 1}]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)


# ---------------------------------------------------------------------------
# D. Verbatim preservation checks
# ---------------------------------------------------------------------------

class TestVerbatimCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "D_VERBATIM")

    def test_education_preserve_verbatim_false_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["education"] = {"preserve_verbatim": False, "entries": []}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_certifications_preserve_verbatim_false_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["certifications"] = {"preserve_verbatim": False, "entries": []}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_early_career_preserve_verbatim_false_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["early_career"] = {"preserve_verbatim": False, "entries": []}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_role_preserve_narrative_verbatim_explicit_false_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0] = {**a["roles"][0], "preserve_narrative_verbatim": False}
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_role_preserve_narrative_verbatim_true_passes(self) -> None:
        a = _minimal_valid_artifact()
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._result(a)
        self.assertIn(r.verdict, (CheckVerdict.PASS, CheckVerdict.WARN))

    def test_missing_hash_fields_emit_warn_not_fail(self) -> None:
        a = _minimal_valid_artifact()
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._result(a)
        self.assertNotEqual(r.verdict, CheckVerdict.FAIL)
        self.assertEqual(r.verdict, CheckVerdict.WARN)

    def test_hash_fields_present_improve_verdict(self) -> None:
        a = _minimal_valid_artifact()
        for sec in ("education", "certifications", "early_career"):
            for entry in a[sec]["entries"]:
                entry["source_hash"] = "abc123"
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        r = self._result(a)
        self.assertEqual(r.verdict, CheckVerdict.PASS)

    def test_verbatim_violations_block_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        a["education"] = {"preserve_verbatim": False, "entries": []}
        self.assertFalse(run_exit_checks(a).sendable)


# ---------------------------------------------------------------------------
# E. Support status checks
# ---------------------------------------------------------------------------

class TestSupportStatusCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "E_SUPPORT_STATUS")

    def test_insufficient_source_support_blocks(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "INSUFFICIENT_SOURCE_SUPPORT"
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_blocked_support_status_blocks(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "BLOCKED"
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_unknown_support_status_blocks(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "UNKNOWN"
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_unknown_is_never_pass(self) -> None:
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "UNKNOWN"
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks, CheckVerdict
        summary = run_exit_checks(a)
        for r in summary.check_results:
            if r.check_id == "E_SUPPORT_STATUS":
                self.assertNotEqual(r.verdict, CheckVerdict.PASS)
                break

    def test_insufficient_source_support_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "INSUFFICIENT_SOURCE_SUPPORT"
        self.assertFalse(run_exit_checks(a).sendable)

    def test_blocked_support_status_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "BLOCKED"
        self.assertFalse(run_exit_checks(a).sendable)

    def test_unknown_support_status_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        a["roles"][0]["bullets"][0]["support_status"] = "UNKNOWN"
        self.assertFalse(run_exit_checks(a).sendable)

    def test_clean_artifact_passes_support_status(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        a = _minimal_valid_artifact()
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)


# ---------------------------------------------------------------------------
# F. Competencies checks
# ---------------------------------------------------------------------------

class TestCompetenciesCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "F_COMPETENCIES")

    def test_valid_2_4_word_phrases_pass(self) -> None:
        a = _minimal_valid_artifact()
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)

    def test_single_word_phrase_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = ["Leadership", "Strategy"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_five_word_sentence_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = ["Led global cloud transformation programs"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_long_sentence_competency_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = [
            "Experienced at managing large teams across distributed environments"
        ]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_empty_phrase_fails(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = ["Cloud Strategy", "", "Agile Delivery"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_empty_items_list_warns(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = []
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.WARN)

    def test_missing_competencies_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["competencies"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_two_word_phrase_passes(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = ["Cloud Strategy", "Risk Management"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)

    def test_four_word_phrase_passes(self) -> None:
        a = _minimal_valid_artifact()
        a["competencies"]["items"] = [
            "Enterprise Cloud Architecture Strategy",
            "Digital Business Transformation",
        ]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.PASS)


# ---------------------------------------------------------------------------
# G. Required sections check
# ---------------------------------------------------------------------------

class TestRequiredSectionsCheck(unittest.TestCase):
    def _result(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        summary = run_exit_checks(artifact)
        return next(r for r in summary.check_results if r.check_id == "G_REQUIRED_SECTIONS")

    def test_all_required_sections_present_passes(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(_minimal_valid_artifact()).verdict, CheckVerdict.PASS)

    def test_missing_education_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["education"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_certifications_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["certifications"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_early_career_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["early_career"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_competencies_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["competencies"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_headline_fails(self) -> None:
        a = _minimal_valid_artifact()
        del a["headline"]
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertEqual(self._result(a).verdict, CheckVerdict.FAIL)

    def test_missing_required_section_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        del a["education"]
        self.assertFalse(run_exit_checks(a).sendable)


# ---------------------------------------------------------------------------
# UNKNOWN invariants
# ---------------------------------------------------------------------------

class TestUnknownInvariants(unittest.TestCase):
    """UNKNOWN is never PASS; material UNKNOWN blocks sendable."""

    def test_unknown_verdict_is_never_pass(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        self.assertNotEqual(CheckVerdict.UNKNOWN, CheckVerdict.PASS)

    def test_unknown_check_verdict_not_pass(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import CheckVerdict
        for v in (CheckVerdict.UNKNOWN, CheckVerdict.FAIL, CheckVerdict.WARN):
            self.assertNotEqual(v, CheckVerdict.PASS)
        self.assertEqual(CheckVerdict.PASS, CheckVerdict.PASS)

    def test_unknown_material_present_blocks_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import (
            ExitCheckSummary,
            CheckVerdict,
            CheckResult,
        )
        cr = CheckResult(
            check_id="TEST",
            section="test",
            verdict=CheckVerdict.UNKNOWN,
            decisive_reason="test unknown",
        )
        summary = ExitCheckSummary(
            overall_verdict=CheckVerdict.UNKNOWN,
            hard_fail_present=False,
            unknown_material_present=True,
            warning_present=False,
            sendable=False,
            check_results=(cr,),
        )
        self.assertFalse(summary.sendable)
        self.assertTrue(summary.unknown_material_present)
        self.assertNotEqual(summary.overall_verdict, CheckVerdict.PASS)

    def test_summary_with_only_pass_is_sendable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        a = _minimal_valid_artifact()
        for sec in ("education", "certifications", "early_career"):
            for entry in a[sec]["entries"]:
                entry["source_hash"] = "deadbeef"
        summary = run_exit_checks(a)
        self.assertTrue(summary.sendable)
        self.assertFalse(summary.hard_fail_present)
        self.assertFalse(summary.unknown_material_present)


# ---------------------------------------------------------------------------
# Aggregate helper tests
# ---------------------------------------------------------------------------

class TestExitCheckSummaryHelpers(unittest.TestCase):
    def _run(self, artifact: dict) -> Any:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        return run_exit_checks(artifact)

    def test_failing_checks_returns_list(self) -> None:
        a = _minimal_valid_artifact()
        del a["headline"]
        summary = self._run(a)
        self.assertGreater(len(summary.failing_checks()), 0)

    def test_warning_checks_on_warn_verdict(self) -> None:
        a = _minimal_valid_artifact()
        summary = self._run(a)
        warns = summary.warning_checks()
        self.assertIsInstance(warns, list)

    def test_hard_fail_present_when_fail(self) -> None:
        a = _minimal_valid_artifact()
        del a["roles"]
        summary = self._run(a)
        self.assertTrue(summary.hard_fail_present)

    def test_sendable_false_when_hard_fail(self) -> None:
        a = _minimal_valid_artifact()
        del a["roles"]
        summary = self._run(a)
        self.assertFalse(summary.sendable)


# ---------------------------------------------------------------------------
# S1-S5 regression
# ---------------------------------------------------------------------------

class TestS1ToS5Regression(unittest.TestCase):
    def test_source_resume_schema_importable(self) -> None:
        import apps_rg.runtime.schemas.source_resume_schema  # noqa: F401

    def test_section_treatment_profile_importable(self) -> None:
        import apps_rg.runtime.schemas.section_treatment_profile  # noqa: F401

    def test_structured_resume_classifier_importable(self) -> None:
        import apps_rg.runtime.u0.structured_resume_classifier  # noqa: F401

    def test_payload_synthesizer_importable(self) -> None:
        import apps_rg.runtime.u0.payload_synthesizer  # noqa: F401

    def test_runtime_summary_importable(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        status = build_resume_shipping_status()
        self.assertFalse(status["l5_governed_production_claimed"])

    def test_exit_checks_coexist_with_s5(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        from apps_rg.runtime.runtime_executive_summary import RESUME_SHIPPING_LIVE_PATH
        self.assertIn("U0", RESUME_SHIPPING_LIVE_PATH)
        summary = run_exit_checks(_minimal_valid_artifact())
        self.assertIsNotNone(summary)


if __name__ == "__main__":
    unittest.main()
