"""Snapshot-first deterministic evaluation runner."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any

from apps_eval.adapters import run_apps_lic_live, run_apps_rg_live
from apps_eval.contracts import (
    CURRENT_EVAL_MANIFEST_SCHEMA_VERSION,
    CURRENT_EVAL_RECORD_SCHEMA_VERSION,
    CURRENT_SCORER_VERSION,
    AppOutputSnapshot,
    CompletedEvalRecord,
    EvalFixture,
    EvalRequest,
    EvalScenario,
    EvalRunMetadata,
    FixtureProvenance,
    L6EvalHandoff,
    RegressionSummary,
    RegressionFlywheelSummary,
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


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _stable_record_id(payload: dict[str, Any]) -> str:
    return _canonical_digest(payload)[:16]


def _path_json_digest(path: Path) -> str:
    return _canonical_digest(_load_json(path))


def _project_version() -> str:
    try:
        return package_version("agentic-workflow")
    except PackageNotFoundError:
        return "1.0.0"


def _git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def _run_started_at(deterministic_only: bool) -> str:
    if deterministic_only:
        return "1970-01-01T00:00:00Z"
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _suite_digest(suite: dict[str, Any]) -> str:
    payload = {
        "app_id": suite.get("app_id", ""),
        "split": suite.get("split", ""),
        "task": suite.get("task", ""),
        "rubric_id": suite.get("rubric_id", ""),
        "fixture_root": suite.get("fixture_root", ""),
        "scenarios": list(suite.get("scenarios", [])),
    }
    return _canonical_digest(payload)


def _threshold_digest(thresholds: dict[str, Any]) -> str:
    return _canonical_digest(thresholds)


def _failure_family(failure_mode: str) -> str:
    if not failure_mode:
        return ""
    return failure_mode.split(".", 1)[0]


def _failure_mode_catalog(graders: list[Any]) -> list[dict[str, str]]:
    return [
        {
            "grader_id": grader.grader_id,
            "failure_mode": grader.failure_mode,
            "severity": grader.severity,
        }
        for grader in graders
    ]


def _failure_mode_catalog_digest(graders: list[Any]) -> str:
    return _canonical_digest(_failure_mode_catalog(graders))


def _sorted_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _failure_mode_rollup(findings: list[Any]) -> dict[str, Any]:
    failed = [finding for finding in findings if not finding.passed]
    failure_mode_counts: Counter[str] = Counter()
    block_failure_mode_counts: Counter[str] = Counter()
    warn_failure_mode_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for finding in failed:
        failure_mode = finding.failure_mode or finding.grader_id
        failure_mode_counts[failure_mode] += 1
        family = _failure_family(failure_mode)
        if family:
            family_counts[family] += 1
        if finding.severity == "block":
            block_failure_mode_counts[failure_mode] += 1
        else:
            warn_failure_mode_counts[failure_mode] += 1
    dominant_mode = failure_mode_counts.most_common(1)[0][0] if failure_mode_counts else ""
    dominant_family = family_counts.most_common(1)[0][0] if family_counts else ""
    return {
        "failed_findings": len(failed),
        "failure_mode_counts": _sorted_counter(failure_mode_counts),
        "failure_family_counts": _sorted_counter(family_counts),
        "block_failure_mode_counts": _sorted_counter(block_failure_mode_counts),
        "warn_failure_mode_counts": _sorted_counter(warn_failure_mode_counts),
        "dominant_failure_mode": dominant_mode,
        "dominant_failure_family": dominant_family,
    }


def _scenario_rollup(scenario_id: str, findings: list[Any], snapshot_ref: str, snapshot_digest: str, fixture_provenance_digest: str) -> dict[str, Any]:
    rollup = _failure_mode_rollup(findings)
    block_failures = sum(1 for finding in findings if not finding.passed and finding.severity == "block")
    failed_findings = rollup["failed_findings"]
    return {
        "scenario_id": scenario_id,
        "passed": block_failures == 0,
        "block_failures": block_failures,
        "failed_findings": failed_findings,
        "snapshot_ref": snapshot_ref,
        "snapshot_digest": snapshot_digest,
        "fixture_provenance_digest": fixture_provenance_digest,
        "failure_modes": list(rollup["failure_mode_counts"].keys()),
        "failure_mode_counts": rollup["failure_mode_counts"],
        "failure_family_counts": rollup["failure_family_counts"],
        "block_failure_mode_counts": rollup["block_failure_mode_counts"],
        "warn_failure_mode_counts": rollup["warn_failure_mode_counts"],
        "dominant_failure_mode": rollup["dominant_failure_mode"],
        "dominant_failure_family": rollup["dominant_failure_family"],
        "findings": [finding.to_dict() for finding in findings],
    }


def _regression_flywheel_summary(
    *,
    record: CompletedEvalRecord,
    findings: list[Any],
    baseline_payload: dict[str, Any] | None,
    comparison: RegressionSummary,
    baseline_path: str = "",
) -> RegressionFlywheelSummary:
    rollup = _failure_mode_rollup(findings)
    current_mode_counts = Counter(rollup["failure_mode_counts"])
    current_family_counts = Counter(rollup["failure_family_counts"])
    baseline_mode_counts: Counter[str] = Counter()
    baseline_family_counts: Counter[str] = Counter()
    if baseline_payload:
        baseline_flywheel = baseline_payload.get("regression_flywheel", {})
        baseline_mode_counts.update(baseline_flywheel.get("current_failure_mode_counts", {}))
        baseline_family_counts.update(baseline_flywheel.get("current_failure_family_counts", {}))
        if not baseline_mode_counts and not baseline_family_counts:
            baseline_scorecard = baseline_payload.get("scorecard", {})
            if isinstance(baseline_scorecard, dict):
                baseline_mode_counts.update(baseline_scorecard.get("failure_mode_counts", {}))
                baseline_family_counts.update(baseline_scorecard.get("failure_family_counts", {}))
    current_modes = set(current_mode_counts)
    baseline_modes = set(baseline_mode_counts)
    current_hotspots = sorted(
        (
            {
                "scenario_id": scenario.get("scenario_id", ""),
                "failed_findings": scenario.get("failed_findings", 0),
                "block_failures": scenario.get("block_failures", 0),
                "dominant_failure_mode": scenario.get("dominant_failure_mode", ""),
                "dominant_failure_family": scenario.get("dominant_failure_family", ""),
                "failure_modes": list(scenario.get("failure_modes", [])),
            }
            for scenario in record.scenario_results
            if scenario.get("failed_findings", 0)
        ),
        key=lambda item: (-int(item["failed_findings"]), -int(item["block_failures"]), item["scenario_id"]),
    )
    return RegressionFlywheelSummary(
        compared=comparison.compared,
        baseline_path=baseline_path or comparison.baseline_path,
        baseline_digest=comparison.baseline_digest,
        current_score=comparison.current_score,
        baseline_score=comparison.baseline_score,
        delta=comparison.delta,
        verdict=comparison.verdict,
        current_failure_mode_counts=rollup["failure_mode_counts"],
        current_failure_family_counts=rollup["failure_family_counts"],
        baseline_failure_mode_counts=_sorted_counter(baseline_mode_counts),
        baseline_failure_family_counts=_sorted_counter(baseline_family_counts),
        dominant_failure_mode=rollup["dominant_failure_mode"],
        dominant_failure_family=rollup["dominant_failure_family"],
        new_failure_modes=sorted(current_modes - baseline_modes),
        recovered_failure_modes=sorted(baseline_modes - current_modes),
        repeated_failure_modes=sorted(mode for mode, count in current_mode_counts.items() if count > 1),
        scenario_hotspots=current_hotspots[:10],
    )


def _load_fixture(suite_id: str, suite: dict[str, Any], scenario_id: str) -> EvalFixture:
    scenario_dir = Path(suite["fixture_root"]) / scenario_id
    scenario_path = scenario_dir / "scenario.yaml"
    input_path = scenario_dir / "input" / "request.json"
    expected_path = scenario_dir / "expected" / "expectations.json"
    snapshot_path = scenario_dir / "snapshots" / "app_output_snapshot.json"
    if not scenario_path.is_file():
        raise FileNotFoundError(f"missing scenario.yaml: {scenario_path}")
    if not input_path.is_file():
        raise FileNotFoundError(f"missing request.json: {input_path}")
    if not expected_path.is_file():
        raise FileNotFoundError(f"missing expectations.json: {expected_path}")
    if not snapshot_path.is_file():
        raise FileNotFoundError(f"missing app_output_snapshot.json: {snapshot_path}")
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
    provenance = FixtureProvenance(
        scenario_id=scenario_id,
        fixture_path=scenario_dir.as_posix(),
        scenario_definition_digest=_canonical_digest(
            {
                "scenario": raw,
                "scenario_id": scenario_id,
                "suite_id": suite_id,
                "app_id": suite["app_id"],
                "rubric_id": suite["rubric_id"],
                "holdout": suite.get("split") == "holdout",
            }
        ),
        input_request_digest=_path_json_digest(input_path),
        expected_digest=_path_json_digest(expected_path),
        snapshot_digest=_path_json_digest(snapshot_path),
    )
    return EvalFixture(
        scenario=scenario,
        input_dir=str(scenario_dir / "input"),
        expected_dir=str(scenario_dir / "expected"),
        snapshot_path=str(snapshot_path),
        artifacts_dir=str(scenario_dir / "snapshots" / "artifacts"),
        expected=_load_json(expected_path),
        provenance=provenance,
    )


def _load_snapshot(fixture: EvalFixture) -> AppOutputSnapshot:
    return AppOutputSnapshot.from_dict(_load_json(Path(fixture.snapshot_path)))


def _run_live(fixture: EvalFixture, run_dir: Path) -> AppOutputSnapshot:
    payload = _load_json(Path(fixture.input_dir) / "request.json")
    scenario_key = hashlib.sha256(fixture.scenario.scenario_id.encode("utf-8")).hexdigest()[:8]
    artifact_dir = run_dir / "la" / scenario_key
    if fixture.scenario.app_id == "apps_rg":
        snapshot = run_apps_rg_live(fixture.scenario.scenario_id, payload, artifact_dir)
    elif fixture.scenario.app_id == "apps_lic":
        snapshot = run_apps_lic_live(fixture.scenario.scenario_id, payload, artifact_dir)
    else:
        raise ValueError(f"unsupported app: {fixture.scenario.app_id}")
    snapshot_dir = run_dir / "live_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / f"{scenario_key}.json").write_text(
        json.dumps(snapshot.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return snapshot


def _score(
    suite_id: str,
    app_id: str,
    scenario_count: int,
    findings: list[Any],
    *,
    thresholds: dict[str, Any],
) -> Scorecard:
    finding_count = len(findings)
    passed = sum(1 for finding in findings if finding.passed)
    failed = finding_count - passed
    block_failures = sum(1 for finding in findings if not finding.passed and finding.severity == "block")
    score = 1.0 if finding_count == 0 else passed / finding_count
    pass_score = float(thresholds.get("pass_score", 1.0))
    verdict = "pass" if score >= pass_score and block_failures == 0 else "fail"
    rollup = _failure_mode_rollup(findings)
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
        failure_mode_counts=rollup["failure_mode_counts"],
        failure_family_counts=rollup["failure_family_counts"],
    )


def compare_record_to_baseline(record: dict[str, Any], baseline: dict[str, Any]) -> RegressionSummary:
    current = float(record.get("scorecard", {}).get("score", 0.0))
    base = float(baseline.get("scorecard", baseline).get("score", 0.0))
    delta = current - base
    verdict = "regression" if delta < -0.000001 else "pass" if delta >= 0 else "warn"
    return RegressionSummary(
        compared=True,
        baseline_digest=_canonical_digest(baseline),
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
        "regression_flywheel": run_dir / "regression_flywheel.json",
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
        "schema_version": CURRENT_EVAL_MANIFEST_SCHEMA_VERSION,
        "record_id": record.record_id,
        "record_schema_version": record.schema_version,
        "suite_id": record.suite_id,
        "app_id": record.app_id,
        "record_seed": record.record_seed,
        "run_metadata": record.run_metadata.to_dict(),
        "fixture_provenance": [provenance.to_dict() for provenance in record.fixture_provenance],
        "regression_flywheel": record.regression_flywheel.to_dict(),
        "artifacts": {k: str(v).replace("\\", "/") for k, v in paths.items()},
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with paths["grader_findings"].open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding.to_dict(), sort_keys=True) + "\n")
    paths["regression"].write_text(json.dumps(record.regression.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    paths["regression_flywheel"].write_text(json.dumps(record.regression_flywheel.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    live_snapshots = run_dir / "live_snapshots"
    if live_snapshots.is_dir():
        paths["live_snapshots"] = live_snapshots
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
    l6_handoff_required = (
        request.mode == "live_adapter"
        or suite.get("split") == "holdout"
        or os.environ.get("APPS_EVAL_RELEASE_GATE") == "1"
    )
    if l6_handoff_required and not request.emit_l6_handoff:
        raise PermissionError(
            "apps_eval L6 shadow handoff is required for live_adapter, holdout, and release-gate runs"
        )
    if suite.get("split") == "holdout" and os.environ.get("APPS_EVAL_RELEASE_GATE") != "1":
        raise PermissionError("holdout suites require APPS_EVAL_RELEASE_GATE=1")
    fixtures = [_load_fixture(request.suite_id, suite, scenario_id) for scenario_id in suite.get("scenarios", [])]
    if not fixtures:
        raise ValueError(f"suite has no fixtures: {request.suite_id}")
    graders = build_default_graders()
    thresholds = load_thresholds_registry().get(request.suite_id, {})
    created_at = _run_started_at(request.deterministic_only)
    git_commit = _git_commit(Path(__file__).resolve().parents[2])
    suite_digest = _suite_digest(suite)
    threshold_digest = _threshold_digest(thresholds)
    failure_mode_catalog_digest = _failure_mode_catalog_digest(graders)
    fixture_provenance = [fixture.provenance for fixture in fixtures]
    baseline_digest = ""
    baseline_payload: dict[str, Any] | None = None
    if request.compare_baseline:
        if not request.baseline_path:
            raise ValueError("baseline_path is required when compare_baseline=true")
        baseline_payload = _load_json(Path(request.baseline_path))
        if baseline_payload.get("schema_version") != CURRENT_EVAL_RECORD_SCHEMA_VERSION:
            raise ValueError(
                f"baseline schema_version mismatch for {request.baseline_path}: "
                f"expected {CURRENT_EVAL_RECORD_SCHEMA_VERSION!r}, found {baseline_payload.get('schema_version')!r}"
            )
        if "record_id" not in baseline_payload or "scorecard" not in baseline_payload:
            raise ValueError(f"baseline missing required eval record fields: {request.baseline_path}")
        baseline_digest = _canonical_digest(baseline_payload)
    record_seed = {
        "schema_version": CURRENT_EVAL_RECORD_SCHEMA_VERSION,
        "suite_id": request.suite_id,
        "app_id": suite["app_id"],
        "mode": request.mode,
        "deterministic_only": request.deterministic_only,
        "with_judge": request.with_judge,
        "compare_baseline": request.compare_baseline,
        "baseline_digest": baseline_digest,
        "emit_l6_handoff": request.emit_l6_handoff,
        "git_commit": git_commit,
        "suite_digest": suite_digest,
        "threshold_digest": threshold_digest,
        "failure_mode_catalog_digest": failure_mode_catalog_digest,
        "grader_ids": [grader.grader_id for grader in graders],
        "scorer_version": CURRENT_SCORER_VERSION,
        "fixture_provenance": [provenance.to_dict() for provenance in fixture_provenance],
    }
    if not request.deterministic_only:
        record_seed["created_at"] = created_at
    record_id = _stable_record_id(record_seed)
    run_dir = Path(request.out_dir) / request.suite_id.replace(".", "_") / record_id
    findings = []
    scenario_results = []
    rubric_ids = sorted({fixture.scenario.rubric_id for fixture in fixtures})
    for fixture in fixtures:
        snapshot = _load_snapshot(fixture) if request.mode == "snapshot" else _run_live(fixture, run_dir)
        snapshot_payload = snapshot.to_dict()
        scenario_findings = [grader.grade(fixture, snapshot) for grader in graders]
        findings.extend(scenario_findings)
        scenario_results.append(
            _scenario_rollup(
                fixture.scenario.scenario_id,
                scenario_findings,
                fixture.snapshot_path if request.mode == "snapshot" else str((run_dir / "live_snapshots" / f"{hashlib.sha256(fixture.scenario.scenario_id.encode('utf-8')).hexdigest()[:8]}.json").as_posix()),
                _canonical_digest(snapshot_payload),
                _canonical_digest(fixture.provenance.to_dict()),
            )
        )
    scorecard = _score(request.suite_id, str(suite["app_id"]), len(fixtures), findings, thresholds=thresholds)
    regression = RegressionSummary(compared=False)
    if request.compare_baseline:
        current = {"scorecard": scorecard.to_dict()}
        base_summary = compare_record_to_baseline(current, baseline_payload or {})
        regression = RegressionSummary(
            **{
                **base_summary.to_dict(),
                "baseline_path": request.baseline_path,
            }
        )
    provisional = CompletedEvalRecord(
        record_id=record_id,
        created_at=created_at,
        suite_id=request.suite_id,
        app_id=str(suite["app_id"]),
        mode=request.mode,
        deterministic_only=request.deterministic_only,
        scenario_results=scenario_results,
        scorecard=scorecard,
        regression=regression,
        artifact_paths={},
        rubric_ids=rubric_ids,
        record_seed=record_seed,
        run_metadata=EvalRunMetadata(
            project_version=_project_version(),
            git_commit=git_commit,
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            cwd=Path.cwd().resolve().as_posix(),
            scorer_version=CURRENT_SCORER_VERSION,
            record_seed_digest=_canonical_digest(record_seed),
            baseline_digest=baseline_digest,
            mode=request.mode,
            deterministic_only=request.deterministic_only,
            with_judge=request.with_judge,
            compare_baseline=request.compare_baseline,
        ),
        fixture_provenance=fixture_provenance,
    )
    flywheel = _regression_flywheel_summary(
        record=provisional,
        findings=findings,
        baseline_payload=baseline_payload,
        comparison=regression,
        baseline_path=request.baseline_path if request.compare_baseline else "",
    )
    record = replace(provisional, regression_flywheel=flywheel)
    paths = _emit_artifacts(record, findings, run_dir, request.emit_l6_handoff)
    record = replace(record, artifact_paths=paths)
    Path(paths["eval_record"]).write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    Path(paths["report"]).write_text(render_report(record, findings), encoding="utf-8")
    if request.emit_l6_handoff:
        from apps_eval.l6_shadow_bridge import emit_completed_eval_l6_shadow_bridge

        bridge_paths = emit_completed_eval_l6_shadow_bridge(
            record,
            run_dir,
            eval_record_path=paths["eval_record"],
            l6_handoff_path=paths.get("l6_handoff", ""),
        )
        paths.update(bridge_paths)
        record = replace(record, artifact_paths=paths)
        Path(paths["eval_record"]).write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        Path(paths["report"]).write_text(render_report(record, findings), encoding="utf-8")
    return record


def render_record(record_path: str) -> str:
    return render_record_markdown(_load_json(Path(record_path)))
