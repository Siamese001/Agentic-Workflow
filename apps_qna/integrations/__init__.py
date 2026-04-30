"""apps_qna intake integrations — Wave 1.

Typed adapters that convert real-world artifacts (markdown JDs, PDF research
briefings, sibling apps_* outputs) into the typed models that drive
CardPackBuilder.

Adapters are deliberately conservative — they emit best-effort scaffolds that
the operator can review and refine before building. None of them call an LLM.

Modules:
    from_jd                 -- markdown JD -> JobDescription
    from_research_brief     -- PDF (or .md) -> ResearchInputs (heuristic)
    from_apps_research      -- apps_research outputs -> ResearchInputs
    from_apps_rg            -- apps_rg resume/STAR YAML -> ExperienceLibrary
    from_apps_exec          -- apps_exec brief -> exec close patterns
    wizard                  -- interactive CLI that composes Interview YAML
"""

from __future__ import annotations

__all__ = [
    "from_jd",
    "from_research_brief",
    "from_apps_research",
    "from_apps_rg",
    "from_apps_exec",
    "from_apps_shared",
    "wizard",
]
