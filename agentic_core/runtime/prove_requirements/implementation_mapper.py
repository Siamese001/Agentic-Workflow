"""
Phase 2 -- map every requirement to code symbols.

For each RequirementRecord we:
  1. Extract anchor symbols (CamelCase tokens, snake_case method-like
     identifiers >= 4 chars) from source_text + normalized_requirement.
  2. Look each anchor up in the code symbol catalog.
  3. Determine whether the matches fall inside the canonical code roots
     for the requirement's owning_layer.
  4. Emit an ImplementationMapping with a deterministic status:

         IMPLEMENTED_CANDIDATE -- one or more anchor matches under the
                                  canonical layer root for owning_layer.
         CROSS_LAYER_CANDIDATE -- anchor matches found, but none under the
                                  canonical layer root.
         AMBIGUOUS_CANDIDATE   -- many anchors with many matches; needs
                                  human disambiguation.
         MISSING              -- anchors extracted but no catalog matches.
         NEEDS_HUMAN_MAPPING  -- no anchors could be extracted from text;
                                  cannot be auto-mapped.
         NOT_APPLICABLE       -- owning_layer is CrossCutting and the
                                  requirement is a pure E2E spec.

These statuses are NOT the final coverage_matrix statuses (PROVEN/MISSING/
PARTIAL/...) -- those are computed by coverage_matrix_builder.py from
implementation status PLUS test/OTEL/replay evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from agentic_core.runtime.prove_requirements.code_symbol_catalog import (
    SymbolLocation,
)
from agentic_core.runtime.prove_requirements.layer_paths import (
    candidate_roots_for_layer,
)
from agentic_core.runtime.prove_requirements.types import RequirementRecord


# Anchor extraction.
#
# CamelCase identifier of length >= 4 chars (excludes "U0", "L0", "PA",
# "C0", which are too short to be code symbols and would cause noise).
_CAMEL_RE = re.compile(r"\b([A-Z][a-zA-Z0-9]{3,})\b")
# snake_case identifier likely to be a method (e1_prep, e2_valid, etc.) --
# at least one underscore, all lowercase + digits.
_SNAKE_RE = re.compile(r"\b([a-z][a-z0-9]{0,}_[a-z][a-z0-9_]{2,})\b")
# Words to suppress because they appear in CamelCase but are English prose,
# not code identifiers.
_CAMEL_STOPWORDS = frozenset(
    {
        "When",
        "Where",
        "While",
        "What",
        "Which",
        "However",
        "Therefore",
        "Hence",
        "Because",
        "Although",
        "Otherwise",
        "Note",
        "Also",
        "Required",
        "Forbidden",
        "Never",
        "Must",
        "Should",
        "These",
        "Those",
        "This",
        "That",
        "Optional",
        "Default",
        "True",
        "False",
        "None",
        "Yes",
        "Output",
        "Input",
        "Layer",
        "Stage",
        "Step",
        "Phase",
        "Wave",
        "Section",
        "Chapter",
        "Authority",
        "Sovereignty",
        "Replay",
        "OpenTelemetry",
        "OTEL",
        "Acceptance",
        "Criteria",
        "Schema",
        "Contract",  # bare "Contract" is too generic; "RouteContract" still matches
        "Object",
        "Field",
        "Value",
        "Status",
        "State",
    }
)


@dataclass(frozen=True)
class ImplementationMapping:
    """Phase 2 output for one requirement record."""

    req_id: str
    implementation_status: str  # see module docstring for vocabulary
    anchors_extracted: Tuple[str, ...]
    matched_anchors: Tuple[str, ...]
    files: Tuple[Dict[str, object], ...] = field(default_factory=tuple)
    canonical_layer_roots: Tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


def extract_anchors(text: str) -> List[str]:
    """Pull candidate anchor symbols from a requirement line."""
    out: List[str] = []
    seen = set()
    for m in _CAMEL_RE.findall(text):
        if m in _CAMEL_STOPWORDS:
            continue
        # Skip if the token is an all-uppercase short word (e.g. "URL").
        if len(m) <= 3:
            continue
        if m not in seen:
            seen.add(m)
            out.append(m)
    for m in _SNAKE_RE.findall(text):
        # Skip very common method-like names that pollute matches.
        if m in {"true", "false", "none", "null", "no", "yes", "and", "or"}:
            continue
        if len(m) < 4:
            continue
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _matches_under_root(rel_path: str, roots: Sequence[str]) -> bool:
    rel_norm = rel_path.replace("\\", "/")
    return any(rel_norm.startswith(r) for r in roots)


def map_requirement(
    record: RequirementRecord,
    catalog: Dict[str, List[SymbolLocation]],
) -> ImplementationMapping:
    """Classify one record against the catalog."""
    anchors = extract_anchors(record.source_text)
    # Also try the normalized form in case bullet markers stripped a clean token
    if not anchors:
        anchors = extract_anchors(record.normalized_requirement)

    canonical_roots = candidate_roots_for_layer(record.owning_layer)

    # Special-case CrossCutting: spec docs (E2E, MANIFEST, etc.) often have
    # zero anchors. Mark them NOT_APPLICABLE up front so they don't dominate
    # the MISSING bucket.
    if record.owning_layer == "CrossCutting" and not anchors:
        return ImplementationMapping(
            req_id=record.req_id,
            implementation_status="NOT_APPLICABLE",
            anchors_extracted=tuple(),
            matched_anchors=tuple(),
            files=tuple(),
            canonical_layer_roots=canonical_roots,
            notes="CrossCutting requirement with no extractable anchor symbol",
        )

    if not anchors:
        return ImplementationMapping(
            req_id=record.req_id,
            implementation_status="NEEDS_HUMAN_MAPPING",
            anchors_extracted=tuple(),
            matched_anchors=tuple(),
            files=tuple(),
            canonical_layer_roots=canonical_roots,
            notes="No CamelCase or snake_case anchor extracted from line",
        )

    matched: List[str] = []
    in_layer_locs: List[SymbolLocation] = []
    out_of_layer_locs: List[SymbolLocation] = []

    for anchor in anchors:
        locs = catalog.get(anchor, [])
        if not locs:
            continue
        matched.append(anchor)
        for loc in locs:
            if _matches_under_root(loc.relative_path, canonical_roots):
                in_layer_locs.append(loc)
            else:
                out_of_layer_locs.append(loc)

    if not matched:
        return ImplementationMapping(
            req_id=record.req_id,
            implementation_status="MISSING",
            anchors_extracted=tuple(anchors),
            matched_anchors=tuple(),
            files=tuple(),
            canonical_layer_roots=canonical_roots,
            notes=f"None of {len(anchors)} anchors resolved to any code symbol",
        )

    # Build file evidence list -- prefer in-layer over out-of-layer.
    chosen = in_layer_locs if in_layer_locs else out_of_layer_locs
    files_payload = tuple(
        {
            "path": loc.relative_path,
            "symbol": loc.name,
            "kind": loc.kind,
            "line": loc.line,
            "in_layer": loc in in_layer_locs,
        }
        for loc in chosen[:25]  # cap noise
    )

    if in_layer_locs and not out_of_layer_locs:
        status = "IMPLEMENTED_CANDIDATE"
        notes = f"{len(matched)} anchor(s) matched inside canonical layer roots"
    elif in_layer_locs and out_of_layer_locs:
        status = "AMBIGUOUS_CANDIDATE"
        notes = (
            f"{len(matched)} anchor(s) matched; "
            f"{len(in_layer_locs)} in-layer + {len(out_of_layer_locs)} cross-layer"
        )
    else:
        status = "CROSS_LAYER_CANDIDATE"
        notes = (
            f"{len(matched)} anchor(s) matched but none under canonical layer "
            f"roots {canonical_roots}"
        )

    return ImplementationMapping(
        req_id=record.req_id,
        implementation_status=status,
        anchors_extracted=tuple(anchors),
        matched_anchors=tuple(matched),
        files=files_payload,
        canonical_layer_roots=canonical_roots,
        notes=notes,
    )


def build_mappings(
    records: Sequence[RequirementRecord],
    catalog: Dict[str, List[SymbolLocation]],
) -> List[ImplementationMapping]:
    return [map_requirement(r, catalog) for r in records]
