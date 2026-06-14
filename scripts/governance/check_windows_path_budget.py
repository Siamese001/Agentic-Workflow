"""Preflight Windows artifact output roots against a reserved path budget."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Sequence

WIN32_MAX_PATH = 260
DEFAULT_WARN_LIMIT = 230
DEFAULT_FAIL_LIMIT = 240
DEFAULT_RUN_ID = "0" * 16
DEFAULT_SUITE = "apps_rg.dev.resume_generation"
DEFAULT_SCENARIO = "resume_tailor_escalation"

DEFAULT_SUFFIX_TEMPLATES = (
    "{suite_path}/{run_id}/eval_record.json",
    "{suite_path}/{run_id}/report.md",
    "{suite_path}/{run_id}/scorecard.csv",
    "{suite_path}/{run_id}/l6_handoff.json",
    "{suite_path}/{run_id}/l6_shadow_bridge_spans.jsonl",
    (
        "{suite_path}/{run_id}/live_adapter_artifacts/{scenario}/"
        "agentic_core_l7_route_family_coverage.json"
    ),
)

_NON_SEGMENT_CHARS = re.compile(r"[^A-Za-z0-9]+")


@dataclass(frozen=True)
class ProjectedPath:
    """A projected artifact path and its rendered string length."""

    path: PurePath
    length: int


def suite_to_path_segment(suite: str) -> str:
    """Match apps_eval suite path normalization for path-budget estimates."""

    segment = _NON_SEGMENT_CHARS.sub("_", suite).strip("_")
    if not segment:
        raise ValueError("suite must contain at least one path-safe character")
    return segment


def suffix_parts(
    template: str,
    *,
    suite: str,
    run_id: str = DEFAULT_RUN_ID,
    scenario: str = DEFAULT_SCENARIO,
) -> tuple[str, ...]:
    """Render a relative suffix template into path parts."""

    rendered = template.format(
        suite_path=suite_to_path_segment(suite),
        run_id=run_id,
        scenario=scenario,
    )
    parts = tuple(part for part in rendered.replace("\\", "/").split("/") if part)
    if not parts:
        raise ValueError(f"empty suffix template: {template!r}")
    if ":" in parts[0]:
        raise ValueError(f"suffix template must be relative: {template!r}")
    return parts


def projected_paths(
    out_dir: str | PurePath,
    *,
    suite: str = DEFAULT_SUITE,
    run_id: str = DEFAULT_RUN_ID,
    scenario: str = DEFAULT_SCENARIO,
    suffix_templates: Sequence[str] | None = None,
) -> list[ProjectedPath]:
    """Return projected paths under an output directory."""

    root = PurePath(out_dir)
    templates = suffix_templates or DEFAULT_SUFFIX_TEMPLATES
    projections: list[ProjectedPath] = []
    for template in templates:
        path = root.joinpath(*suffix_parts(template, suite=suite, run_id=run_id, scenario=scenario))
        projections.append(ProjectedPath(path=path, length=len(str(path))))
    return projections


def budget_violations(
    projections: Sequence[ProjectedPath],
    *,
    warn_limit: int = DEFAULT_WARN_LIMIT,
    fail_limit: int = DEFAULT_FAIL_LIMIT,
) -> tuple[list[ProjectedPath], list[ProjectedPath]]:
    """Split projections into hard failures and warnings."""

    failures = [item for item in projections if item.length >= fail_limit]
    warnings = [item for item in projections if warn_limit <= item.length < fail_limit]
    return failures, warnings


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that projected artifact paths stay below the repo's reserved "
            "Windows MAX_PATH budget."
        )
    )
    parser.add_argument("--out-dir", required=True, type=Path, help="Evaluation or proof output root.")
    parser.add_argument("--suite", default=DEFAULT_SUITE, help="apps_eval suite id.")
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, help="Longest expected scenario id.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID, help="Run id placeholder for path estimates.")
    parser.add_argument(
        "--suffix",
        action="append",
        default=None,
        help=(
            "Relative suffix template to check. May use {suite_path}, {run_id}, "
            "and {scenario}. Repeat to check multiple custom suffixes."
        ),
    )
    parser.add_argument(
        "--warn-limit",
        type=int,
        default=DEFAULT_WARN_LIMIT,
        help="Warn when a projected absolute path reaches this length.",
    )
    parser.add_argument(
        "--budget",
        "--fail-limit",
        dest="fail_limit",
        type=int,
        default=DEFAULT_FAIL_LIMIT,
        help="Fail when a projected absolute path reaches this length.",
    )
    args = parser.parse_args(argv)
    if args.warn_limit >= args.fail_limit:
        parser.error("--warn-limit must be lower than --budget/--fail-limit")
    if args.fail_limit >= WIN32_MAX_PATH:
        parser.error("--budget/--fail-limit must stay below the Win32 MAX_PATH boundary")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir.expanduser().resolve(strict=False)
    projections = projected_paths(
        out_dir,
        suite=args.suite,
        run_id=args.run_id,
        scenario=args.scenario,
        suffix_templates=args.suffix,
    )
    failures, warnings = budget_violations(
        projections,
        warn_limit=args.warn_limit,
        fail_limit=args.fail_limit,
    )
    max_projection = max(projections, key=lambda item: item.length)

    print("Windows path-budget check")
    print(f"- out_dir: {out_dir}")
    print(f"- max_projected_length: {max_projection.length}")
    print(f"- fail_limit: {args.fail_limit}")
    print(f"- win32_max_path: {WIN32_MAX_PATH}")
    print(f"- max_projected_path: {max_projection.path}")

    if failures:
        print("FAIL: projected artifact path exceeds the reserved Windows budget")
        for item in sorted(failures, key=lambda projection: projection.length, reverse=True)[:5]:
            print(f"- {item.length}: {item.path}")
        return 1

    if warnings:
        print("WARN: projected artifact path is close to the reserved Windows budget")
        for item in sorted(warnings, key=lambda projection: projection.length, reverse=True)[:5]:
            print(f"- {item.length}: {item.path}")
        return 0

    print("PASS: projected artifact paths are within budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
