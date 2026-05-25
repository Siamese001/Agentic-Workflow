# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Reasoning prompt construction utilities.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


def build_reasoning_prompt_addendum(params: dict) -> str:
    """Construct system prompt addendum based on reasoning parameters."""
    p = params
    addendum = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n"
    addendum += f"(configuration Level: {p['reasoning_level']}, Intensity: {p['intensity_score']:.1f}/40)\n\n"

    if p["cot"] >= 5:
        addendum += f"• MANDATORY: Explore at least {p['cot']} distinct reasoning paths.\n"
    elif p["cot"] >= 4:
        addendum += f"• Explore {p['cot']} different reasoning paths; compare and synthesize.\n"
    else:
        addendum += "• Consider multiple reasoning approaches before concluding.\n"

    if p["tot_b"] >= 5:
        addendum += f"• MANDATORY: Evaluate {p['tot_b']} different branches at each decision point.\n"
    elif p["tot_b"] >= 4:
        addendum += f"• Explore {p['tot_b']} decision branches at critical junctures.\n"
    else:
        addendum += "• Consider multiple decision branches at key steps.\n"

    if p["tot_d"] >= 5:
        addendum += f"• MANDATORY: Reasoning depth must be {p['tot_d']}+ levels deep.\n"
    elif p["tot_d"] >= 4:
        addendum += f"• Provide {p['tot_d']}-level deep reasoning with layer separation.\n"
    elif p["tot_d"] >= 3:
        addendum += f"• Provide {p['tot_d']}-level reasoning with clear progression.\n"
    else:
        addendum += "• Structure reasoning with clear logical progression.\n"

    if p["reflexion"] and p["max_loops"] >= 3:
        addendum += f"• MANDATORY: Review your answer {p['max_loops']} times, refining each pass.\n"
    elif p["reflexion"] and p["max_loops"] >= 2:
        addendum += f"• Review your answer {p['max_loops']} times; improve if needed.\n"
    elif p["reflexion"]:
        addendum += "• Review and refine your answer at least once.\n"

    addendum += "\nAll directives MUST be followed in the output.\n"
    return addendum
