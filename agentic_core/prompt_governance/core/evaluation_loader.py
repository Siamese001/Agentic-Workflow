"""Centralized evaluation corpus loading and caching system.

Mirrors PromptLoader pattern exactly — pure infrastructure, no business logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class EvalLoadError(Exception):
    """Raised when an evaluation file cannot be loaded."""

    pass


class EvalSchemaError(Exception):
    """Raised when an evaluation file has an invalid schema."""

    pass


class EvaluationLoader:
    """Pure infrastructure component for loading and caching evaluation YAML files.

    Enforces architectural boundaries:
    - No business logic
    - No domain text formatting
    - No direct apps_* access
    """

    def __init__(self, eval_dir: Path) -> None:
        """Initialize with injected evaluation directory.

        Args:
            eval_dir: Base directory containing evaluation YAML files.

        Raises:
            TypeError: If eval_dir is not a Path object.
            ValueError: If eval_dir does not exist or is not a directory.
        """
        if not isinstance(eval_dir, Path):
            raise TypeError("eval_dir must be a Path object")
        if not eval_dir.exists():
            raise ValueError(f"eval_dir does not exist: {eval_dir}")
        if not eval_dir.is_dir():
            raise ValueError(f"eval_dir must be a directory: {eval_dir}")
        self._eval_dir = eval_dir.resolve()
        self._cache: dict[str, dict[str, Any]] = {}

    def load_eval_set(self, name: str) -> dict[str, Any]:
        """Load and cache an evaluation set by name.

        Args:
            name: Evaluation file name without extension (e.g. 'rubric').

        Returns:
            Loaded evaluation data dictionary.

        Raises:
            EvalLoadError: If the file is missing, unreadable, or YAML is malformed.
            EvalSchemaError: If the top-level value is not a dict.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluationLoader.load_eval_set")

        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if name not in self._cache:
            eval_file = self._eval_dir / f"{name}.yaml"
            if not eval_file.exists():
                raise EvalLoadError(f"Evaluation file not found: {eval_file}")
            if not eval_file.is_file():
                raise EvalLoadError(f"Path is not a file: {eval_file}")
            try:
                with open(eval_file, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                raise EvalLoadError(f"Invalid YAML in {eval_file}: {exc}") from exc
            except OSError as exc:
                raise EvalLoadError(f"Cannot read {eval_file}: {exc}") from exc
            if not isinstance(data, dict):
                raise EvalSchemaError(
                    f"Evaluation file root must be a dict, got {type(data).__name__}: {eval_file}"
                )
            self._cache[name] = data
        return self._cache[name]

    def clear_cache(self) -> None:
        """Clear the internal cache. Useful for test isolation."""
        self._cache.clear()

    def cache_info(self) -> dict[str, Any]:
        """Return cache statistics for testing and monitoring."""
        return {"cached_items": len(self._cache), "cache_keys": list(self._cache.keys())}
