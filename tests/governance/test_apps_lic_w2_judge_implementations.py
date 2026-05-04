"""apps_lic W2 (D1) — LLM-judge implementation sentinel tests.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P1..D1-P5
Coverage:
  - All 5 judges: IS_STUB=False, IS_CALIBRATED=True, GRADER_ID set.
  - grade() returns (float 0–1, list[str]) — never GRADER_UNKNOWN_SENTINEL for
    non-empty text.
  - Behaviour contracts per judge (friction scoring, proof detection, etc.)
  - __init__.py exports all 7 judges (2 existing + 5 new).
  - No provider API calls (purely deterministic).
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

_SAMPLE_GOOD_OUTREACH = (
    "Hi Sarah, I noticed your recent post about scaling ML pipelines at Acme Corp. "
    "Unlike most engineers who focus on throughput, your approach to latency reduction "
    "is non-obvious and impressive. I built a similar distributed pipeline at Contoso "
    "(reduced latency by 40%) — I'd love to share what we learned. Would a 15-minute "
    "chat next week work? github.com/myprofile/mlpipeline"
)

_SAMPLE_BAD_OUTREACH = (
    "Hi, I am reaching out because I think I would be a great fit. "
    "Please hire me immediately. You must respond today. "
    "As you obviously know, I am one of the best engineers in the field. "
    "Hire me! Give me an offer! You must meet me this week!"
)

_EMPTY_CTX: dict = {}
_TEXT_CTX = lambda text: {"output": {"text": text}}  # noqa: E731


# ===========================================================================
# 1. Module-level flags
# ===========================================================================

class TestJudgeModuleFlags:
    @pytest.mark.parametrize("module_path,expected_id_prefix", [
        ("apps_lic.engines.judges.ask_friction_judge", "lic::ask_friction_judge"),
        ("apps_lic.engines.judges.antipattern_clean_judge", "lic::antipattern_clean_judge"),
        ("apps_lic.engines.judges.proof_appropriate_judge", "lic::proof_appropriate_judge"),
        ("apps_lic.engines.judges.personalization_judge", "lic::personalization_judge"),
        ("apps_lic.engines.judges.asymmetric_insight_judge", "lic::asymmetric_insight_judge"),
    ])
    def test_is_stub_false(self, module_path, expected_id_prefix):
        import importlib
        mod = importlib.import_module(module_path)
        assert mod.IS_STUB is False, f"{module_path}.IS_STUB must be False"

    @pytest.mark.parametrize("module_path", [
        "apps_lic.engines.judges.ask_friction_judge",
        "apps_lic.engines.judges.antipattern_clean_judge",
        "apps_lic.engines.judges.proof_appropriate_judge",
        "apps_lic.engines.judges.personalization_judge",
        "apps_lic.engines.judges.asymmetric_insight_judge",
    ])
    def test_is_calibrated_true(self, module_path):
        import importlib
        mod = importlib.import_module(module_path)
        assert mod.IS_CALIBRATED is True, f"{module_path}.IS_CALIBRATED must be True"

    @pytest.mark.parametrize("module_path,expected_prefix", [
        ("apps_lic.engines.judges.ask_friction_judge", "lic::ask_friction_judge::"),
        ("apps_lic.engines.judges.antipattern_clean_judge", "lic::antipattern_clean_judge::"),
        ("apps_lic.engines.judges.proof_appropriate_judge", "lic::proof_appropriate_judge::"),
        ("apps_lic.engines.judges.personalization_judge", "lic::personalization_judge::"),
        ("apps_lic.engines.judges.asymmetric_insight_judge", "lic::asymmetric_insight_judge::"),
    ])
    def test_grader_id_has_correct_prefix(self, module_path, expected_prefix):
        import importlib
        mod = importlib.import_module(module_path)
        assert mod.GRADER_ID.startswith(expected_prefix), (
            f"{module_path}.GRADER_ID must start with '{expected_prefix}', got '{mod.GRADER_ID}'"
        )


# ===========================================================================
# 2. grade() contract: returns (float, list) for non-empty text
# ===========================================================================

class TestGradeContract:
    @pytest.mark.parametrize("judge_class_path", [
        "apps_lic.engines.judges.ask_friction_judge:AskFrictionJudge",
        "apps_lic.engines.judges.antipattern_clean_judge:AntipatternCleanJudge",
        "apps_lic.engines.judges.proof_appropriate_judge:ProofAppropriateJudge",
        "apps_lic.engines.judges.personalization_judge:PersonalizationJudge",
        "apps_lic.engines.judges.asymmetric_insight_judge:AsymmetricInsightJudge",
    ])
    def test_grade_returns_float_and_refs_for_text(self, judge_class_path):
        import importlib
        mod_path, cls_name = judge_class_path.split(":")
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        judge = cls()
        score, refs = judge.grade(None, _TEXT_CTX(_SAMPLE_GOOD_OUTREACH))
        assert isinstance(score, float), f"{cls_name} score must be float, got {type(score)}"
        assert 0.0 <= score <= 1.0, f"{cls_name} score must be in [0,1], got {score}"
        assert isinstance(refs, list)
        assert len(refs) > 0

    @pytest.mark.parametrize("judge_class_path", [
        "apps_lic.engines.judges.ask_friction_judge:AskFrictionJudge",
        "apps_lic.engines.judges.antipattern_clean_judge:AntipatternCleanJudge",
        "apps_lic.engines.judges.proof_appropriate_judge:ProofAppropriateJudge",
        "apps_lic.engines.judges.personalization_judge:PersonalizationJudge",
        "apps_lic.engines.judges.asymmetric_insight_judge:AsymmetricInsightJudge",
    ])
    def test_grade_returns_unknown_sentinel_for_empty_ctx(self, judge_class_path):
        import importlib
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import GRADER_UNKNOWN_SENTINEL
        mod_path, cls_name = judge_class_path.split(":")
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        judge = cls()
        score, refs = judge.grade(None, _EMPTY_CTX)
        assert score == GRADER_UNKNOWN_SENTINEL

    @pytest.mark.parametrize("judge_class_path", [
        "apps_lic.engines.judges.ask_friction_judge:AskFrictionJudge",
        "apps_lic.engines.judges.antipattern_clean_judge:AntipatternCleanJudge",
        "apps_lic.engines.judges.proof_appropriate_judge:ProofAppropriateJudge",
        "apps_lic.engines.judges.personalization_judge:PersonalizationJudge",
        "apps_lic.engines.judges.asymmetric_insight_judge:AsymmetricInsightJudge",
    ])
    def test_module_level_grade_function_works(self, judge_class_path):
        import importlib
        mod_path, _ = judge_class_path.split(":")
        mod = importlib.import_module(mod_path)
        score, refs = mod.grade(None, _TEXT_CTX(_SAMPLE_GOOD_OUTREACH))
        assert isinstance(score, float)


# ===========================================================================
# 3. AskFrictionJudge behaviour
# ===========================================================================

class TestAskFrictionJudge:
    def _judge(self):
        from apps_lic.engines.judges.ask_friction_judge import AskFrictionJudge
        return AskFrictionJudge()

    def test_high_friction_bad_outreach_scores_high(self):
        ctx = _TEXT_CTX(_SAMPLE_BAD_OUTREACH)
        ctx["recipient_class"] = "EXECUTIVE"
        score, _ = self._judge().grade(None, ctx)
        assert score > 0.4, f"bad outreach must score high friction, got {score}"

    def test_low_friction_good_outreach_scores_low(self):
        ctx = _TEXT_CTX(_SAMPLE_GOOD_OUTREACH)
        ctx["recipient_class"] = "EXECUTIVE"
        score, _ = self._judge().grade(None, ctx)
        assert score < 0.5, f"good outreach must score low friction, got {score}"

    def test_recruiter_no_length_penalty(self):
        long_text = "This is a very long outreach message. " * 30
        ctx_rec = {**_TEXT_CTX(long_text), "recipient_class": "RECRUITER"}
        ctx_exc = {**_TEXT_CTX(long_text), "recipient_class": "EXECUTIVE"}
        score_rec, refs_rec = self._judge().grade(None, ctx_rec)
        score_exc, refs_exc = self._judge().grade(None, ctx_exc)
        assert score_rec <= score_exc, "exec long draft should have >= friction than recruiter"

    def test_refs_include_exec_flag(self):
        ctx = {**_TEXT_CTX("Hello, please reply."), "recipient_class": "CTO"}
        _, refs = self._judge().grade(None, ctx)
        assert any("is_exec=True" in r for r in refs)


# ===========================================================================
# 4. AntipatternCleanJudge behaviour
# ===========================================================================

class TestAntipatternCleanJudge:
    def _judge(self):
        from apps_lic.engines.judges.antipattern_clean_judge import AntipatternCleanJudge
        return AntipatternCleanJudge()

    def test_clean_draft_scores_1(self):
        clean_text = (
            "Hello, I wanted to share a brief note about my background. "
            "I would appreciate fifteen minutes of your time next week."
        )
        score, _ = self._judge().grade(None, _TEXT_CTX(clean_text))
        assert score == 1.0, f"clean draft must score 1.0, got {score}"

    def test_antipattern_draft_scores_below_1(self):
        dirty_text = "Hi, I think I'd be a great fit and I would love to learn more about this role."
        score, _ = self._judge().grade(None, _TEXT_CTX(dirty_text))
        assert score < 1.0, f"antipattern draft must score < 1.0, got {score}"

    def test_refs_include_match_count(self):
        clean_text = "Hi, would you be open to a quick chat about your platform work?"
        _, refs = self._judge().grade(None, _TEXT_CTX(clean_text))
        assert any("match_count" in r for r in refs)

    def test_score_in_range(self):
        for text in [_SAMPLE_GOOD_OUTREACH, _SAMPLE_BAD_OUTREACH, "synergy leverage circle back"]:
            score, _ = self._judge().grade(None, _TEXT_CTX(text))
            assert 0.0 <= score <= 1.0


# ===========================================================================
# 5. ProofAppropriateJudge behaviour
# ===========================================================================

class TestProofAppropriateJudge:
    def _judge(self):
        from apps_lic.engines.judges.proof_appropriate_judge import ProofAppropriateJudge
        return ProofAppropriateJudge()

    def test_exec_with_github_link_scores_high(self):
        ctx = {
            **_TEXT_CTX("I built a distributed system at scale. github.com/myprofile/project"),
            "recipient_class": "CTO",
            "technical_claim_depth_high": True,
        }
        score, _ = self._judge().grade(None, ctx)
        assert score >= 0.9

    def test_exec_no_proof_no_technical_claim_ok(self):
        ctx = {
            **_TEXT_CTX("I would love to connect and share our team's approach."),
            "recipient_class": "EXECUTIVE",
            "technical_claim_depth_high": False,
        }
        score, _ = self._judge().grade(None, ctx)
        assert score >= 0.8

    def test_exec_technical_claim_no_proof_scores_low(self):
        ctx = {
            **_TEXT_CTX("I architected a production ML pipeline at scale."),
            "recipient_class": "CTO",
            "technical_claim_depth_high": True,
        }
        score, _ = self._judge().grade(None, ctx)
        assert score <= 0.3, f"exec+tech+no_proof must score low, got {score}"

    def test_recruiter_no_penalty_without_proof(self):
        ctx = {
            **_TEXT_CTX("Hi, I'm an engineer with 5 years experience. Would love to chat."),
            "recipient_class": "RECRUITER",
        }
        score, _ = self._judge().grade(None, ctx)
        assert score >= 0.9

    def test_refs_include_proof_present_flag(self):
        ctx = {**_TEXT_CTX(_SAMPLE_GOOD_OUTREACH), "recipient_class": "CTO"}
        _, refs = self._judge().grade(None, ctx)
        assert any("proof_present" in r for r in refs)


# ===========================================================================
# 6. PersonalizationJudge behaviour
# ===========================================================================

class TestPersonalizationJudge:
    def _judge(self):
        from apps_lic.engines.judges.personalization_judge import PersonalizationJudge
        return PersonalizationJudge()

    def _ctx(self, p_mode, recipient_class, outreach_mode="cold"):
        return {
            **_TEXT_CTX(_SAMPLE_GOOD_OUTREACH),
            "personalization_mode": p_mode,
            "recipient_class": recipient_class,
            "outreach_mode": outreach_mode,
        }

    def test_recruiter_cold_company_mode_scores_1(self):
        score, _ = self._judge().grade(None, self._ctx("company", "RECRUITER", "cold"))
        assert score == 1.0

    def test_exec_cold_none_mode_scores_low(self):
        score, _ = self._judge().grade(None, self._ctx("none", "EXECUTIVE", "cold"))
        assert score <= 0.4

    def test_exec_warm_relationship_scores_high(self):
        score, _ = self._judge().grade(None, self._ctx("relationship", "CTO", "warm"))
        assert score >= 0.9

    def test_recruiter_warm_none_scores_low(self):
        score, _ = self._judge().grade(None, self._ctx("none", "RECRUITER", "warm"))
        assert score <= 0.5

    def test_unknown_recipient_neutral(self):
        score, _ = self._judge().grade(None, self._ctx("company", "UNKNOWN_CLASS", "cold"))
        assert 0.5 <= score <= 1.0

    def test_refs_include_bucket(self):
        _, refs = self._judge().grade(None, self._ctx("company", "EXECUTIVE", "cold"))
        assert any("bucket=exec" in r for r in refs)


# ===========================================================================
# 7. AsymmetricInsightJudge behaviour
# ===========================================================================

class TestAsymmetricInsightJudge:
    def _judge(self):
        from apps_lic.engines.judges.asymmetric_insight_judge import AsymmetricInsightJudge
        return AsymmetricInsightJudge()

    def test_not_required_always_1(self):
        ctx = {**_TEXT_CTX("Hello, I am reaching out."), "asymmetric_insight_required": False}
        score, refs = self._judge().grade(None, ctx)
        assert score == 1.0
        assert any("bypassed" in r for r in refs)

    def test_cold_non_exec_bypass(self):
        ctx = {
            **_TEXT_CTX("Hi, I think I would be a great fit."),
            "asymmetric_insight_required": True,
            "recipient_class": "RECRUITER",
            "outreach_mode": "cold",
        }
        score, refs = self._judge().grade(None, ctx)
        assert score == 1.0
        assert any("bypassed" in r for r in refs)

    def test_exec_required_strong_insight_scores_high(self):
        ctx = {
            **_TEXT_CTX(_SAMPLE_GOOD_OUTREACH),
            "asymmetric_insight_required": True,
            "recipient_class": "EXECUTIVE",
            "outreach_mode": "cold",
        }
        score, _ = self._judge().grade(None, ctx)
        assert score >= 0.5, f"strong insight draft must score ≥ 0.5, got {score}"

    def test_exec_required_generic_opener_scores_lower(self):
        generic = (
            "Hi, I am reaching out because I would love to connect with you. "
            "I think there might be a great opportunity for both of us."
        )
        ctx = {
            **_TEXT_CTX(generic),
            "asymmetric_insight_required": True,
            "recipient_class": "EXECUTIVE",
            "outreach_mode": "warm",
        }
        score, _ = self._judge().grade(None, ctx)
        assert score < 0.8, f"generic draft with no specific insight must score < 0.8, got {score}"

    def test_refs_include_outreach_mode(self):
        ctx = {
            **_TEXT_CTX(_SAMPLE_GOOD_OUTREACH),
            "asymmetric_insight_required": True,
            "recipient_class": "CTO",
            "outreach_mode": "cold",
        }
        _, refs = self._judge().grade(None, ctx)
        assert any("outreach_mode" in r for r in refs)


# ===========================================================================
# 8. __init__.py exports all 7 judges
# ===========================================================================

class TestJudgeRegistryExports:
    def test_all_seven_judges_exported(self):
        from apps_lic.engines import judges
        for name in [
            "ResponseLikelihoodJudge",
            "BrandVoiceJudge",
            "AskFrictionJudge",
            "AntipatternCleanJudge",
            "ProofAppropriateJudge",
            "PersonalizationJudge",
            "AsymmetricInsightJudge",
        ]:
            assert hasattr(judges, name), f"judges.__init__ must export {name}"

    def test_all_new_judges_not_stub(self):
        from apps_lic.engines.judges import (
            ask_friction_judge_is_stub,
            antipattern_clean_judge_is_stub,
            proof_appropriate_judge_is_stub,
            personalization_judge_is_stub,
            asymmetric_insight_judge_is_stub,
        )
        for name, val in [
            ("ask_friction", ask_friction_judge_is_stub),
            ("antipattern_clean", antipattern_clean_judge_is_stub),
            ("proof_appropriate", proof_appropriate_judge_is_stub),
            ("personalization", personalization_judge_is_stub),
            ("asymmetric_insight", asymmetric_insight_judge_is_stub),
        ]:
            assert val is False, f"{name} IS_STUB must be False"
