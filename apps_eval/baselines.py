"""Named baseline helpers for apps_eval records."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from apps_eval.contracts import CURRENT_EVAL_RECORD_SCHEMA_VERSION

_BASELINE_NAME = re.compile(r"^[A-Za-z0-9_.-]{3,120}$")
DEFAULT_BASELINE_DIR = Path("apps_eval/baselines")


def baseline_path(name: str, baseline_dir: str | Path = DEFAULT_BASELINE_DIR) -> Path:
    if not _BASELINE_NAME.fullmatch(name):
        raise ValueError("baseline name must use letters, numbers, dots, dashes, or underscores")
    return Path(baseline_dir) / f"{name}.json"


def _validate_record_schema(record: dict[str, Any], path: Path) -> None:
    schema_version = record.get("schema_version")
    if schema_version != CURRENT_EVAL_RECORD_SCHEMA_VERSION:
        raise ValueError(
            f"baseline schema_version mismatch for {path}: expected {CURRENT_EVAL_RECORD_SCHEMA_VERSION!r}, "
            f"found {schema_version!r}"
        )
    if "record_id" not in record or "scorecard" not in record:
        raise ValueError(f"baseline missing required eval record fields: {path}")


def load_baseline(name: str, baseline_dir: str | Path = DEFAULT_BASELINE_DIR) -> dict[str, Any]:
    path = baseline_path(name, baseline_dir)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"baseline must contain an object: {path}")
    _validate_record_schema(data, path)
    return data


def promote_baseline(
    record_path: str | Path,
    name: str,
    *,
    baseline_dir: str | Path = DEFAULT_BASELINE_DIR,
    require_pass: bool = True,
) -> Path:
    source = Path(record_path)
    with source.open(encoding="utf-8") as handle:
        record = json.load(handle)
    if not isinstance(record, dict):
        raise ValueError(f"record must contain an object: {source}")
    _validate_record_schema(record, source)
    if require_pass and record.get("scorecard", {}).get("verdict") != "pass":
        raise ValueError("only passing eval records can be promoted as baselines")
    target = baseline_path(name, baseline_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target
