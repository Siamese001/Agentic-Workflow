"""Typed records returned by :mod:`system_learning.rubrics.registry`.

Only :mod:`dataclasses` and standard library types are used here — the registry
is infrastructure under ``system_learning/`` and must not introduce cross-layer
dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class RubricDimension:
    """One scored dimension inside a rubric file.

    Fields mirror the YAML shape documented in
    ``config/judges/rubrics.yaml`` (scale_min/scale_max, pass/warn thresholds,
    ``unknown_budget``, optional ``weight``).
    """

    name: str
    display_name: str
    description: str
    scale_min: int
    scale_max: int
    pass_threshold: float
    warn_threshold: float
    unknown_budget: float
    weight: float = 1.0
    anchors: Mapping[int, str] = field(default_factory=dict)
    # Raw YAML fragment for fields this dataclass does not yet canonicalize
    # (e.g., ``emits_boolean_flag``); consumers should prefer typed fields
    # and treat ``extras`` as best-effort introspection only.
    extras: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RubricFile:
    """One rubric YAML file, parsed and typed.

    A ``RubricFile`` represents the whole document (dimensions, reference
    dimensions, pairwise policy, consensus policy, partial-credit policy,
    taxonomy). The exact set of top-level groups is rubric-file-specific;
    unknown groups are preserved verbatim on ``raw`` so consumers can read
    them without another YAML round-trip.
    """

    rubric_id: str
    source_path: str
    version: int
    schema: str
    rubric_hash: str
    dimensions: Mapping[str, RubricDimension]
    raw: Mapping[str, Any]

    def has_dimension(self, name: str) -> bool:
        return name in self.dimensions


@dataclass(frozen=True)
class RubricRecord:
    """A single entry in the registry — pair of ``RubricFile`` plus metadata.

    ``loaded_at`` lets consumers assert freshness without re-hashing. ``mtime``
    is the on-disk modification timestamp at load time; if a caller sees a
    newer mtime they should call :meth:`RubricRegistry.reload`.
    """

    rubric_id: str
    rubric_file: RubricFile
    loaded_at: float
    mtime: float
