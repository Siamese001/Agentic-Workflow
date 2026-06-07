"""Matrix Loader — single SSOT for the hardened certification CSV.

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``

Every W0 verifier consumes the canonical CSV through this loader. Two
verifiers running on the same git HEAD MUST see the same row count and
the same row content; otherwise rule §7 (SOURCE_DIVERGENCE) fires.

Public API
----------

- ``CANONICAL_CSV_PATH``: ``Path`` — the bound canonical location
- ``CANONICAL_REQUIREMENT_COUNT``: ``int`` — known-good row count (86)
- ``REQUIRED_COLUMNS``: ``tuple[str, ...]`` — every column the schema
  validator demands; the loader fails closed if any are missing
- ``ALLOWED_CLAIM_TYPES``: ``frozenset[str]``
- ``ALLOWED_PRIORITY``: ``frozenset[str]``
- ``ALLOWED_BOOLEAN_STRINGS``: ``frozenset[str]`` (case-insensitive)
- ``MatrixLoadResult``: dataclass holding rows + manifest
- ``load_matrix(path: Path | None = None) -> MatrixLoadResult``
- ``compute_canonical_manifest(rows) -> dict``: deterministic universe manifest
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final


REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

CANONICAL_CSV_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "reference"
    / "contracts"
    / "certification"
    / "runtime_certification_requirements_100_percent_hardened.csv"
)

# The hardened CSV's known-good count. Tests assert this and the verifiers
# fail-closed if a freshly loaded CSV produces a different count.
# W1p6 (2026-04-30): incremented from 86 → 87 on addition of RTC-REQ-059
# (safe-reuse composite proof for the approved dense+veto architecture).
CANONICAL_REQUIREMENT_COUNT: Final[int] = 87

# All 32 columns required by the hardened schema (RTC-REQ-002, RTC-REQ-110).
REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "req_id",
    "requirement_group",
    "requirement_title",
    "owner_layer",
    "owner_component",
    "requirement_text",
    "claim_type",
    "required_proof_depth",
    "runtime_sensitive",
    "side_effect_sensitive",
    "required_artifacts",
    "required_positive_evidence",
    "required_negative_controls",
    "acceptance_rule",
    "fail_closed_if_missing",
    "required_ci_gate",
    "required_matrix_columns",
    "runtime_claim_allowed_rule",
    "final_acceptance_status_rule",
    "notes",
    "best_practice_basis",
    "best_practice_gap_closed",
    "implementation_target_files",
    "verifier_target_files",
    "required_output_artifacts",
    "positive_assertions_to_implement",
    "negative_assertions_to_implement",
    "downgrade_rule",
    "priority",
    "implementation_wave",
    "windsurf_acceptance_command",
    "current_known_status",
)

# RTC-REQ-003 enum (must match every value in the CSV's claim_type column)
ALLOWED_CLAIM_TYPES: Final[frozenset[str]] = frozenset({
    "DOC_REFERENCE_ONLY",
    "STATIC_CONTRACT",
    "STATIC_ENFORCEMENT",
    "COMPONENT_RUNTIME",
    "COMPOSITION_RUNTIME",
    "INTEGRATED_RUNTIME",
    "OBSERVABILITY_RUNTIME",
    "REPLAY_RUNTIME",
    "NO_BYPASS_RUNTIME",
    "PRODUCTION_DEPENDENCY_RUNTIME",
})

ALLOWED_PRIORITY: Final[frozenset[str]] = frozenset({"P0", "P1", "P2", "P3"})

ALLOWED_BOOLEAN_STRINGS: Final[frozenset[str]] = frozenset({
    "true", "false", "True", "False", "TRUE", "FALSE",
})

# Claims forbidden from claiming runtime — DOC_REFERENCE_ONLY rows can only
# carry STATIC tiers (rule §3 from prompt §22 lines 21-22 doc-only branch).
RUNTIME_FORBIDDEN_CLAIM_TYPES: Final[frozenset[str]] = frozenset({
    "DOC_REFERENCE_ONLY",
})

# Claims that earn runtime proof tiers (E6+).
RUNTIME_CLAIM_TYPES: Final[frozenset[str]] = frozenset({
    "INTEGRATED_RUNTIME",
    "OBSERVABILITY_RUNTIME",
    "REPLAY_RUNTIME",
    "PRODUCTION_DEPENDENCY_RUNTIME",
})


@dataclass(frozen=True)
class MatrixLoadResult:
    """Result of loading the canonical CSV. Holds rows + provenance manifest."""

    rows: tuple[dict[str, str], ...]
    csv_path: Path
    csv_sha256: str
    column_names: tuple[str, ...]
    row_count: int
    manifest: dict[str, Any] = field(default_factory=dict)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class MatrixLoadError(Exception):
    """Raised when the canonical CSV cannot be loaded fail-closed."""


def load_matrix(path: Path | None = None) -> MatrixLoadResult:
    """Load the hardened CSV from the canonical path (or override) fail-closed.

    Raises ``MatrixLoadError`` if:
      - file does not exist
      - file is empty
      - any row has a missing or duplicate ``req_id``
      - column header missing any of ``REQUIRED_COLUMNS``

    Note: this loader does NOT enforce enum values, claim_type validity, etc.
    Those checks live in ``verify_runtime_certification_matrix_schema.py``.
    The loader's job is to deliver structurally-sound rows so the schema
    validator can speak.
    """
    target = path if path is not None else CANONICAL_CSV_PATH
    if not target.exists():
        raise MatrixLoadError(
            f"CSV_NOT_FOUND: canonical CSV missing at {target}"
        )
    if target.stat().st_size == 0:
        raise MatrixLoadError(f"CSV_EMPTY: canonical CSV is empty at {target}")

    csv_sha256 = _sha256_file(target)

    with target.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        column_names = tuple(reader.fieldnames or ())
        rows = tuple(dict(row) for row in reader)

    # Column-presence check (RTC-REQ-002, RTC-REQ-110)
    missing = [c for c in REQUIRED_COLUMNS if c not in column_names]
    if missing:
        raise MatrixLoadError(
            f"MISSING_COLUMNS: canonical CSV missing required columns: {missing}"
        )

    # req_id presence + uniqueness (RTC-REQ-001)
    seen_ids: dict[str, int] = {}
    for i, row in enumerate(rows):
        rid = (row.get("req_id") or "").strip()
        if not rid:
            raise MatrixLoadError(
                f"MISSING_REQ_ID: row {i} has empty req_id"
            )
        if rid in seen_ids:
            raise MatrixLoadError(
                f"DUPLICATE_REQ_ID: '{rid}' appears at row {seen_ids[rid]} and row {i}"
            )
        seen_ids[rid] = i

    manifest = compute_canonical_manifest(rows, csv_path=target, csv_sha256=csv_sha256)

    return MatrixLoadResult(
        rows=rows,
        csv_path=target,
        csv_sha256=csv_sha256,
        column_names=column_names,
        row_count=len(rows),
        manifest=manifest,
    )


def compute_canonical_manifest(
    rows: tuple[dict[str, str], ...] | list[dict[str, str]],
    *,
    csv_path: Path | None = None,
    csv_sha256: str | None = None,
) -> dict[str, Any]:
    """Build the canonical universe manifest used by RTC-REQ-001.

    The manifest is a deterministic snapshot of:
      - bound CSV path + content hash
      - expected count (CANONICAL_REQUIREMENT_COUNT)
      - actual count
      - sorted distinct req_ids
      - duplicate / missing / extra IDs (always [] when load_matrix succeeded;
        retained for downstream divergence detection)
    """
    actual_ids = sorted({(r.get("req_id") or "").strip() for r in rows})
    expected = CANONICAL_REQUIREMENT_COUNT
    actual = len(actual_ids)
    return {
        "csv_path": str(csv_path) if csv_path else "",
        "csv_sha256": csv_sha256 or "",
        "expected_count": expected,
        "actual_count": actual,
        "distinct_req_ids": actual_ids,
        "duplicates": [],
        "missing": [],
        "extra": [],
        "matches_canonical_count": actual == expected,
    }


__all__ = [
    "CANONICAL_CSV_PATH",
    "CANONICAL_REQUIREMENT_COUNT",
    "REQUIRED_COLUMNS",
    "ALLOWED_CLAIM_TYPES",
    "ALLOWED_PRIORITY",
    "ALLOWED_BOOLEAN_STRINGS",
    "RUNTIME_FORBIDDEN_CLAIM_TYPES",
    "RUNTIME_CLAIM_TYPES",
    "MatrixLoadResult",
    "MatrixLoadError",
    "load_matrix",
    "compute_canonical_manifest",
]
