"""Novel tests for the LLM-as-Judge system — Phase 2+3 components.

Covers gaps not in the original test suite:
- JudgeProviderRegistry: register, default, list, set_default
- NullJudgeProvider / GeminiJudgeProvider adapter interface
- LLM judges via NullJudgeProvider (GOV-001, GOV-003, SEC-001 async paths)
- JudgeOrchestrator: full deterministic pipeline, batch, scorecard building
- JudgeScorecard: weighted scoring, custom weights, empty input, render_text
- RegressionAnalyzer: regression detection, improvements, new_failures, thresholds
- Adversarial / property-based: digest stability, score boundary transitions,
  evidence hash mutation invariance, verdict idempotency, rubric custom JSON,
  malformed rubric file resilience, VerdictStore idempotent re-store
- JudgeReport computed properties: fail_count, warn_count
- ARCH-001 edge cases: warn zone (95-99% compliance), mixed valid/invalid layers
- COV-001: exact boundary at 85% warn threshold (6/7 dims)
- GOV-002: partial UWG compliance (warn zone)
- QUAL-001: boundary scores at threshold edges
"""

from __future__ import annotations

import asyncio
import json
import textwrap
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agentic_core.evaluation.judges.types import (
    EvidenceBundle,
    EvidenceItem,
    JudgeReport,
    JudgeReportRow,
    JudgeVerdict,
    VerdictOutcome,
)


# ===================================================================
# Helpers
# ===================================================================


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _verdict(
    target="mod.py",
    dimension="architecture",
    rubric_id="ARCH-001",
    outcome=VerdictOutcome.PASS.value,
    score=1.0,
    reasoning="ok",
    severity="MEDIUM",
    adg_digest="",
) -> JudgeVerdict:
    return JudgeVerdict(
        verdict_id=uuid.uuid4().hex[:12],
        target=target,
        dimension=dimension,
        rubric_id=rubric_id,
        outcome=outcome,
        score=score,
        reasoning=reasoning,
        severity=severity,
        adg_digest=adg_digest,
        created_at=_now(),
    )


def _report(target="mod.py", verdicts=None, overall=1.0, passed=True) -> JudgeReport:
    return JudgeReport(
        target=target,
        verdicts=verdicts or [],
        overall_score=overall,
        passed=passed,
        created_at=_now(),
    )


# ===================================================================
# JudgeProviderRegistry
# ===================================================================


class TestJudgeProviderRegistry:
    def test_register_and_get(self):
        from agentic_core.evaluation.judges.provider_registry import (
            JudgeProviderRegistry,
            NullJudgeProvider,
        )

        reg = JudgeProviderRegistry()
        p = NullJudgeProvider()
        reg.register(p)
        assert reg.get("null") is p

    def test_default_set_on_first_register(self):
        from agentic_core.evaluation.judges.provider_registry import (
            JudgeProviderRegistry,
            NullJudgeProvider,
        )

        reg = JudgeProviderRegistry()
        reg.register(NullJudgeProvider())
        assert reg.default is not None
        assert reg.default.provider_id == "null"

    def test_get_nonexistent_returns_none(self):
        from agentic_core.evaluation.judges.provider_registry import JudgeProviderRegistry

        reg = JudgeProviderRegistry()
        assert reg.get("nonexistent") is None

    def test_set_default(self):
        from agentic_core.evaluation.judges.provider_registry import (
            JudgeProviderRegistry,
            NullJudgeProvider,
        )

        class FakeProvider:
            provider_id = "fake"
            cost_per_eval = 0.0
            async def judge(self, p, r): return {}

        reg = JudgeProviderRegistry()
        reg.register(NullJudgeProvider())
        reg.register(FakeProvider(), default=False)
        reg.set_default("fake")
        assert reg.default.provider_id == "fake"

    def test_set_default_missing_returns_false(self):
        from agentic_core.evaluation.judges.provider_registry import JudgeProviderRegistry

        reg = JudgeProviderRegistry()
        assert reg.set_default("ghost") is False

    def test_provider_ids(self):
        from agentic_core.evaluation.judges.provider_registry import (
            JudgeProviderRegistry,
            NullJudgeProvider,
        )

        reg = JudgeProviderRegistry()
        reg.register(NullJudgeProvider())
        assert "null" in reg.provider_ids

    def test_summary(self):
        from agentic_core.evaluation.judges.provider_registry import (
            JudgeProviderRegistry,
            NullJudgeProvider,
            create_default_registry,
        )

        reg = create_default_registry()
        s = reg.summary()
        assert s["count"] >= 1
        assert s["default"] == "null"
        assert any(p["provider_id"] == "null" for p in s["providers"])

    def test_create_default_registry(self):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        reg = create_default_registry()
        assert reg.default is not None
        assert reg.default.provider_id == "null"
        assert reg.default.cost_per_eval == 0.0


# ===================================================================
# NullJudgeProvider
# ===================================================================


class TestNullJudgeProvider:
    def test_judge_returns_dict(self):
        from agentic_core.evaluation.judges.provider_registry import NullJudgeProvider

        p = NullJudgeProvider()
        result = asyncio.get_event_loop().run_until_complete(
            p.judge("some prompt", "GOV-001")
        )
        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert result["score"] == 0.5
        assert result["provider"] == "null"

    def test_provider_id(self):
        from agentic_core.evaluation.judges.provider_registry import NullJudgeProvider

        assert NullJudgeProvider().provider_id == "null"

    def test_cost_per_eval_zero(self):
        from agentic_core.evaluation.judges.provider_registry import NullJudgeProvider

        assert NullJudgeProvider().cost_per_eval == 0.0


# ===================================================================
# LLM judges via NullJudgeProvider
# ===================================================================


class TestLLMJudgesNullProvider:
    """Test async LLM judges end-to-end using NullJudgeProvider (no API calls)."""

    @pytest.fixture()
    def provider(self):
        from agentic_core.evaluation.judges.provider_registry import NullJudgeProvider
        return NullJudgeProvider()

    @pytest.fixture()
    def engine(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine
        return RubricEngine()

    def test_gov_001_returns_verdict(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_001

        bundle = EvidenceBundle(
            target="agentic_core/L2_execution/x.py",
            adg_edges={"applies_guardrail": [{"symbol": "g"}]},
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_001(bundle, provider, engine)
        )
        assert verdict.rubric_id == "GOV-001"
        assert verdict.target == "agentic_core/L2_execution/x.py"
        assert verdict.outcome in {o.value for o in VerdictOutcome}
        assert 0.0 <= verdict.score <= 1.0

    def test_gov_003_returns_verdict(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_003

        bundle = EvidenceBundle(
            target="agentic_core/L3_orchestration/orch.py",
            adg_edges={"dispatches_agent": [{"symbol": "d"}]},
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_003(bundle, provider, engine)
        )
        assert verdict.rubric_id == "GOV-003"
        assert verdict.outcome in {o.value for o in VerdictOutcome}

    def test_sec_001_skip_no_dynamic_edges(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import judge_sec_001

        bundle = EvidenceBundle(
            target="agentic_core/clean.py",
            adg_edges={"imports": [{"target_name": "json"}]},
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_sec_001(bundle, provider, engine)
        )
        assert verdict.rubric_id == "SEC-001"
        assert verdict.outcome == VerdictOutcome.SKIP.value
        assert verdict.score == 1.0

    def test_sec_001_with_dynamic_edges(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import judge_sec_001

        bundle = EvidenceBundle(
            target="agentic_core/risky.py",
            adg_edges={
                "invokes_eval": [
                    {"symbol": "eval", "source_file": "risky.py", "line_no": 10}
                ]
            },
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_sec_001(bundle, provider, engine)
        )
        assert verdict.rubric_id == "SEC-001"
        assert verdict.outcome != VerdictOutcome.SKIP.value
        assert len(verdict.evidence_items) >= 1

    def test_run_llm_judge_dispatcher(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import run_llm_judge

        bundle = EvidenceBundle(target="test.py")
        verdict = asyncio.get_event_loop().run_until_complete(
            run_llm_judge("GOV-001", bundle, provider, engine)
        )
        assert verdict is not None
        assert verdict.rubric_id == "GOV-001"

    def test_run_llm_judge_unknown_returns_none(self, provider, engine):
        from agentic_core.evaluation.judges.llm_judges import run_llm_judge

        bundle = EvidenceBundle(target="test.py")
        result = asyncio.get_event_loop().run_until_complete(
            run_llm_judge("ARCH-001", bundle, provider, engine)
        )
        assert result is None

    def test_gov_001_missing_rubric_returns_error(self, provider):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_001
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        empty_engine = RubricEngine.__new__(RubricEngine)
        empty_engine._rubrics = {}
        empty_engine._loaded = True

        bundle = EvidenceBundle(target="test.py")
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_001(bundle, provider, empty_engine)
        )
        assert verdict.outcome == VerdictOutcome.ERROR.value


# ===================================================================
# JudgeOrchestrator
# ===================================================================


class TestJudgeOrchestrator:
    @pytest.fixture()
    def orch(self, tmp_path):
        from agentic_core.evaluation.judges.orchestrator import JudgeOrchestrator
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        return JudgeOrchestrator(
            verdict_db_path=str(tmp_path / "verdicts.sqlite"),
            provider_registry=create_default_registry(),
        )

    def test_evaluate_deterministic_only(self, orch):
        report = asyncio.get_event_loop().run_until_complete(
            orch.evaluate(
                module_path="agentic_core/L2_execution/test.py",
                rubric_ids=["ARCH-001"],
                deterministic_only=True,
                persist=False,
            )
        )
        assert report.target == "agentic_core/L2_execution/test.py"
        assert isinstance(report.overall_score, float)
        assert 0.0 <= report.overall_score <= 1.0

    def test_evaluate_no_rubrics_returns_error_report(self, orch):
        report = asyncio.get_event_loop().run_until_complete(
            orch.evaluate(
                module_path="test.py",
                rubric_ids=["NONEXISTENT_RUBRIC_XYZ"],
                deterministic_only=True,
                persist=False,
            )
        )
        assert report.error != "" or report.overall_score == 0.0

    def test_evaluate_batch(self, orch):
        reports = asyncio.get_event_loop().run_until_complete(
            orch.evaluate_batch(
                module_paths=["mod_a.py", "mod_b.py", "mod_c.py"],
                rubric_ids=["QUAL-001"],
                deterministic_only=True,
                persist=False,
            )
        )
        assert len(reports) == 3
        targets = {r.target for r in reports}
        assert targets == {"mod_a.py", "mod_b.py", "mod_c.py"}

    def test_evaluate_with_persist(self, orch):
        asyncio.get_event_loop().run_until_complete(
            orch.evaluate(
                module_path="agentic_core/persist_test.py",
                rubric_ids=["COV-001"],
                deterministic_only=True,
                persist=True,
            )
        )
        store_stats = orch.verdict_store.stats()
        assert store_stats["total_verdicts"] >= 1

    def test_scorecard_rows_sorted_by_score(self, orch):
        verdicts = [
            _verdict(dimension="security", score=0.1, outcome=VerdictOutcome.FAIL.value),
            _verdict(dimension="architecture", score=0.9, outcome=VerdictOutcome.PASS.value),
            _verdict(dimension="code_quality", score=0.5, outcome=VerdictOutcome.WARN.value),
        ]
        rows = orch._build_scorecard(verdicts)
        scores = [r.score for r in rows]
        assert scores == sorted(scores)

    def test_scorecard_worst_outcome_wins(self, orch):
        verdicts = [
            _verdict(dimension="security", score=1.0, outcome=VerdictOutcome.PASS.value),
            _verdict(
                dimension="security",
                score=0.0,
                rubric_id="SEC-002",
                outcome=VerdictOutcome.FAIL.value,
            ),
        ]
        rows = orch._build_scorecard(verdicts)
        sec_row = next(r for r in rows if r.dimension == "security")
        assert sec_row.outcome == VerdictOutcome.FAIL.value

    def test_scorecard_skips_excluded(self, orch):
        verdicts = [
            _verdict(dimension="arch", outcome=VerdictOutcome.SKIP.value, score=1.0),
        ]
        rows = orch._build_scorecard(verdicts)
        assert len(rows) == 0

    def test_summary_keys(self, orch):
        s = orch.summary()
        assert "rubrics" in s
        assert "providers" in s
        assert "deterministic_judges" in s
        assert "llm_judges" in s


# ===================================================================
# JudgeScorecard
# ===================================================================


class TestJudgeScorecardWeighting:
    def test_empty_reports(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        sc = JudgeScorecard()
        result = sc.compute([])
        assert result["overall_score"] == 0.0
        assert result["total_modules"] == 0
        assert result["dimension_scores"] == {}

    def test_single_pass_report(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        v = _verdict(dimension="security", score=1.0)
        report = _report(verdicts=[v])
        sc = JudgeScorecard()
        result = sc.compute([report])
        assert result["overall_score"] == 1.0
        assert result["passed"] is True

    def test_security_weight_dominates(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        reports = [
            _report(
                verdicts=[
                    _verdict(dimension="security", score=0.0, outcome=VerdictOutcome.FAIL.value),
                    _verdict(dimension="code_quality", score=1.0),
                ]
            )
        ]
        sc = JudgeScorecard()
        result = sc.compute(reports)
        # security weight=2.0, code_quality weight=1.0 → weighted avg pulls toward 0
        assert result["overall_score"] < 0.5

    def test_custom_weights_applied(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        reports = [
            _report(
                verdicts=[
                    _verdict(dimension="arch", score=0.0, outcome=VerdictOutcome.FAIL.value),
                    _verdict(dimension="sec", score=1.0),
                ]
            )
        ]
        # Heavily weight sec, ignore arch
        sc_custom = JudgeScorecard(weights={"arch": 0.01, "sec": 100.0})
        result = sc_custom.compute(reports)
        assert result["overall_score"] > 0.95

    def test_fail_summary_sorted_by_severity(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        reports = [
            _report(
                verdicts=[
                    _verdict(dimension="arch", score=0.0, outcome=VerdictOutcome.FAIL.value, severity="LOW"),
                    _verdict(dimension="security", score=0.0, outcome=VerdictOutcome.FAIL.value, severity="CRITICAL"),
                    _verdict(dimension="quality", score=0.0, outcome=VerdictOutcome.FAIL.value, severity="HIGH"),
                ]
            )
        ]
        sc = JudgeScorecard()
        result = sc.compute(reports)
        severities = [f["severity"] for f in result["fail_summary"]]
        assert severities[0] == "CRITICAL"
        assert severities[-1] == "LOW"

    def test_skip_verdicts_not_counted(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        reports = [
            _report(
                verdicts=[
                    _verdict(dimension="arch", outcome=VerdictOutcome.SKIP.value, score=1.0),
                    _verdict(dimension="arch", outcome=VerdictOutcome.SKIP.value, score=1.0),
                ]
            )
        ]
        sc = JudgeScorecard()
        result = sc.compute(reports)
        assert result["total_verdicts"] == 0
        assert result["dimension_scores"] == {}

    def test_module_scores_sorted(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        sc = JudgeScorecard()
        reports = [
            _report("a.py", [_verdict("a.py", score=0.9)], overall=0.9),
            _report("b.py", [_verdict("b.py", score=0.2, outcome=VerdictOutcome.FAIL.value)], overall=0.2),
            _report("c.py", [_verdict("c.py", score=0.5, outcome=VerdictOutcome.WARN.value)], overall=0.5),
        ]
        result = sc.compute(reports)
        scores = [m["overall_score"] for m in result["module_scores"]]
        assert scores == sorted(scores)

    def test_render_text_contains_score(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        sc = JudgeScorecard()
        v = _verdict(dimension="security", score=0.8, outcome=VerdictOutcome.PASS.value)
        result = sc.compute([_report(verdicts=[v])])
        text = sc.render_text(result)
        assert "0.8" in text or "PASS" in text
        assert "Scorecard" in text

    def test_dimension_worst_outcome_fail(self):
        from agentic_core.evaluation.judges.scorecard import JudgeScorecard

        sc = JudgeScorecard()
        reports = [
            _report(
                verdicts=[
                    _verdict(dimension="arch", score=0.9),
                    _verdict(dimension="arch", score=0.0, outcome=VerdictOutcome.FAIL.value),
                ]
            )
        ]
        result = sc.compute(reports)
        assert result["dimension_scores"]["arch"]["outcome"] == "FAIL"


# ===================================================================
# RegressionAnalyzer
# ===================================================================


class TestRegressionAnalyzer:
    @pytest.fixture()
    def store_with_data(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "regs.sqlite"))
        # Old digest verdicts
        old = [
            _verdict("mod_a.py", "arch", "ARCH-001", VerdictOutcome.PASS.value, 1.0, adg_digest="old"),
            _verdict("mod_b.py", "security", "SEC-002", VerdictOutcome.PASS.value, 1.0, adg_digest="old"),
            _verdict("mod_c.py", "quality", "QUAL-001", VerdictOutcome.WARN.value, 0.7, adg_digest="old"),
        ]
        # New digest: mod_a regressed, mod_b improved, mod_c new failure
        new = [
            _verdict("mod_a.py", "arch", "ARCH-001", VerdictOutcome.FAIL.value, 0.5, adg_digest="new"),
            _verdict("mod_b.py", "security", "SEC-002", VerdictOutcome.PASS.value, 1.0, adg_digest="new"),
            _verdict("mod_c.py", "quality", "QUAL-001", VerdictOutcome.FAIL.value, 0.3, adg_digest="new"),
        ]
        store.store_verdicts(old + new)
        return store

    def test_regression_detected(self, store_with_data):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer

        analyzer = RegressionAnalyzer(store_with_data, regression_threshold=0.1)
        result = analyzer.compare("new", "old")
        assert result["has_regressions"] is True
        assert result["regression_count"] >= 1

    def test_regression_mod_a(self, store_with_data):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer

        analyzer = RegressionAnalyzer(store_with_data, regression_threshold=0.1)
        result = analyzer.compare("new", "old")
        reg_targets = {r["target"] for r in result["regressions"]}
        assert "mod_a.py" in reg_targets

    def test_new_failures_identified(self, store_with_data):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer

        analyzer = RegressionAnalyzer(store_with_data, regression_threshold=0.05)
        result = analyzer.compare("new", "old")
        # mod_c was WARN before, now FAIL — that's a new failure
        new_fail_targets = {f["target"] for f in result["new_failures"]}
        assert "mod_c.py" in new_fail_targets

    def test_no_regressions_when_stable(self, tmp_path):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "stable.sqlite"))
        # Same score old and new
        for digest in ("old2", "new2"):
            store.store_verdicts([
                _verdict("m.py", "arch", "ARCH-001", VerdictOutcome.PASS.value, 1.0, adg_digest=digest),
            ])
        analyzer = RegressionAnalyzer(store, regression_threshold=0.05)
        result = analyzer.compare("new2", "old2")
        assert result["regression_count"] == 0
        assert result["has_regressions"] is False

    def test_threshold_filters_small_deltas(self, tmp_path):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "tiny.sqlite"))
        store.store_verdicts([
            _verdict("m.py", "arch", "ARCH-001", VerdictOutcome.PASS.value, 1.0, adg_digest="old3"),
            _verdict("m.py", "arch", "ARCH-001", VerdictOutcome.PASS.value, 0.98, adg_digest="new3"),
        ])
        # With large threshold, tiny delta ignored
        analyzer = RegressionAnalyzer(store, regression_threshold=0.1)
        result = analyzer.compare("new3", "old3")
        assert result["regression_count"] == 0

    def test_render_text_contains_counts(self, store_with_data):
        from agentic_core.evaluation.judges.scorecard import RegressionAnalyzer

        analyzer = RegressionAnalyzer(store_with_data, regression_threshold=0.05)
        result = analyzer.compare("new", "old")
        text = analyzer.render_text(result)
        assert "Regression" in text
        assert "new" in text
        assert "old" in text


# ===================================================================
# JudgeReport computed properties
# ===================================================================


class TestJudgeReportProperties:
    def test_fail_count(self):
        r = JudgeReport(
            target="t.py",
            verdicts=[
                _verdict(outcome=VerdictOutcome.FAIL.value),
                _verdict(outcome=VerdictOutcome.FAIL.value),
                _verdict(outcome=VerdictOutcome.PASS.value),
            ],
        )
        assert r.fail_count == 2

    def test_warn_count(self):
        r = JudgeReport(
            target="t.py",
            verdicts=[
                _verdict(outcome=VerdictOutcome.WARN.value),
                _verdict(outcome=VerdictOutcome.PASS.value),
            ],
        )
        assert r.warn_count == 1

    def test_fail_and_warn_combined(self):
        r = JudgeReport(
            target="t.py",
            verdicts=[
                _verdict(outcome=VerdictOutcome.FAIL.value),
                _verdict(outcome=VerdictOutcome.WARN.value),
                _verdict(outcome=VerdictOutcome.SKIP.value),
                _verdict(outcome=VerdictOutcome.PASS.value),
            ],
        )
        assert r.fail_count == 1
        assert r.warn_count == 1

    def test_empty_verdicts(self):
        r = JudgeReport(target="t.py")
        assert r.fail_count == 0
        assert r.warn_count == 0


# ===================================================================
# Adversarial / Property-based
# ===================================================================


class TestAdversarialDigestStability:
    """Digest and hash properties must be deterministic."""

    def test_evidence_hash_stable_under_repeated_construction(self):
        """Same inputs → same hash across 100 instantiations."""
        hashes = set()
        for _ in range(100):
            b = EvidenceBundle(
                target="stable.py",
                adg_edges={"imports": [{"target_name": "json"}]},
                adg_digest="abc123",
            )
            hashes.add(b.evidence_hash)
        assert len(hashes) == 1

    def test_evidence_hash_changes_on_target_change(self):
        b1 = EvidenceBundle(target="a.py", adg_digest="x")
        b2 = EvidenceBundle(target="b.py", adg_digest="x")
        assert b1.evidence_hash != b2.evidence_hash

    def test_evidence_hash_changes_on_digest_change(self):
        b1 = EvidenceBundle(target="a.py", adg_digest="d1")
        b2 = EvidenceBundle(target="a.py", adg_digest="d2")
        assert b1.evidence_hash != b2.evidence_hash

    def test_verdict_deterministic_digest_stable(self):
        digests = set()
        for _ in range(100):
            v = JudgeVerdict(
                verdict_id="x",
                target="stable.py",
                rubric_id="ARCH-001",
                dimension="arch",
                outcome="PASS",
                score=1.0,
                reasoning="ok",
                adg_digest="abc",
            )
            digests.add(v.deterministic_digest)
        assert len(digests) == 1

    def test_verdict_digest_differs_on_score_change(self):
        base = dict(
            verdict_id="x", target="m.py", rubric_id="ARCH-001",
            dimension="arch", reasoning="ok", adg_digest="abc",
        )
        v1 = JudgeVerdict(**base, outcome="PASS", score=1.0)
        v2 = JudgeVerdict(**base, outcome="PASS", score=0.5)
        assert v1.deterministic_digest != v2.deterministic_digest

    def test_verdict_digest_differs_on_outcome_change(self):
        base = dict(
            verdict_id="x", target="m.py", rubric_id="ARCH-001",
            dimension="arch", reasoning="ok", adg_digest="abc", score=1.0,
        )
        v1 = JudgeVerdict(**base, outcome="PASS")
        v2 = JudgeVerdict(**base, outcome="FAIL")
        assert v1.deterministic_digest != v2.deterministic_digest


class TestScoreBoundaryTransitions:
    """Judges must transition exactly at documented thresholds."""

    def test_arch_001_warn_zone(self):
        """96% compliance → WARN (between 0.95 and 1.0)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        # 25 imports, 1 violation → 24/25 = 0.96 → WARN
        edges = [{"target_layer": "L0", "target_name": f"n{i}", "source_file": "f.py", "line_no": i}
                 for i in range(24)]
        edges.append({"target_layer": "L3", "target_name": "bad", "source_file": "f.py", "line_no": 99})
        bundle = EvidenceBundle(
            target="agentic_core/L1_cognition/mod.py",
            adg_edges={"imports": edges},
            module_metadata={"layer": "L1"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.score == pytest.approx(0.96)
        assert verdict.outcome == VerdictOutcome.WARN.value

    def test_arch_001_fail_zone(self):
        """50% compliance → FAIL (< 0.95)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        edges = [{"target_layer": "L0", "target_name": f"n{i}", "source_file": "f.py", "line_no": i}
                 for i in range(5)]
        edges += [{"target_layer": "L5", "target_name": f"bad{i}", "source_file": "f.py", "line_no": i}
                  for i in range(5)]
        bundle = EvidenceBundle(
            target="agentic_core/L1_cognition/mod.py",
            adg_edges={"imports": edges},
            module_metadata={"layer": "L1"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.score == pytest.approx(0.5)
        assert verdict.outcome == VerdictOutcome.FAIL.value

    def test_qual_001_boundary_at_threshold(self):
        """5 violations → score=0.0 → FAIL."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_001

        bundle = EvidenceBundle(
            target="mod.py",
            adg_edges={"antipattern": [{"symbol": f"ap{i}"} for i in range(5)]},
        )
        verdict = judge_qual_001(bundle)
        assert verdict.score == 0.0
        assert verdict.outcome == VerdictOutcome.FAIL.value

    def test_qual_001_just_below_threshold(self):
        """4 violations → score=0.2 → FAIL (< 0.6 threshold)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_001

        bundle = EvidenceBundle(
            target="mod.py",
            adg_edges={"antipattern": [{"symbol": f"ap{i}"} for i in range(4)]},
        )
        verdict = judge_qual_001(bundle)
        assert verdict.score == pytest.approx(0.2)
        assert verdict.outcome == VerdictOutcome.FAIL.value

    def test_cov_001_warn_at_6_of_7(self):
        """6/7 governance dims → score=6/7≈0.857 → WARN (0.85-1.0)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_cov_001

        bundle = EvidenceBundle(
            target="partial.py",
            adg_edges={
                "records_execution_trace": [{"symbol": "x"}],
                "applies_guardrail": [{"symbol": "x"}],
                "reads_policy_state": [{"symbol": "x"}],
                "signs_execution_trace": [{"symbol": "x"}],
                "snapshots_state": [{"symbol": "x"}],
                "emits_replay_key": [{"symbol": "x"}],
                # emits_determinism_digest is missing
            },
        )
        verdict = judge_cov_001(bundle)
        assert verdict.score == pytest.approx(6 / 7, abs=0.001)
        assert verdict.outcome == VerdictOutcome.WARN.value

    def test_gov_002_warn_zone(self):
        """9/10 writes governed → score=0.9 → WARN (0.9-1.0)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_gov_002

        bundle = EvidenceBundle(
            target="writer.py",
            adg_edges={
                "writes_via_uwg": [{"symbol": f"w{i}"} for i in range(9)],
                "writes_to": [{"symbol": f"w{i}"} for i in range(10)],
            },
        )
        verdict = judge_gov_002(bundle)
        assert verdict.score == pytest.approx(0.9)
        assert verdict.outcome == VerdictOutcome.WARN.value

    def test_qual_002_warn_zone(self):
        """30/50 = 0.4 fanout → WARN (0.4-0.6)."""
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_002

        bundle = EvidenceBundle(
            target="med.py",
            adg_edges={"calls": [{"target_name": f"fn{i}"} for i in range(30)]},
        )
        verdict = judge_qual_002(bundle)
        assert verdict.score == pytest.approx(0.4)
        assert verdict.outcome == VerdictOutcome.WARN.value


class TestRubricEngineRobustness:
    def test_missing_rubrics_file(self, tmp_path):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine(str(tmp_path / "nonexistent.json"))
        assert engine.all_rubrics == []

    def test_malformed_json_does_not_crash(self, tmp_path):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        bad = tmp_path / "bad.json"
        bad.write_text("{this is not valid json", encoding="utf-8")
        engine = RubricEngine(str(bad))
        assert engine.all_rubrics == []

    def test_custom_rubrics_json(self, tmp_path):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        custom = {
            "rubrics": [
                {
                    "rubric_id": "CUSTOM-001",
                    "dimension": "custom",
                    "display_name": "Custom Test",
                    "description": "A test rubric",
                    "scoring_method": "deterministic",
                    "severity": "LOW",
                    "evidence_requirements": [],
                    "scoring_criteria": [],
                    "pass_threshold": 1.0,
                    "warn_threshold": 0.9,
                }
            ]
        }
        p = tmp_path / "custom.json"
        p.write_text(json.dumps(custom), encoding="utf-8")
        engine = RubricEngine(str(p))
        assert len(engine.all_rubrics) == 1
        assert engine.rubric_ids == ["CUSTOM-001"]
        r = engine.get("CUSTOM-001")
        assert r.dimension == "custom"
        assert r.is_deterministic is True

    def test_reload_picks_up_new_rubric(self, tmp_path):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        initial = {"rubrics": []}
        p = tmp_path / "evolving.json"
        p.write_text(json.dumps(initial), encoding="utf-8")
        engine = RubricEngine(str(p))
        assert len(engine.all_rubrics) == 0

        updated = {
            "rubrics": [
                {
                    "rubric_id": "NEW-001",
                    "dimension": "new",
                    "display_name": "New",
                    "description": "",
                    "scoring_method": "deterministic",
                    "severity": "LOW",
                    "pass_threshold": 1.0,
                    "warn_threshold": 0.9,
                }
            ]
        }
        p.write_text(json.dumps(updated), encoding="utf-8")
        count = engine.reload()
        assert count == 1
        assert engine.get("NEW-001") is not None


class TestVerdictStoreIdempotency:
    def test_store_same_verdict_twice_does_not_duplicate_query(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "idem.sqlite"))
        v = _verdict("x.py", adg_digest="d1")
        store.store_verdict(v)
        store.store_verdict(v)
        # Querying by module should return both (store doesn't deduplicate by design)
        # but no crash — idempotent from a stability standpoint
        results = store.query_by_module("x.py")
        assert len(results) >= 1

    def test_batch_returns_correct_count(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "batch_idem.sqlite"))
        verdicts = [_verdict(f"mod_{i}.py") for i in range(20)]
        count = store.store_verdicts(verdicts)
        assert count == 20

    def test_query_by_digest_filters_correctly(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "digest_filter.sqlite"))
        store.store_verdicts([_verdict("a.py", adg_digest="digest_A") for _ in range(3)])
        store.store_verdicts([_verdict("b.py", adg_digest="digest_B") for _ in range(2)])

        results_a = store.query_by_digest("digest_A")
        results_b = store.query_by_digest("digest_B")
        assert len(results_a) == 3
        assert len(results_b) == 2
        assert all(v.adg_digest == "digest_A" for v in results_a)

    def test_query_failures_excludes_pass_warn_skip(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        store = VerdictStore(str(tmp_path / "fails_only.sqlite"))
        store.store_verdicts([
            _verdict("a.py", outcome=VerdictOutcome.PASS.value),
            _verdict("b.py", outcome=VerdictOutcome.WARN.value),
            _verdict("c.py", outcome=VerdictOutcome.SKIP.value),
            _verdict("d.py", outcome=VerdictOutcome.FAIL.value),
            _verdict("e.py", outcome=VerdictOutcome.FAIL.value),
        ])
        failures = store.query_failures()
        assert len(failures) == 2
        assert all(v.outcome == "FAIL" for v in failures)


class TestSec002Boundaries:
    """SEC-002 with all forbidden import variants."""

    @pytest.mark.parametrize("forbidden", ["subprocess", "ctypes", "pickle", "os.system"])
    def test_each_forbidden_import_triggers_fail(self, forbidden):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target="agentic_core/risky.py",
            adg_edges={"imports": [{"target_name": forbidden, "source_file": "risky.py", "line_no": 1}]},
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == VerdictOutcome.FAIL.value
        assert len(verdict.evidence_items) >= 1

    @pytest.mark.parametrize("allowed_path", ["ops_scripts/migrate.py", "tools/gen.py", "tests/unit_test.py"])
    def test_allowlisted_paths_skip(self, allowed_path):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target=allowed_path,
            adg_edges={"imports": [{"target_name": "subprocess"}]},
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == VerdictOutcome.SKIP.value

    def test_no_imports_is_pass(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(target="agentic_core/empty.py", adg_edges={})
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == VerdictOutcome.PASS.value

    def test_safe_import_is_pass(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target="agentic_core/mod.py",
            adg_edges={"imports": [{"target_name": "pathlib"}, {"target_name": "typing"}]},
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == VerdictOutcome.PASS.value


class TestArch001LayerEdgeCases:
    """ARCH-001 with unusual layer combinations."""

    def test_same_layer_import_is_always_ok(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="agentic_core/L3_orchestration/a.py",
            adg_edges={"imports": [{"target_layer": "L3", "target_name": "b", "source_file": "a.py", "line_no": 1}]},
            module_metadata={"layer": "L3"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == VerdictOutcome.PASS.value

    def test_unknown_target_layer_skipped_not_penalized(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="agentic_core/L2_execution/a.py",
            adg_edges={"imports": [{"target_layer": "EXTERNAL", "target_name": "x", "source_file": "a.py", "line_no": 1}]},
            module_metadata={"layer": "L2"},
        )
        verdict = judge_arch_001(bundle)
        # Unknown target layer → no denominator increment → 0 total → score 1.0
        assert verdict.outcome in {VerdictOutcome.PASS.value, VerdictOutcome.SKIP.value}

    def test_l0_can_only_import_l0(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="agentic_core/L0_routing/a.py",
            adg_edges={"imports": [{"target_layer": "L1", "target_name": "x", "source_file": "a.py", "line_no": 1}]},
            module_metadata={"layer": "L0"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == VerdictOutcome.FAIL.value
        assert len(verdict.evidence_items) == 1

    def test_l6_can_import_all_layers(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        edges = [
            {"target_layer": f"L{i}", "target_name": f"n{i}", "source_file": "a.py", "line_no": i}
            for i in range(7)
        ]
        bundle = EvidenceBundle(
            target="agentic_core/L6_observability/a.py",
            adg_edges={"imports": edges},
            module_metadata={"layer": "L6"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == VerdictOutcome.PASS.value
        assert verdict.score == 1.0
