"""Small data contracts for deterministic evaluation runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ALLOWED_APPS = {"apps_rg", "apps_lic"}
EvalMode = Literal["snapshot", "live_adapter"]


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
        if self.mode not in {"snapshot", "live_adapter"}:
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
class EvalFixture:
    scenario: EvalScenario
    input_dir: str
    expected_dir: str
    snapshot_path: str
    artifacts_dir: str
    expected: dict[str, Any]


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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppOutputSnapshot":
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
    evidence: dict[str, Any] = field(default_factory=dict)

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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegressionSummary:
    compared: bool
    baseline_path: str = ""
    current_score: float = 0.0
    baseline_score: float = 0.0
    delta: float = 0.0
    verdict: str = "not_compared"

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

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scorecard"] = self.scorecard.to_dict()
        data["regression"] = self.regression.to_dict()
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
