"""S8: Manual Section Review Harness — contract tests.

Verifies:
- review packet contains all required top-level fields
- sections include headline, executive_summary, competencies, roles,
  education, certifications, early_career
- role bullets produce per-bullet review entries with ordinal
- reviewer_decision defaults to UNREVIEWED
- safe_to_send defaults false
- APPROVE can be represented but does not auto-send (only after explicit set)
- missing deterministic checks create UNKNOWN issue, not PASS
- INSUFFICIENT_SOURCE_SUPPORT/BLOCKED/UNKNOWN support status makes safe_to_send false
- markdown output includes all major sections
- markdown output includes reviewer placeholders
- harness does not mutate input resume
- harness does not import PA, C0, L2, provider/model, section_agentic_pipeline,
  write_section_to_semantic_cache, l6_shadow_learning, or fact_vectors
- existing S1-S7 targeted tests still importable
"""
from __future__ import annotations

import ast
import inspect
import json
import unittest
from copy import deepcopy
from typing import Any


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _minimal_resume() -> dict[str, Any]:
    return {
        "headline": {"text": "Senior IT Executive", "treatment_tier": "HEAVY"},
        "executive_summary": {
            "text": "Experienced IT leader with 20+ years driving digital transformation.",
            "treatment_tier": "HEAVY",
            "support_status": "PASS",
        },
        "competencies": {
            "items": ["Cloud Strategy", "Digital Transformation", "Vendor Management"],
            "support_status": "PASS",
        },
        "roles": [
            {
                "employer": "Acme Corp",
                "title": "VP of IT",
                "narrative": "Led IT function across 3 business units.",
                "support_status": "PASS",
                "bullets": [
                    {"ordinal": 1, "source_text": "Reduced cloud spend by 30%", "support_status": "PASS"},
                    {"ordinal": 2, "source_text": "Launched ERP transformation", "support_status": "PASS"},
                ],
            }
        ],
        "education": {"text": "B.Sc. Computer Science, State University 1998"},
        "certifications": {"text": "AWS Certified Solutions Architect"},
        "early_career": {"text": "Systems analyst at StartupCo, 1994-1996"},
    }


def _minimal_exit_checks() -> dict[str, Any]:
    return {
        "headline": "PASS",
        "executive_summary": "PASS",
        "competencies": "PASS",
        "role_0_narrative": "PASS",
        "role_0_bullet_1": "PASS",
        "role_0_bullet_2": "PASS",
        "education": "PASS",
        "certifications": "PASS",
        "early_career": "PASS",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestModuleImportSmoke(unittest.TestCase):

    def test_module_importable(self) -> None:
        from apps_rg.runtime.review.manual_section_review import (
            build_review_packet,
            format_review_packet_markdown,
            review_packet_to_dict,
            ReviewPacket,
            SectionReview,
        )
        self.assertIsNotNone(build_review_packet)

    def test_profile_json_loadable(self) -> None:
        from pathlib import Path
        p = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "config" / "domain_contract"
            / "resume_manual_section_review_profile.v1.json"
        )
        self.assertTrue(p.exists(), f"Profile not found: {p}")
        with p.open(encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data["app_id"], "apps_rg")


class TestBoundaryGuard(unittest.TestCase):

    def _get_imports(self) -> list[str]:
        import apps_rg.runtime.review.manual_section_review as mod
        tree = ast.parse(inspect.getsource(mod))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        return imported

    def test_no_agentic_core(self) -> None:
        for m in self._get_imports():
            self.assertFalse(m.startswith("agentic_core"), f"Forbidden: {m}")

    def test_no_pa_binding(self) -> None:
        self.assertFalse(any("pa_binding" in m for m in self._get_imports()))

    def test_no_l2_binding(self) -> None:
        self.assertFalse(any("l2_binding" in m for m in self._get_imports()))

    def test_no_c0_binding(self) -> None:
        self.assertFalse(any("c0_binding" in m for m in self._get_imports()))

    def test_no_openai(self) -> None:
        self.assertFalse(any(m.startswith("openai") for m in self._get_imports()))

    def test_no_anthropic(self) -> None:
        self.assertFalse(any(m.startswith("anthropic") for m in self._get_imports()))

    def test_no_local_model_server(self) -> None:
        self.assertFalse(any(m.startswith("local_model_server") for m in self._get_imports()))

    def test_no_httpx(self) -> None:
        self.assertFalse(any(m.startswith("httpx") for m in self._get_imports()))

    def test_no_section_agentic_pipeline(self) -> None:
        self.assertFalse(any("section_agentic_pipeline" in m for m in self._get_imports()))

    def test_no_write_section_to_semantic_cache(self) -> None:
        self.assertFalse(
            any("semantic_cache" in m or "write_section" in m for m in self._get_imports())
        )

    def test_no_l6_shadow_learning(self) -> None:
        self.assertFalse(
            any("l6_shadow" in m or "shadow_learning" in m for m in self._get_imports())
        )

    def test_no_fact_vectors(self) -> None:
        self.assertFalse(any("fact_vectors" in m for m in self._get_imports()))


class TestTopLevelFields(unittest.TestCase):

    def _build(self, **kwargs: Any):
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        return build_review_packet(_minimal_resume(), **kwargs)

    def test_has_review_packet_id(self) -> None:
        p = self._build()
        self.assertTrue(p.review_packet_id)

    def test_has_created_at(self) -> None:
        p = self._build()
        self.assertTrue(p.created_at)

    def test_has_source_resume_digest(self) -> None:
        p = self._build()
        self.assertTrue(p.source_resume_digest)

    def test_has_jd_digest_when_jd_supplied(self) -> None:
        p = self._build(jd_text="Software engineer role at Acme")
        self.assertTrue(p.jd_digest)

    def test_jd_digest_empty_without_jd(self) -> None:
        p = self._build()
        self.assertEqual(p.jd_digest, "")

    def test_has_jd_ref(self) -> None:
        p = self._build(jd_ref="jd_20260514_acme_vp_it")
        self.assertEqual(p.jd_ref, "jd_20260514_acme_vp_it")

    def test_has_section_reviews_list(self) -> None:
        p = self._build()
        self.assertIsInstance(p.section_reviews, list)
        self.assertGreater(len(p.section_reviews), 0)

    def test_has_overall_status(self) -> None:
        p = self._build()
        self.assertTrue(p.overall_status)

    def test_has_reviewer_decision(self) -> None:
        p = self._build()
        self.assertEqual(p.reviewer_decision, "UNREVIEWED")

    def test_has_unresolved_issues(self) -> None:
        p = self._build()
        self.assertIsInstance(p.unresolved_issues, list)

    def test_has_next_action(self) -> None:
        p = self._build()
        self.assertTrue(p.next_action)

    def test_has_profile_ref(self) -> None:
        p = self._build()
        self.assertIn("resume_manual_section_review_profile", p.profile_ref)


class TestSectionCoverage(unittest.TestCase):

    def _section_ids(self) -> set[str]:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume(), exit_check_summary=_minimal_exit_checks())
        return {sr.section_id for sr in p.section_reviews}

    def test_headline_present(self) -> None:
        self.assertIn("headline", self._section_ids())

    def test_executive_summary_present(self) -> None:
        self.assertIn("executive_summary", self._section_ids())

    def test_competencies_present(self) -> None:
        self.assertIn("competencies", self._section_ids())

    def test_education_present(self) -> None:
        self.assertIn("education", self._section_ids())

    def test_certifications_present(self) -> None:
        self.assertIn("certifications", self._section_ids())

    def test_early_career_present(self) -> None:
        self.assertIn("early_career", self._section_ids())

    def test_role_narrative_present(self) -> None:
        self.assertIn("role_0_narrative", self._section_ids())

    def test_role_bullets_present(self) -> None:
        ids = self._section_ids()
        self.assertIn("role_0_bullet_1", ids)
        self.assertIn("role_0_bullet_2", ids)


class TestBulletReviews(unittest.TestCase):

    def test_bullets_have_ordinal(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        bullet_reviews = [sr for sr in p.section_reviews if "bullet" in sr.section_id]
        self.assertEqual(len(bullet_reviews), 2)
        for br in bullet_reviews:
            self.assertIsNotNone(br.bullet_ordinal)

    def test_bullet_ordinals_are_1_and_2(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        ordinals = {
            sr.bullet_ordinal
            for sr in p.section_reviews
            if "bullet" in sr.section_id
        }
        self.assertEqual(ordinals, {1, 2})

    def test_bullets_default_unreviewed(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for sr in p.section_reviews:
            if "bullet" in sr.section_id:
                self.assertEqual(sr.reviewer_decision, "UNREVIEWED")

    def test_bullets_default_safe_to_send_false(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for sr in p.section_reviews:
            if "bullet" in sr.section_id:
                self.assertFalse(sr.safe_to_send)

    def test_ordinal_gap_produces_issue(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        resume["roles"][0]["bullets"] = [
            {"ordinal": 1, "source_text": "First bullet", "support_status": "PASS"},
            {"ordinal": 3, "source_text": "Third bullet — gap at 2", "support_status": "PASS"},
        ]
        p = build_review_packet(resume)
        narrative_review = next(
            sr for sr in p.section_reviews if sr.section_id == "role_0_narrative"
        )
        gap_issues = [i for i in narrative_review.issues if "ORDINAL_GAP" in i]
        self.assertTrue(len(gap_issues) > 0, f"Expected ordinal gap issue, got: {narrative_review.issues}")


class TestReviewerDefaults(unittest.TestCase):

    def test_all_sections_default_unreviewed(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for sr in p.section_reviews:
            self.assertEqual(sr.reviewer_decision, "UNREVIEWED", f"{sr.section_id} not UNREVIEWED")

    def test_all_sections_default_safe_to_send_false(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for sr in p.section_reviews:
            self.assertFalse(sr.safe_to_send, f"{sr.section_id} safe_to_send not False by default")

    def test_packet_reviewer_decision_default_unreviewed(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        self.assertEqual(p.reviewer_decision, "UNREVIEWED")


class TestApproveDoesNotAutoSend(unittest.TestCase):

    def test_approve_decision_can_be_represented(self) -> None:
        from apps_rg.runtime.review.manual_section_review import SectionReview
        sr = SectionReview(
            section_id="headline",
            reviewer_decision="APPROVE",
        )
        self.assertEqual(sr.reviewer_decision, "APPROVE")

    def test_approve_in_section_review_does_not_auto_send_without_clean_checks(self) -> None:
        from apps_rg.runtime.review.manual_section_review import _build_section_review, _load_profile
        profile = _load_profile()
        sr = _build_section_review(
            section_id="headline",
            generated_text="Senior IT Executive",
            support_status="UNKNOWN",
            deterministic_exit_check_status="PASS",
            reviewer_decision="APPROVE",
            profile=profile,
        )
        # UNKNOWN support_status should block safe_to_send even with APPROVE decision
        self.assertFalse(sr.safe_to_send)

    def test_approve_with_clean_status_sets_safe_to_send(self) -> None:
        from apps_rg.runtime.review.manual_section_review import _build_section_review, _load_profile
        profile = _load_profile()
        sr = _build_section_review(
            section_id="headline",
            generated_text="Senior IT Executive",
            support_status="PASS",
            deterministic_exit_check_status="PASS",
            reviewer_decision="APPROVE",
            profile=profile,
        )
        self.assertTrue(sr.safe_to_send)

    def test_unreviewed_never_safe_to_send_regardless_of_status(self) -> None:
        from apps_rg.runtime.review.manual_section_review import _build_section_review, _load_profile
        profile = _load_profile()
        sr = _build_section_review(
            section_id="headline",
            generated_text="Senior IT Executive",
            support_status="PASS",
            deterministic_exit_check_status="PASS",
            reviewer_decision="UNREVIEWED",
            profile=profile,
        )
        self.assertFalse(sr.safe_to_send)


class TestMissingChecksAreNotPass(unittest.TestCase):

    def test_missing_exit_check_creates_issue(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume(), exit_check_summary={})
        headline = next(sr for sr in p.section_reviews if sr.section_id == "headline")
        missing_issues = [i for i in headline.issues if "MISSING_EXIT_CHECK" in i]
        self.assertTrue(len(missing_issues) > 0)

    def test_missing_exit_check_blocks_safe_to_send(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume(), exit_check_summary={})
        for sr in p.section_reviews:
            self.assertFalse(sr.safe_to_send)

    def test_missing_support_status_creates_issue(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        # Remove support_status from headline
        resume["headline"] = {"text": "Senior IT Executive"}
        p = build_review_packet(resume)
        headline = next(sr for sr in p.section_reviews if sr.section_id == "headline")
        missing_issues = [i for i in headline.issues if "MISSING_SUPPORT_STATUS" in i]
        self.assertTrue(len(missing_issues) > 0)

    def test_missing_support_status_blocks_safe_to_send(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        resume["headline"] = {"text": "Senior IT Executive"}
        p = build_review_packet(resume)
        headline = next(sr for sr in p.section_reviews if sr.section_id == "headline")
        self.assertFalse(headline.safe_to_send)

    def test_unknown_exit_check_produces_issue(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume(), exit_check_summary={"headline": "UNKNOWN"})
        headline = next(sr for sr in p.section_reviews if sr.section_id == "headline")
        fail_issues = [i for i in headline.issues if "FAILING_EXIT_CHECK" in i or "MISSING_EXIT_CHECK" in i]
        self.assertTrue(len(fail_issues) > 0)


class TestBlockingSupportStatuses(unittest.TestCase):

    def _make_with_support(self, status: str) -> bool:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        resume["headline"] = {"text": "Senior IT Executive", "support_status": status}
        p = build_review_packet(resume)
        hl = next(sr for sr in p.section_reviews if sr.section_id == "headline")
        return hl.safe_to_send

    def test_insufficient_source_support_blocks(self) -> None:
        self.assertFalse(self._make_with_support("INSUFFICIENT_SOURCE_SUPPORT"))

    def test_blocked_status_blocks(self) -> None:
        self.assertFalse(self._make_with_support("BLOCKED"))

    def test_unknown_status_blocks(self) -> None:
        self.assertFalse(self._make_with_support("UNKNOWN"))

    def test_conflicted_blocks(self) -> None:
        self.assertFalse(self._make_with_support("CONFLICTED"))

    def test_empty_status_blocks(self) -> None:
        self.assertFalse(self._make_with_support("EMPTY"))

    def test_weak_blocks(self) -> None:
        self.assertFalse(self._make_with_support("WEAK"))

    def test_weak_with_caveats_blocks(self) -> None:
        self.assertFalse(self._make_with_support("WEAK_WITH_CAVEATS"))


class TestMarkdownFormatter(unittest.TestCase):

    def _md(self) -> str:
        from apps_rg.runtime.review.manual_section_review import (
            build_review_packet,
            format_review_packet_markdown,
        )
        p = build_review_packet(_minimal_resume(), exit_check_summary=_minimal_exit_checks())
        return format_review_packet_markdown(p)

    def test_markdown_contains_headline(self) -> None:
        self.assertIn("headline", self._md().lower())

    def test_markdown_contains_executive_summary(self) -> None:
        self.assertIn("executive_summary", self._md().lower())

    def test_markdown_contains_competencies(self) -> None:
        self.assertIn("competencies", self._md().lower())

    def test_markdown_contains_roles(self) -> None:
        self.assertIn("role_0_narrative", self._md().lower())

    def test_markdown_contains_education(self) -> None:
        self.assertIn("education", self._md().lower())

    def test_markdown_contains_certifications(self) -> None:
        self.assertIn("certifications", self._md().lower())

    def test_markdown_contains_early_career(self) -> None:
        self.assertIn("early_career", self._md().lower())

    def test_markdown_contains_reviewer_decision_placeholder(self) -> None:
        self.assertIn("UNREVIEWED", self._md())

    def test_markdown_contains_next_action(self) -> None:
        self.assertIn("Next Action", self._md())

    def test_markdown_contains_safe_to_send(self) -> None:
        self.assertIn("Safe to Send", self._md())

    def test_markdown_contains_support_status(self) -> None:
        self.assertIn("Support Status", self._md())

    def test_markdown_contains_exit_check(self) -> None:
        self.assertIn("Exit Check", self._md())

    def test_markdown_boundary_disclaimer(self) -> None:
        md = self._md()
        self.assertIn("Not HITL governance", md)
        self.assertIn("Does not send", md)

    def test_markdown_is_string(self) -> None:
        self.assertIsInstance(self._md(), str)


class TestJsonSerialisation(unittest.TestCase):

    def test_review_packet_to_dict_is_json_serialisable(self) -> None:
        from apps_rg.runtime.review.manual_section_review import (
            build_review_packet,
            review_packet_to_dict,
        )
        p = build_review_packet(_minimal_resume())
        d = review_packet_to_dict(p)
        serialised = json.dumps(d)
        self.assertIsInstance(serialised, str)

    def test_dict_has_section_reviews(self) -> None:
        from apps_rg.runtime.review.manual_section_review import (
            build_review_packet,
            review_packet_to_dict,
        )
        d = review_packet_to_dict(build_review_packet(_minimal_resume()))
        self.assertIn("section_reviews", d)
        self.assertGreater(len(d["section_reviews"]), 0)

    def test_each_section_review_dict_has_required_keys(self) -> None:
        from apps_rg.runtime.review.manual_section_review import (
            build_review_packet,
            review_packet_to_dict,
        )
        d = review_packet_to_dict(build_review_packet(_minimal_resume()))
        required = {
            "section_id", "reviewer_decision", "safe_to_send",
            "issues", "generated_text", "support_status",
            "deterministic_exit_check_status",
        }
        for sr_dict in d["section_reviews"]:
            for key in required:
                self.assertIn(key, sr_dict, f"Key {key!r} missing from section_review dict")


class TestNoMutation(unittest.TestCase):

    def test_resume_not_mutated(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        original = deepcopy(resume)
        build_review_packet(resume)
        self.assertEqual(resume, original, "build_review_packet mutated the input resume")

    def test_exit_checks_not_mutated(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        checks = _minimal_exit_checks()
        original = dict(checks)
        build_review_packet(_minimal_resume(), exit_check_summary=checks)
        self.assertEqual(checks, original)


class TestVerbatimSections(unittest.TestCase):

    def test_verbatim_sections_treatment_tier(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for vsec in ("education", "certifications", "early_career"):
            sr = next((s for s in p.section_reviews if s.section_id == vsec), None)
            self.assertIsNotNone(sr, f"Missing verbatim section: {vsec}")
            self.assertEqual(sr.treatment_tier, "VERBATIM")

    def test_verbatim_sections_support_not_applicable(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        for vsec in ("education", "certifications", "early_career"):
            sr = next(s for s in p.section_reviews if s.section_id == vsec)
            self.assertEqual(sr.support_status, "NOT_APPLICABLE")

    def test_missing_verbatim_hash_warns_not_fails(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        resume = _minimal_resume()
        # education dict without source_hash
        resume["education"] = {"text": "B.Sc. CS"}
        p = build_review_packet(resume)
        edu = next(s for s in p.section_reviews if s.section_id == "education")
        warn_issues = [i for i in edu.issues if "VERBATIM_MISMATCH_WARNING" in i]
        self.assertTrue(len(warn_issues) > 0)
        # Should be WARN not hard FAIL — review packet should still be produceable
        self.assertIsNotNone(p.review_packet_id)


class TestOverallStatus(unittest.TestCase):

    def test_unreviewed_all_is_unreviewed_or_partial(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        p = build_review_packet(_minimal_resume())
        self.assertIn(p.overall_status, ("UNREVIEWED", "PARTIAL_REVIEW", "BLOCKED", "NEEDS_EDIT"))

    def test_blocking_exit_check_produces_blocked_status(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        exit_checks = _minimal_exit_checks()
        exit_checks["headline"] = "FAIL"
        p = build_review_packet(_minimal_resume(), exit_check_summary=exit_checks)
        self.assertEqual(p.overall_status, "BLOCKED")


class TestS1ToS7Regression(unittest.TestCase):

    def test_c0_minimum_safety_still_importable(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        self.assertIsNotNone(run_c0_minimum_safety)

    def test_resume_exit_checks_still_importable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        self.assertIsNotNone(run_exit_checks)

    def test_runtime_summary_still_importable(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        self.assertIsNotNone(build_resume_shipping_status)

    def test_pa_binding_still_importable(self) -> None:
        from apps_rg.runtime.bindings.pa_binding import build_section_prompt_artifact
        self.assertIsNotNone(build_section_prompt_artifact)

    def test_section_treatment_profile_still_importable(self) -> None:
        from apps_rg.runtime.schemas.section_treatment_profile import get_section_policy
        self.assertIsNotNone(get_section_policy)

    def test_s8_coexists_with_all_prior_phases(self) -> None:
        from apps_rg.runtime.review.manual_section_review import build_review_packet
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        self.assertIsNotNone(build_review_packet)
        self.assertIsNotNone(run_exit_checks)
        self.assertIsNotNone(run_c0_minimum_safety)


if __name__ == "__main__":
    unittest.main()
