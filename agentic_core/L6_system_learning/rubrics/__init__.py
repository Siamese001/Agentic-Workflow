"""Rubric registry — read-only, content-addressed view over ``config/judges/*.yaml``.

This package is the engine-side programmatic surface for the rubrics SSOT
(``config/judges/rubrics.yaml`` and ``config/judges/trace_rubric.yaml``). The
YAML files remain the single source of truth; this registry provides:

- A typed record (:class:`RubricRecord`) so consumers avoid hand-parsing YAML.
- A content-addressed hash (``rubric_hash``) stable across whitespace edits.
- A ``version`` + ``loaded_at`` pair so consumers can assert freshness.
- A cheap in-process cache keyed on the on-disk mtime and hash.

Design notes (see plan ``system-learning-waves-7b3c91.md`` phase A2):

- Read-only. Writes happen by editing the YAML and re-loading; no runtime
  mutation of registry state from inside the process.
- Canonicalization strips trailing whitespace, collapses line endings to ``\\n``,
  and sorts mapping keys before hashing, so cosmetic YAML edits do not change
  ``rubric_hash``.
- No dependency on any ``agentic_core`` or ``apps_*`` symbol — the registry is
  infrastructure under ``system_learning/`` and must remain importable from L6
  without introducing cross-layer coupling.
"""

from __future__ import annotations

from .registry import (
    RubricRegistry,
    default_registry,
    load_rubric_file,
)
from .types import (
    RubricDimension,
    RubricFile,
    RubricRecord,
)

__all__ = [
    "RubricDimension",
    "RubricFile",
    "RubricRecord",
    "RubricRegistry",
    "default_registry",
    "load_rubric_file",
]


__layer__ = "L6"
__l6_chapter__ = "06.3"
