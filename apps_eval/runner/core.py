"""Snapshot-first deterministic evaluation runner."""

from __future__ import annotations

import csv
import hashlib
import io
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

from agentic_core.L2_execution.utils import write_gateway as _wg

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
    ScorecardRow,
)
from apps_eval.coverage import apps_rg_contract_digest, build_apps_rg_microstep_evaluation
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


def _is_block_severity(severity: str) -> bool:
    return str(severity or "").lower() == "block"


def _passed(item: Any) -> bool:
    value = getattr(item, "passed", None)
    if isinstance(value, bool):
        return value
    verdict = str(getattr(item, "verdict", "") or "").upper()
    return verdict in {"PASS", "NOT_APPLICABLE"}


def _item_failure_mode(item: Any) -> str:
    return str(getattr(item, "failure_mode", "") or getattr(item, "grader_id", "") or getattr(item, "microstep_id", ""))


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
    failed = [finding for finding in findings if not _passed(finding)]
    failure_mode_counts: Counter[str] = Counter()
    block_failure_mode_counts: Counter[str] = Counter()
    warn_failure_mode_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for finding in failed:
        failure_mode = _item_failure_mode(finding)
        failure_mode_counts[failure_mode] += 1
        family = _failure_family(failure_mode)
        if family:
            family_counts[family] += 1
        if _is_block_severity(getattr(finding, "severity", "")):
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
    _wg.ensure_dir(snapshot_dir)
    _wg.write_text(
        snapshot_dir / f"{scenario_key}.json",
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
    scorecard_rows: list[ScorecardRow] | None = None,
    component_scorecards: list[dict[str, Any]] | None = None,
    coverage_summary: dict[str, Any] | None = None,
) -> Scorecard:
    rows = scorecard_rows or []
    required_rows = [row for row in rows if row.required]
    finding_count = len(findings)
    passed = sum(1 for finding in findings if finding.passed)
    failed = finding_count - passed
    row_passed = sum(1 for row in required_rows if row.verdict in {"PASS", "NOT_APPLICABLE"})
    row_failed = len(required_rows) - row_passed
    block_failures = sum(1 for finding in findings if not finding.passed and _is_block_severity(finding.severity))
    block_failures += sum(1 for row in required_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"} and _is_block_severity(str(row.severity)))
    total_scored = finding_count + len(required_rows)
    score = 1.0 if total_scored == 0 else (passed + row_passed) / total_scored
    pass_score = float(thresholds.get("pass_score", 1.0))
    coverage_blocks = bool((coverage_summary or {}).get("release_blocked"))
    verdict = "pass" if score >= pass_score and block_failures == 0 and not coverage_blocks else "fail"
    rollup = _failure_mode_rollup([*findings, *required_rows])
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
        failed_findings=failed + row_failed,
        block_failures=block_failures,
        score=round(score, 6),
        verdict=verdict,
        dimension_scores=dim_scores,
        failure_mode_counts=rollup["failure_mode_counts"],
        failure_family_counts=rollup["failure_family_counts"],
        scorecard_rows=[row.to_dict() for row in rows],
        component_scorecards=component_scorecards or [],
        coverage_summary=coverage_summary or {},
    )


def _planned_eval_artifacts(run_dir: Path) -> dict[str, Any]:
    return {
        "eval_record": (run_dir / "eval_record.json").as_posix(),
        "scorecard_rows": (run_dir / "scorecard_rows.jsonl").as_posix(),
        "component_scorecards": [
            (run_dir / "component_scorecards.csv").as_posix(),
            (run_dir / "apps_rg_component_scorecard.json").as_posix(),
        ],
        "coverage_matrix": (run_dir / "coverage_matrix.csv").as_posix(),
        "regression_summary": [
            (run_dir / "regression.json").as_posix(),
            (run_dir / "regression_flywheel.json").as_posix(),
        ],
    }


def _snapshot_deterministic_hash(snapshot: AppOutputSnapshot) -> str:
    data = snapshot.to_dict()
    data.pop("deterministic_hash", None)
    return _canonical_digest(data)


def _default_current_run_expected(snapshot: AppOutputSnapshot) -> dict[str, Any]:
    sections = snapshot.output.get("sections")
    required_sections = ["executive_summary", "experience", "skills"]
    if isinstance(sections, dict):
        required_sections = [name for name in required_sections if name in sections]
    return {
        "required_output_keys": ["runtime", "sections"],
        "required_artifacts": ["generated_resume.json", "resume.md"],
        "expected_x3": snapshot.x3_disposition,
        "forbidden_terms": [],
        "grounded_claims_required": True,
        "required_provenance": [],
        "required_sections": required_sections,
        "length_bounds": {"min_words": 50, "max_words": 5000},
        "allow_side_effects": False,
        "escalation_required": False,
    }


def run_current_snapshot_eval(
    snapshot: AppOutputSnapshot,
    *,
    suite_id: str = "apps_rg.current.resume_generation",
    out_dir: str = "artifacts/apps_eval/runs",
    deterministic_only: bool = True,
    emit_l6_handoff: bool = True,
    expected: dict[str, Any] | None = None,
    threshold_suite_id: str = "apps_rg.dev.resume_generation",
) -> CompletedEvalRecord:
    """Evaluate one already-produced app snapshot.

    This is the current-run counterpart to fixture-suite evaluation: apps_rg can
    hand apps_eval the exact generated artifact after UWG promotion and receive
    the same deterministic grader, microstep coverage, and L6 bridge artifacts.
    """
    if snapshot.app_id != "apps_rg":
        raise ValueError(f"current snapshot eval supports apps_rg only, got {snapshot.app_id!r}")
    if not emit_l6_handoff:
        raise PermissionError("apps_rg current-run eval requires L6 shadow handoff")

    scenario_id = snapshot.scenario_id or "apps_rg_current_run"
    stable_snapshot = replace(
        snapshot,
        deterministic_hash=_snapshot_deterministic_hash(snapshot),
    )
    expected_payload = dict(expected or _default_current_run_expected(stable_snapshot))
    created_at = _run_started_at(deterministic_only)
    repo_root = Path(__file__).resolve().parents[2]
    git_commit = _git_commit(repo_root)
    graders = build_default_graders()
    thresholds = load_thresholds_registry().get(
        threshold_suite_id,
        load_thresholds_registry().get("apps_rg.dev.resume_generation", {}),
    )
    fixture_path = stable_snapshot.run_root or ""
    fixture = EvalFixture(
        scenario=EvalScenario(
            scenario_id=scenario_id,
            suite_id=suite_id,
            app_id=stable_snapshot.app_id,
            description="current apps_rg run artifact evaluation",
            fixture_path=fixture_path,
            graders=tuple(grader.grader_id for grader in graders),
            rubric_id="apps_rg_resume_generation_v1",
            holdout=False,
        ),
        input_dir=fixture_path,
        expected_dir=fixture_path,
        snapshot_path="",
        artifacts_dir=fixture_path,
        expected=expected_payload,
        provenance=FixtureProvenance(
            scenario_id=scenario_id,
            fixture_path=fixture_path,
            scenario_definition_digest=_canonical_digest(
                {
                    "scenario_id": scenario_id,
                    "suite_id": suite_id,
                    "app_id": stable_snapshot.app_id,
                    "rubric_id": "apps_rg_resume_generation_v1",
                    "current_run": True,
                }
            ),
            input_request_digest=_canonical_digest(stable_snapshot.provenance.get("resolved_inputs", {})),
            expected_digest=_canonical_digest(expected_payload),
            snapshot_digest=_canonical_digest(stable_snapshot.to_dict()),
        ),
    )

    suite_digest = _canonical_digest(
        {
            "app_id": stable_snapshot.app_id,
            "split": "current",
            "task": "resume_generation",
            "rubric_id": "apps_rg_resume_generation_v1",
            "fixture_root": fixture_path,
            "scenarios": [scenario_id],
        }
    )
    threshold_digest = _threshold_digest(thresholds)
    failure_mode_catalog_digest = _failure_mode_catalog_digest(graders)
    app_microstep_contract_digest = apps_rg_contract_digest()
    record_seed = {
        "schema_version": CURRENT_EVAL_RECORD_SCHEMA_VERSION,
        "suite_id": suite_id,
        "app_id": stable_snapshot.app_id,
        "mode": "current_snapshot",
        "deterministic_only": deterministic_only,
        "with_judge": False,
        "compare_baseline": False,
        "baseline_digest": "",
        "emit_l6_handoff": emit_l6_handoff,
        "git_commit": git_commit,
        "suite_digest": suite_digest,
        "threshold_digest": threshold_digest,
        "failure_mode_catalog_digest": failure_mode_catalog_digest,
        "apps_rg_microstep_contract_digest": app_microstep_contract_digest,
        "grader_ids": [grader.grader_id for grader in graders],
        "scorer_version": CURRENT_SCORER_VERSION,
        "fixture_provenance": [fixture.provenance.to_dict()],
        "current_run_snapshot_digest": fixture.provenance.snapshot_digest,
        "source_run_root": stable_snapshot.run_root,
    }
    if not deterministic_only:
        record_seed["created_at"] = created_at

    record_id = _stable_record_id(record_seed)
    run_dir = Path(out_dir) / suite_id.replace(".", "_") / record_id
    planned_eval_artifacts = _planned_eval_artifacts(run_dir)

    findings = [grader.grade(fixture, stable_snapshot) for grader in graders]
    microstep_eval = build_apps_rg_microstep_evaluation(
        suite_id=suite_id,
        scenario_id=scenario_id,
        snapshot=stable_snapshot,
        run_id=record_id,
        created_at=created_at,
        planned_eval_artifacts=planned_eval_artifacts,
    )
    rows = list(microstep_eval["rows"])
    components = [component.to_dict() for component in microstep_eval["component_scorecards"]]
    coverage = microstep_eval["coverage_summary"].to_dict()
    scenario_result = _scenario_rollup(
        scenario_id,
        findings,
        stable_snapshot.run_root,
        fixture.provenance.snapshot_digest,
        _canonical_digest(fixture.provenance.to_dict()),
    )
    scenario_result["apps_rg_coverage_summary"] = coverage
    suite_coverage = _apps_rg_suite_coverage(
        suite_id=suite_id,
        app_id=stable_snapshot.app_id,
        rows=rows,
        scenario_summaries=[coverage],
    )
    scorecard = _score(
        suite_id,
        stable_snapshot.app_id,
        1,
        findings,
        thresholds=thresholds,
        scorecard_rows=rows,
        component_scorecards=components,
        coverage_summary=suite_coverage,
    )
    regression = RegressionSummary(compared=False)
    provisional = CompletedEvalRecord(
        record_id=record_id,
        created_at=created_at,
        suite_id=suite_id,
        app_id=stable_snapshot.app_id,
        mode="current_snapshot",
        deterministic_only=deterministic_only,
        scenario_results=[scenario_result],
        scorecard=scorecard,
        regression=regression,
        artifact_paths={},
        rubric_ids=["apps_rg_resume_generation_v1"],
        record_seed=record_seed,
        run_metadata=EvalRunMetadata(
            project_version=_project_version(),
            git_commit=git_commit,
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            cwd=Path.cwd().resolve().as_posix(),
            scorer_version=CURRENT_SCORER_VERSION,
            record_seed_digest=_canonical_digest(record_seed),
            baseline_digest="",
            mode="current_snapshot",
            deterministic_only=deterministic_only,
            with_judge=False,
            compare_baseline=False,
        ),
        fixture_provenance=[fixture.provenance],
    )
    flywheel = _regression_flywheel_summary(
        record=provisional,
        findings=findings,
        baseline_payload=None,
        comparison=regression,
    )
    record = replace(provisional, regression_flywheel=flywheel)
    paths = _emit_artifacts(record, findings, run_dir, emit_l6_handoff)
    record = replace(record, artifact_paths=paths)
    _wg.write_text(Path(paths["eval_record"]), json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    _wg.write_text(Path(paths["report"]), render_report(record, findings), encoding="utf-8")
    if emit_l6_handoff:
        from apps_eval.l6_shadow_bridge import emit_completed_eval_l6_shadow_bridge

        bridge_paths = emit_completed_eval_l6_shadow_bridge(
            record,
            run_dir,
            eval_record_path=paths["eval_record"],
            l6_handoff_path=paths.get("l6_handoff", ""),
        )
        paths.update(bridge_paths)
        record = replace(record, artifact_paths=paths)
        _wg.write_text(Path(paths["eval_record"]), json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        _wg.write_text(Path(paths["report"]), render_report(record, findings), encoding="utf-8")
    return record


def _apps_rg_suite_coverage(
    *,
    suite_id: str,
    app_id: str,
    rows: list[ScorecardRow],
    scenario_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    required = [row for row in rows if row.required]
    missing = sum(1 for row in required if row.failure_mode == "coverage.missing_required_artifact")
    unknown = sum(1 for row in required if row.verdict == "UNKNOWN")
    not_run = sum(1 for row in required if row.verdict == "NOT_RUN")
    failed = sum(1 for row in required if row.verdict == "FAIL")
    passed = sum(1 for row in required if row.verdict == "PASS")
    release_blocked = any(row.verdict in {"FAIL", "UNKNOWN", "NOT_RUN"} for row in required)
    coverage_complete = missing == 0 and unknown == 0 and not_run == 0
    return {
        "schema_version": "apps_eval.apps_rg_coverage_summary.v1",
        "suite_id": suite_id,
        "app_id": app_id,
        "required_microsteps": len(required),
        "emitted_rows": len(rows),
        "passed_required": passed,
        "failed_required": failed,
        "missing_required_artifacts": missing,
        "unknown_required": unknown,
        "not_run_required": not_run,
        "coverage_complete": coverage_complete,
        "release_blocked": release_blocked,
        "verdict": "fail" if release_blocked or not coverage_complete else "pass",
        "scenario_summaries": scenario_summaries,
    }


def _csv_cell(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    if value is None:
        return ""
    return str(value)


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
    _wg.ensure_dir(run_dir)
    paths = {
        "eval_record": run_dir / "eval_record.json",
        "scorecard": run_dir / "scorecard.csv",
        "report": run_dir / "report.md",
        "manifest": run_dir / "manifest.json",
        "grader_findings": run_dir / "grader_findings.jsonl",
        "regression": run_dir / "regression.json",
        "regression_flywheel": run_dir / "regression_flywheel.json",
    }
    if record.app_id == "apps_rg":
        paths.update(
            {
                "scorecard_rows": run_dir / "scorecard_rows.jsonl",
                "component_scorecards": run_dir / "component_scorecards.csv",
                "apps_rg_component_scorecard": run_dir / "apps_rg_component_scorecard.json",
                "coverage_matrix": run_dir / "coverage_matrix.csv",
                "missing_required_components": run_dir / "missing_required_components.csv",
                "evidence_index": run_dir / "evidence_index.csv",
                "apps_rg_l6_eval_handoff": run_dir / "apps_rg_l6_eval_handoff.json",
            }
        )
    _wg.write_text(paths["eval_record"], json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    scorecard_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(scorecard_buffer, fieldnames=["dimension", "score"])
    writer.writeheader()
    for key, value in sorted(record.scorecard.dimension_scores.items()):
        writer.writerow({"dimension": key, "score": f"{value:.6f}"})
    writer.writerow({"dimension": "overall", "score": f"{record.scorecard.score:.6f}"})
    _wg.write_text(paths["scorecard"], scorecard_buffer.getvalue(), encoding="utf-8")
    if record.app_id == "apps_rg":
        row_dicts = list(record.scorecard.scorecard_rows)
        component_dicts = list(record.scorecard.component_scorecards)
        coverage_summary = dict(record.scorecard.coverage_summary)
        _wg.write_text(
            paths["scorecard_rows"],
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in row_dicts),
            encoding="utf-8",
        )
        component_fields = [
            "suite_id",
            "app_id",
            "scenario_id",
            "component_id",
            "subcomponent_id",
            "stage_id",
            "lane_id",
            "row_count",
            "required_count",
            "pass_count",
            "fail_count",
            "warn_count",
            "unknown_count",
            "not_run_count",
            "blocking_failure_count",
            "score",
            "verdict",
        ]
        component_buffer = io.StringIO(newline="")
        component_writer = csv.DictWriter(component_buffer, fieldnames=component_fields)
        component_writer.writeheader()
        for row in component_dicts:
            component_writer.writerow({field: _csv_cell(row.get(field)) for field in component_fields})
        _wg.write_text(paths["component_scorecards"], component_buffer.getvalue(), encoding="utf-8")
        component_payload = {
            "schema_version": "apps_eval.apps_rg_component_scorecard.v1",
            "suite_id": record.suite_id,
            "app_id": record.app_id,
            "record_id": record.record_id,
            "coverage_summary": coverage_summary,
            "component_scorecards": component_dicts,
            "row_count": len(row_dicts),
        }
        _wg.write_text(
            paths["apps_rg_component_scorecard"],
            json.dumps(component_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        coverage_fields = [
            "row_id",
            "suite_id",
            "scenario_id",
            "component_id",
            "subcomponent_id",
            "stage_id",
            "lane_id",
            "microstep_id",
            "gate_id",
            "artifact_role",
            "artifact_ref",
            "verdict",
            "score",
            "severity",
            "failure_mode",
            "decisive_reason",
            "evidence_digest",
        ]
        coverage_buffer = io.StringIO(newline="")
        coverage_writer = csv.DictWriter(coverage_buffer, fieldnames=coverage_fields)
        coverage_writer.writeheader()
        for row in row_dicts:
            coverage_writer.writerow({field: _csv_cell(row.get(field)) for field in coverage_fields})
        _wg.write_text(paths["coverage_matrix"], coverage_buffer.getvalue(), encoding="utf-8")
        missing_buffer = io.StringIO(newline="")
        missing_writer = csv.DictWriter(missing_buffer, fieldnames=coverage_fields)
        missing_writer.writeheader()
        for row in row_dicts:
            if row.get("required") and row.get("verdict") in {"FAIL", "UNKNOWN", "NOT_RUN"}:
                missing_writer.writerow({field: _csv_cell(row.get(field)) for field in coverage_fields})
        _wg.write_text(paths["missing_required_components"], missing_buffer.getvalue(), encoding="utf-8")
        evidence_fields = [
            "row_id",
            "microstep_id",
            "lane_id",
            "artifact_role",
            "artifact_ref",
            "evidence_ref",
            "evidence_digest",
            "verdict",
        ]
        evidence_buffer = io.StringIO(newline="")
        evidence_writer = csv.DictWriter(evidence_buffer, fieldnames=evidence_fields)
        evidence_writer.writeheader()
        for row in row_dicts:
            evidence_writer.writerow({field: _csv_cell(row.get(field)) for field in evidence_fields})
        _wg.write_text(paths["evidence_index"], evidence_buffer.getvalue(), encoding="utf-8")
        rg_handoff = {
            "schema_version": "apps_eval.apps_rg_l6_eval_handoff.v1",
            "record_id": record.record_id,
            "suite_id": record.suite_id,
            "app_id": record.app_id,
            "requested_action": "consume_completed_eval_artifacts_only",
            "current_run_mutated": False,
            "future_run_only": True,
            "coverage_summary": coverage_summary,
            "artifact_paths": {
                "eval_record": str(paths["eval_record"]).replace("\\", "/"),
                "scorecard_rows": str(paths["scorecard_rows"]).replace("\\", "/"),
                "component_scorecard": str(paths["apps_rg_component_scorecard"]).replace("\\", "/"),
                "coverage_matrix": str(paths["coverage_matrix"]).replace("\\", "/"),
                "missing_required_components": str(paths["missing_required_components"]).replace("\\", "/"),
            },
        }
        _wg.write_text(
            paths["apps_rg_l6_eval_handoff"],
            json.dumps(rg_handoff, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    _wg.write_text(paths["report"], render_report(record, findings), encoding="utf-8")
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
    _wg.write_text(paths["manifest"], json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    grader_findings_jsonl = "".join(json.dumps(finding.to_dict(), sort_keys=True) + "\n" for finding in findings)
    _wg.write_text(paths["grader_findings"], grader_findings_jsonl, encoding="utf-8")
    _wg.write_text(paths["regression"], json.dumps(record.regression.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    _wg.write_text(
        paths["regression_flywheel"],
        json.dumps(record.regression_flywheel.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
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
        _wg.write_text(handoff_path, json.dumps(handoff.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
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
    app_microstep_contract_digest = apps_rg_contract_digest() if suite.get("app_id") == "apps_rg" else ""
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
        "apps_rg_microstep_contract_digest": app_microstep_contract_digest,
        "grader_ids": [grader.grader_id for grader in graders],
        "scorer_version": CURRENT_SCORER_VERSION,
        "fixture_provenance": [provenance.to_dict() for provenance in fixture_provenance],
    }
    if not request.deterministic_only:
        record_seed["created_at"] = created_at
    record_id = _stable_record_id(record_seed)
    run_dir = Path(request.out_dir) / request.suite_id.replace(".", "_") / record_id
    findings = []
    apps_rg_scorecard_rows: list[ScorecardRow] = []
    apps_rg_component_scorecards: list[dict[str, Any]] = []
    apps_rg_scenario_coverages: list[dict[str, Any]] = []
    scenario_results = []
    rubric_ids = sorted({fixture.scenario.rubric_id for fixture in fixtures})
    planned_eval_artifacts = _planned_eval_artifacts(run_dir) if suite.get("app_id") == "apps_rg" else {}
    for fixture in fixtures:
        snapshot = _load_snapshot(fixture) if request.mode == "snapshot" else _run_live(fixture, run_dir)
        snapshot_payload = snapshot.to_dict()
        scenario_findings = [grader.grade(fixture, snapshot) for grader in graders]
        findings.extend(scenario_findings)
        scenario_result = _scenario_rollup(
            fixture.scenario.scenario_id,
            scenario_findings,
            fixture.snapshot_path if request.mode == "snapshot" else str((run_dir / "live_snapshots" / f"{hashlib.sha256(fixture.scenario.scenario_id.encode('utf-8')).hexdigest()[:8]}.json").as_posix()),
            _canonical_digest(snapshot_payload),
            _canonical_digest(fixture.provenance.to_dict()),
        )
        if suite.get("app_id") == "apps_rg":
            microstep_eval = build_apps_rg_microstep_evaluation(
                suite_id=request.suite_id,
                scenario_id=fixture.scenario.scenario_id,
                snapshot=snapshot,
                run_id=record_id,
                created_at=created_at,
                planned_eval_artifacts=planned_eval_artifacts,
            )
            rows = list(microstep_eval["rows"])
            components = [component.to_dict() for component in microstep_eval["component_scorecards"]]
            coverage = microstep_eval["coverage_summary"].to_dict()
            apps_rg_scorecard_rows.extend(rows)
            apps_rg_component_scorecards.extend(components)
            apps_rg_scenario_coverages.append(coverage)
            scenario_result["apps_rg_coverage_summary"] = coverage
        scenario_results.append(scenario_result)
    apps_rg_coverage_summary = (
        _apps_rg_suite_coverage(
            suite_id=request.suite_id,
            app_id=str(suite["app_id"]),
            rows=apps_rg_scorecard_rows,
            scenario_summaries=apps_rg_scenario_coverages,
        )
        if suite.get("app_id") == "apps_rg"
        else {}
    )
    scorecard = _score(
        request.suite_id,
        str(suite["app_id"]),
        len(fixtures),
        findings,
        thresholds=thresholds,
        scorecard_rows=apps_rg_scorecard_rows,
        component_scorecards=apps_rg_component_scorecards,
        coverage_summary=apps_rg_coverage_summary,
    )
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
    _wg.write_text(Path(paths["eval_record"]), json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    _wg.write_text(Path(paths["report"]), render_report(record, findings), encoding="utf-8")
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
        _wg.write_text(Path(paths["eval_record"]), json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        _wg.write_text(Path(paths["report"]), render_report(record, findings), encoding="utf-8")
    return record


def render_record(record_path: str) -> str:
    return render_record_markdown(_load_json(Path(record_path)))
