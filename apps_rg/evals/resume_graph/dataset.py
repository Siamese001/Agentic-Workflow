"""Dataset loading helpers for the resume-graph evaluator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps_rg.evals.resume_graph.models import EvaluationDataError


def _mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = value.get(key)
    if not isinstance(nested, Mapping):
        raise EvaluationDataError(f"profile field {key!r} must be a mapping")
    return nested


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationDataError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise EvaluationDataError(f"{path}:{line_number}: row must be an object")
        rows.append(row)
    return rows


def _load_jsonl_bytes(payload: bytes, *, source: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvaluationDataError(f"{source}: invalid UTF-8: {exc}") from exc
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationDataError(f"{source}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise EvaluationDataError(f"{source}:{line_number}: row must be an object")
        rows.append(row)
    return rows
