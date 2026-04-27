"""
Phase 3 -- coverage_matrix builder.

Joins:
    requirements_index (Phase 1)
    implementation_map (Phase 2)
    test_evidence     (this module)

Computes the final coverage status per record using the spec vocabulary:

    PROVEN
    IMPLEMENTED_NOT_PROVEN
    PARTIAL
    MISSING
    CONFLICT
    NOT_APPLICABLE_WITH_JUSTIFICATION
    UNMAPPED                          -- the irreducible default

Decision rules (deterministic, source-line-traceable):

    impl=NOT_APPLICABLE                       -> NOT_APPLICABLE_WITH_JUSTIFICATION
    impl=NEEDS_HUMAN_MAPPING                  -> UNMAPPED
    impl=MISSING                              -> MISSING
    impl=AMBIGUOUS_CANDIDATE                  -> CONFLICT
    impl=CROSS_LAYER_CANDIDATE                -> PARTIAL
    impl=IMPLEMENTED_CANDIDATE
        AND req_type in (otel,replay,negative_test) AND test_evidence=False
                                              -> IMPLEMENTED_NOT_PROVEN
        AND req_type=otel  AND no_otel_span_evidence (Phase 5 not done)
                                              -> IMPLEMENTED_NOT_PROVEN
        AND req_type=replay AND no_replay_artifact (Phase 6 not done)
                                              -> IMPLEMENTED_NOT_PROVEN
        AND req_type=negative_test AND no_negative_test_match
                                              -> IMPLEMENTED_NOT_PROVEN
        AND test_evidence=True
                                              -> IMPLEMENTED_NOT_PROVEN
                                                 (PROVEN gated on Phase 5/6/7)

PROVEN status is reserved for requirements where the verification dossier
is fully met. Until Phase 5/6/7 land, no record can be PROVEN -- that
honors the user's "do not collapse UNKNOWN into PASS" stop rule.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Dict, List, Sequence, Tuple

from agentic_core.runtime.prove_requirements.implementation_mapper import (
    ImplementationMapping,
)
from agentic_core.runtime.prove_requirements.test_evidence_scanner import TestHit
from agentic_core.runtime.prove_requirements.types import RequirementRecord


@dataclass(frozen=True)
class CoverageRow:
    req_id: str
    relative_path: str
    line_start: int
    line_end: int
    owning_layer: str
    requirement_type: str
    implementation_status: str
    coverage_status: str
    files: Tuple[Dict[str, object], ...]
    test_files: Tuple[str, ...]
    matched_anchors: Tuple[str, ...]
    verification_needed: Tuple[str, ...]
    notes: str
    source_text_excerpt: str


def _record_dict(r):
    if is_dataclass(r):
        return asdict(r)
    if hasattr(r, "__dict__"):
        return dict(r.__dict__)
    return dict(r)


def _has_any_test_hit(matched_anchors: Sequence[str], test_index: Dict[str, List[TestHit]]) -> bool:
    for anchor in matched_anchors:
        if test_index.get(anchor):
            return True
    return False


def _collect_test_files(
    matched_anchors: Sequence[str], test_index: Dict[str, List[TestHit]]
) -> Tuple[str, ...]:
    seen = set()
    for anchor in matched_anchors:
        for hit in test_index.get(anchor, ()):
            seen.add(hit.relative_path)
    return tuple(sorted(seen))


def compute_coverage_status(
    record: RequirementRecord,  # kept for forthcoming Phase 5/6/7 refinement
    mapping: ImplementationMapping,
    test_index: Dict[str, List[TestHit]],
) -> Tuple[str, Tuple[str, ...]]:
    """Return (coverage_status, test_file_refs).

    The record argument is reserved for Phase 5/6/7 refinement where the
    record.requirement_type drives whether OTEL/replay/negative_test
    evidence is required to upgrade a row to PROVEN.
    """
    _ = record  # noqa: F841
    impl = mapping.implementation_status

    if impl == "NOT_APPLICABLE":
        return ("NOT_APPLICABLE_WITH_JUSTIFICATION", tuple())
    if impl == "NEEDS_HUMAN_MAPPING":
        return ("UNMAPPED", tuple())
    if impl == "MISSING":
        return ("MISSING", tuple())
    if impl == "AMBIGUOUS_CANDIDATE":
        return ("CONFLICT", tuple())
    if impl == "CROSS_LAYER_CANDIDATE":
        # Implementation found but in non-canonical layer -- partial credit.
        test_files = _collect_test_files(mapping.matched_anchors, test_index)
        return ("PARTIAL", test_files)
    if impl == "IMPLEMENTED_CANDIDATE":
        test_files = _collect_test_files(mapping.matched_anchors, test_index)
        # Per the spec, PROVEN requires test + OTEL + replay + negative_test
        # evidence as appropriate. Until Phase 5/6/7 land, no record can be
        # PROVEN. Honor "do not collapse UNKNOWN into PASS".
        return ("IMPLEMENTED_NOT_PROVEN", test_files)
    # Unknown / future status.
    return ("UNMAPPED", tuple())


def build_coverage_rows(
    records: Sequence[RequirementRecord],
    mappings: Sequence[ImplementationMapping],
    test_index: Dict[str, List[TestHit]],
) -> List[CoverageRow]:
    map_by_id = {m.req_id: m for m in mappings}
    rows: List[CoverageRow] = []
    for r in records:
        m = map_by_id.get(
            r.req_id,
            ImplementationMapping(
                req_id=r.req_id,
                implementation_status="NEEDS_HUMAN_MAPPING",
                anchors_extracted=tuple(),
                matched_anchors=tuple(),
            ),
        )
        status, test_files = compute_coverage_status(r, m, test_index)
        # Build files payload as plain dicts for JSON.
        files_payload = tuple(dict(f) for f in m.files)
        rows.append(
            CoverageRow(
                req_id=r.req_id,
                relative_path=r.relative_path,
                line_start=r.line_start,
                line_end=r.line_end,
                owning_layer=r.owning_layer,
                requirement_type=r.requirement_type,
                implementation_status=m.implementation_status,
                coverage_status=status,
                files=files_payload,
                test_files=test_files,
                matched_anchors=tuple(m.matched_anchors),
                verification_needed=tuple(r.verification_needed),
                notes=m.notes,
                source_text_excerpt=r.source_text[:400],
            )
        )
    return rows
