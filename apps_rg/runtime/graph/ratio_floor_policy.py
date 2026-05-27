"""Per-section fact-to-skill ratio floor policy for apps_rg graph grounding quality gates.

Floors are empirically derived from observed runs across the full resume pipeline.
Observed across 7 executive_summary runs: GSR min=0.40, C03 min=0.30.
Floors are set conservatively below minimums to avoid false positives while
detecting meaningful funnel collapse (>40% degradation from observed baseline).

Measurement points:
  GSR = graph_selection_rationale.json::allowed_fact_count / selected_skill_count
        (pre-C0.3 hop traversal; the initial graph selection outcome)
  C03 = native_c03_final_evidence.json::len(selected_source_fact_ids) / selected_skill_count
        (post-C0.3 hop traversal; facts actually reaching the LLM)
"""
from __future__ import annotations

# --- GSR-level floors (graph_selection_rationale.json) ---
# Violation: allowed_fact_count / selected_skill_count < floor
SECTION_GSR_FLOORS: dict[str, float] = {
    "executive_summary": 0.35,
    "competencies": 0.30,
    "headline": 0.45,
    "ibm_bullets": 0.35,
    "ibm_narrative": 0.40,
    "unify_bullets": 0.35,
    "unify_narrative": 0.40,
}

# Default floor for any section not explicitly listed
DEFAULT_GSR_FLOOR: float = 0.25

# --- C03-level floors (native_c03_final_evidence.json) ---
# Violation: len(selected_source_fact_ids) / selected_skill_count < floor
SECTION_C03_FLOORS: dict[str, float] = {
    "executive_summary": 0.25,
    "competencies": 0.18,
    "headline": 0.30,
    "ibm_bullets": 0.22,
    "ibm_narrative": 0.25,
    "unify_bullets": 0.22,
    "unify_narrative": 0.25,
}

# Default floor for any section not explicitly listed
DEFAULT_C03_FLOOR: float = 0.15


def gsr_floor(section: str) -> float:
    """Return the GSR-level fact-to-skill ratio floor for *section*."""
    return SECTION_GSR_FLOORS.get(section, DEFAULT_GSR_FLOOR)


def c03_floor(section: str) -> float:
    """Return the C03-level fact-to-skill ratio floor for *section*."""
    return SECTION_C03_FLOORS.get(section, DEFAULT_C03_FLOOR)


def check_gsr_ratio(
    section: str,
    *,
    allowed_fact_count: int,
    selected_skill_count: int,
) -> tuple[bool, float, float]:
    """Return (passes, actual_ratio, floor).

    ``passes`` is False when the ratio is below the configured floor.
    """
    floor = gsr_floor(section)
    if selected_skill_count == 0:
        return True, 0.0, floor
    ratio = allowed_fact_count / selected_skill_count
    return ratio >= floor, ratio, floor


def check_c03_ratio(
    section: str,
    *,
    fact_count: int,
    selected_skill_count: int,
) -> tuple[bool, float, float]:
    """Return (passes, actual_ratio, floor).

    ``passes`` is False when the ratio is below the configured floor.
    """
    floor = c03_floor(section)
    if selected_skill_count == 0:
        return True, 0.0, floor
    ratio = fact_count / selected_skill_count
    return ratio >= floor, ratio, floor
