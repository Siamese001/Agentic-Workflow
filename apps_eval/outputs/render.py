"""Markdown rendering for sealed eval artifacts."""

from __future__ import annotations

from typing import Any


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _sorted_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _format_modes(counts: dict[str, int], limit: int = 3) -> str:
    if not counts:
        return "n/a"
    return ", ".join(f"{mode} ({count})" for mode, count in _sorted_counts(counts)[:limit])


def render_report(record: Any, findings: list[Any]) -> str:
    scorecard = record.scorecard
    regression = record.regression
    flywheel = getattr(record, "regression_flywheel", None)
    run_metadata = record.run_metadata
    provenance_by_scenario = {item.scenario_id: item for item in getattr(record, "fixture_provenance", [])}
    lines = [
        f"# apps_eval report: {record.suite_id}",
        "",
        "## Run Context",
        "",
        f"Schema version: `{record.schema_version}`",
        f"Record ID: `{record.record_id}`",
        f"Created at: `{record.created_at}`",
        f"Project: `{run_metadata.project_name} {run_metadata.project_version or 'unknown'}`",
        f"Git commit: `{run_metadata.git_commit or 'unknown'}`",
        f"Python: `{run_metadata.python_version or 'unknown'}`",
        f"Platform: `{run_metadata.platform or 'unknown'}`",
        f"Mode: `{record.mode}`",
        f"Deterministic only: `{record.deterministic_only}`",
        f"Compare baseline: `{run_metadata.compare_baseline}`",
        f"Record seed digest: `{run_metadata.record_seed_digest or 'unknown'}`",
        f"Scorer version: `{run_metadata.scorer_version}`",
        "",
        "## Scorecard",
        "",
        f"App: `{record.app_id}`",
        f"Score: `{scorecard.score:.6f}`",
        f"Verdict: `{scorecard.verdict}`",
        f"Scenarios: `{scorecard.scenario_count}`",
        f"Findings: `{scorecard.passed_findings}` passed / `{scorecard.failed_findings}` failed",
        f"Block failures: `{scorecard.block_failures}`",
        "",
    ]
    coverage_summary = getattr(scorecard, "coverage_summary", {}) or {}
    component_scorecards = getattr(scorecard, "component_scorecards", []) or []
    scorecard_rows = getattr(scorecard, "scorecard_rows", []) or []
    if coverage_summary or component_scorecards or scorecard_rows:
        lines.extend(
            [
                "## apps_rg Microstep Coverage",
                "",
                f"Coverage verdict: `{coverage_summary.get('verdict', 'n/a')}`",
                f"Coverage complete: `{coverage_summary.get('coverage_complete', False)}`",
                f"Release blocked: `{coverage_summary.get('release_blocked', False)}`",
                f"Required microsteps: `{coverage_summary.get('required_microsteps', len(scorecard_rows))}`",
                f"Emitted rows: `{coverage_summary.get('emitted_rows', len(scorecard_rows))}`",
                f"Missing required artifacts: `{coverage_summary.get('missing_required_artifacts', 0)}`",
                f"Unknown required: `{coverage_summary.get('unknown_required', 0)}`",
                f"Not run required: `{coverage_summary.get('not_run_required', 0)}`",
                "",
                "| Component | Subcomponent | Stage | Lane | Score | Verdict | Blocks |",
                "|---|---|---|---|---:|---|---:|",
            ]
        )
        for row in component_scorecards[:40]:
            lines.append(
                "| {component} | {subcomponent} | {stage} | {lane} | {score:.6f} | {verdict} | {blocks} |".format(
                    component=_cell(row.get("component_id", "")),
                    subcomponent=_cell(row.get("subcomponent_id", "")),
                    stage=_cell(row.get("stage_id", "")),
                    lane=_cell(row.get("lane_id", "")),
                    score=float(row.get("score", 0.0)),
                    verdict=_cell(row.get("verdict", "")),
                    blocks=int(row.get("blocking_failure_count", 0)),
                )
            )
        if len(component_scorecards) > 40:
            lines.append(f"| _truncated_ | | | | | | {len(component_scorecards) - 40} more |")
        lines.append("")
    lines.extend(
        [
            "## Failure Modes",
            "",
            f"Dominant family: `{(flywheel.dominant_failure_family or 'n/a') if flywheel else 'n/a'}`",
            f"Dominant mode: `{(flywheel.dominant_failure_mode or 'n/a') if flywheel else 'n/a'}`",
            "",
            "| Failure Family | Count |",
            "|---|---:|",
        ]
    )
    family_counts = scorecard.failure_family_counts
    if family_counts:
        for key, value in _sorted_counts(family_counts):
            lines.append(f"| {_cell(key)} | {value} |")
    else:
        lines.append("| _none_ | 0 |")
    lines.extend(
        [
            "",
            "| Failure Mode | Count |",
            "|---|---:|",
        ]
    )
    mode_counts = scorecard.failure_mode_counts
    if mode_counts:
        for key, value in _sorted_counts(mode_counts):
            lines.append(f"| {_cell(key)} | {value} |")
    else:
        lines.append("| _none_ | 0 |")
    lines.extend(
        [
            "",
            "## Fixture Provenance",
            "",
            "| Scenario | Fixture Path | Definition Digest | Input Digest | Expected Digest | Snapshot Digest |",
            "|---|---|---|---|---|---|",
        ]
    )
    for scenario_id, provenance in sorted(provenance_by_scenario.items()):
        lines.append(
            "| {scenario} | {path} | {definition} | {input} | {expected} | {snapshot} |".format(
                scenario=_cell(scenario_id),
                path=_cell(provenance.fixture_path),
                definition=_cell(provenance.scenario_definition_digest),
                input=_cell(provenance.input_request_digest),
                expected=_cell(provenance.expected_digest),
                snapshot=_cell(provenance.snapshot_digest),
            )
        )
    lines.extend(
        [
            "",
            "## Scenario Results",
            "",
            "| Scenario | Passed | Failed Findings | Primary Failure Mode | Snapshot Digest | Snapshot Ref |",
            "|---|---:|---:|---|---|---|",
        ]
    )
    for scenario in record.scenario_results:
        lines.append(
            f"| {_cell(scenario.get('scenario_id', ''))} | {scenario.get('passed', False)} | {scenario.get('failed_findings', 0)} | "
            f"{_cell(scenario.get('dominant_failure_mode', ''))} | {_cell(scenario.get('snapshot_digest', ''))} | {_cell(scenario.get('snapshot_ref', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Dimension Scores",
            "",
            "| Dimension | Score |",
            "|---|---:|",
        ]
    )
    for key, value in sorted(scorecard.dimension_scores.items()):
        lines.append(f"| {_cell(key)} | {value:.6f} |")
    lines.extend(
        [
            "",
            "## Regression",
            "",
            f"Compared: `{regression.compared}`",
            f"Verdict: `{regression.verdict}`",
            f"Delta: `{regression.delta:.6f}`",
            f"Baseline path: `{regression.baseline_path or 'n/a'}`",
            f"Baseline digest: `{regression.baseline_digest or 'n/a'}`",
            "",
            "## Regression Flywheel",
            "",
            f"Compared: `{flywheel.compared if flywheel else False}`",
            f"Current score: `{flywheel.current_score:.6f}`" if flywheel else "Current score: `0.000000`",
            f"Baseline score: `{flywheel.baseline_score:.6f}`" if flywheel else "Baseline score: `0.000000`",
            f"Delta: `{flywheel.delta:.6f}`" if flywheel else "Delta: `0.000000`",
            f"Verdict: `{flywheel.verdict}`" if flywheel else "Verdict: `not_compared`",
            f"New failure modes: `{', '.join(flywheel.new_failure_modes) if flywheel and flywheel.new_failure_modes else 'n/a'}`",
            f"Recovered failure modes: `{', '.join(flywheel.recovered_failure_modes) if flywheel and flywheel.recovered_failure_modes else 'n/a'}`",
            f"Repeated failure modes: `{', '.join(flywheel.repeated_failure_modes) if flywheel and flywheel.repeated_failure_modes else 'n/a'}`",
            "",
            "| Scenario | Failed Findings | Block Failures | Primary Failure Mode | Failure Modes |",
            "|---|---:|---:|---|---|",
        ]
    )
    if flywheel and flywheel.scenario_hotspots:
        for hotspot in flywheel.scenario_hotspots:
            lines.append(
                f"| {_cell(hotspot.get('scenario_id', ''))} | {hotspot.get('failed_findings', 0)} | {hotspot.get('block_failures', 0)} | "
                f"{_cell(hotspot.get('dominant_failure_mode', ''))} | {_cell(', '.join(hotspot.get('failure_modes', [])) or 'n/a')} |"
            )
    else:
        lines.append("| _none_ | 0 | 0 | _n/a_ | _n/a_ |")
    lines.extend(
        [
            "",
            "## Artifact Inventory",
            "",
        ]
    )
    for key, value in sorted(record.artifact_paths.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Scenario | Grader | Passed | Severity | Score | Message |",
            "|---|---|---:|---|---:|---|",
        ]
    )
    for finding in findings:
        lines.append(
            f"| {_cell(finding.scenario_id)} | {_cell(finding.grader_id)} | {finding.passed} | "
            f"{_cell(finding.severity)} | {finding.score:.6f} | {_cell(finding.message)} |"
        )
    lines.extend(
        [
            "",
            "## Review Guidance",
            "",
            "- Treat any block failure as release-blocking until the fixture, snapshot, or product output is corrected.",
            "- Treat warning failures as review items unless the suite threshold already fails.",
            "- Promote a new baseline only from a passing record after reviewing changed fixtures and report artifacts.",
            "",
        ]
    )
    return "\n".join(lines)


def render_record_markdown(record: dict[str, Any]) -> str:
    scorecard = record.get("scorecard", {})
    run_metadata = record.get("run_metadata", {})
    lines = [
        f"# apps_eval record: {record.get('suite_id', '')}",
        "",
        f"Schema version: `{record.get('schema_version', '')}`",
        f"App: `{record.get('app_id', '')}`",
        f"Record ID: `{record.get('record_id', '')}`",
        f"Score: `{scorecard.get('score', 0.0)}`",
        f"Verdict: `{scorecard.get('verdict', '')}`",
        f"Record seed digest: `{run_metadata.get('record_seed_digest', '')}`",
        f"Top failure modes: `{_format_modes(scorecard.get('failure_mode_counts', {}))}`",
        "",
        "## Artifact Inventory",
    ]
    for key, value in sorted((record.get("artifact_paths") or {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"
