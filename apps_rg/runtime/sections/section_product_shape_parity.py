"""Cross-seam parity snapshots: SSOT vs export, judge, graph-only, registry."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.judges import executive_summary_judge_packet as judge_packet_mod
from apps_rg.runtime.sections import exec_summary_graph_only_quality as graph_only_mod
from apps_rg.runtime.sections.section_product_shape_export_bounds import (
    COMPETENCIES_EXPORT_MAX_CATEGORIES,
    EXEC_SUMMARY_EXPORT_MAX_WORDS,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    FORBIDDEN_LEGACY_EXEC_SUMMARY,
    MAX_CATEGORY_COUNT,
    MIN_CATEGORY_COUNT,
    NARRATIVE_MAX_CHARS,
    NARRATIVE_MAX_WORDS,
    SectionProductShape,
    all_generated_lane_shapes,
    section_product_shape,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_SENTENCES,
    EXEC_SUMMARY_MAX_WORDS,
    EXEC_SUMMARY_MIN_SENTENCES,
)

# Live-product patterns that must not appear outside historical/retired contexts.
RETIRED_SHAPE_PROSE_PATTERNS: tuple[str, ...] = (
    r"4\s*[-–]\s*5\s+dense",
    r"4\s+sentences\s+is\s+valid",
    r"4-5\s+dense\s+executive",
)


@dataclass(frozen=True)
class ParityMismatch:
    seam: str
    detail: str


def _import_max_sentences_from_graph_only_source() -> int | None:
    src = open(graph_only_mod.__file__, encoding="utf-8").read()
    if "4–5" in src or "4-5" in src:
        return None
    m = re.search(r"len\(sentences\)\s*>=\s*(\d+)", src)
    if m and int(m.group(1)) >= EXEC_SUMMARY_MIN_SENTENCES:
        return int(m.group(1))
    m2 = re.search(r"sentences\[:(\d+)\]", src)
    if m2:
        return int(m2.group(1))
    return EXEC_SUMMARY_MAX_SENTENCES


def _modular_builder_export_caps() -> tuple[int, int]:
    from apps_rg.l2_recipe import modular_rg_output_builder as mob

    src = open(mob.__file__, encoding="utf-8").read()
    uses_ssot_wc = "EXEC_SUMMARY_EXPORT_MAX_WORDS" in src and "wc > 60" not in src
    max_wc = EXEC_SUMMARY_EXPORT_MAX_WORDS if uses_ssot_wc else -1
    uses_ssot_cat = "COMPETENCIES_EXPORT_MAX_CATEGORIES" in src and "competencies[:6]" not in src
    max_cat = COMPETENCIES_EXPORT_MAX_CATEGORIES if uses_ssot_cat else -1
    return max_wc, max_cat


def audit_ssot_seam_parity() -> list[ParityMismatch]:
    """Return mismatches between SSOT and registered implementation seams."""
    out: list[ParityMismatch] = []

    max_wc, max_cat = _modular_builder_export_caps()
    if max_wc != EXEC_SUMMARY_EXPORT_MAX_WORDS:
        out.append(
            ParityMismatch(
                "modular_rg_output_builder",
                f"exec export max word_count={max_wc} != SSOT {EXEC_SUMMARY_EXPORT_MAX_WORDS}",
            )
        )
    if max_cat != COMPETENCIES_EXPORT_MAX_CATEGORIES:
        out.append(
            ParityMismatch(
                "modular_rg_output_builder",
                f"competencies export slice [:6]={max_cat} != SSOT {COMPETENCIES_EXPORT_MAX_CATEGORIES}",
            )
        )

    rubric = judge_packet_mod.SRFS_GRADE_ONLY_RUBRIC + judge_packet_mod.GRAPH_ONLY_GRADE_ONLY_RUBRIC
    for pat in RETIRED_SHAPE_PROSE_PATTERNS:
        if re.search(pat, rubric, re.IGNORECASE):
            out.append(ParityMismatch("executive_summary_judge_packet", f"rubric matches retired /{pat}/"))

    graph_cap = _import_max_sentences_from_graph_only_source()
    if graph_cap is not None and graph_cap < EXEC_SUMMARY_MIN_SENTENCES:
        out.append(
            ParityMismatch(
                "exec_summary_graph_only_quality",
                f"graph-only cap {graph_cap} < SSOT min sentences {EXEC_SUMMARY_MIN_SENTENCES}",
            )
        )

    ibm = section_product_shape("ibm_narrative")
    if "x2_ibm_narrative_word_budget" not in ibm.bounds_gate_ids:
        out.append(
            ParityMismatch(
                "section_product_shape_ssot",
                "ibm_narrative.bounds_gate_ids missing x2_ibm_narrative_word_budget",
            )
        )

    return out


def assert_ssot_seam_parity() -> None:
    mismatches = audit_ssot_seam_parity()
    if mismatches:
        lines = "\n".join(f"  {m.seam}: {m.detail}" for m in mismatches)
        raise AssertionError(f"SSOT seam parity failures:\n{lines}")


def judge_rubric_shape_constraints(shape: SectionProductShape, rubric: str) -> list[str]:
    """Return violations when rubric text is looser than SSOT for sentence/word bands."""
    issues: list[str] = []
    if shape.section_id == "executive_summary":
        for pat in FORBIDDEN_LEGACY_EXEC_SUMMARY + RETIRED_SHAPE_PROSE_PATTERNS:
            if re.search(pat, rubric, re.IGNORECASE):
                issues.append(f"forbidden pattern /{pat}/")
        if "4 sentences is valid" in rubric.lower():
            issues.append("4 sentences is valid")
    if shape.section_id in ("unify_narrative", "ibm_narrative"):
        if re.search(r"two\s+sentences", rubric, re.IGNORECASE):
            issues.append("two sentences")
    return issues


def narrative_bounds_from_ssot() -> tuple[int, int]:
    return NARRATIVE_MAX_WORDS, NARRATIVE_MAX_CHARS


def competencies_bounds_from_ssot() -> tuple[int, int]:
    return MIN_CATEGORY_COUNT, MAX_CATEGORY_COUNT


__all__ = [
    "ParityMismatch",
    "RETIRED_SHAPE_PROSE_PATTERNS",
    "assert_ssot_seam_parity",
    "audit_ssot_seam_parity",
    "competencies_bounds_from_ssot",
    "judge_rubric_shape_constraints",
    "narrative_bounds_from_ssot",
]
