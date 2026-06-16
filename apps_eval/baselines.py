"""Named baseline helpers for apps_eval records."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

_BASELINE_NAME = re.compile(r"^[A-Za-z0-9_.-]{3,120}$")
DEFAULT_BASELINE_DIR = Path("apps_eval/baselines")


def baseline_path(name: str, baseline_dir: str | Path = DEFAULT_BASELINE_DIR) -> Path:
    if not _BASELINE_NAME.fullmatch(name):
        raise ValueError("baseline name must use letters, numbers, dots, dashes, or underscores")
    return Path(baseline_dir) / f"{name}.json"


def load_baseline(name: str, baseline_dir: str | Path = DEFAULT_BASELINE_DIR) -> dict[str, Any]:
    path = baseline_path(name, baseline_dir)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"baseline must contain an object: {path}")
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
    if require_pass and record.get("scorecard", {}).get("verdict") != "pass":
        raise ValueError("only passing eval records can be promoted as baselines")
    target = baseline_path(name, baseline_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target
