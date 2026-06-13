"""Markdown rendering for sealed eval artifacts."""

from __future__ import annotations

from typing import Any


def render_report(record: Any, findings: list[Any]) -> str:
    lines = [
        f"# apps_eval report: {record.suite_id}",
        "",
        f"App: `{record.app_id}`",
        f"Mode: `{record.mode}`",
        f"Score: `{record.scorecard.score:.6f}`",
        f"Verdict: `{record.scorecard.verdict}`",
        f"Block failures: `{record.scorecard.block_failures}`",
        "",
        "## Findings",
        "",
        "| Scenario | Grader | Passed | Severity | Message |",
        "|---|---|---:|---|---|",
    ]
    for finding in findings:
        lines.append(
            f"| {finding.scenario_id} | {finding.grader_id} | {finding.passed} | {finding.severity} | {finding.message} |"
        )
    lines.append("")
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
