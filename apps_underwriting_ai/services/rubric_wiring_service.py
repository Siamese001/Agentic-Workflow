"""Loads and caches the Qwen-first rationale judge rubric.

The rubric YAML lives at
``apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml``
and is emitted by the activation plan e8a3c5 W1 P1.1.

This service exposes a structured :class:`RubricSpec` to callers
(assembler, validators, telemetry) so the YAML is parsed exactly once
per process.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


_DEFAULT_RUBRIC_PATH = (
    Path(__file__).resolve().parent.parent
    / "policy"
    / "rubrics"
    / "judge_underwriting_decision.yaml"
)


@dataclass(frozen=True)
class RubricCriterion:
    """Single evaluation criterion within the rubric."""

    id: str
    description: str
    weight: float


@dataclass(frozen=True)
class RubricSpec:
    """Parsed rubric specification.

    Attributes mirror the YAML shape exactly. Field names preserve the
    activation plan's schema so downstream consumers can assume stable
    keys.
    """

    rubric_id: str
    rubric_version: int
    owning_app: str
    owning_module: str
    scope: dict[str, Any]
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    criteria: tuple[RubricCriterion, ...]
    raw: dict[str, Any] = field(default_factory=dict)


class RubricSpecError(ValueError):
    """Raised when the rubric YAML is malformed or missing."""


class RubricWiringService:
    """Load + cache the judge rubric for the lifetime of the process.

    Instances are stateless; the cache lives in :func:`_load_cached` and
    is keyed by the resolved rubric path, so multiple instances share a
    single parse.
    """

    def __init__(self, rubric_path: Path | str | None = None) -> None:
        self._rubric_path = (
            Path(rubric_path) if rubric_path is not None else _DEFAULT_RUBRIC_PATH
        )

    @property
    def rubric_path(self) -> Path:
        return self._rubric_path

    def load(self) -> RubricSpec:
        """Parse the rubric YAML (cached per-path)."""
        return _load_cached(str(self._rubric_path.resolve()))

    def reload(self) -> RubricSpec:
        """Bypass the cache and re-parse (useful during iteration)."""
        _load_cached.cache_clear()
        return self.load()


@lru_cache(maxsize=8)
def _load_cached(resolved_path: str) -> RubricSpec:
    path = Path(resolved_path)
    if not path.exists():
        raise RubricSpecError(f"rubric YAML not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RubricSpecError(f"rubric YAML parse error: {exc}") from exc
    if not isinstance(raw, dict):
        raise RubricSpecError(
            f"rubric YAML must be a mapping, got {type(raw).__name__}"
        )
    required_keys = ("rubric_id", "rubric_version", "evaluation_criteria")
    missing = tuple(k for k in required_keys if k not in raw)
    if missing:
        raise RubricSpecError(
            f"rubric YAML missing required keys: {', '.join(missing)}"
        )

    inputs = raw.get("inputs") or {}
    criteria_raw = raw.get("evaluation_criteria") or []
    criteria: list[RubricCriterion] = []
    for entry in criteria_raw:
        if not isinstance(entry, dict):
            continue
        try:
            criteria.append(
                RubricCriterion(
                    id=str(entry["id"]),
                    description=str(entry.get("description", "")).strip(),
                    weight=float(entry.get("weight", 0.0)),
                )
            )
        except (KeyError, ValueError) as exc:
            raise RubricSpecError(
                f"malformed criterion {entry!r}: {exc}"
            ) from exc
    return RubricSpec(
        rubric_id=str(raw["rubric_id"]),
        rubric_version=int(raw["rubric_version"]),
        owning_app=str(raw.get("owning_app", "")),
        owning_module=str(raw.get("owning_module", "")),
        scope=dict(raw.get("scope") or {}),
        required_inputs=tuple(str(i) for i in (inputs.get("required") or ())),
        optional_inputs=tuple(str(i) for i in (inputs.get("optional") or ())),
        criteria=tuple(criteria),
        raw=dict(raw),
    )
