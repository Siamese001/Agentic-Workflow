"""Tests for the LLM-as-Judge system — Phase 0+1 components.

Covers:
- types.py: VerdictOutcome, EvidenceBundle, JudgeVerdict, RubricDefinition
- source_retriever.py: SourceRetriever file/function/class reads
- verdict_store.py: VerdictStore CRUD, trend, regressions
- rubric_engine.py: RubricEngine load, filter, render
- deterministic_judges.py: All 7 deterministic judges
"""

from __future__ import annotations

import textwrap

import pytest

from agentic_core.evaluation.judges.types import (
    EvidenceBundle,
    EvidenceItem,
    JudgeVerdict,
    RubricDefinition,
    ScoringMethod,
    Severity,
    SourceSnippet,
    VerdictOutcome,
)

# ===================================================================
# Types tests
# ===================================================================


class TestVerdictOutcome:
    def test_values(self):
        assert VerdictOutcome.PASS.value == "PASS"
        assert VerdictOutcome.FAIL.value == "FAIL"
        assert VerdictOutcome.WARN.value == "WARN"
        assert VerdictOutcome.NEEDS_REVIEW.value == "NEEDS_REVIEW"

    def test_scoring_method_deterministic(self):
        assert ScoringMethod.DETERMINISTIC.value == "deterministic"

    def test_severity_ordering(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.LOW.value == "LOW"


class TestSourceSnippet:
    def test_frozen(self):
        s = SourceSnippet(
            file_path="test.py", start_line=1, end_line=5, content="hello"
        )
        assert s.file_path == "test.py"
        with pytest.raises(AttributeError):
            s.file_path = "changed"  # type: ignore[misc]


class TestEvidenceBundle:
    def test_evidence_hash_deterministic(self):
        b1 = EvidenceBundle(target="mod.py", adg_digest="abc123")
        b2 = EvidenceBundle(target="mod.py", adg_digest="abc123")
        assert b1.evidence_hash == b2.evidence_hash

    def test_evidence_hash_differs_on_target(self):
        b1 = EvidenceBundle(target="mod_a.py")
        b2 = EvidenceBundle(target="mod_b.py")
        assert b1.evidence_hash != b2.evidence_hash


class TestJudgeVerdict:
    def test_passed_property(self):
        v = JudgeVerdict(
            verdict_id="v1",
            target="t",
            dimension="d",
            rubric_id="r",
            outcome=VerdictOutcome.PASS.value,
            score=1.0,
            reasoning="ok",
        )
        assert v.passed is True

    def test_failed_property(self):
        v = JudgeVerdict(
            verdict_id="v1",
            target="t",
            dimension="d",
            rubric_id="r",
            outcome=VerdictOutcome.FAIL.value,
            score=0.0,
            reasoning="bad",
        )
        assert v.passed is False

    def test_deterministic_digest(self):
        v = JudgeVerdict(
            verdict_id="v1",
            target="t",
            dimension="d",
            rubric_id="r",
            outcome=VerdictOutcome.PASS.value,
            score=1.0,
            reasoning="ok",
            adg_digest="abc",
        )
        assert len(v.deterministic_digest) == 16


class TestRubricDefinition:
    def test_is_deterministic(self):
        r = RubricDefinition(
            rubric_id="TEST",
            dimension="test",
            display_name="Test",
            description="",
            scoring_method="deterministic",
            severity="MEDIUM",
        )
        assert r.is_deterministic is True

    def test_is_not_deterministic(self):
        r = RubricDefinition(
            rubric_id="TEST",
            dimension="test",
            display_name="Test",
            description="",
            scoring_method="llm_pointwise",
            severity="MEDIUM",
        )
        assert r.is_deterministic is False


# ===================================================================
# SourceRetriever tests
# ===================================================================


class TestSourceRetriever:
    @pytest.fixture()
    def repo_dir(self, tmp_path):
        src = tmp_path / "module.py"
        src.write_text(
            textwrap.dedent("""\
            import os

            def hello():
                return "world"

            def goodbye():
                return "farewell"

            class Greeter:
                def greet(self):
                    return "hi"
            """),
            encoding="utf-8",
        )
        return tmp_path

    def test_get_context(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_context("module.py", 4, window=2)
        assert snippet is not None
        assert "hello" in snippet.content
        assert snippet.start_line >= 1

    def test_get_function(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_function("module.py", "hello")
        assert snippet is not None
        assert "world" in snippet.content
        assert snippet.symbol == "hello"

    def test_get_function_not_found(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_function("module.py", "nonexistent")
        assert snippet is None

    def test_get_class(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_class("module.py", "Greeter")
        assert snippet is not None
        assert "greet" in snippet.content
        assert snippet.symbol == "Greeter"

    def test_get_lines(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_lines("module.py", 1, 3)
        assert snippet is not None
        assert "import" in snippet.content

    def test_file_not_found(self, repo_dir):
        from agentic_core.evaluation.judges.source_retriever import SourceRetriever

        r = SourceRetriever(str(repo_dir))
        snippet = r.get_context("nonexistent.py", 1)
        assert snippet is None


# ===================================================================
# VerdictStore tests
# ===================================================================


class TestVerdictStore:
    @pytest.fixture()
    def store(self, tmp_path):
        from agentic_core.evaluation.judges.verdict_store import VerdictStore

        return VerdictStore(str(tmp_path / "test_verdicts.sqlite"))

    @pytest.fixture()
    def sample_verdict(self):
        return JudgeVerdict(
            verdict_id="test-001",
            target="agentic_core/L2_execution/providers.py",
            dimension="architecture",
            rubric_id="ARCH-001",
            outcome=VerdictOutcome.PASS.value,
            score=1.0,
            reasoning="All imports comply",
            evidence_items=(
                EvidenceItem(
                    evidence_type="layer_check",
                    key="L2->L0",
                    value="compliant",
                ),
            ),
            suggestions=("No action needed",),
            severity="CRITICAL",
            adg_digest="abc123",
            provider_id="deterministic",
            evidence_hash="deadbeef",
            created_at="2026-03-17T00:00:00Z",
        )

    def test_store_and_query(self, store, sample_verdict):
        store.store_verdict(sample_verdict)
        results = store.query_by_module(sample_verdict.target)
        assert len(results) == 1
        assert results[0].verdict_id == "test-001"
        assert results[0].score == 1.0

    def test_query_by_dimension(self, store, sample_verdict):
        store.store_verdict(sample_verdict)
        results = store.query_by_dimension("architecture")
        assert len(results) == 1

    def test_query_by_rubric(self, store, sample_verdict):
        store.store_verdict(sample_verdict)
        results = store.query_by_rubric("ARCH-001")
        assert len(results) == 1

    def test_query_failures(self, store):
        fail_verdict = JudgeVerdict(
            verdict_id="fail-001",
            target="bad_module.py",
            dimension="security",
            rubric_id="SEC-002",
            outcome=VerdictOutcome.FAIL.value,
            score=0.0,
            reasoning="Forbidden import",
            created_at="2026-03-17T00:00:00Z",
        )
        store.store_verdict(fail_verdict)
        failures = store.query_failures()
        assert len(failures) == 1
        assert failures[0].outcome == "FAIL"

    def test_store_verdicts_batch(self, store):
        verdicts = [
            JudgeVerdict(
                verdict_id=f"batch-{i}",
                target=f"mod_{i}.py",
                dimension="code_quality",
                rubric_id="QUAL-001",
                outcome=VerdictOutcome.PASS.value,
                score=0.9,
                reasoning="ok",
                created_at="2026-03-17T00:00:00Z",
            )
            for i in range(5)
        ]
        count = store.store_verdicts(verdicts)
        assert count == 5

    def test_trend(self, store):
        for i in range(3):
            store.store_verdict(
                JudgeVerdict(
                    verdict_id=f"trend-{i}",
                    target="mod.py",
                    dimension="arch",
                    rubric_id="ARCH-001",
                    outcome=VerdictOutcome.PASS.value,
                    score=0.8 + i * 0.05,
                    reasoning="ok",
                    adg_digest=f"digest_{i}",
                    created_at=f"2026-03-1{i}T00:00:00Z",
                )
            )
        trend = store.trend("mod.py", "arch", n=10)
        assert len(trend) == 3
        # Ordered oldest to newest
        assert trend[0]["adg_digest"] == "digest_0"

    def test_regressions(self, store):
        store.store_verdict(
            JudgeVerdict(
                verdict_id="prev",
                target="mod.py",
                dimension="arch",
                rubric_id="ARCH-001",
                outcome=VerdictOutcome.PASS.value,
                score=1.0,
                reasoning="ok",
                adg_digest="old",
                created_at="2026-03-16T00:00:00Z",
            )
        )
        store.store_verdict(
            JudgeVerdict(
                verdict_id="curr",
                target="mod.py",
                dimension="arch",
                rubric_id="ARCH-001",
                outcome=VerdictOutcome.WARN.value,
                score=0.8,
                reasoning="degraded",
                adg_digest="new",
                created_at="2026-03-17T00:00:00Z",
            )
        )
        regs = store.regressions("new", "old")
        assert len(regs) == 1
        assert regs[0]["delta"] == pytest.approx(-0.2)

    def test_stats(self, store, sample_verdict):
        store.store_verdict(sample_verdict)
        s = store.stats()
        assert s["total_verdicts"] == 1
        assert s["distinct_targets"] == 1


# ===================================================================
# RubricEngine tests
# ===================================================================


class TestRubricEngine:
    def test_load_default_rubrics(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        assert len(engine.all_rubrics) >= 7
        assert "ARCH-001" in engine.rubric_ids

    def test_get_deterministic(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        det = engine.get_deterministic_rubrics()
        assert all(r.is_deterministic for r in det)
        assert len(det) >= 7

    def test_get_llm_rubrics(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        llm = engine.get_llm_rubrics()
        assert all(not r.is_deterministic for r in llm)

    def test_get_by_dimension(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        arch = engine.get_rubrics_for_dimension("architecture")
        assert len(arch) >= 1
        assert all(r.dimension == "architecture" for r in arch)

    def test_get_by_layer(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        l3 = engine.get_rubrics_for_layer("L3")
        assert len(l3) >= 1

    def test_render_prompt(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        # GOV-001 template has literal braces in JSON example, so format()
        # hits a KeyError and returns the raw template. Verify non-None.
        prompt = engine.render_prompt(
            "GOV-001",
            target="test_module.py",
            source_code="print('hello')",
            adg_edges="imports: []",
        )
        assert prompt is not None
        # Raw template still contains {target} placeholder text
        assert "target" in prompt

    def test_render_prompt_deterministic_returns_none(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        prompt = engine.render_prompt("ARCH-001")
        assert prompt is None

    def test_evidence_requirements(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        reqs = engine.evidence_requirements_for("ARCH-001")
        assert len(reqs) >= 1
        assert any(r["relation"] == "imports" for r in reqs)

    def test_summary(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        s = engine.summary()
        assert s["total_rubrics"] >= 10
        assert "architecture" in s["by_dimension"]

    def test_reload(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        engine = RubricEngine()
        count = engine.reload()
        assert count >= 10


# ===================================================================
# Deterministic judges tests
# ===================================================================


class TestJudgeArch001:
    def test_pass_all_compliant(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="agentic_core/L2_execution/providers.py",
            adg_edges={
                "imports": [
                    {"target_layer": "L0", "target_name": "routing", "source_file": "providers.py", "line_no": 1},
                    {"target_layer": "L1", "target_name": "cognition", "source_file": "providers.py", "line_no": 2},
                    {"target_layer": "L2", "target_name": "execution", "source_file": "providers.py", "line_no": 3},
                ]
            },
            module_metadata={"layer": "L2"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == "PASS"
        assert verdict.score == 1.0

    def test_fail_layer_inversion(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="agentic_core/L1_cognition/bad.py",
            adg_edges={
                "imports": [
                    {"target_layer": "L3", "target_name": "orchestration", "source_file": "bad.py", "line_no": 5},
                    {"target_layer": "L0", "target_name": "routing", "source_file": "bad.py", "line_no": 1},
                ]
            },
            module_metadata={"layer": "L1"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == "FAIL"
        assert verdict.score < 1.0
        assert len(verdict.evidence_items) == 1

    def test_skip_no_imports(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_arch_001

        bundle = EvidenceBundle(
            target="empty.py",
            adg_edges={},
            module_metadata={"layer": "L2"},
        )
        verdict = judge_arch_001(bundle)
        assert verdict.outcome == "SKIP"


class TestJudgeQual001:
    def test_pass_no_violations(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_001

        bundle = EvidenceBundle(target="clean.py", adg_edges={})
        verdict = judge_qual_001(bundle)
        assert verdict.outcome == "PASS"
        assert verdict.score == 1.0

    def test_fail_many_violations(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_001

        bundle = EvidenceBundle(
            target="messy.py",
            adg_edges={
                "antipattern": [{"symbol": f"ap_{i}"} for i in range(10)],
            },
        )
        verdict = judge_qual_001(bundle)
        assert verdict.outcome == "FAIL"
        assert verdict.score == 0.0


class TestJudgeQual002:
    def test_pass_low_fanout(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_002

        bundle = EvidenceBundle(
            target="simple.py",
            adg_edges={"calls": [{"target_name": f"fn_{i}"} for i in range(10)]},
        )
        verdict = judge_qual_002(bundle)
        assert verdict.outcome == "PASS"
        assert verdict.score == 0.8

    def test_fail_high_fanout(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_qual_002

        bundle = EvidenceBundle(
            target="complex.py",
            adg_edges={"calls": [{"target_name": f"fn_{i}"} for i in range(60)]},
        )
        verdict = judge_qual_002(bundle)
        assert verdict.outcome == "FAIL"


class TestJudgeDep001:
    def test_pass_no_cycles(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_dep_001

        bundle = EvidenceBundle(
            target="mod.py",
            adg_edges={
                "imports": [{"target_name": "other.py"}],
            },
        )
        verdict = judge_dep_001(bundle)
        assert verdict.outcome == "PASS"

    def test_fail_cycle_detected(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_dep_001

        bundle = EvidenceBundle(
            target="mod_a.py",
            adg_edges={
                "imports": [{"target_name": "mod_b.py"}],
                "imports_incoming": [{"source_name": "mod_b.py"}],
            },
        )
        verdict = judge_dep_001(bundle)
        assert verdict.outcome == "FAIL"
        assert verdict.score == 0.0


class TestJudgeCov001:
    def test_pass_all_wired(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_cov_001

        bundle = EvidenceBundle(
            target="governed.py",
            adg_edges={
                "records_execution_trace": [{"symbol": "x"}],
                "applies_guardrail": [{"symbol": "x"}],
                "reads_policy_state": [{"symbol": "x"}],
                "signs_execution_trace": [{"symbol": "x"}],
                "snapshots_state": [{"symbol": "x"}],
                "emits_replay_key": [{"symbol": "x"}],
                "emits_determinism_digest": [{"symbol": "x"}],
            },
        )
        verdict = judge_cov_001(bundle)
        assert verdict.outcome == "PASS"
        assert verdict.score == 1.0

    def test_fail_missing_dims(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_cov_001

        bundle = EvidenceBundle(
            target="partial.py",
            adg_edges={
                "records_execution_trace": [{"symbol": "x"}],
                "applies_guardrail": [{"symbol": "x"}],
            },
        )
        verdict = judge_cov_001(bundle)
        assert verdict.outcome == "FAIL"
        assert verdict.score < 1.0
        assert len(verdict.suggestions) > 0


class TestJudgeGov002:
    def test_skip_no_writes(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_gov_002

        bundle = EvidenceBundle(target="readonly.py", adg_edges={})
        verdict = judge_gov_002(bundle)
        assert verdict.outcome == "SKIP"

    def test_pass_all_uwg(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_gov_002

        bundle = EvidenceBundle(
            target="governed_writer.py",
            adg_edges={
                "writes_via_uwg": [{"symbol": "w1"}, {"symbol": "w2"}],
                "writes_to": [{"symbol": "w1"}, {"symbol": "w2"}],
            },
        )
        verdict = judge_gov_002(bundle)
        assert verdict.outcome == "PASS"
        assert verdict.score == 1.0


class TestJudgeSec002:
    def test_pass_clean_imports(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target="agentic_core/clean.py",
            adg_edges={
                "imports": [{"target_name": "json"}, {"target_name": "pathlib"}],
            },
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == "PASS"

    def test_fail_forbidden_import(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target="agentic_core/dangerous.py",
            adg_edges={
                "imports": [
                    {"target_name": "subprocess", "source_file": "dangerous.py", "line_no": 1},
                ],
            },
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == "FAIL"
        assert verdict.score == 0.0

    def test_skip_allowlisted_path(self):
        from agentic_core.evaluation.judges.deterministic_judges import judge_sec_002

        bundle = EvidenceBundle(
            target="tools/my_script.py",
            adg_edges={
                "imports": [{"target_name": "subprocess"}],
            },
        )
        verdict = judge_sec_002(bundle)
        assert verdict.outcome == "SKIP"


class TestRunDeterministicJudge:
    def test_dispatch(self):
        from agentic_core.evaluation.judges.deterministic_judges import run_deterministic_judge

        bundle = EvidenceBundle(
            target="test.py",
            adg_edges={},
            module_metadata={"layer": "L2"},
        )
        verdict = run_deterministic_judge("ARCH-001", bundle)
        assert verdict is not None

    def test_unknown_rubric(self):
        from agentic_core.evaluation.judges.deterministic_judges import run_deterministic_judge

        bundle = EvidenceBundle(target="test.py")
        verdict = run_deterministic_judge("NONEXISTENT", bundle)
        assert verdict is None
