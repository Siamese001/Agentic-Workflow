"""Small data contracts for deterministic evaluation runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ALLOWED_APPS = {"apps_rg", "apps_lic"}
EvalMode = Literal["snapshot", "live_adapter", "current_snapshot"]
PROJECT_NAME = "agentic-workflow"
CURRENT_EVAL_RECORD_SCHEMA_VERSION = "apps_eval.completed_eval.v3"
CURRENT_EVAL_MANIFEST_SCHEMA_VERSION = "apps_eval.eval_manifest.v2"
CURRENT_EVAL_RUN_METADATA_SCHEMA_VERSION = "apps_eval.run_metadata.v1"
CURRENT_FIXTURE_PROVENANCE_SCHEMA_VERSION = "apps_eval.fixture_provenance.v1"
CURRENT_REGRESSION_FLYWHEEL_SCHEMA_VERSION = "apps_eval.regression_flywheel.v1"
CURRENT_TREND_DASHBOARD_SCHEMA_VERSION = "apps_eval.trend_dashboard.v1"
CURRENT_RELEASE_GATE_SCHEMA_VERSION = "apps_eval.release_gate.v1"
CURRENT_SCORER_VERSION = "apps_eval.graders.deterministic.v2"
CURRENT_SCORECARD_ROW_SCHEMA_VERSION = "apps_eval.scorecard_row.v1"
CURRENT_APPS_RG_MICROSTEP_CONTRACT_SCHEMA_VERSION = "apps_eval.apps_rg_stage_microstep_contract.v1"
CURRENT_DIAGNOSTIC_OBSERVATION_SCHEMA_VERSION = "apps_eval.diagnostic_observation.v1"
CURRENT_DIAGNOSTIC_SUMMARY_SCHEMA_VERSION = "apps_eval.diagnostic_summary.v1"

ScorecardRowVerdict = Literal["PASS", "FAIL", "WARN", "UNKNOWN", "NOT_RUN", "NOT_APPLICABLE"]
ScorecardRowSeverity = Literal["BLOCK", "MAJOR", "MINOR", "WARN", "INFO"]
DiagnosticVerdict = Literal["PASS", "WARN", "FAIL", "NOT_OBSERVED"]
DiagnosticPromotionState = Literal["shadow", "warning", "release_candidate", "blocking"]
DiagnosticOverlap = Literal["none", "enriches", "duplicates"]
DiagnosticAuthority = Literal["post_run_l6_shadow_only"]
AppsRgStageId = Literal[
    "U0",
    "L1",
    "L0",
    "C0",
    "PA",
    "L2",
    "X2",
    "X1D",
    "X3",
    "EXIT",
    "UWG",
    "L6",
    "PACKAGE",
    "REGRESSION",
]


@dataclass(frozen=True)
class EvalRequest:
    suite_id: str
    mode: EvalMode = "snapshot"
    deterministic_only: bool = True
    with_judge: bool = False
    compare_baseline: bool = False
    baseline_path: str = ""
    out_dir: str = "artifacts/apps_eval/runs"
    emit_l6_handoff: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"snapshot", "live_adapter", "current_snapshot"}:
            raise ValueError(f"unsupported mode: {self.mode}")
        if self.with_judge and self.deterministic_only:
            raise ValueError("--with-judge requires deterministic_only=false")


@dataclass(frozen=True)
class EvalScenario:
    scenario_id: str
    suite_id: str
    app_id: str
    description: str
    fixture_path: str
    graders: tuple[str, ...]
    rubric_id: str
    holdout: bool = False

    def __post_init__(self) -> None:
        if self.app_id not in ALLOWED_APPS:
            raise ValueError(f"unsupported app_id: {self.app_id}")


@dataclass(frozen=True)
class FixtureProvenance:
    schema_version: str = CURRENT_FIXTURE_PROVENANCE_SCHEMA_VERSION
    scenario_id: str = ""
    fixture_path: str = ""
    scenario_definition_digest: str = ""
    input_request_digest: str = ""
    expected_digest: str = ""
    snapshot_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvalRunMetadata:
    schema_version: str = CURRENT_EVAL_RUN_METADATA_SCHEMA_VERSION
    project_name: str = PROJECT_NAME
    project_version: str = ""
    git_commit: str = ""
    python_version: str = ""
    platform: str = ""
    cwd: str = ""
    runner: str = "apps_eval.runner.core"
    scorer_version: str = CURRENT_SCORER_VERSION
    record_seed_digest: str = ""
    baseline_digest: str = ""
    mode: str = "snapshot"
    deterministic_only: bool = True
    with_judge: bool = False
    compare_baseline: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvalFixture:
    scenario: EvalScenario
    input_dir: str
    expected_dir: str
    snapshot_path: str
    artifacts_dir: str
    expected: dict[str, Any]
    provenance: FixtureProvenance = field(default_factory=FixtureProvenance)


@dataclass(frozen=True)
class AppOutputSnapshot:
    app_id: str
    scenario_id: str
    x3_disposition: str
    output: dict[str, Any]
    claims: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    side_effects: dict[str, Any] = field(default_factory=dict)
    deterministic_hash: str = ""
    run_root: str = ""
    artifact_index: dict[str, Any] = field(default_factory=dict)
    bundle_indexes: list[dict[str, Any]] = field(default_factory=list)
    receipts: list[dict[str, Any]] = field(default_factory=list)
    lane_rows: list[dict[str, Any]] = field(default_factory=list)
    component_rows: list[dict[str, Any]] = field(default_factory=list)
    coverage_summary: dict[str, Any] = field(default_factory=dict)
    raw_artifact_refs: list[str] = field(default_factory=list)
    parent_run_id: str = ""
    child_run_id: str = ""
    section_attempt_id: str = ""
    runtime_exhaust_bundle_id: str = ""
    microstep_contract_digest: str = ""
    registry_digest: str = ""
    snapshot_digest: str = ""
    source_artifact_manifest: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppOutputSnapshot:
        return cls(
            app_id=str(data.get("app_id", "")),
            scenario_id=str(data.get("scenario_id", "")),
            x3_disposition=str(data.get("x3_disposition", "")),
            output=dict(data.get("output") or {}),
            claims=list(data.get("claims") or []),
            artifacts=list(data.get("artifacts") or []),
            provenance=dict(data.get("provenance") or {}),
            side_effects=dict(data.get("side_effects") or {}),
            deterministic_hash=str(data.get("deterministic_hash", "")),
            run_root=str(data.get("run_root", "")),
            artifact_index=dict(data.get("artifact_index") or {}),
            bundle_indexes=list(data.get("bundle_indexes") or []),
            receipts=list(data.get("receipts") or []),
            lane_rows=list(data.get("lane_rows") or []),
            component_rows=list(data.get("component_rows") or []),
            coverage_summary=dict(data.get("coverage_summary") or {}),
            raw_artifact_refs=list(data.get("raw_artifact_refs") or []),
            parent_run_id=str(data.get("parent_run_id") or ""),
            child_run_id=str(data.get("child_run_id") or ""),
            section_attempt_id=str(data.get("section_attempt_id") or ""),
            runtime_exhaust_bundle_id=str(data.get("runtime_exhaust_bundle_id") or ""),
            microstep_contract_digest=str(data.get("microstep_contract_digest") or ""),
            registry_digest=str(data.get("registry_digest") or ""),
            snapshot_digest=str(data.get("snapshot_digest") or ""),
            source_artifact_manifest=list(data.get("source_artifact_manifest") or []),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraderFinding:
    grader_id: str
    scenario_id: str
    passed: bool
    severity: str
    score: float
    message: str
    failure_mode: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScorecardRow:
    suite_id: str
    scenario_id: str
    app_id: str
    row_id: str
    microstep_id: str
    stage_id: AppsRgStageId | str
    component_id: str
    subcomponent_id: str
    verdict: ScorecardRowVerdict | str
    score: float
    severity: ScorecardRowSeverity | str
    required: bool = True
    run_id: str = ""
    lane_id: str = ""
    gate_id: str = ""
    artifact_role: str = ""
    artifact_ref: str = ""
    evidence_ref: str = ""
    evidence_digest: str = ""
    failure_mode: str = ""
    failure_family: str = ""
    observed_value: Any = None
    threshold: Any = None
    decisive_reason: str = ""
    source_system: str = "apps_eval"
    source_artifact_schema: str = ""
    parent_run_id: str = ""
    child_run_id: str = ""
    section_attempt_id: str = ""
    eval_record_id: str = ""
    runtime_exhaust_bundle_id: str = ""
    microstep_contract_digest: str = ""
    registry_digest: str = ""
    snapshot_digest: str = ""
    created_at: str = ""
    schema_version: str = CURRENT_SCORECARD_ROW_SCHEMA_VERSION

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiagnosticSourceArtifactRef:
    artifact_role: str
    artifact_ref: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if not str(self.artifact_role or "").strip():
            raise ValueError("diagnostic source artifact_role is required")
        if not str(self.artifact_ref or "").strip():
            raise ValueError("diagnostic source artifact_ref is required")
        if not str(self.artifact_digest or "").strip():
            raise ValueError("diagnostic source artifact_digest is required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiagnosticObservationV1:
    diagnostic_id: str
    diagnostic_family: str
    suite_id: str
    scenario_id: str
    app_id: str
    run_id: str
    lane_id: str
    stage_id: AppsRgStageId | str
    depends_on_microstep_id: str
    source_artifact_refs: list[DiagnosticSourceArtifactRef]
    diagnostic_verdict: DiagnosticVerdict | str
    observed_value: Any = None
    threshold: Any = None
    reason: str = ""
    recommended_future_action: str = ""
    evidence_ref: str = ""
    evidence_digest: str = ""
    promotion_state: DiagnosticPromotionState | str = "shadow"
    existing_row_overlap: DiagnosticOverlap | str = "enriches"
    authority: DiagnosticAuthority | str = "post_run_l6_shadow_only"
    schema_version: str = CURRENT_DIAGNOSTIC_OBSERVATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        required_fields = {
            "diagnostic_id": self.diagnostic_id,
            "diagnostic_family": self.diagnostic_family,
            "suite_id": self.suite_id,
            "scenario_id": self.scenario_id,
            "app_id": self.app_id,
            "run_id": self.run_id,
            "stage_id": str(self.stage_id),
            "depends_on_microstep_id": self.depends_on_microstep_id,
        }
        missing = [field for field, value in required_fields.items() if not str(value or "").strip()]
        if missing:
            raise ValueError(f"diagnostic observation missing required field(s): {', '.join(missing)}")
        if not self.source_artifact_refs:
            raise ValueError("diagnostic observation requires at least one source artifact ref")
        for ref in self.source_artifact_refs:
            if not isinstance(ref, DiagnosticSourceArtifactRef):
                raise TypeError("source_artifact_refs must contain DiagnosticSourceArtifactRef values")
        if self.diagnostic_verdict not in {"PASS", "WARN", "FAIL", "NOT_OBSERVED"}:
            raise ValueError(f"unsupported diagnostic_verdict: {self.diagnostic_verdict!r}")
        if self.promotion_state == "blocking":
            raise ValueError("diagnostic observations cannot be blocking in this plan")
        if self.existing_row_overlap == "duplicates":
            raise ValueError("diagnostic observations cannot duplicate existing scorecard rows")
        if self.authority != "post_run_l6_shadow_only":
            raise ValueError("diagnostic authority must be post_run_l6_shadow_only")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_artifact_refs"] = [ref.to_dict() for ref in self.source_artifact_refs]
        return data


@dataclass(frozen=True)
class DiagnosticSummaryV1:
    suite_id: str
    app_id: str
    run_id: str
    observation_count: int
    family_counts: dict[str, int] = field(default_factory=dict)
    stage_counts: dict[str, int] = field(default_factory=dict)
    lane_counts: dict[str, int] = field(default_factory=dict)
    verdict_counts: dict[str, int] = field(default_factory=dict)
    promotion_state_counts: dict[str, int] = field(default_factory=dict)
    authority: DiagnosticAuthority | str = "post_run_l6_shadow_only"
    current_run_mutated: bool = False
    future_run_only: bool = True
    schema_version: str = CURRENT_DIAGNOSTIC_SUMMARY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.authority != "post_run_l6_shadow_only":
            raise ValueError("diagnostic summary authority must be post_run_l6_shadow_only")
        if self.current_run_mutated:
            raise ValueError("diagnostic summary cannot report current-run mutation")
        if not self.future_run_only:
            raise ValueError("diagnostic summary must be future-run-only")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComponentScorecard:
    suite_id: str
    app_id: str
    component_id: str
    row_count: int
    required_count: int
    pass_count: int
    fail_count: int
    warn_count: int
    unknown_count: int
    not_run_count: int
    score: float
    verdict: str
    scenario_id: str = ""
    subcomponent_id: str = ""
    stage_id: str = ""
    lane_id: str = ""
    blocking_failure_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverageSummary:
    suite_id: str
    app_id: str
    required_microsteps: int
    emitted_rows: int
    passed_required: int
    failed_required: int
    missing_required_artifacts: int
    unknown_required: int
    not_run_required: int
    coverage_complete: bool
    release_blocked: bool
    verdict: str
    scenario_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Scorecard:
    suite_id: str
    app_id: str
    scenario_count: int
    finding_count: int
    passed_findings: int
    failed_findings: int
    block_failures: int
    score: float
    verdict: str
    dimension_scores: dict[str, float] = field(default_factory=dict)
    failure_mode_counts: dict[str, int] = field(default_factory=dict)
    failure_family_counts: dict[str, int] = field(default_factory=dict)
    scorecard_rows: list[dict[str, Any]] = field(default_factory=list)
    component_scorecards: list[dict[str, Any]] = field(default_factory=list)
    coverage_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegressionSummary:
    compared: bool
    baseline_path: str = ""
    baseline_digest: str = ""
    current_score: float = 0.0
    baseline_score: float = 0.0
    delta: float = 0.0
    verdict: str = "not_compared"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegressionFlywheelSummary:
    schema_version: str = CURRENT_REGRESSION_FLYWHEEL_SCHEMA_VERSION
    compared: bool = False
    baseline_path: str = ""
    baseline_digest: str = ""
    current_score: float = 0.0
    baseline_score: float = 0.0
    delta: float = 0.0
    verdict: str = "not_compared"
    current_failure_mode_counts: dict[str, int] = field(default_factory=dict)
    current_failure_family_counts: dict[str, int] = field(default_factory=dict)
    baseline_failure_mode_counts: dict[str, int] = field(default_factory=dict)
    baseline_failure_family_counts: dict[str, int] = field(default_factory=dict)
    dominant_failure_mode: str = ""
    dominant_failure_family: str = ""
    new_failure_modes: list[str] = field(default_factory=list)
    recovered_failure_modes: list[str] = field(default_factory=list)
    repeated_failure_modes: list[str] = field(default_factory=list)
    scenario_hotspots: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrendSample:
    record_id: str
    suite_id: str
    app_id: str
    split: str
    created_at: str
    score: float
    scorecard_verdict: str
    regression_verdict: str
    block_failures: int
    dominant_failure_mode: str = ""
    dominant_failure_family: str = ""
    record_seed_digest: str = ""
    record_path: str = ""
    failure_mode_counts: dict[str, int] = field(default_factory=dict)
    failure_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_observation_count: int = 0
    diagnostic_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_verdict_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_not_observed_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrendSuiteSummary:
    suite_id: str
    app_id: str
    split: str
    sample_count: int
    latest_record_id: str = ""
    latest_created_at: str = ""
    latest_score: float = 0.0
    previous_score: float = 0.0
    score_delta: float = 0.0
    latest_scorecard_verdict: str = ""
    latest_regression_verdict: str = ""
    window_pass_rate: float = 0.0
    window_regression_rate: float = 0.0
    trend_direction: str = "stable"
    dominant_failure_mode: str = ""
    dominant_failure_family: str = ""
    failure_mode_counts: dict[str, int] = field(default_factory=dict)
    failure_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_observation_count: int = 0
    diagnostic_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_verdict_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_not_observed_rate: float = 0.0
    score_series: list[float] = field(default_factory=list)
    verdict_series: list[str] = field(default_factory=list)
    regression_series: list[str] = field(default_factory=list)
    record_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrendDashboardSummary:
    schema_version: str = CURRENT_TREND_DASHBOARD_SCHEMA_VERSION
    generated_at: str = ""
    trend_id: str = ""
    trend_dashboard_digest: str = ""
    records_root: str = ""
    app_id: str = ""
    split: str = ""
    window_size: int = 5
    history_limit: int = 20
    sample_count: int = 0
    suite_count: int = 0
    latest_pass_rate: float = 0.0
    latest_regression_rate: float = 0.0
    overall_pass_rate: float = 0.0
    overall_regression_rate: float = 0.0
    latest_record_id: str = ""
    latest_suite_id: str = ""
    latest_created_at: str = ""
    latest_score: float = 0.0
    latest_scorecard_verdict: str = ""
    latest_regression_verdict: str = ""
    latest_trend_direction: str = "stable"
    dominant_failure_mode: str = ""
    dominant_failure_family: str = ""
    failure_mode_counts: dict[str, int] = field(default_factory=dict)
    failure_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_observation_count: int = 0
    diagnostic_family_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_verdict_counts: dict[str, int] = field(default_factory=dict)
    diagnostic_not_observed_rate: float = 0.0
    artifact_paths: dict[str, str] = field(default_factory=dict)
    suite_summaries: list[TrendSuiteSummary] = field(default_factory=list)
    samples: list[TrendSample] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseGateDecision:
    schema_version: str = CURRENT_RELEASE_GATE_SCHEMA_VERSION
    generated_at: str = ""
    gate_id: str = ""
    status: str = "blocked"
    records_root: str = ""
    app_id: str = ""
    split: str = ""
    trend_id: str = ""
    trend_dashboard_path: str = ""
    trend_dashboard_digest: str = ""
    window_size: int = 5
    history_limit: int = 20
    min_samples: int = 2
    min_latest_pass_rate: float = 1.0
    min_window_pass_rate: float = 1.0
    max_latest_score_drop: float = 0.0
    sample_count: int = 0
    suite_count: int = 0
    latest_pass_rate: float = 0.0
    latest_regression_rate: float = 0.0
    overall_pass_rate: float = 0.0
    overall_regression_rate: float = 0.0
    blocking_suite_ids: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    suite_checks: list[dict[str, Any]] = field(default_factory=list)
    artifact_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompletedEvalRecord:
    record_id: str
    created_at: str
    suite_id: str
    app_id: str
    mode: str
    deterministic_only: bool
    scenario_results: list[dict[str, Any]]
    scorecard: Scorecard
    regression: RegressionSummary
    artifact_paths: dict[str, str]
    rubric_ids: list[str]
    record_seed: dict[str, Any] = field(default_factory=dict)
    run_metadata: EvalRunMetadata = field(default_factory=EvalRunMetadata)
    fixture_provenance: list[FixtureProvenance] = field(default_factory=list)
    regression_flywheel: RegressionFlywheelSummary = field(default_factory=RegressionFlywheelSummary)
    parent_run_id: str = ""
    child_run_id: str = ""
    section_attempt_id: str = ""
    eval_record_id: str = ""
    runtime_exhaust_bundle_id: str = ""
    microstep_contract_digest: str = ""
    registry_digest: str = ""
    snapshot_digest: str = ""
    schema_version: str = CURRENT_EVAL_RECORD_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scorecard"] = self.scorecard.to_dict()
        data["regression"] = self.regression.to_dict()
        data["regression_flywheel"] = self.regression_flywheel.to_dict()
        return data


@dataclass(frozen=True)
class L6EvalHandoff:
    record_id: str
    suite_id: str
    app_id: str
    eval_record_path: str
    score: float
    verdict: str
    finding_count: int
    block_failures: int
    current_run_mutated: bool = False
    requested_action: str = "consume_completed_eval_record_only"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
