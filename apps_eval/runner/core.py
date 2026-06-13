"""Snapshot-first deterministic evaluation runner."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from apps_eval.adapters import run_apps_lic_live, run_apps_rg_live
from apps_eval.contracts import (
    AppOutputSnapshot,
    CompletedEvalRecord,
    EvalFixture,
    EvalRequest,
    EvalScenario,
    L6EvalHandoff,
    RegressionSummary,
    Scorecard,
)
from apps_eval.graders.deterministic import build_default_graders
from apps_eval.outputs.render import render_report, render_record_markdown
from apps_eval.registry import OLD_SUITE_NAMES, load_suite, load_thresholds_registry


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object in {path}")
    return data


def _stable_record_id(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _load_fixture(suite_id: str, suite: dict[str, Any], scenario_id: str) -> EvalFixture:
    scenario_dir = Path(suite["fixture_root"]) / scenario_id
    scenario_path = scenario_dir / "scenario.yaml"
    if not scenario_path.is_file():
        raise FileNotFoundError(f"missing scenario.yaml: {scenario_path}")
    with scenario_path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    scenario = EvalScenario(
        scenario_id=scenario_id,
        suite_id=suite_id,
        app_id=str(suite["app_id"]),
        description=str(raw.get("description", "")),
        fixture_path=str(scenario_dir),
        graders=tuple(raw.get("graders", [])),
        rubric_id=str(suite["rubric_id"]),
        holdout=suite.get("split") == "holdout",
    )
    expected_dir = scenario_dir / "expected"
    return EvalFixture(
        scenario=scenario,
        input_dir=str(scenario_dir / "input"),
        expected_dir=str(expected_dir),
        snapshot_path=str(scenario_dir / "snapshots" / "app_output_snapshot.json"),
        artifacts_dir=str(scenario_dir / "snapshots" / "artifacts"),
        expected=_load_json(expected_dir / "expectations.json"),
    )


def _load_snapshot(fixture: EvalFixture) -> AppOutputSnapshot:
    return AppOutputSnapshot.from_dict(_load_json(Path(fixture.snapshot_path)))


def _run_live(fixture: EvalFixture, run_dir: Path) -> AppOutputSnapshot:
    payload = _load_json(Path(fixture.input_dir) / "request.json")
    artifact_dir = run_dir / "live_adapter_artifacts" / fixture.scenario.scenario_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    if fixture.scenario.app_id == "apps_rg":
        return run_apps_rg_live(fixture.scenario.scenario_id, payload, artifact_dir)
    if fixture.scenario.app_id == "apps_lic":
        return run_apps_lic_live(fixture.scenario.scenario_id, payload, artifact_dir)
    raise ValueError(f"unsupported app: {fixture.scenario.app_id}")


def _score(suite_id: str, app_id: str, scenario_count: int, findings: list[Any]) -> Scorecard:
    finding_count = len(findings)
    passed = sum(1 for finding in findings if finding.passed)
    failed = finding_count - passed
    block_failures = sum(1 for finding in findings if not finding.passed and finding.severity == "block")
    score = 1.0 if finding_count == 0 else passed / finding_count
    thresholds = load_thresholds_registry().get(suite_id, {})
    pass_score = float(thresholds.get("pass_score", 1.0))
    verdict = "pass" if score >= pass_score and block_failures == 0 else "fail"
    dim: dict[str, list[float]] = {}
    for finding in findings:
        dim.setdefault(finding.grader_id, []).append(finding.score)
    dim_scores = {key: sum(vals) / len(vals) for key, vals in sorted(dim.items())}
    return Scorecard(
        suite_id=suite_id,
        app_id=app_id,
        scenario_count=scenario_count,
        finding_count=finding_count,
        passed_findings=passed,
        failed_findings=failed,
        block_failures=block_failures,
        score=round(score, 6),
        verdict=verdict,
        dimension_scores=dim_scores,
    )


def compare_record_to_baseline(record: dict[str, Any], baseline: dict[str, Any]) -> RegressionSummary:
    current = float(record.get("scorecard", {}).get("score", 0.0))
    base = float(baseline.get("scorecard", baseline).get("score", 0.0))
    delta = current - base
    verdict = "regression" if delta < -0.000001 else "pass" if delta >= 0 else "warn"
    return RegressionSummary(
        compared=True,
        current_score=current,
        baseline_score=base,
        delta=round(delta, 6),
        verdict=verdict,
    )


def _emit_artifacts(record: CompletedEvalRecord, findings: list[Any], run_dir: Path, emit_l6_handoff: bool) -> dict[str, str]:
    run_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "eval_record": run_dir / "eval_record.json",
        "scorecard": run_dir / "scorecard.csv",
        "report": run_dir / "report.md",
        "manifest": run_dir / "manifest.json",
        "grader_findings": run_dir / "grader_findings.jsonl",
        "regression": run_dir / "regression.json",
    }
    paths["eval_record"].write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    with paths["scorecard"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dimension", "score"])
        writer.writeheader()
        for key, value in sorted(record.scorecard.dimension_scores.items()):
            writer.writerow({"dimension": key, "score": f"{value:.6f}"})
        writer.writerow({"dimension": "overall", "score": f"{record.scorecard.score:.6f}"})
    paths["report"].write_text(render_report(record, findings), encoding="utf-8")
    manifest = {
        "record_id": record.record_id,
        "suite_id": record.suite_id,
        "app_id": record.app_id,
        "artifacts": {k: str(v).replace("\\", "/") for k, v in paths.items()},
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with paths["grader_findings"].open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding.to_dict(), sort_keys=True) + "\n")
    paths["regression"].write_text(json.dumps(record.regression.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    if emit_l6_handoff:
        handoff = L6EvalHandoff(
            record_id=record.record_id,
            suite_id=record.suite_id,
            app_id=record.app_id,
            eval_record_path=str(paths["eval_record"]).replace("\\", "/"),
            score=record.scorecard.score,
            verdict=record.scorecard.verdict,
            finding_count=record.scorecard.finding_count,
            block_failures=record.scorecard.block_failures,
        )
        handoff_path = run_dir / "l6_handoff.json"
        handoff_path.write_text(json.dumps(handoff.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        paths["l6_handoff"] = handoff_path
    return {k: str(v).replace("\\", "/") for k, v in paths.items()}


def run_eval(request: EvalRequest) -> CompletedEvalRecord:
    if request.suite_id in OLD_SUITE_NAMES:
        raise ValueError(f"old suite name is rejected: {request.suite_id}")
    if request.with_judge:
        raise NotImplementedError("pinned rubric judge is not configured; run deterministic graders only")
    suite = load_suite(request.suite_id)
    if suite.get("app_id") not in {"apps_rg", "apps_lic"}:
        raise ValueError(f"unsupported app: {suite.get('app_id')}")
    if suite.get("split") == "holdout" and os.environ.get("APPS_EVAL_RELEASE_GATE") != "1":
        raise PermissionError("holdout suites require APPS_EVAL_RELEASE_GATE=1")
    fixtures = [_load_fixture(request.suite_id, suite, scenario_id) for scenario_id in suite.get("scenarios", [])]
    if not fixtures:
        raise ValueError(f"suite has no fixtures: {request.suite_id}")
    run_seed = {
        "suite_id": request.suite_id,
        "mode": request.mode,
        "fixtures": [fixture.scenario.scenario_id for fixture in fixtures],
    }
    record_id = _stable_record_id(run_seed)
    run_dir = Path(request.out_dir) / request.suite_id.replace(".", "_") / record_id
    graders = build_default_graders()
    findings = []
    scenario_results = []
    rubric_ids = sorted({fixture.scenario.rubric_id for fixture in fixtures})
    for fixture in fixtures:
        snapshot = _load_snapshot(fixture) if request.mode == "snapshot" else _run_live(fixture, run_dir)
        scenario_findings = [grader.grade(fixture, snapshot) for grader in graders]
        findings.extend(scenario_findings)
        scenario_results.append(
            {
                "scenario_id": fixture.scenario.scenario_id,
                "passed": all(f.passed or f.severity != "block" for f in scenario_findings),
                "findings": [f.to_dict() for f in scenario_findings],
            }
        )
    scorecard = _score(request.suite_id, str(suite["app_id"]), len(fixtures), findings)
    regression = RegressionSummary(compared=False)
    if request.compare_baseline:
        if not request.baseline_path:
            raise ValueError("baseline_path is required when compare_baseline=true")
        baseline = _load_json(Path(request.baseline_path))
        current = {"scorecard": scorecard.to_dict()}
        base_summary = compare_record_to_baseline(current, baseline)
        regression = RegressionSummary(**{**base_summary.to_dict(), "baseline_path": request.baseline_path})
    provisional = CompletedEvalRecord(
        record_id=record_id,
        created_at="1970-01-01T00:00:00Z" if request.deterministic_only else "runtime_generated",
        suite_id=request.suite_id,
        app_id=str(suite["app_id"]),
        mode=request.mode,
        deterministic_only=request.deterministic_only,
        scenario_results=scenario_results,
        scorecard=scorecard,
        regression=regression,
        artifact_paths={},
        rubric_ids=rubric_ids,
    )
    paths = _emit_artifacts(provisional, findings, run_dir, request.emit_l6_handoff)
    record = CompletedEvalRecord(
        **{
            **provisional.to_dict(),
            "artifact_paths": paths,
            "scorecard": scorecard,
            "regression": regression,
        }
    )
    Path(paths["eval_record"]).write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return record


def render_record(record_path: str) -> str:
    return render_record_markdown(_load_json(Path(record_path)))
