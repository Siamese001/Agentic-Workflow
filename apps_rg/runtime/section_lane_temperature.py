"""Default LLM temperature per section lane (matches former dispatch parser defaults)."""
from __future__ import annotations


def default_temperature_for_section(section_id: str) -> float:
    sid = str(section_id).strip().lower()
    if sid == "headline":
        from apps_rg.runtime.sections import headline_lane as m

        return float(m.HEADLINE_TEMP_DEFAULT)
    if sid == "executive_summary":
        from apps_rg.runtime.sections import executive_summary_lane as m

        return float(m.EXEC_SUMMARY_TEMP_DEFAULT)
    if sid == "unify_bullets":
        from apps_rg.runtime.sections import unify_bullets_lane as m

        return float(m.UNIFY_TEMP_DEFAULT)
    if sid == "unify_narrative":
        from apps_rg.runtime.sections import unify_narrative_lane as m

        return float(m.NARRATIVE_TEMP_DEFAULT)
    if sid == "ibm_bullets":
        from apps_rg.runtime.sections import ibm_bullets_lane as m

        return float(m.IBM_TEMP_DEFAULT)
    if sid == "ibm_narrative":
        from apps_rg.runtime.sections import ibm_narrative_lane as m

        return float(m.IBM_NARRATIVE_TEMP_DEFAULT)
    if sid == "competencies":
        from apps_rg.runtime.sections import competencies_lane as m

        return float(m.COMPETENCIES_TEMP_DEFAULT)
    return 0.45


__all__ = ["default_temperature_for_section"]
