#!/usr/bin/env python3
"""Require trigger and output-quality eval fixtures for high-risk skills."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".codex" / "skills"
REQUIRED_SKILLS = (
    "artifact-management",
    "boundary-enforcement",
    "graph-analysis",
    "mcp-integration",
    "operational-gates",
    "structured-reasoning",
    "testing-framework",
)
MIN_TRIGGER_TOTAL = 12
MIN_TRIGGER_PER_LABEL = 6
MIN_OUTPUT_EVALS = 2
_VALID_SPLITS = {"train", "validation"}


@dataclass(slots=True)
class EvalCoverageResult:
    skill: str
    issues: list[str] = field(default_factory=list)
    trigger_queries: int = 0
    output_evals: int = 0


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"missing {path.name}"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"invalid {path.name}: {exc}"


def _validate_trigger_queries(payload: Any) -> tuple[list[str], int]:
    issues: list[str] = []
    if not isinstance(payload, list):
        return ["trigger_queries.json must contain a JSON array"], 0

    positives = 0
    negatives = 0
    split_labels: dict[str, set[bool]] = {split: set() for split in _VALID_SPLITS}
    seen_queries: set[str] = set()
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            issues.append(f"trigger query {index} must be an object")
            continue
        query = row.get("query")
        should_trigger = row.get("should_trigger")
        split = row.get("split")
        if not isinstance(query, str) or not query.strip():
            issues.append(f"trigger query {index} has no non-empty query")
        elif query.strip() in seen_queries:
            issues.append(f"trigger query {index} duplicates another query")
        else:
            seen_queries.add(query.strip())
        if not isinstance(should_trigger, bool):
            issues.append(f"trigger query {index} should_trigger must be boolean")
        else:
            positives += int(should_trigger)
            negatives += int(not should_trigger)
        if split not in _VALID_SPLITS:
            issues.append(f"trigger query {index} split must be train or validation")
        elif isinstance(should_trigger, bool):
            split_labels[split].add(should_trigger)

    if len(payload) < MIN_TRIGGER_TOTAL:
        issues.append(f"requires at least {MIN_TRIGGER_TOTAL} trigger queries")
    if positives < MIN_TRIGGER_PER_LABEL:
        issues.append(f"requires at least {MIN_TRIGGER_PER_LABEL} should-trigger queries")
    if negatives < MIN_TRIGGER_PER_LABEL:
        issues.append(f"requires at least {MIN_TRIGGER_PER_LABEL} should-not-trigger queries")
    for split, labels in sorted(split_labels.items()):
        if labels != {False, True}:
            issues.append(f"{split} split must include positive and negative queries")
    return issues, len(payload)


def _validate_output_evals(payload: Any, skill_name: str) -> tuple[list[str], int]:
    issues: list[str] = []
    if not isinstance(payload, dict):
        return ["evals.json must contain a JSON object"], 0
    if payload.get("skill_name") != skill_name:
        issues.append("evals.json skill_name must match the skill directory")
    evals = payload.get("evals")
    if not isinstance(evals, list):
        return [*issues, "evals.json must contain an evals array"], 0

    seen_ids: set[str] = set()
    for index, row in enumerate(evals):
        if not isinstance(row, dict):
            issues.append(f"output eval {index} must be an object")
            continue
        eval_id = str(row.get("id", "")).strip()
        if not eval_id:
            issues.append(f"output eval {index} has no id")
        elif eval_id in seen_ids:
            issues.append(f"output eval {index} duplicates id {eval_id}")
        else:
            seen_ids.add(eval_id)
        for field_name in ("prompt", "expected_output"):
            value = row.get(field_name)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"output eval {index} field {field_name} must be non-empty")
        files = row.get("files", [])
        if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
            issues.append(f"output eval {index} files must be a string array")

    if len(evals) < MIN_OUTPUT_EVALS:
        issues.append(f"requires at least {MIN_OUTPUT_EVALS} output evals")
    return issues, len(evals)


def evaluate_skill(skill_dir: Path) -> EvalCoverageResult:
    result = EvalCoverageResult(skill=skill_dir.name)
    trigger_payload, trigger_error = _load_json(skill_dir / "evals" / "trigger_queries.json")
    if trigger_error:
        result.issues.append(trigger_error)
    else:
        issues, count = _validate_trigger_queries(trigger_payload)
        result.issues.extend(issues)
        result.trigger_queries = count

    output_payload, output_error = _load_json(skill_dir / "evals" / "evals.json")
    if output_error:
        result.issues.append(output_error)
    else:
        issues, count = _validate_output_evals(output_payload, skill_dir.name)
        result.issues.extend(issues)
        result.output_evals = count
    return result


def evaluate_required_skills(
    skills_root: Path,
    required_skills: tuple[str, ...] = REQUIRED_SKILLS,
) -> list[EvalCoverageResult]:
    results: list[EvalCoverageResult] = []
    for skill_name in required_skills:
        skill_dir = skills_root / skill_name
        if not (skill_dir / "SKILL.md").is_file():
            results.append(EvalCoverageResult(skill=skill_name, issues=["required skill is missing"]))
            continue
        results.append(evaluate_skill(skill_dir))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skills-root", type=Path, default=SKILLS_ROOT)
    args = parser.parse_args(argv)

    results = evaluate_required_skills(args.skills_root.resolve())
    failures = [result for result in results if result.issues]
    report = {
        "status": "FAIL" if failures else "PASS",
        "required_skills": list(REQUIRED_SKILLS),
        "thresholds": {
            "trigger_total": MIN_TRIGGER_TOTAL,
            "trigger_per_label": MIN_TRIGGER_PER_LABEL,
            "output_evals": MIN_OUTPUT_EVALS,
        },
        "results": [asdict(result) for result in results],
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif failures:
        print("[skill_eval_coverage] FAIL:")
        for result in failures:
            print(f"  {result.skill}")
            for issue in result.issues:
                print(f"    - {issue}")
    else:
        print(f"[skill_eval_coverage] OK: {len(results)} core skills have eval coverage.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
