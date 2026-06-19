"""Wave 5 ADG testing-hotspots — apps_eval.contracts.models pure surface.

Substitution note: the Wave-5 plan listed ``apps_eval/engines/scorecard_engine.py``
and ``regression_detector.py`` which do not exist in this repo. The nearest
untested equivalent carrying the scorecard / regression data contracts is
``apps_eval/contracts/models.py`` — the frozen dataclasses (EvalRequest,
EvalScenario, AppOutputSnapshot, GraderFinding, Scorecard, RegressionSummary,
CompletedEvalRecord, L6EvalHandoff). This module covers their defaults,
frozen-ness, __post_init__ validation, and (de)serialization round-trips.
"""

from __future__ import annotations

import dataclasses

import pytest

from apps_eval.contracts.models import (
    CURRENT_EVAL_RECORD_SCHEMA_VERSION,
    CURRENT_RELEASE_GATE_SCHEMA_VERSION,
    CURRENT_REGRESSION_FLYWHEEL_SCHEMA_VERSION,
    CURRENT_TREND_DASHBOARD_SCHEMA_VERSION,
    ALLOWED_APPS,
    AppOutputSnapshot,
    CompletedEvalRecord,
    EvalRequest,
    EvalScenario,
    EvalRunMetadata,
    FixtureProvenance,
    GraderFinding,
    L6EvalHandoff,
    RegressionSummary,
    RegressionFlywheelSummary,
    ReleaseGateDecision,
    Scorecard,
    TrendDashboardSummary,
    TrendSample,
    TrendSuiteSummary,
)


def _scorecard(**overrides) -> Scorecard:
    base = dict(
        suite_id="suite",
        app_id="apps_rg",
        scenario_count=1,
        finding_count=2,
        passed_findings=2,
        failed_findings=0,
        block_failures=0,
        score=1.0,
        verdict="pass",
    )
    base.update(overrides)
    return Scorecard(**base)


class TestModuleConstants:
    def test_allowed_apps_set(self):
        assert ALLOWED_APPS == {"apps_rg", "apps_lic"}

    def test_completed_eval_schema_version_is_explicit(self):
        assert CURRENT_EVAL_RECORD_SCHEMA_VERSION.endswith(".v3")

    def test_trend_schema_versions_are_explicit(self):
        assert CURRENT_TREND_DASHBOARD_SCHEMA_VERSION.endswith(".v1")
        assert CURRENT_RELEASE_GATE_SCHEMA_VERSION.endswith(".v1")


class TestEvalRequest:
    def test_defaults(self):
        req = EvalRequest(suite_id="s1")
        assert req.mode == "snapshot"
        assert req.deterministic_only is True
        assert req.with_judge is False
        assert req.compare_baseline is False
        assert req.out_dir == "artifacts/apps_eval/runs"
        assert req.emit_l6_handoff is False

    def test_is_frozen(self):
        req = EvalRequest(suite_id="s1")
        with pytest.raises(dataclasses.FrozenInstanceError):
            req.suite_id = "other"  # type: ignore[misc]

    @pytest.mark.parametrize("mode", ["snapshot", "live_adapter"])
    def test_valid_modes_accepted(self, mode):
        assert EvalRequest(suite_id="s1", mode=mode).mode == mode  # type: ignore[arg-type]

    def test_unsupported_mode_rejected(self):
        with pytest.raises(ValueError, match="unsupported mode"):
            EvalRequest(suite_id="s1", mode="bogus")  # type: ignore[arg-type]

    def test_judge_requires_non_deterministic(self):
        with pytest.raises(ValueError, match="with-judge requires"):
            EvalRequest(suite_id="s1", with_judge=True, deterministic_only=True)

    def test_judge_allowed_when_not_deterministic_only(self):
        req = EvalRequest(suite_id="s1", with_judge=True, deterministic_only=False)
        assert req.with_judge is True


class TestEvalScenario:
    def test_holdout_defaults_false(self):
        sc = EvalScenario(
            scenario_id="sc",
            suite_id="su",
            app_id="apps_rg",
            description="d",
            fixture_path="/x",
            graders=("schema",),
            rubric_id="r1",
        )
        assert sc.holdout is False
        assert sc.graders == ("schema",)

    @pytest.mark.parametrize("app_id", ["apps_rg", "apps_lic"])
    def test_valid_app_ids(self, app_id):
        sc = EvalScenario(
            scenario_id="sc",
            suite_id="su",
            app_id=app_id,
            description="d",
            fixture_path="/x",
            graders=(),
            rubric_id="r1",
        )
        assert sc.app_id == app_id

    def test_unsupported_app_id_rejected(self):
        with pytest.raises(ValueError, match="unsupported app_id"):
            EvalScenario(
                scenario_id="sc",
                suite_id="su",
                app_id="apps_nope",
                description="d",
                fixture_path="/x",
                graders=(),
                rubric_id="r1",
            )


class TestAppOutputSnapshot:
    def test_defaults_for_collection_fields(self):
        snap = AppOutputSnapshot(
            app_id="apps_rg", scenario_id="s1", x3_disposition="X3A", output={}
        )
        assert snap.claims == []
        assert snap.artifacts == []
        assert snap.provenance == {}
        assert snap.side_effects == {}
        assert snap.deterministic_hash == ""

    def test_from_dict_empty_uses_defaults(self):
        snap = AppOutputSnapshot.from_dict({})
        assert snap.app_id == ""
        assert snap.scenario_id == ""
        assert snap.output == {}
        assert snap.claims == []

    def test_from_dict_populates_all_fields(self):
        data = {
            "app_id": "apps_lic",
            "scenario_id": "s9",
            "x3_disposition": "X3B_ESCALATE_HITL",
            "output": {"k": 1},
            "claims": [{"id": "c1"}],
            "artifacts": ["a.json"],
            "provenance": {"evidence_refs": ["e1"]},
            "side_effects": {"writes": []},
            "deterministic_hash": "abc",
        }
        snap = AppOutputSnapshot.from_dict(data)
        assert snap.app_id == "apps_lic"
        assert snap.claims == [{"id": "c1"}]
        assert snap.artifacts == ["a.json"]
        assert snap.deterministic_hash == "abc"

    def test_to_dict_roundtrip_keys(self):
        snap = AppOutputSnapshot(
            app_id="apps_rg", scenario_id="s1", x3_disposition="X3A", output={"k": 1}
        )
        d = snap.to_dict()
        assert d["app_id"] == "apps_rg"
        assert "deterministic_hash" in d
        # from_dict(to_dict(x)) is identity on the modelled fields.
        assert AppOutputSnapshot.from_dict(d) == snap

    def test_from_dict_coerces_non_string_scalars(self):
        snap = AppOutputSnapshot.from_dict({"app_id": 123, "scenario_id": 9})
        assert snap.app_id == "123"
        assert snap.scenario_id == "9"


class TestGraderFinding:
    def test_to_dict(self):
        finding = GraderFinding(
            grader_id="schema",
            scenario_id="s1",
            passed=True,
            severity="block",
            score=1.0,
            message="ok",
        )
        d = finding.to_dict()
        assert d["grader_id"] == "schema"
        assert d["passed"] is True
        assert d["evidence"] == {}
        assert d["failure_mode"] == ""


class TestScorecardAndRegression:
    def test_scorecard_dimension_scores_default(self):
        sc = _scorecard()
        assert sc.dimension_scores == {}
        assert sc.failure_mode_counts == {}
        assert sc.failure_family_counts == {}
        assert sc.to_dict()["verdict"] == "pass"

    def test_regression_summary_defaults(self):
        reg = RegressionSummary(compared=False)
        assert reg.verdict == "not_compared"
        assert reg.delta == 0.0
        assert reg.baseline_path == ""
        assert reg.baseline_digest == ""

    def test_regression_to_dict(self):
        reg = RegressionSummary(compared=True, delta=-0.1, verdict="regression")
        d = reg.to_dict()
        assert d["compared"] is True
        assert d["verdict"] == "regression"


class TestTrendContracts:
    def test_trend_sample_to_dict(self):
        sample = TrendSample(
            record_id="rid",
            suite_id="apps_rg.dev.resume_generation",
            app_id="apps_rg",
            split="dev",
            created_at="2026-06-17T00:00:00Z",
            score=1.0,
            scorecard_verdict="pass",
            regression_verdict="not_compared",
            block_failures=0,
        )
        d = sample.to_dict()
        assert d["record_id"] == "rid"
        assert d["split"] == "dev"
        assert d["failure_mode_counts"] == {}
        assert d["failure_family_counts"] == {}

    def test_suite_and_dashboard_defaults(self):
        suite = TrendSuiteSummary(suite_id="apps_rg.dev.resume_generation", app_id="apps_rg", split="dev", sample_count=0)
        dashboard = TrendDashboardSummary()
        decision = ReleaseGateDecision()
        assert suite.sample_count == 0
        assert dashboard.artifact_paths == {}
        assert dashboard.trend_dashboard_digest == ""
        assert dashboard.suite_summaries == []
        assert dashboard.to_dict()["artifact_paths"] == {}
        assert dashboard.to_dict()["trend_dashboard_digest"] == ""
        assert decision.status == "blocked"
        assert decision.decision_kind == "ADVISORY_EVAL_REGRESSION_CHECK"
        assert decision.release_authority == "NONE"
        assert decision.artifact_paths == {}
        assert decision.to_dict()["schema_version"] == CURRENT_RELEASE_GATE_SCHEMA_VERSION


class TestCompletedEvalRecord:
    def test_nested_to_dict_serializes_children(self):
        sc = _scorecard()
        reg = RegressionSummary(compared=False)
        rec = CompletedEvalRecord(
            record_id="rid",
            created_at="t",
            suite_id="suite",
            app_id="apps_rg",
            mode="snapshot",
            deterministic_only=True,
            scenario_results=[],
            scorecard=sc,
            regression=reg,
            artifact_paths={},
            rubric_ids=["r1"],
        )
        d = rec.to_dict()
        # Nested dataclasses become plain dicts, not dataclass instances.
        assert isinstance(d["scorecard"], dict)
        assert d["scorecard"]["verdict"] == "pass"
        assert isinstance(d["regression"], dict)
        assert d["regression"]["compared"] is False
        assert d["schema_version"] == CURRENT_EVAL_RECORD_SCHEMA_VERSION
        assert d["record_seed"] == {}
        assert d["run_metadata"]["scorer_version"].endswith(".v2")
        assert d["fixture_provenance"] == []
        assert d["regression_flywheel"]["schema_version"] == CURRENT_REGRESSION_FLYWHEEL_SCHEMA_VERSION
        assert d["regression_flywheel"]["current_failure_mode_counts"] == {}


class TestRegressionFlywheelSummary:
    def test_to_dict(self):
        flywheel = RegressionFlywheelSummary(
            compared=True,
            baseline_path="/tmp/base.json",
            baseline_digest="base",
            current_score=0.9,
            baseline_score=1.0,
            delta=-0.1,
            verdict="regression",
            current_failure_mode_counts={"policy.x3_disposition_mismatch": 2},
            current_failure_family_counts={"policy": 2},
            dominant_failure_mode="policy.x3_disposition_mismatch",
            dominant_failure_family="policy",
            new_failure_modes=["policy.x3_disposition_mismatch"],
            recovered_failure_modes=[],
            repeated_failure_modes=["policy.x3_disposition_mismatch"],
            scenario_hotspots=[{"scenario_id": "sc1", "failed_findings": 2, "block_failures": 2}],
        )
        d = flywheel.to_dict()
        assert d["schema_version"] == CURRENT_REGRESSION_FLYWHEEL_SCHEMA_VERSION
        assert d["compared"] is True
        assert d["dominant_failure_mode"] == "policy.x3_disposition_mismatch"


class TestProvenanceContracts:
    def test_fixture_provenance_to_dict(self):
        provenance = FixtureProvenance(
            scenario_id="sc1",
            fixture_path="/tmp/sc1",
            scenario_definition_digest="a",
            input_request_digest="b",
            expected_digest="c",
            snapshot_digest="d",
        )
        d = provenance.to_dict()
        assert d["schema_version"].endswith(".v1")
        assert d["scenario_id"] == "sc1"

    def test_run_metadata_to_dict(self):
        metadata = EvalRunMetadata(
            project_version="1.0.0",
            git_commit="abc",
            python_version="3.11.0",
            platform="win32",
            cwd="/repo",
            record_seed_digest="digest",
            baseline_digest="base",
            mode="snapshot",
            deterministic_only=True,
            compare_baseline=False,
        )
        d = metadata.to_dict()
        assert d["project_name"] == "agentic-workflow"
        assert d["git_commit"] == "abc"
        assert d["record_seed_digest"] == "digest"


class TestL6EvalHandoff:
    def test_invariant_defaults(self):
        handoff = L6EvalHandoff(
            record_id="rid",
            suite_id="suite",
            app_id="apps_rg",
            eval_record_path="p/eval_record.json",
            score=1.0,
            verdict="pass",
            finding_count=3,
            block_failures=0,
        )
        # L6 must never request mutation of the current run.
        assert handoff.current_run_mutated is False
        assert handoff.requested_action == "consume_completed_eval_record_only"

    def test_to_dict(self):
        handoff = L6EvalHandoff(
            record_id="rid",
            suite_id="suite",
            app_id="apps_rg",
            eval_record_path="p",
            score=0.5,
            verdict="fail",
            finding_count=1,
            block_failures=1,
        )
        assert handoff.to_dict()["verdict"] == "fail"
