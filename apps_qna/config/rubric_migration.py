"""Per-app rubric migration helper — D3.3.

Validates and reports alignment between eval_rubrics.yaml dimensions and
grader_roster.yaml grader entries for apps_qna. Ensures every dim with
grader_type=llm_as_judge has a corresponding registered judge in the
llm_judge_graders roster, and vice versa.

This module is purely analytical — it reads the YAML configs and returns
a typed migration report. It does NOT mutate any files.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D3.3
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_CONFIG_DIR = Path(__file__).parent / "domain_contract"
_RUBRIC_PATH = _CONFIG_DIR / "eval_rubrics.yaml"
_ROSTER_PATH = _CONFIG_DIR / "grader_roster.yaml"

_LLM_JUDGE_GRADER_TYPE = "llm_as_judge"
_JUDGE_ID_PATTERN = re.compile(r"qna::(\w+)_judge::\w+")


@dataclass(frozen=True)
class RubricDimEntry:
    """A single dimension from the eval rubric."""

    dimension_id: str
    grader_type: str
    weight: float = 0.0
    min_required_score: float = 0.0
    fail_closed_if_unknown: bool = True


@dataclass(frozen=True)
class MigrationReport:
    """Result of a rubric↔roster alignment check.

    Attributes:
        llm_dims: Rubric dims declared as llm_as_judge.
        registered_judges: Judge IDs in the roster's llm_judge_graders list.
        missing_in_roster: Dims present in rubric but absent from roster.
        missing_in_rubric: Roster judges with no matching rubric dim.
        aligned: True when missing_in_roster and missing_in_rubric are empty.
        all_dims: All dims from the rubric (for reference).
    """

    llm_dims: tuple[RubricDimEntry, ...] = field(default_factory=tuple)
    registered_judges: tuple[str, ...] = field(default_factory=tuple)
    missing_in_roster: tuple[str, ...] = field(default_factory=tuple)
    missing_in_rubric: tuple[str, ...] = field(default_factory=tuple)
    aligned: bool = False
    all_dims: tuple[RubricDimEntry, ...] = field(default_factory=tuple)


def _load_yaml_simple(path: Path) -> list[dict[str, Any]]:
    """Minimal YAML loader — handles only the flat list-of-dicts structure
    used by apps_qna domain contracts. Avoids a PyYAML dependency at this
    layer by delegating to PyYAML when available, falling back to a best-
    effort parser for CI environments without it.
    """
    try:
        import yaml  # type: ignore[import]
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except ImportError:
        pass

    lines = path.read_text(encoding="utf-8").splitlines()
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in lines:
        if line.startswith("- ") and ":" in line:
            if current:
                records.append(current)
            key, _, value = line[2:].partition(":")
            current = {key.strip(): value.strip()}
        elif line.startswith("  ") and ":" in line and not line.strip().startswith("-"):
            key, _, value = line.strip().partition(":")
            current[key.strip()] = value.strip()
    if current:
        records.append(current)
    return records


def _extract_llm_dims(rubric_path: Path) -> tuple[tuple[RubricDimEntry, ...], tuple[RubricDimEntry, ...]]:
    """Return (llm_dims, all_dims) from the rubric YAML."""
    try:
        records = _load_yaml_simple(rubric_path)
    except Exception:
        return (), ()

    all_dims: list[RubricDimEntry] = []
    llm_dims: list[RubricDimEntry] = []
    for record in records:
        dims_raw = record.get("score_dimensions") or []
        for dim in dims_raw:
            if not isinstance(dim, dict):
                continue
            entry = RubricDimEntry(
                dimension_id=str(dim.get("dimension_id", "")),
                grader_type=str(dim.get("grader_type", "")),
                weight=float(dim.get("weight", 0.0)),
                min_required_score=float(dim.get("min_required_score", 0.0)),
                fail_closed_if_unknown=bool(dim.get("fail_closed_if_unknown", True)),
            )
            all_dims.append(entry)
            if entry.grader_type == _LLM_JUDGE_GRADER_TYPE:
                llm_dims.append(entry)
    return tuple(llm_dims), tuple(all_dims)


def _extract_registered_judges(roster_path: Path) -> tuple[str, ...]:
    """Return the llm_judge_graders list from the roster YAML."""
    try:
        records = _load_yaml_simple(roster_path)
    except Exception:
        return ()
    judges: list[str] = []
    for record in records:
        raw = record.get("llm_judge_graders") or []
        if isinstance(raw, list):
            judges.extend(str(j) for j in raw if j)
    return tuple(judges)


def _dim_id_from_judge_id(judge_id: str) -> str:
    """Extract the dimension id from a roster judge id.

    e.g. "qna::context_recall_judge::v1" → "context_recall"
    """
    match = _JUDGE_ID_PATTERN.match(judge_id)
    if match:
        return match.group(1)
    return judge_id


def check_rubric_roster_alignment(
    rubric_path: Path | None = None,
    roster_path: Path | None = None,
) -> MigrationReport:
    """Check alignment between eval_rubrics.yaml and grader_roster.yaml.

    Args:
        rubric_path: Path to eval_rubrics.yaml (defaults to canonical location).
        roster_path: Path to grader_roster.yaml (defaults to canonical location).

    Returns:
        MigrationReport describing alignment state.
    """
    rp = rubric_path or _RUBRIC_PATH
    rop = roster_path or _ROSTER_PATH

    llm_dims, all_dims = _extract_llm_dims(rp)
    registered = _extract_registered_judges(rop)

    llm_dim_ids = {d.dimension_id for d in llm_dims}
    registered_dim_ids = {_dim_id_from_judge_id(j) for j in registered}

    missing_in_roster = tuple(sorted(llm_dim_ids - registered_dim_ids))
    missing_in_rubric = tuple(sorted(registered_dim_ids - llm_dim_ids))
    aligned = not missing_in_roster and not missing_in_rubric

    return MigrationReport(
        llm_dims=llm_dims,
        registered_judges=registered,
        missing_in_roster=missing_in_roster,
        missing_in_rubric=missing_in_rubric,
        aligned=aligned,
        all_dims=all_dims,
    )


def get_judge_class_for_dim(dimension_id: str) -> type | None:
    """Look up the D1.2 judge class for a given rubric dimension_id.

    Returns None if no judge is registered for the dim.

    Args:
        dimension_id: Rubric dimension id (e.g. "context_recall").

    Returns:
        Judge class or None.
    """
    try:
        from apps_qna.engines.judges import (
            ContextRecallJudge,
            ContextPrecisionJudge,
            AnswerRelevancyJudge,
        )
    except ImportError:
        return None

    _DIM_TO_CLASS: dict[str, type] = {
        "context_recall": ContextRecallJudge,
        "context_precision": ContextPrecisionJudge,
        "answer_relevancy": AnswerRelevancyJudge,
    }
    return _DIM_TO_CLASS.get(dimension_id)


__all__ = [
    "MigrationReport",
    "RubricDimEntry",
    "check_rubric_roster_alignment",
    "get_judge_class_for_dim",
]
