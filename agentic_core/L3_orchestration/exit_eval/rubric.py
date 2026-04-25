"""Rubric loader — parses YAML rubric files per grader_composition_spec §2.

A rubric declares a gate's dimensions, composition mode, and aggregate
threshold. Rubrics are version-pinned (``rubric_version``) and the version
MUST increment on any change (spec §6.4, H7).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from agentic_core.L3_orchestration.exit_eval.composition import CompositionMode
from agentic_core.L3_orchestration.exit_eval.dimension import Dimension, GraderClass


class RubricError(ValueError):
    """Raised on rubric parse/validation failure.

    By H8 fail-mode matrix, a malformed rubric routes the affected gate to
    X3A (DENY) with ``RUBRIC_UNAVAILABLE`` — never falls back to a default.
    """


@dataclass(frozen=True)
class Rubric:
    """A gate's evaluation contract.

    Attributes:
        gate: The gate this rubric belongs to (``X1A``, ``X1B``, ...).
        version: Monotonic version tag (``X1D@v3``). Written to BUS P and
            OTel spans so a disposition can be traced back to its exact
            rubric.
        dimensions: Ordered list of dimensions.
        composition: Composition mode (binary/weighted/hybrid).
        aggregate_threshold: Required for weighted and hybrid modes.
    """

    gate: str
    version: str
    dimensions: tuple[Dimension, ...]
    composition: CompositionMode
    aggregate_threshold: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.gate:
            raise RubricError("Rubric.gate must be non-empty")
        if not self.version:
            raise RubricError("Rubric.version must be non-empty")
        if not self.dimensions:
            raise RubricError(f"Rubric {self.gate}: at least one dimension required")

        names = [d.name for d in self.dimensions]
        if len(names) != len(set(names)):
            dups = sorted({n for n in names if names.count(n) > 1})
            raise RubricError(f"Rubric {self.gate}: duplicate dimension names {dups}")

        if self.composition in (CompositionMode.WEIGHTED, CompositionMode.HYBRID):
            if self.aggregate_threshold is None:
                raise RubricError(
                    f"Rubric {self.gate}: {self.composition.value} requires aggregate_threshold"
                )
            if not 0.0 <= self.aggregate_threshold <= 1.0:
                raise RubricError(f"Rubric {self.gate}: aggregate_threshold must be in [0, 1]")

        if self.composition is CompositionMode.HYBRID:
            hard = [d for d in self.dimensions if d.is_hard_gate]
            soft = [d for d in self.dimensions if not d.is_hard_gate]
            if not hard:
                raise RubricError(f"Rubric {self.gate}: hybrid mode requires at least one hard gate")
            if not soft:
                raise RubricError(f"Rubric {self.gate}: hybrid mode requires at least one non-hard dimension")


def load_rubric(path: str | Path) -> Rubric:
    """Load and validate a YAML rubric.

    Raises:
        RubricError: on parse error, schema error, or semantic validation
            error. Caller is responsible for fail-closing the affected gate.
    """
    rubric_path = Path(path)
    try:
        raw_text = rubric_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RubricError(f"cannot read rubric {path!s}: {exc}") from exc

    try:
        raw = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise RubricError(f"invalid YAML in rubric {path!s}: {exc}") from exc

    if not isinstance(raw, dict):
        raise RubricError(f"rubric {path!s}: top-level must be a mapping")

    return _rubric_from_dict(raw, source=str(rubric_path))


def rubric_from_mapping(data: dict[str, Any]) -> Rubric:
    """Parse a rubric from an in-memory mapping (testing / dynamic configs)."""
    return _rubric_from_dict(data, source="<memory>")


def _rubric_from_dict(data: dict[str, Any], *, source: str) -> Rubric:
    try:
        gate = str(data["gate"])
        version = str(data["version"])
        composition = CompositionMode(str(data["composition"]))
        dims_raw = data["dimensions"]
    except KeyError as exc:
        raise RubricError(f"rubric {source}: missing required key {exc}") from exc
    except ValueError as exc:
        raise RubricError(f"rubric {source}: bad composition value: {exc}") from exc

    if not isinstance(dims_raw, list):
        raise RubricError(f"rubric {source}: dimensions must be a list")

    dimensions: list[Dimension] = []
    for idx, dim_raw in enumerate(dims_raw):
        if not isinstance(dim_raw, dict):
            raise RubricError(f"rubric {source}: dimensions[{idx}] must be a mapping")
        dimensions.append(_dimension_from_dict(dim_raw, source=source, idx=idx))

    aggregate_threshold = data.get("aggregate_threshold")
    if aggregate_threshold is not None:
        try:
            aggregate_threshold = float(aggregate_threshold)
        except (TypeError, ValueError) as exc:
            raise RubricError(f"rubric {source}: aggregate_threshold must be numeric") from exc

    metadata = data.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise RubricError(f"rubric {source}: metadata must be a mapping")

    return Rubric(
        gate=gate,
        version=version,
        dimensions=tuple(dimensions),
        composition=composition,
        aggregate_threshold=aggregate_threshold,
        metadata=metadata,
    )


def _dimension_from_dict(data: dict[str, Any], *, source: str, idx: int) -> Dimension:
    try:
        name = str(data["name"])
        grader_class = GraderClass(str(data["grader_class"]))
    except KeyError as exc:
        raise RubricError(f"rubric {source}: dimensions[{idx}] missing {exc}") from exc
    except ValueError as exc:
        raise RubricError(f"rubric {source}: dimensions[{idx}] bad grader_class: {exc}") from exc

    scale_raw = data.get("scale", [0.0, 1.0])
    if not isinstance(scale_raw, (list, tuple)) or len(scale_raw) != 2:
        raise RubricError(f"rubric {source}: dimensions[{idx}] scale must be [lo, hi]")
    try:
        scale = (float(scale_raw[0]), float(scale_raw[1]))
    except (TypeError, ValueError) as exc:
        raise RubricError(f"rubric {source}: dimensions[{idx}] scale not numeric") from exc

    try:
        return Dimension(
            name=name,
            grader_class=grader_class,
            scale=scale,
            weight=float(data.get("weight", 1.0)),
            is_hard_gate=bool(data.get("is_hard_gate", False)),
            threshold=float(data.get("threshold", 0.0)),
            abstain_allowed=bool(data.get("abstain_allowed", False)),
        )
    except ValueError as exc:
        raise RubricError(f"rubric {source}: dimensions[{idx}] ({name}): {exc}") from exc


__all__ = ["Rubric", "RubricError", "load_rubric", "rubric_from_mapping"]
