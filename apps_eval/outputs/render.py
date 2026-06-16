"""Markdown rendering for sealed eval artifacts."""

from __future__ import annotations

from typing import Any


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(record: Any, findings: list[Any]) -> str:
    scorecard = record.scorecard
    regression = record.regression
    lines = [
        f"# apps_eval report: {record.suite_id}",
        "",
        f"App: `{record.app_id}`",
        f"Mode: `{record.mode}`",
        f"Score: `{scorecard.score:.6f}`",
        f"Verdict: `{scorecard.verdict}`",
        f"Scenarios: `{scorecard.scenario_count}`",
        f"Findings: `{scorecard.passed_findings}` passed / `{scorecard.failed_findings}` failed",
        f"Block failures: `{scorecard.block_failures}`",
        "",
        "## Scenario Results",
        "",
        "| Scenario | Passed | Failed Findings |",
        "|---|---:|---:|",
    ]
    for scenario in record.scenario_results:
        failed = sum(1 for finding in scenario.get("findings", []) if not finding.get("passed"))
        lines.append(f"| {_cell(scenario.get('scenario_id', ''))} | {scenario.get('passed', False)} | {failed} |")
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
            "",
            "## Artifacts",
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
    lines = [
        f"# apps_eval record: {record.get('suite_id', '')}",
        "",
        f"App: `{record.get('app_id', '')}`",
        f"Score: `{scorecard.get('score', 0.0)}`",
        f"Verdict: `{scorecard.get('verdict', '')}`",
        "",
        "## Artifacts",
    ]
    for key, value in sorted((record.get("artifact_paths") or {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"
